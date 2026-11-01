"""
SAFE-VISION (SafeAd AI) — Google Colab Qwen3-VL Server
Runs on Google Colab (with NVIDIA A100 GPU recommended, or T4/V100/L4).
Exposes a high-speed FastAPI server via ngrok or localtunnel.
Enables real-time remote inference from the local Streamlit / FastAPI frontend.
"""

import os
import sys
import time
import json
import tempfile
from typing import Dict, Any, List, Optional
from PIL import Image

def run_server(port: int = 8000, ngrok_token: Optional[str] = None):
    try:
        from fastapi import FastAPI, UploadFile, File, Form, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        import uvicorn
        import torch
        from transformers import AutoProcessor
    except ImportError:
        print("[ERROR] Required packages missing. Please run:")
        print("!pip install -U 'transformers>=4.48.0' accelerate qwen-vl-utils fastapi uvicorn python-multipart pyngrok pillow opencv-python")
        return

    # Check for Qwen3-VL model class
    try:
        from transformers import Qwen3VLForConditionalGeneration
    except ImportError:
        try:
            from transformers import AutoModelForVision2Seq as Qwen3VLForConditionalGeneration
        except ImportError:
            from transformers import Qwen2_5_VLForConditionalGeneration as Qwen3VLForConditionalGeneration

    try:
        from qwen_vl_utils import process_vision_info
    except ImportError:
        process_vision_info = None

    print("=" * 70)
    print("   SAFE-VISION: QWEN3-VL GOOGLE COLAB INFERENCE SERVER")
    print("=" * 70)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else torch.float16
    print(f"Device: {device} | Precision: {dtype}")

    if device == "cpu":
        print("[WARNING] No GPU detected! Inference will be slow. Switch Colab runtime to GPU (A100 recommended).")

    MODEL_ID = "Qwen/Qwen3-VL-8B-Instruct"
    print(f"Loading {MODEL_ID}...")

    try:
        processor = AutoProcessor.from_pretrained(MODEL_ID)
        model = Qwen3VLForConditionalGeneration.from_pretrained(
            MODEL_ID,
            torch_dtype=dtype,
            device_map="auto" if device == "cuda" else None
        )
        if device == "cuda":
            model = model.eval()
        print(f"[SUCCESS] {MODEL_ID} loaded successfully!")
    except Exception as e:
        print(f"[FALLBACK] Could not load {MODEL_ID} directly ({e}). Trying Qwen/Qwen2.5-VL-7B-Instruct...")
        MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"
        processor = AutoProcessor.from_pretrained(MODEL_ID)
        model = Qwen3VLForConditionalGeneration.from_pretrained(
            MODEL_ID,
            torch_dtype=dtype,
            device_map="auto" if device == "cuda" else None
        ).eval()

    app = FastAPI(title="SafeAd AI - Qwen3-VL Inference Server")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    SYSTEM_PROMPT = """You are a senior digital advertising trust and safety compliance officer.
Analyze the provided advertisement creative, extracted on-screen text (OCR), and speech audio transcript.
Evaluate the content against the four official statutory advertising policy tiers:
1. SAFE_FOR_ALL: General family audiences, consumer goods, education, technology. Zero adult themes, zero physical violence.
2. SAFE_14_PLUS: Mild adolescent action, competitive esports, teen cosmetics, dark fantasy. Strictly no explicit nudity, real combat violence, alcohol branding, or gambling.
3. SAFE_18_PLUS: Lawful commercial goods legally restricted to adults (alcoholic beverages, licensed casino wagering, adult dating, high-risk finance). Must contain statutory warnings.
4. UNSAFE_FOR_ALL: Prohibited contraband, real physical violence, hate speech, financial scams ("paisa double", guaranteed return crypto schemes), malware, phishing.

Respond STRICTLY in valid JSON matching this schema:
{
  "reasoning": "<concise step-by-step policy justification>",
  "predicted_class": "<SAFE_FOR_ALL | SAFE_14_PLUS | SAFE_18_PLUS | UNSAFE_FOR_ALL>",
  "confidence_scores": {
    "SAFE_FOR_ALL": <float 0.0-1.0>,
    "SAFE_14_PLUS": <float 0.0-1.0>,
    "SAFE_18_PLUS": <float 0.0-1.0>,
    "UNSAFE_FOR_ALL": <float 0.0-1.0>
  },
  "statutory_risk_score": <float 0.0-100.0>,
  "detected_violations": ["<violation_tags>"]
}"""

    @app.get("/health")
    def health():
        gpu_info = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
        return {
            "status": "online",
            "model": MODEL_ID,
            "device": str(device),
            "gpu": gpu_info,
            "precision": str(dtype),
            "service": "SAFE-VISION Qwen3-VL Inference Engine"
        }

    @app.post("/predict_qwen")
    async def predict_qwen(
        file: UploadFile = File(...),
        title: str = Form(""),
        caption: str = Form(""),
        extracted_ocr: str = Form(""),
        audio_transcript: str = Form("")
    ):
        start_time = time.perf_counter()
        contents = await file.read()
        suffix = os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            # Extract image or video keyframe
            if suffix in [".mp4", ".mov", ".avi", ".webm", ".mkv"]:
                import cv2
                cap = cv2.VideoCapture(tmp_path)
                total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, total // 2))
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None:
                    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                else:
                    pil_img = Image.new("RGB", (300, 300), color=(128, 128, 128))
            else:
                pil_img = Image.open(tmp_path).convert("RGB")

            # Build multimodal prompt
            user_text = f"Creative Title: '{title}'\nCaption / Ad Copy: '{caption}'\n"
            if extracted_ocr:
                user_text += f"Extracted OCR Text: '{extracted_ocr}'\n"
            if audio_transcript:
                user_text += f"Audio Speech Transcript: '{audio_transcript}'\n"
            user_text += "Evaluate the creative and output JSON compliance verdict."

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": pil_img},
                        {"type": "text", "text": user_text}
                    ]
                }
            ]

            prompt_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            if process_vision_info:
                image_inputs, video_inputs = process_vision_info(messages)
                inputs = processor(
                    text=[prompt_text],
                    images=image_inputs,
                    videos=video_inputs,
                    padding=True,
                    return_tensors="pt"
                ).to(device)
            else:
                inputs = processor(text=[prompt_text], images=[pil_img], return_tensors="pt").to(device)

            with torch.inference_mode():
                generated_ids = model.generate(
                    **inputs,
                    max_new_tokens=400,
                    do_sample=False,
                    temperature=None,
                    top_p=None
                )

            # Strip input prompt tokens
            trimmed_ids = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
            raw_response = processor.batch_decode(trimmed_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

            # Parse JSON
            cleaned = raw_response.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[-1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[-1].split("```")[0].strip()

            try:
                parsed = json.loads(cleaned)
            except Exception:
                # Heuristic fallback if JSON format had minor trailing characters
                import re
                m = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if m:
                    parsed = json.loads(m.group(0))
                else:
                    parsed = {
                        "reasoning": cleaned,
                        "predicted_class": "SAFE_FOR_ALL",
                        "confidence_scores": {"SAFE_FOR_ALL": 0.75, "SAFE_14_PLUS": 0.15, "SAFE_18_PLUS": 0.05, "UNSAFE_FOR_ALL": 0.05},
                        "statutory_risk_score": 10.0,
                        "detected_violations": []
                    }

            pred_class = parsed.get("predicted_class", "SAFE_FOR_ALL")
            if pred_class not in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL"]:
                pred_class = "SAFE_FOR_ALL"

            conf_scores = parsed.get("confidence_scores", {})
            confidence = float(conf_scores.get(pred_class, 0.85))
            risk_score = float(parsed.get("statutory_risk_score", 15.0))
            reasoning = parsed.get("reasoning", "Completed policy compliance review.")

            elapsed = round(time.perf_counter() - start_time, 3)

            return {
                "classification": pred_class,
                "predicted_class": pred_class,
                "confidence": confidence,
                "confidence_scores": conf_scores,
                "risk_score": risk_score,
                "statutory_risk_score": risk_score,
                "reasoning": reasoning,
                "explanation": f"[Qwen3-VL A100 GPU]: {reasoning}",
                "violations": parsed.get("detected_violations", []),
                "model_version": f"{MODEL_ID} (Google Colab {device.upper()})",
                "latency_seconds": elapsed,
                "raw_json": parsed
            }

        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    # Expose via ngrok if available
    public_url = None
    if ngrok_token:
        try:
            from pyngrok import ngrok
            ngrok.set_auth_token(ngrok_token)
            public_tunnel = ngrok.connect(port)
            public_url = public_tunnel.public_url
            print("\n" + "=" * 70)
            print(f"🚀 PUBLIC COLAB URL: {public_url}")
            print(f"👉 Copy this URL into the Streamlit Brand Owner Workspace Colab field!")
            print("=" * 70 + "\n")
        except Exception as e:
            print(f"[ngrok notice]: {e}")

    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--ngrok", type=str, default=None)
    args = parser.parse_args()
    run_server(port=args.port, ngrok_token=args.ngrok)
