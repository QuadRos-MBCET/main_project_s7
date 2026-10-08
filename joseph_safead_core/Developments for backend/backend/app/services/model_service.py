import os
import requests
from dotenv import load_dotenv

load_dotenv()
COLAB_API_URL = os.getenv("COLAB_API_URL")

class ModelService:
    @staticmethod
    def predict_multimodal(file_path: str) -> dict:
        """
        Sends the image to the Google Colab GPU server to run BLIP and NSFW classification.
        Returns: {"caption": "...", "visual_risk": 0.0, "visual_violations": []}
        """
        if not COLAB_API_URL:
            print("COLAB_API_URL not set, falling back to empty output.")
            return {"caption": "No caption (Colab disconnected)", "visual_risk": 0.0, "visual_violations": []}
            
        try:
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or 'application/octet-stream'
            
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, mime_type)}
                response = requests.post(f"{COLAB_API_URL}/predict", files=files, timeout=45)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Colab Error: {response.text}")
        except Exception as e:
            print(f"Error connecting to Colab: {e}")
            
        return {"caption": "Error connecting to Colab", "visual_risk": 0.0, "visual_violations": []}
