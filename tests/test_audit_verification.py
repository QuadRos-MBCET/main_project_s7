"""
Tests for verifying the SAFE-VISION (SafeAd AI) technical audit findings.
Verifies:
1. Formula weight discrepancies between PPT specification and running code.
2. The compensatory dilution flaw and artificial risk_score caps (39.9 and 65.0).
3. Category assignment precedence (Stage 1 veto vs PPT score bands).
4. Unreachable human-in-the-loop (REQUIRES_HUMAN_REVIEW) confidence condition.
"""

import unittest
import os
import sys

# Ensure project roots are in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core")
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if JB_DIR not in sys.path:
    sys.path.insert(0, JB_DIR)
if B2JB_DIR not in sys.path:
    sys.path.insert(0, B2JB_DIR)

from backend2jb.models.fusion.safead_fusion import SafeAdFusion, SafeAdAssessment

class TestSafeAdAuditVerification(unittest.TestCase):
    def setUp(self):
        self.fusion = SafeAdFusion()

    def test_weight_discrepancy_code_vs_ppt(self):
        """
        Verify Discrepancy A:
        PPT formula specifies:
          nsfw: 0.25, ocr: 0.20, violence: 0.20, visual: 0.15, audio: 0.10, adrisk: 0.10
        Running code (L243-250) actually computes:
          visual: 0.25, violence: 0.20, nsfw: 0.20, ocr: 0.15, audio: 0.10, adrisk: 0.10
        """
        # Test individual activation to extract effective weights in code
        
        # 1. Visual weight test (visual_unsafe = True, all else 0)
        # Note: visual_unsafe triggers 100 * weight in code
        # However, visual_unsafe also sets visual categories or prohibited checks if present.
        # Let's inspect weighted_score contribution directly:
        assessment_visual = {
            "visual": {"unsafe": True, "detected_categories": []},
            "video": {}, "ocr": {}, "audio": {}, "text_safety": {}, "advertisement_risks": {}
        }
        res_vis = self.fusion.combine_assessment(assessment_visual)
        # In running code: 100 * 0.25 = 25.0 (capped at 39.9). PPT specifies 100 * 0.15 = 15.0
        self.assertEqual(res_vis["risk_score"], 25.0, 
                         f"Code uses visual weight 0.25 (score 25.0), whereas PPT specifies 0.15 (score 15.0)")

        # 2. NSFW weight test (nsfw = 1.0, all else 0)
        # If nsfw >= 0.25, code activates adult content score (capped at 65.0)
        # For nsfw = 0.20 (below adult threshold 0.25 to stay in general formula):
        # Code: 20 * 0.20 = 4.0. PPT: 20 * 0.25 = 5.0
        assessment_nsfw = {
            "visual": {"unsafe": False},
            "video": {"adult": 0.20},
            "ocr": {}, "audio": {}, "text_safety": {}, "advertisement_risks": {}
        }
        res_nsfw = self.fusion.combine_assessment(assessment_nsfw)
        # In code: 20.0 * 0.20 = 4.0
        self.assertEqual(res_nsfw["risk_score"], 4.0,
                         f"Code uses nsfw weight 0.20 (score 4.0), whereas PPT specifies 0.25 (score 5.0)")

        # 3. OCR weight test (ocr.deceptive = 0.20)
        # Code: 20 * 0.15 = 3.0. PPT: 20 * 0.20 = 4.0
        assessment_ocr = {
            "visual": {"unsafe": False}, "video": {},
            "ocr": {"deceptive": 0.20},
            "audio": {}, "text_safety": {}, "advertisement_risks": {}
        }
        res_ocr = self.fusion.combine_assessment(assessment_ocr)
        self.assertEqual(res_ocr["risk_score"], 3.0,
                         f"Code uses ocr weight 0.15 (score 3.0), whereas PPT specifies 0.20 (score 4.0)")

    def test_score_caps_clamping(self):
        """
        Verify Discrepancy B:
        Code hard-caps risk_score to:
          - 39.9 for general ads (min(39.9, weighted_score))
          - 65.0 for adult ads (min(65.0, ...))
        even when linear combination exceeds these values.
        """
        # Case 1: General ad with high non-prohibited linear components
        # visual unsafe=True (25.0) + ocr deceptive=1.0 (15.0) + ad_risks deceptive=0.49 (4.9) = 44.9 weighted score
        # Since prohibited_risk = 49.0 (< 50) and adult_content_score = 0 (< 0.25),
        # risk_score is capped at 39.9 despite weighted sum being 44.9!
        assessment_general_high = {
            "visual": {"unsafe": True, "detected_categories": []},
            "video": {"violence": 0.0, "adult": 0.0},
            "ocr": {"deceptive": 1.0},
            "audio": {},
            "text_safety": {"categories": {"detected": []}},
            "advertisement_risks": {"deceptive_marketing": 0.49}
        }
        res = self.fusion.combine_assessment(assessment_general_high)
        # Weighted sum: 25.0 + 15.0 + 4.9 = 44.9
        # Code clamps to min(39.9, weighted_score) -> 39.9!
        self.assertEqual(res["risk_score"], 39.9, 
                         f"Risk score was capped at 39.9 instead of true weighted sum 44.9")

        # Case 2: Adult ad with high adult score (adult=1.0)
        # adult_content_score * 70 = 70.0. Weighted sum with nsfw 1.0 (20.0) + ocr 100 (15.0) + visual 100 (25.0) + audio 100 (10.0) = 70.0
        # But code clamps with min(65.0, ...)
        assessment_adult_high = {
            "visual": {"unsafe": True, "detected_categories": []},
            "video": {"adult": 1.0},
            "ocr": {"risk_score": 100.0, "adult": 1.0},
            "audio": {"risk_score": 100.0},
            "text_safety": {},
            "advertisement_risks": {}
        }
        res_adult = self.fusion.combine_assessment(assessment_adult_high)
        self.assertEqual(res_adult["risk_score"], 65.0,
                         f"Adult risk score was capped at 65.0 despite severe signals")

    def test_category_precedence_and_dilution(self):
        """
        Verify Discrepancy B & C:
        Linear formula exhibits compensatory dilution:
          violence = 0.50 with zero other signals -> weighted sum = 0.50 * 100 * 0.20 = 10.0
          Under PPT linear sum (0-25 = SAFE_FOR_ALL), a violent ad would be approved!
        The code overrides this via Stage 1 Prohibited Veto Gate:
          violence >= 0.50 forces UNSAFE_FOR_ALL (REJECT).
        """
        assessment_violence = {
            "visual": {"unsafe": False},
            "video": {"violence": 0.50},
            "ocr": {}, "audio": {}, "text_safety": {}, "advertisement_risks": {}
        }
        res = self.fusion.combine_assessment(assessment_violence)
        
        # Linear weighted score alone would be 10.0 (SAFE_FOR_ALL)
        # But Stage 1 veto triggers prohibited content
        self.assertEqual(res["classification"], "UNSAFE_FOR_ALL")
        self.assertEqual(res["publication_action"], "REJECT")
        self.assertEqual(res["policy_stage"], "PROHIBITED_CONTENT_POLICY")
        self.assertTrue(res["prohibited_content_detected"])

    def test_unreachable_human_review_condition(self):
        """
        Verify Discrepancy D:
        In safead_fusion.py line 262:
          confidence = round(min(1.0, max(0.40, 0.85 + (0.03 * min(modalities_checked, 4)))), 2)
        Because base confidence is 0.85, confidence is mathematically always >= 0.85.
        Line 294 checks: if confidence < self.CONFIDENCE_THRESHOLD (0.50)
        This condition can NEVER be reached under any input!
        """
        # Test 1: Completely empty input (minimum possible modalities)
        empty_assessment = {}
        res_empty = self.fusion.combine_assessment(empty_assessment)
        self.assertGreaterEqual(res_empty["confidence"], 0.85)
        self.assertNotEqual(res_empty["classification"], "REQUIRES_HUMAN_REVIEW")

        # Test 2: Contradictory / ambiguous signals
        ambiguous_assessment = {
            "visual": {"unsafe": False},
            "video": {"adult": 0.24, "violence": 0.49},  # just below thresholds
            "ocr": {"risk_score": 45.0},
            "audio": {"risk_score": 10.0},
            "text_safety": {},
            "advertisement_risks": {}
        }
        res_ambig = self.fusion.combine_assessment(ambiguous_assessment)
        self.assertGreaterEqual(res_ambig["confidence"], 0.85)
        self.assertFalse(res_ambig["requires_human_review"], 
                         "Human review was not triggered due to hardcoded base confidence of 0.85")

if __name__ == "__main__":
    unittest.main()
