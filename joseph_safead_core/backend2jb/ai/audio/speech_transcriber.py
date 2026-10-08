import os
import time
from typing import Dict, Any, Optional

try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

from ai.config import DEVICE, WHISPER_MODEL
from ai.memory_manager import MemoryManager
from ai.audio.audio_extractor import extract_audio_from_video, cleanup_temp_audio

class SpeechTranscriber:
    """
    OpenAI Whisper Speech-to-Text Transcriber for SafeAd AI.
    
    IMPORTANT ARCHITECTURAL PROTOCOL:
    - Whisper ONLY performs speech-to-text transcription.
    - Whisper does NOT make safety or policy violation decisions.
    - Preserves original speech transcript and language detection (English, Hindi, Malayalam, Tamil, etc.).
    - Optimized for Google Colab Free execution with VRAM safety checks.
    """

    def __init__(self, model_name: str = WHISPER_MODEL, device: str = DEVICE):
        self.model_name = model_name
        self.device = device if (HAS_TORCH and torch.cuda.is_available()) else "cpu"
        self._model = None
        self._pipe = None
        self._is_loaded = False

    def load_model(self, *args, **kwargs):
        """Loads OpenAI Whisper model lazily."""
        if self._is_loaded:
            return self

        print(f"[SpeechTranscriber] Loading Whisper model '{self.model_name}' on {self.device}...")
        try:
            import whisper
            self._model = whisper.load_model(self.model_name, device=self.device)
            self._is_loaded = True
            print(f"[SpeechTranscriber] Loaded OpenAI Whisper '{self.model_name}' successfully.")
        except Exception as e1:
            print(f"[SpeechTranscriber WARNING] OpenAI Whisper load fallback: {e1}")
            # Attempt Hugging Face transformers Whisper pipeline fallback
            try:
                from transformers import pipeline
                device_idx = 0 if (HAS_TORCH and torch.cuda.is_available() and self.device == "cuda") else -1
                self._pipe = pipeline(
                    "automatic-speech-recognition",
                    model=f"openai/whisper-{self.model_name}",
                    device=device_idx
                )
                self._is_loaded = True
                print(f"[SpeechTranscriber] Loaded Hugging Face Whisper pipeline fallback.")
            except Exception as e2:
                print(f"[SpeechTranscriber WARNING] Speech recognition model offline: {e2}")
                self._model = None
                self._pipe = None
                self._is_loaded = True

        return self

    def transcribe_audio_file(self, wav_path: str) -> Dict[str, Any]:
        """
        Transcribes a WAV audio file to text.
        Handles short audio (5s, 10s, 20s, 30s) and long audio cleanly.
        Auto-detects language and preserves original transcript without forced translation.
        """
        if not wav_path or not os.path.exists(wav_path):
            return {
                "transcript": "",
                "detected_language": "unknown",
                "status": "empty_input",
                "transcription_duration_seconds": 0.0
            }

        if not self._is_loaded:
            self.load_model()

        start_time = time.time()
        transcript = ""
        detected_language = "unknown"

        # 1. Primary OpenAI Whisper Library
        if self._model is not None:
            try:
                if HAS_TORCH:
                    with torch.inference_mode():
                        res = self._model.transcribe(wav_path, fp16=(self.device == "cuda"))
                else:
                    res = self._model.transcribe(wav_path, fp16=False)

                transcript = res.get("text", "").strip()
                detected_language = res.get("language", "unknown")
            except Exception as e:
                print(f"[SpeechTranscriber ERROR] Whisper inference error: {e}")

        # 2. Secondary Hugging Face Pipeline Fallback
        elif self._pipe is not None:
            try:
                res = self._pipe(wav_path)
                if isinstance(res, dict):
                    transcript = res.get("text", "").strip()
                detected_language = "auto"
            except Exception as e:
                print(f"[SpeechTranscriber ERROR] Transformers Whisper pipeline error: {e}")

        duration = round(time.time() - start_time, 4)
        MemoryManager.clear_gpu_memory()

        # Normalize detected language display string
        lang_str = str(detected_language).lower()
        lang_map = {
            "en": "English", "english": "English",
            "ml": "Malayalam", "malayalam": "Malayalam",
            "hi": "Hindi", "hindi": "Hindi",
            "ta": "Tamil", "tamil": "Tamil",
            "te": "Telugu", "telugu": "Telugu",
            "kn": "Kannada", "kannada": "Kannada"
        }
        display_language = lang_map.get(lang_str, str(detected_language).capitalize())

        status_str = "success" if transcript else ("silence" if (self._model or self._pipe) else "whisper_unavailable")

        return {
            "transcript": transcript,
            "detected_language": display_language,
            "status": status_str,
            "transcription_duration_seconds": duration
        }

    def transcribe_video(self, video_path: str) -> Dict[str, Any]:
        """
        Complete end-to-end video audio transcription wrapper.
        Extracts audio track, transcribes via Whisper, cleans up temp files, and returns evidence.
        """
        extraction_res = extract_audio_from_video(video_path)

        if not extraction_res.get("audio_present", False):
            return {
                "audio_available": False,
                "whisper_model": self.model_name,
                "detected_language": "N/A",
                "transcript": "",
                "status": extraction_res.get("status", "no_audio"),
                "message": extraction_res.get("message", "No audio stream found."),
                "transcription_duration_seconds": 0.0
            }

        wav_path = extraction_res.get("wav_path")
        stt_res = self.transcribe_audio_file(wav_path)

        # Cleanup temporary audio WAV file
        cleanup_temp_audio(wav_path)

        return {
            "audio_available": True,
            "whisper_model": f"whisper-{self.model_name}",
            "detected_language": stt_res.get("detected_language", "Unknown"),
            "transcript": stt_res.get("transcript", ""),
            "status": stt_res.get("status", "success"),
            "message": "Transcription completed successfully." if stt_res.get("transcript") else "Audio processed (no spoken speech detected).",
            "transcription_duration_seconds": stt_res.get("transcription_duration_seconds", 0.0)
        }


def load_whisper_model(model_name: str = WHISPER_MODEL) -> SpeechTranscriber:
    """Convenience function to load SpeechTranscriber instance."""
    transcriber = SpeechTranscriber(model_name=model_name)
    transcriber.load_model()
    return transcriber


def transcribe_audio(wav_path: str) -> Dict[str, Any]:
    """Convenience function for audio WAV transcription."""
    transcriber = SpeechTranscriber()
    return transcriber.transcribe_audio_file(wav_path)


def transcribe_video_audio(video_path: str) -> Dict[str, Any]:
    """Convenience function for end-to-end video audio transcription."""
    transcriber = SpeechTranscriber()
    return transcriber.transcribe_video(video_path)
