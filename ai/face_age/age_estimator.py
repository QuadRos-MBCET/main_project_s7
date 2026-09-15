import torch
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import torch.nn.functional as F

from .model_manager import ModelManager

class AgeEstimator:
    def __init__(self, model_name="nateraw/vit-age-classifier", device=None):
        self.device = device or ModelManager.get_device()
        self.feature_extractor = ViTImageProcessor.from_pretrained(model_name)
        self.model = ViTForImageClassification.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def estimate_age(self, face_image: Image.Image):
        inputs = self.feature_extractor(images=face_image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.inference_mode():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=1)
            
            confidence, predicted_class_idx = torch.max(probs, 1)
            predicted_class_idx = predicted_class_idx.item()
            confidence = confidence.item()
            
            age_range = self.model.config.id2label[predicted_class_idx]
            
        return {
            "estimated_age": None,
            "age_range": age_range,
            "confidence": round(confidence, 4)
        }
