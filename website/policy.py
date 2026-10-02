# website/policy.py

def enforce_age_aware_policy(class_id: int, user_age_category: str) -> dict:
    """
    Implements the age-aware policy engine for the 4-class SafeAd system.
    
    class_id mapping:
    0 = Safe for All
    1 = 14+
    2 = 18+
    3 = Unsafe for All
    
    user_age_category should be one of:
    "<14", "14-17", "18+" (or compatible variants)
    """
    # Normalize user age category
    cat = user_age_category.lower()
    if "child" in cat or "14" in cat and "<" in cat:
        user_tier = 0  # Under 14
    elif "14" in cat or "teen" in cat:
        user_tier = 1  # 14 to 17
    elif "18" in cat or "adult" in cat or "not a child" in cat:
        user_tier = 2  # 18+
    else:
        # Default fallback (most restrictive)
        user_tier = 0

    action = "REJECT"
    reason = ""
    can_view = False

    if class_id == 0:  # Safe for All
        action = "APPROVE"
        can_view = True
        reason = "Advertisement is Safe for All and approved."
        
    elif class_id == 1:  # 14+
        action = "AGE RESTRICT 14+"
        can_view = (user_tier >= 1)
        reason = "Advertisement is restricted to users 14 and older."
        
    elif class_id == 2:  # 18+
        action = "AGE RESTRICT 18+"
        can_view = (user_tier >= 2)
        reason = "Advertisement is restricted to users 18 and older (Adults only)."
        
    elif class_id == 3:  # Unsafe for All
        action = "REJECT"
        can_view = False
        reason = "Advertisement contains prohibited content and is unsafe for all users."

    return {
        "action": action,
        "can_view": can_view,
        "policy_reason": reason,
        "user_tier_detected": user_tier
    }
