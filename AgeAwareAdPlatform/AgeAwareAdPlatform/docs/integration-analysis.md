# Integration Analysis: Age-Aware Advertisement Moderation & Delivery Platform

**Document Path**: `docs/integration-analysis.md`  
**Source Repositories**:
1. *Advertisement Moderation Backend*: `https://github.com/QuadRos-MBCET/main_project_s7/tree/backend2jb`
2. *Face / Age Estimation Software*: `https://github.com/QuadRos-MBCET/main_project_s7/tree/feature/face-age-estimation`

---

## 1. Advertisement Backend Architecture

### Core Architecture & Framework
The advertisement moderation system is built in Python 3.10+ using **FastAPI** as the primary REST application server, with **SQLAlchemy ORM** managing relational persistence and **Pydantic v2 / pydantic_settings** governing request and response schemas.

The system is designed with an AI client dispatch layer (`backend/app/services/ai_client_service.py`):
1. **Remote Colab GPU Inference Server**: If an external GPU worker URL is provided via the `COLAB_API_URL` environment variable, the service tests endpoint liveness (`GET /health`) and offloads inference to the remote Colab server (`POST /predict`).
2. **Local Multi-Modal Pipeline Fallback**: If no Colab server is configured or if the remote ping fails, the service falls back gracefully to the local AI engine (`ai.pipeline.run_safead_inference`), which utilizes multi-modal safety evaluation modules with CPU fallback.
3. **Fail-Closed Security Guarantee**: If a critical processing failure or exception occurs during model execution, the service **never fails open**. It strictly yields `classification="UNSAFE_FOR_ALL"` and `publication_action="REJECT"`.

### Key AI/ML Models
- **Visual Safety**: `meta-llama/Llama-Guard-3-11B-Vision`
- **Adult / NSFW**: `Falconsai/nsfw_image_detection` Vision Transformer + HSV/YCbCr chrominance skin pixel ratio heuristic
- **Video Violence**: Pretrained `MCG-NJU/videomae-base-finetuned-kinetics` (VideoMAE)
- **OCR Text Extraction**: PP-OCR / PaddleOCR text detection & recognition
- **Audio Extraction & Speech-to-Text**: `openai/whisper-small` / `whisper-base`
- **Text Safety Guardrail**: `meta-llama/Llama-Guard-3-1B`
- **SafeAd Fusion Engine**: Deterministic `SafeAdFusion` combining modality risks into a 0–100 fused risk score with threshold-based policy determinations.

---

## 2. Face-Age Software Architecture

### Core Architecture & Framework
The face detection and age estimation software is implemented in Python and exists in two complementary forms within `feature/face-age-estimation`:
1. **Live Camera Application (`camera_app.py`)**: A multithreaded real-time tracking application running OpenCV `cv2.VideoCapture(0)` on the main thread and offloading inference asynchronously to a worker thread running `FaceAgePipeline`.
2. **Web / Streamlit Modules (`website/face_age_app.py` & `website/classifier.py`)**: Web-compatible facial capture (`st.camera_input` / HTML5 WebRTC canvas) passing image frames to `estimate_detailed_age_from_face()`.

### Computer Vision & Model Pipeline
- **Face Detection**:
  - Primary: MTCNN (`facenet-pytorch`) returning bounding box coordinates `[x1, y1, x2, y2]` and detection probability.
  - Secondary / Fallback: OpenCV Haar Cascade Classifier (`haarcascade_frontalface_default.xml`) with multi-scale passes.
- **Age Classification**:
  - Primary: HuggingFace Vision Transformer `nateraw/vit-age-classifier` returning logits across age brackets (`0-2`, `3-9`, `10-19`, `20-29`, `30-39`, `40-49`, `50-59`, `60-69`, `more than 70`).
  - Fallback: Pre-trained Scikit-Learn `MLPClassifier` trained on geometric facial features (aspect ratio, facial roundness, 10-bin vertical projection histogram).
- **Anti-Spoofing & Liveness Guardrails**:
  - Specular glare reflection detection (HSV V-channel saturation).
  - Skin tone naturalness analysis (YCrCb Cr/Cb gamut response).
  - 2D FFT Frequency & Moiré pattern analysis to detect screen re-sampling grids.
  - Canny edge + Hough line analysis to detect rectangular display or photo paper frames.
- **Post-Registration Behavior**:
  - The camera is activated **strictly during registration**. Once a valid face frame is classified into an age category, the camera stream is halted immediately. No continuous video tracking is performed during regular feed browsing.

---

## 3. Existing APIs and Endpoints

### Authentication & User Management
- `POST /api/v1/auth/register`:
  - **Body**: `{"username": str, "email": str, "password": str, "date_of_birth": "YYYY-MM-DD"}`
  - **Action**: Registers user, performs DOB verification, hashes password via bcrypt, stores user record.
  - **Returns**: `UserResponse` (`id`, `username`, `email`, `role`, `verified_age_group`, `chronological_age`, `age_verification_status`).
- `POST /api/v1/auth/login`:
  - **Body**: `{"username": str, "password": str}`
  - **Returns**: JWT Bearer token, `user_id`, `username`, `role`, `verified_age_group`.

### Age Verification
- `POST /api/v1/age/verify`:
  - **Body**: `{"user_id": int, "date_of_birth": "YYYY-MM-DD", "face_image_base64": Optional[str]}`
  - **Action**: Invokes `AgeVerificationService.verify_user_age()` with facial image input, persists calculated `verified_age_group`, `estimated_age`, `chronological_age`, and confidence in DB.
  - **Returns**: Updated `UserResponse`.

### Advertisement Moderation
- `POST /api/v1/advertisements/check` / `POST /api/v1/moderation/moderate`:
  - **Form Data**: `file` (Binary), `title` (str), `caption` (str), `user_id` (int).
  - **Action**: Saves media to upload directory, runs multi-modal AI moderation, generates deterministic risk score and safety classification, records `Advertisement`, `ModerationResult`, and `AuditLog`.
  - **Returns**: `StandardizedModerationResponse`.
- `GET /api/v1/moderation/{id}`:
  - **Returns**: Detailed moderation results, evidence matrix, and classification for given Ad ID.
- `GET /api/v1/moderation/history`:
  - **Returns**: Recent moderation results with evidence dictionaries.
- `GET /api/v1/moderation/logs`:
  - **Returns**: Immutable audit trail entries.

### Admin & Human Review (HITL)
- `GET /api/v1/admin/pending`:
  - **Returns**: Advertisements in `HUMAN_REVIEW`, `PENDING`, or `RESTRICT` status.
- `POST /api/v1/admin/override`:
  - **Body**: `{"ad_id": int, "action": "APPROVE"|"AGE_RESTRICT"|"REJECT", "final_classification": "SAFE_FOR_ALL"|"SAFE_14_PLUS"|"SAFE_18_PLUS"|"UNSAFE_FOR_ALL", "moderator_notes": str}`
  - **Action**: Sets `ModerationResult.is_human_reviewed = True`, updates `final_classification` and `status`, appends moderator notes, and records an audit log entry.
  - **Returns**: `{"status": "success", "ad_id": int, "new_action": str, "final_classification": str}`.

### Ad Delivery & Social Feed
- `GET /api/v1/advertisements/user_feed?user_age_group={group}`:
  - **Parameters**: `user_age_group` (`UNDER_14`, `AGE_14_TO_17`, `AGE_18_PLUS`).
  - **Action**: Queries non-rejected advertisements whose `final_classification` satisfies `PolicyService.evaluate_user_access`.
  - **Returns**: Filtered list of eligible advertisement payloads.

---

## 4. Existing Data Structures

### SQLAlchemy ORM Models (`backend/app/db/models.py`)
1. **`User`**:
   - `id`: Integer primary key
   - `username`: String(50), unique, indexed
   - `email`: String(100), unique, indexed
   - `password_hash`: String(255)
   - `date_of_birth`: DateTime
   - `age_verification_status`: String(50) (e.g., `VERIFIED`, `CONFLICT_FLAGGED`)
   - `verified_age_group`: Enum (`UNDER_14`, `AGE_14_TO_17`, `AGE_18_PLUS`)
   - `estimated_age`: Float
   - `chronological_age`: Integer
   - `age_difference`: Float
   - `age_confidence`: Float
   - `role`: Enum (`USER`, `MODERATOR`, `ADMIN`)
   - `is_active`: Boolean
   - `created_at`: DateTime
2. **`Advertisement`**:
   - `id`: Integer primary key
   - `title`: String(255)
   - `caption`: Text
   - `file_path`: String(255)
   - `media_type`: String(50) (`image` or `video`)
   - `status`: String(50) (`PENDING`, `APPROVE`, `AGE_RESTRICT`, `REJECT`, `HUMAN_REVIEW`)
   - `owner_id`: Integer foreign key -> `users.id`
   - `created_at`: DateTime
3. **`ModerationResult`**:
   - `id`: Integer primary key
   - `advertisement_id`: Integer foreign key -> `advertisements.id`, unique
   - `model_version`: String(100)
   - `classification`: Enum (`SAFE_FOR_ALL`, `SAFE_14_PLUS`, `SAFE_18_PLUS`, `UNSAFE_FOR_ALL`, `REQUIRES_HUMAN_REVIEW`)
   - `risk_category`: String(100)
   - `risk_score`: Float (0.0 to 100.0)
   - `confidence`: Float (0.0 to 1.0)
   - `explanation`: Text
   - `evidence`: Text (JSON string containing multi-modal telemetry)
   - `moderation_action`: Enum (`APPROVE`, `AGE_RESTRICT`, `REJECT`, `HUMAN_REVIEW`)
   - `age_restriction`: Integer (e.g., 14, 18, or null)
   - `publishable`: Boolean
   - `is_human_reviewed`: Boolean
   - `moderator_id`: Integer foreign key -> `users.id`
   - `moderator_notes`: Text
   - `processing_time_seconds`: Float
   - `created_at`, `completed_at`: DateTime
4. **`AuditLog`**:
   - `id`: Integer primary key
   - `ad_id`: Integer foreign key -> `advertisements.id`
   - `user_id`: Integer foreign key -> `users.id`
   - `action`: String(100)
   - `details`: Text
   - `timestamp`: DateTime

---

## 5. Advertisement Classification Output Mapping

| Backend Internal Enum | Fused Action Badge | Application / UI Display Label | Ad Delivery Eligibility | Rejection Status |
| :--- | :--- | :--- | :--- | :--- |
| `SAFE_FOR_ALL` | `APPROVE — SAFE FOR ALL` | **SAFE FOR ALL** | All users (`UNDER_14`, `14+`, `18+`) | Approved |
| `SAFE_14_PLUS` | `AGE RESTRICTED — 14+` | **14+** | Users `14-17` and `18+` only | Approved (Restricted) |
| `SAFE_18_PLUS` | `AGE RESTRICTED — 18+` | **18+** | Users `18+` only | Approved (Restricted) |
| `UNSAFE_FOR_ALL` | `REJECT — UNSAFE FOR ALL` | **UNSAFE FOR ALL** | **NEVER DELIVERED TO ANY USER** | **STRICTLY REJECTED** |
| `REQUIRES_HUMAN_REVIEW` | `MODERATOR QUEUED` | **PENDING HUMAN REVIEW** | Blocked until human decision | Queued for Review |

---

## 6. Age Estimation Output Mapping

| ViT Label Range / Model Output | Estimated Age (Midpoint) | Normalized Category | User Account Group | Delivered Ad Categories |
| :--- | :--- | :--- | :--- | :--- |
| `0-2`, `3-9` | `< 14` (e.g., 7.0) | `LESS THAN 14` | `UNDER_14` (`SAFE FOR ALL`) | Only `SAFE FOR ALL` ads |
| `10-19` | `14-17` (e.g., 15.5) | `14 TO 17` | `AGE_14_TO_17` (`14+`) | `SAFE FOR ALL` + `14+` ads |
| `20-29`, `30-39`, `40+` | `18+` (e.g., 25.0) | `18 AND ABOVE` | `AGE_18_PLUS` (`18+`) | `SAFE FOR ALL` + `14+` + `18+` ads |

### Anomaly / Edge Case Handling
1. **0 Faces Detected**: Returns `"faces_detected": 0`. The registration flow displays an alert and prompts the user to position their face clearly in frame. Registration cannot proceed without a valid face scan.
2. **Multiple Faces Detected**: Returns `"faces_detected": > 1`. The flow triggers `"Multiple faces detected"`, requiring a single user for verification.
3. **Photo Spoof Detected**: If screen glare, unnatural gamut, or Moiré patterns exceed thresholds (`spoof_score >= 0.40`), spoof warning is raised.

---

## 7. Authentication Flow

```
[ User / Advertiser / Reviewer ]
             |
    POST /api/v1/auth/login
             |
    Verify bcrypt password hash
             |
    Generate JWT Token (HS256)
             |
    Return { access_token, user_id, username, role, verified_age_group }
             |
[ Client stores token & verified_age_group in session ]
```

On subsequent requests:
- Bearer token is passed via `Authorization: Bearer <token>`.
- Client role and saved age group determine portal access and feed filtering.

---

## 8. Database and Storage Architecture

- **Primary Database**: SQLite file `safead.db` (or MySQL configured via `DATABASE_URL`).
- **Media File Storage**: Local filesystem directory `uploads/` storing submitted image and video advertisements with timestamps to prevent naming collisions.
- **Privacy Design**:
  - User camera frames are processed in-memory during registration to extract face landmarks and predict age.
  - Raw camera frames are **not saved permanently** to disk or database. Only the derived `verified_age_group`, `estimated_age`, and verification status are persisted.

---

## 9. Required Environment Variables

```bash
# Core Settings
PROJECT_NAME="Age-Aware Advertisement Platform"
API_V1_STR="/api/v1"
SECRET_KEY="safead_ai_jwt_secret_key_change_in_production_2026"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database Connection
DATABASE_URL="sqlite:///./safead.db"

# Remote AI Acceleration (Optional - local fallback automatically used if blank)
COLAB_API_URL=""

# Server Ports
BACKEND_HOST="127.0.0.1"
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

---

## 10. Integration Points & Adapters

1. **`FaceAgeAdapter` (`camera-integration/face_age_adapter.py`)**:
   - Bridges the web registration frontend with the MTCNN/ViT pipeline and Haar Cascade + anti-spoof fallback.
   - Takes a Base64-encoded image or canvas snapshot, performs face detection, anti-spoofing check, and age classification, returning standardized payload:
     `{"success": bool, "faces_detected": int, "estimated_age": float, "age_category": str, "confidence": float, "is_spoof": bool}`.
2. **`AdDeliveryService` (`services/ad_delivery_service.py`)**:
   - Implements the strict age-matching policy. Queries the database for advertisements where `status != 'REJECT'` and `is_publishable = True`.
   - Compares the advertisement's `final_classification` against the user's `verified_age_group`.
   - Never exposes internal AI confidence, moderation logs, or unapproved ads to the user feed.
3. **`ReviewService` (`services/review_service.py`)**:
   - Exposes HITL moderation methods for the Reviewer Portal.
   - Handles the human override workflow: sets `is_human_reviewed = True`, updates `final_classification`, records moderator notes, and generates an audit log record.

---

## 11. Data Flow Between Systems

```
[ ADVERTISER ]
      |
      | 1. Upload Ad (Media + Title + Caption)
      v
[ FASTAPI BACKEND: /api/v1/advertisements/check ]
      |
      | 2. Execute Multi-Modal AI Moderation
      v
[ SAFEAD AI PIPELINE (Visual + Video + OCR + Speech + Fusion) ]
      |
      | 3. Raw Classification (SAFE_FOR_ALL / SAFE_14_PLUS / SAFE_18_PLUS / UNSAFE_FOR_ALL)
      v
[ ADVERTISER PORTAL ]
      |
      |-- A. Advertiser Accepts --> Status: APPROVED (or AGE_RESTRICT)
      |
      \-- B. Advertiser Disputes --> Status: HUMAN_REVIEW (Queued)
                                           |
                                           v
                             [ HUMAN REVIEWER PORTAL ]
                                           |
                                           | Overrides classification
                                           v
                             [ FINAL CLASSIFICATION STORED ]
                                           |
                                           +---------------------------------+
                                                                             |
[ USER REGISTRATION ]                                                        |
      |                                                                      |
      | Camera Snapshot (Single Frame)                                        |
      v                                                                      |
[ FACE-AGE ADAPTER (MTCNN/ViT + Anti-Spoof) ]                                |
      |                                                                      |
      | Estimated Age & Category (SAFE FOR ALL / 14+ / 18+)                  |
      v                                                                      |
[ USER ACCOUNT (verified_age_group saved, Camera Stops) ]                     |
      |                                                                      |
      | User Login later (Read saved category)                                |
      v                                                                      |
[ SOCIAL FEED ("AuraFeed") ] <-----------------------------------------------+
      |
      | Request eligible sponsored ads
      v
[ AD DELIVERY SERVICE: Match (User Category, Final Ad Classification) ]
      |
      | Strict filtering:
      | - SAFE FOR ALL user -> receives SAFE FOR ALL ads only
      | - 14+ user          -> receives SAFE FOR ALL + 14+ ads
      | - 18+ user          -> receives SAFE FOR ALL + 14+ + 18+ ads
      | - UNSAFE FOR ALL    -> BLOCKED FOR EVERYONE
      v
[ SPONSORED ADS IN FEED ]
```

---

## 12. Limitations & Missing Interfaces Addressed

1. **Standalone Script Integration**: `camera_app.py` in the face-age branch was designed as an OpenCV GUI loop (`cv2.imshow()`). In a modern web application, camera frames are captured in the browser via WebRTC/canvas and sent to an API endpoint. We created `FaceAgeAdapter` to execute the exact same MTCNN + ViT / Haar Cascade pipeline directly on uploaded or streamed frames.
2. **Merge Conflict In Original Branch**: Branch `backend2jb` contained an unresolved git conflict in `backend/app/api/v1/moderation.py` from commit `9b64db6`. We analyzed the parent commits and restored the clean implementation from commit `712a4be`.
3. **Separation of Portals**: The prototype code had a single Streamlit script mixing advertiser and user feeds. Our new platform provides three distinct, professionally branded portals:
   - **Advertiser Portal**: Enterprise campaign manager and upload feedback.
   - **Reviewer / Admin Portal**: Operations dashboard with human review queue and override actions.
   - **AuraFeed Social Feed**: Modern consumer social media feed with natural sponsored ad insertion.
