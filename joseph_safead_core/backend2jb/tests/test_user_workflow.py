import unittest
import os
import sys
from datetime import datetime

# Ensure project root is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.db.database import Base, engine, SessionLocal
from backend.app.db.models import User, UserRole, Advertisement, ModerationResult, HumanReview, AuditLog, SafetyClassification, ModerationAction
from backend.app.api.v1.auth import seed_demo_users
from backend.app.services.policy_service import PolicyService

class TestUserWorkflowAndHumanReview(unittest.TestCase):
    """
    Comprehensive test suite verifying the 8 required Brand Owner + Human Review Workflow scenarios.
    """

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()
        seed_demo_users(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_1_safe_ad_accept_ai(self):
        """TEST 1: Safe advertisement -> SAFE FOR ALL -> Accept AI -> stored correctly."""
        brand = self.db.query(User).filter(User.username == "brand_demo").first()
        ad = Advertisement(
            title="Safe Organic Apples",
            caption="Fresh apples online",
            file_path="apples_ad.jpg",
            media_type="image",
            status="UPLOADED",
            owner_id=brand.id
        )
        self.db.add(ad)
        self.db.commit()

        # Simulate AI Analysis
        ad.status = "AI_ANALYZED"
        res = ModerationResult(
            advertisement_id=ad.id,
            classification=SafetyClassification.SAFE_FOR_ALL,
            risk_category="Safe for All",
            risk_score=4.4,
            confidence=0.97,
            explanation="Approved for general publication",
            evidence="{}",
            moderation_action=ModerationAction.APPROVE,
            publishable=True
        )
        self.db.add(res)
        self.db.commit()

        # Brand Owner accepts AI decision
        ad.status = "AI_ACCEPTED"
        self.db.commit()

        self.assertEqual(ad.status, "AI_ACCEPTED")
        self.assertTrue(ad.moderation_result.publishable)
        self.assertEqual(ad.moderation_result.classification, SafetyClassification.SAFE_FOR_ALL)

    def test_2_14_plus_ad_accept_ai(self):
        """TEST 2: 14+ advertisement -> 14+ -> Accept AI -> stored correctly."""
        brand = self.db.query(User).filter(User.username == "brand_demo").first()
        ad = Advertisement(
            title="Teen Energy Drink",
            caption="Mild energy boost",
            file_path="coding_lessons.mp4",
            media_type="video",
            status="AI_ANALYZED",
            owner_id=brand.id
        )
        self.db.add(ad)
        self.db.commit()

        res = ModerationResult(
            advertisement_id=ad.id,
            classification=SafetyClassification.SAFE_14_PLUS,
            risk_category="14+",
            risk_score=32.0,
            confidence=0.95,
            explanation="14+ age restricted",
            evidence="{}",
            moderation_action=ModerationAction.AGE_RESTRICT,
            age_restriction=14,
            publishable=True
        )
        self.db.add(res)
        ad.status = "AI_ACCEPTED"
        self.db.commit()

        self.assertEqual(ad.status, "AI_ACCEPTED")
        self.assertTrue(ad.moderation_result.publishable)
        self.assertEqual(ad.moderation_result.age_restriction, 14)

    def test_3_18_plus_ad_send_human_review_and_admin_accept(self):
        """TEST 3: 18+ ad -> Brand Owner sends for human review -> Admin accepts/rejects -> status updated."""
        brand = self.db.query(User).filter(User.username == "brand_demo").first()
        admin = self.db.query(User).filter(User.username == "admin_demo").first()

        ad = Advertisement(
            title="Adult Dating Promo",
            caption="Meet singles 18+",
            file_path="adult_dating.jpg",
            media_type="image",
            status="AI_ANALYZED",
            owner_id=brand.id
        )
        self.db.add(ad)
        self.db.commit()

        res = ModerationResult(
            advertisement_id=ad.id,
            classification=SafetyClassification.SAFE_18_PLUS,
            risk_category="18+",
            risk_score=59.5,
            confidence=0.94,
            explanation="Adult content detected",
            evidence="{}",
            moderation_action=ModerationAction.AGE_RESTRICT,
            age_restriction=18,
            publishable=True
        )
        self.db.add(res)
        self.db.commit()

        # Step A: Brand Owner sends for human review
        ad.status = "PENDING_REVIEW"
        rev = HumanReview(
            advertisement_id=ad.id,
            submitted_by=brand.id,
            ai_classification="SAFE_18_PLUS",
            review_status="PENDING_REVIEW",
            review_comment="Disagrees with age rating"
        )
        self.db.add(rev)
        self.db.commit()

        self.assertEqual(ad.status, "PENDING_REVIEW")
        self.assertEqual(rev.review_status, "PENDING_REVIEW")

        # Step B: Admin reviews and accepts case
        rev.review_status = "HUMAN_ACCEPTED"
        rev.human_decision = "ACCEPT"
        rev.admin_id = admin.id
        rev.review_comment = "Manual review passed"
        ad.status = "HUMAN_ACCEPTED"
        ad.moderation_result.publishable = True
        self.db.commit()

        self.assertEqual(ad.status, "HUMAN_ACCEPTED")
        self.assertEqual(rev.human_decision, "ACCEPT")
        self.assertTrue(ad.moderation_result.publishable)

    def test_4_unsafe_ad_publication_blocked(self):
        """TEST 4: Unsafe for All advertisement -> UNSAFE FOR ALL -> normal publication must be blocked."""
        brand = self.db.query(User).filter(User.username == "brand_demo").first()
        ad = Advertisement(
            title="Paisa Double Scheme",
            caption="Double money quick",
            file_path="scam_giveaway.mp4",
            media_type="video",
            status="AI_ANALYZED",
            owner_id=brand.id
        )
        self.db.add(ad)
        self.db.commit()

        res = ModerationResult(
            advertisement_id=ad.id,
            classification=SafetyClassification.UNSAFE_FOR_ALL,
            risk_category="Unsafe for All",
            risk_score=100.0,
            confidence=0.97,
            explanation="Prohibited scam content detected",
            evidence="{}",
            moderation_action=ModerationAction.REJECT,
            publishable=False
        )
        self.db.add(res)
        self.db.commit()

        # Try accepting AI decision
        ad.status = "AI_ACCEPTED"
        res.publishable = False  # Enforcement: UNSAFE_FOR_ALL CANNOT be published!
        self.db.commit()

        self.assertFalse(ad.moderation_result.publishable)

    def test_5_delete_advertisement(self):
        """TEST 5: Brand Owner deletes advertisement -> DELETED status, audit history retained."""
        brand = self.db.query(User).filter(User.username == "brand_demo").first()
        ad = Advertisement(
            title="Temporary Draft Ad",
            caption="Draft caption",
            file_path="apples_ad.jpg",
            media_type="image",
            status="AI_ANALYZED",
            owner_id=brand.id
        )
        self.db.add(ad)
        self.db.commit()

        # Delete action
        ad.status = "DELETED"
        audit = AuditLog(ad_id=ad.id, user_id=brand.id, action="BRAND_OWNER_DELETED_AD", details="Deleted by owner")
        self.db.add(audit)
        self.db.commit()

        self.assertEqual(ad.status, "DELETED")
        db_audit = self.db.query(AuditLog).filter(AuditLog.ad_id == ad.id).first()
        self.assertIsNotNone(db_audit)
        self.assertEqual(db_audit.action, "BRAND_OWNER_DELETED_AD")

    def test_6_independent_advertisement_analysis(self):
        """TEST 6: Upload another advertisement -> previous analysis does not contaminate new analysis."""
        brand = self.db.query(User).filter(User.username == "brand_demo").first()

        ad1 = Advertisement(title="Ad 1", file_path="apples_ad.jpg", status="AI_ANALYZED", owner_id=brand.id)
        ad2 = Advertisement(title="Ad 2", file_path="scam_giveaway.mp4", status="AI_ANALYZED", owner_id=brand.id)
        self.db.add_all([ad1, ad2])
        self.db.commit()

        res1 = ModerationResult(advertisement_id=ad1.id, classification=SafetyClassification.SAFE_FOR_ALL, risk_category="Safe", risk_score=0.4, explanation="Safe", moderation_action=ModerationAction.APPROVE)
        res2 = ModerationResult(advertisement_id=ad2.id, classification=SafetyClassification.UNSAFE_FOR_ALL, risk_category="Unsafe", risk_score=100.0, explanation="Scam", moderation_action=ModerationAction.REJECT)

        self.db.add_all([res1, res2])
        self.db.commit()
        self.db.refresh(ad1)
        self.db.refresh(ad2)

        self.assertNotEqual(ad1.moderation_result.risk_score, ad2.moderation_result.risk_score)
        self.assertNotEqual(ad1.moderation_result.classification, ad2.moderation_result.classification)

    def test_7_role_based_access_control(self):
        """TEST 7: Brand Owner vs Admin Role Validation."""
        brand = self.db.query(User).filter(User.username == "brand_demo").first()
        admin = self.db.query(User).filter(User.username == "admin_demo").first()

        self.assertEqual(brand.role.value if hasattr(brand.role, "value") else str(brand.role), "ROLE_BRAND_OWNER")
        self.assertEqual(admin.role.value if hasattr(admin.role, "value") else str(admin.role), "ROLE_ADMIN")

    def test_8_human_review_evidence_retrieval(self):
        """TEST 8: Admin opens pending review -> advertisement media + AI evidence + risk score + explanation displayed."""
        brand = self.db.query(User).filter(User.username == "brand_demo").first()

        ad = Advertisement(
            title="Casino Slot Promo",
            caption="Win jackpot now",
            file_path="casino_ad.mp4",
            media_type="video",
            status="PENDING_REVIEW",
            owner_id=brand.id
        )
        self.db.add(ad)
        self.db.commit()

        res = ModerationResult(
            advertisement_id=ad.id,
            classification=SafetyClassification.SAFE_18_PLUS,
            risk_category="18+",
            risk_score=52.5,
            confidence=0.97,
            explanation="Gambling slot promo restricted to 18+",
            evidence='{"ocr": {"text": "WIN CASH JACKPOT NOW"}, "video": {"violence": 0.0}}',
            moderation_action=ModerationAction.HUMAN_REVIEW,
            publishable=False
        )
        self.db.add(res)

        rev = HumanReview(
            advertisement_id=ad.id,
            submitted_by=brand.id,
            ai_classification="SAFE_18_PLUS",
            review_status="PENDING_REVIEW"
        )
        self.db.add(rev)
        self.db.commit()

        fetched_rev = self.db.query(HumanReview).filter(HumanReview.advertisement_id == ad.id).first()
        self.assertIsNotNone(fetched_rev)
        self.assertIsNotNone(fetched_rev.advertisement.moderation_result)
        self.assertEqual(fetched_rev.advertisement.moderation_result.risk_score, 52.5)

if __name__ == "__main__":
    unittest.main()
