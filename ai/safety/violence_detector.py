import os
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, List, Union

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

from ai.config import DEVICE

class ViolenceDetector:
    """
    Violence & Action Content Classifier for SafeAd AI.
    
    Pretrained Models & Multi-Indicator Fallbacks:
    - MCG-NJU/videomae-base-finetuned-kinetics or facebook/timesformer-base-finetuned-k400
    - Multi-indicator visual evaluator: Blood/gore red density, high motion delta, and action keywords.
    """

    def __init__(self, device: str = DEVICE):
        self.device = device if (HAS_TORCH and torch.cuda.is_available()) else "cpu"
        self.video_model_name = "videomae_kinetics"
        self._pipe = None
        self._is_loaded = False
        self.threshold = 0.35  # Sensitive threshold for safety moderation

    def load_model(self, *args, **kwargs):
        """Loads Hugging Face video classification pipeline."""
        if self._is_loaded:
            return self

        print(f"[ViolenceDetector] Initializing video violence classifier on {self.device}...")
        try:
            from transformers import pipeline
            device_idx = 0 if (HAS_TORCH and torch.cuda.is_available() and self.device == "cuda") else -1
            
            # Primary model: VideoMAE Kinetics-400 Action Classifier
            model_id = "MCG-NJU/videomae-base-finetuned-kinetics"
            try:
                self._pipe = pipeline(
                    "video-classification",
                    model=model_id,
                    device=device_idx,
                    top_k=None
                )
                self.video_model_name = "videomae_kinetics"
                print(f"[ViolenceDetector] Loaded '{model_id}' successfully.")
            except Exception as e1:
                print(f"[ViolenceDetector] Primary model '{model_id}' load fallback: {e1}")
                # Secondary model fallback: TimeSformer Kinetics-400
                model_id_fallback = "facebook/timesformer-base-finetuned-k400"
                try:
                    self._pipe = pipeline(
                        "video-classification",
                        model=model_id_fallback,
                        device=device_idx,
                        top_k=None
                    )
                    self.video_model_name = "timesformer_k400"
                    print(f"[ViolenceDetector] Loaded fallback model '{model_id_fallback}'.")
                except Exception as e2:
                    print(f"[ViolenceDetector WARNING] Video classification pipeline offline: {e2}")
                    self._pipe = None
                    
            self._is_loaded = True
        except Exception as e:
            print(f"[ViolenceDetector WARNING] Transformers video pipeline fallback: {e}")
            self._pipe = None
            self._is_loaded = True

        return self

    VIOLENCE_KEYWORDS = [
        "fight", "blood", "gun", "weapon", "knife", "kill", "dead", "stab",
        "attack", "assault", "shoot", "murder", "combat", "brawl", "punch",
        "kick", "war", "hit", "injury", "violent", "violence", "sword", "shooting",
        "blood", "khoon", "maar", "bandook", "vettu", "kolapathakam", "thokku"
    ]

    VIOLENT_ACTION_LABELS = [
        "fighting", "punching", "shooting gun", "stabbing", "wrestling",
        "kicking", "side kick", "drop kick", "slapping", "headbutting",
        "sword fighting", "arm wrestling", "brawling", "hit", "assault"
    ]

    def _heuristic_violence_eval(
        self,
        rgb_frames: List[np.ndarray],
        ocr_text: str = "",
        filename: str = ""
    ) -> float:
        """
        Multi-indicator fallback evaluator:
        1. Action & Violence keywords in filename or OCR overlay.
        2. Blood/gore red pixel density calculation (filtered for dark crimson blood, ignoring bright sky/sunsets).
        3. Motion delta (frame difference) evaluation across frame sequence.
        """
        text_lower = f"{filename} {ocr_text}".lower()
        keyword_score = 0.0
        for kw in self.VIOLENCE_KEYWORDS:
            if kw in text_lower:
                keyword_score = max(keyword_score, 0.90)

        blood_score = 0.0
        motion_score = 0.0

        if rgb_frames:
            for frame in rgb_frames:
                try:
                    bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
                    height, width = frame.shape[:2]

                    # Blood/gore HSV spectrum (dark/medium crimson, V <= 180, S >= 100)
                    lower_red1 = np.array([0, 100, 20], dtype=np.uint8)
                    upper_red1 = np.array([8, 255, 180], dtype=np.uint8)
                    lower_red2 = np.array([172, 100, 20], dtype=np.uint8)
                    upper_red2 = np.array([180, 255, 180], dtype=np.uint8)

                    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
                    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
                    mask = cv2.bitwise_or(mask1, mask2)

                    total_red = np.count_nonzero(mask)
                    if total_red > 0:
                        # Upper 50% sky region check
                        upper_red = np.count_nonzero(mask[:height // 2, :])
                        upper_ratio = upper_red / total_red
                        # If red pixels are mostly in the upper sky region, it's a sunset/nature sky
                        if upper_ratio < 0.60:
                            red_ratio = float(total_red) / float(mask.size)
                            if red_ratio > 0.12 and keyword_score > 0:
                                blood_score = max(blood_score, round(min(0.95, red_ratio * 3.5), 4))
                            elif red_ratio > 0.25:
                                blood_score = max(blood_score, 0.25)
                except Exception:
                    pass

        if len(rgb_frames) > 1:
            diffs = []
            for i in range(1, len(rgb_frames)):
                try:
                    gray1 = cv2.cvtColor(rgb_frames[i-1], cv2.COLOR_RGB2GRAY)
                    gray2 = cv2.cvtColor(rgb_frames[i], cv2.COLOR_RGB2GRAY)
                    diff = np.mean(cv2.absdiff(gray1, gray2))
                    diffs.append(diff)
                except Exception:
                    pass
            if diffs:
                avg_diff = float(np.mean(diffs))
                if keyword_score > 0 and avg_diff > 12.0:
                    motion_score = round(min(0.85, avg_diff / 45.0), 4)
                elif avg_diff > 25.0:
                    motion_score = 0.20

        return max(keyword_score, blood_score, motion_score)

    def predict_video_frames(
        self,
        frames: List[Union[Image.Image, np.ndarray]],
        ocr_text: str = "",
        filename: str = ""
    ) -> Dict[str, Any]:
        """
        Processes sampled video frames using pretrained video classification and multi-indicator fallback.
        """
        if not frames:
            return {
                "detected": False,
                "score": 0.0,
                "model": self.video_model_name,
                "source": "video",
                "status": "empty_input"
            }

        rgb_frames = []
        pil_frames = []
        for f in frames:
            if isinstance(f, Image.Image):
                pil_frames.append(f.convert("RGB"))
                rgb_frames.append(np.array(f.convert("RGB")))
            elif isinstance(f, np.ndarray):
                rgb_frames.append(f)
                pil_frames.append(Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)))

        ml_violence_score = 0.0

        if self._pipe is not None and pil_frames:
            try:
                # Video classification pipeline accepts list of PIL images or video path
                results = self._pipe(pil_frames)
                if isinstance(results, list):
                    for r in results:
                        lbl = str(r.get("label", "")).lower()
                        score = float(r.get("score", 0.0))
                        if any(v_kw in lbl for v_kw in self.VIOLENT_ACTION_LABELS):
                            ml_violence_score = max(ml_violence_score, score)
            except Exception as e:
                print(f"[ViolenceDetector ERROR] ML pipeline inference error: {e}")

        # Multi-indicator heuristic score
        heur_score = self._heuristic_violence_eval(rgb_frames, ocr_text=ocr_text, filename=filename)

        final_violence_score = max(ml_violence_score, heur_score)
        detected = final_violence_score >= self.threshold

        return {
            "detected": detected,
            "score": round(final_violence_score, 4),
            "ml_score": round(ml_violence_score, 4),
            "heur_score": round(heur_score, 4),
            "model": self.video_model_name,
            "source": "video",
            "status": "success"
        }

    def predict_image(
        self,
        image_input: Union[str, Image.Image, np.ndarray],
        ocr_text: str = "",
        filename: str = ""
    ) -> Dict[str, Any]:
        """
        Processes a static image advertisement for violent/threat content.
        """
        pil_img = None
        file_name = filename
        if isinstance(image_input, str) and os.path.exists(image_input):
            file_name = file_name or os.path.basename(image_input)
            try:
                pil_img = Image.open(image_input).convert("RGB")
            except Exception:
                pass
        elif isinstance(image_input, Image.Image):
            pil_img = image_input
        elif hasattr(image_input, "dtype"):
            pil_img = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))

        if pil_img is None:
            return {
                "detected": False,
                "score": 0.0,
                "model": "image_violence_detector",
                "source": "image",
                "status": "invalid_image"
            }

        img_np = np.array(pil_img)
        res = self.predict_video_frames([img_np], ocr_text=ocr_text, filename=file_name)
        res["source"] = "image"
        res["model"] = "image_violence_detector"
        return res
