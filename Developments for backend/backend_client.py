import requests
import os

BASE_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

class BackendClient:
    def __init__(self):
        self.token = None

    def login(self, username, password):
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False
        
    def submit_advertisement(self, title, caption, file_path):
        if not self.token:
            raise Exception("Not authenticated")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'
        
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, mime_type)}
            data = {"title": title, "caption": caption}
            response = requests.post(
                f"{BASE_URL}/advertisements/",
                headers=headers,
                data=data,
                files=files
            )
            
        if response.status_code != 201:
            raise Exception(f"API Error ({response.status_code}): {response.text}")
            
        return response.json()

# Global client instance for Streamlit
client = BackendClient()
