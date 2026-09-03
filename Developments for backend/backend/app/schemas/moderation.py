from pydantic import BaseModel
from typing import List, Optional
from app.db.models import SafetyClassification, ModerationAction

class PredictionSchema(BaseModel):
    classification: SafetyClassification
    risk_score: float
    risk_score_available: bool
    risk_category: str
    explanation: str
    evidence: List[str]
    model_version: str

class ModerationResultOut(BaseModel):
    advertisement_id: int
    classification: SafetyClassification
    risk_category: Optional[str]
    risk_score: Optional[float]
    risk_score_available: bool
    explanation: str
    age_restriction: Optional[int]
    moderation_action: ModerationAction
    publishable: bool
    model_version: str

    class Config:
        from_attributes = True
