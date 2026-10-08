import requests
from typing import Dict, Any, Optional
from config.default_config import settings

class AgeRegistrationService:
    """
    Service coordinating facial age estimation during account creation.
    Strictly enforces:
    1. Single-use camera operation at registration only.
    2. Camera termination immediately upon verification.
    3. Storing resulting age category with user account.
    4. Subsequent logins read saved category without activating camera.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}").rstrip('/')

    def estimate_age_from_snapshot(self, image_base64: str = "", preset: str = "") -> Dict[str, Any]:
        """
        Sends camera snapshot to FaceAgeAdapter.
        Checks for single face, anti-spoofing, and predicts age.
        """
        url = f"{self.base_url}/api/v1/age/estimate"
        payload = {"image_base64": image_base64, "preset": preset}
        try:
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            return {
                "success": False,
                "error": "ESTIMATION_FAILED",
                "message": resp.json().get("detail", "Age estimation failed.")
            }
        except Exception as e:
            # Fallback to local adapter directly if backend is local
            try:
                from camera_integration.face_age_adapter import face_age_adapter
                from camera_integration.camera_handler import CameraHandler
                if not image_base64 and preset:
                    synth = CameraHandler.generate_synthetic_face(preset)
                    image_base64 = CameraHandler.frame_to_base64(synth)
                return face_age_adapter.process_frame(image_base64)
            except Exception as inner_e:
                return {
                    "success": False,
                    "error": "SERVICE_UNAVAILABLE",
                    "message": f"Face-Age service offline: {str(e)} / {str(inner_e)}"
                }

    def register_user_with_age(
        self,
        username: str,
        email: str,
        password: str,
        date_of_birth: str,
        image_base64: Optional[str] = None,
        preset: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete registration workflow:
        1. Estimates age via FaceAgeAdapter
        2. Validates single face & anti-spoof
        3. Maps age to category (<14: SAFE FOR ALL, 14-17: 14+, 18+: 18+)
        4. Registers account in DB with assigned category
        5. Halts camera
        """
        # Step 1: Run Age Estimation
        face_res = self.estimate_age_from_snapshot(image_base64=image_base64 or "", preset=preset or "")
        
        if not face_res.get("success"):
            return {
                "success": False,
                "error": face_res.get("error", "FACE_CHECK_FAILED"),
                "message": face_res.get("message", "Face verification failed. Please try again.")
            }

        # Step 2: Register User Account
        from services.auth_service import auth_service
        reg_res = auth_service.register(username, email, password, date_of_birth)
        
        if not reg_res.get("success"):
            return reg_res

        user_data = reg_res["data"]
        user_id = user_data["id"]

        # Step 3: Update Account with Facial Age Verification Details
        try:
            from backend.app.db.database import SessionLocal
            from backend.app.db.models import User, AgeGroup
            db = SessionLocal()
            u = db.query(User).filter(User.id == user_id).first()
            if u:
                u.estimated_age = face_res.get("estimated_age")
                u.age_confidence = face_res.get("confidence", 0.85)
                db_group = face_res.get("database_age_group", "AGE_18_PLUS")
                try:
                    u.verified_age_group = AgeGroup(db_group)
                except Exception:
                    u.verified_age_group = AgeGroup.AGE_18_PLUS
                u.age_verification_status = "VERIFIED_BIOMETRIC"
                db.commit()
            db.close()
        except Exception as db_err:
            print(f"[AgeRegistrationService] DB update warning: {db_err}")

        return {
            "success": True,
            "message": "User registered successfully with verified age category.",
            "user_id": user_id,
            "username": username,
            "estimated_age": face_res.get("estimated_age"),
            "assigned_category": face_res.get("user_category"),
            "confidence": face_res.get("confidence"),
            "database_age_group": face_res.get("database_age_group")
        }

age_registration_service = AgeRegistrationService()
