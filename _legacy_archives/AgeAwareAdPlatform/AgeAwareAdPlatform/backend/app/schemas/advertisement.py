from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AdvertisementCreate(BaseModel):
    title: str
    caption: Optional[str] = ""

class AdvertisementResponse(BaseModel):
    id: int
    title: str
    caption: Optional[str] = None
    file_path: str
    media_type: str
    status: str
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
