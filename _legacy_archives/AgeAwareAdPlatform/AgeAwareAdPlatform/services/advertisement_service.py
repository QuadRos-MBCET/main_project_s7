import os
import requests
import mimetypes
from typing import Dict, Any, Optional, List
from config.default_config import settings

class AdvertisementService:
    """
    Client service for Advertisement management, uploading, and status tracking.
    """
    
    ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".mp4", ".mov", ".avi"}

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}").rstrip('/')

    def map_classification(self, backend_enum: str) -> str:
        """Maps backend enum string to one of the 4 standard application categories."""
        return settings.BACKEND_TO_APP_MAP.get(backend_enum, "UNSAFE FOR ALL")

    def upload_advertisement(
        self,
        file_path_or_bytes: Any,
        filename: str,
        title: str,
        caption: str = "",
        user_id: int = 1
    ) -> Dict[str, Any]:
        """
        Uploads an advertisement to the backend moderation pipeline.
        Validates file format, posts multipart form, and returns standardized response.
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            return {
                "success": False,
                "error": f"Unsupported file format '{ext}'. Supported: {', '.join(self.ALLOWED_EXTENSIONS)}"
            }

        url = f"{self.base_url}/api/v1/advertisements/check"
        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or "application/octet-stream"

        try:
            if isinstance(file_path_or_bytes, (str, os.PathLike)) and os.path.exists(file_path_or_bytes):
                with open(file_path_or_bytes, "rb") as f:
                    files = {"file": (filename, f, mime_type)}
                    data = {"title": title, "caption": caption, "user_id": str(user_id)}
                    resp = requests.post(url, files=files, data=data, timeout=60)
            else:
                files = {"file": (filename, file_path_or_bytes, mime_type)}
                data = {"title": title, "caption": caption, "user_id": str(user_id)}
                resp = requests.post(url, files=files, data=data, timeout=60)

            if resp.status_code == 200:
                raw_data = resp.json()
                raw_classification = raw_data.get("classification", "UNSAFE_FOR_ALL")
                app_category = self.map_classification(raw_classification)
                raw_data["application_category"] = app_category
                
                # Check rejection status
                is_rejected = (app_category == "UNSAFE FOR ALL") or (raw_data.get("publication_action") == "REJECT")
                raw_data["is_rejected"] = is_rejected
                
                return {"success": True, "data": raw_data}
            return {
                "success": False,
                "error": resp.json().get("detail", f"Moderation failed with status {resp.status_code}")
            }
        except Exception as e:
            return {"success": False, "error": f"Network/Backend error: {str(e)}"}

    def get_moderation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves moderation history with mapped display labels."""
        url = f"{self.base_url}/api/v1/moderation/history?limit={limit}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                items = resp.json()
                for item in items:
                    raw_cls = item.get("final_classification") or item.get("classification", "UNSAFE_FOR_ALL")
                    item["application_category"] = self.map_classification(raw_cls)
                    item["is_rejected"] = (item["application_category"] == "UNSAFE FOR ALL") or (item.get("publication_action") == "REJECT")
                return items
            return []
        except Exception:
            return []

    def request_human_review(self, ad_id: int, reason: str = "") -> Dict[str, Any]:
        """Flags an advertisement for human moderator review when advertiser disputes AI decision."""
        # Update via database or admin status
        try:
            from backend.app.db.database import SessionLocal
            from backend.app.db.models import Advertisement, ModerationAction, AuditLog
            db = SessionLocal()
            ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
            if not ad:
                db.close()
                return {"success": False, "error": "Advertisement not found."}
                
            ad.status = "HUMAN_REVIEW"
            if ad.moderation_result:
                ad.moderation_result.moderation_action = ModerationAction.HUMAN_REVIEW
                ad.moderation_result.explanation += f" [Advertiser Review Requested: {reason}]"
                ad.moderation_result.publishable = False
                
            audit = AuditLog(
                ad_id=ad.id,
                user_id=ad.owner_id or 1,
                action="ADVERTISER_REQUESTED_HUMAN_REVIEW",
                details=f"Advertiser requested manual review. Reason: {reason}"
            )
            db.add(audit)
            db.commit()
            db.close()
            return {"success": True, "message": "Advertisement submitted to human review queue."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_advertisement(self, ad_id: int) -> Dict[str, Any]:
        """Deletes an uploaded advertisement and its associated records from DB and disk."""
        try:
            from backend.app.db.database import SessionLocal
            from backend.app.db.models import Advertisement, ModerationResult, AuditLog
            db = SessionLocal()
            ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
            if not ad:
                db.close()
                return {"success": False, "error": f"Advertisement #{ad_id} not found."}

            if ad.file_path and os.path.exists(ad.file_path):
                try:
                    os.remove(ad.file_path)
                except Exception:
                    pass

            db.query(ModerationResult).filter(ModerationResult.advertisement_id == ad_id).delete()
            db.query(AuditLog).filter(AuditLog.ad_id == ad_id).delete()
            db.delete(ad)
            db.commit()
            db.close()
            return {"success": True, "message": f"Advertisement #{ad_id} deleted successfully."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_all_advertisements(self) -> Dict[str, Any]:
        """Deletes all uploaded advertisements from database and cleans uploads directory."""
        try:
            from backend.app.db.database import SessionLocal
            from backend.app.db.models import Advertisement, ModerationResult, AuditLog
            db = SessionLocal()
            db.query(ModerationResult).delete()
            db.query(AuditLog).delete()
            db.query(Advertisement).delete()
            db.commit()
            db.close()

            # Clean uploads folder
            from config.default_config import settings
            upload_dir = settings.UPLOAD_DIR
            if upload_dir.exists():
                for f in upload_dir.iterdir():
                    if f.is_file():
                        try:
                            f.unlink()
                        except Exception:
                            pass
            return {"success": True, "message": "All advertisements removed successfully."}
        except Exception as e:
            return {"success": False, "error": str(e)}

advertisement_service = AdvertisementService()
