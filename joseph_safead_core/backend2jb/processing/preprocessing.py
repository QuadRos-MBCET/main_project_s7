import os
from PIL import Image
import cv2
from typing import Tuple

SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
SUPPORTED_VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv", ".m4v", ".3gp"}

def validate_advertisement_file(file_path: str) -> Tuple[bool, str, str]:
    """
    Validates existence, media format, and file integrity.
    Returns (is_valid, media_type, status_message).
    """
    if not file_path:
        return True, "text", "No media file provided; text-only payload."

    if not os.path.exists(file_path):
        return False, "unknown", "File does not exist on disk."

    ext = os.path.splitext(file_path)[1].lower()

    if ext in SUPPORTED_IMAGE_EXTS:
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True, "image", "Valid image file."
        except Exception as e:
            return False, "image", f"Corrupted image file: {e}"

    elif ext in SUPPORTED_VIDEO_EXTS:
        try:
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return False, "video", "Unreadable video stream."
            cap.release()
            return True, "video", "Valid video file."
        except Exception as e:
            return False, "video", f"Corrupted video file: {e}"

    return False, "unknown", f"Unsupported media extension: {ext}"
