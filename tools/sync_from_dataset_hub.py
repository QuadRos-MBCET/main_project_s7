"""
sync_from_dataset_hub.py
------------------------
Imports approved images and reels from safead-dataset-hub into main_project_s7's database.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

HUB_ROOT = PROJECT_ROOT.parent
MANIFEST_PATH = HUB_ROOT / "app_content" / "content_manifest.json"

from backend.app.db.database import SessionLocal, engine, Base
from backend.app.db.models import Advertisement, ModerationResult, SafetyClassification, ModerationAction, User, UserRole, AgeGroup
from datetime import datetime

CATEGORY_MAP = {
    "SAFE_FOR_ALL": SafetyClassification.SAFE_FOR_ALL,
    "SAFE_14_PLUS": SafetyClassification.AGE_14_PLUS,
    "SAFE_18_PLUS": SafetyClassification.AGE_18_PLUS
}

def sync():
    Base.metadata.create_all(bind=engine)
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.id == 1).first()
        if not admin:
            admin = User(
                id=1,
                username="admin",
                email="admin@safead.ai",
                password_hash="system_seed",
                date_of_birth=datetime(1995, 1, 1),
                age_verification_status="VERIFIED",
                verified_age_group=AgeGroup.AGE_18_PLUS,
                role=UserRole.ADMIN
            )
            db.add(admin)
            db.commit()

        items = data.get("content_items", [])
        added_count = 0

        for item in items:
            abs_media_path = str((HUB_ROOT / item["media_path"]).resolve())
            
            # Check existing
            existing = db.query(Advertisement).filter(Advertisement.file_path == abs_media_path).first()
            if existing:
                continue

            classification = CATEGORY_MAP.get(item["age_category"], SafetyClassification.SAFE_FOR_ALL)
            action = ModerationAction.APPROVE if classification == SafetyClassification.SAFE_FOR_ALL else ModerationAction.RESTRICT

            ad = Advertisement(
                title=item.get("title", "Approved Content"),
                caption=item.get("caption", ""),
                file_path=abs_media_path,
                media_type="video" if item.get("content_type") == "reel" else "image",
                status="APPROVED",
                owner_id=admin.id
            )
            db.add(ad)
            db.commit()
            db.refresh(ad)

            mod_result = ModerationResult(
                advertisement_id=ad.id,
                model_version="SafeAd_DatasetHub_V1",
                classification=classification,
                risk_category="general_creative",
                risk_score=0.0,
                risk_score_available=True,
                explanation=item.get("caption", "Approved dataset item"),
                evidence=f"Source: {item.get('source_name')}; License: {item.get('license_status')}",
                moderation_action=action,
                age_restriction=item.get("minimum_age", 0),
                publishable=True
            )
            db.add(mod_result)
            db.commit()
            added_count += 1

        print(f"Successfully synced {added_count} approved items into main_project_s7 database.")
        print(f"Total advertisements in DB: {db.query(Advertisement).count()}")
    finally:
        db.close()

if __name__ == "__main__":
    sync()
