"""
SafeAd AI (SAFE-VISION) — Phase 6A: Unit and Focused Improvement Test Suite.

Verifies:
1. EnhancedAlcoholDetector: Positive brand/ABV triggers and non-alcoholic negative controls.
2. KineticViolenceDecoupler: Decoupling of sports/camera motion from interpersonal physical violence.
3. ContextAwareApparelGater: Contextual suppression of binary ViT adult false triggers on standard apparel.
4. DeceptiveAdvertisingIdentifier: Interception of crypto scams, prize phishing, and quack medical claims.
5. AdaptiveOCREnhancer: Image contrast enhancement pipeline stability.
6. PolicyFirstFusion Invariants: Non-dilution, detector failure routing, publication withholding, and benign resilience.
"""

import os
import sys
import pytest
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core")
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
for p in [ROOT_DIR, JB_DIR, B2JB_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from tests.experimental_repaired_detectors import (
    EnhancedAlcoholDetector,
    KineticViolenceDecoupler,
    ContextAwareApparelGater,
    DeceptiveAdvertisingIdentifier,
    AdaptiveOCREnhancer
)
from models.fusion.experimental_policy_fusion import ExperimentalPolicyFusion


class TestPhase6ADetectorImprovements:
    """Task 3 & Task 4 Verification Tests."""

    # -------------------------------------------------------------------------
    # 1. Alcohol Detector Verification
    # -------------------------------------------------------------------------
    def test_alcohol_positive_controls(self):
        detector = EnhancedAlcoholDetector()
        
        # Test 1: Brand mention
        res1 = detector.detect(ocr_text="Enjoy Heineken beer ice cold")
        assert res1["alcohol_detected"] is True
        assert "heineken" in res1["matched_brands"] or "beer" in res1["matched_brands"]

        # Test 2: Spirits brand & ABV
        res2 = detector.detect(ocr_text="Jack Daniels Old No. 7 Tennessee Whiskey 40% ABV")
        assert res2["alcohol_detected"] is True
        assert res2["confidence"] >= 0.65

        # Test 3: Verified alcohol keyword + visual container cue
        res3 = detector.detect(ocr_text="Grand opening celebration with champagne toast", visual_caption="people cheering with wine glass at bar counter")
        assert res3["alcohol_detected"] is True
        assert res3["visual_cue_present"] is True

    def test_alcohol_negative_controls(self):
        detector = EnhancedAlcoholDetector()

        # Strict constraint: Container / glass presence alone does NOT trigger alcohol
        res_container_only = detector.detect(ocr_text="Grand opening celebration tonight", visual_caption="people cheering with glasses at restaurant table")
        assert res_container_only["alcohol_detected"] is False
        assert res_container_only["score"] == 0.0

        # Non-alcoholic olive oil bottle
        res_oil = detector.detect(ocr_text="Pure Extra Virgin Olive Oil Cold Pressed", visual_caption="a glass bottle on wooden table")
        assert res_oil["alcohol_detected"] is False

        # Non-alcoholic explicit declaration
        res_non_alc = detector.detect(ocr_text="Heineken 0.0% Non-Alcoholic Beer - Zero Alcohol")
        assert res_non_alc["alcohol_detected"] is False
        assert res_non_alc["score"] == 0.0

        # Soda / soft drink
        res_soda = detector.detect(ocr_text="Refreshing Pepsi Cola with real sugar", visual_caption="a cold soda can on table")
        assert res_soda["alcohol_detected"] is False

        # Fruit juice
        res_juice = detector.detect(ocr_text="100% Pure Squeezed Orange Juice", visual_caption="a glass of orange juice with fruit slices")
        assert res_juice["alcohol_detected"] is False

    # -------------------------------------------------------------------------
    # 2. Kinetic Violence Decoupling Verification
    # -------------------------------------------------------------------------
    def test_violence_positive_interpersonal_aggression(self):
        decoupler = KineticViolenceDecoupler()
        
        # Real combat action
        segments = [
            {"label": "fighting", "score": 0.78},
            {"label": "punching", "score": 0.65}
        ]
        res = decoupler.evaluate_video_action(segments, raw_motion_diff=25.0)
        assert res["violence_detected"] is True
        assert res["violence_score"] >= 0.70
        assert res["top_violent_action"] == "fighting"
        assert res["action"] == "REJECT"

    def test_violence_benign_sports_and_motion_suppression(self):
        decoupler = KineticViolenceDecoupler()

        # Athletic skateboarding with fast cuts (visual violence flag = False)
        segments = [
            {"label": "skateboarding", "score": 0.45},
            {"label": "jumping", "score": 0.20}
        ]
        res = decoupler.evaluate_video_action(segments, raw_motion_diff=28.0, visual_violence_flag=False)
        assert res["violence_detected"] is False
        assert res["violence_score"] <= 0.18
        assert res["action"] == "APPROVE"

        # Toy commercial camera action (like SAFEAD_S14P_VID_003)
        segments_toy = [
            {"label": "racing", "score": 0.30},
            {"label": "headbanging", "score": 0.18}
        ]
        res_toy = decoupler.evaluate_video_action(segments_toy, raw_motion_diff=32.0, text_context="Daredevil trick track car racer", visual_violence_flag=False)
        assert res_toy["violence_detected"] is False
        assert res_toy["violence_score"] <= 0.18

    def test_violence_ambiguous_conflict_routes_to_human_review(self):
        decoupler = KineticViolenceDecoupler()

        # The SAFEAD_UFA_VID_001 / 003 case: Visual detector flagged violence, but VideoMAE returned diffuse low-confidence labels
        ambiguous_segments = [
            {"label": "celebrating", "score": 0.08},
            {"label": "parasailing", "score": 0.06}
        ]
        res = decoupler.evaluate_video_action(
            sampled_segments=ambiguous_segments,
            raw_motion_diff=25.0,
            visual_violence_flag=True
        )
        # MUST NOT suppress! Must route to human review and withhold publication!
        assert res["requires_human_review"] is True
        assert res["action"] == "ROUTE_TO_HUMAN_REVIEW"
        assert res["violence_detected"] is False
        assert "Detector conflict" in res["policy_reasons"][0]

    # -------------------------------------------------------------------------
    # 3. Context-Aware Apparel vs NSFW Gating
    # -------------------------------------------------------------------------
    def test_apparel_false_positive_suppression(self):
        gater = ContextAwareApparelGater()

        # Model posing in summer dress (ViT gave false 0.52 adult score)
        res = gater.evaluate_attire_safety(
            vit_adult_score=0.52,
            visual_caption="a fashion model posing in elegant summer dress and jacket"
        )
        assert res["recommended_category"] == "SAFE_FOR_ALL"
        assert res["adjusted_adult_score"] <= 0.20

    def test_swimwear_contextual_categorization(self):
        gater = ContextAwareApparelGater()

        # Swimwear at beach -> SAFE_14_PLUS
        res = gater.evaluate_attire_safety(
            vit_adult_score=0.60,
            visual_caption="a woman in bikini smiling poolside at summer beach resort"
        )
        assert res["recommended_category"] == "SAFE_14_PLUS"
        assert 0.25 <= res["adjusted_adult_score"] <= 0.45

    def test_explicit_adult_preservation(self):
        gater = ContextAwareApparelGater()

        # Genuinely explicit attire -> SAFE_18_PLUS
        res = gater.evaluate_attire_safety(
            vit_adult_score=0.75,
            visual_caption="close up of woman in black lace lingerie in bedroom"
        )
        assert res["recommended_category"] == "SAFE_18_PLUS"
        assert res["adjusted_adult_score"] >= 0.70

    # -------------------------------------------------------------------------
    # 4. Deceptive Advertising Identification
    # -------------------------------------------------------------------------
    def test_deceptive_scam_detection(self):
        identifier = DeceptiveAdvertisingIdentifier()

        # Crypto doubling fraud
        res1 = identifier.evaluate("Official Crypto Giveaway: Send 0.1 BTC to receive 0.2 BTC back instantly!")
        assert res1["is_deceptive"] is True
        assert res1["risk_score"] >= 0.60

        # Prize phishing shortlink
        res2 = identifier.evaluate("Congratulations! You won the prize! Enter competition and claim reward: http://tinyurl.com/win99")
        assert res2["is_deceptive"] is True

        # Quack Victorian cure
        res3 = identifier.evaluate("Dr. Parcells Extraordinary Medicines: Universal miracle cure for all chronic diseases.")
        assert res3["is_deceptive"] is True

    def test_deceptive_benign_commercial_whitelist(self):
        identifier = DeceptiveAdvertisingIdentifier()

        # Legitimate promo with terms and conditions
        res = identifier.evaluate("Special summer promotion: Get 20% off all sportswear. Terms & conditions apply. Official website.")
        assert res["is_deceptive"] is False
        assert res["risk_score"] == 0.0

    # -------------------------------------------------------------------------
    # 5. Adaptive OCR Preprocessing Verification
    # -------------------------------------------------------------------------
    def test_ocr_enhancer_clahe_execution(self):
        enhancer = AdaptiveOCREnhancer()
        synthetic_low_contrast = np.full((100, 100, 3), 180, dtype=np.uint8)
        synthetic_low_contrast[40:60, 40:60] = 190

        enhanced = enhancer.preprocess_image(synthetic_low_contrast)
        assert enhanced is not None
        assert enhanced.shape == (100, 100, 3)
        assert enhanced.dtype == np.uint8

    # -------------------------------------------------------------------------
    # 6. Policy-First Fusion Invariants (Task 4)
    # -------------------------------------------------------------------------
    def test_prohibited_non_dilution_invariant(self):
        fusion = ExperimentalPolicyFusion(enable_ambiguity_routing=False)
        
        # High scam score, zero on all other modalities
        assessment = {
            "visual": {"violence": 0.0, "adult": 0.0, "child_safety": 0.0},
            "video": {"violence": 0.0, "adult": 0.0, "child_safety": 0.0},
            "ocr": {"text": "Scam ad", "adult": 0.0, "violence": 0.0, "scam": 0.0, "deceptive": 0.0, "status": "success"},
            "audio": {"audio_available": False, "transcript": "", "violence": 0.0, "adult": 0.0, "child_safety": 0.0},
            "text_safety": {"categories": {}, "overall_risk": 0.0},
            "advertisement_risks": {"scam": 0.90, "deceptive_marketing": 0.0, "explicit_content": 0.0}
        }
        res = fusion.combine_assessment(assessment)
        assert res["classification"] == "UNSAFE_FOR_ALL"
        assert res["publication_action"] == "REJECT"
        assert res["risk_score"] >= 75.0  # Monotonic score preservation

    def test_detector_failure_routes_to_human_review(self):
        fusion = ExperimentalPolicyFusion(enable_ambiguity_routing=True)
        
        # OCR failed due to memory clamp or error
        assessment = {
            "visual": {"violence": 0.0, "adult": 0.0, "child_safety": 0.0},
            "video": {"violence": 0.0, "adult": 0.0, "child_safety": 0.0},
            "ocr": {"text": "", "status": "error: memory_clamp_oom"},
            "audio": {"audio_available": False},
            "text_safety": {},
            "advertisement_risks": {}
        }
        res = fusion.combine_assessment(assessment)
        assert res["classification"] == "REQUIRES_HUMAN_REVIEW"
        assert res["publication_action"] == "ROUTE_TO_HUMAN_REVIEW"
        assert res["requires_human_review"] is True

    def test_age_suitability_separated_from_universal_prohibition(self):
        fusion = ExperimentalPolicyFusion(enable_ambiguity_routing=False)

        # Regulated alcohol product (safe for 18+, not prohibited)
        assessment = {
            "visual": {"violence": 0.0, "adult": 0.0, "child_safety": 0.0},
            "video": {"violence": 0.0, "adult": 0.0, "child_safety": 0.0},
            "ocr": {"text": "Guinness Stout", "adult": 0.0, "violence": 0.0, "scam": 0.0, "status": "success"},
            "audio": {"audio_available": False},
            "text_safety": {"categories": {"alcohol": 0.85}},
            "advertisement_risks": {}
        }
        res = fusion.combine_assessment(assessment)
        assert res["classification"] == "SAFE_18_PLUS"
        assert res["publication_action"] == "AGE_RESTRICT"
        assert res["classification"] != "UNSAFE_FOR_ALL"

    def test_benign_content_resilience(self):
        fusion = ExperimentalPolicyFusion(enable_ambiguity_routing=False)

        # Clean Nike sneaker advertisement
        assessment = {
            "visual": {"violence": 0.0, "adult": 0.05, "child_safety": 0.0},
            "video": {"violence": 0.05, "adult": 0.0, "child_safety": 0.0},
            "ocr": {"text": "Just Do It Nike Air Max", "adult": 0.0, "violence": 0.0, "scam": 0.0, "status": "success"},
            "audio": {"audio_available": False},
            "text_safety": {"categories": {"overall_text_risk": 0.0}},
            "advertisement_risks": {"scam": 0.0, "deceptive_marketing": 0.0}
        }
        res = fusion.combine_assessment(assessment)
        assert res["classification"] == "SAFE_FOR_ALL"
        assert res["publication_action"] == "APPROVE"
        assert res["risk_score"] < 25.0
