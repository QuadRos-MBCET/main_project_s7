import requests
from typing import Dict, Any, Optional
from config.default_config import settings

class BackendClient:
    """
    HTTP client for the SafeAd AI FastAPI backend.
    """
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}").rstrip('/')

    def check_health(self) -> Dict[str, Any]:
        try:
            r = requests.get(f"{self.base_url}/health", timeout=3)
            return {"online": r.status_code == 200, "details": r.json() if r.status_code == 200 else {}}
        except Exception as e:
            return {"online": False, "error": str(e)}

backend_client = BackendClient()
