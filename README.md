# SAFEAD AI (SAFE-VISION)
## Multimodal Advertisement Safety & Policy Moderation Framework

---

### Project Overview

**SafeAd AI** is a multimodal trust and safety moderation framework designed for pre-publication advertisement safety checking. The framework accepts uploaded image or video advertisements and evaluates their safety across visual content, video action sequences, embedded OCR text overlays, spoken audio transcripts, and contextual safety policies.

---

### System Pipeline Architecture

```
                 UPLOADED ADVERTISEMENT
                          |
             +------------+------------+
             |                         |
          IMAGE                     VIDEO
             |                         |
             |                  Keyframe Sampling
             |                         |
             |                  Frame Analysis
             |                         |
             +------------+------------+
                          |
                  MULTIMODAL ANALYSIS
                          |
       +------------------+------------------+
       |                  |                  |
     VISUAL              TEXT              AUDIO
       |                  |                  |
  Llama Guard           PP-OCR            Whisper
    Vision                |                  |
       |                  +---------+--------+
       |                            |
       +----------------------------+
                    |
             SAFETY EVIDENCE
                    |
          SafeAd Fusion Layer
                    |
              Risk Score
                    |
          Policy Decision Layer
                    |
       +------------+------------+
       |                         |
      SAFE                     UNSAFE
       |                         |
   Age Category              Reject
       |
 +-----+---------+
 |       |       |
All     14+     18+
```

---

### Key System Features & Modalities

1. **Visual Safety Analysis**: Evaluates image/frame content using pretrained multimodal visual safety models (**Llama Guard 3 Vision**).
2. **Adult / NSFW Detection**: Frame-level classification using **Falconsai/nsfw_image_detection** ViT, aggregated into video-level adult scores.
3. **Video Violence Detection**: Action sequence classification using pretrained **VideoMAE** (`MCG-NJU/videomae-base-finetuned-kinetics`).
4. **Adaptive Keyframe Sampling**: Handles short (10s, 20s, 30s) and long video advertisements adaptively without frame padding.
5. **Multilingual OCR Pipeline**: Extracts embedded text overlays across video keyframes using **PP-OCR / PaddleOCR**.
6. **Audio Extraction & Speech Transcription**: Extracts audio streams and transcribes spoken speech using **OpenAI Whisper**.
7. **Text Safety Guardrail**: Evaluates OCR text and Whisper transcripts using **Llama Guard 3-1B**.
8. **Deterministic SafeAd Evidence Fusion Layer**: Fuses multi-modal risk scores (0–100), dominant risks, and model confidence without random or placeholder outputs.
9. **Four-Level Policy Classification**:
   - `SAFE_FOR_ALL` (*Safe for All*) $\rightarrow$ **APPROVED**
   - `SAFE_14_PLUS` (*14+*) $\rightarrow$ **AGE RESTRICTED — 14+**
   - `SAFE_18_PLUS` (*18+*) $\rightarrow$ **AGE RESTRICTED — 18+**
   - `UNSAFE_FOR_ALL` (*Unsafe for All*) $\rightarrow$ **REJECT — UNSAFE FOR ALL**
10. **Google Colab Free Compatibility**: Enforces sequential model loading, lazy initialization, and VRAM memory flushing between stages.

---

### Modality & Pretrained Model Summary

| Modality | Pretrained Safety Model / Engine | Purpose | Output Evidence |
| :--- | :--- | :--- | :--- |
| **Visual Safety** | `meta-llama/Llama-Guard-3-11B-Vision` | Visual frame safety evidence generator | Visual risk flags & category confidence |
| **Adult / NSFW** | `Falconsai/nsfw_image_detection` | ViT NSFW image/frame classifier | Frame probabilities & max adult score |
| **Video Violence** | `MCG-NJU/videomae-base-finetuned-kinetics` | VideoMAE action sequence classifier | Video violence score & detected clips |
| **OCR Text** | `PP-OCR / PaddleOCR` | Multilingual embedded text extractor | Aggregated overlay text & confidence |
| **Audio Speech** | `openai/whisper-small` / `whisper-base` | Audio extraction & speech-to-text | Audio availability & transcript string |
| **Text Safety** | `meta-llama/Llama-Guard-3-1B` | Text safety policy guardrail | Separate OCR & audio transcript risks |
| **Fusion Layer** | `SafeAdFusion` (CPU) | Deterministic evidence fusion engine | Fused risk score (0-100) & policy decision |

---

### Project File Structure

```
Project CT_27 - Copy/
├── app/ or frontend/
│   └── streamlit_app.py           # Streamlit 8-Step Moderation Portal
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── moderation.py      # POST /api/moderate, GET /api/moderation/history
│   │   │   ├── advertisements.py # POST /api/v1/advertisements/check, user_feed
│   │   │   ├── auth.py            # Registration & Login endpoints
│   │   │   └── age.py             # User age verification workflow
│   │   ├── db/
│   │   │   ├── models.py          # SQLAlchemy models (User, Advertisement, ModerationResult)
│   │   │   └── database.py        # MySQL database session (SQLite fallback)
│   │   ├── services/
│   │   │   ├── ai_client_service.py # AI Client Dispatcher
│   │   │   └── policy_service.py    # Policy Decision Service
│   │   └── main.py                # FastAPI application entry point
├── models/
│   ├── model_manager.py           # Sequential model loader & VRAM memory manager
│   ├── visual_safety.py           # Llama Guard 3 Vision visual safety detector
│   ├── nsfw_detector.py           # Falconsai NSFW detector
│   ├── violence_detector.py       # VideoMAE video violence detector
│   ├── ocr_service.py             # PP-OCR / PaddleOCR service
│   ├── audio_service.py           # Whisper audio transcription service
│   ├── text_safety.py             # Llama Guard 3-1B text safety detector
│   └── fusion/
│       └── safead_fusion.py       # Deterministic SafeAd Fusion Layer
├── processing/
│   ├── video_sampling.py          # Adaptive keyframe extraction
│   ├── audio_extraction.py        # Audio stream extraction to WAV
│   └── preprocessing.py           # Media file validation
├── tests/
│   └── test_moderation_pipeline.py# Unit & Integration Test Suite (12 Scenarios)
├── colab_setup.py                 # Google Colab automated setup script
├── requirements.txt               # System Python dependencies
└── README.md                      # Project Documentation
```

---

### Quick Start & Execution

#### 1. Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run Unit Test Suite
python -m unittest tests/test_moderation_pipeline.py

# Start FastAPI Backend Server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Start Streamlit Moderation Portal
streamlit run frontend/streamlit_app.py
```

#### 2. Google Colab Setup
1. Upload project files to Google Colab.
2. Run automated setup script:
   ```python
   !python colab_setup.py
   ```
3. Run test suite or start moderation pipeline:
   ```python
   from ai.pipeline import run_safead_inference
   result = run_safead_inference("violence_ad.mp4", "Sample Ad Title", "Sample Ad Copy")
   print(result)
   ```

---

### REST API Endpoints

- `POST /api/moderate` — Submits image/video for full multimodal safety moderation.
- `POST /api/moderate/image` — Submits image advertisement.
- `POST /api/moderate/video` — Submits video advertisement.
- `GET /api/moderation/{id}` — Retrieves moderation report by Ad ID.
- `GET /api/moderation/history` — Retrieves history of moderation requests.
- `GET /api/health` — Returns system health status and active database engine.
