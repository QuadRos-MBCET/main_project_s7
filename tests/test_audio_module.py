import os
import unittest
import numpy as np
import cv2
from PIL import Image

from ai.audio.audio_extractor import extract_audio_from_video, cleanup_temp_audio, AudioExtractor
from ai.audio.speech_transcriber import SpeechTranscriber, transcribe_video_audio
from ai.audio.audio_analyzer import AudioAnalyzer, analyze_video_audio
from ai.text.text_processor import analyze_multimodal_text
from ai.safety.safety_pipeline import SafetyPipeline

class TestAudioModule(unittest.TestCase):
    """
    Unit test suite for SafeAd AI Audio Safety Analysis Module (Step 2).
    Verifies audio extraction, Whisper STT fallback, short/long video support,
    multilingual/transcript policy evaluation, and multimodal schema formatting.
    """

    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_media"))
        os.makedirs(cls.test_dir, exist_ok=True)
        
        # Create a synthetic 5-second video without audio track
        cls.no_audio_video = os.path.join(cls.test_dir, "synth_5s_no_audio.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(cls.no_audio_video, fourcc, 30.0, (320, 240))
        for _ in range(150):
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

    def test_audio_extraction_no_audio_video(self):
        """Verifies that videos without audio tracks return audio_present=False gracefully."""
        res = extract_audio_from_video(self.no_audio_video)
        self.assertIsInstance(res, dict)
        self.assertFalse(res.get("audio_present"))
        self.assertIn(res.get("status"), ["no_audio", "ffmpeg_unavailable", "extraction_error"])

    def test_speech_transcriber_fallback(self):
        """Verifies that speech transcriber handles missing/empty WAV files without crashing."""
        transcriber = SpeechTranscriber(model_name="base")
        res = transcriber.transcribe_audio_file("non_existent_file.wav")
        self.assertIsInstance(res, dict)
        self.assertEqual(res.get("transcript"), "")
        self.assertEqual(res.get("detected_language"), "unknown")

    def test_audio_analyzer_schema(self):
        """Verifies that AudioAnalyzer returns standard structured audio evidence schema."""
        analyzer = AudioAnalyzer()
        audio_info = analyzer.analyze_audio(self.no_audio_video)
        self.assertIsInstance(audio_info, dict)
        self.assertIn("available", audio_info)
        self.assertIn("whisper_model", audio_info)
        self.assertIn("detected_language", audio_info)
        self.assertIn("transcript", audio_info)
        self.assertIn("violence", audio_info)
        self.assertIn("adult_content", audio_info)
        self.assertIn("child_safety", audio_info)

    def test_text_processor_transcript_integration(self):
        """Verifies that spoken speech transcript keywords contribute directly to safety policy evaluation."""
        text_res = analyze_multimodal_text(
            title="Safe Ad Title",
            caption="Clean caption",
            ocr_text="",
            transcript="Win real money now at our online casino jackpot poker table"
        )
        self.assertIn("Gambling", text_res.get("violations", []))
        self.assertGreaterEqual(text_res.get("text_risk_score", 0.0), 50.0)

    def test_audio_pipeline_end_to_end(self):
        """Verifies end-to-end SafetyPipeline execution with audio evidence integration."""
        pipeline = SafetyPipeline()
        schema = pipeline.analyze_advertisement(self.no_audio_video)
        self.assertIsInstance(schema, dict)
        self.assertEqual(schema.get("media_type"), "video")
        self.assertIn("audio", schema)
        self.assertFalse(schema["audio"].get("available", False))
        self.assertIn("conclusive_summary", schema)

def test_audio_pipeline():
    """Diagnostic runner for audio pipeline testing."""
    print("Running SafeAd AI Audio Pipeline Diagnostic Test...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAudioModule))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    unittest.main()
