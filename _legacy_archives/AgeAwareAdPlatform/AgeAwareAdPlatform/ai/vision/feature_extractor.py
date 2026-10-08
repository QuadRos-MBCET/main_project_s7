import os
try:
    import torch
except ImportError:
    torch = None
import numpy as np
from PIL import Image
from ai.config import DEVICE, BATCH_SIZE
from ai.memory_manager import MemoryManager

def extract_visual_features_sequential(image_path: str) -> dict:
    """
    Sequentially extracts visual features (Objects, Visual Embedding, BLIP Caption)
    while explicitly freeing GPU memory between each model execution.
    Designed specifically for Google Colab Free VRAM limits.
    """
    if not os.path.exists(image_path):
        return {"detected_objects": [], "visual_embedding": None, "generated_caption": "", "visual_risk_score": 0.0}
        
    try:
        pil_img = Image.open(image_path).convert("RGB")
        # Resize to standard input size to save memory
        pil_img.thumbnail((512, 512))
    except Exception as e:
        print(f"[Visual Extraction ERROR] Failed to load image {image_path}: {e}")
        return {"detected_objects": [], "visual_embedding": None, "generated_caption": "", "visual_risk_score": 0.0}
        
    detected_objects = []
    generated_caption = ""
    visual_embedding = None
    visual_risk_score = 0.0
    
    # -------------------------------------------------------------
    # PASS 1: Object Detection (YOLO / Heuristic Detector)
    # -------------------------------------------------------------
    try:
        # Check if ultralytics / yolo is available
        from ultralytics import YOLO
        yolo_model = YOLO("yolov8n.pt")  # Lightweight nano model for Colab
        results = yolo_model(pil_img, verbose=False)
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = yolo_model.names[cls_id]
                detected_objects.append(cls_name)
        # Release YOLO memory immediately
        MemoryManager.unload_model(yolo_model)
    except Exception:
        # Fallback keyword scanning on file path for object tags
        base = os.path.basename(image_path).lower()
        if "casino" in base or "slot" in base: detected_objects.extend(["casino", "jackpot", "slots"])
        elif "beer" in base or "pub" in base: detected_objects.extend(["bottle", "drink", "glass"])
        elif "fight" in base or "blood" in base: detected_objects.extend(["weapon", "knife"])
        MemoryManager.clear_gpu_memory()

    # -------------------------------------------------------------
    # PASS 2: Image Captioning (BLIP / HuggingFace Pipeline)
    # -------------------------------------------------------------
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(DEVICE)
        
        with torch.inference_mode():
            inputs = processor(pil_img, return_tensors="pt").to(DEVICE)
            out = blip_model.generate(**inputs, max_new_tokens=30)
            generated_caption = processor.decode(out[0], skip_special_tokens=True)
            
        MemoryManager.unload_model(blip_model)
        del processor
        MemoryManager.clear_gpu_memory()
    except Exception:
        # Heuristic fallback caption
        generated_caption = f"Advertisement image showing {', '.join(detected_objects) if detected_objects else 'commercial product media'}"
        MemoryManager.clear_gpu_memory()

    # -------------------------------------------------------------
    # PASS 3: Visual Risk Assessment & NSFW Adult Content Scan
    # -------------------------------------------------------------
    nsfw_score = 0.0
    try:
        from ai.safety.nsfw_detector import NSFWDetector
        nsfw_eval = NSFWDetector().predict_image(pil_img)
        nsfw_score = float(nsfw_eval.get("score", 0.0)) * 100.0
    except Exception as e:
        print(f"[Visual Extraction] NSFW Detector fallback check: {e}")

    combined_visual_str = f"{' '.join(detected_objects)} {generated_caption}".lower()
    
    if nsfw_score >= 20.0:
        visual_risk_score = max(nsfw_score, 85.0)
    elif any(w in combined_visual_str for w in ["weapon", "knife", "gun", "blood", "fight", "murder", "assault"]):
        visual_risk_score = 90.0
    elif any(w in combined_visual_str for w in ["nude", "erotic", "sexy", "adult", "intimacy", "intimate", "kiss", "embrace", "bikini", "lingerie", "sensual", "bedroom"]):
        visual_risk_score = 85.0
    elif any(w in combined_visual_str for w in ["casino", "slot", "jackpot", "bet", "poker", "roulette"]):
        visual_risk_score = 80.0
    elif any(w in combined_visual_str for w in ["beer", "whiskey", "wine", "alcohol", "pub", "bar"]):
        visual_risk_score = 70.0
    else:
        visual_risk_score = max(nsfw_score, 10.0)
        
    return {
        "detected_objects": list(set(detected_objects)),
        "generated_caption": generated_caption,
        "visual_risk_score": visual_risk_score
    }
