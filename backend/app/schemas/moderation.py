from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from backend.app.db.models import SafetyClassification, ModerationAction

class StandardizedModerationResponse(BaseModel):
    ad_id: int
    classification: SafetyClassification
    risk_score: Optional[float] = None
    risk_score_available: bool
    risk_category: str
    explanation: str
    age_restriction: Optional[int] = None
    action: ModerationAction
    publishable: bool
    violations: Optional[List[str]] = []
    
    class Config:
        from_attributes = True

class ModerationOverrideRequest(BaseModel):
    ad_id: int
    action: ModerationAction
    notes: Optional[str] = ""
