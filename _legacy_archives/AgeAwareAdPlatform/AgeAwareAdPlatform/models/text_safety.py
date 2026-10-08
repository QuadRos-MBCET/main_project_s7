import os
from typing import Dict, Any, List, Optional

try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

class SafeAdTextSafetyDetector:
    """
    Pretrained Text Safety Model for SafeAd AI.
    
    Primary Pretrained Model:
    - meta-llama/Llama-Guard-3-1B or Hugging Face open text safety classifier.
    
    Evaluates:
    1. OCR extracted advertisement text
    2. Whisper speech transcript
    
    Outputs normalized safety evidence dictionary:
    {
        "violent": float,
        "sexual": float,
        "child_safety": float,
        "hate": float,
        "gambling": float,
        "alcohol": float,
        "drugs": float,
        "misleading": float,
        "overall_text_risk": float,
        "detected_categories": [...]
    }
    """

    def __init__(
        self,
        model_id: str = "meta-llama/Llama-Guard-3-1B",
        device: str = "cuda" if (HAS_TORCH and torch.cuda.is_available()) else "cpu"
    ):
        self.model_id = model_id
        self.device = device
        self._tokenizer = None
        self._model = None
        self._pipe = None
        self._is_loaded = False

    def load_model(self):
        """Loads text safety model lazily."""
        if self._is_loaded:
            return self

        print(f"[SafeAdTextSafetyDetector] Loading text safety model '{self.model_id}' on {self.device}...")
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            try:
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
                print(f"[SafeAdTextSafetyDetector] Loaded '{self.model_id}' successfully.")
            except Exception as e1:
                print(f"[SafeAdTextSafetyDetector WARNING] Llama Guard 3-1B load fallback: {e1}")
                from transformers import pipeline
                device_idx = 0 if (HAS_TORCH and torch.cuda.is_available() and self.device == "cuda") else -1
                self._pipe = pipeline(
                    "text-classification",
                    model="mrm8488/distilroberta-finetuned-toxic-content",
                    device=device_idx
                )
                print(f"[SafeAdTextSafetyDetector] Loaded open text safety classifier fallback.")

            self._is_loaded = True
        except Exception as e:
            print(f"[SafeAdTextSafetyDetector WARNING] Text safety model initialization fallback: {e}")
            self._is_loaded = True

        return self

    MULTILINGUAL_SAFETY_KEYWORDS = {
        "violent": ["kill", "blood", "fight", "murder", "weapon", "shoot", "gun", "stab", "dead", "death", "violence", "violent", "combat", "assault", "knife", "sword", "explosion", "attack", "maar", "khoon", "vettu", "kolapathakam", "action fight scene", "brutal combat"],
        "sexual": ["intimacy", "intimate", "sexy", "adult", "porn", "xxx", "erotic", "nude", "nudity", "sensual", "dating", "sex", "sexual", "romance", "lingerie", "bikini", "ganda", "ashleel", "nanga", "adult dating 18+"],
        "child_safety": ["underage", "minor", "child exploitation", "csam", "illegal minor", "child solicitation", "pedophile"],
        "hate": ["hate", "racist", "slur", "discriminate", "terrorist", "nazi", "extremist", "hate speech"],
        "gambling": ["casino", "poker", "jackpot", "bet", "betting", "lottery", "slot machine", "slots", "roulette", "blackjack", "wagering", "satta", "juwa", "rummy", "win cash", "grand casino"],
        "alcohol": ["whiskey", "beer", "wine", "alcohol", "liquor", "spirits", "pub", "bar", "cocktail", "brewery", "sharaab", "daru", "beer pub"],
        "drugs": ["weed", "marijuana", "cocaine", "heroin", "narcotic", "pills", "drugs", "ganja", "nasha"],
        "misleading": ["paisa double", "get rich quick", "earn cash fast", "guaranteed returns", "raato raat ameer", "double your money", "risk free income", "100% guaranteed profit", "scam giveaway", "free gift card"]
    }

    CATEGORY_NAME_MAP = {
        "violent": "Violence",
        "sexual": "Adult/Sexual Content",
        "child_safety": "Child Safety Risk",
        "hate": "Hate Speech",
        "gambling": "Gambling",
        "alcohol": "Alcohol/Tobacco",
        "drugs": "Drugs",
        "misleading": "Misleading Advertisement"
    }

    def predict_text(self, text: str) -> Dict[str, Any]:
        """
        Evaluates a text input (title + caption + OCR text or transcript) and returns normalized safety probabilities per category.
        """
        if not text or not text.strip():
            return {
                "violent": 0.0,
                "sexual": 0.0,
                "child_safety": 0.0,
                "hate": 0.0,
                "gambling": 0.0,
                "alcohol": 0.0,
                "drugs": 0.0,
                "misleading": 0.0,
                "overall_text_risk": 0.0,
                "detected_categories": []
            }

        if not self._is_loaded:
            self.load_model()

        text_lower = text.lower()
        cat_scores = {
            "violent": 0.0, "sexual": 0.0, "child_safety": 0.0, "hate": 0.0,
            "gambling": 0.0, "alcohol": 0.0, "drugs": 0.0, "misleading": 0.0
        }
        detected = []

        # 1. Primary Model Generation / Classification
        if self._model is not None and self._tokenizer is not None and HAS_TORCH:
            try:
                prompt = f"<|user|>\nEvaluate advertisement text for policy safety:\n{text}\n<|assistant|>"
                inputs = self._tokenizer(prompt, return_tensors="pt").to(self.device)
                with torch.inference_mode():
                    output_ids = self._model.generate(**inputs, max_new_tokens=40)
                    response = self._tokenizer.decode(output_ids[0], skip_special_tokens=True).lower()

                if "unsafe" in response or "s1" in response:
                    cat_scores["violent"] = 0.90
                if "s2" in response or "sexual" in response:
                    cat_scores["sexual"] = 0.90
                if "s3" in response or "child" in response:
                    cat_scores["child_safety"] = 1.00
                if "s4" in response or "hate" in response:
                    cat_scores["hate"] = 0.90
            except Exception as e:
                print(f"[SafeAdTextSafetyDetector ERROR] Inference error: {e}")

        # 2. Multilingual keyword rule verification
        for category, keywords in self.MULTILINGUAL_SAFETY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    base_score = 1.0 if category in ["child_safety", "misleading"] else 0.85
                    cat_scores[category] = max(cat_scores[category], base_score)
                    display_name = self.CATEGORY_NAME_MAP.get(category, category.replace("_", " ").title())
                    if display_name not in detected:
                        detected.append(display_name)

        overall_risk = max(cat_scores.values()) if cat_scores else 0.0

        return {
            "violent": round(float(cat_scores["violent"]), 4),
            "sexual": round(float(cat_scores["sexual"]), 4),
            "child_safety": round(float(cat_scores["child_safety"]), 4),
            "hate": round(float(cat_scores["hate"]), 4),
            "gambling": round(float(cat_scores["gambling"]), 4),
            "alcohol": round(float(cat_scores["alcohol"]), 4),
            "drugs": round(float(cat_scores["drugs"]), 4),
            "misleading": round(float(cat_scores["misleading"]), 4),
            "overall_text_risk": round(float(overall_risk), 4),
            "detected_categories": detected
        }
