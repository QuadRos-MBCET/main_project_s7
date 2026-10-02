class PolicyService:
    @staticmethod
    def apply_age_policy(classification: str, user_age_group: str = "AGE_18_PLUS") -> str:
        """
        Enforces age-aware policy restrictions based on user demographics and ad classification.
        """
        if classification == "SAFE_FOR_ALL":
            return "APPROVE"
        elif classification == "UNSAFE_FOR_ALL":
            return "REJECT"
            
        # Age-aware logic
        if classification == "AGE_18_PLUS":
            if user_age_group == "AGE_18_PLUS":
                return "APPROVE"
            else:
                return "RESTRICT"
                
        if classification == "AGE_14_PLUS":
            if user_age_group in ["AGE_14_TO_17", "AGE_18_PLUS"]:
                return "APPROVE"
            else:
                return "RESTRICT"
                
        return "REJECT"
