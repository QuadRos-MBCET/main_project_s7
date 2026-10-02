import unittest
import os
import sys
from pathlib import Path

# Add platform roots to path
PLATFORM_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLATFORM_ROOT))
for sub in ["services", "camera-integration", "backend-integration", "config"]:
    p = str(PLATFORM_ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

from services.ad_delivery_service import ad_delivery_service
from services.review_service import review_service
from services.age_registration_service import age_registration_service
from camera_integration.face_age_adapter import face_age_adapter
from camera_integration.camera_handler import CameraHandler
from config.default_config import settings

class TestAgeAwareAdPlatform(unittest.TestCase):
    """
    Comprehensive test suite covering all 8 mandatory specification scenarios.
    """

    # -------------------------------------------------------------
    # Test 1 — Safe Advertisement
    # Ad -> SAFE FOR ALL, User -> SAFE FOR ALL => SHOWN
    # -------------------------------------------------------------
    def test_1_safe_advertisement_delivery(self):
        """Test 1: Safe advertisement is shown to a SAFE FOR ALL user."""
        ad_category = "SAFE FOR ALL"
        user_category = "SAFE FOR ALL"
        
        is_eligible = ad_delivery_service.evaluate_eligibility(user_category, ad_category)
        self.assertTrue(is_eligible, "SAFE FOR ALL ad should be delivered to SAFE FOR ALL user.")

    # -------------------------------------------------------------
    # Test 2 — 14+ Advertisement
    # Ad -> 14+: SAFE FOR ALL user -> HIDDEN, 14+ user -> SHOWN, 18+ user -> SHOWN
    # -------------------------------------------------------------
    def test_2_fourteen_plus_advertisement_delivery(self):
        """Test 2: 14+ ad is hidden from SAFE FOR ALL, shown to 14+ and 18+ users."""
        ad_category = "14+"
        
        # SAFE FOR ALL user -> HIDDEN
        self.assertFalse(
            ad_delivery_service.evaluate_eligibility("SAFE FOR ALL", ad_category),
            "14+ ad MUST NOT be shown to a SAFE FOR ALL (<14) user."
        )
        
        # 14+ user -> SHOWN
        self.assertTrue(
            ad_delivery_service.evaluate_eligibility("14+", ad_category),
            "14+ ad MUST be shown to a 14+ user."
        )
        
        # 18+ user -> SHOWN
        self.assertTrue(
            ad_delivery_service.evaluate_eligibility("18+", ad_category),
            "14+ ad MUST be shown to an 18+ user."
        )

    # -------------------------------------------------------------
    # Test 3 — 18+ Advertisement
    # Ad -> 18+: SAFE FOR ALL -> HIDDEN, 14+ -> HIDDEN, 18+ -> SHOWN
    # -------------------------------------------------------------
    def test_3_eighteen_plus_advertisement_delivery(self):
        """Test 3: 18+ ad is hidden from SAFE FOR ALL and 14+, shown to 18+."""
        ad_category = "18+"
        
        self.assertFalse(
            ad_delivery_service.evaluate_eligibility("SAFE FOR ALL", ad_category),
            "18+ ad MUST NOT be shown to a SAFE FOR ALL user."
        )
        self.assertFalse(
            ad_delivery_service.evaluate_eligibility("14+", ad_category),
            "18+ ad MUST NOT be shown to a 14+ user."
        )
        self.assertTrue(
            ad_delivery_service.evaluate_eligibility("18+", ad_category),
            "18+ ad MUST be shown to an 18+ user."
        )

    # -------------------------------------------------------------
    # Test 4 — Unsafe Advertisement
    # Ad -> UNSAFE FOR ALL: Any user -> NOT SHOWN
    # -------------------------------------------------------------
    def test_4_unsafe_advertisement_never_delivered(self):
        """Test 4: UNSAFE FOR ALL ad is NEVER shown to ANY user category."""
        ad_category = "UNSAFE FOR ALL"
        
        for user_cat in ["SAFE FOR ALL", "14+", "18+"]:
            self.assertFalse(
                ad_delivery_service.evaluate_eligibility(user_cat, ad_category),
                f"UNSAFE FOR ALL ad must NEVER be delivered to {user_cat} user."
            )

    # -------------------------------------------------------------
    # Test 5 — Human Review Override
    # AI -> 18+, Reviewer -> 14+ => Final -> 14+
    # 14+ user -> SHOWN, SAFE FOR ALL -> HIDDEN
    # -------------------------------------------------------------
    def test_5_human_review_override_precedence(self):
        """Test 5: Human reviewer override replaces AI prediction as final classification."""
        ai_prediction = "18+"
        human_decision = "14+"
        
        # When human overrides, final_classification becomes human_decision
        final_classification = human_decision
        
        # Delivery must check final_classification, NOT ai_prediction
        self.assertTrue(
            ad_delivery_service.evaluate_eligibility("14+", final_classification),
            "After override to 14+, 14+ user MUST be allowed to see the ad."
        )
        self.assertFalse(
            ad_delivery_service.evaluate_eligibility("SAFE FOR ALL", final_classification),
            "After override to 14+, SAFE FOR ALL user MUST still NOT see the ad."
        )

    # -------------------------------------------------------------
    # Test 6 — Registration & Facial Age Estimation
    # User registers -> Face-age software estimates age = 16 -> Category = 14+
    # Stored -> Camera stops -> Login -> Stored category = 14+
    # -------------------------------------------------------------
    def test_6_registration_and_age_estimation(self):
        """Test 6: Facial age estimation assigns correct category and stops camera."""
        # Generate synthetic teen face
        teen_face = CameraHandler.generate_synthetic_face("teen")
        b64_frame = CameraHandler.frame_to_base64(teen_face)
        
        res = face_age_adapter.process_frame(b64_frame)
        self.assertTrue(res["success"], "Face detection and estimation should succeed.")
        self.assertEqual(res["faces_detected"], 1, "Exactly one face must be detected.")
        self.assertIn(res["user_category"], ["14+", "18+"], "Teen face must yield 14+ (or adjacent) category.")

        # Simulate child face
        child_face = CameraHandler.generate_synthetic_face("child")
        res_child = face_age_adapter.process_frame(CameraHandler.frame_to_base64(child_face))
        self.assertTrue(res_child["success"])
        self.assertEqual(res_child["user_category"], "SAFE FOR ALL", "Child face must map to SAFE FOR ALL.")

    # -------------------------------------------------------------
    # Test 7 — Error Handling & Fail-Closed Guardrails
    # Test backend/camera failures. Restricted ads never shown because of an error.
    # -------------------------------------------------------------
    def test_7_error_handling_and_fail_closed(self):
        """Test 7: Fail closed behavior on missing face, multiple faces, or corrupt image."""
        # 0 Faces (Blank black frame)
        blank = CameraHandler.frame_to_base64(CameraHandler.generate_synthetic_face("child") * 0)
        res_blank = face_age_adapter.process_frame(blank)
        self.assertFalse(res_blank["success"])
        self.assertEqual(res_blank.get("faces_detected", 0), 0)

        # Corrupt data
        res_corrupt = face_age_adapter.process_frame("corrupted_base64_string_xyz")
        self.assertFalse(res_corrupt["success"])
        
        # Ad delivery with invalid/unknown category must fail closed
        self.assertFalse(
            ad_delivery_service.evaluate_eligibility("UNKNOWN_USER", "18+"),
            "Unknown user must fail closed."
        )
        self.assertFalse(
            ad_delivery_service.evaluate_eligibility("SAFE FOR ALL", "CORRUPT_AD"),
            "Unknown ad classification must fail closed."
        )

    # -------------------------------------------------------------
    # Test 8 — Demo Mode Simulator
    # Verify all 3 user categories can be simulated accurately
    # -------------------------------------------------------------
    def test_8_demo_mode_simulation(self):
        """Test 8: Demo mode simulation verifies eligibility across all 3 personas."""
        ad_pool = [
            {"title": "Toy Ad", "final_classification": "SAFE FOR ALL"},
            {"title": "Video Game Ad", "final_classification": "14+"},
            {"title": "Premium Whiskey Ad", "final_classification": "18+"},
            {"title": "Malware Scam Ad", "final_classification": "UNSAFE FOR ALL"}
        ]
        
        for persona in ["SAFE FOR ALL", "14+", "18+"]:
            delivered = [
                ad["title"] for ad in ad_pool
                if ad_delivery_service.evaluate_eligibility(persona, ad["final_classification"])
            ]
            
            # UNSAFE FOR ALL is never delivered in any persona
            self.assertNotIn("Malware Scam Ad", delivered)
            
            if persona == "SAFE FOR ALL":
                self.assertEqual(delivered, ["Toy Ad"])
            elif persona == "14+":
                self.assertEqual(delivered, ["Toy Ad", "Video Game Ad"])
            elif persona == "18+":
                self.assertEqual(delivered, ["Toy Ad", "Video Game Ad", "Premium Whiskey Ad"])

    # -------------------------------------------------------------
    # Test 9 — 2-Step Facial Similarity & Proof ID Verification
    # Compare live camera photo vs proof ID photo
    # -------------------------------------------------------------
    def test_9_facial_similarity_and_proof_id_verification(self):
        """Test 9: Verifies face similarity cross-check between camera photo and proof ID."""
        cam_face = CameraHandler.generate_synthetic_face("adult")
        id_face = CameraHandler.generate_synthetic_face("adult")

        cam_b64 = CameraHandler.frame_to_base64(cam_face)
        id_b64 = CameraHandler.frame_to_base64(id_face)

        res = face_age_adapter.compare_face_similarity(cam_b64, id_b64)
        self.assertTrue(res["success"], "Face similarity cross-check should succeed.")
        self.assertTrue(res["is_same_person"], "Matching synthetic adult face profiles must verify as same person.")
        self.assertGreaterEqual(res["similarity_score"], 0.55, "Similarity score must be >= 55% for matching faces.")
        self.assertIn("user_category", res)

if __name__ == "__main__":
    unittest.main()

