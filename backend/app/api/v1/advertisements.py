import os
import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app.db.database import get_db
from backend.app.db.models import User, Advertisement, ModerationResult, AuditLog, SafetyClassification, AgeGroup
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
    1. Validates input
    2. Saves media to disk
    3. Executes Colab/AI pipeline
    4. Evaluates policy & publication action
    5. Stores results in MySQL/SQLite
    6. Returns standardized JSON response
    """
    # Save file
    file_ext = os.path.splitext(file.filename)[1].lower()
    filename = f"ad_{int(time.time())}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    media_type = "video" if file_ext in [".mp4", ".avi", ".mov"] else "image"
    
    # Create DB record
    ad = Advertisement(
        title=title,
        caption=caption,
        file_path=file_path,
        media_type=media_type,
        status="PROCESSING",
        owner_id=user_id
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    
    # Run AI inference
    ai_results = AIClientService.process_advertisement(file_path, title, caption)
    
    classification_str = ai_results.get("classification", "UNSAFE_FOR_ALL")
    try:
        classification_enum = SafetyClassification(classification_str)
    except Exception:
        classification_enum = SafetyClassification.UNSAFE_FOR_ALL
        
    publication_action = PolicyService.determine_publication_action(classification_enum)
    ad.status = publication_action.value
    
    # Create Moderation Result
    mod_result = ModerationResult(
        advertisement_id=ad.id,
        model_version="SafeAd_V1_ColabFree",
        classification=classification_enum,
        risk_category=ai_results.get("risk_category", "general_audience"),
        risk_score=ai_results.get("risk_score", None),
        risk_score_available=ai_results.get("risk_score_available", False),
        explanation=ai_results.get("explanation", "Completed safety audit."),
        evidence=str(ai_results.get("violations", [])),
        moderation_action=publication_action,
        age_restriction=ai_results.get("age_restriction", None),
        publishable=ai_results.get("publishable", False)
    )
    db.add(mod_result)
    
    # Audit log entry
    log_entry = AuditLog(
        ad_id=ad.id,
        user_id=user_id,
        action=publication_action.value,
        details=f"Processed via SafeAd AI Pipeline. Classification: {classification_str}"
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "ad_id": ad.id,
        "classification": classification_enum,
        "risk_score": mod_result.risk_score,
        "risk_score_available": mod_result.risk_score_available,
        "risk_category": mod_result.risk_category,
        "explanation": mod_result.explanation,
        "age_restriction": mod_result.age_restriction,
        "action": publication_action,
        "publishable": mod_result.publishable,
        "violations": ai_results.get("violations", []),
        "extracted_ocr": ai_results.get("extracted_ocr", "OCR scan completed."),
        "detected_objects": ai_results.get("detected_objects", ["Object scanning complete."]),
        "generated_caption": ai_results.get("generated_caption", "Visual feature extraction complete."),
        "faiss_match": ai_results.get("faiss_match", {"title": "Vector Exemplar Index Searched", "distance": 0.0})
    }

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
