import os
import sys
import shutil
import subprocess
import tempfile
from typing import Dict, Any

def ensure_ffmpeg_on_path() -> bool:
    """
    Ensures FFmpeg executable is available on system PATH by binding imageio_ffmpeg.
    """
    try:
        import imageio_ffmpeg
        ffmpeg_bin_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
        ffmpeg_exe_name = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_symlink = os.path.join(ffmpeg_bin_dir, "ffmpeg.exe")

        if not os.path.exists(ffmpeg_symlink):
            try:
                shutil.copyfile(ffmpeg_exe_name, ffmpeg_symlink)
            except Exception:
                pass

        if ffmpeg_bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = ffmpeg_bin_dir + os.path.pathsep + os.environ.get("PATH", "")
        return True
    except Exception:
        return False

# Ensure FFmpeg PATH on module import
ensure_ffmpeg_on_path()

def check_audio_stream_exists(video_path: str) -> bool:
    """
    Checks whether a video file contains an audio stream.
    Uses PyAV (av) first; falls back to FFmpeg / MoviePy stream checks.
    """
    if not os.path.exists(video_path):
        return False

    ensure_ffmpeg_on_path()

    # 1. PyAV Stream Check
    try:
        import av
        container = av.open(video_path)
        audio_streams = [s for s in container.streams if s.type == "audio"]
        container.close()
        if len(audio_streams) > 0:
            return True
    except Exception:
        pass

    # 2. MoviePy / Subprocess check fallback
    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(video_path)
        has_audio = clip.audio is not None
        clip.close()
        return has_audio
    except Exception:
        pass

    return False

def extract_audio_to_wav(video_path: str, output_wav_path: str = None) -> Dict[str, Any]:
    """
    Extracts audio from video file into 16kHz mono WAV format for Whisper speech transcription.
    Returns dictionary with status and output file path.
    """
    if not os.path.exists(video_path):
        return {"audio_available": False, "wav_path": None, "message": "Video file not found."}

    ensure_ffmpeg_on_path()

    has_audio = check_audio_stream_exists(video_path)
    if not has_audio:
        return {"audio_available": False, "wav_path": None, "message": "No audio stream detected in video."}

    if output_wav_path is None:
        temp_dir = tempfile.gettempdir()
        filename = f"safead_audio_{os.getpid()}_{os.path.basename(video_path)}.wav"
        output_wav_path = os.path.join(temp_dir, filename)

    # 1. FFmpeg extraction
    try:
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            output_wav_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        if res.returncode == 0 and os.path.exists(output_wav_path) and os.path.getsize(output_wav_path) > 1000:
            return {"audio_available": True, "wav_path": output_wav_path, "message": "Audio extracted successfully via FFmpeg."}
    except Exception as e:
        print(f"[audio_extraction WARNING] FFmpeg command error: {e}")

    # 2. MoviePy extraction fallback
    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(video_path)
        if clip.audio is not None:
            clip.audio.write_audiofile(output_wav_path, fps=16000, nchannels=1, logger=None)
            clip.close()
            if os.path.exists(output_wav_path) and os.path.getsize(output_wav_path) > 1000:
                return {"audio_available": True, "wav_path": output_wav_path, "message": "Audio extracted successfully via MoviePy."}
    except Exception:
        pass

    return {"audio_available": False, "wav_path": None, "message": "Audio extraction failed or file unreadable."}

def cleanup_audio_file(wav_path: str):
    """Safely removes temporary WAV audio file."""
    if wav_path and os.path.exists(wav_path):
        try:
            os.remove(wav_path)
        except Exception:
            pass
