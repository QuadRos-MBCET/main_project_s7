def normalize_age_prediction(age_range: str, confidence: float) -> str:
    if confidence < 0.3:
        return "UNKNOWN"
    
    # Precise mapping to requested age categories:
    # 1. Less than 14
    # 2. 14 to 17
    # 3. 18 and above
    if age_range in ["0-2", "3-9"]:
        return "LESS THAN 14"
    elif age_range == "10-19":
        return "14 TO 17"
    else:
        return "18 AND ABOVE"
