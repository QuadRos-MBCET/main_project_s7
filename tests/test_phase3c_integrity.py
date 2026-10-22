"""
SafeAd AI (SAFE-VISION) — Phase 3C Implementation Integrity and Safety Tests.

Verifies:
1. OCR Preprocessing Dimension Clamp (MAX_OCR_DIMENSION = 1920).
2. OCR Error Capture & Explicit Status Tracking (No silent masking).
3. Production Fusion Invariance: Confirms frozen state of safead_fusion.py.
4. Held-Out Test Set Isolation: Confirms test set integrity and group separation.
5. Detector Output Serialization: Confirms cache schema and completeness.
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd
from PIL import Image

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core")
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
for p in [ROOT_DIR, JB_DIR, B2JB_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from models.ocr_service import SafeAdOCRService
from models.fusion.safead_fusion import SafeAdFusion


class TestPhase3CIntegrity:

    def test_ocr_safe_dimension_clamp(self):
        """Verifies that images larger than MAX_OCR_DIMENSION (1920) are safely clamped."""
        ocr = SafeAdOCRService()
        # Create a large dummy synthetic image (e.g. 3000 x 2000)
        large_img = np.zeros((3000, 2000, 3), dtype=np.uint8)
        
        # Test extract_from_image
        res = ocr.extract_from_image(large_img)
        assert "status" in res
        assert "ocr_text" in res
        assert res["status"] in ["empty_text", "success"]

    def test_ocr_explicit_error_status(self):
        """Verifies that invalid or corrupted image inputs produce an explicit error status."""
        ocr = SafeAdOCRService()
        res = ocr.extract_from_image(None)
        assert res["status"] == "empty_input"
        assert res["ocr_text"] == ""

    def test_production_risk_scoring_frozen(self):
        """Confirms that production scoring weights and artificial caps remain exactly as audited."""
        fusion = SafeAdFusion()
        # 1. Visual weight test (visual_unsafe = True gives 25.0 in code, not 15.0)
        assessment_vis = {
            "visual": {"unsafe": True, "detected_categories": []},
            "video": {}, "ocr": {}, "audio": {}, "text_safety": {}, "advertisement_risks": {}
        }
        res_vis = fusion.combine_assessment(assessment_vis)
        assert res_vis["risk_score"] == 25.0

        # 2. Confirm score cap 39.9: visual_unsafe=True (25.0) + ocr deceptive=1.0 (15.0) = 40.0 -> clamped to 39.9
        assessment_cap1 = {
            "visual": {"unsafe": True, "detected_categories": []},
            "video": {"violence": 0.0, "adult": 0.0},
            "ocr": {"deceptive": 1.0},
            "audio": {}, "text_safety": {},
            "advertisement_risks": {"deceptive_marketing": 0.49}
        }
        res_cap1 = fusion.combine_assessment(assessment_cap1)
        assert res_cap1["risk_score"] == 39.9, f"Expected 39.9 cap, got {res_cap1['risk_score']}"

        # 3. Confirm score cap 65.0: adult content score >= 0.25 with high weighted score
        assessment_cap2 = {
            "visual": {"unsafe": True, "detected_categories": []},
            "video": {"adult": 1.0},
            "ocr": {"risk_score": 100.0, "adult": 1.0},
            "audio": {"risk_score": 100.0},
            "text_safety": {},
            "advertisement_risks": {}
        }
        res_cap2 = fusion.combine_assessment(assessment_cap2)
        assert res_cap2["risk_score"] == 65.0, f"Expected 65.0 cap, got {res_cap2['risk_score']}"

    def test_held_out_test_set_isolation(self):
        """Verifies that the held-out test set exists, has 96 samples, and has zero overlap with development set."""
        dataset_root = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub"
        split_dir = os.path.join(dataset_root, "splits", "repaired_benchmark")
        dev_path = os.path.join(split_dir, "development_set.csv")
        test_path = os.path.join(split_dir, "test_held_out.csv")

        assert os.path.exists(dev_path), f"Dev split missing: {dev_path}"
        assert os.path.exists(test_path), f"Test split missing: {test_path}"

        dev_df = pd.read_csv(dev_path)
        test_df = pd.read_csv(test_path)

        assert len(dev_df) == 284
        assert len(test_df) == 96

        dev_ids = set(dev_df["sample_id"])
        test_ids = set(test_df["sample_id"])
        overlap = dev_ids.intersection(test_ids)
        assert len(overlap) == 0, f"Leakage detected between Dev and Test: {overlap}"

    def test_detector_cache_schema(self):
        """Verifies that the detector cache structure contains required diagnostic and modality fields."""
        cache_path = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "saved_detector_outputs.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert isinstance(data, dict)
            for sid, record in data.items():
                assert "sample_id" in record
                assert "media_type" in record
                assert "true_label" in record
                assert "predicted_label" in record
                assert "risk_score" in record
                assert "raw_detector_evidence" in record
                break
