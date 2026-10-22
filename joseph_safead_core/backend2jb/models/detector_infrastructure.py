"""
SafeAd AI (SAFE-VISION) — Phase 5A: Detector Infrastructure & Lifecycle Manager.

Provides:
1. Explicit model availability checks (prevents HTTP 401 stalls for gated/missing models).
2. Deterministic offline-first fallback hierarchy.
3. Explicit status tracking:
   - LOADED_SUCCESS: Model loaded and active.
   - MODEL_UNAVAILABLE: Gated or missing weights; bypassed without network penalty.
   - MODALITY_ABSENT: Media does not contain target modality (e.g. video has no audio, image has no text).
   - INFERENCE_FAILED: Model crashed during forward pass.
   - HEURISTIC_FALLBACK: Operating on deterministic heuristic rules.
4. Clean model provenance tracking (model_id, version, device, status, latency).
5. Zero hardcoded authentication tokens.
"""

import os
from enum import Enum
from typing import Dict, Any, Optional, Tuple

try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False


class DetectorStatus(str, Enum):
    LOADED_SUCCESS = "LOADED_SUCCESS"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    MODALITY_ABSENT = "MODALITY_ABSENT"
    INFERENCE_FAILED = "INFERENCE_FAILED"
    HEURISTIC_FALLBACK = "HEURISTIC_FALLBACK"


GATED_MODEL_PREFIXES = [
    "meta-llama/",
    "google/gemma",
    "mistralai/Mistral-Large"
]


def is_gated_model(model_id: str) -> bool:
    """Checks whether a Hugging Face model identifier requires gated authorization."""
    return any(model_id.startswith(prefix) for prefix in GATED_MODEL_PREFIXES)


def has_hf_token() -> bool:
    """Checks if a Hugging Face token is available in environment without hardcoding."""
    return bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN"))


def is_model_cached_locally(model_id: str) -> bool:
    """
    Checks if model weights exist in the local Hugging Face hub cache
    without making any remote network calls.
    """
    try:
        from huggingface_hub import try_to_load_from_cache
        # Look for standard configuration or model file
        cached = try_to_load_from_cache(model_id, "config.json")
        if isinstance(cached, str) and os.path.exists(cached):
            return True
        # Also check directory name convention
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        expected_folder = f"models--{model_id.replace('/', '--')}"
        folder_path = os.path.join(cache_dir, expected_folder)
        return os.path.exists(folder_path)
    except Exception:
        return False


def check_model_availability(
    model_id: str,
    allow_remote_download: bool = False
) -> Tuple[bool, str]:
    """
    Determines whether a model can be loaded without causing network errors or 401 Client Errors.
    Returns (can_load, reason).
    """
    # 1. Check local cache first
    if is_model_cached_locally(model_id):
        return True, "LOCAL_CACHE_HIT"

    # 2. Check if gated without token
    if is_gated_model(model_id) and not has_hf_token():
        return False, "GATED_MODEL_NO_TOKEN"

    # 3. Check if remote download is permitted
    if not allow_remote_download and os.environ.get("SAFEAD_ALLOW_REMOTE_DOWNLOAD", "0") != "1":
        return False, "REMOTE_DOWNLOAD_DISABLED"

    return True, "REMOTE_AVAILABLE"
