import torch
from facenet_pytorch import MTCNN
from PIL import Image
import numpy as np

from .model_manager import ModelManager

class FaceDetector:
    def __init__(self, device=None, keep_all=True):
        self.device = device or ModelManager.get_device()
        self.detector = MTCNN(keep_all=keep_all, device=self.device)

    def detect_faces(self, image: Image.Image):
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        boxes, probs = self.detector.detect(image)
        
        faces = []
        if boxes is not None:
            for i, (box, prob) in enumerate(zip(boxes, probs)):
                if prob is not None:
                    # MTCNN boxes are [x1, y1, x2, y2]
                    x1, y1, x2, y2 = [int(b) for b in box]
                    # Crop face
                    face_crop = image.crop((x1, y1, x2, y2))
                    faces.append({
                        "face_id": i + 1,
                        "bbox": [x1, y1, x2, y2],
                        "detection_confidence": float(prob),
                        "face_crop": face_crop
                    })
        return faces
