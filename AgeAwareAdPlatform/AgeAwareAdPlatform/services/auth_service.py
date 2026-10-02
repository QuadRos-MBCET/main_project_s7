import requests
from typing import Dict, Any, Optional
from config.default_config import settings

class AuthService:
    """
    Unified client service for User, Advertiser, and Reviewer authentication.
    Communicates with backend /api/v1/auth endpoints.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}").rstrip('/')
        
    def register(self, username: str, email: str, password: str, date_of_birth: str) -> Dict[str, Any]:
        """Registers a new account."""
        url = f"{self.base_url}/api/v1/auth/register"
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "date_of_birth": date_of_birth
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                return {"success": True, "data": resp.json()}
            return {"success": False, "error": resp.json().get("detail", "Registration failed.")}
        except Exception as e:
            return {"success": False, "error": f"Network/Backend error: {str(e)}"}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticates user and returns JWT token and verified age group."""
        url = f"{self.base_url}/api/v1/auth/login"
        payload = {"username": username, "password": password}
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # Map backend verified_age_group to application display label
                db_group = data.get("verified_age_group", "AGE_18_PLUS")
                app_cat = "18+"
                if db_group == "UNDER_14":
                    app_cat = "SAFE FOR ALL"
                elif db_group == "AGE_14_TO_17":
                    app_cat = "14+"
                data["display_age_category"] = app_cat
                return {"success": True, "data": data}
            return {"success": False, "error": resp.json().get("detail", "Invalid username or password.")}
        except Exception as e:
            return {"success": False, "error": f"Network/Backend error: {str(e)}"}

auth_service = AuthService()
