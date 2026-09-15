MULTILINGUAL_SAFETY_KEYWORDS = {
    "Adult/Sexual Content": {
        "english": ["intimacy", "intimate", "sexy", "adult", "porn", "xxx", "erotic", "nude", "nudity", "sensual", "dating", "sex", "sexual", "romance", "kiss", "kissing", "lingerie", "bikini", "condom", "bedroom", "bed", "passion", "lust", "cleavage", "topless", "naked"],
        "hinglish": ["ganda", "nanga", "ashleel", "pyaar", "chumma", "chudai"],
        "manglish": ["kadi", "leela", "vaanam", "thundu", "muttam", "kammam"]
    },
    "Gambling": {
        "english": ["bet", "betting", "casino", "poker", "jackpot", "win money", "lottery", "slot machine", "slots", "roulette", "blackjack", "wagering", "earn cash", "cash prize", "stake"],
        "hinglish": ["satta", "juwa", "dream11", "paisa jeeto", "khelo aur jeeto", "rummy"],
        "manglish": ["panthayam", "kuri", "paisa kalikkam", "lucky draw"]
    },
    "Violence": {
        "english": ["kill", "blood", "fight", "murder", "weapon", "shoot", "gun", "stab", "dead", "death", "violence", "violent", "combat", "assault", "knife", "sword", "explosion", "attack"],
        "hinglish": ["maar", "khoon", "dhamaka", "bandook", "ladai"],
        "manglish": ["krouryam", "chora", "idi", "vettu", "kolapathakam", "thokku"]
    },
    "Alcohol/Tobacco": {
        "english": ["whiskey", "beer", "wine", "alcohol", "liquor", "spirits", "smoke", "vape", "vaping", "cigarette", "cigar", "bar", "pub", "cocktail", "brewery"],
        "hinglish": ["sharaab", "daru", "sutta", "sigret", "nashe"],
        "manglish": ["madhyam", "kallu", "vellamadi", "vali", "beedi"]
    },
    "Drugs": {
        "english": ["weed", "marijuana", "cocaine", "heroin", "narcotic", "pills", "drugs"],
        "hinglish": ["charas", "ganja", "nasha", "dawai"],
        "manglish": ["kanjavu", "lahari", "marunnu"]
    },
    "Misleading Advertisement": {
        "english": ["earn cash fast", "paisa double", "get rich quick", "free gift card", "guaranteed returns", "giveaway", "click here to win", "instant cash", "double your money", "100% guaranteed profit", "risk free income"],
        "hinglish": ["paisa double", "free prize", "raato raat ameer", "lakhpati"],
        "manglish": ["paisa double", "panam nedam", "free gift", "parasyam", "thattippu"]
    }
}

def analyze_multimodal_text(title: str, caption: str, ocr_text: str, image_caption: str) -> dict:
    """
    Combines all textual modalities (Title + Caption + OCR + Image Caption)
    and computes policy risk scores and category violations.
    """
    combined_text = f"{title or ''} {caption or ''} {ocr_text or ''} {image_caption or ''}".lower()
    
    category_scores = {}
    violations = []
    
    for category, langs in MULTILINGUAL_SAFETY_KEYWORDS.items():
        hits = 0
        matched_words = []
        for lang, keywords in langs.items():
            for kw in keywords:
                if kw in combined_text:
                    hits += 1
                    matched_words.append(kw)
        
        # 50.0 per keyword hit ensures clear policy violation triggers
        score = min(hits * 50.0, 100.0)
        category_scores[category] = score
        if score > 0:
            violations.append(category)
            
    text_risk_score = max(category_scores.values()) if category_scores else 0.0
    
    return {
        "combined_text": combined_text,
        "text_risk_score": text_risk_score,
        "category_scores": category_scores,
        "violations": violations
    }
