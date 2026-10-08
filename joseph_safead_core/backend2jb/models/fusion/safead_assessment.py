from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class SafeAdAssessment:
    """
    Central SafeAd Assessment Matrix Data Structure.
    Collects structured safety evidence across all modalities prior to SafeAdFusion.
    """
    visual: Dict[str, Any] = field(default_factory=lambda: {
        "violence": 0.0,
        "adult": 0.0,
        "child_safety": 0.0,
        "other_unsafe": 0.0,
        "unsafe": False,
        "evidence": []
    })
    
    video: Dict[str, Any] = field(default_factory=lambda: {
        "violence": 0.0,
        "adult": 0.0,
        "child_safety": 0.0,
        "other_unsafe": 0.0,
        "sampled_segments": []
    })
    
    ocr: Dict[str, Any] = field(default_factory=lambda: {
        "text": "",
        "violence": 0.0,
        "adult": 0.0,
        "child_safety": 0.0,
        "scam": 0.0,
        "deceptive": 0.0,
        "confidence": 0.0,
        "evidence": []
    })
    
    audio: Dict[str, Any] = field(default_factory=lambda: {
        "audio_available": False,
        "language": "N/A",
        "transcript": "",
        "violence": 0.0,
        "adult": 0.0,
        "child_safety": 0.0,
        "scam": 0.0,
        "deceptive": 0.0,
        "evidence": []
    })
    
    text_safety: Dict[str, Any] = field(default_factory=lambda: {
        "categories": {},
        "overall_risk": 0.0,
        "evidence": []
    })
    
    advertisement_risks: Dict[str, Any] = field(default_factory=lambda: {
        "scam": 0.0,
        "deceptive_marketing": 0.0,
        "explicit_content": 0.0,
        "evidence": []
    })

    prohibited_risks: List[str] = field(default_factory=list)
    prohibited_confidence: float = 0.0
    policy_stage: str = "INITIALIZED"
    policy_reasons: List[str] = field(default_factory=list)

    @classmethod
    def from_modalities(
        cls,
        visual: Dict[str, Any] = None,
        video: Dict[str, Any] = None,
        ocr: Dict[str, Any] = None,
        audio: Dict[str, Any] = None,
        text_safety: Dict[str, Any] = None,
        advertisement_risks: Dict[str, Any] = None
    ) -> "SafeAdAssessment":
        """Constructs a SafeAdAssessment object from modality outputs."""
        return cls(
            visual=visual or {},
            video=video or {},
            ocr=ocr or {},
            audio=audio or {},
            text_safety=text_safety or {},
            advertisement_risks=advertisement_risks or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts SafeAdAssessment matrix into a JSON-serializable dictionary."""
        return {
            "visual": self.visual,
            "video": self.video,
            "ocr": self.ocr,
            "audio": self.audio,
            "text_safety": self.text_safety,
            "advertisement_risks": self.advertisement_risks,
            "prohibited_risks": self.prohibited_risks,
            "prohibited_confidence": self.prohibited_confidence,
            "policy_stage": self.policy_stage,
            "policy_reasons": self.policy_reasons
        }
