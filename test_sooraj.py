# Create this file in your project folder and name it: test_sooraj.py
import pytest
from face_detection import detect_faces
# Test 1: Standard valid face image
def test_valid_image():
    assert detect_faces("valid_face.jpg") >= 1
# Test 2: Missing or empty image file
def test_empty_image():
    with pytest.raises(ValueError):
        detect_faces("empty.jpg")
# Test 3: Corrupted file input (Equivalence Partitioning)
def test_corrupted_image():
    with pytest.raises(IOError):
        detect_faces("corrupt.txt")
# Test 4: Image with exactly 0x0 resolution (Boundary Value Analysis)
def test_zero_resolution():
    with pytest.raises(ValueError):
        detect_faces("zero_res.jpg")
# Test 5: Unsupported format (Equivalence Partitioning)
def test_unsupported_format():
    with pytest.raises(ValueError):
        detect_faces("video.mp4")
