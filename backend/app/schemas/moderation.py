from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.app.db.models import SafetyClassification, ModerationAction

class StandardizedModerationResponse(BaseModel):
    ad_id: int
    status: str = "success"
    classification: SafetyClassification
    display_label: str
    risk_score: Optional[float] = None
    confidence: Optional[float] = None
    publication_action: ModerationAction
    action_badge: str
    publishable: bool
    detected_categories: List[str] = []
    violations: List[str] = []
    explanation: str
    evidence: Dict[str, Any] = {}
    extracted_ocr: Optional[str] = ""
    audio_transcript: Optional[str] = ""
    processing_time_seconds: Optional[float] = None

    class Config:
        from_attributes = True

class ModerationOverrideRequest(BaseModel):
    ad_id: int
    action: ModerationAction
    notes: Optional[str] = ""
