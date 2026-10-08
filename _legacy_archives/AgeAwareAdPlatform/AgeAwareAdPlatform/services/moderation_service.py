import requests
import json
from typing import Dict, Any, List, Optional
from config.default_config import settings

class ModerationService:
    """
    Direct service wrapper for AI Moderation inspection, evidence telemetry,
    and audit trail monitoring.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}").rstrip('/')

    def get_moderation_details(self, ad_id: int) -> Dict[str, Any]:
        """Fetches full moderation assessment matrix and explanation for an ad."""
        url = f"{self.base_url}/api/v1/moderation/{ad_id}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                raw_cls = data.get("final_classification") or data.get("classification", "UNSAFE_FOR_ALL")
                data["application_category"] = settings.BACKEND_TO_APP_MAP.get(raw_cls, "UNSAFE FOR ALL")
                return {"success": True, "data": data}
            return {"success": False, "error": f"Ad #{ad_id} not found."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves system audit logs."""
        url = f"{self.base_url}/api/v1/moderation/logs?limit={limit}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return []
        except Exception:
            return []

moderation_service = ModerationService()
