# Age-Aware Advertisement Moderation and Delivery Platform (SafeAd AI)

A robust, enterprise-grade trust and safety platform that bridges **SafeAd AI Multi-Modal Moderation** and **Biometric Facial Age Estimation** into an age-aware advertising and social delivery ecosystem.

---

## 1. Project Overview

Digital advertising platforms face a fundamental challenge: delivering contextually relevant advertisements while strictly preventing minors from being exposed to age-restricted (14+, 18+) or harmful (Unsafe for All) promotional content.

This platform integrates two core AI frameworks into a unified application architecture:
1. **Advertisement Moderation Backend** (`QuadRos-MBCET/main_project_s7` branch `backend2jb`): Multi-modal safety inspection evaluating visual frames, action sequences, text OCR overlays, and audio speech transcripts.
2. **Face / Age Estimation Software** (`QuadRos-MBCET/main_project_s7` branch `feature/face-age-estimation`): Real-time facial biometric landmark analysis, anti-spoofing detection, and neural age classification.

### Component Provenance
- **Existing Repositories (Upstream Source of Truth)**:
  - `SafeAd AI` multi-modal pipeline, models (`visual_safety`, `nsfw_detector`, `violence_detector`, `ocr_service`, `audio_service`, `text_safety`, `SafeAdFusion`).
  - `FaceAgePipeline` (`MTCNN`, `ViT` age classifier `nateraw/vit-age-classifier`, Haar Cascade + anti-spoofing).
- **Newly Created in `Desktop/AgeAwareAdPlatform`**:
  - Unified FastAPI backend integration with full Human-in-the-Loop (HITL) override tracking.
  - `camera-integration/face_age_adapter.py`: Production camera adapter with single-frame registration enforcement, anti-spoofing, and robust CPU fallbacks.
  - `services/`: Clean decoupled service layer (`authService`, `advertisementService`, `moderationService`, `ageRegistrationService`, `reviewService`, `adDeliveryService`, `analyticsService`).
  - Three distinct portals:
    - 🏢 **Advertiser Portal**: Enterprise ad campaign manager, upload, AI telemetry preview, dispute/review request.
    - 🛡️ **Human Reviewer Portal**: HITL moderation queue, multi-modal evidence review, and final classification override.
    - ⚙️ **Compliance Admin Console**: Real-time database metrics, audit history, system health.
    - 📸 **AuraFeed Social Feed**: Modern consumer social experience with natural, age-aware sponsored ad delivery.
    - 👤 **Registration View**: Single-use camera age verification that permanently stops camera post-registration.
    - 📐 **Architecture View**: Complete interactive documentation and delivery matrix.
  - Comprehensive automated test suite (`tests/test_suite.py`) verifying all 8 core workflows.

---

## 2. Platform Architecture

```
                                 THE TWO CORE WORKFLOWS

 [ FLOW A: ADVERTISER MODERATION ]                  [ FLOW B: USER REGISTRATION ]
                 |                                                |
                 v                                                v
          Advertiser Upload                              User Starts Registration
                 |                                                |
                 v                                                v
     FastAPI Backend (/check)                           Single Camera Snapshot
                 |                                                |
                 v                                                v
    SafeAd Multi-Modal Pipeline                         FaceAgeAdapter (MTCNN/ViT)
 (Vision + Video + OCR + Audio + Fusion)                          |
                 |                                                v
                 v                                      Estimated Age & Category
     AI Safety Classification                                     |
 (SAFE FOR ALL / 14+ / 18+ / UNSAFE)                              v
                 |                                      Save Category to User Account
        +--------+--------+                                       |
        |                 |                                       v
    [Accept]          [Dispute]                          Camera Stops Permanently
        |                 |                                       |
        |                 v                                       v
        |        Human Review Queue                            User Login
        |                 |                                       |
        |                 v                                       v
        |        Reviewer Overrides                          AuraFeed Social Feed
        |                 |                                       |
        +--------+--------+                                       v
                 |                                      Fetch Eligible Sponsored Ads
                 v                                                |
        Final Classification                                      v
                 |                                      Ad Delivery Engine
                 +-------------------------------------> [User Cat + Final Ad Cat]
                                                                  |
                                                                  v
                                                        Sponsored Ad in Feed
```

---

## 3. Four Standard Advertisement Categories & Mapping

Every advertisement in the platform is mapped to exactly one of four standardized categories:

| Backend Enum | Fused Action Badge | Application Category | Ad Delivery Rule |
| :--- | :--- | :--- | :--- |
| `SAFE_FOR_ALL` | `APPROVED — SAFE FOR ALL` | **SAFE FOR ALL** | Delivered to all users (`UNDER_14`, `14+`, `18+`) |
| `SAFE_14_PLUS` | `AGE RESTRICTED — 14+` | **14+** | Delivered to users `14+` and `18+` only |
| `SAFE_18_PLUS` | `AGE RESTRICTED — 18+` | **18+** | Delivered to users `18+` only |
| `UNSAFE_FOR_ALL`| `REJECT — UNSAFE FOR ALL` | **UNSAFE FOR ALL** | **STRICTLY BLOCKED FOR ALL USERS** |

---

## 4. User Age Categories & Registration Flow

Facial age estimation is used **strictly during registration**:
1. User enters profile information.
2. Camera is activated for a **single photo snapshot**.
3. `FaceAgeAdapter` detects face count, anti-spoof indicators, and classifies age:
   - Estimated age `< 14` $\rightarrow$ **SAFE FOR ALL** (`UNDER_14`)
   - Estimated age `14 – 17` $\rightarrow$ **14+** (`AGE_14_TO_17`)
   - Estimated age `18+` $\rightarrow$ **18+** (`AGE_18_PLUS`)
4. Stored in account profile (`User.verified_age_group`).
5. **Camera stops immediately.** No continuous tracking or surveillance during feed browsing.

---

## 5. Age-Aware Ad Delivery Eligibility Matrix

The delivery engine strictly enforces the following matrix:

| Authenticated User Age | SAFE FOR ALL Ad | 14+ Ad | 18+ Ad | UNSAFE FOR ALL Ad |
| :--- | :---: | :---: | :---: | :---: |
| **SAFE FOR ALL (< 14)** | ✅ **SHOWN** | ⛔ HIDDEN | ⛔ HIDDEN | ⛔ **NEVER DELIVERED** |
| **14+ (14 – 17)** | ✅ **SHOWN** | ✅ **SHOWN** | ⛔ HIDDEN | ⛔ **NEVER DELIVERED** |
| **18+ (18+)** | ✅ **SHOWN** | ✅ **SHOWN** | ✅ **SHOWN** | ⛔ **NEVER DELIVERED** |

### Human Reviewer Override Precedence
If an AI misclassifies an advertisement (e.g. AI predicts `18+` on an artisan root beer ad) and a Human Moderator reviews and changes it to `14+`:
- `final_classification` is updated to `14+`.
- Live ad delivery immediately begins delivering the ad to `14+` and `18+` users, while remaining hidden from `SAFE FOR ALL` users.
- `final_classification` always takes precedence over `ai_classification`.

---

## 6. Directory Structure

```text
Desktop/AgeAwareAdPlatform/
├── backend/
│   ├── app/
│   │   ├── api/v1/                # auth, advertisements, moderation, admin, age
│   │   ├── core/                  # config, security (HMAC-SHA256 JWT, hashing)
│   │   ├── db/                    # SQLAlchemy database engine, models (User, Advertisement, etc.)
│   │   ├── schemas/               # Pydantic schemas
│   │   └── services/              # policy_service, ai_client_service, age_service
│   └── safead.db                  # Relational database
├── camera-integration/
│   ├── face_age_adapter.py        # MTCNN / ViT / Haar Cascade / Anti-Spoofing adapter
│   └── camera_handler.py          # Frame capture & synthetic face generation
├── services/
│   ├── auth_service.py            # Account registration & login
│   ├── advertisement_service.py   # Ad submission & classification mapper
│   ├── moderation_service.py      # Telemetry & audit logs
│   ├── age_registration_service.py# Biometric age onboarding
│   ├── review_service.py          # HITL moderation queue & override
│   ├── ad_delivery_service.py     # Age-aware delivery engine
│   └── analytics_service.py       # Live database metrics
├── frontend/
│   ├── app.py                     # Unified multi-portal Streamlit entry point
│   ├── registration_view.py       # Biometric onboarding with camera
│   └── architecture_view.py       # Interactive architecture & matrix view
├── advertiser-portal/
│   └── advertiser_view.py         # Enterprise campaign hub
├── reviewer-portal/
│   └── reviewer_view.py           # HITL moderation console
├── admin-dashboard/
│   └── admin_view.py              # Compliance & metrics console
├── user-feed/
│   └── feed_view.py               # AuraFeed consumer social experience
├── assets/
│   ├── sample_media/              # Pre-bundled test ads (apples_ad.jpg, beer_pub.jpg, etc.)
│   └── uploads/                   # Runtime ad media uploads
├── config/
│   ├── default_config.py          # Platform settings & category mappings
│   └── policy_rules.json          # Declarative policy rules
├── docs/
│   └── integration-analysis.md    # In-depth architectural analysis
├── tests/
│   └── test_suite.py              # Automated 8-scenario test suite
├── .env.example                   # Environment configuration template
├── run_platform.py                # Platform launcher
└── README.md                      # Documentation
```

---

## 7. Setup & Installation Instructions

### Prerequisites
- Python 3.10+
- Webcam (Optional: pre-bundled synthetic profiles and sample media allow full testing without hardware)

### 1. Configure Environment
```bash
cd Desktop/AgeAwareAdPlatform
copy .env.example .env
```

### 2. Execute Automated Test Suite
To verify the complete 8-scenario delivery and moderation suite:
```bash
python run_platform.py --test
```
*Expected Result:*
```text
Ran 8 tests in 0.855s
OK
```

### 3. Launch the Platform
Start both the FastAPI backend server (Port 8000) and the Web Portals (Port 8501) with a single command:
```bash
python run_platform.py
```
- **Backend REST API**: `http://127.0.0.1:8000` (Docs at `/docs`)
- **Web Portals**: `http://127.0.0.1:8501`

To run components individually:
```bash
# Run backend only
python run_platform.py --backend-only

# Run frontend only
python run_platform.py --frontend-only
```

---

## 8. Interactive Testing & Verification Walkthrough

1. **Test Advertiser Flow**:
   - Open `http://127.0.0.1:8501` and navigate to **🏢 Advertiser Enterprise Portal**.
   - Select the checkbox to use pre-bundled sample media.
   - Choose `apples_ad.jpg` $\rightarrow$ Submit. Observe `SAFE FOR ALL` classification (94% confidence). Accept classification.
   - Choose `beer_pub.jpg` $\rightarrow$ Submit. Observe `18+` classification (`AGE_RESTRICTED`).
   - Click **Option B: Request Human Review**, enter rationale ("Artisan non-alcoholic craft root beer, suitable for 14+"), and submit.
2. **Test Human Reviewer Override Flow**:
   - Navigate to **🛡️ Human Reviewer (HITL) Queue**.
   - Locate the beer ad. Review AI telemetry and advertiser's note.
   - Select `14+` from the dropdown, add moderator rationale, and click **Lock Decision**.
   - Observe that the ad is now finalized as `14+`.
3. **Test User Registration Flow**:
   - Navigate to **👤 User Registration & Age Verification**.
   - Fill in username, email, password, and DOB.
   - Choose camera capture (or select the **Teen Face (14-17)** preset).
   - Click **Complete Registration**. The camera verifies the face, assigns `14+`, stores it, and halts camera permanently.
4. **Test Consumer Feed & Age-Aware Ad Delivery**:
   - Navigate to **📸 AuraFeed (Social Media Feed)**.
   - Use the **Demo Mode Controller** at the top:
     - Set Persona to **SAFE FOR ALL**: Observe that only `apples_ad.jpg` appears. The beer ad and violence ads are completely hidden.
     - Set Persona to **14+**: Observe that `apples_ad.jpg` AND the overridden `beer_pub.jpg` appear.
     - Set Persona to **18+**: All approved ads appear.
     - Notice that `UNSAFE FOR ALL` ads (e.g. `violence_ad.mp4`) are **never delivered to any user under any circumstance**.
     - Notice that normal users see only clean "Sponsored" tags with zero exposure to internal AI confidence or moderation scores.

---

## 9. Security, Privacy & Compliance Guardrails

- **Single-Use Camera**: The webcam is initialized only during registration, takes one frame, and is terminated. Normal browsing does not access the camera.
- **Biometric Minimization**: Raw facial photos are not stored permanently. Only the derived integer/enum age category is retained in the account record.
- **Fail-Closed Security**: If a model, connection, or file parse fails, the platform strictly rejects the advertisement (`UNSAFE_FOR_ALL`) rather than failing open.
- **Role Isolation**: Ordinary users cannot access advertiser analytics, audit logs, or AI debugging information.

---

## 10. Known Limitations

- **GPU Acceleration**: When running without local PyTorch/CUDA or external Colab GPU workers, deep-learning models automatically fall back to CPU geometric heuristics and OpenCV Haar cascades, which run smoothly at 30+ FPS on any modern CPU.
- **WebRTC in Headless Browsers**: When running in automated test environments without a physical webcam, use the pre-bundled synthetic face presets (`child`, `teen`, `adult`) provided in `CameraHandler`.
