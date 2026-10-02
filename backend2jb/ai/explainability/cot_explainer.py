def generate_cot_explanation(
    classification: str,
    risk_score: float,
    risk_score_available: bool,
    violations: list,
    ocr_text: str,
    detected_objects: list,
    similar_case: dict,
    speech_transcript: str = ""
) -> str:
    """
    Generates evidence-grounded Chain-of-Thought (CoT) audit explanations.
    Strictly uses actual visual, OCR, audio speech transcript, and policy evidence extracted during inference.
    """
    cot_steps = []
    
    # Step 1: Decision Overview
    if risk_score_available and risk_score is not None:
        cot_steps.append(f"1. Unified multimodal risk assessment evaluated at {risk_score:.1f}%.")
    else:
        cot_steps.append("1. Multimodal risk assessment evaluated without a numerical probability score.")
        
    # Step 2: Evidence Findings (Visual, OCR, Audio Transcript, Policy Violations)
    evidence_items = []
    if violations:
        evidence_items.append(f"Policy flags triggered: {', '.join(violations)}")
    if ocr_text and ocr_text not in ["No text detected in creative overlay.", "No text detected."]:
        evidence_items.append(f"OCR embedded text detected: '{ocr_text[:60]}...'")
    if speech_transcript and speech_transcript not in ["No spoken speech detected.", "N/A", ""]:
        evidence_items.append(f"Audio transcript detected: '{speech_transcript[:60]}...'")
    if detected_objects:
        evidence_items.append(f"Visual objects identified: {', '.join(detected_objects[:5])}")
        
    if evidence_items:
        cot_steps.append(f"2. Extracted Evidence: {'; '.join(evidence_items)}.")
    else:
        cot_steps.append("2. Extracted Evidence: No explicit policy flags or prohibited objects detected.")

    # Step 3: FAISS Vector Match
    if similar_case and isinstance(similar_case, dict) and "title" in similar_case:
        cot_steps.append(f"3. FAISS Vector Case Match: Identified historical exemplar '{similar_case['title']}' (Distance: {similar_case.get('distance', 0.0):.3f}, Policy: {similar_case.get('policy', 'N/A')}).")
    elif similar_case and isinstance(similar_case, str) and "No similar" not in similar_case:
        cot_steps.append(f"3. FAISS Vector Case Match: {similar_case}")
        
    # Step 4: Final Recommendation
    cls_upper = str(classification).upper()
    if cls_upper in ["UNSAFE_FOR_ALL", "FLAGGED_UNSAFE", "REJECT"]:
        cot_steps.append("4. Final Action: REJECT. High-risk indicators exceed platform safety thresholds.")
    elif cls_upper in ["AGE_18_PLUS", "RESTRICT_18"]:
        cot_steps.append("4. Final Action: RESTRICT (18+). Content suitable only for verified adult users.")
    elif cls_upper in ["AGE_14_PLUS", "RESTRICT_14"]:
        cot_steps.append("4. Final Action: RESTRICT (14+). Content suitable for users aged 14 and older.")
    else:
        cot_steps.append("4. Final Action: APPROVE. Safe for general audience distribution.")
        
    return " | ".join(cot_steps)
