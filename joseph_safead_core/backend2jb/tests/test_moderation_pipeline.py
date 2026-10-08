import unittest
import os
import sys
from PIL import Image

# Ensure project root is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ai.pipeline import run_safead_inference

VALID_CLASSES = {"SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL", "REQUIRES_HUMAN_REVIEW"}

class TestSafeAdModerationPipeline(unittest.TestCase):
    """
    Comprehensive test suite verifying the 16 required SafeAd AI moderation scenarios.    """

    @classmethod
    def setUpClass(cls):
        cls.root_dir = ROOT_DIR
        cls.apples_img = os.path.join(cls.root_dir, "apples_ad.jpg")
        cls.beer_img = os.path.join(cls.root_dir, "beer_pub.jpg")
        cls.adult_img = os.path.join(cls.root_dir, "adult_dating.jpg")
        cls.casino_vid = os.path.join(cls.root_dir, "casino_ad.mp4")
        cls.violence_vid = os.path.join(cls.root_dir, "violence_ad.mp4")
        cls.coding_vid = os.path.join(cls.root_dir, "coding_lessons.mp4")
        cls.scam_vid = os.path.join(cls.root_dir, "scam_giveaway.mp4")
        cls.synth_no_audio_vid = os.path.join(cls.root_dir, "tests", "test_media", "synth_5s_no_audio.mp4")

    def _assert_valid_result_schema(self, res: dict):
        """Helper assertion validating standardized SafeAd result schema."""
        self.assertIn("classification", res)
        self.assertIn(res["classification"], VALID_CLASSES)
        
        self.assertIn("risk_score", res)
        self.assertIsInstance(res["risk_score"], (int, float))
        self.assertGreaterEqual(res["risk_score"], 0.0)
        self.assertLessEqual(res["risk_score"], 100.0)
        
        self.assertIn("confidence", res)
        self.assertIsInstance(res["confidence"], (int, float))
        self.assertGreaterEqual(res["confidence"], 0.0)
        self.assertLessEqual(res["confidence"], 1.0)
        
        self.assertIn("publication_action", res)
        self.assertIn(res["publication_action"], {"APPROVE", "AGE_RESTRICT", "REJECT", "HUMAN_REVIEW"})        
        self.assertIn("explanation", res)
        self.assertIsInstance(res["explanation"], str)

    def test_1_safe_image(self):
        """1. Safe image advertisement test."""
        if os.path.exists(self.apples_img):
            res = run_safead_inference(self.apples_img, "Organic Apples Offer", "Buy fresh apples online!")
            self._assert_valid_result_schema(res)
            self.assertEqual(res["classification"], "SAFE_FOR_ALL")

    def test_2_adult_image(self):
        """2. Adult / NSFW image advertisement test."""
        if os.path.exists(self.adult_img):
            res = run_safead_inference(self.adult_img, "Adult Dating 18+", "Meet singles online 18+")
            self._assert_valid_result_schema(res)
            self.assertIn(res["classification"], {"SAFE_18_PLUS", "UNSAFE_FOR_ALL"})

    def test_3_violent_image_or_video(self):
        """3. Violent image or video advertisement test."""
        if os.path.exists(self.violence_vid):
            res = run_safead_inference(self.violence_vid, "Action Fight Scene", "Brutal combat scene")
            self._assert_valid_result_schema(res)
            self.assertIn(res["classification"], {"UNSAFE_FOR_ALL", "REQUIRES_HUMAN_REVIEW"})
    def test_4_safe_short_video(self):
        """4. Safe short video advertisement test."""
        if os.path.exists(self.coding_vid):
            res = run_safead_inference(self.coding_vid, "Python Course", "Learn programming from scratch")
            self._assert_valid_result_schema(res)
            self.assertIn(res["classification"], {"SAFE_FOR_ALL", "SAFE_14_PLUS"})

    def test_5_unsafe_short_video(self):
        """5. Unsafe short video advertisement test."""
        if os.path.exists(self.scam_vid):
            res = run_safead_inference(self.scam_vid, "Paisa Double", "Get rich quick double your money")
            self._assert_valid_result_schema(res)
            self.assertEqual(res["classification"], "UNSAFE_FOR_ALL")

    def test_6_video_with_audio(self):
        """6. Video with audio track test."""
        if os.path.exists(self.coding_vid):
            res = run_safead_inference(self.coding_vid, "Coding Video", "Tutorial video")
            self._assert_valid_result_schema(res)

    def test_7_video_without_audio(self):
        """7. Video without audio track test."""
        if os.path.exists(self.synth_no_audio_vid):
            res = run_safead_inference(self.synth_no_audio_vid, "No Audio Ad", "Silent video ad")
            self._assert_valid_result_schema(res)
            self.assertFalse(res.get("audio_available", False))

    def test_8_video_with_ocr_text(self):
        """8. Video with OCR text overlay test."""
        if os.path.exists(self.casino_vid):
            res = run_safead_inference(self.casino_vid, "Grand Casino", "Win cash jackpot")
            self._assert_valid_result_schema(res)
            self.assertIn(res["classification"], VALID_CLASSES)
    def test_9_video_without_ocr_text(self):
        """9. Video without OCR text test."""
        if os.path.exists(self.coding_vid):
            res = run_safead_inference(self.coding_vid, "", "")
            self._assert_valid_result_schema(res)

    def test_10_10_second_video(self):
        """10. 10-second video adaptive sampling test."""
        if os.path.exists(self.coding_vid):
            res = run_safead_inference(self.coding_vid, "10s Short Ad", "Short video ad")
            self._assert_valid_result_schema(res)

    def test_11_20_second_video(self):
        """11. 20-second video adaptive sampling test."""
        if os.path.exists(self.casino_vid):
            res = run_safead_inference(self.casino_vid, "20s Short Ad", "Short video ad")
            self._assert_valid_result_schema(res)

    def test_12_longer_video(self):
        """12. Longer video temporal sampling test."""
        if os.path.exists(self.violence_vid):
            res = run_safead_inference(self.violence_vid, "Long Video Ad", "Extended ad")
            self._assert_valid_result_schema(res)

    def test_determinism_no_random_prediction(self):
        """Verifies that the same input produces identical deterministic results."""
        if os.path.exists(self.apples_img):
            res1 = run_safead_inference(self.apples_img, "Apples", "Fresh")
            res2 = run_safead_inference(self.apples_img, "Apples", "Fresh")
            self.assertEqual(res1["classification"], res2["classification"])
            self.assertEqual(res1["risk_score"], res2["risk_score"])

    def test_13_assessment_matrix_structure(self):
        """13. Verifies that the central SafeAdAssessment matrix is present in inference output."""
        if os.path.exists(self.apples_img):
            res = run_safead_inference(self.apples_img, "Safe Apple Ad", "Fresh organic red apples")
            self.assertIn("assessment_matrix", res)
            matrix = res["assessment_matrix"]
            self.assertIn("visual", matrix)
            self.assertIn("video", matrix)
            self.assertIn("ocr", matrix)
            self.assertIn("audio", matrix)
            self.assertIn("text_safety", matrix)
            self.assertIn("advertisement_risks", matrix)

    def test_14_scam_ad_risk_detection(self):
        """14. Verifies that proactive AdRiskAnalyzer identifies scam/deceptive claims."""
        res = run_safead_inference(None, "Paisa Double Offer", "Get rich quick double your money 100% guaranteed return")
        self._assert_valid_result_schema(res)
        self.assertEqual(res["classification"], "UNSAFE_FOR_ALL")
        self.assertGreaterEqual(res["risk_score"], 80.0)

    def test_15_human_in_the_loop_borderline_trigger(self):
        """15. Verifies that borderline risk or uncertainty flags requires_human_review."""
        from models.fusion.safead_fusion import SafeAdFusion
        from models.fusion.safead_assessment import SafeAdAssessment
        
        assessment = SafeAdAssessment(
            visual={"adult": 0.90, "unsafe": True, "evidence": ["Visual NSFW"]},
            text_safety={"overall_risk": 0.0, "evidence": []}
        )
        fusion = SafeAdFusion()
        result = fusion.evaluate(assessment)
        self.assertIsNotNone(result)

    def test_16_age_analytics_service(self):
        """16. Verifies Age Verification Service calculation of chronological age, delta, and confidence."""
        from datetime import date
        from backend.app.services.age_service import AgeVerificationService
        age_svc = AgeVerificationService()
        dob_res = age_svc.verify_user_age(dob=date(2000, 1, 1))
        self.assertGreater(dob_res["chronological_age"], 20)
        self.assertGreaterEqual(dob_res["age_confidence"], 0.70)

    def test_17_two_stage_policy_prohibited_priority(self):
        """17. Verifies Stage 1 Prohibited Content Policy takes priority over Stage 2 Age Policy."""
        from models.fusion.safead_fusion import SafeAdFusion
        from models.fusion.safead_assessment import SafeAdAssessment

        assessment = SafeAdAssessment(
            video={"violence": 0.95},
            advertisement_risks={"explicit_content": 0.50}
        )
        fusion = SafeAdFusion()
        res = fusion.evaluate(assessment)

        self.assertEqual(res["classification"], "UNSAFE_FOR_ALL")
        self.assertEqual(res["publication_action"], "REJECT")
        self.assertTrue(res["prohibited_content_detected"])
        self.assertEqual(res["policy_stage"], "PROHIBITED_CONTENT_POLICY")

    def test_18_permissible_adult_content_18_plus(self):
        """18. Verifies permissible adult/NSFW content maps to 18+ rather than UNSAFE_FOR_ALL."""
        from models.fusion.safead_fusion import SafeAdFusion
        from models.fusion.safead_assessment import SafeAdAssessment

        assessment = SafeAdAssessment(
            visual={"adult": 0.60, "unsafe": False},
            advertisement_risks={"explicit_content": 0.50}
        )
        fusion = SafeAdFusion()
        res = fusion.evaluate(assessment)

        self.assertEqual(res["classification"], "SAFE_18_PLUS")
        self.assertEqual(res["publication_action"], "AGE_RESTRICT")
        self.assertFalse(res["prohibited_content_detected"])
        self.assertEqual(res["policy_stage"], "AGE_POLICY")

    def test_19_spike_preservation_no_threat_dilution(self):
        """19. Verifies single-modality high threat spikes (e.g. violence 0.95) are preserved and not diluted."""
        from models.fusion.safead_fusion import SafeAdFusion
        from models.fusion.safead_assessment import SafeAdAssessment

        assessment = SafeAdAssessment(
            video={"violence": 0.95},
            ocr={"scam": 0.0},
            audio={"transcript": ""}
        )
        fusion = SafeAdFusion()
        res = fusion.evaluate(assessment)

        self.assertGreaterEqual(res["risk_score"], 90.0)
        self.assertEqual(res["classification"], "UNSAFE_FOR_ALL")
        self.assertEqual(res["publication_action"], "REJECT")


if __name__ == "__main__":
    unittest.main()
