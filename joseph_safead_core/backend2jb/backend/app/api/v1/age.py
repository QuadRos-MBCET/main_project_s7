from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.db.database import get_db
from backend.app.db.models import User
from backend.app.schemas.user import AgeVerificationRequest, UserResponse
from backend.app.services.age_service import AgeVerificationService

router = APIRouter()

@router.post("/verify", response_model=UserResponse)
def verify_age(req: AgeVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    try:
        dob = datetime.strptime(req.date_of_birth, "%Y-%m-%d")
    except ValueError:
        dob = user.date_of_birth
        
    # Execute verification logic
    res = AgeVerificationService.verify_user_age(dob, face_image=req.face_image_base64)
    
    # Store result in DB
    user.date_of_birth = dob
    user.age_verification_status = res["status"]
    user.verified_age_group = res["verified_age_group"]
    user.chronological_age = res["chronological_age"]
    user.estimated_age = res["estimated_age"]
    
    db.commit()
    db.refresh(user)
    return user
