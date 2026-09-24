import os
import requests
from backend.app.core.config import settings

class AIClientService:
    @staticmethod
    def process_advertisement(file_path: str, title: str = "", caption: str = "") -> dict:
        """
        Executes AI inference either via local AI pipeline or remote Colab API server.
        """
        colab_url = settings.COLAB_API_URL
        
        # 1. Remote Colab API server execution if configured
        if colab_url and colab_url.strip():
            target_url = colab_url.strip().rstrip('/')
            print(f"[AIClientService] Checking Remote Colab Server health at: {target_url}...")
            
            is_colab_online = False
            try:
                h_res = requests.get(f"{target_url}/health", timeout=1.5)
                if h_res.status_code == 200:
                    is_colab_online = True
            except Exception as h_err:
                print(f"[AIClientService WARNING] Remote Colab ping failed: {h_err}. Using local AI pipeline...")

            if is_colab_online:
                try:
                    import mimetypes
                    mime_type, _ = mimetypes.guess_type(file_path)
                    mime_type = mime_type or 'application/octet-stream'
                    
                    headers = {"ngrok-skip-browser-warning": "true"}
                    with open(file_path, "rb") as f:
                        files = {"file": (os.path.basename(file_path), f, mime_type)}
                        data = {"title": title, "caption": caption}
                        response = requests.post(
                            f"{target_url}/predict",
                            headers=headers,
                            files=files,
                            data=data,
                            timeout=90
                        )
                        if response.status_code == 200:
                            print(f"[AIClientService] Remote Colab GPU Inference complete!")
                            return response.json()
                except Exception as e:
                    print(f"[AIClientService WARNING] Remote Colab request failed: {e}. Falling back to local pipeline...")

        # 2. Local AI Pipeline Execution
        try:
            from ai.pipeline import run_safead_inference
            return run_safead_inference(file_path, title, caption)
        except Exception as e:
            print(f"[AIClientService ERROR] Local AI Pipeline execution error: {e}")
            return {
                "classification": "UNSAFE_FOR_ALL",
                "display_label": "Unsafe for All",
                "risk_score": 100.0,
                "confidence": 1.0,
                "publication_action": "REJECT",
                "action_badge": "REJECT — UNSAFE FOR ALL",
                "detected_categories": ["Processing Error"],
                "explanation": f"AI Processing failure: {e}",
                "evidence": {}
            }
