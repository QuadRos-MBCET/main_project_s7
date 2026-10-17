import pytest
from PIL import Image
import numpy as np
import json
from ai.face_age.face_age_pipeline import FaceAgePipeline
from ai.face_age.utils import normalize_age_prediction

@pytest.fixture
def dummy_pipeline():
    return FaceAgePipeline()

def test_normalize_age_prediction():
    # Test confidence low
    assert normalize_age_prediction("10-19", 0.4) == "UNKNOWN"
    
    # Test child mapping
    assert normalize_age_prediction("0-2", 0.9) == "CHILD"
    assert normalize_age_prediction("3-9", 0.8) == "CHILD"
    
    # Test teen mapping
    assert normalize_age_prediction("10-19", 0.85) == "TEEN"
    
    # Test adult mapping
    assert normalize_age_prediction("20-29", 0.99) == "ADULT"
    assert normalize_age_prediction("more than 70", 0.7) == "ADULT"

def test_no_face(dummy_pipeline):
    # create a pure black image (no face)
    img = Image.fromarray(np.zeros((300, 300, 3), dtype=np.uint8))
    result = dummy_pipeline.analyze(img)
    
    assert result["media_type"] == "image"
    assert result["faces_detected"] == 0
    assert len(result["faces"]) == 0

def test_json_serialization():
    # just testing that outputs are serializable
    output = {
        "media_type": "image",
        "faces_detected": 1,
        "faces": [
            {
                "face_id": 1,
                "bbox": [10, 20, 100, 120],
                "detection_confidence": 0.98,
                "age_estimation": {
                    "estimated_age": None,
                    "age_range": "20-29",
                    "confidence": 0.91
                },
                "normalized_age_group": "ADULT"
            }
        ]
    }
    
    json_str = json.dumps(output)
    assert "media_type" in json_str
