import os
import time
import yaml
from PIL import Image
from typing import Dict, Any, List

from ai.config import DEVICE, MAX_VIDEO_FRAMES, IS_COLAB
from ai.memory_manager import MemoryManager
from ai.ocr.ocr_extractor import extract_ocr_from_image, extract_video_ocr
from ai.pipeline import validate_advertisement_input, sample_video_frames, print_video_processing_report
from ai.safety.model_manager import safety_model_manager
from ai.safety.violence_detector import ViolenceDetector
from ai.safety.nsfw_detector import NSFWDetector
from ai.safety.child_safety_detector import ChildSafetyDetector

class SafetyPipeline:
    """
    Standardized AI Safety Detection Pipeline for SafeAd AI.
    Optimized strictly for Google Colab Free execution.
    """

    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../configs/colab_config.yaml")
        )
        self.config = self._load_config()
        self.max_video_frames = self.config.get("video_processing", {}).get("max_frames", MAX_VIDEO_FRAMES)
        self.nsfw_aggregation = self.config.get("models", {}).get("nsfw", {}).get("aggregation_method", "max")
        
        # Register model loaders with SafetyModelManager for sequential execution
        safety_model_manager.register_loader("violence", lambda: ViolenceDetector().load_model())
        safety_model_manager.register_loader("nsfw", lambda: NSFWDetector().load_model())
        safety_model_manager.register_loader("child_safety", lambda: ChildSafetyDetector().load_model())

    def _load_config(self) -> dict:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"[SafetyPipeline WARNING] Could not parse config yaml ({e}). Using defaults.")
        return {}

    def analyze_advertisement(self, file_path: str) -> Dict[str, Any]:
        """
        Executes end-to-end safety evidence extraction on an advertisement (image or video).
        Employs sequential model loading to preserve Google Colab Free VRAM.
        """
        pipeline_start = time.time()
        timing_breakdown = {}
        failed_components = []

        # 1. Input Validation & Metadata Extraction
        t0 = time.time()
        is_valid, media_type_or_err = validate_advertisement_input(file_path)
        if not is_valid:
            return {
                "status": "error",
                "error": f"Invalid input file: {media_type_or_err}",
                "file_name": os.path.basename(file_path) if os.path.exists(file_path) else file_path,
                "media_type": "unknown",
                "conclusive_summary": {
                    "overall_safety_status": "REJECTED_INVALID",
                    "is_safe": False,
                    "primary_violation": "INVALID_INPUT",
                    "summary_statement": f"Execution halted: Invalid input file format or corrupted media ({media_type_or_err})."
                },
                "processing": {
                    "status": "failed",
                    "device": DEVICE,
                    "total_time_seconds": round(time.time() - pipeline_start, 4)
                }
            }

        media_type = media_type_or_err
        file_name = os.path.basename(file_path)

        # Preprocessing & Frame Extraction
        sampled_frames: List[Image.Image] = []
        video_meta = {}
        if media_type == "video":
            print("[1] Video loaded successfully")
            sampled_frames, video_meta = sample_video_frames(file_path, max_frames=self.max_video_frames, return_metadata=True)
            print(f"[2] Duration detected: {video_meta.get('duration', 0.0):.2f}s (FPS: {video_meta.get('fps', 0.0)}, Total Frames: {video_meta.get('total_frames', 0)})")
            if not sampled_frames:
                return {
                    "status": "error",
                    "error": "Failed to extract keyframes from video advertisement.",
                    "file_name": file_name,
                    "media_type": "video",
                    "conclusive_summary": {
                        "overall_safety_status": "REJECTED_CORRUPTED",
                        "is_safe": False,
                        "primary_violation": "UNREADABLE_VIDEO",
                        "summary_statement": "Failed to extract video keyframes."
                    }
                }
            print(f"[3] Representative frames selected ({len(sampled_frames)} frames)")
            eval_img = sampled_frames[len(sampled_frames) // 2]
        else:
            try:
                eval_img = Image.open(file_path).convert("RGB")
                sampled_frames = [eval_img]
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"Corrupted image file: {e}",
                    "file_name": file_name,
                    "media_type": "image",
                    "conclusive_summary": {
                        "overall_safety_status": "REJECTED_CORRUPTED",
                        "is_safe": False,
                        "primary_violation": "CORRUPTED_IMAGE",
                        "summary_statement": f"Corrupted image file: {e}"
                    }
                }

        timing_breakdown["preprocessing_seconds"] = round(time.time() - t0, 4)

        # 2. OCR Text Extraction & Audio Speech Transcription
        t0 = time.time()
        print("[4] Frames preprocessed")
        try:
            if media_type == "video":
                ocr_text = extract_video_ocr(sampled_frames)
            else:
                ocr_text = extract_ocr_from_image(eval_img)
        except Exception as e:
            print(f"[SafetyPipeline WARNING] OCR extraction failed: {e}")
            ocr_text = "No text detected."
            failed_components.append("ocr")
        timing_breakdown["ocr_seconds"] = round(time.time() - t0, 4)

        # 3. Audio Extraction & Speech Transcription (Whisper)
        t0 = time.time()
        audio_res = {
            "available": False,
            "whisper_model": "whisper-base",
            "detected_language": "N/A",
            "transcript": "",
            "status": "not_applicable",
            "message": "Audio analysis skipped for image media type.",
            "transcription_duration_seconds": 0.0,
            "violence": {"risk": False, "score": None},
            "adult_content": {"risk": False, "score": None},
            "child_safety": {"risk": False, "score": None}
        }
        if media_type == "video":
            try:
                from ai.audio.audio_analyzer import AudioAnalyzer
                audio_analyzer = AudioAnalyzer()
                audio_res = audio_analyzer.analyze_audio(file_path)
            except Exception as e_aud:
                print(f"[SafetyPipeline WARNING] Audio analysis component error: {e_aud}")
                audio_res["message"] = f"Audio analysis error: {e_aud}"
                failed_components.append("audio")
        timing_breakdown["audio_seconds"] = round(time.time() - t0, 4)

        # Combine text modalities (OCR + Audio Transcript) for textual safety checks
        combined_text_eval = f"{ocr_text} {audio_res.get('transcript', '')}".strip()

        # 4. Sequential Model Execution: Violence Detection
        t0 = time.time()
        violence_res = {}
        try:
            with safety_model_manager.use("violence") as violence_model:
                if violence_model is not None:
                    if media_type == "video":
                        violence_res = violence_model.predict_video_frames(sampled_frames, ocr_text=combined_text_eval, filename=file_name, sampling_meta=video_meta)
                    else:
                        violence_res = violence_model.predict_image(eval_img, ocr_text=combined_text_eval, filename=file_name)
                else:
                    violence_res = {"detected": False, "score": 0.0, "model": "videomae_kinetics", "status": "load_failed"}
                    failed_components.append("violence")
        except Exception as e:
            print(f"[SafetyPipeline ERROR] Violence detector error: {e}")
            violence_res = {"detected": False, "score": 0.0, "model": "videomae_kinetics", "status": f"error: {e}"}
            failed_components.append("violence")
        timing_breakdown["violence_seconds"] = round(time.time() - t0, 4)
        print("[5] VideoMAE inference completed")


        # 5. Sequential Model Execution: NSFW / Adult Content Detection
        t0 = time.time()
        nsfw_res = {}
        try:
            with safety_model_manager.use("nsfw") as nsfw_model:
                if nsfw_model is not None:
                    if media_type == "video":
                        nsfw_res = nsfw_model.predict_video_frames(
                            sampled_frames,
                            aggregation_method=self.nsfw_aggregation,
                            ocr_text=combined_text_eval
                        )
                    else:
                        nsfw_res = nsfw_model.predict_image(
                            eval_img,
                            ocr_text=combined_text_eval
                        )
                else:
                    nsfw_res = {"detected": False, "score": 0.0, "model": "falconsai_nsfw", "status": "load_failed"}
                    failed_components.append("nsfw")
        except Exception as e:
            print(f"[SafetyPipeline ERROR] NSFW detector error: {e}")
            nsfw_res = {"detected": False, "score": 0.0, "model": "falconsai_nsfw", "status": f"error: {e}"}
            failed_components.append("nsfw")
        timing_breakdown["nsfw_seconds"] = round(time.time() - t0, 4)

        # 6. Sequential Model Execution: Child Safety Risk Detection
        t0 = time.time()
        child_res = {}
        try:
            with safety_model_manager.use("child_safety") as child_model:
                if child_model is not None:
                    child_res = child_model.predict(sampled_frames, ocr_text=combined_text_eval)
                else:
                    child_res = {
                        "risk_detected": False,
                        "score": None,
                        "category": "child_safety_risk",
                        "model": "open_safety_guard",
                        "evidence": "Child safety detector component failed to load.",
                        "status": "load_failed"
                    }
                    failed_components.append("child_safety")
        except Exception as e:
            print(f"[SafetyPipeline ERROR] Child safety detector error: {e}")
            child_res = {
                "risk_detected": False,
                "score": None,
                "category": "child_safety_risk",
                "model": "open_safety_guard",
                "evidence": f"Error during child safety evaluation: {e}",
                "status": f"error: {e}"
            }
            failed_components.append("child_safety")
        timing_breakdown["child_safety_seconds"] = round(time.time() - t0, 4)

        total_time = round(time.time() - pipeline_start, 4)
        gpu_info = MemoryManager.get_gpu_memory_info()

        # Clean VRAM after overall execution
        MemoryManager.clear_gpu_memory()

        # Standardized Output Schema
        status_flag = "success" if not failed_components else "partial"

        # Conclusive Safety Evidence Summary
        detected_risks = []
        if nsfw_res.get("detected", False):
            detected_risks.append(f"ADULT_NSFW_CONTENT (Score: {nsfw_res.get('score', 0.0)})")
        if violence_res.get("detected", False):
            detected_risks.append(f"VIOLENCE_CONTENT (Score: {violence_res.get('score', 0.0)})")
        if child_res.get("risk_detected", False):
            detected_risks.append("CHILD_SAFETY_RISK (Flagged)")

        if detected_risks:
            overall_safety_status = "FLAGGED_UNSAFE"
            is_safe = False
            primary_violation = detected_risks[0]
            summary_statement = f"CRITICAL POLICY RISK DETECTED: Advertisement contains {', '.join(detected_risks)}."
        else:
            overall_safety_status = "PASSED_SAFE"
            is_safe = True
            primary_violation = "NONE"
            summary_statement = "PASSED: No violence, adult/NSFW, or child-safety risk evidence detected in advertisement frames, OCR overlay, or speech transcript."

        print("[6] Video-level prediction generated")

        output_schema = {
            "media_type": media_type,
            "file_name": file_name,
            "conclusive_summary": {
                "overall_safety_status": overall_safety_status,
                "is_safe": is_safe,
                "primary_violation": primary_violation,
                "detected_risks": detected_risks,
                "summary_statement": summary_statement
            },
            "violence": {
                "detected": violence_res.get("detected", False),
                "score": violence_res.get("score", 0.0),
                "model": violence_res.get("model", "videomae_kinetics"),
                "source": violence_res.get("source", media_type)
            },
            "adult_content": {
                "detected": nsfw_res.get("detected", False),
                "score": nsfw_res.get("score", 0.0),
                "mean_score": nsfw_res.get("mean_score", nsfw_res.get("score", 0.0)),
                "frames_evaluated": nsfw_res.get("frames_evaluated", len(sampled_frames)),
                "model": nsfw_res.get("model", "falconsai_nsfw")
            },
            "child_safety": {
                "risk_detected": child_res.get("risk_detected", False),
                "score": child_res.get("score", None),
                "category": "child_safety_risk",
                "model": child_res.get("model", "open_safety_guard"),
                "evidence": child_res.get("evidence", "No child-safety risk flags detected."),
                "limitations": child_res.get("limitations", "")
            },
            "ocr_text": ocr_text,
            "audio": audio_res,
            "frames_analyzed": len(sampled_frames),
            "processing": {
                "status": status_flag,
                "failed_components": failed_components,
                "device": DEVICE,
                "gpu_name": gpu_info.get("device_name", "CPU"),
                "total_time_seconds": total_time,
                "breakdown": timing_breakdown,
                "memory_mb": {
                    "allocated": gpu_info.get("allocated_mb", 0.0),
                    "free": gpu_info.get("free_mb", 0.0)
                }
            }
        }

        if media_type == "video" and video_meta:
            self.print_multimodal_video_analysis_report(output_schema, video_meta)

        return output_schema

    @staticmethod
    def print_multimodal_video_analysis_report(schema: dict, meta: dict):
        """Prints formatted Multimodal Video Analysis Report as specified in Section 12."""
        conclusive = schema.get("conclusive_summary", {})
        violence = schema.get("violence", {})
        adult = schema.get("adult_content", {})
        child = schema.get("child_safety", {})
        audio = schema.get("audio", {})

        conf_score = max(violence.get("score", 0.0) or 0.0, adult.get("score", 0.0) or 0.0)

        print("\n" + "=" * 60)
        print("SAFEAD AI — MULTIMODAL VIDEO ANALYSIS")
        print("=" * 60)
        print("\nVIDEO")
        print(f"Duration:       {meta.get('duration', 0.0):.2f}s")
        print(f"FPS:            {meta.get('fps', 0.0):.2f}")
        print(f"Total Frames:   {meta.get('total_frames', 0)}")
        print(f"Sampled Frames: {meta.get('sampled_frames', 0)}")
        print("-" * 60)

        print("\nVISUAL ANALYSIS")
        print(f"Video Model:      {violence.get('model', 'videomae_kinetics')}")
        print(f"Video Prediction: {conclusive.get('overall_safety_status', 'PASSED_SAFE')}")
        print(f"Confidence:       {conf_score:.4f}")
        print("-" * 60)

        print("\nOCR ANALYSIS")
        print("Extracted Text:")
        print(f'"{schema.get("ocr_text", "No text detected.")}"')
        print("-" * 60)

        print("\nAUDIO ANALYSIS")
        print(f"Audio Available:   {'YES' if audio.get('available') else 'NO'}")
        print(f"Whisper Model:     {audio.get('whisper_model', 'N/A')}")
        print(f"Detected Language: {audio.get('detected_language', 'N/A')}")
        print("Transcript:")
        tx = audio.get('transcript', '')
        if tx:
            print(f'"{tx}"')
        else:
            print('"No spoken speech detected."')
        print("-" * 60)

        print("\nSAFETY EVIDENCE")
        print(f"Violence Evidence:     {'DETECTED [UNSAFE]' if violence.get('detected') else 'CLEAN [SAFE]'} (Score: {violence.get('score', 0.0)})")
        print(f"Adult/NSFW Evidence:   {'DETECTED [UNSAFE]' if adult.get('detected') else 'CLEAN [SAFE]'} (Score: {adult.get('score', 0.0)})")
        print(f"Child Safety Evidence: {'RISK FLAGGED [UNSAFE]' if child.get('risk_detected') else 'NO RISK [SAFE]'}")
        print("-" * 60)


        print("\nCURRENT SAFETY DECISION")
        print(f"Classification: {conclusive.get('overall_safety_status', 'PASSED_SAFE')}")
        print(f"Confidence:     {conf_score:.4f}")
        print(f"Explanation:    {conclusive.get('summary_statement', '')}")
        print("=" * 60 + "\n")

