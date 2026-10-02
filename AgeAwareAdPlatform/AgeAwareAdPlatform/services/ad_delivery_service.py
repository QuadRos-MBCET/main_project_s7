import requests
from typing import List, Dict, Any, Optional
from config.default_config import settings

class AdDeliveryService:
    """
    Core Age-Aware Advertisement Delivery Engine.
    Enforces strict access control:
    - User Category + Final Ad Classification -> Eligibility
    - Reads FINAL CLASSIFICATION (honoring human reviewer overrides)
    - Strips internal AI metrics, debugging details, and confidence scores from user view
    - Hard blocks UNSAFE FOR ALL from ever being delivered
    """
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}").rstrip('/')

    def evaluate_eligibility(self, user_category: str, ad_final_category: str) -> bool:
        """
        Pure policy evaluation function:
        Returns True only if the user is permitted to view the advertisement.
        """
        # Hard block: UNSAFE FOR ALL is never permitted to anyone
        if ad_final_category == "UNSAFE FOR ALL":
            return False

        allowed_categories = settings.DELIVERY_ELIGIBILITY.get(user_category, [])
        return ad_final_category in allowed_categories

    def get_eligible_sponsored_ads(self, user_category: str) -> List[Dict[str, Any]]:
        """
        Fetches approved advertisements from the backend and filters strictly for the given user category.
        Ensures NO unapproved or UNSAFE ads are returned.
        Strips out internal AI scoring so normal users only see clean sponsored content.
        """
        # Convert app user category to DB AgeGroup enum string
        db_group = "AGE_18_PLUS"
        if user_category == "SAFE FOR ALL":
            db_group = "UNDER_14"
        elif user_category == "14+":
            db_group = "AGE_14_TO_17"

        url = f"{self.base_url}/api/v1/advertisements/user_feed?user_age_group={db_group}"
        
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                raw_ads = resp.json()
                eligible_ads = []
                
                for ad in raw_ads:
                    raw_cls = ad.get("final_classification") or ad.get("classification", "UNSAFE_FOR_ALL")
                    app_ad_cat = settings.BACKEND_TO_APP_MAP.get(raw_cls, "UNSAFE FOR ALL")
                    
                    # Double-check backend enforcement
                    if self.evaluate_eligibility(user_category, app_ad_cat):
                        clean_ad = {
                            "id": ad.get("id"),
                            "brand_name": ad.get("title", "Sponsored Brand"),
                            "caption": ad.get("caption", ""),
                            "file_path": ad.get("file_path", ""),
                            "media_type": ad.get("media_type", "image"),
                            "is_sponsored": True,
                            # Public badge only (e.g. "Sponsored • 14+") - NO internal scores
                            "age_badge": app_ad_cat
                        }
                        eligible_ads.append(clean_ad)
                        
                return eligible_ads
            return []
        except Exception:
            # Fallback direct DB query if backend service is local
            return self._query_db_direct(user_category)

    def _query_db_direct(self, user_category: str) -> List[Dict[str, Any]]:
        """Direct DB fallback if API request fails."""
        try:
            from backend.app.db.database import SessionLocal
            from backend.app.db.models import Advertisement, SafetyClassification
            db = SessionLocal()
            ads = db.query(Advertisement).filter(Advertisement.status != "REJECT").all()
            eligible = []
            
            for ad in ads:
                if ad.moderation_result and ad.moderation_result.publishable:
                    raw_cls = (ad.moderation_result.final_classification or ad.moderation_result.classification).value
                    app_cat = settings.BACKEND_TO_APP_MAP.get(raw_cls, "UNSAFE FOR ALL")
                    if self.evaluate_eligibility(user_category, app_cat):
                        eligible.append({
                            "id": ad.id,
                            "brand_name": ad.title,
                            "caption": ad.caption or "",
                            "file_path": ad.file_path,
                            "media_type": ad.media_type,
                            "is_sponsored": True,
                            "age_badge": app_cat
                        })
            db.close()
            return eligible
        except Exception:
            return []

ad_delivery_service = AdDeliveryService()
