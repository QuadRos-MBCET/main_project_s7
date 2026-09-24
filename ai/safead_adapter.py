class SafeAdModelService:
    @staticmethod
    def adapt_prediction(
        fused_score: float,
        visual_risk: float,
        text_risk: float,
        violations: list,
        explanation_str: str,
        audio_risk: float = 0.0,
        speech_transcript: str = ""
    ) -> dict:
        """
        Adapts raw multimodal model predictions (visual, text, audio, metadata) into the SafeAd standardized 4-Class schema:
        1. SAFE_FOR_ALL   (Publishable, Age Restriction: None, Action: APPROVE)
        2. AGE_14_PLUS    (Publishable, Age Restriction: 14,   Action: RESTRICT)
        3. AGE_18_PLUS    (Publishable, Age Restriction: 18,   Action: RESTRICT)
        4. UNSAFE_FOR_ALL (Not Publishable, Age Restriction: None, Action: REJECT)
        """
        risk_score_available = (fused_score is not None and fused_score >= 0)
        
        # Check violations list or Phase 1 risk flags across visual, OCR, audio speech, and metadata
        has_violence = any("violence" in str(v).lower() for v in violations)
        has_child_risk = any("child" in str(v).lower() for v in violations)
        has_adult = any("adult" in str(v).lower() or "nsfw" in str(v).lower() or "sexual" in str(v).lower() for v in violations)
        has_gambling = any("gambling" in str(v).lower() or "casino" in str(v).lower() for v in violations)
        has_substances = any("alcohol" in str(v).lower() or "tobacco" in str(v).lower() or "drugs" in str(v).lower() for v in violations)
        has_misleading = any("misleading" in str(v).lower() or "scam" in str(v).lower() for v in violations)

        effective_fused = max(fused_score, audio_risk)

        # Standardized 4-Class Classification Mapping Logic
        # 1. UNSAFE_FOR_ALL: Child Safety, Violence, Deceptive/Scam Claims, or High Multimodal Risk (> 75%)
        if effective_fused > 75.0 or visual_risk > 85.0 or has_violence or has_child_risk or has_misleading:
            classification = "UNSAFE_FOR_ALL"
            risk_category = "prohibited"
            action = "REJECT"
            age_restriction = None
            publishable = False
            
        # 2. AGE_18_PLUS: Gambling, Adult Content, Alcohol/Tobacco, Drugs, or Moderate/High Risk (> 35%)
        elif has_adult or has_gambling or has_substances or visual_risk > 50.0 or effective_fused > 35.0:
            classification = "AGE_18_PLUS"
            risk_category = "adult_restricted"
            action = "RESTRICT"
            age_restriction = 18
            publishable = True
            
        # 3. AGE_14_PLUS: Moderate risk or mild sensitive terms (> 20%)
        elif effective_fused > 20.0:
            classification = "AGE_14_PLUS"
            risk_category = "teen_restricted"
            action = "RESTRICT"
            age_restriction = 14
            publishable = True
            
        # 4. SAFE_FOR_ALL: General audience content
        else:
            classification = "SAFE_FOR_ALL"
            risk_category = "general_audience"
            action = "APPROVE"
            age_restriction = None
            publishable = True
            
        # Standardized schema
        return {
            "classification": classification,
            "risk_score": round(effective_fused, 2) if risk_score_available else None,
            "risk_score_available": risk_score_available,
            "risk_category": risk_category,
            "explanation": explanation_str,
            "age_restriction": age_restriction,
            "action": action,
            "publishable": publishable,
            "violations": violations,
            "speech_transcript": speech_transcript
        }
