"""
End-to-End Integration and Regression Tests for Candidate B (Phase 7A Tasks 1, 2, 3).

Verifies:
1. EnhancedAlcoholDetector is executed during real pipeline inference when selectable flag is active.
2. Detector evidence, reasons, and audit trails are recorded in pipeline output.
3. Negative controls (soda, olive oil, 0.0% non-alcoholic beer) do not trigger alcohol detection.
4. Production behavior is 100% unchanged by default (pipeline_mode='production').
5. Reproduces the exact 194-sample development results:
   - 31.96% -> 33.51% accuracy
   - 26.47% -> 35.29% 18+ recall
   - 80.00% PFAR
   - Exactly 3 samples changed: SAFEAD_S18P_IMG_002, 006, 031.
"""

import os
import sys
import json
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core")
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
for p in [B2JB_DIR, JB_DIR]:
    if p not in sys.path:
        sys.path.append(p)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
else:
    sys.path.remove(ROOT_DIR)
    sys.path.insert(0, ROOT_DIR)

from backend2jb.ai.pipeline import run_safead_inference
from models.fusion.safead_fusion import SafeAdFusion
from models.experimental_detectors import EnhancedAlcoholDetector


def test_candidate_b_selectable_execution_and_evidence():
    """Verify Candidate B executes during inference and attaches evidence only when selected."""
    # Production default: alcohol audit is inactive
    res_prod = run_safead_inference(
        file_path="",
        title="Budweiser King of Beers",
        caption="Cold lager beer in a frosty mug",
        pipeline_mode="production"
    )
    assert res_prod["pipeline_mode"] == "production"
    assert res_prod["experimental_audit"]["alcohol"] is None

    # Candidate B active: alcohol detector executes and attaches evidence
    res_b = run_safead_inference(
        file_path="",
        title="Budweiser King of Beers",
        caption="Cold lager beer in a frosty mug",
        pipeline_mode="candidate_b"
    )
    assert res_b["pipeline_mode"] == "candidate_b"
    alc_audit = res_b["experimental_audit"]["alcohol"]
    assert alc_audit is not None
    assert alc_audit["alcohol_detected"] is True
    assert alc_audit["score"] >= 0.85
    assert any("Budweiser" in r or "budweiser" in r for r in alc_audit["reasons"])
    # Age policy classification correctly restricted to 18+
    assert res_b["classification"] == "SAFE_18_PLUS"
    assert str(res_b["age_restriction"]).startswith("18")


def test_candidate_b_negative_controls_on_real_inference_path():
    """Verify negative controls on real inference path: soda, olive oil, and 0.0% non-alcoholic beer."""
    # Negative Control 1: Fruit Soda in glass
    res_soda = run_safead_inference(
        file_path="",
        title="Sparkling Orange Soda",
        caption="Delicious fruit soda drink in a cold glass bottle",
        pipeline_mode="candidate_b"
    )
    assert res_soda["experimental_audit"]["alcohol"]["alcohol_detected"] is False
    assert res_soda["classification"] == "SAFE_FOR_ALL"

    # Negative Control 2: Olive oil bottle
    res_oil = run_safead_inference(
        file_path="",
        title="Extra Virgin Olive Oil",
        caption="Organic cold pressed cooking oil bottle for salads",
        pipeline_mode="candidate_b"
    )
    assert res_oil["experimental_audit"]["alcohol"]["alcohol_detected"] is False
    assert res_oil["classification"] == "SAFE_FOR_ALL"

    # Negative Control 3: Explicit 0.0% alcohol-free beer
    res_non_alc = run_safead_inference(
        file_path="",
        title="Heineken 0.0 Non-Alcoholic",
        caption="0.0% alcohol-free malt beverage with zero alcohol",
        pipeline_mode="candidate_b"
    )
    assert res_non_alc["experimental_audit"]["alcohol"]["alcohol_detected"] is False
    assert "non-alcoholic" in res_non_alc["experimental_audit"]["alcohol"]["reasons"][0].lower()
    assert res_non_alc["classification"] == "SAFE_FOR_ALL"


def test_production_behavior_unchanged_by_default():
    """Verify that omitting pipeline_mode defaults strictly to production configuration."""
    res_default = run_safead_inference(
        file_path="",
        title="Generic Commercial Product",
        caption="High quality kitchen blender"
    )
    assert res_default["pipeline_mode"] == "production"
    assert res_default["experimental_audit"]["alcohol"] is None
    assert res_default["experimental_audit"]["violence"] is None


def test_reproduction_of_194_sample_development_benchmark():
    """Verify exact numerical reproduction of the 194-sample development results."""
    cache_path = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "saved_detector_outputs.json")
    assert os.path.exists(cache_path), f"Cache not found: {cache_path}"

    with open(cache_path, "r", encoding="utf-8") as f:
        cached_data = json.load(f)

    assert len(cached_data) == 194

    fusion = SafeAdFusion()
    alc_detector = EnhancedAlcoholDetector()

    preds_base = {}
    preds_cand_b = {}
    ground_truth = {}

    for sid, sample in cached_data.items():
        gt = sample["true_label"]
        ground_truth[sid] = gt
        ev = sample["raw_detector_evidence"]

        # Baseline prediction
        res_base = fusion.combine_assessment(ev)
        preds_base[sid] = res_base["classification"]

        # Candidate B prediction
        ev_b = json.loads(json.dumps(ev))
        ocr_tx = sample.get("extracted_ocr", "")
        aud_tx = ev_b.get("audio", {}).get("transcript", "")
        vis_objs = sample.get("ocr_scan", {}).get("detected_objects", [])

        res_alc = alc_detector.evaluate_alcohol(
            ocr_text=ocr_tx,
            speech_transcript=aud_tx,
            visual_objects=vis_objs
        )
        if res_alc["alcohol_detected"]:
            ev_b.setdefault("text_safety", {}).setdefault("categories", {})["alcohol"] = res_alc["score"]
            ev_b.setdefault("advertisement_risks", {})["explicit_content"] = max(
                ev_b.get("advertisement_risks", {}).get("explicit_content", 0.0),
                res_alc["score"]
            )
            ev_b.setdefault("advertisement_risks", {}).setdefault("evidence", []).extend(res_alc.get("reasons", []))

        res_b = fusion.combine_assessment(ev_b)
        preds_cand_b[sid] = res_b["classification"]

    # 1. Accuracy Verification
    correct_base = sum(1 for sid in cached_data if preds_base[sid] == ground_truth[sid])
    correct_cand_b = sum(1 for sid in cached_data if preds_cand_b[sid] == ground_truth[sid])

    acc_base = round(correct_base / 194.0, 4)
    acc_cand_b = round(correct_cand_b / 194.0, 4)

    assert correct_base == 62
    assert acc_base == 0.3196  # 31.96%
    assert correct_cand_b == 65
    assert acc_cand_b == 0.3351  # 33.51%

    # 2. Recall: SAFE_18_PLUS
    s18p_ids = [sid for sid, gt in ground_truth.items() if gt == "SAFE_18_PLUS"]
    assert len(s18p_ids) == 34

    s18p_base_correct = sum(1 for sid in s18p_ids if preds_base[sid] == "SAFE_18_PLUS")
    s18p_cand_b_correct = sum(1 for sid in s18p_ids if preds_cand_b[sid] == "SAFE_18_PLUS")

    rec_base_18p = round(s18p_base_correct / 34.0, 4)
    rec_cand_b_18p = round(s18p_cand_b_correct / 34.0, 4)

    assert s18p_base_correct == 9
    assert rec_base_18p == 0.2647  # 26.47%
    assert s18p_cand_b_correct == 12
    assert rec_cand_b_18p == 0.3529  # 35.29%

    # 3. Prohibited False Acceptance (PFAR)
    ufa_ids = [sid for sid, gt in ground_truth.items() if gt == "UNSAFE_FOR_ALL"]
    assert len(ufa_ids) == 10

    ufa_base_false_accepted = sum(1 for sid in ufa_ids if preds_base[sid] != "UNSAFE_FOR_ALL")
    ufa_cand_b_false_accepted = sum(1 for sid in ufa_ids if preds_cand_b[sid] != "UNSAFE_FOR_ALL")

    assert ufa_base_false_accepted == 8
    assert ufa_cand_b_false_accepted == 8  # PFAR remains 80.00% (zero regressions)

    # 4. Exact Changed Samples Verification
    changed_samples = [sid for sid in cached_data if preds_base[sid] != preds_cand_b[sid]]
    assert len(changed_samples) == 3
    assert set(changed_samples) == {"SAFEAD_S18P_IMG_002", "SAFEAD_S18P_IMG_006", "SAFEAD_S18P_IMG_031"}

    # Confirm all 3 moved from SAFE_FOR_ALL to SAFE_18_PLUS
    for sid in changed_samples:
        assert preds_base[sid] == "SAFE_FOR_ALL"
        assert preds_cand_b[sid] == "SAFE_18_PLUS"
        assert ground_truth[sid] == "SAFE_18_PLUS"
