import os
import sys
import subprocess
import tempfile
from typing import Dict, Any, Optional

from ai.config import AUDIO_SAMPLE_RATE, AUDIO_CACHE_DIR

class AudioExtractor:
    """
    Robust audio stream extractor for SafeAd AI.
    Extracts audio tracks from video files (.mp4, .mov, .avi, .mkv, .webm) into mono 16kHz WAV files.
    Handles videos without audio streams gracefully without throwing errors or crashing.
    """

    def __init__(self, sample_rate: int = AUDIO_SAMPLE_RATE, cache_dir: str = AUDIO_CACHE_DIR):
        self.sample_rate = sample_rate
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def extract_audio(self, video_path: str, output_wav_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Extracts mono 16kHz WAV audio from a video file without loading full video into RAM.
        Returns dictionary containing extraction status and temporary WAV filepath.
        """
        if not os.path.exists(video_path):
            return {
                "audio_present": False,
                "wav_path": None,
                "status": "file_not_found",
                "message": f"Video file not found: {video_path}"
            }

        if output_wav_path is None:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_wav_path = os.path.join(self.cache_dir, f"{base_name}_temp_audio.wav")

        ffmpeg_cmd = None
        # 1. Try system ffmpeg binary
        try:
            res = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0:
                ffmpeg_cmd = "ffmpeg"
        except Exception:
            pass

        # 2. Try imageio_ffmpeg fallback binary
        if ffmpeg_cmd is None:
            try:
                import imageio_ffmpeg
                ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()
            except Exception:
                pass

        if ffmpeg_cmd is None:
            return {
                "audio_present": False,
                "wav_path": None,
                "status": "ffmpeg_unavailable",
                "message": "ffmpeg executable not found on system. Audio extraction skipped."
            }

        # Run ffmpeg to extract mono 16kHz PCM WAV
        cmd = [
            ffmpeg_cmd,
            "-y",                     # Overwrite output file
            "-i", video_path,         # Input video file
            "-vn",                    # Disable video recording
            "-ac", "1",               # Convert to mono channel
            "-ar", str(self.sample_rate), # Set sample rate to 16kHz
            "-acodec", "pcm_s16le",   # Standard 16-bit PCM WAV codec
            output_wav_path
        ]

        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if proc.returncode == 0 and os.path.exists(output_wav_path) and os.path.getsize(output_wav_path) > 100:
                return {
                    "audio_present": True,
                    "wav_path": output_wav_path,
                    "status": "extracted",
                    "message": "Audio stream extracted successfully."
                }
            else:
                # Video has no audio stream or audio track is muted/empty
                self.cleanup(output_wav_path)
                return {
                    "audio_present": False,
                    "wav_path": None,
                    "status": "no_audio",
                    "message": "No audio track found in video or audio stream is muted."
                }
        except Exception as e:
            self.cleanup(output_wav_path)
            return {
                "audio_present": False,
                "wav_path": None,
                "status": "extraction_error",
                "message": f"Audio extraction error: {e}"
            }

    @staticmethod
    def cleanup(wav_path: Optional[str]):
        """Safely removes temporary WAV file after processing."""
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass

def extract_audio_from_video(video_path: str, output_wav_path: Optional[str] = None) -> Dict[str, Any]:
    """Convenience wrapper for AudioExtractor.extract_audio()."""
    extractor = AudioExtractor()
    return extractor.extract_audio(video_path, output_wav_path)

def cleanup_temp_audio(wav_path: Optional[str]):
    """Convenience wrapper for AudioExtractor.cleanup()."""
    AudioExtractor.cleanup(wav_path)
