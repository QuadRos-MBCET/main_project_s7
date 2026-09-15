import cv2
from PIL import Image
import numpy as np
import threading
import time
from ai.face_age.face_age_pipeline import FaceAgePipeline

class FastAgeTracker:
    def __init__(self):
        self.pipeline = FaceAgePipeline()
        self.pipeline._initialize_models()
        self.lock = threading.Lock()
        self.latest_result = None
        self.pending_frame = None
        self.is_running = True
        self.is_busy = False
        
        # Start background AI worker thread
        self.thread = threading.Thread(target=self._ai_worker, daemon=True)
        self.thread.start()

    def _ai_worker(self):
        while self.is_running:
            frame_to_process = None
            with self.lock:
                if self.pending_frame is not None:
                    frame_to_process = self.pending_frame
                    self.pending_frame = None
                    self.is_busy = True

            if frame_to_process is not None:
                try:
                    # Scale down frame to 400px width for 5x faster MTCNN & ViT processing
                    h, w = frame_to_process.shape[:2]
                    target_w = 400
                    scale = target_w / float(w) if w > target_w else 1.0
                    
                    if scale < 1.0:
                        small = cv2.resize(frame_to_process, (target_w, int(h * scale)))
                    else:
                        small = frame_to_process
                        
                    rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(rgb_small)
                    
                    res = self.pipeline.analyze(pil_img)
                    
                    # Scale bounding boxes back up to original camera resolution
                    if res.get("faces"):
                        for face in res["faces"]:
                            x1, y1, x2, y2 = face["bbox"]
                            face["bbox"] = [
                                int(x1 / scale), 
                                int(y1 / scale), 
                                int(x2 / scale), 
                                int(y2 / scale)
                            ]
                    
                    with self.lock:
                        self.latest_result = res
                except Exception:
                    pass
                finally:
                    with self.lock:
                        self.is_busy = False
            else:
                time.sleep(0.01)

    def submit_frame(self, frame):
        with self.lock:
            if not self.is_busy:
                self.pending_frame = frame.copy()

    def get_latest_result(self):
        with self.lock:
            return self.latest_result

    def stop(self):
        self.is_running = False

def main():
    print("Initializing Fast Threaded AI Engine (MTCNN + ViT)...")
    tracker = FastAgeTracker()
    
    print("Opening camera feed...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not access webcam.")
        return

    print("Camera opened successfully!")
    print("---------------------------------------------------------")
    print("Fast Continuous Live Age Tracking Active (30+ FPS).")
    print("Move your face in front of the camera for smooth live monitoring.")
    print("Press 'Q' to exit.")
    print("---------------------------------------------------------")
    
    # Fast OpenCV Haar cascade for instantaneous frame-by-frame bounding box tracking
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Submit current frame to background AI thread for ViT age estimation
        tracker.submit_frame(frame)
        
        # Fast local cascade pass for instant smooth box movement
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fast_faces = cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(40, 40))
        
        # Retrieve latest deep learning age prediction from worker thread
        ai_res = tracker.get_latest_result()
        
        annotated = frame.copy()
        
        # Display AI result boxes and predictions
        if ai_res and ai_res.get("faces"):
            for face in ai_res["faces"]:
                x1, y1, x2, y2 = face["bbox"]
                age_info = face["age_estimation"]
                age_range = age_info.get("age_range", "Unknown")
                confidence = age_info.get("confidence", 0.0)
                norm_group = face.get("normalized_age_group", "UNKNOWN")
                
                box_color = (0, 0, 255) if norm_group == "CHILD" else (0, 255, 0)
                label = f"Age: {age_range} ({norm_group}) | {confidence:.0%}"
                
                # Draw main bounding box
                cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 3)
                
                # Draw header label box
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
                y_start = max(0, y1 - 30)
                cv2.rectangle(annotated, (x1, y_start), (x1 + tw + 10, y_start + 30), box_color, -1)
                cv2.putText(annotated, label, (x1 + 5, y_start + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        elif len(fast_faces) > 0:
            # Fallback instant bounding box while ViT thread computes initial frame
            for (x, y, w, h) in fast_faces:
                cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 255), 2)
                cv2.putText(annotated, "Analyzing Age...", (x, max(0, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

        cv2.putText(annotated, "SafeAd AI - Fast Live Age Tracker (Press Q to exit)", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        
        cv2.imshow('SafeAd AI - Live Continuous Face Age Tracker', annotated)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    tracker.stop()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
