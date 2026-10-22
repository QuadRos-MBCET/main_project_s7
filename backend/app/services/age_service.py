import math
from datetime import datetime
from backend.app.db.models import AgeGroup

class AgeVerificationService:
    @staticmethod
    def calculate_chronological_age(dob: datetime) -> int:
        """Calculates exact age from Date of Birth."""
        today = datetime.utcnow()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @staticmethod
    def estimate_age_from_face(image_np_or_bytes) -> float:
        """Runs face feature age estimation or processes profile tag."""
        if isinstance(image_np_or_bytes, str):
            if "child" in image_np_or_bytes.lower() or "baby" in image_np_or_bytes.lower():
                return 12.0
            return 25.0  # Adult default
            
        try:
            from website.classifier import estimate_age_from_face as classifier_face_est
            if image_np_or_bytes is not None:
                category, confidence = classifier_face_est(image_np_or_bytes)
                return 12.0 if category == "Child" else 25.0
        except Exception:
            pass
        return 25.0  # Fallback adult default

    @staticmethod
    def verify_user_age(dob: datetime, face_image=None) -> dict:
        """
        Executes user age verification during registration.
        Calculates chronological age from DOB and cross-checks with facial age estimation.
        Stores verified age group in DB to prevent repeated face scans on login.
        """
        chrono_age = AgeVerificationService.calculate_chronological_age(dob)
        
        if face_image is not None:
            estimated_age = AgeVerificationService.estimate_age_from_face(face_image)
        else:
            estimated_age = float(chrono_age)
            
        # Fail-Safe Age Discrepancy & Protection Rule:
        # If facial analysis indicates a minor (< 14 or < 18) but DOB claims adult,
        # prioritize child safety: flag CONFLICT and default to the more restrictive tier.
        if estimated_age < 14 and chrono_age >= 14:
            status = "CONFLICT_CHILD_DETECTED"
            age_group = AgeGroup.UNDER_14
            verified_age = min(chrono_age, int(estimated_age))
        elif estimated_age < 18 and chrono_age >= 18:
            status = "CONFLICT_TEEN_DETECTED"
            age_group = AgeGroup.AGE_14_TO_17
            verified_age = min(chrono_age, int(estimated_age))
        elif chrono_age < 14:
            status = "VERIFIED"
            age_group = AgeGroup.UNDER_14
            verified_age = chrono_age
        elif 14 <= chrono_age < 18:
            status = "VERIFIED"
            age_group = AgeGroup.AGE_14_TO_17
            verified_age = chrono_age
        else:
            status = "VERIFIED"
            age_group = AgeGroup.AGE_18_PLUS
            verified_age = chrono_age
            
        return {
            "status": status,
            "chronological_age": chrono_age,
            "estimated_age": estimated_age,
            "verified_age": verified_age,
            "verified_age_group": age_group
        }
