import os
import unittest
import numpy as np
from PIL import Image

from ai.pipeline import validate_advertisement_input, sample_video_frames
from ai.ocr.ocr_extractor import extract_ocr_from_image
from ai.safety.model_manager import SafetyModelManager, safety_model_manager
from ai.safety.violence_detector import ViolenceDetector
from ai.safety.nsfw_detector import NSFWDetector
from ai.safety.child_safety_detector import ChildSafetyDetector
from ai.safety.safety_pipeline import SafetyPipeline

class TestSafetyPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.samples_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../datasets/samples")
        )
        cls.sample_img = os.path.join(cls.samples_dir, "safe_python_ad.jpg")
        cls.sample_vid = os.path.join(cls.samples_dir, "safe_python_ad.mp4")

        # Create fallback test files if samples directory doesn't exist
        if not os.path.exists(cls.sample_img):
            os.makedirs(cls.samples_dir, exist_ok=True)
            img = Image.fromarray(np.uint8(np.random.rand(100, 100, 3) * 255))
            img.save(cls.sample_img)

    def test_input_validation(self):
        """Validates file integrity checks for images and videos."""
        if os.path.exists(self.sample_img):
            is_valid, media_type = validate_advertisement_input(self.sample_img)
            self.assertTrue(is_valid)
            self.assertEqual(media_type, "image")

        is_valid, err = validate_advertisement_input("non_existent_file.xyz")
        self.assertFalse(is_valid)

    def test_frame_sampling(self):
        """Tests uniform video frame sampling."""
        if os.path.exists(self.sample_vid):
            frames = sample_video_frames(self.sample_vid, max_frames=4)
            self.assertIsInstance(frames, list)
            if frames:
                self.assertLessEqual(len(frames), 4)

    def test_ocr_extraction(self):
        """Tests text extraction output."""
        if os.path.exists(self.sample_img):
            text = extract_ocr_from_image(self.sample_img)
            self.assertIsInstance(text, str)
            self.assertTrue(len(text) > 0)

    def test_model_manager_sequential_context(self):
        """Tests that ModelManager releases memory and manages state correctly."""
        manager = SafetyModelManager()
        manager.register_loader("test_violence", lambda: ViolenceDetector())
        
        with manager.use("test_violence") as model:
            self.assertIsNotNone(model)
            status = manager.get_model_status()
            self.assertEqual(status.get("test_violence"), "loaded")
            
        status_after = manager.get_model_status()
        self.assertEqual(status_after.get("test_violence"), "unloaded")

    def test_violence_detector(self):
        """Tests ViolenceDetector response structure."""
        detector = ViolenceDetector().load_model()
        res = detector.predict_image(self.sample_img)
        self.assertIn("detected", res)
        self.assertIn("score", res)
        self.assertIn("model", res)

    def test_nsfw_detector(self):
        """Tests NSFWDetector response structure."""
        detector = NSFWDetector().load_model()
        res = detector.predict_image(self.sample_img)
        self.assertIn("detected", res)
        self.assertIn("score", res)
        self.assertIn("model", res)

    def test_child_safety_detector(self):
        """Tests ChildSafetyDetector response structure."""
        detector = ChildSafetyDetector().load_model()
        dummy_img = Image.new("RGB", (50, 50), color="white")
        res = detector.predict([dummy_img], ocr_text="Family friendly advertisement")
        self.assertIn("risk_detected", res)
        self.assertIn("category", res)
        self.assertEqual(res["category"], "child_safety_risk")

    def test_safety_pipeline_standardized_schema(self):
        """Tests full SafetyPipeline end-to-end output schema compliance."""
        pipeline = SafetyPipeline()
        output = pipeline.analyze_advertisement(self.sample_img)
        
        # Verify required JSON schema keys
        self.assertIn("media_type", output)
        self.assertIn("conclusive_summary", output)
        self.assertIn("violence", output)
        self.assertIn("adult_content", output)
        self.assertIn("child_safety", output)
        self.assertIn("ocr_text", output)
        self.assertIn("frames_analyzed", output)
        self.assertIn("processing", output)

        # Verify conclusive summary details
        summary = output["conclusive_summary"]
        self.assertIn("overall_safety_status", summary)
        self.assertIn("is_safe", summary)
        self.assertIn("primary_violation", summary)
        self.assertIn("summary_statement", summary)

        # Verify performance metrics breakdown
        processing = output["processing"]
        self.assertIn("total_time_seconds", processing)
        self.assertIn("breakdown", processing)
        self.assertIn("memory_mb", processing)

if __name__ == "__main__":
    unittest.main()
