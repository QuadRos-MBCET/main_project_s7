from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.app.db.models import SafetyClassification, ModerationAction

class StandardizedModerationResponse(BaseModel):
    ad_id: int
    status: str = "completed"
    classification: SafetyClassification
    display_label: str
    risk_score: Optional[float] = None
    confidence: Optional[float] = 0.85
    publication_action: ModerationAction
    action_badge: str
    publishable: bool
    requires_human_review: bool = False
    human_review_required: bool = False
    prohibited_content_detected: bool = False
    age_restriction: Optional[str] = None
    policy_stage: Optional[str] = "POLICY_ENGINE"
    policy_reasons: List[str] = []
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
    final_classification: Optional[SafetyClassification] = SafetyClassification.SAFE_FOR_ALL
    moderator_notes: Optional[str] = ""
