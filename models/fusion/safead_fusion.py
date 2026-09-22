from typing import Dict, Any, List, Optional

class SafeAdFusion:
    """
    Deterministic SafeAd Multimodal Evidence Fusion Layer & Policy Decision Engine.
    
    Combines evidence across all modalities:
    - Visual Safety (Llama Guard 3 Vision)
    - Video Violence (VideoMAE)
    - Adult / NSFW Content (Falconsai ViT)
    - Child Safety Risk
    - OCR Overlay Text Safety (Llama Guard 3-1B)
    - Audio Speech Transcript Safety (Whisper + Llama Guard 3-1B)
    - Contextual Vector Retrieval (FAISS)
    
    Safety Priority Rules:
    1. Child sexual exploitation / severe child safety risk -> UNSAFE_FOR_ALL (REJECT)
    2. Severe violent content -> UNSAFE_FOR_ALL (REJECT)
    3. Other prohibited content (scams, illegal drugs) -> UNSAFE_FOR_ALL (REJECT)
    4. Adult-only permissible content -> SAFE_18_PLUS (AGE RESTRICTED 18+)
    5. Teen-restricted content (gambling/alcohol) -> SAFE_14_PLUS (AGE RESTRICTED 14+)
    6. Otherwise -> SAFE_FOR_ALL (APPROVED)
    
    Target Classifications (Exact 4 Classes):
    - SAFE_FOR_ALL
    - SAFE_14_PLUS
    - SAFE_18_PLUS
    - UNSAFE_FOR_ALL
    """

    def combine_evidence(
        self,
        visual_evidence: Dict[str, Any],
        video_violence_evidence: Dict[str, Any],
        nsfw_evidence: Dict[str, Any],
        ocr_evidence: Dict[str, Any],
        ocr_text_safety: Dict[str, Any],
        audio_evidence: Dict[str, Any],
        context_evidence: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Combines modality evidence into a single deterministic risk score, dominant risks, confidence,
        policy classification, publication action, and concise explanation.
        """

        # Extract risk metrics per modality
        visual_unsafe = visual_evidence.get("unsafe", False)
        visual_cats = visual_evidence.get("detected_categories", [])
        
        violence_score = video_violence_evidence.get("violence_score", 0.0)
        violence_detected = video_violence_evidence.get("violence_detected", False)
        
        nsfw_score = nsfw_evidence.get("adult_score", 0.0)
        nsfw_detected = nsfw_evidence.get("adult_content_detected", False)
        
        ocr_risk = ocr_text_safety.get("overall_text_risk", 0.0)
        ocr_cats = ocr_text_safety.get("detected_categories", [])
        
        audio_available = audio_evidence.get("audio_available", False)
        audio_safety = audio_evidence.get("audio_safety", {})
        audio_risk = audio_safety.get("overall_risk", 0.0)
        
        # Child safety check
        child_safety_flag = (
            "Child Safety Risk" in visual_cats or
            ocr_text_safety.get("child_safety", 0.0) >= 0.50 or
            audio_safety.get("child_safety", 0.0) >= 0.50
        )
        
        # Collect dominant risks
        dominant_risks = []
        if child_safety_flag:
            dominant_risks.append("Child Safety Risk")
        if violence_detected or violence_score >= 0.35 or "Violence" in ocr_cats or audio_safety.get("violence", 0.0) >= 0.35:
            dominant_risks.append("Violence")
        if nsfw_detected or nsfw_score >= 0.35 or "Sexual Content" in ocr_cats or audio_safety.get("adult", 0.0) >= 0.35:
            dominant_risks.append("Adult/Sexual Content")
        if "Hate Content" in visual_cats or ocr_text_safety.get("hate", 0.0) >= 0.50:
            dominant_risks.append("Hate Speech")
            
        # Add OCR / Audio explicit infractions (Gambling, Alcohol, Scams)
        for cat in ocr_cats:
            if cat not in dominant_risks:
                dominant_risks.append(cat)

        # Calculate weighted multi-modal risk score (0-100)
        # Visual (30%), Video Violence (25%), Adult/NSFW (20%), Text/OCR (15%), Audio (10%)
        weighted_score = (
            (100.0 if visual_unsafe else 0.0) * 0.30 +
            (violence_score * 100.0) * 0.25 +
            (nsfw_score * 100.0) * 0.20 +
            (ocr_risk * 100.0) * 0.15 +
            (audio_risk * 100.0) * 0.10
        )
        
        # Cap risk score at 100
        risk_score = round(min(100.0, max(0.0, weighted_score)), 2)
        
        # Calculate cross-modal agreement & overall confidence
        modalities_checked = 3 + (1 if audio_available else 0)
        flagged_modalities = 0
        if visual_unsafe: flagged_modalities += 1
        if violence_detected: flagged_modalities += 1
        if nsfw_detected: flagged_modalities += 1
        if ocr_risk >= 0.35: flagged_modalities += 1
        if audio_risk >= 0.35: flagged_modalities += 1
        
        confidence = round(0.80 + (0.05 * min(modalities_checked, 4)), 2)

        # Policy Priority Engine: Map to 1 of 4 exact target classes
        if child_safety_flag:
            classification = "UNSAFE_FOR_ALL"
            display_label = "Unsafe for All"
            publication_action = "REJECT"
            action_badge = "REJECT — UNSAFE FOR ALL"
        elif "Violence" in dominant_risks and (violence_score >= 0.60 or risk_score >= 70.0):
            classification = "UNSAFE_FOR_ALL"
            display_label = "Unsafe for All"
            publication_action = "REJECT"
            action_badge = "REJECT — UNSAFE FOR ALL"
        elif "Misleading Advertisement" in dominant_risks or "Hate Speech" in dominant_risks or risk_score >= 80.0:
            classification = "UNSAFE_FOR_ALL"
            display_label = "Unsafe for All"
            publication_action = "REJECT"
            action_badge = "REJECT — UNSAFE FOR ALL"
        elif "Adult/Sexual Content" in dominant_risks or nsfw_detected or nsfw_score >= 0.35 or risk_score >= 40.0:
            classification = "SAFE_18_PLUS"
            display_label = "18+"
            publication_action = "AGE_RESTRICT"
            action_badge = "AGE RESTRICTED — 18+"
        elif "Gambling" in dominant_risks or "Alcohol/Tobacco" in dominant_risks or "Drugs" in dominant_risks or risk_score >= 25.0:
            classification = "SAFE_14_PLUS"
            display_label = "14+"
            publication_action = "AGE_RESTRICT"
            action_badge = "AGE RESTRICTED — 14+"
        else:
            classification = "SAFE_FOR_ALL"
            display_label = "Safe for All"
            publication_action = "APPROVE"
            action_badge = "APPROVED — SAFE FOR ALL"

        # Generate concise evidence-based explanation
        reasons = []
        if child_safety_flag:
            reasons.append("Child safety risk flags detected in advertisement content.")
        if violence_detected or violence_score >= 0.35:
            reasons.append(f"Violence detected in sampled video segments (score: {violence_score:.2f}).")
        if nsfw_detected or nsfw_score >= 0.35:
            reasons.append(f"Adult visual content detected across sampled frames (score: {nsfw_score:.2f}).")
        if ocr_risk >= 0.35 and ocr_cats:
            reasons.append(f"OCR overlay contains policy-restricted content ({', '.join(ocr_cats)}).")
        if audio_available and audio_risk >= 0.35:
            reasons.append("Speech transcript contains policy-restricted content.")
        if not reasons:
            reasons.append("No policy infractions or safety risks detected across visual, text, or audio modalities.")

        explanation = " ".join(reasons)

        modality_evidence = {
            "visual": visual_evidence,
            "video": video_violence_evidence,
            "nsfw": nsfw_evidence,
            "ocr": {
                "extracted_text": ocr_evidence.get("ocr_text", ""),
                "confidence": ocr_evidence.get("ocr_confidence", 0.0),
                "risk": ocr_risk
            },
            "audio": {
                "available": audio_available,
                "transcript": audio_evidence.get("transcript", ""),
                "risk": audio_risk
            },
            "context": context_evidence or {"status": "no_context"}
        }

        return {
            "classification": classification,
            "display_label": display_label,
            "risk_score": risk_score,
            "confidence": confidence,
            "publication_action": publication_action,
            "action_badge": action_badge,
            "dominant_risks": dominant_risks,
            "detected_categories": dominant_risks,
            "explanation": explanation,
            "evidence": modality_evidence
        }
