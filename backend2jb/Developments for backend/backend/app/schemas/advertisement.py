from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AdvertisementBase(BaseModel):
    title: str
    caption: Optional[str] = None

class AdvertisementCreate(AdvertisementBase):
    pass

class AdvertisementOut(AdvertisementBase):
    id: int
    file_path: str
    media_type: str
    status: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
