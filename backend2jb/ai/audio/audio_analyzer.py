from typing import Dict, Any
from ai.audio.speech_transcriber import transcribe_video_audio, SpeechTranscriber
from ai.config import WHISPER_MODEL

class AudioAnalyzer:
    """
    Audio Safety Analysis Branch Coordinator for SafeAd AI.
    Integrates audio extraction, Whisper STT transcription, and formats structured audio evidence.
    """

    def __init__(self, whisper_model: str = WHISPER_MODEL):
        self.transcriber = SpeechTranscriber(model_name=whisper_model)

    def analyze_audio(self, video_path: str) -> Dict[str, Any]:
        """
        Executes end-to-end audio extraction and speech-to-text transcription.
        Returns structured audio evidence dictionary.
        """
        stt_result = self.transcriber.transcribe_video(video_path)

        available = stt_result.get("audio_available", False)
        transcript = stt_result.get("transcript", "")
        language = stt_result.get("detected_language", "N/A")
        status = stt_result.get("status", "no_audio")
        duration = stt_result.get("transcription_duration_seconds", 0.0)

        # Standardized Audio Analysis Evidence Schema
        audio_evidence = {
            "available": available,
            "whisper_model": stt_result.get("whisper_model", f"whisper-{WHISPER_MODEL}"),
            "detected_language": language,
            "transcript": transcript,
            "status": status,
            "message": stt_result.get("message", ""),
            "transcription_duration_seconds": duration,
            "violence": {
                "risk": False,
                "score": None
            },
            "adult_content": {
                "risk": False,
                "score": None
            },
            "child_safety": {
                "risk": False,
                "score": None
            }
        }

        return audio_evidence

    @staticmethod
    def print_audio_analysis_report(audio_info: Dict[str, Any]):
        """Prints standard formatted audio analysis summary card."""
        print("\n" + "=" * 50)
        print("AUDIO ANALYSIS")
        print("=" * 50)
        print(f"Audio Available:   {'YES' if audio_info.get('available') else 'NO'}")
        print(f"Whisper Model:     {audio_info.get('whisper_model', 'N/A')}")
        print(f"Detected Language: {audio_info.get('detected_language', 'N/A')}")
        print("Transcript:")
        tx = audio_info.get('transcript', '')
        if tx:
            print(f'"{tx}"')
        else:
            print('"No spoken speech detected."')
        print(f"Status:            {audio_info.get('message', audio_info.get('status', 'N/A'))}")
        print("=" * 50 + "\n")


def analyze_video_audio(video_path: str) -> Dict[str, Any]:
    """Convenience wrapper for AudioAnalyzer.analyze_audio()."""
    analyzer = AudioAnalyzer()
    return analyzer.analyze_audio(video_path)
