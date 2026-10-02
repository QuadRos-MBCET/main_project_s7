from PIL import Image
from typing import Dict, Any

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
        
        result_faces = []
        for face in detected_faces:
            age_estimation = self.age_estimator.estimate_age(face["face_crop"])
            
            normalized_group = normalize_age_prediction(
                age_range=age_estimation["age_range"], 
                confidence=age_estimation["confidence"]
            )
            
            # don't return face_crop in final JSON output
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
