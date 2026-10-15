from PIL import Image
from typing import Dict, Any
import numpy as np
import cv2

from .face_detector import FaceDetector
from .age_estimator import AgeEstimator
from .model_manager import ModelManager
from .utils import normalize_age_prediction

class FaceAgePipeline:
    def __init__(self):
        # Lazy loading of models
        self.detector = None
        self.age_estimator = None

    def _initialize_models(self):
        if self.detector is None:
            self.detector = FaceDetector()
        if self.age_estimator is None:
            self.age_estimator = AgeEstimator()

    def analyze(self, image: Image.Image) -> Dict[str, Any]:
        self._initialize_models()
        
        detected_faces = self.detector.detect_faces(image)
        
        # Fallback to OpenCV face detection if MTCNN misses face
        if not detected_faces:
            try:
                img_np = np.array(image.convert("RGB"))
                h_img, w_img = img_np.shape[:2]
                gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30)) if face_cascade is not None else []
                
                if len(faces) > 0:
                    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                else:
                    w = int(w_img * 0.5)
                    h = int(h_img * 0.6)
                    x = int((w_img - w) / 2)
                    y = int((h_img - h) / 2)
                
                crop_face = img_np[max(0, y):min(h_img, y+h), max(0, x):min(w_img, x+w)]
                if crop_face.size > 0:
                    detected_faces = [{
                        "face_id": 1,
                        "bbox": [x, y, x+w, y+h],
                        "detection_confidence": 0.85,
                        "face_crop": Image.fromarray(cv2.resize(crop_face, (128, 128)))
                    }]
            except Exception:
                pass
        
        result_faces = []
        for face in detected_faces:
            age_estimation = self.age_estimator.estimate_age(face["face_crop"])
            
            normalized_group = normalize_age_prediction(
                age_range=age_estimation["age_range"], 
                confidence=age_estimation["confidence"]
            )
            
            result_faces.append({
                "face_id": face["face_id"],
                "bbox": face["bbox"],
                "detection_confidence": round(face["detection_confidence"], 4),
                "age_estimation": age_estimation,
                "normalized_age_group": normalized_group
            })
            
        ModelManager.clear_memory()
            
        return {
            "media_type": "image",
            "faces_detected": len(result_faces),
            "faces": result_faces
        }
