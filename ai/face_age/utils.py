def normalize_age_prediction(age_range: str, confidence: float) -> str:
    if confidence < 0.5:
        return "UNKNOWN"
    
    # Simple mapping based on expected ranges from the ViT model
    child_ranges = ["0-2", "3-9"]
    teen_ranges = ["10-19"]
    
    if age_range in child_ranges:
        return "CHILD"
    elif age_range in teen_ranges:
        return "TEEN"
    else:
        return "ADULT"
