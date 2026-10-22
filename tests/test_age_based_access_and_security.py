"""
Comprehensive Integration Tests for Age-Based Access & Backend Security (Phase 7B Task 5).

Verifies:
1. Feed listing tier gating:
   - Under 14: SAFE_FOR_ALL only.
   - Ages 14-17: SAFE_FOR_ALL and SAFE_14_PLUS.
   - Ages 18+: SAFE_FOR_ALL, SAFE_14_PLUS, and SAFE_18_PLUS.
   - UNSAFE_FOR_ALL: Blocked for everyone.
   - REQUIRES_HUMAN_REVIEW: Blocked for everyone until authorized approval.
2. Direct media endpoint authorization (/api/v1/advertisements/{id}/media):
   - Direct URL requests check age tier and safety status.
   - Unauthorized access raises HTTP 403 Forbidden.
   - Prohibited and human-review media cannot be downloaded by anyone.
3. Safe fallback behavior when facial age estimation conflicts with claimed DOB.
4. Absence of unauthenticated public static route bypasses.
"""

import os
import sys
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
    User, Advertisement, ModerationResult,
    SafetyClassification, ModerationAction, AgeGroup
)
from backend.app.services.policy_service import PolicyService
from backend.app.services.age_service import AgeVerificationService

# Shared in-memory DB for tests
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


def test_feed_listing_strict_age_gating_tiers():
    """Verify that get_user_feed strictly enforces age-tier boundaries and blocks unsafe/hitl content."""
    db = TestingSessionLocal()
    
    # 1. SAFE_FOR_ALL ad
    ad_sfa = Advertisement(title="SFA Ad", file_path="sfa.jpg", status="APPROVE", owner_id=1)
    db.add(ad_sfa)
    db.flush()
    db.add(ModerationResult(advertisement_id=ad_sfa.id, classification=SafetyClassification.SAFE_FOR_ALL, moderation_action=ModerationAction.APPROVE, risk_category="general", explanation="ok", publishable=True))

    # 2. AGE_14_PLUS ad
    ad_14p = Advertisement(title="14P Ad", file_path="14p.jpg", status="RESTRICT", owner_id=1)
    db.add(ad_14p)
    db.flush()
    db.add(ModerationResult(advertisement_id=ad_14p.id, classification=SafetyClassification.AGE_14_PLUS, moderation_action=ModerationAction.RESTRICT, risk_category="teen", explanation="ok", age_restriction=14, publishable=True))

    # 3. AGE_18_PLUS ad
    ad_18p = Advertisement(title="18P Ad", file_path="18p.jpg", status="RESTRICT", owner_id=1)
    db.add(ad_18p)
    db.flush()
    db.add(ModerationResult(advertisement_id=ad_18p.id, classification=SafetyClassification.AGE_18_PLUS, moderation_action=ModerationAction.RESTRICT, risk_category="adult", explanation="ok", age_restriction=18, publishable=True))

    # 4. UNSAFE_FOR_ALL ad
    ad_ufa = Advertisement(title="UFA Ad", file_path="ufa.jpg", status="REJECT", owner_id=1)
    db.add(ad_ufa)
    db.flush()
    db.add(ModerationResult(advertisement_id=ad_ufa.id, classification=SafetyClassification.UNSAFE_FOR_ALL, moderation_action=ModerationAction.REJECT, risk_category="prohibited", explanation="rejected", publishable=False))

    # 5. REQUIRES_HUMAN_REVIEW ad
    ad_hitl = Advertisement(title="HITL Ad", file_path="hitl.jpg", status="HUMAN_REVIEW", owner_id=1)
    db.add(ad_hitl)
    db.flush()
    db.add(ModerationResult(advertisement_id=ad_hitl.id, classification=SafetyClassification.REQUIRES_HUMAN_REVIEW, moderation_action=ModerationAction.HUMAN_REVIEW, risk_category="audit", explanation="pending", publishable=False))

    db.commit()

    # Tier 1: UNDER_14
    res_u14 = client.get("/api/v1/advertisements/user_feed?user_age_group=UNDER_14")
    assert res_u14.status_code == 200
    ids_u14 = [a["id"] for a in res_u14.json()]
    assert ids_u14 == [ad_sfa.id], f"UNDER_14 received forbidden ads: {ids_u14}"

    # Tier 2: AGE_14_TO_17
    res_teen = client.get("/api/v1/advertisements/user_feed?user_age_group=AGE_14_TO_17")
    assert res_teen.status_code == 200
    ids_teen = [a["id"] for a in res_teen.json()]
    assert set(ids_teen) == {ad_sfa.id, ad_14p.id}, f"AGE_14_TO_17 expected [SFA, 14P], got: {ids_teen}"

    # Tier 3: AGE_18_PLUS
    res_adult = client.get("/api/v1/advertisements/user_feed?user_age_group=AGE_18_PLUS")
    assert res_adult.status_code == 200
    ids_adult = [a["id"] for a in res_adult.json()]
    assert set(ids_adult) == {ad_sfa.id, ad_14p.id, ad_18p.id}, f"AGE_18_PLUS expected [SFA, 14P, 18P], got: {ids_adult}"
    assert ad_ufa.id not in ids_adult
    assert ad_hitl.id not in ids_adult

    db.close()


def test_direct_media_endpoint_authorization_and_url_protection():
    """Verify that direct media retrieval enforces authorization and blocks bypasses."""
    db = TestingSessionLocal()
    dummy_file = os.path.abspath("test_auth_media.jpg")
    with open(dummy_file, "wb") as f:
        f.write(b"PROTECTED_MEDIA_CONTENT")

    try:
        # Create ads
        ad_18p = Advertisement(title="18+ Ad", file_path=dummy_file, status="RESTRICT", owner_id=1)
        db.add(ad_18p)
        db.flush()
        db.add(ModerationResult(advertisement_id=ad_18p.id, classification=SafetyClassification.AGE_18_PLUS, moderation_action=ModerationAction.RESTRICT, risk_category="adult", explanation="ok", age_restriction=18, publishable=True))

        ad_hitl = Advertisement(title="HITL Ad", file_path=dummy_file, status="HUMAN_REVIEW", owner_id=1)
        db.add(ad_hitl)
        db.flush()
        db.add(ModerationResult(advertisement_id=ad_hitl.id, classification=SafetyClassification.REQUIRES_HUMAN_REVIEW, moderation_action=ModerationAction.HUMAN_REVIEW, risk_category="review", explanation="pending", publishable=False))

        ad_ufa = Advertisement(title="UFA Ad", file_path=dummy_file, status="REJECT", owner_id=1)
        db.add(ad_ufa)
        db.flush()
        db.add(ModerationResult(advertisement_id=ad_ufa.id, classification=SafetyClassification.UNSAFE_FOR_ALL, moderation_action=ModerationAction.REJECT, risk_category="prohibited", explanation="rejected", publishable=False))

        db.commit()

        # 1. Under-14 requesting 18+ media -> MUST BE 403
        r1 = client.get(f"/api/v1/advertisements/{ad_18p.id}/media?user_age_group=UNDER_14")
        assert r1.status_code == 403
        assert "Access Restricted" in r1.json()["detail"]

        # 2. Teen (14-17) requesting 18+ media -> MUST BE 403
        r2 = client.get(f"/api/v1/advertisements/{ad_18p.id}/media?user_age_group=AGE_14_TO_17")
        assert r2.status_code == 403
        assert "Access Restricted" in r2.json()["detail"]

        # 3. Adult requesting 18+ media -> 200 OK
        r3 = client.get(f"/api/v1/advertisements/{ad_18p.id}/media?user_age_group=AGE_18_PLUS")
        assert r3.status_code == 200
        assert r3.content == b"PROTECTED_MEDIA_CONTENT"

        # 4. Adult requesting REQUIRES_HUMAN_REVIEW media -> MUST BE 403
        r4 = client.get(f"/api/v1/advertisements/{ad_hitl.id}/media?user_age_group=AGE_18_PLUS")
        assert r4.status_code == 403
        assert "Publication Withheld" in r4.json()["detail"]

        # 5. Adult requesting UNSAFE_FOR_ALL media -> MUST BE 403
        r5 = client.get(f"/api/v1/advertisements/{ad_ufa.id}/media?user_age_group=AGE_18_PLUS")
        assert r5.status_code == 403
        assert "Publication Withheld" in r5.json()["detail"]

    finally:
        db.close()
        if os.path.exists(dummy_file):
            os.remove(dummy_file)


def test_safe_fallback_on_conflicting_age_estimation():
    """Verify that age verification falls back safely to the more restrictive tier on discrepancy."""
    # Scenario 1: DOB claims age 25, but facial estimation detects child (e.g. 10.0)
    # Child safety priority: MUST flag CONFLICT_CHILD_DETECTED and restrict to UNDER_14
    dob_adult = datetime(2000, 1, 1)
    res_child_conflict = AgeVerificationService.verify_user_age(dob=dob_adult, face_image="child_photo.jpg")
    assert res_child_conflict["status"] == "CONFLICT_CHILD_DETECTED"
    assert res_child_conflict["verified_age_group"] == AgeGroup.UNDER_14

    # Scenario 2: Normal consistent child
    dob_child = datetime(2015, 6, 1)
    res_child = AgeVerificationService.verify_user_age(dob=dob_child, face_image="child_photo.jpg")
    assert res_child["status"] == "VERIFIED"
    assert res_child["verified_age_group"] == AgeGroup.UNDER_14

    # Scenario 3: Normal consistent adult
    res_adult = AgeVerificationService.verify_user_age(dob=dob_adult, face_image=None)
    assert res_adult["status"] == "VERIFIED"
    assert res_adult["verified_age_group"] == AgeGroup.AGE_18_PLUS


def test_no_unauthenticated_static_route_bypass():
    """Verify that the FastAPI application does not mount unauthenticated public static routes to uploads."""
    routes = [r.path for r in app.routes]
    # Verify /uploads or /media is not directly exposed as StaticFiles mount
    assert "/uploads" not in routes, "SECURITY VULNERABILITY: /uploads is directly exposed via static mount!"
    assert "/media" not in routes, "SECURITY VULNERABILITY: /media is directly exposed via static mount!"


def test_fail_closed_unauthenticated_and_uncertain_age_defaults():
    """Verify that unauthenticated or uncertain requests strictly fail-closed to UNDER_14."""
    db = TestingSessionLocal()
    dummy_file = os.path.abspath("test_fail_closed.jpg")
    with open(dummy_file, "wb") as f:
        f.write(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB")

    try:
        ad_sfa = Advertisement(title="SFA Ad", file_path=dummy_file, status="APPROVE", owner_id=1)
        ad_18p = Advertisement(title="18+ Ad", file_path=dummy_file, status="APPROVE", owner_id=1)
        db.add_all([ad_sfa, ad_18p])
        db.commit()

        mod_sfa = ModerationResult(
            advertisement_id=ad_sfa.id,
            classification=SafetyClassification.SAFE_FOR_ALL,
            moderation_action=ModerationAction.APPROVE,
            risk_category="LOW",
            explanation="Safe for all",
            publishable=True
        )
        mod_18p = ModerationResult(
            advertisement_id=ad_18p.id,
            classification=SafetyClassification.SAFE_18_PLUS,
            moderation_action=ModerationAction.RESTRICT,
            risk_category="MODERATE",
            explanation="Adult restricted",
            publishable=True
        )
        db.add_all([mod_sfa, mod_18p])
        db.commit()

        # 1. Unauthenticated / Parameter-less feed query -> MUST default to UNDER_14 (only SFA returned)
        r_feed = client.get("/api/v1/advertisements/user_feed")
        assert r_feed.status_code == 200
        feed_ids = [item["id"] for item in r_feed.json()]
        assert ad_sfa.id in feed_ids, "SFA ad must be returned for fail-closed default"
        assert ad_18p.id not in feed_ids, "18+ ad MUST NOT be returned when age parameter is omitted!"

        # 2. Unauthenticated / Parameter-less media access to 18+ ad -> MUST fail closed to 403 Forbidden
        r_media_no_param = client.get(f"/api/v1/advertisements/{ad_18p.id}/media")
        assert r_media_no_param.status_code == 403
        assert "Access Restricted" in r_media_no_param.json()["detail"]

        # 3. Malformed age group -> MUST fail closed to 403 Forbidden
        r_media_malformed = client.get(f"/api/v1/advertisements/{ad_18p.id}/media?user_age_group=INVALID_ATTEMPT")
        assert r_media_malformed.status_code == 403

        # 4. Parameter-less access to SFA ad -> ALLOWED
        r_media_sfa = client.get(f"/api/v1/advertisements/{ad_sfa.id}/media")
        assert r_media_sfa.status_code == 200

    finally:
        db.close()
        if os.path.exists(dummy_file):
            os.remove(dummy_file)
