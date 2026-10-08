import os
import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple, Dict, Any

DEFAULT_TARGET_FRAMES = 16

def get_video_metadata(video_path: str) -> Dict[str, Any]:
    """
    Extracts metadata from a video file (FPS, frame count, duration in seconds).
    Handles unreadable or corrupted files gracefully.
    """
    if not os.path.exists(video_path):
        return {
            "filename": os.path.basename(video_path),
            "fps": 30.0,
            "total_frames": 0,
            "duration": 0.0,
            "is_readable": False
        }

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            "filename": os.path.basename(video_path),
            "fps": 30.0,
            "total_frames": 0,
            "duration": 0.0,
            "is_readable": False
        }

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if fps <= 0 or np.isnan(fps):
        fps = 30.0

    if total_frames <= 0:
        count = 0
        while True:
            ret, _ = cap.read()
            if not ret:
                break
            count += 1
        total_frames = count
        cap.release()
        cap = cv2.VideoCapture(video_path)

    duration = float(total_frames) / float(fps) if fps > 0 else 0.0
    cap.release()

    return {
        "filename": os.path.basename(video_path),
        "fps": round(float(fps), 2),
        "total_frames": total_frames,
        "duration": round(float(duration), 2),
        "is_readable": total_frames > 0
    }

def extract_adaptive_keyframes(
    video_path: str,
    target_frames: int = DEFAULT_TARGET_FRAMES,
    return_metadata: bool = True
) -> Tuple[List[Image.Image], Dict[str, Any]]:
    """
    Adaptive Keyframe Sampling Pipeline for SafeAd AI.
    
    Sampling Logic:
    - IF video duration <= 30 sec: Dense sampling across the entire video.
    - IF video duration <= 2 min:  Representative clip/frame sampling across the video.
    - IF video duration > 2 min:   Sparse temporal sampling across the full duration.
    
    Robustness:
    - Handles corrupted frames cleanly.
    - Uniformly handles short videos with low frame count without external padding.
    """
    meta = get_video_metadata(video_path)
    duration = meta["duration"]
    fps = meta["fps"]
    total_frames = meta["total_frames"]

    if total_frames <= 0 or not meta["is_readable"]:
        empty_meta = {
            "filename": os.path.basename(video_path),
            "duration": 0.0,
            "fps": fps,
            "total_frames": 0,
            "sampled_count": 0,
            "sampling_strategy": "FAILED_UNREADABLE",
            "short_video_handled": False
        }
        return ([], empty_meta) if return_metadata else []

    # Read all valid raw frames from video stream
    cap = cv2.VideoCapture(video_path)
    raw_frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            raw_frames.append(Image.fromarray(frame_rgb))
        except Exception:
            continue
    cap.release()

    available_frames = len(raw_frames)
    if available_frames == 0:
        empty_meta = {
            "filename": os.path.basename(video_path),
            "duration": duration,
            "fps": fps,
            "total_frames": 0,
            "sampled_count": 0,
            "sampling_strategy": "NO_VALID_FRAMES",
            "short_video_handled": False
        }
        return ([], empty_meta) if return_metadata else []

    # Determine adaptive sampling strategy based on video duration
    if duration <= 30.0:
        strategy_name = "Dense Uniform Sampling (<= 30s Ad)"
        num_samples = max(target_frames, min(available_frames, 20))
    elif duration <= 120.0:
        strategy_name = "Representative Clip Sampling (30s - 2m Ad)"
        num_samples = target_frames
    else:
        strategy_name = "Sparse Temporal Sampling (> 2m Video)"
        num_samples = target_frames

    indices = np.linspace(0, available_frames - 1, num_samples, dtype=int)
    sampled_frames = [raw_frames[i] for i in indices]

    sampling_meta = {
        "filename": os.path.basename(video_path),
        "duration": duration,
        "fps": fps,
        "total_frames": available_frames,
        "sampled_count": len(sampled_frames),
        "sampling_strategy": strategy_name,
        "short_video_handled": available_frames < target_frames,
        "indices_sampled": indices.tolist()
    }

    if return_metadata:
        return sampled_frames, sampling_meta
    return sampled_frames
