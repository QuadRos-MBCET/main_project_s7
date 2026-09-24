import os
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, List, Union

try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

from ai.config import DEVICE

class NSFWDetector:
    """
    Adult / NSFW Content Classifier for SafeAd AI.
    
    Pretrained Models & Fallbacks:
    - Falconsai/nsfw_image_detection (ViT Image Classification)
    - YCbCr & HSV skin chrominance filtering fallback
    - ML model prediction priority (prevents false positives on sunsets, sand, and nature media)
    """

    def __init__(self, model_id: str = "Falconsai/nsfw_image_detection", device: str = DEVICE):
        self.model_id = model_id
        self.device = device if (HAS_TORCH and torch.cuda.is_available()) else "cpu"
        self._pipe = None
        self._is_loaded = False
        self.threshold = 0.35  # Sensitive threshold for ad safety moderation

    def load_model(self, *args, **kwargs):
        """Loads Hugging Face pipeline for Falconsai/nsfw_image_detection."""
        if self._is_loaded and self._pipe is not None:
            return self

        print(f"[NSFWDetector] Loading '{self.model_id}' on {self.device}...")
        try:
            from transformers import pipeline
            device_idx = 0 if (HAS_TORCH and torch.cuda.is_available() and self.device == "cuda") else -1
            self._pipe = pipeline(
                "image-classification",
                model=self.model_id,
                device=device_idx,
                top_k=None  # Return ALL class probabilities
            )
            self._is_loaded = True
        except Exception as e:
            print(f"[NSFWDetector WARNING] Hugging Face pipeline fallback: {e}")
            self._pipe = None
            self._is_loaded = True

        return self

    def _heuristic_skin_nsfw_eval(self, pil_img: Image.Image) -> float:
        """
        Calculates human skin-pixel density using YCbCr & HSV chrominance constraints.
        Filters out upper 50% sky regions to prevent false positives on sunsets, deserts, and nature media.
        """
        try:
            img_np = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)
            height, width = img_np.shape[:2]

            # YCbCr Human Skin Filter (Cb: 77..127, Cr: 133..173) with Y brightness cap (Y <= 215)
            ycrcb = cv2.cvtColor(img_np, cv2.COLOR_BGR2YCrCb)
            mask_ycrcb = cv2.inRange(ycrcb, np.array([0, 133, 77], dtype=np.uint8), np.array([215, 173, 127], dtype=np.uint8))
            
            # HSV Human Skin Filter
            hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
            mask_hsv = cv2.inRange(hsv, np.array([0, 30, 60], dtype=np.uint8), np.array([20, 150, 215], dtype=np.uint8))
            
            # Combined Skin Mask requiring BOTH YCbCr AND HSV
            skin_mask = cv2.bitwise_and(mask_ycrcb, mask_hsv)
            total_skin = np.count_nonzero(skin_mask)

            if total_skin == 0:
                return 0.01

            # Upper 50% sky region filter (sunsets, golden hour skies)
            upper_skin = np.count_nonzero(skin_mask[:height // 2, :])
            upper_ratio = upper_skin / total_skin
            if upper_ratio > 0.60:
                # Skin-like pixels are concentrated in the top half of the frame (sky/sun horizon)
                return 0.01

            # Horizontal span filter (ocean sunset reflections, desert dunes)
            col_counts = np.count_nonzero(skin_mask, axis=0)
            active_col_ratio = float(np.count_nonzero(col_counts > 0)) / float(width)
            if active_col_ratio > 0.70:
                # Skin-like color pixels span across the horizon (>70% of frame width)
                return 0.01

            skin_ratio = float(total_skin) / float(skin_mask.size)
            if skin_ratio > 0.35:
                return round(min(0.85, skin_ratio * 1.5), 4)
            return round(max(0.01, skin_ratio * 0.2), 4)
        except Exception:
            return 0.01

    ADULT_TEXT_KEYWORDS = [
        "18+", "adults only", "adult content", "nsfw", "xxx", "sex", "nude", "nudity",
        "erotic", "erotica", "porn", "porno", "strip", "sensual", "escort", "dating 18+",
        "hentai", "camgirl", "nsfw ad", "playboy", "onlyfans", "x-rated", "sexy girls"
    ]

    def _eval_ocr_adult_text(self, ocr_text: str) -> float:
        """Evaluates OCR text overlay for adult/NSFW policy violation keywords."""
        if not ocr_text:
            return 0.0
        text_lower = ocr_text.lower()
        for kw in self.ADULT_TEXT_KEYWORDS:
            if kw in text_lower:
                print(f"[NSFWDetector] Adult policy keyword detected in OCR overlay: '{kw}'")
                return 0.90
        return 0.0

    def predict_image(
        self,
        image_input: Union[str, Image.Image, np.ndarray],
        ocr_text: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluates a single image (or video frame) for NSFW/adult content.
        ML ViT predictions take precedence over fallback color heuristics to prevent false positives on nature media.
        """
        if not self._is_loaded:
            self.load_model()

        pil_img = None
        if isinstance(image_input, str) and os.path.exists(image_input):
            try:
                pil_img = Image.open(image_input).convert("RGB")
            except Exception:
                pass
        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
        elif hasattr(image_input, "dtype"):
            pil_img = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))

        ocr_score = self._eval_ocr_adult_text(ocr_text)

        if pil_img is None:
            return {
                "detected": ocr_score >= self.threshold,
                "score": ocr_score,
                "frames_evaluated": 0,
                "model": "falconsai_nsfw",
                "status": "invalid_input" if ocr_score == 0.0 else "ocr_only"
            }

        nsfw_score = 0.0
        normal_score = 0.0

        if self._pipe is not None:
            try:
                results = self._pipe(pil_img)
                
                for r in results:
                    lbl = str(r.get("label", "")).lower().strip()
                    score = float(r.get("score", 0.0))
                    
                    if any(k in lbl for k in ["nsfw", "porn", "porno", "sexy", "hentai", "explicit", "adult", "erotica", "label_1", "18+"]):
                        nsfw_score = max(nsfw_score, score)
                    elif any(k in lbl for k in ["normal", "neutral", "safe", "label_0"]):
                        normal_score = max(normal_score, score)

            except Exception as e:
                print(f"[NSFWDetector ERROR] Inference error: {e}")

        # Supplementary skin density heuristic
        heur_score = self._heuristic_skin_nsfw_eval(pil_img)

        # ML model prediction priority logic
        if self._pipe is not None:
            if normal_score >= 0.50 or (normal_score > nsfw_score and nsfw_score < 0.35):
                # ML model indicates frame is safe/normal: suppress skin heuristic false positives
                final_nsfw_score = max(nsfw_score, ocr_score)
            else:
                final_nsfw_score = max(nsfw_score, min(heur_score, 0.35), ocr_score)
        else:
            # Offline fallback mode: cap pure skin heuristic at 0.25 unless supported by OCR
            final_nsfw_score = max(nsfw_score, min(heur_score, 0.25), ocr_score)

        detected = final_nsfw_score >= self.threshold




        return {
            "detected": detected,
            "score": round(final_nsfw_score, 4),
            "ml_score": round(nsfw_score, 4),
            "heur_score": round(heur_score, 4),
            "ocr_score": round(ocr_score, 4),
            "frames_evaluated": 1,
            "model": "falconsai_nsfw",
            "status": "success"
        }

    def predict_video_frames(
        self,
        frames: List[Union[Image.Image, np.ndarray]],
        aggregation_method: str = "max",
        ocr_text: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluates sampled video frames for NSFW content.
        """
        ocr_score = self._eval_ocr_adult_text(ocr_text)

        if not frames:
            return {
                "detected": ocr_score >= self.threshold,
                "score": ocr_score,
                "mean_score": ocr_score,
                "frames_evaluated": 0,
                "model": "falconsai_nsfw",
                "status": "empty_frames"
            }

        frame_scores = []
        for f in frames:
            res = self.predict_image(f, ocr_text="")
            frame_scores.append(res.get("score", 0.0))

        max_score = float(np.max(frame_scores)) if frame_scores else 0.0
        mean_score = float(np.mean(frame_scores)) if frame_scores else 0.0

        selected_visual_score = max_score if aggregation_method == "max" else mean_score
        final_video_score = max(selected_visual_score, ocr_score)

        return {
            "detected": final_video_score >= self.threshold,
            "score": round(final_video_score, 4),
            "max_score": round(max_score, 4),
            "mean_score": round(mean_score, 4),
            "ocr_score": round(ocr_score, 4),
            "frames_evaluated": len(frames),
            "model": "falconsai_nsfw",
            "aggregation": aggregation_method,
            "frame_scores": [round(s, 4) for s in frame_scores],
            "status": "success"
        }
