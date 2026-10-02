class SafeAdClassifier:
    @staticmethod
    def classify(fused_score: float, visual_risk: float, nlp_risk: float, speech_risk: float, violations: list) -> dict:
        """
        Adapts binary risks into the Future SafeAd 4-Class Architecture.
        """
        if fused_score > 75 or visual_risk > 75:
            classification = "UNSAFE_FOR_ALL"
            risk_category = "PROHIBITED_CONTENT"
        elif fused_score > 35 or "Adult/Sexual Content" in violations:
            classification = "AGE_18_PLUS"
            risk_category = "ADULT_RESTRICTED"
        elif "Alcohol/Tobacco" in violations:
            classification = "AGE_18_PLUS"
            risk_category = "RESTRICTED_SUBSTANCES"
        else:
            classification = "SAFE_FOR_ALL"
            risk_category = "GENERAL_AUDIENCE"
            
        return {
            "classification": classification,
            "classification_status": "FOUR_CLASS_MODEL_ADAPTED",
            "risk_category": risk_category,
            "risk_score": fused_score,
            "risk_score_available": True
        }
