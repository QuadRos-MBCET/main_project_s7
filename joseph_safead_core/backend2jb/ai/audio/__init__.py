"""
SafeAd AI - Audio Safety Analysis Module
Provides audio extraction, OpenAI Whisper STT speech transcription, and audio evidence processing.
"""

from ai.audio.audio_extractor import extract_audio_from_video, cleanup_temp_audio, AudioExtractor
from ai.audio.speech_transcriber import load_whisper_model, transcribe_audio, transcribe_video_audio, SpeechTranscriber
from ai.audio.audio_analyzer import AudioAnalyzer, analyze_video_audio
from ai.audio.audio_event_detector import AudioEventDetector

__all__ = [
    "extract_audio_from_video",
    "cleanup_temp_audio",
    "AudioExtractor",
    "load_whisper_model",
    "transcribe_audio",
    "transcribe_video_audio",
    "SpeechTranscriber",
    "AudioAnalyzer",
    "analyze_video_audio",
    "AudioEventDetector",
]
