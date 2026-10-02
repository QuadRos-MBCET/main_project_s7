class ExplanationService:
    @staticmethod
    def generate_explanation(classification: str, risk_score: float, violations: list, colab_caption: str) -> dict:
        """
        Generates an explainable AI reason based on multimodal evidence.
        """
        violation_str = ", ".join(violations) if violations else "None"
        
        explanation = f"AI Decision: {classification} (Risk: {risk_score:.1f}%). Violated Policies: {violation_str}."
        
        if classification == "UNSAFE_FOR_ALL":
            explanation += f" Rejection triggered due to high-risk multimodal indicators."
        elif classification in ["AGE_18_PLUS", "AGE_14_PLUS"]:
            explanation += f" Age restriction triggered based on identified policy flags."
        else:
            explanation += " No significant policy violations detected."
            
        evidence = {
            "detected_violations": violations,
            "generated_caption": colab_caption
        }
        
        return {
            "explanation": explanation,
            "evidence": evidence
        }
