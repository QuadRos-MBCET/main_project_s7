"""
SafeAd AI (SAFE-VISION) — Experimental Repaired Detectors.
Contains experimental detector modules approved for controlled testing:
1. EnhancedAlcoholDetector: Gated keyword, brand, and visual token alcohol detector with strict negative controls.
2. KineticViolenceDecoupler: Video action recognizer with fail-safe human review routing.

IMPORTANT:
- These modules are experimental and MUST NOT be active in the production pipeline by default.
- Production scoring formulas in models/fusion/safead_fusion.py remain strictly frozen.
"""

import re
from typing import Dict, Any, List, Optional


class EnhancedAlcoholDetector:
    """
    Experimental detector for alcoholic beverages and drinking establishments.
    Adheres to strict negative-control principles:
    - Generic bottle / glass presence alone NEVER equates to alcohol.
    - Explicit non-alcoholic claims ('0.0%', 'non-alcoholic', 'virgin') force suppression.
    - Requires verified brand or explicit ABV keyword before triggering.
    """
    VERIFIED_ALCOHOL_BRANDS = [
        "budweiser", "heineken", "corona", "guinness", "stella artois",
        "carlsberg", "smirnoff", "absolut", "bacardi", "captain morgan",
        "jack daniel's", "jack daniels", "johnnie walker", "chivas regal",
        "glenfiddich", "jameson", "hennessy", "remy martin", "grey goose",
        "tanqueray", "bombay sapphire", "gordon's", "baileys", "kahlua",
        "moet", "dom perignon", "veuve clicquot", "tuborg", "kingfisher"
    ]

    EXPLICIT_ALCOHOL_KEYWORDS = [
        "whiskey", "whisky", "vodka", "rum", "tequila", "gin", "brandy",
        "cognac", "beer", "lager", "ale", "stout", "wine", "champagne",
        "liqueur", "liquor", "cocktail", "bourbon", "scotch", "draught beer",
        "hard seltzer", "alcoholic beverage", "craft beer", "brewery", "distillery"
    ]

    GENERIC_CONTAINERS = [
        "bottle", "glass", "wine glass", "beer glass", "cocktail glass",
        "tumbler", "drink", "liquid", "cup", "mug", "bar", "restaurant"
    ]

    EXPLICIT_NON_ALCOHOLIC_TOKENS = [
        "0.0%", "0.0 %", "non-alcoholic", "non alcoholic", "alcohol-free",
        "alcohol free", "zero alcohol", "virgin cocktail", "virgin mojito",
        "soft drink", "fruit juice", "sparkling water", "energy drink",
        "olive oil", "cooking oil", "vinegar"
    ]

    def evaluate_alcohol(
        self,
        ocr_text: str = "",
        speech_transcript: str = "",
        visual_objects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates advertisement text, transcript, and visual object tokens for alcohol promotion.
        """
        vis_objs = visual_objects or []
        combined_text = f"{ocr_text} {speech_transcript}".lower()
        vis_tokens_lower = [str(o).lower() for o in vis_objs]

        # 1. Negative Control Check: Explicit non-alcoholic claims
        has_non_alc = any(t in combined_text for t in self.EXPLICIT_NON_ALCOHOLIC_TOKENS)
        if has_non_alc:
            return {
                "alcohol_detected": False,
                "confidence": 0.95,
                "score": 0.0,
                "reasons": ["Explicit non-alcoholic / zero-alcohol product declaration detected."],
                "matched_brands": [],
                "matched_keywords": []
            }

        matched_brands = [b for b in self.VERIFIED_ALCOHOL_BRANDS if re.search(r'\b' + re.escape(b) + r'\b', combined_text)]
        matched_keywords = [k for k in self.EXPLICIT_ALCOHOL_KEYWORDS if re.search(r'\b' + re.escape(k) + r'\b', combined_text)]

        has_container = any(c in vis_tokens_lower or c in combined_text for c in self.GENERIC_CONTAINERS)

        # 2. Strict Negative Control: Container presence alone NEVER equates to alcohol
        if not matched_brands and not matched_keywords:
            return {
                "alcohol_detected": False,
                "confidence": 0.90,
                "score": 0.0,
                "reasons": ["No verified alcohol brands or keywords found. Generic containers decoupled."],
                "matched_brands": [],
                "matched_keywords": []
            }

        # 3. Verified Detection
        if matched_brands:
            score = 0.95 if has_container else 0.85
            reasons = [f"Verified alcohol brand identified: {', '.join(matched_brands)}"]
            if has_container:
                reasons.append("Alcoholic beverage container/establishment context confirmed.")
            return {
                "alcohol_detected": True,
                "confidence": score,
                "score": score,
                "reasons": reasons,
                "matched_brands": matched_brands,
                "matched_keywords": matched_keywords
            }

        if matched_keywords:
            score = 0.85 if has_container else 0.70
            reasons = [f"Explicit alcohol category keyword identified: {', '.join(matched_keywords)}"]
            return {
                "alcohol_detected": True,
                "confidence": score,
                "score": score,
                "reasons": reasons,
                "matched_brands": [],
                "matched_keywords": matched_keywords
            }

        return {
            "alcohol_detected": False,
            "confidence": 0.90,
            "score": 0.0,
            "reasons": [],
            "matched_brands": [],
            "matched_keywords": []
        }


class KineticViolenceDecoupler:
    """
    Experimental decoupler separating genuine interpersonal violence from
    camera motion, athletic activities, and dynamic videography.

    Fail-Safe Routing Principle:
    - If visual safety flags violence and VideoMAE confidence is low (< 0.30)
      without a high-confidence benign athletic explanation, it ROUTES TO HUMAN REVIEW
      and WITHHOLDS publication.
    """
    INTERPERSONAL_VIOLENCE_ACTIONS = [
        "punching person", "slapping", "kicking", "wrestling", "brawling",
        "fighting", "sword fighting", "shooting gun", "stabbing", "headbutting"
    ]

    BENIGN_ATHLETIC_AND_MOTION_ACTIONS = [
        "running on treadmill", "jogging", "marathon running", "swimming",
        "skateboarding", "snowboarding", "gymnastics tumbling", "dancing",
        "playing basketball", "playing tennis", "driving car", "cycling",
        "parkour", "pole vault", "cheerleading"
    ]

    def evaluate_video_action(
        self,
        sampled_segments: List[Dict[str, Any]],
        raw_motion_diff: float = 0.0,
        text_context: str = "",
        visual_violence_flag: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluates sampled video action segments with fail-safe ambiguity routing.
        """
        top_violence_prob = 0.0
        violent_label = None
        top_benign_prob = 0.0
        benign_label = None

        for seg in sampled_segments:
            lbl = str(seg.get("label", "")).lower()
            score = float(seg.get("score", 0.0))

            if any(v_act in lbl for v_act in self.INTERPERSONAL_VIOLENCE_ACTIONS):
                if score > top_violence_prob:
                    top_violence_prob = score
                    violent_label = lbl

            if any(a_act in lbl for a_act in self.BENIGN_ATHLETIC_AND_MOTION_ACTIONS):
                if score > top_benign_prob:
                    top_benign_prob = score
                    benign_label = lbl

        text_lower = text_context.lower()
        has_violent_text = any(w in text_lower for w in ["fight", "murder", "blood", "gun", "knife", "combat", "war", "assault", "brawl"])

        # Case 1: Confirmed Interpersonal Violence
        if top_violence_prob >= 0.40 or (top_violence_prob >= 0.25 and has_violent_text) or has_violent_text:
            return {
                "violence_detected": True,
                "requires_human_review": False,
                "action": "REJECT",
                "violence_score": round(max(top_violence_prob, 0.85 if has_violent_text else 0.70), 4),
                "top_violent_action": violent_label,
                "policy_reasons": [f"Prohibited interpersonal violence detected ({violent_label or 'text cues'})"],
                "explanation": "Severe physical aggression or violent weapon action confirmed."
            }

        # Case 2: Visual Violence Flagged with Low-Confidence / Conflicting VideoMAE Evidence (FAIL-SAFE)
        if visual_violence_flag:
            if top_benign_prob >= 0.45 and not has_violent_text:
                return {
                    "violence_detected": False,
                    "requires_human_review": False,
                    "action": "APPROVE",
                    "violence_score": 0.12,
                    "policy_reasons": [f"Visual motion explained by high-confidence athletic action ({benign_label})"],
                    "explanation": "High-confidence athletic action confirmed; camera motion decoupled."
                }
            else:
                # VideoMAE returned diffuse or low confidence (< 0.30) -> DO NOT SUPPRESS. Route to HITL!
                return {
                    "violence_detected": False,
                    "requires_human_review": True,
                    "action": "ROUTE_TO_HUMAN_REVIEW",
                    "violence_score": 0.60,
                    "policy_reasons": ["Detector conflict: Visual guard flagged violence, but video classifier returned low confidence (< 0.30). Withheld for human safety officer review."],
                    "explanation": "Ambiguous/conflicting video violence evidence. Publication withheld pending human review."
                }

        # Case 3: Visual Violence NOT Flagged
        if top_benign_prob >= 0.15:
            return {
                "violence_detected": False,
                "requires_human_review": False,
                "action": "APPROVE",
                "violence_score": 0.05,
                "policy_reasons": [],
                "explanation": f"Benign motion identified ({benign_label}); camera movement decoupled."
            }

        final_v = min(0.18, raw_motion_diff / 100.0)
        return {
            "violence_detected": False,
            "requires_human_review": False,
            "action": "APPROVE",
            "violence_score": final_v,
            "policy_reasons": [],
            "explanation": "Standard commercial video pacing; no violence detected."
        }
