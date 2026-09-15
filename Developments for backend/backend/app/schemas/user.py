from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from app.db.models import UserRole, AgeGroup

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    date_of_birth: datetime

class UserOut(UserBase):
    id: int
    role: UserRole
    date_of_birth: datetime
    age_verification_status: str
    verified_age_group: Optional[AgeGroup] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
