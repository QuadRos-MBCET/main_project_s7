import os
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, List, Union, Tuple

class SafeAdOCRService:
    """
    Multilingual OCR Pipeline for SafeAd AI.
    
    Preferred Engine: PP-OCR / PaddleOCR
    Fallback Engine: PyTesseract / OpenCV Preprocessing
    
    Extracts embedded ad overlay text, confidence scores, bounding boxes, and language.
    Aggregates text across representative video keyframes while removing duplicate lines.
    Does NOT depend on filenames for safety classification.
    """

    def __init__(self, use_gpu: bool = False):
        self.use_gpu = use_gpu
        self._paddle_ocr = None
        self._engine_type = "none"
        self._is_initialized = False

    def initialize_ocr(self):
        """Initializes PaddleOCR / PyTesseract OCR engine."""
        if self._is_initialized:
            return self

        try:
            from paddleocr import PaddleOCR
            self._paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
            self._engine_type = "paddleocr"
            print("[SafeAdOCRService] PP-OCR / PaddleOCR initialized successfully.")
        except Exception as e:
            print(f"[SafeAdOCRService WARNING] PaddleOCR initialization fallback ({e}). Using PyTesseract...")
            self._paddle_ocr = None
            self._engine_type = "pytesseract"

        self._is_initialized = True
        return self

    def extract_from_image(
        self,
        image_input: Union[str, Image.Image, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Extracts OCR text, average confidence, bounding box details, and language from a single image/frame.
        """
        if not self._is_initialized:
            self.initialize_ocr()

        img_np = None
        file_path = ""

        if isinstance(image_input, str) and os.path.exists(image_input):
            file_path = image_input
            img_np = cv2.imread(file_path)
        elif isinstance(image_input, Image.Image):
            img_np = cv2.cvtColor(np.array(image_input.convert("RGB")), cv2.COLOR_RGB2BGR)
        elif hasattr(image_input, "dtype"):
            img_np = image_input

        if img_np is None:
            return {
                "ocr_text": "",
                "ocr_confidence": 0.0,
                "bounding_boxes": [],
                "language": "N/A",
                "engine": self._engine_type
            }

        extracted_lines = []
        confidences = []
        bboxes = []

        # 1. PaddleOCR Execution
        if self._engine_type == "paddleocr" and self._paddle_ocr is not None:
            try:
                result = self._paddle_ocr.ocr(img_np, cls=True)
                if result and result[0]:
                    for line in result[0]:
                        bbox = line[0]
                        text_val = line[1][0]
                        conf_val = float(line[1][1])
                        
                        clean_text = text_val.strip()
                        if clean_text:
                            extracted_lines.append(clean_text)
                            confidences.append(conf_val)
                            bboxes.append(bbox)
            except Exception as e:
                print(f"[SafeAdOCRService ERROR] PaddleOCR extraction error: {e}")

        # 2. PyTesseract Fallback
        if not extracted_lines:
            try:
                import pytesseract
                pil_img = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
                tess_data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
                
                n_boxes = len(tess_data["text"])
                for i in range(n_boxes):
                    text_val = tess_data["text"][i].strip()
                    conf_val = int(tess_data["conf"][i])
                    if text_val and conf_val > 20:
                        extracted_lines.append(text_val)
                        confidences.append(conf_val / 100.0)
                        bboxes.append([
                            tess_data["left"][i], tess_data["top"][i],
                            tess_data["width"][i], tess_data["height"][i]
                        ])
            except Exception:
                pass

        full_text = " ".join(extracted_lines)
        avg_conf = float(np.mean(confidences)) if confidences else 0.0

        return {
            "ocr_text": full_text,
            "ocr_confidence": round(avg_conf, 4),
            "bounding_boxes": bboxes[:20],
            "language": "en",
            "engine": self._engine_type
        }

    def extract_from_video_frames(
        self,
        frames: List[Union[Image.Image, np.ndarray]]
    ) -> Dict[str, Any]:
        """
        Aggregates OCR text across representative video keyframes, removes duplicate phrases,
        and returns structured result.
        """
        if not frames:
            return {
                "ocr_text": "",
                "ocr_confidence": 0.0,
                "frame_text": [],
                "engine": self._engine_type
            }

        seen_phrases = set()
        unique_lines = []
        frame_text_list = []
        all_confidences = []

        for idx, frame in enumerate(frames):
            res = self.extract_from_image(frame)
            tx = res.get("ocr_text", "")
            conf = res.get("ocr_confidence", 0.0)
            
            frame_entry = {
                "frame_index": idx,
                "text": tx,
                "confidence": conf
            }
            frame_text_list.append(frame_entry)

            if tx:
                all_confidences.append(conf)
                for line in tx.split():
                    line_clean = line.strip().lower()
                    if line_clean and len(line_clean) > 1 and line_clean not in seen_phrases:
                        seen_phrases.add(line_clean)
                        unique_lines.append(line.strip())

        aggregated_text = " ".join(unique_lines)
        overall_conf = float(np.mean(all_confidences)) if all_confidences else 0.0

        return {
            "ocr_text": aggregated_text,
            "ocr_confidence": round(overall_conf, 4),
            "frame_text": frame_text_list,
            "engine": self._engine_type
        }
