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
    res = AgeVerificationService.verify_user_age(dob, image_input=req.face_image_base64)
    
    # Store result in DB
    user.date_of_birth = dob
    user.age_verification_status = res["status"]
    user.verified_age_group = res["verified_age_group"]
    user.chronological_age = res["chronological_age"]
    user.estimated_age = res["estimated_age"]
    
    db.commit()
    db.refresh(user)
    return user

@router.post("/estimate")
def estimate_facial_age(req: dict):
    """
    Direct face detection and age estimation endpoint for registration.
    Invokes FaceAgeAdapter (MTCNN/ViT + Anti-spoof + Haar Cascade fallback).
    """
    try:
        from face_age_adapter import face_age_adapter
        from camera_handler import CameraHandler
    except ImportError:
        import sys
        from pathlib import Path
        cam_dir = Path(__file__).resolve().parent.parent.parent.parent / "camera-integration"
        if str(cam_dir) not in sys.path:
            sys.path.insert(0, str(cam_dir))
        from face_age_adapter import face_age_adapter
        from camera_handler import CameraHandler

    img_input = req.get("image_base64")
    preset = req.get("preset")
    if not img_input and preset:
        synth = CameraHandler.generate_synthetic_face(preset)
        img_input = CameraHandler.frame_to_base64(synth)

    if not img_input:
        raise HTTPException(status_code=400, detail="Missing image data or preset.")

    result = face_age_adapter.process_frame(img_input)
    return result
