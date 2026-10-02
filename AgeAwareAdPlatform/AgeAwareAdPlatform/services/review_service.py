import requests
from typing import Dict, Any, List, Optional
from config.default_config import settings

class ReviewService:
    """
    Service managing Human-in-the-Loop (HITL) moderation workflows and final classification overrides.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}").rstrip('/')

    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """Retrieves advertisements queued for human review."""
        url = f"{self.base_url}/api/v1/admin/pending"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                ads = resp.json()
                for ad in ads:
                    raw_cls = ad.get("classification", "REQUIRES_HUMAN_REVIEW")
                    ad["display_category"] = settings.BACKEND_TO_APP_MAP.get(raw_cls, "PENDING REVIEW")
                return ads
            return []
        except Exception:
            return []

    def submit_override_decision(
        self,
        ad_id: int,
        target_category: str,
        moderator_notes: str = ""
    ) -> Dict[str, Any]:
        """
        Submits human moderator override decision.
        CRITICAL RULE: The human classification strictly overrides the AI prediction
        and becomes the final_classification used by Ad Delivery.
        """
        if target_category not in settings.AD_CATEGORIES:
            return {"success": False, "error": f"Invalid target category '{target_category}'."}

        backend_cls = settings.APP_TO_BACKEND_MAP.get(target_category, "UNSAFE_FOR_ALL")
        
        # Determine moderation action
        if target_category == "SAFE FOR ALL":
            action = "APPROVE"
        elif target_category in ["14+", "18+"]:
            action = "AGE_RESTRICT"
        else:
            action = "REJECT"

        url = f"{self.base_url}/api/v1/admin/override"
        payload = {
            "ad_id": ad_id,
            "action": action,
            "final_classification": backend_cls,
            "moderator_notes": moderator_notes
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                data["display_final_category"] = target_category
                return {"success": True, "data": data}
            return {"success": False, "error": resp.json().get("detail", "Override submission failed.")}
        except Exception as e:
            return {"success": False, "error": f"Network/Backend error: {str(e)}"}

review_service = ReviewService()
