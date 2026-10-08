from typing import Dict, Any, List

class AdRiskAnalyzer:
    """
    Dedicated Proactive Advertisement Risk Analyzer for SafeAd AI.
    
    Evaluates advertisement-specific risk categories:
    1. Scam Indicators (e.g. get rich quick, double your money, guaranteed returns)
    2. Deceptive Marketing (e.g. risk-free income, raato raat ameer, 100% free prize)
    3. Explicit Content Indicators (e.g. adult-only explicit materials)
    
    Combines rule-based semantic analysis with text safety model predictions.
    Keeps model-generated evidence and rule-generated evidence distinguishable internally.
    """

    SCAM_KEYWORDS = [
        "scam", "paisa double", "get rich quick", "double your money", "guaranteed return",
        "100% guaranteed profit", "instant cash", "raato raat ameer", "earn 100000 daily",
        "pyramid scheme", "investment trick", "crypto giveaway", "free bitcoin"
    ]

    DECEPTIVE_MARKETING_KEYWORDS = [
        "risk free income", "100% free gift", "click here to win", "claim your prize",
        "lakhpati", "free prize", "guaranteed win", "no investment needed win cash",
        "thattippu", "free gift card", "instant rich"
    ]

    EXPLICIT_KEYWORDS = [
        "xxx", "porn", "porno", "nude", "nudity", "erotica", "x-rated", "18+ adult",
        "escort", "hentai", "camgirl", "nsfw ad", "onlyfans"
    ]

    def analyze_ad_risks(
        self,
        ocr_text: str = "",
        transcript: str = "",
        title: str = "",
        caption: str = "",
        text_safety_output: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Evaluates advertisement copy and text inputs for scam, deceptive marketing, and explicit risks.
        """
        combined_text = f"{title or ''} {caption or ''} {ocr_text or ''} {transcript or ''}".lower()
        
        scam_score = 0.0
        deceptive_score = 0.0
        explicit_score = 0.0
        rule_evidence = []
        detected_risks = []

        # 1. Scam Keyword Evaluation
        for kw in self.SCAM_KEYWORDS:
            if kw in combined_text:
                scam_score = max(scam_score, 0.85)
                rule_evidence.append(f"Scam indicator keyword '{kw}' detected in copy.")
                if "Scam Indicators" not in detected_risks:
                    detected_risks.append("Scam Indicators")

        # 2. Deceptive Marketing Evaluation
        for kw in self.DECEPTIVE_MARKETING_KEYWORDS:
            if kw in combined_text:
                deceptive_score = max(deceptive_score, 0.80)
                rule_evidence.append(f"Deceptive marketing keyword '{kw}' detected in copy.")
                if "Deceptive Marketing" not in detected_risks:
                    detected_risks.append("Deceptive Marketing")

        # 3. Explicit Content Keyword Evaluation
        for kw in self.EXPLICIT_KEYWORDS:
            if kw in combined_text:
                explicit_score = max(explicit_score, 0.90)
                rule_evidence.append(f"Explicit content keyword '{kw}' detected in copy.")
                if "Explicit Content" not in detected_risks:
                    detected_risks.append("Explicit Content")

        # 4. Integrate Text Safety Model Outputs if available
        if text_safety_output:
            if text_safety_output.get("misleading", 0.0) >= 0.50:
                deceptive_score = max(deceptive_score, text_safety_output.get("misleading"))
                rule_evidence.append("Text safety model detected misleading marketing semantics.")
                if "Deceptive Marketing" not in detected_risks:
                    detected_risks.append("Deceptive Marketing")
            if text_safety_output.get("sexual", 0.0) >= 0.50:
                explicit_score = max(explicit_score, text_safety_output.get("sexual"))

        return {
            "scam_score": round(scam_score, 4),
            "deceptive_marketing_score": round(deceptive_score, 4),
            "explicit_content_score": round(explicit_score, 4),
            "detected_risks": detected_risks,
            "rule_based_evidence": rule_evidence
        }
