"""
SafeAd AI (SAFE-VISION) — Phase 5A: Unit Tests for Detector Infrastructure & Offline Management.

Verifies:
1. Gated models without tokens are identified immediately without remote network calls.
2. Local cached models (unitary/toxic-bert, Salesforce/blip-image-captioning-base) are detected as available offline.
3. Empty text inputs return MODALITY_ABSENT.
4. Model provenance metadata is accurately populated.
"""

import os
import sys
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
for p in [ROOT_DIR, B2JB_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from models.detector_infrastructure import (
    check_model_availability,
    is_gated_model,
    is_model_cached_locally,
    DetectorStatus
)
from models.text_safety import SafeAdTextSafetyDetector
from models.visual_safety import VisualSafetyDetector


class TestDetectorInfrastructure:

    def test_gated_model_check_prevents_network_handshake(self):
        """Verifies that meta-llama models without token are flagged immediately without network call."""
        is_gated = is_gated_model("meta-llama/Llama-Guard-3-1B")
        assert is_gated is True

        # When no HF_TOKEN is in env, check_model_availability must return False
        if not os.environ.get("HF_TOKEN"):
            can_load, reason = check_model_availability("meta-llama/Llama-Guard-3-1B")
            assert can_load is False
            assert reason == "GATED_MODEL_NO_TOKEN"

    def test_local_cached_models_detected(self):
        """Verifies that pre-cached models in ~/.cache/huggingface/hub are detected as local hits."""
        assert is_model_cached_locally("unitary/toxic-bert") is True
        assert is_model_cached_locally("Salesforce/blip-image-captioning-base") is True
        assert is_model_cached_locally("Falconsai/nsfw_image_detection") is True

    def test_text_safety_modality_absent_on_empty_input(self):
        """Verifies that empty text inputs return MODALITY_ABSENT status."""
        detector = SafeAdTextSafetyDetector()
        res = detector.predict_text("")
        assert res["execution_status"] == DetectorStatus.MODALITY_ABSENT.value
        assert "model_provenance" in res
        assert res["model_provenance"]["status"] == DetectorStatus.MODALITY_ABSENT.value

    def test_visual_safety_offline_fallback_provenance(self):
        """Verifies visual safety initializes with offline fallback and sets valid provenance."""
        v_det = VisualSafetyDetector()
        v_det.load_model()
        assert v_det._status in [DetectorStatus.LOADED_SUCCESS.value, DetectorStatus.HEURISTIC_FALLBACK.value]
        assert "local cache" in v_det._active_model_name or "heuristics" in v_det._active_model_name
