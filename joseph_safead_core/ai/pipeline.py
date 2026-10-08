import os
import cv2
import numpy as np
from PIL import Image
try:
    import torch
except ImportError:
    torch = None
from ai.config import MAX_VIDEO_FRAMES, FRAME_SAMPLE_STRATEGY
from ai.ocr.ocr_extractor import extract_ocr_from_image
from ai.memory_manager import MemoryManager

try:
    from ai.vision.feature_extractor import extract_visual_features_sequential
    from ai.text.text_processor import analyze_multimodal_text
    from ai.retrieval.faiss_retriever import retrieve_similar_exemplar
    from ai.explainability.cot_explainer import generate_cot_explanation
    from ai.safead_adapter import SafeAdModelService
except ImportError:
    extract_visual_features_sequential = None
    analyze_multimodal_text = None
    retrieve_similar_exemplar = None
    generate_cot_explanation = None
    SafeAdModelService = None

def validate_advertisement_input(file_path: str) -> tuple:
    """Validates input file existence, media type, and integrity."""
    if not os.path.exists(file_path):
        return False, "File does not exist on disk."
        
    ext = os.path.splitext(file_path)[1].lower()
    supported_imgs = [".jpg", ".jpeg", ".png", ".webp"]
    supported_vids = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv", ".m4v", ".3gp"]
    
    if ext in supported_imgs:
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True, "image"
        except Exception as e:
            return False, f"Corrupted image file: {e}"
            
    elif ext in supported_vids:
        try:
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return False, "Unreadable video stream."
            cap.release()
            return True, "video"
        except Exception as e:
            return False, f"Corrupted video file: {e}"
            
    return False, f"Unsupported file extension: {ext}"

def sample_video_frames(video_path: str, max_frames: int = MAX_VIDEO_FRAMES) -> list:
    """
    Uniformly samples representative frames from a video file
    without loading the entire video into RAM/VRAM.
    """
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        return []
        
    indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
    sampled_frames = []
    
    for idx in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        if idx in indices:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            sampled_frames.append(Image.fromarray(frame_rgb))
            
    cap.release()
    return sampled_frames

def run_safead_inference(file_path: str, title: str = "", caption: str = "") -> dict:
    """
    Runs the complete memory-efficient advertisement safety inference pipeline.
    Suitable for Google Colab Free execution.
    """
    is_valid, media_type = validate_advertisement_input(file_path)
    if not is_valid:
        return {
            "error": f"Invalid Input: {media_type}",
            "classification": "UNSAFE_FOR_ALL",
            "risk_score": None,
            "risk_score_available": False,
            "risk_category": "invalid_input",
            "explanation": f"Input validation failure: {media_type}",
            "age_restriction": None,
            "action": "REJECT",
            "publishable": False,
            "violations": ["Invalid Input"]
        }
        
    print(f"[SafeAd Inference] Processing {media_type.upper()}: {os.path.basename(file_path)}...")
    
    # 1. Video vs Image input handling
    if media_type == "video":
        frames = sample_video_frames(file_path, max_frames=MAX_VIDEO_FRAMES)
        if not frames:
            return {"error": "Failed to extract keyframes from video."}
        # Process middle keyframe for visual analysis
        target_img = frames[len(frames) // 2]
        temp_img_path = file_path + "_keyframe.jpg"
        target_img.save(temp_img_path)
        eval_path = temp_img_path
    else:
        eval_path = file_path
        temp_img_path = None
        
    # 2. Sequential Visual Feature Extraction (YOLO, BLIP, VRAM release)
    visual_results = extract_visual_features_sequential(eval_path)
    
    # 3. OCR Text Extraction
    ocr_text = extract_ocr_from_image(eval_path)
    
    # Clean temporary keyframe if created
    if temp_img_path and os.path.exists(temp_img_path):
        os.remove(temp_img_path)
        
    # 4. Text & Multilingual NLP Analysis
    text_results = analyze_multimodal_text(
        title=title,
        caption=caption,
        ocr_text=ocr_text,
        image_caption=visual_results["generated_caption"]
    )
    
    # 5. Multimodal Risk Fusion Score (Visual 40%, Text 60%)
    fused_risk_score = (visual_results["visual_risk_score"] * 0.4) + (text_results["text_risk_score"] * 0.6)
    
    # 6. FAISS Vector Retrieval for Historical Policy Exemplar Match
    faiss_match = retrieve_similar_exemplar(text_results["combined_text"])
    
    # 7. Chain-of-Thought (CoT) Explanation Generation
    all_violations = list(set(text_results["violations"]))
    
    # Determine candidate classification for explanation
    candidate_class = "SAFE_FOR_ALL"
    if fused_risk_score > 75.0 or visual_results["visual_risk_score"] > 85.0 or "Violence" in all_violations or "Misleading Advertisement" in all_violations:
        candidate_class = "UNSAFE_FOR_ALL"
    elif "Gambling" in all_violations or "Adult/Sexual Content" in all_violations or "Alcohol/Tobacco" in all_violations or "Drugs" in all_violations or fused_risk_score > 35.0:
        candidate_class = "AGE_18_PLUS"
    elif fused_risk_score > 20.0:
        candidate_class = "AGE_14_PLUS"
        
    explanation_str = generate_cot_explanation(
        classification=candidate_class,
        risk_score=fused_risk_score,
        risk_score_available=True,
        violations=all_violations,
        ocr_text=ocr_text,
        detected_objects=visual_results["detected_objects"],
        similar_case=faiss_match
    )
    
    # 8. Standardized Prediction Schema Adaptation
    final_output = SafeAdModelService.adapt_prediction(
        fused_score=fused_risk_score,
        visual_risk=visual_results["visual_risk_score"],
        text_risk=text_results["text_risk_score"],
        violations=all_violations,
        explanation_str=explanation_str
    )
    
    # Attach extra metadata for UI display
    final_output["extracted_ocr"] = ocr_text
    final_output["detected_objects"] = visual_results["detected_objects"]
    final_output["generated_caption"] = visual_results["generated_caption"]
    final_output["faiss_match"] = faiss_match
    
    MemoryManager.clear_gpu_memory()
    return final_output

if __name__ == "__main__":
    # Dry run check
    print("Running dry run check on pipeline...")
    MemoryManager.print_resource_status()
