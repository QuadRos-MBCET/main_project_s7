"""
MiniFASNet State-of-the-Art Face Anti-Spoofing Deep Learning Engine
Implements the official MiniVision Silent-Face-Anti-Spoofing dual-model ensemble:
- Model 1: MiniFASNetV2 (scale 2.7 for medium face and facial boundary context)
- Model 2: MiniFASNetV1SE (scale 4.0 for wide device/bezel/background context)
Pre-trained on CelebA-Spoof and CASIA-SURF presentation attack datasets.
Class outputs:
  Class 0: Print Attack (photograph, paper badge)
  Class 1: Live Human Subject
  Class 2: Replay Attack (smartphone screen, tablet, LCD/OLED display)
"""

import os
import cv2
import numpy as np
import torch
from website.FasNetBackbone import MiniFASNetV1SE, MiniFASNetV2
from website.FasNetUtils import crop

class DeepFASNetPredictor:
    """
    Singleton deep learning face anti-spoofing predictor using dual MiniFASNet models.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.device = torch.device("cpu")
        self.loaded = False
        self.model_v2 = None
        self.model_v1se = None

        curr_dir = os.path.dirname(os.path.abspath(__file__))
        weights_dir = os.path.join(curr_dir, "weights")
        v2_path = os.path.join(weights_dir, "2.7_80x80_MiniFASNetV2.pth")
        v1se_path = os.path.join(weights_dir, "4_0_0_80x80_MiniFASNetV1SE.pth")

        # Auto-download weights if missing
        os.makedirs(weights_dir, exist_ok=True)
        for path, url in [
            (v2_path, "https://github.com/minivision-ai/Silent-Face-Anti-Spoofing/raw/master/resources/anti_spoof_models/2.7_80x80_MiniFASNetV2.pth"),
            (v1se_path, "https://github.com/minivision-ai/Silent-Face-Anti-Spoofing/raw/master/resources/anti_spoof_models/4_0_0_80x80_MiniFASNetV1SE.pth")
        ]:
            if not os.path.exists(path) or os.path.getsize(path) < 1000000:
                try:
                    import urllib.request
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=15) as resp, open(path, "wb") as out:
                        out.write(resp.read())
                except Exception:
                    pass

        try:
            if os.path.exists(v2_path) and os.path.exists(v1se_path):
                # Load MiniFASNetV2 (scale 2.7)
                m2 = MiniFASNetV2(conv6_kernel=(5, 5)).to(self.device)
                st2 = torch.load(v2_path, map_location=self.device)
                if list(st2.keys())[0].startswith("module."):
                    st2 = {k[7:]: v for k, v in st2.items()}
                m2.load_state_dict(st2)
                m2.eval()
                self.model_v2 = m2

                # Load MiniFASNetV1SE (scale 4.0)
                m1se = MiniFASNetV1SE(conv6_kernel=(5, 5)).to(self.device)
                st1se = torch.load(v1se_path, map_location=self.device)
                if list(st1se.keys())[0].startswith("module."):
                    st1se = {k[7:]: v for k, v in st1se.items()}
                m1se.load_state_dict(st1se)
                m1se.eval()
                self.model_v1se = m1se

                self.loaded = True
        except Exception:
            self.loaded = False

    def predict(self, image_np: np.ndarray, face_bbox: tuple) -> dict:
        """
        Runs dual-scale MiniFASNet inference on face.
        Returns:
            dict with {
                'is_screen': bool,
                'p_screen': float,
                'p_live': float,
                'p_print': float,
                'confidence': float,
                'model_name': str
            }
        """
        if not self.loaded or image_np is None or face_bbox is None:
            return {"is_screen": False, "p_screen": 0.0, "p_live": 1.0, "p_print": 0.0, "confidence": 0.0, "model_name": "None"}

        try:
            x, y, w, h = face_bbox
            c1 = crop(image_np, (x, y, w, h), 2.7, 80, 80)
            c2 = crop(image_np, (x, y, w, h), 4.0, 80, 80)

            t1 = torch.from_numpy(c1.transpose((2, 0, 1))).float().unsqueeze(0).to(self.device)
            t2 = torch.from_numpy(c2.transpose((2, 0, 1))).float().unsqueeze(0).to(self.device)

            with torch.no_grad():
                out1 = torch.softmax(self.model_v2(t1), dim=1).cpu().numpy()[0]
                out2 = torch.softmax(self.model_v1se(t2), dim=1).cpu().numpy()[0]

            comb = (out1 + out2) / 2.0
            p_print = float(comb[0])
            p_live = float(comb[1])
            p_screen = float(comb[2])

            return {
                "is_screen": p_screen >= 0.70,
                "p_screen": round(p_screen, 4),
                "p_live": round(p_live, 4),
                "p_print": round(p_print, 4),
                "confidence": round(p_screen, 4),
                "model_name": "MiniFASNet Dual-Scale Ensemble (SOTA)",
            }
        except Exception:
            return {"is_screen": False, "p_screen": 0.0, "p_live": 1.0, "p_print": 0.0, "confidence": 0.0, "model_name": "None"}


_GLOBAL_FAS_PREDICTOR = None

def get_fasnet_predictor() -> DeepFASNetPredictor:
    global _GLOBAL_FAS_PREDICTOR
    if _GLOBAL_FAS_PREDICTOR is None:
        _GLOBAL_FAS_PREDICTOR = DeepFASNetPredictor()
    return _GLOBAL_FAS_PREDICTOR
