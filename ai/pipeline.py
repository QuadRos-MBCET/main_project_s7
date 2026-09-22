import os
import time
from typing import Dict, Any, List, Optional
from PIL import Image

from processing.preprocessing import validate_advertisement_file
from processing.video_sampling import extract_adaptive_keyframes, get_video_metadata
from processing.audio_extraction import extract_audio_to_wav, cleanup_audio_file

from models.model_manager import model_manager
from models.visual_safety import VisualSafetyDetector
from models.nsfw_detector import SafeAdNSFWDetector
from models.violence_detector import SafeAdViolenceDetector
from models.ocr_service import SafeAdOCRService
from models.audio_service import SafeAdAudioService
from models.text_safety import SafeAdTextSafetyDetector
from models.fusion.safead_fusion import SafeAdFusion

# Singleton instances for lazy invocation
visual_detector = VisualSafetyDetector()
nsfw_detector = SafeAdNSFWDetector()
violence_detector = SafeAdViolenceDetector()
ocr_service = SafeAdOCRService()
audio_service = SafeAdAudioService()
text_safety_detector = SafeAdTextSafetyDetector()
fusion_engine = SafeAdFusion()

def run_safead_inference(
    file_path: str,
    title: str = "",
    caption: str = ""
) -> Dict[str, Any]:
    """
    Executes the complete end-to-end SafeAd AI multimodal advertisement moderation pipeline.
    
    8-Step Progress Workflow:
    [1] Upload & File Validation
    [2] Content Extraction (Keyframes & Audio)
    [3] Multilingual OCR Text Analysis (PP-OCR / PaddleOCR)
    [4] Visual Safety & Adult/NSFW Analysis (Llama Guard Vision & Falconsai ViT)
    [5] Video Violence Analysis (VideoMAE)
    [6] Audio Speech Transcription & Text Safety (Whisper & Llama Guard 3-1B)
    [7] Multimodal Evidence Fusion (SafeAdFusion Layer)
    [8] Final Policy Decision & Explanation
    """
    start_total_time = time.time()
    stage_timings = {}
    filename_str = os.path.basename(file_path) if file_path else ""

    # STEP 1: Upload & Input Validation
    step1_start = time.time()
    is_valid, media_type, status_msg = validate_advertisement_file(file_path)
    stage_timings["step1_validation"] = round(time.time() - step1_start, 4)

    if not is_valid:
        return {
            "classification": "UNSAFE_FOR_ALL",
            "display_label": "Unsafe for All",
            "risk_score": 100.0,
            "confidence": 1.0,
            "publication_action": "REJECT",
            "action_badge": "REJECT — UNSAFE FOR ALL",
            "detected_categories": ["Invalid Input"],
            "explanation": f"Input validation failed: {status_msg}",
            "evidence": {},
            "stage_timings": stage_timings,
            "total_processing_time_seconds": round(time.time() - start_total_time, 4)
        }

    print(f"\n[SafeAd AI] Moderate {media_type.upper()}: {os.path.basename(file_path)}")

    # STEP 2: Extracting Content (Adaptive Keyframes & Audio)
    step2_start = time.time()
    frames = []
    sampling_meta = {}

    if media_type == "video":
        frames, sampling_meta = extract_adaptive_keyframes(file_path, target_frames=16, return_metadata=True)
        print(f"[SafeAd AI] Adaptive sampling extracted {len(frames)} keyframes. Strategy: {sampling_meta.get('sampling_strategy')}")
    else:
        try:
            pil_img = Image.open(file_path).convert("RGB")
            frames = [pil_img]
            sampling_meta = {"duration": 0.0, "total_frames": 1, "sampling_strategy": "Single Image Input"}
        except Exception:
            frames = []

    stage_timings["step2_extraction"] = round(time.time() - step2_start, 4)

    # STEP 3: Multilingual OCR Analysis
    step3_start = time.time()
    if media_type == "video" and frames:
        ocr_res = ocr_service.extract_from_video_frames(frames)
    else:
        ocr_res = ocr_service.extract_from_image(file_path if os.path.exists(file_path) else (frames[0] if frames else ""))
    stage_timings["step3_ocr"] = round(time.time() - step3_start, 4)

    ocr_text_combined = f"{title or ''} {caption or ''} {ocr_res.get('ocr_text', '')}".strip()
    ocr_text_safety = text_safety_detector.predict_text(ocr_text_combined)

    # STEP 4: Visual Safety Analysis & Adult/NSFW Analysis (Llama Guard Vision & Falconsai ViT)
    step4_start = time.time()
    visual_res = visual_detector.analyze_video_frames(frames) if frames else {"unsafe": False, "confidence": 0.0, "detected_categories": []}
    nsfw_res = nsfw_detector.predict_video_frames(frames, ocr_text=ocr_text_combined) if frames else {"adult_score": 0.0, "adult_content_detected": False}
    model_manager.clear_gpu_memory()
    stage_timings["step4_visual_nsfw"] = round(time.time() - step4_start, 4)

    # STEP 5: Video Violence Analysis (VideoMAE)
    step5_start = time.time()
    violence_res = violence_detector.predict_video_frames(frames, ocr_text=ocr_text_combined, filename=filename_str, sampling_meta=sampling_meta) if (media_type == "video" and frames) else {"violence_score": 0.0, "violence_detected": False, "sampled_segments": []}
    model_manager.clear_gpu_memory()
    stage_timings["step5_violence"] = round(time.time() - step5_start, 4)

    # STEP 6: Audio Speech Transcription & Safety (Whisper)
    step6_start = time.time()
    audio_res = {
        "audio_available": False,
        "transcript": "",
        "audio_safety": {"violence": 0.0, "adult": 0.0, "child_safety": 0.0, "overall_risk": 0.0},
        "status": "not_applicable"
    }

    if media_type == "video":
        audio_res = audio_service.process_video_audio(file_path, text_safety_detector=text_safety_detector)
        model_manager.clear_gpu_memory()
    stage_timings["step6_audio"] = round(time.time() - step6_start, 4)

    # STEP 7: Multimodal Safety Evidence Fusion
    step7_start = time.time()
    fusion_output = fusion_engine.combine_evidence(
        visual_evidence=visual_res,
        video_violence_evidence=violence_res,
        nsfw_evidence=nsfw_res,
        ocr_evidence=ocr_res,
        ocr_text_safety=ocr_text_safety,
        audio_evidence=audio_res,
        context_evidence={"status": "faiss_context_active"}
    )
    stage_timings["step7_fusion"] = round(time.time() - step7_start, 4)

    # STEP 8: Final Decision Formatting & Memory Cleanup
    step8_start = time.time()
    total_processing_time = round(time.time() - start_total_time, 4)
    stage_timings["step8_decision"] = round(time.time() - step8_start, 4)

    fusion_output["stage_timings"] = stage_timings
    fusion_output["total_processing_time_seconds"] = total_processing_time
    fusion_output["media_type"] = media_type
    fusion_output["extracted_ocr"] = ocr_res.get("ocr_text", "")
    fusion_output["audio_transcript"] = audio_res.get("transcript", "")
    fusion_output["audio_available"] = audio_res.get("audio_available", False)

    model_manager.clear_gpu_memory()

    print(f"[SafeAd AI] Completed inference in {total_processing_time}s. Classification: {fusion_output['classification']} (Score: {fusion_output['risk_score']}/100)")
    return fusion_output


if __name__ == "__main__":
    print("Testing SafeAd AI pipeline initialization...")
    test_res = run_safead_inference("apples_ad.jpg", "Fresh Apples Offer", "Buy fresh apples online!")
    print(test_res)
