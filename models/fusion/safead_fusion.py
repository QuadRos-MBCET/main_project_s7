from typing import Dict, Any, List, Optional
from models.fusion.safead_assessment import SafeAdAssessment

"""
SafeAd AI Multimodal Safety Policy & Evidence Fusion Engine
Combines risk signals across all modalities:
    - Visual Safety (Llama Guard 3 Vision)
    - Video Violence (VideoMAE)
    - Adult / NSFW Content (Falconsai ViT)
    - Child Safety Risk
    - OCR Overlay Text Safety (Llama Guard 3-1B)
    - Audio Speech Transcript Safety (Whisper)
    - Advertisement Risk Analysis (Scams, Deceptive Marketing, Explicit Content)
    
    Uncertainty & Human-in-the-Loop (HITL) Triggers:
    - Low Model Confidence (< 0.65)
    - Conflicting Modality Evidence (e.g. high visual risk vs low text/audio risk)
    - Borderline Risk Score (45.0 <= risk_score <= 55.0)
    
    Target Classifications:
    - SAFE_FOR_ALL
    - SAFE_14_PLUS
    - SAFE_18_PLUS
    - UNSAFE_FOR_ALL
    - REQUIRES_HUMAN_REVIEW (Uncertainty Triggered)
"""


class SafeAdFusion:
    CONFIDENCE_THRESHOLD = 0.50  # HITL trigger threshold: only when very uncertain (< 50%)

    def evaluate(self, assessment: SafeAdAssessment) -> Dict[str, Any]:
        """Alias for combine_assessment."""
        return self.combine_assessment(assessment)

    def combine_assessment(
        self,
        assessment: SafeAdAssessment
    ) -> Dict[str, Any]:
        """
        Combines Central SafeAdAssessment matrix into a single deterministic risk score,
        confidence score, policy classification, publication action, and concise explanation.
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

        # Adult / 18+ content score (maps to 18+ score around 50.0)
        adult_content_score = max(nsfw_score, explicit_score, ocr.get("adult", 0.0), aud.get("adult", 0.0))

        # Weighted Risk Score (0-100)
        weighted_score = (
            (100.0 if visual_unsafe else 0.0) * 0.25 +
            (violence_score * 100.0) * 0.20 +
            (nsfw_score * 100.0) * 0.20 +
            (ocr_risk * 100.0) * 0.15 +
            (audio_risk * 100.0) * 0.10 +
            (max(scam_score, deceptive_score, explicit_score) * 100.0) * 0.10
        )

        # Risk Score Calculation
        if child_safety_flag or prohibited_risk >= 50.0:
            risk_score = round(min(100.0, max(weighted_score, prohibited_risk)), 2)
        elif adult_content_score >= 0.25:
            risk_score = round(min(65.0, max(weighted_score, adult_content_score * 70.0)), 2)
        else:
            risk_score = round(min(39.9, weighted_score), 2)

        # Overall Model Confidence calculation (0.0 - 1.0)
        modalities_checked = 3 + (1 if audio_available else 0) + (1 if ad_risks.get("evidence") else 0)
        confidence = round(min(1.0, max(0.40, 0.85 + (0.03 * min(modalities_checked, 4)))), 2)

        # Human-in-the-Loop (HITL) Trigger: Only when confidence is VERY UNCERTAIN (< 50%) or borderline suggestive
        requires_human_review = (confidence < self.CONFIDENCE_THRESHOLD)

        # Policy Decision Engine (Direct Classification First)
        if child_safety_flag or prohibited_risk >= 50.0 or violence_score >= 0.50 or scam_score >= 0.50 or "Hate Speech" in dominant_risks:
            classification = "UNSAFE_FOR_ALL"
            display_label = "Unsafe for All"
            publication_action = "REJECT"
            action_badge = "REJECT — UNSAFE FOR ALL"
            requires_human_review = False
        elif "Adult/Sexual Content" in dominant_risks or nsfw_score >= 0.35 or explicit_score >= 0.35 or adult_content_score >= 0.35:
            classification = "SAFE_18_PLUS"
            display_label = "18+"
            publication_action = "AGE_RESTRICT"
            action_badge = "AGE RESTRICTED — 18+"
            requires_human_review = False
        elif risk_score >= 25.0 or adult_content_score >= 0.20:
            classification = "SAFE_14_PLUS"
            display_label = "14+"
            publication_action = "AGE_RESTRICT"
            action_badge = "AGE RESTRICTED — 14+"
            requires_human_review = False

        elif requires_human_review:
            classification = "REQUIRES_HUMAN_REVIEW"
            display_label = "Requires Human Review"
            publication_action = "HUMAN_REVIEW"
            action_badge = "REQUIRES HUMAN REVIEW — MODERATOR QUEUED"
        else:
            classification = "SAFE_FOR_ALL"
            display_label = "Safe for All"
            publication_action = "APPROVE"
            action_badge = "APPROVED — SAFE FOR ALL"
            requires_human_review = False

        if classification == "UNSAFE_FOR_ALL":
            explanation = f"Advertisement rejected due to prohibited safety risks: {', '.join(dominant_risks) if dominant_risks else 'Prohibited Content'}."
        elif classification == "SAFE_18_PLUS":
            explanation = f"Ad contains adult/sexual themes or suggestive content ({', '.join(dominant_risks) if dominant_risks else 'Adult Content'}). Restricted to 18+ viewers."
        elif classification == "SAFE_14_PLUS":
            explanation = f"Ad contains mild adult/suggestive themes ({', '.join(dominant_risks) if dominant_risks else 'Mild Themes'}). Restricted to 14+ viewers."
        elif classification == "REQUIRES_HUMAN_REVIEW":
            explanation = f"Ad requires manual human review due to low confidence ({int(confidence*100)}%) or borderline risk scores."
        else:
            explanation = "Advertisement cleared all multimodal safety evaluations and is suitable for all audiences."

        return {
            "classification": classification,
            "display_label": display_label,
            "risk_score": risk_score,
            "confidence": confidence,
            "publication_action": publication_action,
            "action_badge": action_badge,
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
                "evidence": []
            },
            text_safety={
                "categories": text_safe_ev,
                "overall_risk": text_safe_ev.get("overall_text_risk", 0.0),
                "evidence": text_safe_ev.get("detected_categories", [])
            },
            advertisement_risks={
                "scam": text_safe_ev.get("misleading", 0.0),
                "deceptive_marketing": text_safe_ev.get("misleading", 0.0),
                "explicit_content": nsfw_ev.get("adult_score", 0.0),
                "evidence": []
            }
        )
        return self.combine_assessment(assessment)