"""
SafeAd AI (SAFE-VISION) — Phase 4B Task 2 Integration Tests:
Verification of DeBERTa Signal Propagation and Fusion Decision Effects.

Verifies:
1. DeBERTa signal is genuinely passed into System D (ExperimentalPolicyFusion) via improved_text_output.
2. System D Prohibited Veto Gate activates and changes classification from SAFE_FOR_ALL to UNSAFE_FOR_ALL.
3. DeBERTa signal is genuinely passed into System B (SafeAdFusion) via advertisement_risks.
4. Clean benign inputs do not trigger false prohibited vetoes.
5. System D routes detector failures to REQUIRES_HUMAN_REVIEW (abstention).
"""

import os
import sys
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core")
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
for p in [ROOT_DIR, JB_DIR, B2JB_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from models.fusion.safead_fusion import SafeAdFusion
from models.fusion.experimental_policy_fusion import ExperimentalPolicyFusion


class TestCandidateSystemsIntegration:

    def test_deberta_signal_changes_system_d_decision(self):
        """Verifies that injecting DeBERTa scam detection into System D converts SAFE_FOR_ALL to UNSAFE_FOR_ALL."""
        fusion_d = ExperimentalPolicyFusion()
        
        # Base evidence with clean visual and empty keyword detection (would be SAFE_FOR_ALL)
        base_evidence = {
            "visual": {"adult": 0.02, "violence": 0.0, "unsafe": False},
            "video": {"adult": 0.02, "violence": 0.0},
            "ocr": {"text": "Deposit 250 USD and earn 5000 USD in 48 hours", "status": "success"},
            "audio": {},
            "text_safety": {"categories": {}},
            "advertisement_risks": {"scam": 0.0, "deceptive_marketing": 0.0} # Keyword detector missed it
        }

        # Without DeBERTa (System C path)
        res_without = fusion_d.combine_assessment(base_evidence, improved_text_output=None)
        assert res_without["classification"] == "SAFE_FOR_ALL"
        assert res_without["publication_action"] == "APPROVE"

        # With DeBERTa scam flag (System D path)
        deberta_signal = {
            "prohibited_risk": 0.86,
            "scam_score": 0.86,
            "is_flagged_prohibited": True,
            "legit_score": 0.12
        }
        res_with = fusion_d.combine_assessment(base_evidence, improved_text_output=deberta_signal)
        assert res_with["classification"] == "UNSAFE_FOR_ALL"
        assert res_with["publication_action"] == "REJECT"
        assert res_with["policy_stage"] == "PROHIBITED_POLICY_VETO"
        assert res_with["risk_score"] >= 75.0

    def test_deberta_signal_affects_system_b_risk_score(self):
        """Verifies that DeBERTa scam signal injected into System B updates SafeAdFusion risk score."""
        fusion_b = SafeAdFusion()

        # Evidence where keywords found nothing
        evidence_baseline = {
            "visual": {"unsafe": False},
            "video": {}, "ocr": {}, "audio": {}, "text_safety": {},
            "advertisement_risks": {"scam": 0.0}
        }
        res_base = fusion_b.combine_assessment(evidence_baseline)
        score_base = res_base["risk_score"]

        # Injected DeBERTa score (System B path)
        evidence_with_deberta = {
            "visual": {"unsafe": False},
            "video": {}, "ocr": {}, "audio": {}, "text_safety": {},
            "advertisement_risks": {"scam": 0.86}
        }
        res_deb = fusion_b.combine_assessment(evidence_with_deberta)
        score_deb = res_deb["risk_score"]

        # When scam >= 0.50 (0.86), prohibited_risk becomes 86.0 >= 50.0, overriding risk_score to 86.0
        assert score_deb > score_base
        assert score_deb == 86.0
        assert res_deb["classification"] == "UNSAFE_FOR_ALL"

    def test_clean_input_does_not_trigger_false_veto(self):
        """Verifies that clean benign ads with low DeBERTa risk are approved in System D."""
        fusion_d = ExperimentalPolicyFusion()
        clean_evidence = {
            "visual": {"adult": 0.01, "violence": 0.0, "unsafe": False},
            "video": {"adult": 0.01, "violence": 0.0},
            "ocr": {"text": "AeroPress Coffee Maker fresh mornings", "status": "success"},
            "audio": {},
            "text_safety": {"categories": {}},
            "advertisement_risks": {"scam": 0.0, "deceptive_marketing": 0.0}
        }
        benign_deberta = {
            "prohibited_risk": 0.05,
            "scam_score": 0.02,
            "is_flagged_prohibited": False,
            "legit_score": 0.92
        }
        res = fusion_d.combine_assessment(clean_evidence, improved_text_output=benign_deberta)
        assert res["classification"] == "SAFE_FOR_ALL"
        assert res["publication_action"] == "APPROVE"
        assert res["risk_score"] < 25.0

    def test_detector_failure_routes_to_human_review_in_system_d(self):
        """Verifies that OCR error status routes to REQUIRES_HUMAN_REVIEW in System D."""
        fusion_d = ExperimentalPolicyFusion()
        error_evidence = {
            "visual": {"adult": 0.01, "violence": 0.0, "unsafe": False},
            "video": {"adult": 0.01, "violence": 0.0},
            "ocr": {"text": "", "status": "error: memory allocation failed"},
            "audio": {}, "text_safety": {}, "advertisement_risks": {}
        }
        res = fusion_d.combine_assessment(error_evidence)
        assert res["classification"] == "REQUIRES_HUMAN_REVIEW"
        assert res["publication_action"] == "ROUTE_TO_HUMAN_REVIEW"
        assert res["policy_stage"] == "HUMAN_IN_THE_LOOP_ROUTING"
