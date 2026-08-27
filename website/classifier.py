import cv2
import numpy as np
import pandas as pd
import random

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import make_pipeline
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neural_network import MLPClassifier
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# =====================================================================
# 1. FACIAL AGE ESTIMATION SYSTEM (Haar Cascade + Scikit-Learn MLP)
# =====================================================================

try:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
except Exception:
    face_cascade = None

def detect_and_crop_face(image_np: np.ndarray) -> tuple:
    if image_np is None:
        return np.zeros((128, 128, 3), dtype=np.uint8), None
    if face_cascade is None:
        return cv2.resize(image_np, (128, 128)), None
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    try:
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    except Exception:
        faces = []
    if len(faces) == 0:
        return cv2.resize(image_np, (128, 128)), None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    cropped_face = image_np[y:y+h, x:x+w]

    return cv2.resize(cropped_face, (128, 128)), (x, y, w, h)

def extract_facial_features(cropped_face: np.ndarray, bbox: tuple) -> np.ndarray:
    if bbox is not None:
        x, y, w, h = bbox
        aspect_ratio = w / h
        roundness = min(w, h) / max(w, h)
    else:
        aspect_ratio = 1.0
        roundness = 1.0
    gray_face = cv2.cvtColor(cropped_face, cv2.COLOR_RGB2GRAY)
    vertical_projection = np.mean(gray_face, axis=1)
    projection_bins = np.array([np.mean(chunk) for chunk in np.array_split(vertical_projection, 10)])
    projection_bins_normalized = (projection_bins - np.mean(projection_bins)) / (np.std(projection_bins) + 1e-6)
    return np.concatenate(([aspect_ratio, roundness], projection_bins_normalized))

# Fit a static, robust reference model for face-based age estimation
def _train_static_face_classifier():
    features_list = []
    labels_list = []
    
    # Generate Child round profiles (label=0) vs Adult long profiles (label=1)
    for _ in range(100):
        # Child Face
        img_child = np.ones((128, 128, 3), dtype=np.uint8) * 240
        cv2.ellipse(img_child, (64, 64), (45, 45), 0, 0, 360, (255, 200, 180), -1)
        cv2.circle(img_child, (49, 69), 7, (40, 40, 40), -1)
        cv2.circle(img_child, (79, 69), 7, (40, 40, 40), -1)
        cropped, bbox = detect_and_crop_face(img_child)
        features_list.append(extract_facial_features(cropped, bbox))
        labels_list.append(0)
        
        # Adult Face
        img_adult = np.ones((128, 128, 3), dtype=np.uint8) * 240
        cv2.ellipse(img_adult, (64, 64), (36, 54), 0, 0, 360, (245, 190, 160), -1)
        cv2.circle(img_adult, (49, 54), 4, (40, 40, 40), -1)
        cv2.circle(img_adult, (79, 54), 4, (40, 40, 40), -1)
        cropped, bbox = detect_and_crop_face(img_adult)
        features_list.append(extract_facial_features(cropped, bbox))
        labels_list.append(1)
        
    if HAS_SKLEARN:
        clf = MLPClassifier(hidden_layer_sizes=(16, 8), max_iter=300, random_state=42)
        clf.fit(np.array(features_list), np.array(labels_list))
        return clf
    return None

face_age_clf = _train_static_face_classifier()

def estimate_age_from_face(image_np: np.ndarray) -> tuple:
    """
    Returns estimated age classification ('Child' or 'Not a Child') and child probability.
    """
    cropped_face, bbox = detect_and_crop_face(image_np)
    if not HAS_SKLEARN:
        # Fallback heuristic: roundness threshold (child face is rounder)
        if bbox is not None:
            x, y, w, h = bbox
            roundness = min(w, h) / max(w, h)
        else:
            roundness = 1.0
        prob_child = float(np.clip((roundness - 0.7) / 0.3, 0.0, 1.0))
        prediction = "Child" if prob_child > 0.5 else "Not a Child"
        return prediction, prob_child

    feats = extract_facial_features(cropped_face, bbox)
    probs = face_age_clf.predict_proba([feats])[0]
    prob_child = probs[0]
    prediction = "Child" if prob_child > 0.5 else "Not a Child"
    return prediction, prob_child

# =====================================================================
# 2. BEHAVIORAL AGE ESTIMATION SYSTEM (Search Queries + Reel Retention)
# =====================================================================

training_queries = [
    # Child searches
    {"queries": "cartoon animations free online games toy reviews fun math games", "label": "Child"},
    {"queries": "minecraft speedrun roblox play online stories for kids baby shark", "label": "Child"},
    {"queries": "science facts for school project dinosaurs drawing animals toys", "label": "Child"},
    {"queries": "barbie dressup coloring books fairy tales rhymes cartoon songs", "label": "Child"},
    # Adult searches
    {"queries": "stock market predictions mortgage interest rates job search linkedin career", "label": "Not a Child"},
    {"queries": "machine learning developer documentation coding tutorial python django", "label": "Not a Child"},
    {"queries": "real estate investing credit cards travel insurance mutual fund", "label": "Not a Child"},
    {"queries": "world news politics tax filings office dashboard analytics", "label": "Not a Child"}
]

if HAS_SKLEARN:
    df_queries = pd.DataFrame(training_queries)
    text_clf = make_pipeline(TfidfVectorizer(), MultinomialNB())
    text_clf.fit(df_queries["queries"], df_queries["label"])
else:
    text_clf = None

def estimate_age_from_behavior(session_queries: list, gk_watches: list, adult_watches: list) -> tuple:
    """
    Fuses search queries and video watch retention metrics to predict user category.
    """
    # 1. Evaluate search query text probability
    if HAS_SKLEARN:
        query_text = " ".join(session_queries) if session_queries else "normal browse"
        text_probs = text_clf.predict_proba([query_text])[0]
        classes = text_clf.classes_
        child_text_prob = text_probs[np.where(classes == "Child")[0][0]]
    else:
        # Fallback keyword analyzer
        child_keywords = ["minecraft", "roblox", "kids", "toy", "cartoon", "baby", "rhymes", "fun", "game", "dinosaur"]
        query_text = " ".join(session_queries).lower() if session_queries else "normal browse"
        hits = sum(1 for w in child_keywords if w in query_text)
        child_text_prob = min(hits * 0.35, 1.0)

    # 2. Evaluate video retention
    # retention = duration_watched / total_duration
    avg_gk_ret = np.mean([w["duration_watched"] / w["total_duration"] for w in gk_watches]) if gk_watches else 0.0
    avg_adult_ret = np.mean([w["duration_watched"] / w["total_duration"] for w in adult_watches]) if adult_watches else 0.0

    # Combine signals (40% searches, 60% watch retention bias)
    fused_child_score = child_text_prob * 0.4 + (avg_gk_ret - avg_adult_ret + 1.0) / 2.0 * 0.6

    prediction = "Child" if fused_child_score > 0.5 else "Not a Child"
    return prediction, fused_child_score

if __name__ == "__main__":
    # Test face detection & behavior
    dummy_child_face = np.ones((128, 128, 3), dtype=np.uint8) * 240
    cv2.ellipse(dummy_child_face, (64, 64), (45, 45), 0, 0, 360, (255, 200, 180), -1)
    
    pred_face, prob_face = estimate_age_from_face(dummy_child_face)
    print(f"Face Classifier -> Pred: {pred_face}, Confidence: {prob_face:.2%}")

    queries = ["minecraft videos", "dinosaur stories for kids"]
    gk = [{"duration_watched": 50, "total_duration": 60}]
    adult = [{"duration_watched": 5, "total_duration": 100}]
    pred_behav, prob_behav = estimate_age_from_behavior(queries, gk, adult)
    print(f"Behavioral Classifier -> Pred: {pred_behav}, Confidence: {prob_behav:.2%}")
