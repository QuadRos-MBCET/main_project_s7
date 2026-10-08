from typing import Dict, Any, Optional

class AudioEventDetector:
    """
    Architectural extension point for non-speech acoustic event classification.
    
    CURRENT RELEASE SCOPE:
    - SafeAd AI Step 2 active scope: Speech-to-text (STT) transcription via OpenAI Whisper.
    - Future extension scope: Acoustic event classifier (e.g. gunshots, screaming, explosions, glass breaking).
    """

    def __init__(self):
        self.mode = "speech_only_active"

    def detect_events(self, wav_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Stub method returning structured acoustic event detection payload.
        """
        return {
            "events_detected": [],
            "acoustic_risk_score": 0.0,
            "status": "speech_only_mode",
            "message": "Acoustic event classification reserved for future release extension. Speech STT active."
        }
