import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import Advertisement, ModerationResult, AuditLog, ModerationAction, SafetyClassification
from backend.app.schemas.moderation import ModerationOverrideRequest

router = APIRouter()

@router.get("/pending")
def get_pending_moderations(db: Session = Depends(get_db)):
    """
    Returns advertisements queued for human moderator review (e.g. low confidence / conflicting modalities / borderline scores).
    """
    ads = db.query(Advertisement).filter(
        Advertisement.status.in_(["HUMAN_REVIEW", "PENDING", "RESTRICT"])
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
    """
    Submits a human moderator decision (APPROVE / AGE RESTRICT / REJECT) with target classification override.
    """
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
        user_id=1,  # Moderator user context
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
