from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from backend.app.db.models import UserRole, AgeGroup

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    date_of_birth: str  # YYYY-MM-DD string

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    role: str
    verified_age_group: str

class AgeVerificationRequest(BaseModel):
    user_id: int
    date_of_birth: str
    face_image_base64: Optional[str] = None

class AgeEstimateRequest(BaseModel):
    image_base64: Optional[str] = None
    preset: Optional[str] = None

class AgeEstimateResponse(BaseModel):
    success: bool
    faces_detected: int
    estimated_age: Optional[float] = None
    age_range_label: Optional[str] = None
    user_category: Optional[str] = None
    database_age_group: Optional[str] = None
    confidence: Optional[float] = None
    is_spoof: Optional[bool] = False
    spoof_score: Optional[float] = 0.0
    spoof_reason: Optional[str] = ""
    error: Optional[str] = None
    message: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    verified_age_group: Optional[AgeGroup] = None
    chronological_age: Optional[int] = None
    age_verification_status: str
    
    class Config:
        from_attributes = True
