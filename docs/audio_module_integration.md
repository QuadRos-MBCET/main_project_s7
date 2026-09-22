# SafeAd AI — Audio Safety Analysis Module Integration Report

**Author:** Antigravity AI  
**Project:** SAFE-VISION / SafeAd AI  
**Target Environment:** Google Colab Free (CPU/GPU Fallback)  

---

## 1. Current Video Pipeline Inspection

The existing video analysis workflow operates as follows:
- **Input Entry Point:** Uploaded videos enter through the FastAPI backend (`backend/app/api/v1/moderation.py`) which invokes `AIClientService.process_advertisement()`, directing calls to `ai.pipeline.run_safead_inference()` (or remote Colab API endpoint).
- **Validation:** `validate_advertisement_input()` in `ai/pipeline.py` checks file existence, extension, and OpenCV stream readability (`cv2.VideoCapture`).
- **Frame Extraction:** `sample_video_frames()` in `ai/pipeline.py` uniformly samples $N$ frames (default $N=8$, configurable via `MAX_VIDEO_FRAMES`) without loading full video into RAM.
- **Visual Safety Prediction:** `extract_visual_features_sequential()` in `ai/vision/feature_extractor.py` processes keyframes using YOLO object detection and BLIP captioning. In parallel, `SafetyPipeline` in `ai/safety/safety_pipeline.py` runs sequential visual safety detectors (`ViolenceDetector` with X3D-M, `NSFWDetector` with FalconsAI NSFW, and `ChildSafetyDetector`).
- **OCR Text Processing:** `extract_ocr_from_image()` in `ai/ocr/ocr_extractor.py` extracts embedded text overlays from keyframes.
- **Multimodal Text Analysis:** `analyze_multimodal_text()` in `ai/text/text_processor.py` analyzes title, caption, OCR text, and visual captions against policy keywords (multilingual: English, Hinglish, Manglish).
- **Explainability & Classification:** `generate_cot_explanation()` in `ai/explainability/cot_explainer.py` generates Chain-of-Thought summaries, and `SafeAdModelService.adapt_prediction()` in `ai/safead_adapter.py` maps scores to standard 4-Class categories (`SAFE_FOR_ALL`, `AGE_14_PLUS`, `AGE_18_PLUS`, `UNSAFE_FOR_ALL`).

---

## 2. Audio Extraction Insertion Point

Audio extraction will be inserted into the video processing branch in `ai/pipeline.py` (and `ai/safety/safety_pipeline.py`):
```
Uploaded Video (.mp4, .mov, .avi, .mkv)
       │
       ├─► Video Frame Extraction ──► Visual Safety Analysis ──► Visual Risk & Features
       │
       └─► ffmpeg Audio Extraction ──► Temporary Mono WAV (16kHz)
                │
                ▼
           Whisper STT ──► Transcript & Language Detection
                │
                ▼
           Text Safety Analysis ──► Audio Safety Evidence
                │
                ▼
     Multimodal Evidence Aggregation & Standardized Output
```
- Audio extraction occurs immediately after video validation.
- If the video contains no audio track or is muted, audio extraction returns `{"audio_present": false, "transcript": "", "status": "no_audio"}` safely without throwing errors.

---

## 3. Existing Output Structure & Extension

### Standard 4-Class Output (`SafeAdModelService.adapt_prediction`)
```json
{
  "classification": "SAFE_FOR_ALL",
  "risk_score": 0.0,
  "risk_score_available": true,
  "risk_category": "general_audience",
  "explanation": "...",
  "age_restriction": null,
  "action": "APPROVE",
  "publishable": true,
  "violations": []
}
```

### Extended Safety Evidence Format with Audio Analysis
```json
{
  "audio_analysis": {
    "audio_present": true,
    "transcript": "Transcribed speech content from video advertisement...",
    "language": "en",
    "transcription_duration_seconds": 2.45,
    "model": "whisper-base",
    "violence": {
      "risk": false,
      "score": null
    },
    "adult_content": {
      "risk": false,
      "score": null
    },
    "child_safety": {
      "risk": false,
      "score": null
    }
  }
}
```

---

## 4. Files that Need Modification

1. `ai/config.py`: Add audio settings (`WHISPER_MODEL = "base"`, `AUDIO_SAMPLE_RATE = 16000`, audio cache directory).
2. `ai/pipeline.py`: Wire `AudioAnalyzer` into `run_safead_inference()`, include transcript in `analyze_multimodal_text()`, attach `audio_analysis` to result.
3. `ai/safety/safety_pipeline.py`: Incorporate audio transcription & text safety evaluation into `SafetyPipeline.analyze_advertisement()`.
4. `ai/text/text_processor.py`: Extend `analyze_multimodal_text()` parameters to support `transcript` input.
5. `notebooks/safead_inference.ipynb`: Add audio analysis demonstration cell.

---

## 5. New Files Required

1. `ai/audio/__init__.py`: Package initialization.
2. `ai/audio/audio_extractor.py`: Handles ffmpeg audio stream extraction to temporary 16kHz mono WAV files, graceful handling of muted or missing audio.
3. `ai/audio/speech_transcriber.py`: Manages OpenAI Whisper model loading, GPU/CPU inference, language detection, memory clearing.
4. `ai/audio/audio_analyzer.py`: Main audio branch coordinator combining extraction, STT, safety analysis, caching, and schema formatting.
5. `ai/audio/audio_event_detector.py`: Architectural extension point for future non-speech acoustic event classification (with clear documentation of speech-only scope).
6. `tests/test_audio_module.py`: Unit tests for audio extraction, Whisper transcription, fallback handling, and output schema verification.

---

## 6. Integration Strategy

- **Modularity First:** The `ai/audio` module will function as an independent, fully testable branch.
- **Zero Disturbance:** Visual feature extractors (`YOLO`, `BLIP`, `X3D-M`, `FalconsAI NSFW`) and core API models will remain untouched.
- **Data Flow Integration:** Audio transcripts will be merged into the text analysis pipeline alongside OCR and metadata text, ensuring speech-based policy violations (gambling, adult speech, violence threats, scams) contribute directly to safety scoring.

---

## 7. Google Colab Resource Considerations

- **Sequential Execution:** Run visual models $\rightarrow$ release VRAM $\rightarrow$ extract audio $\rightarrow$ run Whisper STT $\rightarrow$ release VRAM.
- **Model Efficiency:** Default to `WHISPER_MODEL = "base"` (or `"tiny"`), with configurable options for `"small"`.
- **Memory Management:** Utilize `MemoryManager.clear_gpu_memory()`, `torch.inference_mode()`, and explicit model unloading to maintain optimal VRAM footprint below free Colab limits.
- **Temporary File Cleanup:** Automatically clean up temporary audio `.wav` files after transcription.
