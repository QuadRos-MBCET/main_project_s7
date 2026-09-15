import cv2
from PIL import Image
import numpy as np
import time
from ai.face_age.face_age_pipeline import FaceAgePipeline

def main():
    print("Loading AI Models for Continuous Live Monitoring (MTCNN + ViT)...")
    pipeline = FaceAgePipeline()
    pipeline._initialize_models()
    
    print("Opening video camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not access webcam camera.")
        return

    print("Camera opened successfully!")
    print("---------------------------------------------------------")
    print("Live Real-Time Continuous Monitoring Active.")
    print("Move your face in front of the camera to see live age tracking.")
    print("Press 'Q' to exit.")
    print("---------------------------------------------------------")
    
    frame_count = 0
    last_faces = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame from camera.")
            break

        frame_count += 1
        
        # Run deep learning age estimation every 3 frames for optimal FPS performance
        if frame_count % 3 == 1 or not last_faces:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            try:
                result = pipeline.analyze(pil_image)
                last_faces = result.get("faces", [])
            except Exception as e:
                pass
                
        # Draw bounding boxes and age labels for all detected faces on the live video stream
        annotated_frame = frame.copy()
        for face in last_faces:
            x1, y1, x2, y2 = face["bbox"]
            age_info = face["age_estimation"]
            age_range = age_info.get("age_range", "Unknown")
            confidence = age_info.get("confidence", 0.0)
            normalized = face.get("normalized_age_group", "UNKNOWN")
            
            # Color code box: Red for CHILD, Green for ADULT/TEEN, Yellow for UNKNOWN
            box_color = (0, 0, 255) if normalized == "CHILD" else (0, 255, 0) if normalized in ["ADULT", "TEEN"] else (0, 255, 255)
            
            label = f"Age: {age_range} ({normalized}) | {confidence:.0%}"
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, 2)
            
            # Draw label background box
            (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
            y_label_start = max(0, y1 - 30)
            cv2.rectangle(annotated_frame, (x1, y_label_start), (x1 + text_width + 10, y_label_start + 30), box_color, -1)
            
            # Draw text
            cv2.putText(annotated_frame, label, (x1 + 5, y_label_start + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            
        # Top banner
        cv2.putText(annotated_frame, f"SafeAd AI - Live Continuous Monitoring (Faces: {len(last_faces)})", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        
        cv2.imshow('SafeAd AI - Continuous Live Age Detection (Press Q to exit)', annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
