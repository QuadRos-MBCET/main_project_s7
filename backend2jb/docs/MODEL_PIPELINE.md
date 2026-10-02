# SafeAd AI - Model Pipeline Specification

## Overview
This document provides complete technical specifications for the individual machine learning models, heuristic scanners, and fusion analytics comprising the SafeAd AI pipeline.

---

## 1. Visual Safety Engine
* **Primary Models**: Llama Guard Vision / Falconsai NSFW Vision Model.
* **Input Specs**: 
  * Single PIL Images or RGB Frame Tensors (`[3, 224, 224]`).
  * Dynamic scaling and normalization via standard ImageNet transform matrices.
* **Outputs**:
  * `nsfw_score`: Float ($0.0\text{--}1.0$) representing explicit/nudity probability.
  * `visual_flag`: `SAFE`, `SUGGESTIVE`, or `UNSAFE`.
* **Execution Logic**:
  * Image uploads execute single-pass vision evaluation.
  * Video uploads sample 16 keyframes uniformly; max NSFW score across keyframes determines video visual score.

---

## 2. Video Violence Detector
* **Primary Model**: `VideoMAEForVideoClassification` (`MCG-NJU/videomae-base-finetuned-kinetics`).
* **Input Specs**:
  * 16-frame uniform spatio-temporal video clip tensor: `torch.Size([1, 16, 3, 224, 224])`.
* **Outputs**:
  * `violence_score`: Float ($0.0\text{--}1.0$).
  * `violence_flag`: `NONE`, `LOW`, `HIGH`.
* **Execution Logic**:
  * Keyframes are stacked into a 5D temporal tensor.
  * Probabilities across action classes associated with fighting, physical assault, or explicit violence are aggregated into `violence_score`.

---

## 3. Optical Character Recognition (OCR) Engine
* **Primary Model**: `PaddleOCR` (English + Multilingual) with `PyTesseract` fallback.
* **Input Specs**:
  * High-resolution keyframe images (`[H, W, 3]`).
* **Outputs**:
  * `ocr_text`: Concatenated string of all detected text on ad banners or video overlays.
  * `text_regions`: Bounding boxes and confidence scores per detected text line.
* **Execution Logic**:
  * Filters out low-confidence OCR noise ($< 0.40$).
  * Extracted text is fed directly into the Text Safety Model and Ad Risk Analyzer.

---

## 4. Audio Processing & Speech-to-Text Engine
* **Primary Model**: OpenAI `Whisper` (`base` / `small` model architecture).
* **Input Specs**:
  * 16kHz mono WAV audio file extracted via PyAV / `imageio_ffmpeg`.
* **Outputs**:
  * `audio_transcript`: Full text transcript of spoken speech in ad.
  * `detected_language`: ISO language code (e.g. `en`, `es`, `hi`, `fr`).
  * `speech_detected`: Boolean flag indicating whether speech was present.
* **Execution Logic**:
  * Automatically detects language and transcribes spoken audio.
  * If no audio stream or silent track, `speech_detected` is set to `False` without failing pipeline.

---

## 5. Text Safety Model
* **Primary Model**: Llama Guard 3-1B / Safety Classifier.
* **Input Specs**:
  * Combined text corpus: `Ad Title + Ad Description + OCR Text + Audio Transcript`.
* **Outputs**:
  * `text_safety_score`: Float ($0.0\text{--}1.0$).
  * `toxic_categories`: List of policy flags (e.g., `hate_speech`, `harassment`, `profanity`, `adult_text`).
* **Execution Logic**:
  * Assesses full ad copy against standard compliance guidelines.

---

## 6. Ad Risk Analyzer
* **Type**: Policy-based heuristic & regex rules engine.
* **Targets**:
  * **Scam / Deceptive Claims**: Promises like "double your money", "guaranteed 1000% return", "crypto giveaway", "instant wealth".
  * **Explicit Content Offers**: Unsolicited adult adult messaging, illegal gambling, unregulated pharmaceutical products.
  * **Child Safety Violations**: Targeting restricted items to minors.
* **Outputs**:
  * `ad_risk_score`: Float ($0\text{--}100$).
  * `risk_category`: `SCAM_DECEPTIVE`, `EXPLICIT_OFFER`, `VIOLENCE_WEAPONS`, `CHILD_UNSAFE`, or `NONE`.
  * `ad_risk_flags`: Array of matched rule descriptions.

---

## 7. User Age-Confidence Analytics Engine
* **Primary Model**: OpenCV DNN / Haar Cascade Face Detector + DOB Calculator.
* **Input Specs**:
  * User DOB (`YYYY-MM-DD`).
  * Optional User Face Image.
* **Outputs**:
  * `chronological_age`: Exact integer age derived from DOB.
  * `estimated_age`: Estimated facial age from visual model.
  * `age_difference`: $\Delta = |\text{chronological\_age} - \text{estimated\_age}|$.
  * `age_confidence`: Normalized score ($0.0\text{--}1.0$) computed via Gaussian decay:
    $$\text{age\_confidence} = \exp\left(-\frac{\Delta^2}{2 \times 5^2}\right)$$
* **Usage**:
  * Verifies if user age aligns with content rating (`SAFE_18_PLUS`, `SAFE_14_PLUS`).
  * Highlights discrepancy if age verification fails or face confidence is low.

---

## 8. SafeAd Assessment Matrix & Fusion Model
The `SafeAdAssessment` dataclass aggregates all modality outputs:

```python
@dataclass
class SafeAdAssessment:
    visual_score: float         # 0.0 to 1.0 (NSFW / Visual risk)
    violence_score: float       # 0.0 to 1.0 (VideoMAE score)
    ocr_text: str               # Extracted OCR text
    audio_transcript: str       # Spoken transcript from Whisper
    text_safety_score: float    # 0.0 to 1.0 (Text safety score)
    ad_risk_score: float        # 0.0 to 100.0 (Scam / deceptive claim score)
    ad_risk_flags: List[str]    # Triggered risk flags
    modality_confidences: dict  # Per-modality confidence values
```

`SafeAdFusion` computes:
$$\text{Overall Risk Score} = \max\left(\text{ad\_risk\_score},\; 100 \times \left(0.35 \cdot S_{\text{vis}} + 0.25 \cdot S_{\text{viol}} + 0.20 \cdot S_{\text{text}} + 0.20 \cdot S_{\text{audio}}\right)\right)$$
$$\text{Confidence Score} = 1.0 - \text{Variance}(S_{\text{vis}}, S_{\text{viol}}, S_{\text{text}}, S_{\text{audio}})$$

---

## Model Pipeline Summary Table

| Modality / Engine | Underly Model / Method | Input | Key Output Metrics | Memory Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Visual Safety** | Falconsai NSFW / Vision | PIL / Tensor | `nsfw_score` (0-1) | Low (~200MB) |
| **Video Violence** | VideoMAE (Transformers) | 16-frame Tensor | `violence_score` (0-1) | Medium (~400MB) |
| **OCR Engine** | PaddleOCR / Tesseract | Keyframe Image | Extracted Text | Low (~150MB) |
| **Audio STT** | OpenAI Whisper | 16kHz WAV | Transcript + Lang | Medium (~500MB) |
| **Text Safety** | Llama Guard 3-1B | String | Safety Score (0-1) | Low (~300MB) |
| **Ad Risk Scanner**| Regex & Rule Engine | String Corpus | Risk Score (0-100) | Minimal (<1MB) |
| **Age Analytics** | OpenCV Face + DOB | Image + Date | `age_confidence` (0-1) | Minimal (~50MB) |
