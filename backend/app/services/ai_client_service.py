import os
import mimetypes
import time
from typing import Optional, Dict, Any
import requests
from backend.app.core.config import settings

class AIClientService:
    @staticmethod
    def test_colab_connection(colab_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Tests connection to the specified or configured Google Colab tunnel URL.
        """
        target = (colab_url or settings.COLAB_API_URL or "").strip().rstrip("/")
        if not target:
            return {"status": "unconfigured", "message": "No Colab URL provided."}
        try:
            res = requests.get(
                f"{target}/health",
                headers={"ngrok-skip-browser-warning": "69420", "User-Agent": "SafeAd-Backend/1.0"},
                timeout=30.0
            )
            if res.status_code == 200:
                data = res.json()
                return {
                    "status": "online",
                    "url": target,
                    "model": data.get("model", "Qwen3-VL-8B-Instruct"),
                    "device": data.get("device", "cuda"),
                    "gpu": data.get("gpu", "NVIDIA GPU"),
                    "precision": data.get("precision", "bfloat16"),
                    "details": data
                }
            return {"status": "error", "message": f"Server returned HTTP {res.status_code}: {res.text}"}
        except Exception as e:
            return {"status": "offline", "message": str(e), "url": target}

    @staticmethod
    def _call_colab_predict(
        colab_url: str,
        file_path: str,
        title: str = "",
        caption: str = "",
        extracted_ocr: str = "",
        audio_transcript: str = ""
    ) -> Optional[Dict[str, Any]]:
        target = colab_url.strip().rstrip("/")
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"
        headers = {"ngrok-skip-browser-warning": "69420", "User-Agent": "SafeAd-Backend/1.0"}

        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, mime_type)}
            data = {
                "title": title or "",
                "caption": caption or "",
                "extracted_ocr": extracted_ocr or "",
                "audio_transcript": audio_transcript or ""
            }
            # Try /predict_qwen first (safead qwen server) then legacy /predict
            for endpoint in ["/predict_qwen", "/predict"]:
                try:
                    resp = requests.post(
                        f"{target}{endpoint}",
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=120
                    )
                    if resp.status_code == 200:
                        return resp.json()
                except Exception as e:
                    print(f"[AIClientService] Endpoint {target}{endpoint} attempt error: {e}")
                    continue
        return None

    @staticmethod
    def _run_local_pipeline(file_path: str, title: str = "", caption: str = "", pipeline_mode: str = "learned_rf") -> dict:
        try:
            try:
                from ai.pipeline import run_safead_inference
            except (ImportError, ModuleNotFoundError):
                import sys
                jb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "joseph_safead_core", "backend2jb"))
                if jb_dir not in sys.path:
                    sys.path.insert(0, jb_dir)
                try:
                    from ai.pipeline import run_safead_inference
                except (ImportError, ModuleNotFoundError):
                    from backend2jb.ai.pipeline import run_safead_inference
            return run_safead_inference(file_path, title, caption, pipeline_mode=pipeline_mode)
        except Exception as e:
            print(f"[AIClientService ERROR] Local AI Pipeline execution error: {e}")
            return {
                "classification": "UNSAFE_FOR_ALL",
                "risk_score": 100.0,
                "confidence": 1.0,
                "risk_score_available": True,
                "risk_category": "error_fallback",
                "explanation": f"AI Processing failure: {e}",
                "age_restriction": None,
                "action": "REJECT",
                "publication_action": "REJECT",
                "publishable": False,
                "violations": ["Processing Error"]
            }

    @classmethod
    def process_advertisement(
        cls,
        file_path: str,
        title: str = "",
        caption: str = "",
        pipeline_mode: Optional[str] = "learned_rf",
        colab_url: Optional[str] = None
    ) -> dict:
        """
        Executes AI inference. Supports:
        - "qwen3_vl": Direct Qwen3-VL VLM cloud inference via Google Colab.
        - "strategy_d": Hierarchical Safety Fusion combining local Learned RF and cloud Qwen3-VL VLM.
        - "learned_rf", "learned_rf_hitl", "candidate_b", "production": Local feature-based models.
        Automatically falls back to local Learned Random Forest if Colab is offline.
        """
        active_mode = (pipeline_mode or "learned_rf").lower()
        effective_colab_url = (colab_url or settings.COLAB_API_URL or "").strip()

        # =========================================================================
        # 1. Direct Qwen3-VL Inference via Google Colab
        # =========================================================================
        if active_mode == "qwen3_vl":
            if effective_colab_url:
                check = cls.test_colab_connection(effective_colab_url)
                if check.get("status") == "online":
                    qwen_res = cls._call_colab_predict(effective_colab_url, file_path, title, caption)
                    if qwen_res:
                        pred_class = qwen_res.get("classification") or qwen_res.get("predicted_class", "SAFE_FOR_ALL")
                        is_unsafe = pred_class == "UNSAFE_FOR_ALL"
                        is_hitl = pred_class == "REQUIRES_HUMAN_REVIEW"
                        action = "REJECT" if is_unsafe else ("HUMAN_REVIEW" if is_hitl else ("AGE_RESTRICT" if ("18" in pred_class or "14" in pred_class) else "APPROVE"))
                        publishable = not (is_unsafe or is_hitl)
                        risk_score = float(qwen_res.get("risk_score", 15.0 if publishable else 95.0))
                        confidence = float(qwen_res.get("confidence", 0.90))
                        reasoning = qwen_res.get("reasoning", qwen_res.get("explanation", "Completed safety evaluation via Qwen3-VL."))

                        return {
                            "classification": pred_class,
                            "display_label": pred_class.replace("_", " ").title(),
                            "publication_action": action,
                            "action": action,
                            "publishable": publishable,
                            "risk_score": risk_score,
                            "risk_score_available": True,
                            "confidence": confidence,
                            "risk_category": "high_risk" if is_unsafe else ("adult_content" if "18" in pred_class else "general_audience"),
                            "explanation": f"**[Qwen3-VL A100 GPU Evaluation]**:\n\n{reasoning}",
                            "reasoning": reasoning,
                            "vlm_reasoning": reasoning,
                            "violations": qwen_res.get("violations", []),
                            "pipeline_mode": "qwen3_vl",
                            "policy_stage": "Qwen3-VL-8B Direct Cloud VLM Inference",
                            "model_version": qwen_res.get("model_version", "Qwen3-VL-8B-Instruct (Google Colab A100)"),
                            "total_processing_time_seconds": qwen_res.get("latency_seconds", 0.0),
                            "confidence_scores": qwen_res.get("confidence_scores", {}),
                            "colab_connected": True
                        }

            # Colab unavailable -> graceful fallback
            print(f"[AIClientService WARNING] Qwen3-VL Colab endpoint unreachable at '{effective_colab_url}'. Falling back to local Learned RF.")
            local_fallback = cls._run_local_pipeline(file_path, title, caption, pipeline_mode="learned_rf")
            local_fallback["pipeline_mode"] = "learned_rf"
            local_fallback["colab_fallback"] = True
            local_fallback["colab_warning"] = f"⚠️ Google Colab GPU endpoint was offline or not configured ('{effective_colab_url}'). Automatically fell back to local Learned Random Forest."
            local_fallback["explanation"] = f"⚠️ **Colab Server Offline**: Connection to `{effective_colab_url or 'unspecified'}` failed. Reverted to local Learned Random Forest.\n\n" + local_fallback.get("explanation", "")
            return local_fallback

        # =========================================================================
        # 2. Strategy D: Hierarchical Safety Fusion (Qwen3-VL + Learned RF)
        # =========================================================================
        if active_mode == "strategy_d":
            # First, execute local detector pipeline to extract 33-dim features, OCR, audio, and RF predictions
            local_res = cls._run_local_pipeline(file_path, title, caption, pipeline_mode="learned_rf")
            extracted_ocr = local_res.get("extracted_ocr", "")
            audio_transcript = local_res.get("audio_transcript", "")

            # If Colab is configured and online, query Qwen3-VL
            qwen_res = None
            if effective_colab_url:
                check = cls.test_colab_connection(effective_colab_url)
                if check.get("status") == "online":
                    qwen_res = cls._call_colab_predict(
                        effective_colab_url,
                        file_path,
                        title,
                        caption,
                        extracted_ocr=extracted_ocr,
                        audio_transcript=audio_transcript
                    )

            if qwen_res:
                qwen_pred = qwen_res.get("classification") or qwen_res.get("predicted_class", "SAFE_FOR_ALL")
                qwen_reasoning = qwen_res.get("reasoning", "")
                qwen_violations = [str(v).lower() for v in qwen_res.get("violations", [])]
                qwen_conf_scores = qwen_res.get("confidence_scores", {})

                rf_pred = local_res.get("classification", "SAFE_FOR_ALL")
                rf_probs = local_res.get("probabilities", {})
                p_ufa = rf_probs.get("UNSAFE_FOR_ALL", 0.0)
                p_s18p = rf_probs.get("SAFE_18_PLUS", 0.0)

                # Identify semantic harms
                is_violent_vlm = any(
                    kw in str(qwen_reasoning).lower() or any(kw in v for v in qwen_violations)
                    for kw in ["violence", "weapon", "combat", "assault", "blood", "knife", "gun", "brawl", "gore"]
                )
                is_scam_vlm = any(
                    kw in str(qwen_reasoning).lower() or any(kw in v for v in qwen_violations)
                    for kw in ["scam", "fraud", "paisa double", "guaranteed return", "phishing", "ponzi", "cryptocurrency giveaway"]
                )
                is_adult_topic_vlm = any(
                    kw in str(qwen_reasoning).lower() or any(kw in v for v in qwen_violations)
                    for kw in ["alcohol", "beer", "wine", "liquor", "casino", "gambling", "dating", "betting", "roulette"]
                )

                # -------------------------------------------------------------
                # Strategy D Predeclared Arbitration Hierarchy:
                # -------------------------------------------------------------
                # Rule 1: Non-Negotiable Safety Veto (Physical violence, combat, weapons, or financial fraud)
                if qwen_pred == "UNSAFE_FOR_ALL" and (is_violent_vlm or is_scam_vlm):
                    fused_class = "UNSAFE_FOR_ALL"
                    rule_tag = "Rule 1: Non-Negotiable Safety Veto (Qwen3-VL VLM identified prohibited violence / weapons / financial fraud)"
                    action = "REJECT"
                    publishable = False
                    risk_score = 98.0
                    confidence = max(0.95, qwen_conf_scores.get("UNSAFE_FOR_ALL", 0.95))
                elif p_ufa >= 0.40:
                    fused_class = "UNSAFE_FOR_ALL"
                    rule_tag = "Rule 1: Random Forest Prohibited Safety Veto (RF P(UNSAFE_FOR_ALL) >= 0.40)"
                    action = "REJECT"
                    publishable = False
                    risk_score = 92.0
                    confidence = p_ufa

                # Rule 2: Commercial Age-Gating Calibration (Rescue lawful commercial adult goods from VLM over-policing)
                elif qwen_pred == "UNSAFE_FOR_ALL" and is_adult_topic_vlm and not (is_violent_vlm or is_scam_vlm) and (rf_pred == "SAFE_18_PLUS" or p_s18p >= 0.35):
                    fused_class = "SAFE_18_PLUS"
                    rule_tag = "Rule 2: Commercial Age-Gating Calibration (Rescued lawful adult commercial goods from VLM over-policing via RF domain detectors)"
                    action = "AGE_RESTRICT"
                    publishable = True
                    risk_score = 55.0
                    confidence = 0.88

                # Rule 3: Consensus Agreement
                elif qwen_pred == rf_pred:
                    fused_class = qwen_pred
                    rule_tag = f"Rule 3: Dual-Model Consensus Agreement ({qwen_pred})"
                    action = "REJECT" if fused_class == "UNSAFE_FOR_ALL" else ("AGE_RESTRICT" if ("18" in fused_class or "14" in fused_class) else "APPROVE")
                    publishable = fused_class != "UNSAFE_FOR_ALL"
                    risk_score = local_res.get("risk_score", 15.0)
                    confidence = round(0.5 * (float(local_res.get("confidence", 0.8)) + float(qwen_res.get("confidence", 0.8))), 2)

                # Rule 4: Educational / Adolescent Distinction
                elif qwen_pred == "SAFE_14_PLUS" and rf_pred == "SAFE_FOR_ALL":
                    fused_class = "SAFE_14_PLUS"
                    rule_tag = "Rule 4: Adolescent Context Distinction (Qwen3-VL multimodal text-vision comprehension isolated 14+ adolescent restriction)"
                    action = "AGE_RESTRICT"
                    publishable = True
                    risk_score = 30.0
                    confidence = 0.85

                # Rule 5: Confirmed Adult Domain Features
                elif rf_pred == "SAFE_18_PLUS" and p_s18p >= 0.60:
                    fused_class = "SAFE_18_PLUS"
                    rule_tag = "Rule 5: Random Forest Confirmed Adult Domain Features"
                    action = "AGE_RESTRICT"
                    publishable = True
                    risk_score = 52.0
                    confidence = p_s18p

                # Rule 6: Qwen VLM Semantic Dominance
                else:
                    fused_class = qwen_pred
                    rule_tag = f"Rule 6: Qwen3-VL Semantic Dominance ({qwen_pred})"
                    action = "REJECT" if fused_class == "UNSAFE_FOR_ALL" else ("AGE_RESTRICT" if ("18" in fused_class or "14" in fused_class) else "APPROVE")
                    publishable = fused_class != "UNSAFE_FOR_ALL"
                    risk_score = float(qwen_res.get("risk_score", 20.0))
                    confidence = float(qwen_res.get("confidence", 0.85))

                composite_explanation = (
                    f"### 🛡️ Strategy D: Hierarchical Safety Fusion\n"
                    f"**Decision Arbitration**: `{rule_tag}`\n\n"
                    f"**Qwen3-VL A100 VLM Semantic Reasoning**:\n{qwen_reasoning}\n\n"
                    f"**Random Forest Ensemble**: Predicted `{rf_pred}` (Probabilities: `{rf_probs}`)\n\n"
                    f"**Final Status**: `{fused_class}` — `{action}`"
                )

                return {
                    "classification": fused_class,
                    "display_label": fused_class.replace("_", " ").title(),
                    "publication_action": action,
                    "action": action,
                    "publishable": publishable,
                    "risk_score": risk_score,
                    "risk_score_available": True,
                    "confidence": confidence,
                    "policy_stage": "Strategy D Hierarchical Safety Fusion",
                    "fusion_rule_applied": rule_tag,
                    "explanation": composite_explanation,
                    "reasoning": qwen_reasoning,
                    "vlm_reasoning": qwen_reasoning,
                    "qwen_prediction": qwen_pred,
                    "rf_prediction": rf_pred,
                    "rf_probabilities": rf_probs,
                    "violations": list(set(local_res.get("violations", []) + qwen_res.get("violations", []))),
                    "pipeline_mode": "strategy_d",
                    "model_version": "Strategy D (Qwen3-VL + Learned RF Hierarchical Fusion)",
                    "extracted_ocr": extracted_ocr,
                    "audio_transcript": audio_transcript,
                    "evidence": local_res.get("evidence", {}),
                    "assessment_matrix": local_res.get("assessment_matrix", {}),
                    "total_processing_time_seconds": round(
                        float(local_res.get("total_processing_time_seconds", 0.0)) + float(qwen_res.get("latency_seconds", 0.0)),
                        3
                    ),
                    "colab_connected": True
                }

            # Colab was offline -> return local Learned RF with alert note
            local_res["pipeline_mode"] = "learned_rf"
            local_res["colab_fallback"] = True
            local_res["colab_warning"] = f"⚠️ Google Colab GPU endpoint was offline or not reachable ('{effective_colab_url}'). Executed local Learned Random Forest fallback."
            local_res["explanation"] = f"⚠️ **Colab GPU Offline**: Connection to `{effective_colab_url or 'unspecified'}` failed. Reverted to local Learned Random Forest.\n\n" + local_res.get("explanation", "")
            return local_res

        # =========================================================================
        # 3. Standard Local Pipeline Modes (learned_rf, learned_rf_hitl, candidate_b, production)
        # =========================================================================
        return cls._run_local_pipeline(file_path, title, caption, pipeline_mode=active_mode)
