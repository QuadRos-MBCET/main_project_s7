import os
import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.db.database import get_db
from backend.app.db.models import Advertisement, ModerationResult, AuditLog, SafetyClassification
from backend.app.schemas.moderation import StandardizedModerationResponse
from backend.app.services.ai_client_service import AIClientService
from backend.app.services.policy_service import PolicyService

router = APIRouter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/moderate", response_model=StandardizedModerationResponse)
async def moderate_advertisement(
    file: UploadFile = File(...),
    title: str = Form(...),
    caption: Optional[str] = Form(""),
    user_id: int = Form(1),
    db: Session = Depends(get_db)
):
    """
    Direct endpoint for submitting advertisement media for AI safety checking and policy evaluation.
    """
    file_ext = os.path.splitext(file.filename)[1].lower()
    filename = f"mod_{int(time.time())}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    media_type = "video" if file_ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"] else "image"
    
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
    
    ai_results = AIClientService.process_advertisement(file_path, title, caption)
    
    classification_str = ai_results.get("classification", "UNSAFE_FOR_ALL")
    try:
        classification_enum = SafetyClassification(classification_str)
    except Exception:
        classification_enum = SafetyClassification.UNSAFE_FOR_ALL
        
    publication_action = PolicyService.determine_publication_action(classification_enum)
    ad.status = publication_action.value
    
    mod_result = ModerationResult(
        advertisement_id=ad.id,
        model_version="SafeAd_V2_Multimodal",
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
    
    log_entry = AuditLog(
        ad_id=ad.id,
        user_id=user_id,
        action=publication_action.value,
        details=f"Moderated via SafeAd API. Classification: {classification_str}"
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
        "violations": ai_results.get("violations", [])
    }

@router.get("/history", response_model=List[StandardizedModerationResponse])
def get_moderation_history(limit: int = 50, db: Session = Depends(get_db)):
    results = db.query(ModerationResult).order_by(ModerationResult.id.desc()).limit(limit).all()
    history = []
    for r in results:
        history.append({
            "ad_id": r.advertisement_id,
            "classification": r.classification,
            "risk_score": r.risk_score,
            "risk_score_available": r.risk_score_available,
            "risk_category": r.risk_category,
            "explanation": r.explanation,
            "age_restriction": r.age_restriction,
            "action": r.moderation_action,
            "publishable": r.publishable,
            "violations": eval(r.evidence) if r.evidence and r.evidence.startswith("[") else []
        })
    return history

@router.get("/logs")
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    return [{
        "id": l.id,
        "ad_id": l.ad_id,
        "user_id": l.user_id,
        "action": l.action,
        "details": l.details,
        "timestamp": l.timestamp
    } for l in logs]
