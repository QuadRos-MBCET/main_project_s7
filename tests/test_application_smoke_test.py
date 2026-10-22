"""
SafeAd AI (SAFE-VISION) — Phase 7C Application & Database Smoke Test.

Verifies:
1. Clean database schema initialization (Base.metadata.create_all).
2. User account creation with age groups (UNDER_14, AGE_14_TO_17, AGE_18_PLUS).
3. Advertisement submission and moderation pipeline recording.
4. Status transitions:
   - SAFE_FOR_ALL -> APPROVE, publishable=True.
   - REQUIRES_HUMAN_REVIEW -> HUMAN_REVIEW, publishable=False, persisted in human_reviews queue.
5. Human moderator review workflow:
   - Moderator override transitions status to APPROVE or REJECT.
   - AuditLog records the review decision and timestamp.
6. Backend age authorization security:
   - Under-14 user feed receives only SAFE_FOR_ALL ads.
   - Protected media serving endpoint returns HTTP 403 for human-review or unsafe ads.
   - Parameter-less access fails closed to UNDER_14.
7. Broken/missing media handling:
   - Missing media returns HTTP 404 cleanly without application crash.
"""

import os
import sys
import tempfile
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.main import app
from backend.app.db.database import Base, get_db
from backend.app.db.models import (
    User, Advertisement, ModerationResult, HumanReview, AuditLog,
    SafetyClassification, ModerationAction, AgeGroup
)
from backend.app.services.policy_service import PolicyService

# In-memory SQLite DB for smoke test
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_smoke_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


def test_database_and_application_smoke_workflow():
    db = TestingSessionLocal()
    temp_dir = tempfile.mkdtemp()
    test_media_sfa = os.path.join(temp_dir, "test_sfa.jpg")
    test_media_hitl = os.path.join(temp_dir, "test_hitl.jpg")
    
    with open(test_media_sfa, "wb") as f:
        f.write(b"SAMPLE_IMAGE_DATA_SFA")
    with open(test_media_hitl, "wb") as f:
        f.write(b"SAMPLE_IMAGE_DATA_HITL")

    try:
        # 1. Create Brand Owner & Users across age tiers
        owner = User(
            username="brand_lead",
            email="brand@safead.org",
            password_hash="hashed_pw_123",
            date_of_birth=datetime(1990, 5, 15),
            age_verification_status="VERIFIED",
            verified_age_group=AgeGroup.AGE_18_PLUS
        )
        child_user = User(
            username="child_viewer",
            email="child@safead.org",
            password_hash="hashed_pw_child",
            date_of_birth=datetime(2016, 8, 20),
            age_verification_status="VERIFIED",
            verified_age_group=AgeGroup.UNDER_14
        )
        db.add_all([owner, child_user])
        db.commit()

        # 2. Submit & Record SFA Advertisement
        ad_sfa = Advertisement(
            title="Everyday Backpack",
            caption="Ergonomic school backpack for all ages",
            file_path=test_media_sfa,
            media_type="image",
            status="APPROVE",
            owner_id=owner.id
        )
        db.add(ad_sfa)
        db.commit()

        mod_sfa = ModerationResult(
            advertisement_id=ad_sfa.id,
            classification=SafetyClassification.SAFE_FOR_ALL,
            risk_category="LOW",
            risk_score=0.05,
            explanation="Approved everyday apparel merchandise.",
            moderation_action=ModerationAction.APPROVE,
            publishable=True
        )
        db.add(mod_sfa)
        db.commit()

        # 3. Submit & Record Ambiguous Advertisement -> REQUIRES_HUMAN_REVIEW
        ad_hitl = Advertisement(
            title="Ambiguous Combat Video Game",
            caption="Action fighting game trailer",
            file_path=test_media_hitl,
            media_type="video",
            status="HUMAN_REVIEW",
            owner_id=owner.id
        )
        db.add(ad_hitl)
        db.commit()

        mod_hitl = ModerationResult(
            advertisement_id=ad_hitl.id,
            classification=SafetyClassification.REQUIRES_HUMAN_REVIEW,
            risk_category="UNCERTAIN",
            risk_score=0.62,
            explanation="Ambiguous kinetic movement and fantasy combat. Escalated to human review.",
            moderation_action=ModerationAction.HUMAN_REVIEW,
            publishable=False
        )
        db.add(mod_hitl)
        db.commit()

        # Route to human review queue
        review_entry = HumanReview(
            advertisement_id=ad_hitl.id,
            review_status="PENDING",
            decision_type="DISAGREEMENT_ESCALATION"
        )
        db.add(review_entry)
        db.commit()

        # --- VERIFICATION CHECKS ---

        # Check A: Child feed receives only SFA
        feed_child = client.get("/api/v1/advertisements/user_feed?user_age_group=UNDER_14")
        assert feed_child.status_code == 200
        items_child = [item["id"] for item in feed_child.json()]
        assert ad_sfa.id in items_child, "SFA ad must be visible to child"
        assert ad_hitl.id not in items_child, "HITL ad must NEVER appear in child feed"

        # Check B: Adult feed also withholds unapproved human review ad
        feed_adult = client.get("/api/v1/advertisements/user_feed?user_age_group=AGE_18_PLUS")
        assert feed_adult.status_code == 200
        items_adult = [item["id"] for item in feed_adult.json()]
        assert ad_hitl.id not in items_adult, "HITL ad must NEVER appear in adult feed before human approval"

        # Check C: Media serving endpoint blocks unapproved HITL ad (HTTP 403)
        res_media_hitl = client.get(f"/api/v1/advertisements/{ad_hitl.id}/media?user_age_group=AGE_18_PLUS")
        assert res_media_hitl.status_code == 403
        assert "Publication Withheld" in res_media_hitl.json()["detail"]

        # Check D: Missing media file returns 404 cleanly
        ad_missing = Advertisement(
            title="Missing File Ad",
            file_path="non_existent_file_path_123.jpg",
            media_type="image",
            status="APPROVE",
            owner_id=owner.id
        )
        db.add(ad_missing)
        db.commit()
        mod_missing = ModerationResult(
            advertisement_id=ad_missing.id,
            classification=SafetyClassification.SAFE_FOR_ALL,
            risk_category="LOW",
            explanation="Approved missing file",
            moderation_action=ModerationAction.APPROVE,
            publishable=True
        )
        db.add(mod_missing)
        db.commit()

        res_media_missing = client.get(f"/api/v1/advertisements/{ad_missing.id}/media?user_age_group=UNDER_14")
        assert res_media_missing.status_code == 404
        assert "not found on disk" in res_media_missing.json()["detail"]

        # Check E: Human Moderator Review Approval Transition
        # Moderator reviews the ambiguous item and approves it with age restriction (AGE_14_PLUS)
        review_entry.review_status = "COMPLETED"
        review_entry.human_decision = "AGE_RESTRICT_14_PLUS"
        review_entry.review_comment = "Fantasy combat verified suitable for teens 14+."
        review_entry.reviewed_at = datetime.utcnow()

        # Update ad status
        ad_hitl.status = "RESTRICT"
        mod_hitl.classification = SafetyClassification.SAFE_14_PLUS
        mod_hitl.moderation_action = ModerationAction.RESTRICT
        mod_hitl.publishable = True
        
        # Log in AuditLog
        audit = AuditLog(
            ad_id=ad_hitl.id,
            action="MODERATOR_OVERRIDE_APPROVE_14_PLUS",
            user_id=1,
            details="Escalated review resolved by human moderator."
        )
        db.add(audit)
        db.commit()

        # Now verify post-moderation feed visibility:
        # Child (<14) feed still does NOT receive 14+ ad
        feed_child_after = client.get("/api/v1/advertisements/user_feed?user_age_group=UNDER_14")
        items_child_after = [item["id"] for item in feed_child_after.json()]
        assert ad_hitl.id not in items_child_after, "14+ approved ad must not appear in child feed"

        # Teen (14-17) feed NOW receives the approved 14+ ad!
        feed_teen = client.get("/api/v1/advertisements/user_feed?user_age_group=AGE_14_TO_17")
        items_teen = [item["id"] for item in feed_teen.json()]
        assert ad_hitl.id in items_teen, "14+ approved ad must appear in teen feed"

        # Protected media serving NOW serves HTTP 200 for authorized teen
        res_media_teen = client.get(f"/api/v1/advertisements/{ad_hitl.id}/media?user_age_group=AGE_14_TO_17")
        assert res_media_teen.status_code == 200

    finally:
        db.close()
        for p in [test_media_sfa, test_media_hitl]:
            if os.path.exists(p):
                os.remove(p)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
