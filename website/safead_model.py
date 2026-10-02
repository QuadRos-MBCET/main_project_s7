import os
import pickle
import numpy as np
try:
    import pandas as pd
    from sklearn.neural_network import MLPClassifier
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support
    from sklearn.model_selection import train_test_split
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Four-Class Taxonomy
CLASS_MAP = {
    0: "Safe for All",
    1: "14+",
    2: "18+",
    3: "Unsafe for All"
}

# Ordered policies for feature vectorization
POLICIES = [
    "Adult/Sexual Content", 
    "Child Safety", 
    "Violence", 
    "Gambling", 
    "Alcohol/Tobacco", 
    "Drugs", 
    "Hate/Abusive Content", 
    "Misleading Advertisement",
    "Other Age-Restricted Content"
]

class SafeAdMultimodalFusion:
    def __init__(self, model_path="safead_fusion_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.feature_names = [f"visual_{p}" for p in POLICIES] + \
                             [f"ocr_{p}" for p in POLICIES] + \
                             [f"speech_{p}" for p in POLICIES]

    def _build_feature_vector(self, visual_scores: dict, ocr_scores: dict, speech_scores: dict) -> np.ndarray:
        vec = []
        for p in POLICIES:
            vec.append(visual_scores.get(p, 0.0))
        for p in POLICIES:
            vec.append(ocr_scores.get(p, 0.0))
        for p in POLICIES:
            vec.append(speech_scores.get(p, 0.0))
        return np.array(vec, dtype=np.float32)

    def train_model(self, X_train, y_train):
        if not HAS_SKLEARN:
            print("scikit-learn not installed. Training skipped.")
            return
            
        print(f"Training SafeAd Multimodal Fusion Model on {len(y_train)} samples...")
        self.model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Save model
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        print("Model trained and saved to", self.model_path)

    def load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            return True
        return False

    def predict(self, visual_scores: dict, ocr_scores: dict, speech_scores: dict) -> dict:
        """
        Forward pass for the SafeAd model.
        Returns the predicted class, risk score (max probability), and contributing modalities.
        """
        features = self._build_feature_vector(visual_scores, ocr_scores, speech_scores)
        
        if self.model is None:
            # Fallback to rule-based heuristic if model is not trained yet (e.g., browser env)
            return self._heuristic_fallback(visual_scores, ocr_scores, speech_scores)
            
        # Reshape for single prediction
        X = features.reshape(1, -1)
        
        if not HAS_SKLEARN:
             return self._heuristic_fallback(visual_scores, ocr_scores, speech_scores)
             
        try:
            pred_class = int(self.model.predict(X)[0])
            probs = self.model.predict_proba(X)[0]
            risk_score = float(np.max(probs))
            
            # Simple feature attribution (which modality had the highest inputs?)
            v_sum = np.sum(X[0, 0:9])
            o_sum = np.sum(X[0, 9:18])
            s_sum = np.sum(X[0, 18:27])
            
            modalities = []
            if v_sum > 0: modalities.append("Visual")
            if o_sum > 0: modalities.append("OCR/Text")
            if s_sum > 0: modalities.append("Speech")
            
            return {
                "class_id": pred_class,
                "class_name": CLASS_MAP[pred_class],
                "risk_score": risk_score,
                "evidence_modalities": modalities,
                "is_heuristic": False
            }
        except Exception:
             return self._heuristic_fallback(visual_scores, ocr_scores, speech_scores)

    def _heuristic_fallback(self, visual_scores, ocr_scores, speech_scores):
        """
        Fallback logic for when the model isn't trained or scikit-learn is missing (Stlite WebAssembly).
        Maps maximum risk scores into the 4 classes.
        """
        max_visual = max(visual_scores.values()) if visual_scores else 0
        max_ocr = max(ocr_scores.values()) if ocr_scores else 0
        max_speech = max(speech_scores.values()) if speech_scores else 0
        
        max_overall = max(max_visual, max_ocr, max_speech)
        
        modalities = []
        if max_visual > 0: modalities.append("Visual")
        if max_ocr > 0: modalities.append("OCR/Text")
        if max_speech > 0: modalities.append("Speech")
        
        # Policy Mapping Heuristic
        # 0: Safe, 1: 14+, 2: 18+, 3: Unsafe for All
        # Drugs/Child Safety/Extreme Hate -> Unsafe for All
        unsafe_policies = ["Drugs", "Child Safety", "Hate/Abusive Content", "Misleading Advertisement"]
        adult_policies = ["Adult/Sexual Content", "Violence", "Gambling", "Alcohol/Tobacco", "Other Age-Restricted Content"]
        
        class_id = 0
        risk_score = max_overall / 100.0 if max_overall > 0 else 0.05
        
        # Check all combined scores
        combined_scores = {}
        for p in POLICIES:
            combined_scores[p] = max(visual_scores.get(p, 0), ocr_scores.get(p, 0), speech_scores.get(p, 0))
            
        for p, score in combined_scores.items():
            if score > 60:
                if p in unsafe_policies:
                    class_id = max(class_id, 3)
                elif p in adult_policies:
                    class_id = max(class_id, 2)
                    
        # 14+ trigger (moderate scores in adult policies)
        if class_id == 0:
            for p, score in combined_scores.items():
                if 30 < score <= 60 and p in adult_policies:
                    class_id = max(class_id, 1)

        return {
            "class_id": class_id,
            "class_name": CLASS_MAP[class_id],
            "risk_score": risk_score,
            "evidence_modalities": modalities,
            "is_heuristic": True
        }

def evaluate_model(model, X_test, y_test):
    """
    Evaluates the model and calculates Accuracy, Precision, Recall, F1 for the 4 classes.
    """
    if not HAS_SKLEARN:
        return {}
        
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(y_test, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0)
    
    # Macro averages
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(y_test, y_pred, average='macro', zero_division=0)
    
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3])
    
    results = {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "per_class": {}
    }
    
    for i in range(4):
        results["per_class"][CLASS_MAP[i]] = {
            "precision": p[i],
            "recall": r[i],
            "f1": f1[i]
        }
    
    print("\n=== SafeAd Evaluation Results ===")
    print(f"Accuracy: {acc:.4f} | Macro F1: {macro_f1:.4f}")
    print("\nPer-Class Breakdown:")
    for cls_name, metrics in results["per_class"].items():
        print(f" - {cls_name:15}: P={metrics['precision']:.4f}, R={metrics['recall']:.4f}, F1={metrics['f1']:.4f}")
        
    return results
