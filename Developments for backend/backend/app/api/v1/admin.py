from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, UserRole, ModerationResult

router = APIRouter()

# Mock dependency for Admin enforcement
def get_current_admin_user(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions. Admin required.")
    return user

@router.get("/statistics")
def get_admin_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    """
    Returns high-level moderation statistics for the Admin dashboard.
    """
    total_users = db.query(User).count()
    total_moderations = db.query(ModerationResult).count()
    
    # Simple mockup of statistics aggregation
    stats = {
        "total_users": total_users,
        "total_moderations": total_moderations,
        "system_status": "Operational",
        "active_model_version": "current-development-model-v1"
    }
    return stats
