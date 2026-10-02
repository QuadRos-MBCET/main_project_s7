import cv2
import numpy as np
import base64
from typing import Optional, Tuple

class CameraHandler:
    """
    Manages local hardware camera acquisition and frame verification.
    Ensures camera is acquired ONLY during registration and stops immediately.
    """
    
    @staticmethod
    def capture_single_frame(device_index: int = 0) -> Tuple[bool, Optional[np.ndarray], str]:
        """
        Opens camera, captures exactly one stable frame, and immediately releases camera.
        """
        cap = cv2.VideoCapture(device_index)
        if not cap.isOpened():
            return False, None, "Could not open camera device. Please check hardware permissions."
        
        # Warm up sensor for 3 frames
        for _ in range(3):
            cap.read()
            
        ret, frame = cap.read()
        cap.release()  # Strictly release immediately
        
        if not ret or frame is None:
            return False, None, "Camera frame capture failed."
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return True, rgb_frame, "Frame captured successfully."

    @staticmethod
    def generate_synthetic_face(age_preset: str = "adult") -> np.ndarray:
        """
        Generates simulated face image for testing / demo modes when no physical webcam is attached.
        Presets: 'child' (<14), 'teen' (14-17), 'adult' (18+)
        """
        img = np.ones((240, 240, 3), dtype=np.uint8) * 235
        
        if age_preset == "child":
            # Round juvenile face (width ~ height)
            cv2.ellipse(img, (120, 120), (75, 75), 0, 0, 360, (255, 205, 185), -1)
            cv2.circle(img, (95, 105), 10, (40, 40, 40), -1)
            cv2.circle(img, (145, 105), 10, (40, 40, 40), -1)
            cv2.ellipse(img, (120, 145), (20, 12), 0, 0, 180, (180, 50, 50), 3)
        elif age_preset == "teen":
            # Intermediate face proportions
            cv2.ellipse(img, (120, 120), (68, 85), 0, 0, 360, (250, 195, 175), -1)
            cv2.circle(img, (95, 110), 9, (40, 40, 40), -1)
            cv2.circle(img, (145, 110), 9, (40, 40, 40), -1)
            cv2.line(img, (105, 150), (135, 150), (180, 50, 50), 3)
        else:
            # Adult oval face
            cv2.ellipse(img, (120, 120), (60, 95), 0, 0, 360, (245, 190, 160), -1)
            cv2.circle(img, (95, 110), 8, (40, 40, 40), -1)
            cv2.circle(img, (145, 110), 8, (40, 40, 40), -1)
            cv2.line(img, (100, 160), (140, 160), (160, 40, 40), 3)
            
        return img

    @staticmethod
    def frame_to_base64(frame: np.ndarray) -> str:
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.jpg', bgr)
        return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
