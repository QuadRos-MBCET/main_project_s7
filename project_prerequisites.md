# SAFE-VISION (SafeAd AI): External & System Prerequisites

This document lists the **external system components, credentials, and configurations** required for the project that are **not** part of the Python packages or code currently implemented.

---

## 🔑 1. API Keys & Access Tokens (Cloud MLLM & Model Hubs)

If you plan to use cloud-based VLMs (to bypass local CPU/GPU compute constraints) or download gated models:

1.  **Hugging Face Access Token (`HF_TOKEN`)**:
    *   *Why*: Needed to download gated models (such as `meta-llama/Llama-Guard-3-11B-Vision`) from the Hugging Face Hub.
    *   *Where to get*: Create an account on [huggingface.co](https://huggingface.co/) and generate a read-access token in your Profile Settings.
2.  **Google Gemini API Key (`GEMINI_API_KEY`)**:
    *   *Why*: Recommended for running multimodal inference on videos and images cheaply and fast without local GPU hardware.
    *   *Where to get*: Generate a free-tier key on Google AI Studio.
3.  **OpenAI API Key (`OPENAI_API_KEY`)**:
    *   *Why*: Optional fallback if utilizing GPT-4o-mini for multimodal moderation.

---

## ⚙️ 2. External System-Level Binaries (Required for Windows OS)

These are software dependencies that **cannot** be installed via `pip` and must be installed directly on your Windows operating system:

1.  **FFmpeg Binary**:
    *   *Why*: OpenCV (`cv2`) and Python video libraries require FFmpeg to decode and sample video streams (`.mp4`, `.avi`, `.mov`). Without FFmpeg installed and registered in your system PATH, video loading calls in Python will fail silently.
    *   *Installation*: Download from [ffmpeg.org](https://ffmpeg.org/download.html), extract, and add the `bin` folder to your Windows Environment Variables.
2.  **Tesseract OCR Engine**:
    *   *Why*: Required for the OCR text extraction block (`pytesseract`) to scan video frames for text overlays.
    *   *Installation*: Install using the [Windows Tesseract Installer](https://github.com/UB-Mannheim/tesseract/wiki). You must add the installation folder (usually `C:\Program Files\Tesseract-OCR`) to your system PATH.
3.  **Git LFS (Large File Storage)**:
    *   *Why*: Necessary to clone or download large dataset repositories and model weight tensors from Hugging Face and GitHub.
    *   *Installation*: Run `git lfs install` in your command line after installing Git.

---

## 🗂️ 3. Database & Storage Setup

1.  **Vector Database (FAISS or ChromaDB)**:
    *   *Why*: To store and retrieve safety policy rules.
    *   *Setup*: While the logic is mocked using matrices, a real deployment requires setting up a vector index store file (e.g. `policy_vector_index.faiss`) saved locally.
2.  **SQL Database Engine**:
    *   *Why*: To record advertiser campaigns, user search logs, and model moderation reasoning audit trails.
    *   *Setup*: A local SQLite file (`safead_database.db`) needs to be initialized with table structures (Users, Ads, ModerationLogs).
