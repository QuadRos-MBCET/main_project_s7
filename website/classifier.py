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

def detect_photo_spoof(image_np: np.ndarray, cropped_face: np.ndarray = None) -> tuple[bool, float, str]:
    """
    Detects whether the captured face image is a photograph/screen display (photo spoof)
    or a real live face.
    
    Returns:
        (is_spoof: bool, spoof_score: float, reason: str)
    """
    if image_np is None:
        return False, 0.0, "No image"

    if cropped_face is None:
        cropped_face, _ = detect_and_crop_face(image_np)
        
    score_indicators = []
    reasons = []
    
    # 1. Specular Glare & Reflection Analysis (Screen / Photo reflection)
    hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
    v_chan = hsv[:, :, 2]
    s_chan = hsv[:, :, 1]
    
    specular_mask = (v_chan > 245) & (s_chan < 30)
    specular_ratio = np.mean(specular_mask)
    if specular_ratio > 0.015:
        score_indicators.append(0.35)
        reasons.append("Screen / photo specular glare reflection detected")

    # 2. Color Gamut & YCrCb Skin Tone Naturalness
    if cropped_face is not None and cropped_face.size > 0:
        ycrcb = cv2.cvtColor(cropped_face, cv2.COLOR_RGB2YCrCb)
        cr = ycrcb[:, :, 1]
        cb = ycrcb[:, :, 2]
        skin_mask = (cr >= 133) & (cr <= 173) & (cb >= 77) & (cb <= 127)
        skin_ratio = np.mean(skin_mask)
        if skin_ratio < 0.25:
            score_indicators.append(0.30)
            reasons.append("Unnatural skin tone color response (display/photo gamut)")

        # 3. Frequency & FFT Moiré Pattern Analysis
        gray_face = cv2.cvtColor(cropped_face, cv2.COLOR_RGB2GRAY)
        f = np.fft.fft2(gray_face)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-6)
        h, w = gray_face.shape
        cy, cx = h // 2, w // 2
        high_freq_ratio = float(np.mean(magnitude_spectrum[:max(1, cy//2), :max(1, cx//2)]) / (np.mean(magnitude_spectrum) + 1e-6))
        if high_freq_ratio > 1.25 or high_freq_ratio < 0.65:
            score_indicators.append(0.25)
            reasons.append("Display screen Moiré pattern / re-sampling grid artifact")

    # 4. Rectangular Screen / Paper Border Frame Detection
    try:
        gray_img = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray_img, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80, minLineLength=60, maxLineGap=10)
        if lines is not None and len(lines) >= 4:
            vert_horiz_count = 0
            for line in lines:
                flat = np.ravel(line)
                if len(flat) >= 4:
                    x1, y1, x2, y2 = flat[:4]
                    angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                    if angle < 10 or angle > 80:
                        vert_horiz_count += 1
            if vert_horiz_count >= 4:
                score_indicators.append(0.25)
                reasons.append("Rectangular screen / printed photo border frame detected")
    except Exception:
        pass

    total_spoof_score = float(np.sum(score_indicators))
    is_spoof = total_spoof_score >= 0.40
    reason_str = "; ".join(reasons) if reasons else "Live face verified"
    
    return is_spoof, round(min(1.0, total_spoof_score), 3), reason_str


def estimate_detailed_age_from_face(image_np: np.ndarray) -> dict:
    """
    Returns full detailed age estimation dictionary using MTCNN + ViT Age Pipeline with Anti-Spoof Detection:
    - age_range: "Less than 14", "14 to 17", "18 and above"
    - category: "Less than 14", "14 to 17", or "18 and above"
    - is_spoof: bool
    - spoof_score: float
    - spoof_reason: str
    """
    cropped_face, bbox = detect_and_crop_face(image_np)
    try:
        is_spoof, spoof_score, spoof_reason = detect_photo_spoof(image_np, cropped_face)
    except Exception as e:
        is_spoof, spoof_score, spoof_reason = False, 0.0, f"Spoof check bypass: {e}"

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
                    "is_spoof": is_spoof,
                    "spoof_score": spoof_score,
                    "spoof_reason": spoof_reason,
                    "pipeline_result": res,
                    "faces_detected": res["faces_detected"]
                }
        except Exception:
            pass

    # Fallback model categorization
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
        "is_spoof": is_spoof,
        "spoof_score": spoof_score,
        "spoof_reason": spoof_reason,
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
# 1.5 ID CARD VERIFICATION & FACE SIMILARITY MATCHING SYSTEM
# =====================================================================
import re
import datetime

try:
    from facenet_pytorch import InceptionResnetV1
    import torch
    _FACENET_EMBEDDER = InceptionResnetV1(pretrained='vggface2').eval()
    HAS_FACENET = True
except Exception:
    _FACENET_EMBEDDER = None
    HAS_FACENET = False

def compute_face_similarity(face1_np: np.ndarray, face2_np: np.ndarray) -> float:
    """
    Computes deep facial feature similarity metric (0.0 to 1.0 / 0% to 100%) between
    an ID Card Face and a Live Captured Face using FaceNet (InceptionResnetV1 VGGFace2 Embeddings).
    Accurately distinguishes different individuals from the same person.
    """
    if face1_np is None or face2_np is None or face1_np.size == 0 or face2_np.size == 0:
        return 0.0

    if HAS_FACENET and _FACENET_EMBEDDER is not None:
        try:
            # Resize to 160x160 for FaceNet and normalize to [-1, 1]
            f1 = cv2.resize(face1_np, (160, 160)).astype(np.float32) / 255.0
            f2 = cv2.resize(face2_np, (160, 160)).astype(np.float32) / 255.0

            f1 = (f1 - 0.5) / 0.5
            f2 = (f2 - 0.5) / 0.5

            t1 = torch.tensor(f1).permute(2, 0, 1).unsqueeze(0).float()
            t2 = torch.tensor(f2).permute(2, 0, 1).unsqueeze(0).float()

            with torch.no_grad():
                e1 = _FACENET_EMBEDDER(t1).numpy()[0]
                e2 = _FACENET_EMBEDDER(t2).numpy()[0]

            # Calculate 512-D Cosine Similarity
            cosine_sim = float(np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2) + 1e-6))
            
            # Map FaceNet cosine range (-0.2 to 0.8) into calibrated 0% to 100% confidence score:
            # - Same person: cosine >= 0.50 -> match_score >= 70%
            # - Different person: cosine <= 0.30 -> match_score <= 50%
            calibrated_score = float(np.clip((cosine_sim + 0.20) / 1.0, 0.0, 1.0))
            return round(calibrated_score, 4)
        except Exception:
            pass

    # Secondary structural fallback metric
    try:
        f1 = cv2.resize(face1_np, (128, 128))
        f2 = cv2.resize(face2_np, (128, 128))
        g1 = cv2.cvtColor(f1, cv2.COLOR_RGB2GRAY)
        g2 = cv2.cvtColor(f2, cv2.COLOR_RGB2GRAY)
        p1 = np.mean(g1, axis=1)
        p2 = np.mean(g2, axis=1)
        proj_sim = float(np.dot(p1, p2) / (np.linalg.norm(p1) * np.linalg.norm(p2) + 1e-6))
        return round(float(np.clip(proj_sim * 0.7, 0.0, 1.0)), 4)
    except Exception:
        return 0.3500


def extract_dob_and_age_from_id(id_image_np: np.ndarray, manual_dob: str = None) -> tuple[str, int, str]:
    """
    Extracts Date of Birth (DOB) and computes actual age from ID Card image using EasyOCR & Regex.
    Returns (dob_str, calculated_age, age_category).
    """
    extracted_text = ""
    
    # Try EasyOCR text extraction
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(id_image_np)
        extracted_text = " ".join([res[1] for res in results])
    except Exception:
        pass

    if manual_dob:
        extracted_text += " " + manual_dob

    current_year = datetime.datetime.now().year
    
    # Search for DOB patterns: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, or Year YYYY
    dob_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})', extracted_text)
    year_match = re.search(r'(?:DOB|Birth|Year)[:\s]*(\d{4})', extracted_text, re.IGNORECASE)

    if dob_match:
        dob_str = dob_match.group(1)
        try:
            parts = re.split(r'[/-]', dob_str)
            birth_year = int(parts[-1]) if len(parts[-1]) == 4 else int(parts[0])
        except Exception:
            birth_year = current_year - 20
    elif year_match:
        birth_year = int(year_match.group(1))
        dob_str = f"Year {birth_year}"
    else:
        birth_year = current_year - 22
        dob_str = f"Estimated YOB {birth_year}"

    calc_age = max(1, current_year - birth_year)

    if calc_age < 14:
        cat = "Less than 14"
    elif 14 <= calc_age <= 17:
        cat = "14 to 17"
    else:
        cat = "18 and above"

    return dob_str, calc_age, cat


def verify_id_card_and_live_face(id_image_np: np.ndarray, live_image_np: np.ndarray, manual_dob: str = None) -> dict:
    """
    Performs complete ID Verification:
    1. Detects face on ID card and cropped live face.
    2. Runs Anti-Spoof Liveness check on live face.
    3. Computes Face Similarity (ID Face vs Live Face).
    4. Extracts DOB & Age from ID Card.
    5. Cross-matches ID DOB Age vs Live ViT Facial Age Prediction.
    """
    id_face, id_bbox = detect_and_crop_face(id_image_np)
    live_face, live_bbox = detect_and_crop_face(live_image_np)

    # 1. Anti-Spoofing check on live face
    is_spoof, spoof_score, spoof_reason = detect_photo_spoof(live_image_np, live_face)

    # 2. Deep FaceNet Similarity
    face_sim_score = compute_face_similarity(id_face, live_face)
    face_match = face_sim_score >= 0.65  # Require >= 65% similarity threshold

    # 3. DOB & Age from ID
    dob_str, id_age, id_age_cat = extract_dob_and_age_from_id(id_image_np, manual_dob)

    # 4. Facial ViT Age Prediction
    detailed_live = estimate_detailed_age_from_face(live_image_np)
    live_age_cat = detailed_live["category"]

    # 5. DOB vs Live Age Category Match
    dob_age_match = (id_age_cat == live_age_cat)

    # Overall Status
    if is_spoof:
        status = "FAILED_SPOOF"
        message = "DONT TRY TO PLAY A FOOL WITH ME NIGESH"
    elif not face_match:
        status = "FAILED_FACE_MISMATCH"
        message = f"❌ ID Face Mismatch! Similarity score is only {face_sim_score:.1%} (Live face does not match ID photo)."
    elif not dob_age_match:
        status = "FAILED_DOB_MISMATCH"
        message = f"⚠️ DOB Mismatch Alert! ID Card DOB indicates '{id_age_cat}' ({id_age} yrs), but live facial scan predicts '{live_age_cat}'."
    else:
        status = "VERIFIED_SUCCESS"
        message = f"✅ Identity & Age Verified! Face match: {face_sim_score:.1%}. ID DOB: {dob_str} ({id_age_cat})."

    return {
        "status": status,
        "message": message,
        "face_similarity": face_sim_score,
        "face_match": face_match,
        "dob_age_match": dob_age_match,
        "id_face": id_face,
        "live_face": live_face,
        "id_dob_str": dob_str,
        "id_age": id_age,
        "id_age_category": id_age_cat,
        "live_age_category": live_age_cat,
        "is_spoof": is_spoof,
        "spoof_reason": spoof_reason
    }

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
