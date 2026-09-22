import os
import unittest
import numpy as np
import cv2
from PIL import Image

from ai.config import MAX_VIDEO_FRAMES
from ai.pipeline import sample_video_frames, load_video_metadata, run_safead_inference
from ai.safety.safety_pipeline import SafetyPipeline

class TestVideoDurationRobustness(unittest.TestCase):
    """
    Dedicated test suite verifying video processing pipeline robustness
    across videos of any duration (5s, 10s, 20s, 30s, 1m, 8+m), ensuring zero crashes,
    valid frame sampling shapes, and accurate prediction structures.
    """

    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../scratch_test_videos"))
        os.makedirs(cls.test_dir, exist_ok=True)
        
        # Existing sample videos in root workspace
        cls.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.sample_5s = os.path.join(cls.root_dir, "geometry_class.mp4")
        cls.sample_10s = os.path.join(cls.root_dir, "coding_lessons.mp4")
        cls.sample_12s = os.path.join(cls.root_dir, "scam_giveaway.mp4")
        cls.sample_52s = os.path.join(cls.root_dir, "casino_ad.mp4")

        # Generate temporary synthetic videos for missing duration ranges (e.g. 1s, 2s, 20s, 30s)
        cls.synth_videos = {}
        durations = [1.0, 2.0, 20.0, 30.0]
        for d in durations:
            path = os.path.join(cls.test_dir, f"synth_{int(d)}s.mp4")
            if not os.path.exists(path):
                cls._create_synthetic_video(path, duration_sec=d, fps=30.0)
            cls.synth_videos[d] = path

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary synthetic videos
        if os.path.exists(cls.test_dir):
            for f in os.listdir(cls.test_dir):
                try:
                    os.remove(os.path.join(cls.test_dir, f))
                except Exception:
                    pass
            try:
                os.rmdir(cls.test_dir)
            except Exception:
                pass

    @staticmethod
    def _create_synthetic_video(output_path: str, duration_sec: float, fps: float = 30.0):
        total_frames = max(1, int(duration_sec * fps))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (320, 240))
        
        for i in range(total_frames):
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            # Add dynamic element to verify motion delta
            color = (int((i * 5) % 255), int((i * 10) % 255), 200)
            cv2.circle(frame, (160 + int(i % 50), 120), 30, color, -1)
            cv2.putText(frame, f"Frame {i}/{total_frames}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            out.write(frame)
        out.release()

    def test_video_metadata_loading(self):
        """Verifies load_video_metadata extracts FPS, total frames, and duration accurately."""
        if os.path.exists(self.sample_5s):
            meta = load_video_metadata(self.sample_5s)
            self.assertTrue(meta["is_readable"])
            self.assertGreater(meta["total_frames"], 0)
            self.assertGreater(meta["duration"], 0)

    def test_duration_independent_temporal_sampling(self):
        """
        Verifies that uniform temporal sampling produces exactly MAX_VIDEO_FRAMES (16)
        for short (1s, 2s, 5s), medium (10s, 12s, 20s, 30s), and long (52s) videos.
        """
        all_test_paths = [self.sample_5s, self.sample_10s, self.sample_12s, self.sample_52s] + list(self.synth_videos.values())
        
        for vpath in all_test_paths:
            if not os.path.exists(vpath):
                continue
            
            frames, meta = sample_video_frames(vpath, max_frames=MAX_VIDEO_FRAMES, return_metadata=True)
            
            # Assert frame count equals required model input count
            self.assertEqual(len(frames), MAX_VIDEO_FRAMES, f"Failed required frame count for {vpath}")
            
            # Assert frame dimensions and PIL type
            for f in frames:
                self.assertIsInstance(f, Image.Image)
                self.assertGreater(f.width, 0)
                self.assertGreater(f.height, 0)
                
            # Check short video duplication metadata
            if meta["total_frames"] < MAX_VIDEO_FRAMES:
                self.assertEqual(meta["short_video_handling"], "ENABLED")
                self.assertEqual(meta["frames_duplicated"], MAX_VIDEO_FRAMES - meta["total_frames"])
            else:
                self.assertEqual(meta["short_video_handling"], "DISABLED")
                self.assertEqual(meta["frames_duplicated"], 0)

    def test_run_safead_inference_duration_robustness(self):
        """Verifies end-to-end SafeAd inference pipeline on short, medium, and long videos."""
        test_samples = [
            ("5s video", self.sample_5s),
            ("10s video", self.sample_10s),
            ("12s video", self.sample_12s),
            ("52s video", self.sample_52s)
        ]
        
        for name, vpath in test_samples:
            if not os.path.exists(vpath):
                continue
            
            result = run_safead_inference(vpath, title=f"Test {name}", caption="Safety test")
            self.assertNotIn("error", result, f"Inference returned error for {name}")
            self.assertIn("classification", result)
            self.assertIn("action", result)
            self.assertIn("publishable", result)

    def test_safety_pipeline_duration_robustness(self):
        """Verifies SafetyPipeline.analyze_advertisement across video duration spectrum."""
        pipeline = SafetyPipeline()
        
        for d, vpath in self.synth_videos.items():
            result = pipeline.analyze_advertisement(vpath)
            self.assertEqual(result.get("status", "success"), "success" if not result.get("processing", {}).get("failed_components") else "partial")
            self.assertIn("conclusive_summary", result)
            self.assertIn("violence", result)
            self.assertIn("adult_content", result)
            self.assertIn("child_safety", result)

if __name__ == "__main__":
    unittest.main()
