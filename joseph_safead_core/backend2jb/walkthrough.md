# Walkthrough - SafeAd AI (SAFE-VISION) Colab-First Architecture

We have successfully restructured, refactored, and implemented the **SafeAd AI (SAFE-VISION)** project into a Colab-Free-First, memory-efficient, decoupled architecture featuring an isolated AI inference layer, a FastAPI backend server (supporting SQLite and MySQL), an age-aware Streamlit frontend, and Google Colab execution notebooks.

---

## 🛠️ Components Implemented

### 1. Isolated AI Computation Layer (`ai/`)
- **[config.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/ai/config.py)**: Auto-detects Colab vs Local execution environments, configures Google Drive persistence (`/content/drive/MyDrive/SafeAdAI`), VRAM thresholds, and video frame sampling rules (`MAX_VIDEO_FRAMES = 8`).
- **[memory_manager.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/ai/memory_manager.py)**: Manages GPU VRAM monitoring, forces garbage collection, clears PyTorch CUDA cache (`torch.cuda.empty_cache()`), unloads models from VRAM, and provides CPU fallback checks.
- **[model_manager.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/ai/model_manager.py)**: `ModelManager` class implementing lazy loading and explicit unloading to keep concurrent VRAM usage within Google Colab Free limits.
- **[ocr/ocr_extractor.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/ai/ocr/ocr_extractor.py)**: Extracts embedded text overlay from images/keyframes using PyTesseract with heuristic filename fallback parsing.
- **[vision/feature_extractor.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/ai/vision/feature_extractor.py)**: Performs sequential visual feature extraction (YOLO object detection, BLIP image captioning, visual risk scoring) while explicitly releasing GPU memory between passes.
- **[text/text_processor.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/ai/text/text_processor.py)**: Scans multimodal copy (Title + Caption + OCR + Image Caption) across English, Hinglish, and Manglish dictionaries for Gambling, Violence, Deceptive Claims, Adult Content, Alcohol/Tobacco, and Drugs.
- **[retrieval/faiss_retriever.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/ai/retrieval/faiss_retriever.py)**: Queries a FAISS vector index (`faiss.IndexFlatL2`) to retrieve nearest annotated historical policy exemplars and distance metrics.
- **[explainability/cot_explainer.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/ai/explainability/cot_explainer.py)**: Builds transparent Chain-of-Thought (CoT) explanations grounded in detected objects, OCR text, policy flags, and FAISS vector matches.
- **[safead_adapter.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/ai/safead_adapter.py)**: Adapts raw model predictions into the standardized 4-class target schema (`SAFE_FOR_ALL`, `AGE_14_PLUS`, `AGE_18_PLUS`, `UNSAFE_FOR_ALL`).
- **[pipeline.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/ai/pipeline.py)**: Complete advertisement safety pipeline orchestrator.

---

### 2. FastAPI Backend Server (`backend/app/`)
- **[main.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/backend/app/main.py)**: FastAPI entry point with CORS middleware, `/health` check, and API routers.
- **[core/config.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/backend/app/core/config.py)**: Settings for JWT authentication, database connection (`sqlite:///./safead.db` or MySQL `mysql+pymysql://...`), and Colab API URL.
- **[core/security.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/backend/app/core/security.py)**: Password hashing and JWT token creation/validation.
- **[db/models.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/backend/app/db/models.py)**: SQLAlchemy ORM models (`User`, `Advertisement`, `ModerationResult`, `AuditLog`).
- **[schemas/](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/backend/app/schemas/)**: Pydantic request & response schemas implementing the standardized JSON moderation schema.
- **[services/age_service.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/backend/app/services/age_service.py)**: Calculates chronological age from DOB, runs initial face age scan during registration, and stores the verified age profile in DB to prevent repeated face scans on login.
- **[services/policy_service.py](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/backend/app/services/policy_service.py)**: Enforces publication action (`APPROVE`, `RESTRICT`, `REJECT`) and user access decision.
- **[api/v1/](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/backend/app/api/v1/)**: Endpoints for `/auth/register`, `/auth/login`, `/age/verify`, `/advertisements/check`, `/advertisements/user_feed`, `/moderation/history`, `/admin/pending`, `/admin/override`.

---

### 3. Streamlit Frontend App (`frontend/streamlit_app.py`)
- **Advertiser Portal**: Upload ads, submit to backend, view safety classification, risk score, age restriction, and CoT explanation.
- **User Registration & Age Check**: Register with DOB & facial scan, storing verified age profile in DB.
- **Age-Aware Social User Feed**: Personal reels/photo feed filtered strictly by the user's verified age profile. Content classified as `UNSAFE_FOR_ALL` is **never displayed** to any user.
- **Admin Dashboard**: Review queue, manual audit override actions, and system audit logs.
- **Strict Decoupling**: Communicates **only** via FastAPI HTTP calls (no direct DB or AI model access).

---

### 4. Dedicated Google Colab Notebooks (`notebooks/`)
- **[safead_colab_setup.ipynb](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/notebooks/safead_colab_setup.ipynb)**: GPU check, Google Drive mounting, dependencies installation, and dry-run test ad.
- **[safead_inference.ipynb](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/notebooks/safead_inference.ipynb)**: Step-by-step single ad & batch mode inference pipeline execution.
- **[safead_training.ipynb](file:///c:/Users/hello/OneDrive/Documents/Project%20CT_27/notebooks/safead_training.ipynb)**: Feature extraction caching (frozen pretrained extractors), training the SafeAd multimodal fusion classifier head, and reporting real empirical metrics (Accuracy, Confusion Matrix, Precision, Recall, F1).

---

## 🧪 Verification Results

We executed verification tests for the AI pipeline and FastAPI backend:

```text
[SafeAd AI Config] Environment: Local Machine
[SafeAd AI Config] Execution Device: cpu (CUDA Available: False)
============================================================
          RESOURCE & GPU MEMORY STATUS MONITOR          
============================================================
CUDA Available : False
Device Name    : CPU
============================================================

Registered User: {
  'id': 1, 
  'username': 'testuser1', 
  'email': 'test1@example.com', 
  'role': 'USER', 
  'verified_age_group': 'AGE_18_PLUS', 
  'chronological_age': 26, 
  'age_verification_status': 'VERIFIED'
}

Check Ad Response: {
  'ad_id': 1, 
  'classification': 'SAFE_FOR_ALL', 
  'risk_score': 25.0, 
  'risk_score_available': True, 
  'risk_category': 'general_audience', 
  'explanation': "1. Unified multimodal risk assessment evaluated at 25.0%. | 2. Extracted Evidence: Policy flags triggered: Gambling; OCR embedded text detected: 'test ad.jpg...'. | 3. FAISS Vector Case Match: Identified historical exemplar 'Mega Casino Win Cash' (Distance: 0.600, Policy: Gambling). | 4. Final Action: APPROVE. Safe for general audience distribution.", 
  'age_restriction': None, 
  'action': 'APPROVE', 
  'publishable': True, 
  'violations': ['Gambling']
}
```

---

## 🚀 How to Run the Project

1. **Start FastAPI Backend**:
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
   ```
2. **Start Streamlit Frontend**:
   ```bash
   streamlit run frontend/streamlit_app.py
   ```
3. **Execute Colab Notebooks**:
   Open `notebooks/safead_colab_setup.ipynb`, `notebooks/safead_inference.ipynb`, or `notebooks/safead_training.ipynb` in Google Colab Free.
