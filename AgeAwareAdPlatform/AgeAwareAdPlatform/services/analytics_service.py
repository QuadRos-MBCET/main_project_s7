from typing import Dict, Any
from config.default_config import settings

class AnalyticsService:
    """
    Computes real platform metrics directly from the SQLAlchemy database.
    Distinguishes real production data from demo simulation metrics.
    """
    
    @staticmethod
    def get_platform_metrics() -> Dict[str, Any]:
        """Queries actual database tables for real system analytics."""
        try:
            from backend.app.db.database import SessionLocal
            from backend.app.db.models import User, Advertisement, ModerationResult, SafetyClassification, ModerationAction, AgeGroup
            db = SessionLocal()
            
            # Advertisements metrics
            total_ads = db.query(Advertisement).count()
            approved_ads = db.query(Advertisement).filter(Advertisement.status == "APPROVE").count()
            rejected_ads = db.query(Advertisement).filter(Advertisement.status == "REJECT").count()
            pending_review = db.query(Advertisement).filter(Advertisement.status.in_(["HUMAN_REVIEW", "PENDING"])).count()
            
            # Classification breakdown
            results = db.query(ModerationResult).all()
            cat_counts = {
                "SAFE FOR ALL": 0,
                "14+": 0,
                "18+": 0,
                "UNSAFE FOR ALL": 0
            }
            human_overrides = 0
            for r in results:
                eff_cls = (r.final_classification or r.classification).value
                app_cat = settings.BACKEND_TO_APP_MAP.get(eff_cls, "UNSAFE FOR ALL")
                if app_cat in cat_counts:
                    cat_counts[app_cat] += 1
                if r.is_human_reviewed:
                    human_overrides += 1
            
            # User demographic breakdown
            users = db.query(User).all()
            total_users = len(users)
            user_age_counts = {
                "SAFE FOR ALL": 0,
                "14+": 0,
                "18+": 0
            }
            for u in users:
                if u.verified_age_group == AgeGroup.UNDER_14:
                    user_age_counts["SAFE FOR ALL"] += 1
                elif u.verified_age_group == AgeGroup.AGE_14_TO_17:
                    user_age_counts["14+"] += 1
                else:
                    user_age_counts["18+"] += 1

            db.close()
            
            return {
                "is_real_data": True,
                "total_advertisements": total_ads,
                "approved_advertisements": approved_ads,
                "rejected_advertisements": rejected_ads,
                "pending_human_review": pending_review,
                "human_overrides_count": human_overrides,
                "category_breakdown": cat_counts,
                "total_users": total_users,
                "user_age_breakdown": user_age_counts
            }
        except Exception as e:
            return {
                "is_real_data": False,
                "error": str(e),
                "total_advertisements": 0,
                "approved_advertisements": 0,
                "rejected_advertisements": 0,
                "pending_human_review": 0,
                "human_overrides_count": 0,
                "category_breakdown": {"SAFE FOR ALL": 0, "14+": 0, "18+": 0, "UNSAFE FOR ALL": 0},
                "total_users": 0,
                "user_age_breakdown": {"SAFE FOR ALL": 0, "14+": 0, "18+": 0}
            }

analytics_service = AnalyticsService()
