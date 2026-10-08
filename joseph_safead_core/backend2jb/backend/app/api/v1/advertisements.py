import os
import json
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app.db.database import get_db
from backend.app.db.models import User, Advertisement, ModerationResult, HumanReview, AuditLog, SafetyClassification, ModerationAction, AgeGroup
from backend.app.schemas.moderation import StandardizedModerationResponse, AdUploadResponse, HumanReviewSubmissionRequest, AcceptAIResponse
from backend.app.services.ai_client_service import AIClientService
from backend.app.services.policy_service import PolicyService

router = APIRouter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=AdUploadResponse)
async def upload_advertisement(
    file: UploadFile = File(...),
    title: str = Form(...),
    caption: Optional[str] = Form(""),
    user_id: int = Form(1),
    db: Session = Depends(get_db)
):
    """
    Step 1 of Brand Owner workflow: Upload advertisement creative.
    Stores metadata in DB with status UPLOADED. Does NOT trigger expensive AI inference yet.
    """
    file_ext = os.path.splitext(file.filename)[1].lower()
    filename = f"mod_{int(time.time())}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    content = await file.read()
    file_size = len(content)
    with open(file_path, "wb") as f:
        f.write(content)
        
    media_type = "video" if file_ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"] else "image"
    
    ad = Advertisement(
        title=title,
        caption=caption,
        file_path=file_path,
        media_type=media_type,
        status="UPLOADED",
        owner_id=user_id
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    
    audit = AuditLog(
        ad_id=ad.id,
        user_id=user_id,
        action="BRAND_OWNER_UPLOADED_AD",
        details=f"Uploaded creative '{title}' ({media_type.upper()}, {file_size} bytes)"
    )
    db.add(audit)
    db.commit()

    return {
        "id": ad.id,
        "title": ad.title,
        "caption": ad.caption or "",
        "filename": file.filename,
        "file_path": file_path,
        "media_type": media_type,
        "file_size": file_size,
        "uploaded_at": str(ad.created_at or datetime.now()),
        "status": "UPLOADED"
    }

@router.post("/{id}/analyze", response_model=StandardizedModerationResponse)
async def analyze_advertisement_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Step 2 of Brand Owner workflow: Trigger AI inference for an uploaded advertisement.
    Executes the full SafeAd AI multimodal pipeline.
    """
    ad = db.query(Advertisement).filter(Advertisement.id == id).first()
    if not ad:
        raise HTTPException(status_code=404, detail=f"Advertisement ID #{id} not found.")
        
    if ad.status == "DELETED":
        raise HTTPException(status_code=400, detail="Cannot analyze a deleted advertisement.")

    ad.status = "ANALYZING"
    db.commit()

    ai_results = AIClientService.process_advertisement(ad.file_path, ad.title, ad.caption or "")

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

    ad.status = "AI_ANALYZED"
    requires_hitl = ai_results.get("requires_human_review", False) or publication_action == ModerationAction.HUMAN_REVIEW

    if ad.moderation_result:
        mod_result = ad.moderation_result
        mod_result.classification = classification_enum
        mod_result.risk_category = ai_results.get("display_label", classification_str)
        mod_result.risk_score = ai_results.get("risk_score", 0.0)
        mod_result.confidence = ai_results.get("confidence", 0.85)
        mod_result.explanation = ai_results.get("explanation", "Completed safety audit.")
        mod_result.evidence = json.dumps(ai_results.get("evidence", {}))
        mod_result.moderation_action = publication_action
        mod_result.age_restriction = 18 if classification_enum == SafetyClassification.SAFE_18_PLUS else (14 if classification_enum == SafetyClassification.SAFE_14_PLUS else None)
        mod_result.publishable = publication_action not in [ModerationAction.REJECT, ModerationAction.HUMAN_REVIEW]
        mod_result.processing_time_seconds = ai_results.get("total_processing_time_seconds", 0.0)
    else:
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
            is_human_reviewed=False
        )
        db.add(mod_result)

    audit = AuditLog(
        ad_id=ad.id,
        user_id=ad.owner_id or 1,
        action="AI_ANALYZED",
        details=f"AI inference completed. Classification: {classification_str} | Risk Score: {ai_results.get('risk_score')}/100"
    )
    db.add(audit)
    db.commit()

    return {
        "ad_id": ad.id,
        "status": "AI_ANALYZED",
        "classification": classification_enum,
        "display_label": ai_results.get("display_label", classification_enum.value),
        "risk_score": mod_result.risk_score,
        "confidence": mod_result.confidence,
        "publication_action": publication_action,
        "action_badge": ai_results.get("action_badge", f"{publication_action.value} — {classification_enum.value}"),
        "publishable": mod_result.publishable,
        "requires_human_review": requires_hitl,
        "human_review_required": requires_hitl,
        "prohibited_content_detected": ai_results.get("prohibited_content_detected", False),
        "age_restriction": ai_results.get("age_restriction"),
        "policy_stage": ai_results.get("policy_stage", "POLICY_ENGINE"),
        "policy_reasons": ai_results.get("policy_reasons", []),
        "detected_categories": ai_results.get("detected_categories", []),
        "violations": ai_results.get("dominant_risks", []),
        "explanation": ai_results.get("explanation", ""),
        "evidence": ai_results.get("evidence", {}),
        "extracted_ocr": ai_results.get("extracted_ocr", ""),
        "audio_transcript": ai_results.get("audio_transcript", ""),
        "processing_time_seconds": mod_result.processing_time_seconds
    }

@router.get("/{id}")
def get_advertisement_by_id(id: int, db: Session = Depends(get_db)):
    """Retrieves full metadata, AI results, and review state for an advertisement."""
    ad = db.query(Advertisement).filter(Advertisement.id == id).first()
    if not ad:
        raise HTTPException(status_code=404, detail=f"Advertisement ID #{id} not found.")

    res = ad.moderation_result
    evidence_dict = {}
    if res and res.evidence:
        try:
            evidence_dict = json.loads(res.evidence)
        except Exception:
            pass

    review_info = None
    if ad.human_review:
        review_info = {
            "review_id": ad.human_review.id,
            "status": ad.human_review.review_status,
            "human_decision": ad.human_review.human_decision,
            "review_comment": ad.human_review.review_comment,
            "submitted_at": str(ad.human_review.submitted_at),
            "reviewed_at": str(ad.human_review.reviewed_at) if ad.human_review.reviewed_at else None
        }

    return {
        "id": ad.id,
        "ad_id": ad.id,
        "title": ad.title,
        "caption": ad.caption,
        "file_path": ad.file_path,
        "media_type": ad.media_type,
        "status": ad.status,
        "owner_id": ad.owner_id,
        "created_at": str(ad.created_at),
        "classification": res.classification.value if res else "UNANALYZED",
        "risk_score": res.risk_score if res else None,
        "confidence": res.confidence if res else None,
        "explanation": res.explanation if res else "",
        "publishable": res.publishable if res else False,
        "evidence": evidence_dict,
        "human_review": review_info
    }

@router.post("/{id}/accept-ai", response_model=AcceptAIResponse)
def accept_ai_decision(id: int, db: Session = Depends(get_db)):
    """
    Brand Owner accepts the AI classification.
    Status transitions to AI_ACCEPTED. If classification is UNSAFE_FOR_ALL, normal publication remains blocked.
    """
    ad = db.query(Advertisement).filter(Advertisement.id == id).first()
    if not ad:
        raise HTTPException(status_code=404, detail=f"Advertisement ID #{id} not found.")

    if ad.status == "DELETED":
        raise HTTPException(status_code=400, detail="Cannot accept a deleted advertisement.")

    res = ad.moderation_result
    classification = res.classification.value if res else "UNSAFE_FOR_ALL"

    ad.status = "AI_ACCEPTED"

    if classification == "UNSAFE_FOR_ALL":
        if res:
            res.publishable = False
        message = "Advertisement is classified as Unsafe for All and should not be published."
        publishable = False
    elif classification == "SAFE_18_PLUS":
        if res:
            res.publishable = True
        message = "Advertisement accepted with 18+ age restriction."
        publishable = True
    elif classification == "SAFE_14_PLUS":
        if res:
            res.publishable = True
        message = "Advertisement accepted with 14+ age restriction."
        publishable = True
    else:
        if res:
            res.publishable = True
        message = "Advertisement approved for all age groups."
        publishable = True

    audit = AuditLog(
        ad_id=ad.id,
        user_id=ad.owner_id or 1,
        action="BRAND_OWNER_ACCEPTED_AI",
        details=f"Brand owner accepted AI decision ({classification}). Publishable: {publishable}"
    )
    db.add(audit)
    db.commit()

    return {
        "ad_id": ad.id,
        "status": "AI_ACCEPTED",
        "accepted": True,
        "publishable": publishable,
        "classification": classification,
        "message": message
    }

@router.delete("/{id}")
def delete_advertisement(id: int, db: Session = Depends(get_db)):
    """
    Brand Owner deletes an advertisement.
    Sets status to DELETED and marks non-publishable while preserving audit trail.
    """
    ad = db.query(Advertisement).filter(Advertisement.id == id).first()
    if not ad:
        raise HTTPException(status_code=404, detail=f"Advertisement ID #{id} not found.")

    ad.status = "DELETED"
    if ad.moderation_result:
        ad.moderation_result.publishable = False

    audit = AuditLog(
        ad_id=ad.id,
        user_id=ad.owner_id or 1,
        action="BRAND_OWNER_DELETED_AD",
        details="Brand owner deleted advertisement."
    )
    db.add(audit)
    db.commit()

    return {
        "id": id,
        "status": "DELETED",
        "message": "Advertisement deleted successfully."
    }

@router.post("/{id}/human-review")
def send_for_human_review(
    id: int,
    req: Optional[HumanReviewSubmissionRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Brand Owner submits an advertisement for Admin Human Review.
    Creates HumanReview record in PENDING_REVIEW status.
    """
    ad = db.query(Advertisement).filter(Advertisement.id == id).first()
    if not ad:
        raise HTTPException(status_code=404, detail=f"Advertisement ID #{id} not found.")

    if ad.status == "DELETED":
        raise HTTPException(status_code=400, detail="Cannot submit a deleted advertisement for review.")

    user_id = req.user_id if req else 1
    reason = req.reason if req else ""

    ad.status = "PENDING_REVIEW"
    res = ad.moderation_result
    ai_class = res.classification.value if res else "UNKNOWN"

    if res:
        res.moderation_action = ModerationAction.HUMAN_REVIEW
        res.is_human_reviewed = False

    human_rev = db.query(HumanReview).filter(HumanReview.advertisement_id == ad.id).first()
    if not human_rev:
        human_rev = HumanReview(
            advertisement_id=ad.id,
            submitted_by=user_id,
            ai_classification=ai_class,
            review_status="PENDING_REVIEW",
            review_comment=reason,
            submitted_at=datetime.now()
        )
        db.add(human_rev)
    else:
        human_rev.review_status = "PENDING_REVIEW"
        human_rev.review_comment = reason
        human_rev.submitted_at = datetime.now()

    audit = AuditLog(
        ad_id=ad.id,
        user_id=user_id,
        action="SUBMITTED_FOR_HUMAN_REVIEW",
        details=f"Brand owner requested human review. Reason: {reason or 'N/A'}"
    )
    db.add(audit)
    db.commit()

    return {
        "id": ad.id,
        "review_id": human_rev.id,
        "status": "PENDING_REVIEW",
        "message": "Your advertisement has been submitted for human review."
    }

@router.post("/check", response_model=StandardizedModerationResponse)
async def check_advertisement(
    file: UploadFile = File(...),
    title: str = Form(...),
    caption: Optional[str] = Form(""),
    user_id: int = Form(1),
    db: Session = Depends(get_db)
):
    """Submits advertisement media for AI safety checking and policy evaluation."""
    from backend.app.api.v1.moderation import moderate_advertisement
    return await moderate_advertisement(file=file, title=title, caption=caption, user_id=user_id, db=db)

@router.get("/user_feed")
def get_user_feed(user_age_group: str = "AGE_18_PLUS", db: Session = Depends(get_db)):
    """Returns age-filtered advertisements eligible for the specified user age group."""
    try:
        user_group_enum = AgeGroup(user_age_group)
    except Exception:
        user_group_enum = AgeGroup.AGE_18_PLUS

    ads = db.query(Advertisement).filter(Advertisement.status.in_(["AI_ACCEPTED", "HUMAN_ACCEPTED"])).all()
    filtered_ads = []

    for ad in ads:
        if ad.moderation_result and ad.moderation_result.publishable:
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
