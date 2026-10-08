import requests
import os

BASE_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

class BackendClient:
    def __init__(self):
        self.token = None

    def login(self, username="testuser", password="testpassword"):
        """Logs in user via JSON payload. Auto-registers if user does not exist."""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": username, "password": password},
                timeout=5
            )
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                return True
            
            # If 401/400 (user not found / incorrect creds), attempt registration then retry login
            if response.status_code in (400, 401, 404):
                reg_res = requests.post(
                    f"{BASE_URL}/auth/register",
                    json={
                        "username": username,
                        "email": f"{username}@example.com",
                        "password": password,
                        "date_of_birth": "1995-01-01"
                    },
                    timeout=5
                )
                if reg_res.status_code in (200, 201, 400):
                    retry_res = requests.post(
                        f"{BASE_URL}/auth/login",
                        json={"username": username, "password": password},
                        timeout=5
                    )
                    if retry_res.status_code == 200:
                        self.token = retry_res.json().get("access_token")
                        return True
        except Exception as e:
            print(f"[BackendClient] Backend server offline or connection error: {e}")
            return False
        return False
        
    def submit_advertisement(self, title, caption, file_path):
        # Auto login if token is missing
        if not self.token:
            success = self.login()
            if not success and not self.token:
                raise Exception("FastAPI Backend Server is not reachable or authentication failed. Please start backend via: uvicorn backend.app.main:app --port 8000")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'
        
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, mime_type)}
            data = {"title": title, "caption": caption}
            response = requests.post(
                f"{BASE_URL}/advertisements/check",
                headers=headers,
                data=data,
                files=files,
                timeout=120
            )
            
        if response.status_code not in (200, 201):
            raise Exception(f"API Error ({response.status_code}): {response.text}")
            
        return response.json()

# Global client instance for Streamlit
client = BackendClient()
