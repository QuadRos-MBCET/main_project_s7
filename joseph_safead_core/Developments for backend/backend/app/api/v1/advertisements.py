import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Advertisement, User
from app.schemas.advertisement import AdvertisementOut
from app.core.config import settings

router = APIRouter()

# Dependency to get current user (mocked for now since auth middleware isn't fully wired)
def get_current_user_mock(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

@router.post("/", response_model=AdvertisementOut, status_code=status.HTTP_201_CREATED)
async def submit_advertisement(
    title: str = Form(...),
    caption: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_mock)
):
    # Validate file type
    allowed_content_types = ["image/jpeg", "image/png", "video/mp4", "video/avi", "video/quicktime"]
    if file.content_type not in allowed_content_types:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    
    # Ensure upload dir exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Store in DB
    ad = Advertisement(
        title=title,
        caption=caption,
        file_path=file_path,
        media_type=file.content_type,
        owner_id=current_user.id
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    
    # Here we would normally trigger background processing.
    # For now we just return the ad object.
    
    return ad
