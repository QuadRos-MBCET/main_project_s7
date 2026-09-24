# SafeAd AI - System Architecture

## Overview
SafeAd AI (SAFE-VISION) is an enterprise-grade, multimodal AI moderation system designed to enforce compliance, content safety, and proactive ad risk filtering for digital advertising platforms. The system ingests multimodal advertisements (images, short video clips, audio tracks, and advertising copy) and performs automated analysis to assess risk, classify content safety, determine age appropriateness, and route ambiguous or borderline cases to human moderators.

---

## The 5 Official Project Objectives

```
+-----------------------------------------------------------------------------------+
|                            SAFEAD AI OBJECTIVES MATRIX                             |
+--------------------------+--------------------------------------------------------+
| 1. Multimodal Pipeline   | Central SafeAdAssessment matrix synthesizing visual,    |
|                          | video, OCR, audio, text safety, and ad risk outputs.   |
+--------------------------+--------------------------------------------------------+
| 2. Proactive Filtering   | Ad Risk Analyzer detecting violence, adult/NSFW, child |
|                          | safety, financial scams, & deceptive marketing claims. |
+--------------------------+--------------------------------------------------------+
| 3. Age-Confidence        | Content rating (SAFE_FOR_ALL, SAFE_14_PLUS,            |
|    Analytics             | SAFE_18_PLUS, UNSAFE_FOR_ALL) + User face-age delta   |
|                          | confidence scoring (0.0 - 1.0).                        |
+--------------------------+--------------------------------------------------------+
| 4. Transparent Scoring   | Overall risk score (0-100), confidence score (0-1),   |
|                          | full modality breakdown, and natural language rationale.|
+--------------------------+--------------------------------------------------------+
| 5. Human-in-the-Loop     | Uncertainty handling (confidence < 0.65, conflicting   |
|                          | modalities, borderline risk 45-55) queued for review.  |
+--------------------------+--------------------------------------------------------+
```

---

## High-Level Data Flow & Workflow Architecture

```
                       UPLOADED ADVERTISEMENT
                     (Image / Video + Text / Audio)
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
             Keyframe Sampler             Audio Extractor
           (Adaptive FPS Sampling)     (PyAV / FFmpeg Subprocess)
                    │                             │
    ┌───────────────┼───────────────┐             │
    ▼               ▼               ▼             ▼
Visual Safety   Video Safety       OCR         Whisper
(Llama Guard / (VideoMAE        (PaddleOCR / (Speech-to-Text
 Falconsai)      Violence)       Tesseract)   Transcript)
    │               │               │             │
    └───────────────┼───────────────┴─────────────┘
                    │
                    ▼
         Text Safety Model & Ad Risk Analyzer
          (Llama Guard 3-1B + Regex Scanners)
                    │
                    ▼
        ┌───────────────────────────────────────┐
        │       SafeAdAssessment Matrix         │
        │  Visual  │ Video │ OCR │ Audio │ Text │
        └───────────────────┬───────────────────┘
                            │
                            ▼
                    SafeAdFusion Engine
            (Weighted Modality Score Synthesis)
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
          ▼                                   ▼
   Deterministic Policy                 Age-Confidence Analytics
   & Risk Categorization               (DOB Delta & Face Confidence)
          │                                   │
          └─────────────────┬─────────────────┘
                            │
                            ▼
          ┌───────────────────────────────────┐
          │ High Confidence & Decisive Risk?  │
          └─────────────────┬─────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │ YES                       │ NO (Confidence < 0.65,
              ▼                           │     Borderline Score 45-55,
       Final Decision                     │     or Conflicting Modality)
 (SAFE_FOR_ALL, SAFE_14_PLUS,             ▼
  SAFE_18_PLUS, UNSAFE_FOR_ALL)    HUMAN REVIEW QUEUE
                                  (Moderator Admin Dashboard)
```

---

## System Components

### 1. Multi-Modal Ingestion & Sampling Layer
* **Video Keyframe Sampler**: Uses OpenCV to sample video frames adaptively based on video duration (10s short ads: high temporal density; >30s: uniform stride sampling).
* **Audio Extractor**: Uses PyAV and `imageio-ffmpeg` to strip audio tracks into standardized 16kHz WAV format for speech model ingestion.

### 2. Multi-Model Inference Engines
* **Visual Safety**: Classifies images and keyframes into safe, suggestive, or NSFW categories using fine-tuned vision models (Falconsai NSFW / Llama Guard Vision).
* **Video Violence Detector**: Passes 16-frame spatio-temporal tensor clips into `VideoMAEForVideoClassification` to evaluate combat, weapons, or aggressive motion.
* **OCR Module**: Extracts burned-in text overlays using `PaddleOCR` (or `PyTesseract` fallback) to catch text hidden inside images.
* **Audio Speech-to-Text**: Converts spoken ad dialogue into clean text using OpenAI `Whisper`.
* **Text Safety & Ad Risk Analyzer**: Evaluates ad title, description, OCR text, and audio transcript for hate speech, scams, deceptive promises ("get rich quick", "100% guaranteed return"), and illegal product promotion.

### 3. SafeAd Fusion & Decision Matrix
The `SafeAdFusion` engine synthesizes all findings into a unified `SafeAdAssessment` matrix:
* Computes weighted overall `risk_score` ($0\text{--}100$).
* Computes `confidence` ($0.0\text{--}1.0$) reflecting agreement among modalities.
* Identifies conflicting signals across modalities (e.g., safe visual but deceptive audio).
* Evaluates borderline risk thresholds ($45\text{--}55$).

### 4. Human-in-the-Loop (HITL) Queue & Moderator Dashboard
Any ad triggering one of the following criteria is assigned status `REQUIRES_HUMAN_REVIEW` and pushed to the Moderator Dashboard:
1. Low overall confidence ($< 0.65$)
2. Conflicting modality findings (e.g. Visual SAFE, Text UNSAFE)
3. Borderline risk score ($45 \le \text{risk\_score} \le 55$)

Moderators can inspect the exact evidence matrix, review video keyframes, listen to audio, and either approve or override the automated decision.

---

## VRAM Optimization & Sequential Execution Strategy
To guarantee seamless execution on resource-constrained environments like Google Colab Free Tier (T4 GPU with 15GB VRAM), SafeAd AI utilizes:
1. **Lazy Loading**: Models are instantiated only when required for the uploaded media type.
2. **Sequential Inference Pipeline**: Execution moves sequentially through modalities rather than keeping all models in GPU memory simultaneously.
3. **Explicit Memory Flushing**: `torch.cuda.empty_cache()` and Python garbage collection (`gc.collect()`) are invoked after every single modality step.

---

## Database Architecture
SafeAd AI utilizes SQLAlchemy supporting SQLite (local development) and MySQL (production deployments).
Key tables include:
* `advertisements`: Stores metadata, media path, user DOB, and submission timestamp.
* `moderation_results`: Stores final safety classification, risk score, confidence score, age confidence analytics, and `is_human_reviewed` status.
* `assessment_matrices`: Stores granular modality results (`visual_score`, `ocr_text`, `audio_transcript`, `ad_risk_flags`).
