import os
import json
import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app.db.database import get_db
from backend.app.db.models import User, Advertisement, ModerationResult, AuditLog, SafetyClassification, ModerationAction, AgeGroup
from backend.app.schemas.moderation import StandardizedModerationResponse
from backend.app.services.ai_client_service import AIClientService
from backend.app.services.policy_service import PolicyService

router = APIRouter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/check", response_model=StandardizedModerationResponse)
async def check_advertisement(
    file: UploadFile = File(...),
    title: str = Form(...),
    caption: Optional[str] = Form(""),
    user_id: int = Form(1),
    db: Session = Depends(get_db)
):
    """
    Submits advertisement media for AI safety checking and policy evaluation.
    Delegates to full moderation pipeline.
    """
    from backend.app.api.v1.moderation import moderate_advertisement
    return await moderate_advertisement(file=file, title=title, caption=caption, user_id=user_id, db=db)

@router.get("/user_feed")
def get_user_feed(user_age_group: str = "AGE_18_PLUS", db: Session = Depends(get_db)):
    """
    Returns age-filtered advertisements eligible for the specified user age group.
    UNSAFE_FOR_ALL content is NEVER included.
    """
    try:
        user_group_enum = AgeGroup(user_age_group)
    except Exception:
        user_group_enum = AgeGroup.AGE_18_PLUS

    ads = db.query(Advertisement).filter(Advertisement.status != "REJECT").all()
    filtered_ads = []

    for ad in ads:
        if ad.moderation_result:
            is_allowed = PolicyService.evaluate_user_access(
                ad.moderation_result.classification,
                user_group_enum
            )
            if is_allowed:
                filtered_ads.append({
                    "id": ad.id,
                    "title": ad.title,
                    "caption": ad.caption,
                    "file_path": ad.file_path,
                    "media_type": ad.media_type,
                    "classification": ad.moderation_result.classification.value,
                    "age_restriction": ad.moderation_result.age_restriction
                })

    return filtered_ads
