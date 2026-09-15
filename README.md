# 🛡️ SafeAd AI (SAFE-VISION)

**A Multimodal Trust and Safety Framework for Early Detection of Harmful Advertisements and Age-Aware Content Moderation**

Designed specifically around the constraints of **Google Colab Free** (VRAM caching, sequential model loading/unloading, lazy execution, `torch.inference_mode()`, batch size 1) with a decoupled **FastAPI Backend** and an interactive **Streamlit Frontend**.

---

## ⚡ Phase 1: AI Safety-Detection Core (Google Colab Free)

Phase 1 focuses on creating a reliable, Colab-compatible detection layer that accepts an advertisement image or video and produces structured safety evidence for:
* **Child-Safety Risk**
* **Violence Content**
* **Adult / NSFW Content**
* **Embedded Text (OCR)**

### 🚀 How to Run Phase 1 in Google Colab Free

1. Open **Google Colab Free** ([colab.research.google.com](https://colab.research.google.com/)).
2. Upload or open the dedicated Phase 1 notebook:
   `notebooks/safead_phase1_colab.ipynb`
3. Execute **Cell 1** to inspect the Colab Environment (Python, PyTorch, CUDA, GPU Memory, System RAM, Disk Space).
4. Run **Cell 2 & 3** to mount Google Drive and sync codebase files to local `/content` for high-speed disk I/O.
5. Run **Cells 4 & 5** to perform sequential safety detection on sample image and video advertisements.
6. Observe the standardized evidence JSON output and verify complete post-inference VRAM cleanup.

---

## 📊 Pretrained AI Safety Models (Phase 1 Documentation Table)

| Model Name | Category | Input Format | Source / Training Dataset | License | Parameters / Model Size | GPU Requirements | Actual Output Format | Key Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **X3D-M** | Violence Content | Video Clips / Sampled Frames | `visionlab-ai/school-violence-detection-models` (School/Real-world Violence) | Apache 2.0 / MIT | ~3.8M params (~15MB) | ~1.2 GB VRAM (FP16) | `{"detected": bool, "score": float, "source": "video"}` | Trained on clip motion & physical combat; non-physical threats require multimodal context. |
| **Image Violence Classifier** | Violence Content | Static Image (`.jpg`, `.png`, `.webp`) | Fine-tuned ImageNet / Threat Classification Datasets | MIT / Permissive | ~11M params (~44MB) | ~0.5 GB VRAM | `{"detected": bool, "score": float, "source": "image"}` | May flag non-violent action sports without semantic overlay analysis. |
| **ViT NSFW Detector** | Adult / NSFW | Image / Sampled Video Frames | `Falconsai/nsfw_image_detection` (NSFW vs Normal Image Benchmark) | Apache 2.0 | ~86M params (~340MB) | ~1.5 GB VRAM | `{"detected": bool, "score": float, "mean_score": float}` | Frame sampling frequency determines sensitivity on rapid video transitions. |
| **Llama Guard 3 / Open Safety Guard** | Child Safety Risk | Image Keyframes + OCR Overlay Text | Legitimate Open Safety Guardrails / Policy Datasets (No CSAM) | Llama 3 Community / Permissive | ~8B INT8 / Open Guard (~4.2GB) | ~4.5 GB VRAM (INT8) | `{"risk_detected": bool, "score": null, "category": "child_safety_risk"}` | Evaluates policy risk flags; score set to `null` as model outputs categorical risk labels. Zero CSAM data used. |
| **PyTesseract Engine** | OCR Overlay Text | Image / Frame Crop | Tesseract OCR Multilingual Synthetic & Real Overlay Text | Apache 2.0 | CPU Utility | 0 MB VRAM (CPU) | `{"ocr_text": "..."}` | Stylized artistic fonts or low-contrast text require heuristic string fallback parsing. |

---

## 🏗️ System Architecture

```text
               STREAMLIT FRONTEND (frontend/streamlit_app.py)
                                    |
                                    v
                 FASTAPI BACKEND (backend/app/main.py)
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
  SQL DATABASE (MySQL / SQLite)                   COLAB AI SERVICE LAYER (ai/)
  - Users & Age Verification                      - Memory Manager (VRAM Release)
  - Advertisements                                - Sequential Model Loader
  - Moderation Results & Audit Logs               - OCR, Visual & Text Extractors
                                                  - Safety Detection Core (ai/safety/)
                                                    * violence_detector.py
                                                    * nsfw_detector.py
                                                    * child_safety_detector.py
                                                    * safety_pipeline.py
                                                    * model_manager.py
                                                  - SafeAd 4-Class Adapter (Phase 2)
```

---

## 📦 Phase 1 Directory Structure

```text
Project CT_27/
├── ai/                         # Isolated AI & Model Computation Layer (Colab GPU execution)
│   ├── config.py               # Path & VRAM configuration
│   ├── memory_manager.py       # VRAM tracking, lazy loading & cache release
│   ├── model_manager.py        # Base model loader
│   ├── safety/                 # Phase 1 Safety Detection Core
│   │   ├── model_manager.py    # Context-managed sequential loader
│   │   ├── violence_detector.py# X3D-M video & image violence detector
│   │   ├── nsfw_detector.py    # Falconsai NSFW classifier & frame aggregator
│   │   ├── child_safety_detector.py # Child safety risk evaluator with limitations
│   │   └── safety_pipeline.py  # End-to-end evidence aggregator
│   ├── ocr/                    # OCR text extraction (PyTesseract + fallback)
│   ├── vision/                 # Visual feature extractors
│   ├── text/                   # Multilingual NLP
│   └── pipeline.py             # Base inference pipeline
├── configs/                    # System YAML configurations
│   ├── colab_config.yaml       # Phase 1 Colab configuration
│   └── config.yaml
├── notebooks/                  # Dedicated Google Colab Notebooks
│   ├── safead_phase1_colab.ipynb # Dedicated Phase 1 Colab Notebook
│   ├── safead_colab_setup.ipynb
│   └── safead_inference.ipynb
├── tests/                      # Automated test suite
│   └── test_safety_pipeline.py # Unit tests for safety detectors & schema
├── requirements.txt            # Dependencies list
└── README.md                   # System documentation
```

---

## 🧪 Running Unit Tests

Run the safety detection test suite locally:
```bash
python -m unittest tests/test_safety_pipeline.py
```
