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
