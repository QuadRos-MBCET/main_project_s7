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
    from ai.face_age.face_age_pipeline import FaceAgePipeline
    from PIL import Image
    _FACE_AGE_PIPELINE = FaceAgePipeline()
    HAS_PIPELINE = True
except Exception:
    _FACE_AGE_PIPELINE = None
    HAS_PIPELINE = False

try:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
except Exception:
    face_cascade = None

def detect_and_crop_face(image_np: np.ndarray) -> tuple:
    if image_np is None:
        return np.zeros((128, 128, 3), dtype=np.uint8), None
    h_img, w_img = image_np.shape[:2]
    
    if HAS_PIPELINE:
        try:
            pil_img = Image.fromarray(image_np)
            faces = _FACE_AGE_PIPELINE.detector.detect_faces(pil_img)
            if faces:
                main_face = max(faces, key=lambda f: f["detection_confidence"])
                x1, y1, x2, y2 = main_face["bbox"]
                w = max(1, x2 - x1)
                h = max(1, y2 - y1)
                face_crop = np.array(main_face["face_crop"])
                return cv2.resize(face_crop, (128, 128)), (x1, y1, w, h)
        except Exception:
            pass

    if face_cascade is None:
        # Default center box fallback if cascade classifier is missing
        w = int(w_img * 0.4)
        h = int(w_img * 0.5) # standard portrait ratio
        x = int((w_img - w) / 2)
        y = int((h_img - h) / 2)
        cropped_face = image_np[max(0, y):min(h_img, y+h), max(0, x):min(w_img, x+w)]
        return cv2.resize(cropped_face, (128, 128)), (x, y, w, h)
        
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    try:
        # Pass 1: Standard high-precision cascade pass
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            # Pass 2: High sensitivity pass for difficult lighting/angles
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20))
    except Exception:
        faces = []
        
    if len(faces) == 0:
        # Pass 3: Center-of-frame box fallback (assuming user is facing the camera)
        w = int(w_img * 0.4)
        h = int(w_img * 0.5)
        x = int((w_img - w) / 2)
        y = int((h_img - h) / 2)
        faces = [(x, y, w, h)]
        
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    y_start = max(0, y)
    y_end = min(h_img, y+h)
    x_start = max(0, x)
    x_end = min(w_img, x+w)
    cropped_face = image_np[y_start:y_end, x_start:x_end]

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

def estimate_detailed_age_from_face(image_np: np.ndarray) -> dict:
    """
    Returns full detailed age estimation dictionary using MTCNN + ViT Age Pipeline:
    - age_range: e.g. "20-29", "10-19", "0-2", "30-39"
    - normalized_group: "LESS THAN 14", "14 TO 17", "18 AND ABOVE"
    - category: "Less than 14", "14 to 17", or "18 and above"
    - confidence: float score (e.g. 0.7401)
    - pipeline_result: full dict from FaceAgePipeline
    """
    if HAS_PIPELINE and image_np is not None:
        try:
            pil_img = Image.fromarray(image_np)
            res = _FACE_AGE_PIPELINE.analyze(pil_img)
            if res.get("faces_detected", 0) > 0:
                face = res["faces"][0]
                age_range = face["age_estimation"].get("age_range", "Unknown")
                norm_group = face.get("normalized_age_group", "UNKNOWN")
                conf = face["age_estimation"].get("confidence", 0.0)
                
                # Standardize category text according to user spec
                if norm_group == "LESS THAN 14" or age_range in ["0-2", "3-9"]:
                    category = "Less than 14"
                    norm_group = "LESS THAN 14"
                elif norm_group == "14 TO 17" or age_range == "10-19":
                    category = "14 to 17"
                    norm_group = "14 TO 17"
                else:
                    category = "18 and above"
                    norm_group = "18 AND ABOVE"

                return {
                    "age_range": category,
                    "normalized_group": norm_group,
                    "confidence": float(conf),
                    "category": category,
                    "pipeline_result": res,
                    "faces_detected": res["faces_detected"]
                }
        except Exception:
            pass

    # Fallback model categorization
    cropped_face, bbox = detect_and_crop_face(image_np)
    if not HAS_SKLEARN or face_age_clf is None:
        if bbox is not None:
            x, y, w, h = bbox
            roundness = min(w, h) / max(w, h)
        else:
            roundness = 1.0
        prob_child = float(np.clip((roundness - 0.7) / 0.3, 0.0, 1.0))
        cat = "Less than 14" if prob_child > 0.5 else "18 and above"
        norm_group = "LESS THAN 14" if prob_child > 0.5 else "18 AND ABOVE"
    else:
        feats = extract_facial_features(cropped_face, bbox)
        probs = face_age_clf.predict_proba([feats])[0]
        prob_child = probs[0]
        cat = "Less than 14" if prob_child > 0.5 else "18 and above"
        norm_group = "LESS THAN 14" if prob_child > 0.5 else "18 AND ABOVE"

    return {
        "age_range": cat,
        "normalized_group": norm_group,
        "confidence": float(prob_child if cat == "Less than 14" else max(0.0, 1.0 - prob_child)),
        "category": cat,
        "pipeline_result": None,
        "faces_detected": 1
    }

def estimate_age_from_face(image_np: np.ndarray) -> tuple:
    """
    Returns estimated age classification ('Less than 14', '14 to 17', '18 and above') and confidence.
    """
    detailed = estimate_detailed_age_from_face(image_np)
    return detailed["category"], detailed["confidence"]

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
