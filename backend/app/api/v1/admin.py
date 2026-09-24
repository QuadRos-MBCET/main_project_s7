import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import Advertisement, ModerationResult, HumanReview, AuditLog, ModerationAction, SafetyClassification
from backend.app.schemas.moderation import ModerationOverrideRequest, HumanReviewDecisionRequest

router = APIRouter()

@router.get("/reviews")
def get_admin_reviews(review_status: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Returns list of human review cases for the Admin Dashboard.
    Filters by review_status if provided (e.g., PENDING_REVIEW, HUMAN_ACCEPTED, HUMAN_REJECTED, ALL).
    """
    # Sync any pending advertisements into human_reviews if missing
    pending_ads = db.query(Advertisement).filter(Advertisement.status == "PENDING_REVIEW").all()
    for p_ad in pending_ads:
        existing_rev = db.query(HumanReview).filter(HumanReview.advertisement_id == p_ad.id).first()
        if not existing_rev:
            ai_class = p_ad.moderation_result.classification.value if p_ad.moderation_result else "UNKNOWN"
            new_rev = HumanReview(
                advertisement_id=p_ad.id,
                submitted_by=p_ad.owner_id or 1,
                ai_classification=ai_class,
                review_status="PENDING_REVIEW"
            )
            db.add(new_rev)
    db.commit()

    query = db.query(HumanReview)
    if review_status and review_status.upper() != "ALL":
        query = query.filter(HumanReview.review_status == review_status.upper())

    reviews = query.order_by(HumanReview.submitted_at.desc()).all()

    out = []
    for rev in reviews:
        ad = rev.advertisement
        res = ad.moderation_result if ad else None
        evidence_dict = {}
        if res and res.evidence:
            try:
                evidence_dict = json.loads(res.evidence)
            except Exception:
                pass

        out.append({
            "review_id": rev.id,
            "ad_id": ad.id if ad else None,
            "title": ad.title if ad else "N/A",
            "caption": ad.caption if ad else "",
            "file_path": ad.file_path if ad else "",
            "media_type": ad.media_type if ad else "image",
            "ad_status": ad.status if ad else "UNKNOWN",
            "ai_classification": rev.ai_classification or (res.classification.value if res else "UNKNOWN"),
            "risk_score": res.risk_score if res else None,
            "confidence": res.confidence if res else 0.50,
            "explanation": res.explanation if res else "",
            "evidence": evidence_dict,
            "review_status": rev.review_status,
            "human_decision": rev.human_decision,
            "review_comment": rev.review_comment,
            "submitted_by": rev.submitted_by,
            "admin_id": rev.admin_id,
            "submitted_at": str(rev.submitted_at),
            "reviewed_at": str(rev.reviewed_at) if rev.reviewed_at else None
        })

    return out

@router.get("/reviews/{id}")
def get_admin_review_by_id(id: int, db: Session = Depends(get_db)):
    """Gets detailed view of a single human review case including media path and full AI evidence."""
    rev = db.query(HumanReview).filter(
        (HumanReview.id == id) | (HumanReview.advertisement_id == id)
    ).first()

    if not rev:
        ad = db.query(Advertisement).filter(Advertisement.id == id).first()
        if not ad:
            raise HTTPException(status_code=404, detail=f"Human review case or Advertisement #{id} not found.")
        rev = HumanReview(
            advertisement_id=ad.id,
            submitted_by=ad.owner_id or 1,
            ai_classification=ad.moderation_result.classification.value if ad.moderation_result else "UNKNOWN",
            review_status="PENDING_REVIEW"
        )
        db.add(rev)
        db.commit()
        db.refresh(rev)

    ad = rev.advertisement
    res = ad.moderation_result if ad else None
    evidence_dict = {}
    if res and res.evidence:
        try:
            evidence_dict = json.loads(res.evidence)
        except Exception:
            pass

    return {
        "review_id": rev.id,
        "ad_id": ad.id if ad else None,
        "title": ad.title if ad else "N/A",
        "caption": ad.caption if ad else "",
        "file_path": ad.file_path if ad else "",
        "media_type": ad.media_type if ad else "image",
        "ad_status": ad.status if ad else "UNKNOWN",
        "ai_classification": rev.ai_classification or (res.classification.value if res else "UNKNOWN"),
        "risk_score": res.risk_score if res else None,
        "confidence": res.confidence if res else 0.50,
        "explanation": res.explanation if res else "",
        "evidence": evidence_dict,
        "ocr_text": res.evidence and json.loads(res.evidence).get("ocr", {}).get("text", "") if res and res.evidence else "",
        "audio_transcript": res.evidence and json.loads(res.evidence).get("audio", {}).get("transcript", "") if res and res.evidence else "",
        "review_status": rev.review_status,
        "human_decision": rev.human_decision,
        "review_comment": rev.review_comment,
        "submitted_by": rev.submitted_by,
        "admin_id": rev.admin_id,
        "submitted_at": str(rev.submitted_at),
        "reviewed_at": str(rev.reviewed_at) if rev.reviewed_at else None
    }

@router.post("/reviews/{id}/accept")
def accept_human_review(
    id: int,
    req: Optional[HumanReviewDecisionRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Admin accepts the advertisement for publication.
    Updates status to HUMAN_ACCEPTED and marks publishable = True.
    """
    rev = db.query(HumanReview).filter(
        (HumanReview.id == id) | (HumanReview.advertisement_id == id)
    ).first()

    if not rev:
        ad = db.query(Advertisement).filter(Advertisement.id == id).first()
        if not ad:
            raise HTTPException(status_code=404, detail=f"Human review case or Advertisement #{id} not found.")
        rev = HumanReview(
            advertisement_id=ad.id,
            submitted_by=ad.owner_id or 1,
            ai_classification=ad.moderation_result.classification.value if ad.moderation_result else "UNKNOWN",
            review_status="PENDING_REVIEW"
        )
        db.add(rev)
        db.commit()
        db.refresh(rev)

    admin_id = req.admin_id if req else 2
    comment = req.review_comment if req else "Reviewed manually. Content is acceptable under project safety policy."

    rev.review_status = "HUMAN_ACCEPTED"
    rev.human_decision = "ACCEPT"
    rev.admin_id = admin_id
    rev.review_comment = comment
    rev.reviewed_at = datetime.now()

    ad = rev.advertisement
    if ad:
        ad.status = "HUMAN_ACCEPTED"
        if ad.moderation_result:
            ad.moderation_result.moderation_action = ModerationAction.APPROVE
            ad.moderation_result.publishable = True
            ad.moderation_result.is_human_reviewed = True
            ad.moderation_result.moderator_id = admin_id
            ad.moderation_result.moderator_notes = comment

    audit = AuditLog(
        ad_id=ad.id if ad else None,
        user_id=admin_id,
        action="ADMIN_ACCEPTED_HUMAN_REVIEW",
        details=f"Admin ACCEPTED advertisement. Comment: {comment}"
    )
    db.add(audit)
    db.commit()

    return {
        "review_id": rev.id,
        "ad_id": ad.id if ad else None,
        "review_status": "HUMAN_ACCEPTED",
        "human_decision": "ACCEPT",
        "publishable": True,
        "message": "Human review decision accepted. Advertisement approved for publication."
    }

@router.post("/reviews/{id}/reject")
def reject_human_review(
    id: int,
    req: Optional[HumanReviewDecisionRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Admin rejects the advertisement.
    Updates status to HUMAN_REJECTED and marks publishable = False.
    """
    rev = db.query(HumanReview).filter(
        (HumanReview.id == id) | (HumanReview.advertisement_id == id)
    ).first()

    if not rev:
        ad = db.query(Advertisement).filter(Advertisement.id == id).first()
        if not ad:
            raise HTTPException(status_code=404, detail=f"Human review case or Advertisement #{id} not found.")
        rev = HumanReview(
            advertisement_id=ad.id,
            submitted_by=ad.owner_id or 1,
            ai_classification=ad.moderation_result.classification.value if ad.moderation_result else "UNKNOWN",
            review_status="PENDING_REVIEW"
        )
        db.add(rev)
        db.commit()
        db.refresh(rev)

    admin_id = req.admin_id if req else 2
    comment = req.review_comment if req else "Advertisement contains prohibited content and must not be published."

    rev.review_status = "HUMAN_REJECTED"
    rev.human_decision = "REJECT"
    rev.admin_id = admin_id
    rev.review_comment = comment
    rev.reviewed_at = datetime.now()

    ad = rev.advertisement
    if ad:
        ad.status = "HUMAN_REJECTED"
        if ad.moderation_result:
            ad.moderation_result.moderation_action = ModerationAction.REJECT
            ad.moderation_result.publishable = False
            ad.moderation_result.is_human_reviewed = True
            ad.moderation_result.moderator_id = admin_id
            ad.moderation_result.moderator_notes = comment

    audit = AuditLog(
        ad_id=ad.id if ad else None,
        user_id=admin_id,
        action="ADMIN_REJECTED_HUMAN_REVIEW",
        details=f"Admin REJECTED advertisement. Comment: {comment}"
    )
    db.add(audit)
    db.commit()

    return {
        "review_id": rev.id,
        "ad_id": ad.id if ad else None,
        "review_status": "HUMAN_REJECTED",
        "human_decision": "REJECT",
        "publishable": False,
        "message": "Human review decision rejected. Advertisement blocked from publication."
    }

@router.get("/pending")
def get_pending_moderations(db: Session = Depends(get_db)):
    """Returns advertisements queued for human moderator review."""
    ads = db.query(Advertisement).filter(
        Advertisement.status.in_(["PENDING_REVIEW", "HUMAN_REVIEW", "PENDING", "RESTRICT"])
    ).all()

    out = []
    for ad in ads:
        res = ad.moderation_result
        evidence_dict = {}
        if res and res.evidence:
            try:
                evidence_dict = json.loads(res.evidence)
            except Exception:
                pass

        out.append({
            "id": ad.id,
            "title": ad.title,
            "caption": ad.caption,
            "file_path": ad.file_path,
            "media_type": ad.media_type,
            "status": ad.status,
            "classification": res.classification.value if res else "REQUIRES_HUMAN_REVIEW",
            "risk_score": res.risk_score if res else None,
            "confidence": res.confidence if res else 0.50,
            "explanation": res.explanation if res else "Queued for human moderator review.",
            "evidence": evidence_dict,
            "created_at": str(ad.created_at) if ad.created_at else ""
        })
    return out

@router.post("/override")
def override_moderation(req: ModerationOverrideRequest, db: Session = Depends(get_db)):
    """Submits a human moderator decision with target classification override."""
    ad = db.query(Advertisement).filter(Advertisement.id == req.ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    ad.status = req.action.value

    if ad.moderation_result:
        ad.moderation_result.moderation_action = req.action
        ad.moderation_result.classification = req.final_classification or SafetyClassification.SAFE_FOR_ALL
        ad.moderation_result.is_human_reviewed = True
        ad.moderation_result.moderator_notes = req.moderator_notes
        ad.moderation_result.explanation += f" [HUMAN MODERATOR OVERRIDE: {req.moderator_notes}]"
        ad.moderation_result.publishable = req.action != ModerationAction.REJECT

    audit = AuditLog(
        ad_id=ad.id,
        user_id=1,
        action=f"HUMAN_MODERATOR_OVERRIDE_{req.action.value}",
        details=f"Human moderator override to {req.action.value} ({req.final_classification.value}). Notes: {req.moderator_notes}"
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "ad_id": ad.id,
        "new_action": req.action.value,
        "final_classification": req.final_classification.value
    }
