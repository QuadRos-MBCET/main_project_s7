import cv2
from PIL import Image
import numpy as np
from ai.face_age.face_age_pipeline import FaceAgePipeline

def main():
    print("Loading AI Models (this may take a moment)...")
    pipeline = FaceAgePipeline()
    
    print("Opening camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Camera opened successfully!")
    print("-----------------------------------------")
    print("Press 'SPACE' to capture and analyze an image.")
    print("Press 'Q' to quit.")
    print("-----------------------------------------")
    
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        # Display the live video feed
        cv2.imshow('Camera - Press SPACE to analyze, Q to quit', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Press 'SPACE' to capture and analyze
        if key == 32:  
            print("\nAnalyzing captured image...")
            # Convert BGR (OpenCV) to RGB (PIL)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Run inference
            result = pipeline.analyze(pil_image)
            
            # Draw bounding boxes and labels on the captured frame
            annotated_frame = frame.copy()
            for face in result.get("faces", []):
                x1, y1, x2, y2 = face["bbox"]
                
                age_info = face["age_estimation"]
                age_range = age_info["age_range"]
                confidence = age_info["confidence"]
                normalized = face["normalized_age_group"]
                
                if confidence < 0.5:
                    label = "Age: Unknown"
                else:
                    label = f"{age_range} ({normalized}) conf:{confidence:.2f}"
                
                # Draw red rectangle around the face
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                
                # Draw background for text to make it readable
                (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(annotated_frame, (x1, y1 - 25), (x1 + text_width, y1), (0, 0, 255), -1)
                
                # Draw text
                cv2.putText(annotated_frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
            print(f"Detected {result['faces_detected']} face(s).")
            
            # Show the result in a new window until a key is pressed
            cv2.imshow('Analysis Result - Press any key to close', annotated_frame)
            cv2.waitKey(0)
            cv2.destroyWindow('Analysis Result - Press any key to close')
            
        # Press 'q' to quit
        elif key == ord('q'):
            break

    # Release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
