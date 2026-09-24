import os
import json
import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.db.database import get_db
from backend.app.db.models import Advertisement, ModerationResult, AuditLog, SafetyClassification, ModerationAction
from backend.app.schemas.moderation import StandardizedModerationResponse, ModerationOverrideRequest
from backend.app.services.ai_client_service import AIClientService
from backend.app.services.policy_service import PolicyService

router = APIRouter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/moderate", response_model=StandardizedModerationResponse)
@router.post("/analyze", response_model=StandardizedModerationResponse)
async def moderate_advertisement(
    file: UploadFile = File(...),
    title: str = Form(...),
    caption: Optional[str] = Form(""),
    user_id: int = Form(1),
    db: Session = Depends(get_db)
):
    """
    Submits advertisement media for AI safety checking, SafeAdAssessment matrix synthesis,
    and policy evaluation.    """
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
        
    action_str = ai_results.get("publication_action", "REJECT")
    try:
        publication_action = ModerationAction(action_str)
    except Exception:
        publication_action = PolicyService.determine_publication_action(classification_enum)
        
    ad.status = publication_action.value
    requires_hitl = ai_results.get("requires_human_review", False) or publication_action == ModerationAction.HUMAN_REVIEW
    
    mod_result = ModerationResult(
        advertisement_id=ad.id,
        model_version="SafeAd_V2_Multimodal",
        classification=classification_enum,
        risk_category=ai_results.get("display_label", classification_str),
        risk_score=ai_results.get("risk_score", 0.0),
        confidence=ai_results.get("confidence", 0.85),
        explanation=ai_results.get("explanation", "Completed safety audit."),
        evidence=json.dumps(ai_results.get("evidence", {})),
        moderation_action=publication_action,
        age_restriction=18 if classification_enum == SafetyClassification.SAFE_18_PLUS else (14 if classification_enum == SafetyClassification.SAFE_14_PLUS else None),
        publishable=publication_action not in [ModerationAction.REJECT, ModerationAction.HUMAN_REVIEW],
        processing_time_seconds=ai_results.get("total_processing_time_seconds", 0.0),
        is_human_reviewed=False    )
    db.add(mod_result)
    
    log_entry = AuditLog(
        ad_id=ad.id,
        user_id=user_id,
        action=publication_action.value,
        details=f"Processed via SafeAd API. Classification: {classification_str} | HITL Queued: {requires_hitl}"
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "ad_id": ad.id,
        "status": "completed",
        "classification": classification_enum,
        "display_label": ai_results.get("display_label", classification_enum.value),
        "risk_score": mod_result.risk_score,
        "confidence": mod_result.confidence,
        "publication_action": publication_action,
        "action_badge": ai_results.get("action_badge", f"{publication_action.value} — {classification_enum.value}"),
        "publishable": mod_result.publishable,
        "requires_human_review": requires_hitl,
        "detected_categories": ai_results.get("detected_categories", []),
        "violations": ai_results.get("dominant_risks", []),
        "explanation": ai_results.get("explanation", ""),
        "evidence": ai_results.get("evidence", {}),
        "extracted_ocr": ai_results.get("extracted_ocr", ""),
        "audio_transcript": ai_results.get("audio_transcript", ""),
        "processing_time_seconds": mod_result.processing_time_seconds
    }

@router.post("/moderate/video", response_model=StandardizedModerationResponse)
async def moderate_video_advertisement(
    file: UploadFile = File(...),
    title: str = Form(...),
    caption: Optional[str] = Form(""),
    user_id: int = Form(1),
    db: Session = Depends(get_db)
):
    """Endpoint specifically for video advertisements."""
    return await moderate_advertisement(file=file, title=title, caption=caption, user_id=user_id, db=db)

@router.get("/{id}", response_model=StandardizedModerationResponse)
def get_moderation_by_id(id: int, db: Session = Depends(get_db)):
    ad = db.query(Advertisement).filter(Advertisement.id == id).first()
    if not ad or not ad.moderation_result:
        raise HTTPException(status_code=404, detail=f"Moderation result for Ad ID #{id} not found.")

    res = ad.moderation_result
    evidence_dict = {}
    try:
        evidence_dict = json.loads(res.evidence) if res.evidence else {}
    except Exception:
        pass

    return {
        "ad_id": ad.id,
        "status": "completed",
        "classification": res.classification,
        "display_label": res.risk_category,
        "risk_score": res.risk_score,
        "confidence": res.confidence,
        "publication_action": res.moderation_action,
        "action_badge": f"{res.moderation_action.value} — {res.classification.value}",
        "publishable": res.publishable,
        "requires_human_review": res.moderation_action == ModerationAction.HUMAN_REVIEW,
        "detected_categories": [],
        "violations": [],
        "explanation": res.explanation,
        "evidence": evidence_dict,
        "processing_time_seconds": res.processing_time_seconds
    }

@router.get("/logs")
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Returns audit logs."""
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    return [{
        "id": l.id,
        "ad_id": l.ad_id,
        "user_id": l.user_id,
        "action": l.action,
        "details": l.details,
        "timestamp": l.timestamp
    } for l in logs]
