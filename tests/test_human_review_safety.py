"""
Unit & Integration Tests for Backend Human-Review Publication Safeguards (Phase 7A Task 4).

Verifies that advertisements routed to REQUIRES_HUMAN_REVIEW cannot appear in:
1. Public or age-filtered feed queries at the database & authorization layer.
2. The protected backend media-serving endpoint (HTTP 403 Forbidden).
3. Any user age tier (UNDER_14, AGE_14_TO_17, AGE_18_PLUS).
"""

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.db.database import Base, get_db
from backend.app.db.models import (
    User, Advertisement, ModerationResult,
    SafetyClassification, ModerationAction, AgeGroup
)
from backend.app.services.policy_service import PolicyService

from sqlalchemy.pool import StaticPool

# In-memory SQLite for testing with StaticPool so all connections share the same memory DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


def test_policy_service_requires_human_review_mapping():
    """Verify PolicyService maps REQUIRES_HUMAN_REVIEW to ModerationAction.HUMAN_REVIEW."""
    action = PolicyService.determine_publication_action(SafetyClassification.REQUIRES_HUMAN_REVIEW)
    assert action == ModerationAction.HUMAN_REVIEW


def test_policy_service_withholds_human_review_from_all_age_tiers():
    """Verify evaluate_user_access strictly denies REQUIRES_HUMAN_REVIEW for all age groups."""
    for age_group in [AgeGroup.UNDER_14, AgeGroup.AGE_14_TO_17, AgeGroup.AGE_18_PLUS]:
        assert not PolicyService.evaluate_user_access(
            SafetyClassification.REQUIRES_HUMAN_REVIEW,
            age_group
        ), f"Failed to withhold human review for {age_group}"


def test_policy_service_withholds_unsafe_from_all_age_tiers():
    """Verify evaluate_user_access strictly denies UNSAFE_FOR_ALL for all age groups."""
    for age_group in [AgeGroup.UNDER_14, AgeGroup.AGE_14_TO_17, AgeGroup.AGE_18_PLUS]:
        assert not PolicyService.evaluate_user_access(
            SafetyClassification.UNSAFE_FOR_ALL,
            age_group
        ), f"Failed to withhold unsafe content for {age_group}"


def test_user_feed_excludes_human_review_and_unsafe_ads():
    """Verify that get_user_feed never serves REQUIRES_HUMAN_REVIEW, UNSAFE_FOR_ALL, or PENDING ads."""
    db = TestingSessionLocal()
    
    # 1. Approved Safe ad
    ad_safe = Advertisement(title="Safe Food Ad", file_path="sample.jpg", status="APPROVE", owner_id=1)
    db.add(ad_safe)
    db.flush()
    mod_safe = ModerationResult(
        advertisement_id=ad_safe.id,
        classification=SafetyClassification.SAFE_FOR_ALL,
        moderation_action=ModerationAction.APPROVE,
        risk_category="general",
        explanation="Safe",
        publishable=True
    )
    db.add(mod_safe)

    # 2. Human Review Ad
    ad_hitl = Advertisement(title="Ambiguous Violent Action Ad", file_path="brawl.mp4", status="HUMAN_REVIEW", owner_id=1)
    db.add(ad_hitl)
    db.flush()
    mod_hitl = ModerationResult(
        advertisement_id=ad_hitl.id,
        classification=SafetyClassification.REQUIRES_HUMAN_REVIEW,
        moderation_action=ModerationAction.HUMAN_REVIEW,
        risk_category="ambiguous_violence",
        explanation="Conflict between visual and video motion",
        publishable=False
    )
    db.add(mod_hitl)

    # 3. Unsafe / Prohibited Ad
    ad_unsafe = Advertisement(title="Phishing Scam Ad", file_path="scam.jpg", status="REJECT", owner_id=1)
    db.add(ad_unsafe)
    db.flush()
    mod_unsafe = ModerationResult(
        advertisement_id=ad_unsafe.id,
        classification=SafetyClassification.UNSAFE_FOR_ALL,
        moderation_action=ModerationAction.REJECT,
        risk_category="scam",
        explanation="Prohibited deceptive scheme",
        publishable=False
    )
    db.add(mod_unsafe)

    # 4. Pending unmoderated Ad
    ad_pending = Advertisement(title="Unmoderated Ad", file_path="pending.jpg", status="PENDING", owner_id=1)
    db.add(ad_pending)

    db.commit()

    # Query feed for adults
    res = client.get("/api/v1/advertisements/user_feed?user_age_group=AGE_18_PLUS")
    assert res.status_code == 200
    feed_ads = res.json()
    feed_ids = [a["id"] for a in feed_ads]

    assert ad_safe.id in feed_ids
    assert ad_hitl.id not in feed_ids, "CRITICAL VULNERABILITY: Human review ad appeared in user feed!"
    assert ad_unsafe.id not in feed_ids, "CRITICAL VULNERABILITY: Unsafe ad appeared in user feed!"
    assert ad_pending.id not in feed_ids, "CRITICAL VULNERABILITY: Pending unmoderated ad appeared in user feed!"
    db.close()


def test_media_serving_endpoint_blocks_human_review_and_unsafe():
    """Verify backend media serving endpoint denies access (HTTP 403) to unapproved & human review ads."""
    db = TestingSessionLocal()
    
    # Create test media file on disk
    dummy_media_path = os.path.abspath("test_dummy_media.jpg")
    with open(dummy_media_path, "wb") as f:
        f.write(b"DUMMY_IMAGE_DATA")

    try:
        # Ad 1: Human Review
        ad_hitl = Advertisement(title="HITL Ad", file_path=dummy_media_path, status="HUMAN_REVIEW", owner_id=1)
        db.add(ad_hitl)
        db.flush()
        mod_hitl = ModerationResult(
            advertisement_id=ad_hitl.id,
            classification=SafetyClassification.REQUIRES_HUMAN_REVIEW,
            moderation_action=ModerationAction.HUMAN_REVIEW,
            risk_category="violence_conflict",
            explanation="Requires human check",
            publishable=False
        )
        db.add(mod_hitl)

        # Ad 2: Safe Ad
        ad_safe = Advertisement(title="Safe Ad", file_path=dummy_media_path, status="APPROVE", owner_id=1)
        db.add(ad_safe)
        db.flush()
        mod_safe = ModerationResult(
            advertisement_id=ad_safe.id,
            classification=SafetyClassification.SAFE_FOR_ALL,
            moderation_action=ModerationAction.APPROVE,
            risk_category="safe",
            explanation="Approved",
            publishable=True
        )
        db.add(mod_safe)

        db.commit()

        # Request media for Human Review ad -> MUST BE 403 FORBIDDEN
        res_hitl = client.get(f"/api/v1/advertisements/{ad_hitl.id}/media")
        assert res_hitl.status_code == 403, f"Expected 403 for HITL ad media, got {res_hitl.status_code}"
        assert "Publication Withheld" in res_hitl.json()["detail"]

        # Request media for Safe ad -> MUST BE 200 OK
        res_safe = client.get(f"/api/v1/advertisements/{ad_safe.id}/media")
        assert res_safe.status_code == 200
        assert res_safe.content == b"DUMMY_IMAGE_DATA"

    finally:
        db.close()
        if os.path.exists(dummy_media_path):
            os.remove(dummy_media_path)
