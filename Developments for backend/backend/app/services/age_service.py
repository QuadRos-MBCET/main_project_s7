import math
from datetime import datetime
from app.db.models import AgeGroup

class AgeVerificationService:
    @staticmethod
    def calculate_chronological_age(dob: datetime) -> int:
        today = datetime.utcnow()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @staticmethod
    def estimate_age_from_face(image_bytes: bytes) -> float:
        # TODO: Implement actual face-based age estimation using DeepFace or similar
        # For now, this is a placeholder that mocks the age
        return 25.0

    @staticmethod
    def verify_age(dob: datetime, face_image_bytes: bytes) -> dict:
        chrono_age = AgeVerificationService.calculate_chronological_age(dob)
        estimated_age = AgeVerificationService.estimate_age_from_face(face_image_bytes)
        
        # Simple policy: if estimated age is within 5 years of chrono age, accept chrono age
        if abs(chrono_age - estimated_age) <= 5:
            verified_age = chrono_age
            status = "VERIFIED"
        else:
            # Conflict detected, fallback to the more restrictive age or require manual review
            verified_age = min(chrono_age, math.floor(estimated_age))
            status = "CONFLICT_DETECTED"
            
        if verified_age < 14:
            age_group = AgeGroup.UNDER_14
        elif 14 <= verified_age < 18:
            age_group = AgeGroup.AGE_14_TO_17
        else:
            age_group = AgeGroup.AGE_18_PLUS
            
        return {
            "status": status,
            "chrono_age": chrono_age,
            "estimated_age": estimated_age,
            "verified_age": verified_age,
            "verified_age_group": age_group
        }
