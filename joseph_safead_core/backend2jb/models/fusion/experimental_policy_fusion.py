"""
SafeAd AI (SAFE-VISION) — Experimental Policy-First Multimodal Fusion Engine.

Separate experimental module created for Phase 4A Task 3.
Production implementation in safead_fusion.py remains completely UNTOUCHED.

Key Architectural Principles:
1. Policy-First Gate: Evaluates prohibited content rules first before age gating.
2. Eliminates Compensatory Dilution: Prohibited violations immediately reject regardless of safe modalities.
3. Detector-Specific Calibrated Thresholds: Thresholds tuned per modality rather than assuming universal 0.50.
4. Reachable Human-In-The-Loop (HITL): Explicit routing for detector errors, borderline signals, or missing evidence.
5. Continuous, Monotonic Risk Scoring: Eliminates artificial clamping caps (39.9, 65.0).
"""

from typing import Dict, Any, List, Optional
import numpy as np


class ExperimentalPolicyFusion:
    """
    Experimental Policy-First Fusion Engine for SafeAd AI.
    Decouples Prohibited Policy Enforcement from Age-Appropriate Content Gating.
    """

    def __init__(
        self,
        # Detector-specific thresholds calibrated on Development Folds
        prohibited_nsfw_thresh: float = 0.75,
        prohibited_violence_thresh: float = 0.65,
        prohibited_scam_thresh: float = 0.45,
        adult_18p_nsfw_thresh: float = 0.35,
        adult_18p_text_thresh: float = 0.40,
        teen_14p_nsfw_thresh: float = 0.12,
        teen_14p_violence_thresh: float = 0.18,
        hitl_confidence_thresh: float = 0.60,
        enable_ambiguity_routing: bool = True
    ):
        self.prohibited_nsfw_thresh = prohibited_nsfw_thresh
        self.prohibited_violence_thresh = prohibited_violence_thresh
        self.prohibited_scam_thresh = prohibited_scam_thresh
        self.adult_18p_nsfw_thresh = adult_18p_nsfw_thresh
        self.adult_18p_text_thresh = adult_18p_text_thresh
        self.teen_14p_nsfw_thresh = teen_14p_nsfw_thresh
        self.teen_14p_violence_thresh = teen_14p_violence_thresh
        self.hitl_confidence_thresh = hitl_confidence_thresh
        self.enable_ambiguity_routing = enable_ambiguity_routing

    def combine_assessment(
        self,
        assessment_matrix: Dict[str, Any],
        improved_text_output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes Policy-First 4-Stage Decision Flow:
        Stage 1: Prohibited Content Policy Gate (Veto)
        Stage 2: Ambiguity & Processing Failure Gate (Reachable Human Review)
        Stage 3: Age-Appropriate Suitability Gate (18+ vs 14+ vs Safe for All)
        Stage 4: Continuous Monotonic Risk Score Calculation
        """
        vis = assessment_matrix.get("visual", {})
        vid = assessment_matrix.get("video", {})
        ocr = assessment_matrix.get("ocr", {})
        aud = assessment_matrix.get("audio", {})
        txt = assessment_matrix.get("text_safety", {})
        adr = assessment_matrix.get("advertisement_risks", {})

        # 1. Extract signals
        nsfw_score = max(vis.get("adult", 0.0), vid.get("adult", 0.0))
        violence_score = max(vis.get("violence", 0.0), vid.get("violence", 0.0))
        child_safety = max(vis.get("child_safety", 0.0), vid.get("child_safety", 0.0), txt.get("categories", {}).get("child_safety", 0.0))
        
        # Text scam / deceptive signals (incorporating improved text output if provided)
        base_scam = max(adr.get("scam", 0.0), adr.get("deceptive_marketing", 0.0))
        if improved_text_output:
            scam_score = max(base_scam, improved_text_output.get("prohibited_risk", 0.0))
            is_improved_text_flagged = improved_text_output.get("is_flagged_prohibited", False)
        else:
            scam_score = base_scam
            is_improved_text_flagged = False

        alcohol_score = max(txt.get("categories", {}).get("alcohol", 0.0), ocr.get("adult", 0.0))
        ocr_status = ocr.get("status", "success")
        is_ocr_error = ocr_status.startswith("error")

        policy_reasons = []
        action = "APPROVE"
        classification = "SAFE_FOR_ALL"
        policy_stage = "INITIALIZED"

        # =====================================================================
        # STAGE 1: PROHIBITED CONTENT POLICY GATE (ZERO COMPENSATORY DILUTION)
        # =====================================================================
        prohibited_detected = False

        if child_safety > 0.05:
            prohibited_detected = True
            policy_reasons.append("Zero-tolerance child safety violation detected.")

        if nsfw_score >= self.prohibited_nsfw_thresh:
            prohibited_detected = True
            policy_reasons.append(f"Severe prohibited explicit/adult content detected (score: {nsfw_score:.2f}).")

        if violence_score >= self.prohibited_violence_thresh:
            prohibited_detected = True
            policy_reasons.append(f"Severe prohibited violence or graphic physical combat detected (score: {violence_score:.2f}).")

        if scam_score >= self.prohibited_scam_thresh or is_improved_text_flagged:
            prohibited_detected = True
            policy_reasons.append(f"Prohibited deceptive marketing, financial fraud, or illegal offer detected (score: {scam_score:.2f}).")

        if prohibited_detected:
            policy_stage = "PROHIBITED_POLICY_VETO"
            classification = "UNSAFE_FOR_ALL"
            action = "REJECT"
            # Monotonic Prohibited Score band [75.0, 100.0]
            max_viol = max(nsfw_score, violence_score, scam_score, 0.50)
            risk_score = round(75.0 + 25.0 * min(1.0, (max_viol - 0.45) / 0.55), 2)
            confidence = 0.95
            return self._build_result(classification, action, risk_score, confidence, policy_stage, policy_reasons, True)

        # =====================================================================
        # STAGE 2: AMBIGUITY & DETECTOR FAILURE GATE (REACHABLE HUMAN REVIEW)
        # =====================================================================
        requires_human_review = False

        # Route detector failures (e.g. OCR crashing or missing keyframes)
        if is_ocr_error:
            requires_human_review = True
            policy_reasons.append(f"OCR detector failure requires manual review: {ocr_status}")

        # Route borderline ambiguous signals (only if ambiguity routing is enabled)
        if self.enable_ambiguity_routing:
            is_borderline_nsfw = (0.28 <= nsfw_score < self.adult_18p_nsfw_thresh)
            is_borderline_scam = (0.30 <= scam_score < self.prohibited_scam_thresh)
            is_borderline_viol = (0.45 <= violence_score < self.prohibited_violence_thresh)

            if (is_borderline_nsfw or is_borderline_scam or is_borderline_viol):
                requires_human_review = True
                policy_reasons.append("Borderline risk signals detected across modalities; routed to human safety officer.")

        if requires_human_review:
            policy_stage = "HUMAN_IN_THE_LOOP_ROUTING"
            classification = "REQUIRES_HUMAN_REVIEW"
            action = "ROUTE_TO_HUMAN_REVIEW"
            risk_score = 50.0
            confidence = 0.55
            return self._build_result(classification, action, risk_score, confidence, policy_stage, policy_reasons, False)

        # =====================================================================
        # STAGE 3: AGE-APPROPRIATE SUITABILITY GATE (18+ vs 14+ vs ALL)
        # =====================================================================
        policy_stage = "AGE_GATING_POLICY"

        # Check 18+ Adult Content / Regulated Products
        is_18_plus = (
            nsfw_score >= self.adult_18p_nsfw_thresh or
            alcohol_score >= self.adult_18p_text_thresh or
            "Alcohol/Tobacco" in txt.get("categories", {}).get("detected_categories", [])
        )

        if is_18_plus:
            classification = "SAFE_18_PLUS"
            action = "AGE_RESTRICT"
            policy_reasons.append("Contains permissible adult content, alcohol, or regulated adult products.")
            # Monotonic 18+ Score band [50.0, 74.9]
            severity = max(nsfw_score, alcohol_score)
            risk_score = round(50.0 + 24.9 * min(1.0, severity), 2)
            confidence = 0.92
            return self._build_result(classification, action, risk_score, confidence, policy_stage, policy_reasons, False)

        # Check 14+ Teen Content (Suggestive Themes, Action Violence)
        is_14_plus = (
            nsfw_score >= self.teen_14p_nsfw_thresh or
            violence_score >= self.teen_14p_violence_thresh or
            "Violence" in txt.get("categories", {}).get("detected_categories", [])
        )

        if is_14_plus:
            classification = "SAFE_14_PLUS"
            action = "AGE_RESTRICT"
            policy_reasons.append("Contains teen-oriented action themes, mild violence, or mature recreational creative.")
            # Monotonic 14+ Score band [25.0, 49.9]
            severity = max(nsfw_score / self.adult_18p_nsfw_thresh, violence_score / self.prohibited_violence_thresh)
            risk_score = round(25.0 + 24.9 * min(1.0, severity), 2)
            confidence = 0.90
            return self._build_result(classification, action, risk_score, confidence, policy_stage, policy_reasons, False)

        # Safe for All Audiences
        classification = "SAFE_FOR_ALL"
        action = "APPROVE"
        policy_reasons.append("Advertisement cleared all safety checks and is suitable for all audiences.")
        # Monotonic General Score band [0.0, 24.9]
        benign_residual = max(nsfw_score, violence_score, scam_score)
        risk_score = round(min(24.9, benign_residual * 40.0), 2)
        confidence = 0.94
        return self._build_result(classification, action, risk_score, confidence, policy_stage, policy_reasons, False)

    def _build_result(
        self,
        classification: str,
        action: str,
        risk_score: float,
        confidence: float,
        policy_stage: str,
        policy_reasons: List[str],
        prohibited_detected: bool
    ) -> Dict[str, Any]:
        return {
            "classification": classification,
            "publication_action": action,
            "risk_score": risk_score,
            "confidence": confidence,
            "policy_stage": policy_stage,
            "policy_reasons": policy_reasons,
            "prohibited_content_detected": prohibited_detected,
            "requires_human_review": bool(action == "ROUTE_TO_HUMAN_REVIEW")
        }
