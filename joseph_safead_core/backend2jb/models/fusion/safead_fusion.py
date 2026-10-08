from typing import Dict, Any, List, Optional
from models.fusion.safead_assessment import SafeAdAssessment

"""
SafeAd AI Multimodal Safety Policy & Evidence Fusion Engine
Executes an explicit TWO-STAGE policy architecture:

    STAGE 1: PROHIBITED CONTENT POLICY ENGINE (ProhibitedContentPolicyEngine)
        - Inspects multimodal evidence from SafeAdAssessment
        - Evaluates severe prohibited risks:
            * Child exploitation / severe child safety risk
            * Extreme graphic / prohibited physical violence
            * Hate speech / discriminatory content
            * Scam / illegal / prohibited commercial offers ("paisa double", "guaranteed cash")
            * Severe deceptive advertisement claims
        - Distinguishes DETECTED CONTENT from PROHIBITED CONTENT.
        - Permissible adult content (e.g. 18+ swimwear, adult apparel, mature dating copy) is PERMITTED here for Stage 2.
        - Decision: PROHIBITED -> UNSAFE_FOR_ALL (REJECT) OR PERMITTED -> STAGE 2.

    STAGE 2: AGE POLICY ENGINE (AgePolicyEngine)
        - Executes ONLY IF Stage 1 determines content is PERMITTED (Stage 1 has priority!).
        - Evaluates age appropriateness:
            * SAFE_FOR_ALL (General low-risk content) -> APPROVE
            * SAFE_14_PLUS (Moderate/suggestive content) -> AGE_RESTRICT (14+)
            * SAFE_18_PLUS (Permissible adult content/attire/mature copy) -> AGE_RESTRICT (18+)

    HUMAN-IN-THE-LOOP (HITL):
        - Triggered when model confidence < 0.50 (CONFIDENCE_THRESHOLD).
        - Direct prohibited decisions (high-confidence prohibited threat) always take priority over HITL.
"""

class ProhibitedPolicyDecision:
    def __init__(self, is_prohibited: bool, prohibited_risks: List[str], confidence: float, reasons: List[str]):
        self.is_prohibited = is_prohibited
        self.prohibited_risks = prohibited_risks
        self.confidence = confidence
        self.reasons = reasons


class ProhibitedContentPolicyEngine:
    """
    Stage 1: Prohibited Content Policy Engine.
    Inspects multimodal evidence matrix to detect prohibited threats.
    """
    def evaluate(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> ProhibitedPolicyDecision:
        vis = data.get("visual", {})
        vid = data.get("video", {})
        ocr = data.get("ocr", {})
        aud = data.get("audio", {})
        text_safe = data.get("text_safety", {})
        ad_risks = data.get("advertisement_risks", {})

        visual_cats = vis.get("detected_categories", [])
        ocr_cats = text_safe.get("categories", {}).get("detected", []) if isinstance(text_safe.get("categories"), dict) else text_safe.get("evidence", [])

        violence_score = metrics.get("violence_score", 0.0)
        scam_score = metrics.get("scam_score", 0.0)
        deceptive_score = metrics.get("deceptive_score", 0.0)
        child_safety_flag = metrics.get("child_safety_flag", False)
        prohibited_risk = metrics.get("prohibited_risk", 0.0)

        prohibited_risks = []
        reasons = []

        # 1. Child Safety Risk (Prohibited)
        if child_safety_flag:
            prohibited_risks.append("Child Safety Risk")
            reasons.append("Child safety exploitation risk detected across visual/textual modalities")

        # 2. Extreme / Prohibited Violence (Prohibited)
        if violence_score >= 0.50:
            prohibited_risks.append("Severe Prohibited Violence")
            reasons.append(f"High-confidence kinetic violence activity detected (score: {violence_score*100:.1f}/100)")

        # 3. Scam & Illegal Offers (Prohibited)
        if scam_score >= 0.50 or ocr.get("scam", 0.0) >= 0.50 or aud.get("scam", 0.0) >= 0.50:
            prohibited_risks.append("Scam / Prohibited Financial Offer")
            reasons.append("Prohibited deceptive financial scheme or scam offer detected in copy/transcript")

        # 4. Severe Deceptive Marketing (Prohibited)
        if deceptive_score >= 0.70:
            prohibited_risks.append("Severe Deceptive Marketing")
            reasons.append("Extreme misleading or deceptive commercial claims detected")

        # 5. Hate Speech (Prohibited)
        if "Hate Speech" in ocr_cats or "Hate Content" in visual_cats:
            prohibited_risks.append("Hate Speech")
            reasons.append("Prohibited hate speech or discriminatory content detected in text overlay")

        # Overall Prohibited Decision
        is_prohibited = len(prohibited_risks) > 0 or prohibited_risk >= 50.0

        if is_prohibited and not reasons:
            reasons.append(f"Multimodal prohibited risk score ({prohibited_risk:.1f}/100) exceeded safety policy threshold")

        confidence = round(min(1.0, max(0.50, (prohibited_risk / 100.0) if is_prohibited else 0.85)), 2)

        return ProhibitedPolicyDecision(
            is_prohibited=is_prohibited,
            prohibited_risks=prohibited_risks,
            confidence=confidence,
            reasons=reasons
        )


class AgePolicyDecision:
    def __init__(self, classification: str, display_label: str, publication_action: str, action_badge: str, age_restriction: Optional[str], reasons: List[str]):
        self.classification = classification
        self.display_label = display_label
        self.publication_action = publication_action
        self.action_badge = action_badge
        self.age_restriction = age_restriction
        self.reasons = reasons


class AgePolicyEngine:
    """
    Stage 2: Age Policy Engine.
    Executes ONLY when Stage 1 determines content is PERMITTED (Stage 1 has priority!).
    Categorizes permitted content into appropriate age rating buckets:
      - SAFE_FOR_ALL (General audiences) -> APPROVE
      - SAFE_14_PLUS (Teens 14+) -> AGE_RESTRICT (14+)
      - SAFE_18_PLUS (Adults 18+ for permissible swimwear, apparel, mature dating copy) -> AGE_RESTRICT (18+)
    """
    def evaluate(self, risk_score: float, adult_content_score: float, nsfw_score: float, explicit_score: float, dominant_risks: List[str]) -> AgePolicyDecision:
        reasons = []

        # 1. Adult / 18+ Content (Permissible adult content)
        if "Adult/Sexual Content" in dominant_risks or nsfw_score >= 0.35 or explicit_score >= 0.35 or adult_content_score >= 0.35:
            classification = "SAFE_18_PLUS"
            display_label = "18+"
            publication_action = "AGE_RESTRICT"
            action_badge = "AGE RESTRICTED — 18+"
            age_restriction = "18+"
            reasons.append(f"Ad contains permissible adult/sexual themes or suggestive attire (score: {adult_content_score*100:.1f}/100)")

        # 2. Teen / 14+ Content (Mild suggestive copy or themes)
        elif risk_score >= 25.0 or adult_content_score >= 0.20:
            classification = "SAFE_14_PLUS"
            display_label = "14+"
            publication_action = "AGE_RESTRICT"
            action_badge = "AGE RESTRICTED — 14+"
            age_restriction = "14+"
            reasons.append(f"Ad contains mild adult/suggestive themes (score: {risk_score:.1f}/100)")

        # 3. Safe For All (General audiences)
        else:
            classification = "SAFE_FOR_ALL"
            display_label = "Safe for All"
            publication_action = "APPROVE"
            action_badge = "APPROVED — SAFE FOR ALL"
            age_restriction = None
            reasons.append("Ad cleared all multimodal safety evaluations and is suitable for all audiences")

        return AgePolicyDecision(
            classification=classification,
            display_label=display_label,
            publication_action=publication_action,
            action_badge=action_badge,
            age_restriction=age_restriction,
            reasons=reasons
        )


class SafeAdFusion:
    CONFIDENCE_THRESHOLD = 0.50  # HITL trigger threshold: only when very uncertain (< 50%)

    def __init__(self):
        self.prohibited_engine = ProhibitedContentPolicyEngine()
        self.age_engine = AgePolicyEngine()

    def evaluate(self, assessment: SafeAdAssessment) -> Dict[str, Any]:
        """Alias for combine_assessment."""
        return self.combine_assessment(assessment)

    def combine_assessment(
        self,
        assessment: SafeAdAssessment
    ) -> Dict[str, Any]:
        """
        Combines Central SafeAdAssessment matrix using explicit Two-Stage Policy Architecture:
          STAGE 1: Prohibited Content Check (ProhibitedContentPolicyEngine)
          STAGE 2: Age Policy Check (AgePolicyEngine)
          HITL Routing: Low confidence / ambiguous evidence -> REQUIRES_HUMAN_REVIEW
        """
        data = assessment.to_dict() if isinstance(assessment, SafeAdAssessment) else assessment

        vis = data.get("visual", {})
        vid = data.get("video", {})
        ocr = data.get("ocr", {})
        aud = data.get("audio", {})
        text_safe = data.get("text_safety", {})
        ad_risks = data.get("advertisement_risks", {})

        # Extract risk signals per modality
        visual_unsafe = vis.get("unsafe", False)
        visual_cats = vis.get("detected_categories", [])

        violence_score = max(vid.get("violence", 0.0), vis.get("violence", 0.0))
        nsfw_score = max(vid.get("adult", 0.0), vis.get("adult", 0.0))

        ocr_risk = max(ocr.get("adult", 0.0), ocr.get("violence", 0.0), ocr.get("scam", 0.0), ocr.get("deceptive", 0.0))
        ocr_cats = text_safe.get("categories", {}).get("detected", []) if isinstance(text_safe.get("categories"), dict) else text_safe.get("evidence", [])

        audio_available = aud.get("audio_available", False)
        audio_risk = max(aud.get("adult", 0.0), aud.get("violence", 0.0), aud.get("scam", 0.0))

        scam_score = ad_risks.get("scam", 0.0)
        deceptive_score = ad_risks.get("deceptive_marketing", 0.0)
        explicit_score = ad_risks.get("explicit_content", 0.0)

        # Child safety check
        child_safety_flag = (
            "Child Safety Risk" in visual_cats or
            vis.get("child_safety", 0.0) >= 0.50 or
            vid.get("child_safety", 0.0) >= 0.50 or
            ocr.get("child_safety", 0.0) >= 0.50 or
            aud.get("child_safety", 0.0) >= 0.50
        )

        # Collect dominant risk flags
        dominant_risks = []
        if child_safety_flag: dominant_risks.append("Child Safety Risk")
        if violence_score >= 0.35: dominant_risks.append("Violence")
        if nsfw_score >= 0.35 or explicit_score >= 0.50: dominant_risks.append("Adult/Sexual Content")
        if scam_score >= 0.50: dominant_risks.append("Scam Indicators")
        if deceptive_score >= 0.50: dominant_risks.append("Deceptive Marketing")
        if "Hate Speech" in ocr_cats or "Hate Content" in visual_cats: dominant_risks.append("Hate Speech")

        # Max prohibited threat risk (violence, scams, deceptive claims, hate speech, child safety)
        prohibited_risk = max(
            violence_score,
            scam_score,
            deceptive_score,
            ocr.get("scam", 0.0),
            aud.get("scam", 0.0)
        ) * 100.0

        # Adult / 18+ content score
        adult_content_score = max(nsfw_score, explicit_score, ocr.get("adult", 0.0), aud.get("adult", 0.0))

        # Weighted Risk Score (0-100) with spike-preservation
        weighted_score = (
            (100.0 if visual_unsafe else 0.0) * 0.25 +
            (violence_score * 100.0) * 0.20 +
            (nsfw_score * 100.0) * 0.20 +
            (ocr_risk * 100.0) * 0.15 +
            (audio_risk * 100.0) * 0.10 +
            (max(scam_score, deceptive_score, explicit_score) * 100.0) * 0.10
        )

        # Risk Score Calculation (0.0 - 100.0)
        if child_safety_flag or prohibited_risk >= 50.0:
            risk_score = round(min(100.0, max(weighted_score, prohibited_risk)), 2)
        elif adult_content_score >= 0.25:
            risk_score = round(min(65.0, max(weighted_score, adult_content_score * 70.0)), 2)
        else:
            risk_score = round(min(39.9, weighted_score), 2)

        # Overall Model Confidence calculation (0.0 - 1.0)
        modalities_checked = 3 + (1 if audio_available else 0) + (1 if ad_risks.get("evidence") else 0)
        confidence = round(min(1.0, max(0.40, 0.85 + (0.03 * min(modalities_checked, 4)))), 2)

        # Build metrics package for Stage 1 Engine
        stage1_metrics = {
            "violence_score": violence_score,
            "scam_score": scam_score,
            "deceptive_score": deceptive_score,
            "child_safety_flag": child_safety_flag,
            "prohibited_risk": prohibited_risk
        }

        # =================================================================
        # STAGE 1: EXECUTE PROHIBITED CONTENT POLICY ENGINE
        # =================================================================
        prohibited_decision = self.prohibited_engine.evaluate(data, stage1_metrics)

        if prohibited_decision.is_prohibited:
            # Stage 1 Decision: PROHIBITED -> UNSAFE FOR ALL -> REJECT
            classification = "UNSAFE_FOR_ALL"
            display_label = "Unsafe for All"
            publication_action = "REJECT"
            action_badge = "REJECT — UNSAFE FOR ALL"
            prohibited_content_detected = True
            age_restriction = None
            policy_stage = "PROHIBITED_CONTENT_POLICY"
            policy_reasons = prohibited_decision.reasons
            requires_human_review = False
        else:
            # Stage 1 Decision: PERMITTED -> Check HITL then STAGE 2
            prohibited_content_detected = False

            # Check Human-in-the-Loop review condition (Low confidence / ambiguous)
            if confidence < self.CONFIDENCE_THRESHOLD:
                classification = "REQUIRES_HUMAN_REVIEW"
                display_label = "Requires Human Review"
                publication_action = "HUMAN_REVIEW"
                action_badge = "REQUIRES HUMAN REVIEW — MODERATOR QUEUED"
                age_restriction = None
                policy_stage = "HUMAN_IN_THE_LOOP"
                policy_reasons = [f"Model confidence ({int(confidence*100)}%) is below review threshold ({int(self.CONFIDENCE_THRESHOLD*100)}%)"]
                requires_human_review = True
            else:
                # =========================================================
                # STAGE 2: EXECUTE AGE POLICY ENGINE
                # =========================================================
                age_decision = self.age_engine.evaluate(
                    risk_score=risk_score,
                    adult_content_score=adult_content_score,
                    nsfw_score=nsfw_score,
                    explicit_score=explicit_score,
                    dominant_risks=dominant_risks
                )

                classification = age_decision.classification
                display_label = age_decision.display_label
                publication_action = age_decision.publication_action
                action_badge = age_decision.action_badge
                age_restriction = age_decision.age_restriction
                policy_stage = "AGE_POLICY"
                policy_reasons = age_decision.reasons
                requires_human_review = False

        # Generate Evidence-Based Explanation (XAI)
        if classification == "UNSAFE_FOR_ALL":
            explanation = (
                f"Stage 1 Prohibited Content Policy Check FAILED: "
                f"{'; '.join(policy_reasons)}. "
                f"Combined risk score: {risk_score:.1f}/100 (Confidence: {int(confidence*100)}%). "
                f"The advertisement is prohibited from publication and rejected."
            )
        elif classification == "SAFE_18_PLUS":
            explanation = (
                f"Stage 1 Prohibited Check PASSED. "
                f"Stage 2 Age Policy evaluation: {'; '.join(policy_reasons)}. "
                f"Risk score: {risk_score:.1f}/100. Age restricted to 18+ audiences."
            )
        elif classification == "SAFE_14_PLUS":
            explanation = (
                f"Stage 1 Prohibited Check PASSED. "
                f"Stage 2 Age Policy evaluation: {'; '.join(policy_reasons)}. "
                f"Risk score: {risk_score:.1f}/100. Age restricted to 14+ audiences."
            )
        elif classification == "REQUIRES_HUMAN_REVIEW":
            explanation = (
                f"Stage 1 Prohibited Check PASSED. "
                f"Routed to Human Moderator Review Queue due to low model confidence ({int(confidence*100)}%)."
            )
        else:
            explanation = (
                f"Stage 1 Prohibited Check PASSED. "
                f"Stage 2 Age Policy evaluation: {'; '.join(policy_reasons)}. "
                f"Risk score: {risk_score:.1f}/100 (Confidence: {int(confidence*100)}%). "
                f"Approved for general publication."
            )

        return {
            "classification": classification,
            "publication_action": publication_action,
            "action_badge": action_badge,
            "display_label": display_label,
            "risk_score": risk_score,
            "confidence": confidence,
            "prohibited_content_detected": prohibited_content_detected,
            "age_restriction": age_restriction,
            "policy_stage": policy_stage,
            "policy_reasons": policy_reasons,
            "human_review_required": requires_human_review,
            "requires_human_review": requires_human_review,
            "dominant_risks": dominant_risks,
            "detected_categories": dominant_risks,
            "explanation": explanation,
            "assessment_matrix": data,
            "evidence": data
        }

    def combine_evidence(self, *args, **kwargs) -> Dict[str, Any]:
        """Backward compatibility wrapper for legacy combine_evidence calls."""
        if len(args) == 1 and isinstance(args[0], SafeAdAssessment):
            return self.combine_assessment(args[0])
            
        visual_ev = kwargs.get("visual_evidence", args[0] if len(args) > 0 else {})
        violence_ev = kwargs.get("video_violence_evidence", args[1] if len(args) > 1 else {})
        nsfw_ev = kwargs.get("nsfw_evidence", args[2] if len(args) > 2 else {})
        ocr_ev = kwargs.get("ocr_evidence", args[3] if len(args) > 3 else {})
        text_safe_ev = kwargs.get("ocr_text_safety", args[4] if len(args) > 4 else {})
        audio_ev = kwargs.get("audio_evidence", args[5] if len(args) > 5 else {})
        
        assessment = SafeAdAssessment(
            visual={
                "violence": visual_ev.get("violence", 0.0),
                "adult": nsfw_ev.get("adult_score", 0.0),
                "unsafe": visual_ev.get("unsafe", False),
                "evidence": visual_ev.get("detected_categories", [])
            },
            video={
                "violence": violence_ev.get("violence_score", 0.0),
                "adult": nsfw_ev.get("adult_score", 0.0),
                "sampled_segments": violence_ev.get("sampled_segments", [])
            },
            ocr={
                "text": ocr_ev.get("ocr_text", ""),
                "adult": text_safe_ev.get("sexual", 0.0),
                "violence": text_safe_ev.get("violent", 0.0),
                "scam": text_safe_ev.get("misleading", 0.0),
                "confidence": ocr_ev.get("ocr_confidence", 0.0),
                "evidence": text_safe_ev.get("detected_categories", [])
            },
            audio={
                "audio_available": audio_ev.get("audio_available", False),
                "language": audio_ev.get("language", "English"),
                "transcript": audio_ev.get("transcript", ""),
                "adult": audio_ev.get("audio_safety", {}).get("adult", 0.0),
                "violence": audio_ev.get("audio_safety", {}).get("violence", 0.0),
                "scam": audio_ev.get("audio_safety", {}).get("scam", 0.0)
            },
            text_safety=text_safe_ev,
            advertisement_risks={
                "scam": text_safe_ev.get("misleading", 0.0),
                "deceptive_marketing": text_safe_ev.get("deceptive", 0.0),
                "explicit_content": nsfw_ev.get("adult_score", 0.0)
            }
        )
        return self.combine_assessment(assessment)