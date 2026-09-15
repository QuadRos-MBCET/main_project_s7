from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import Advertisement, ModerationResult, AuditLog, ModerationAction
from backend.app.schemas.moderation import ModerationOverrideRequest

router = APIRouter()

@router.get("/pending")
def get_pending_moderations(db: Session = Depends(get_db)):
    ads = db.query(Advertisement).filter(Advertisement.status.in_(["PENDING", "RESTRICT"])).all()
    out = []
    for ad in ads:
        res = ad.moderation_result
        out.append({
            "id": ad.id,
            "title": ad.title,
            "caption": ad.caption,
            "file_path": ad.file_path,
            "media_type": ad.media_type,
            "status": ad.status,
            "classification": res.classification.value if res else "UNKNOWN",
            "risk_score": res.risk_score if res else None,
            "explanation": res.explanation if res else "Pending review"
        })
    return out

@router.post("/override")
def override_moderation(req: ModerationOverrideRequest, db: Session = Depends(get_db)):
    ad = db.query(Advertisement).filter(Advertisement.id == req.ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
        
    ad.status = req.action.value
    
    if ad.moderation_result:
        ad.moderation_result.moderation_action = req.action
        ad.moderation_result.explanation += f" [ADMIN OVERRIDE: {req.notes}]"
        
    audit = AuditLog(
        ad_id=ad.id,
        user_id=1,  # Admin user context
        action=f"ADMIN_OVERRIDE_{req.action.value}",
        details=f"Admin manual override to {req.action.value}. Notes: {req.notes}"
    )
    db.add(audit)
    db.commit()
    
    return {"status": "success", "ad_id": ad.id, "new_action": req.action.value}
