import requests
import os

FACE_AGE_API_URL = os.getenv("FACE_AGE_API_URL", "http://localhost:8001/api")

class FaceAgeClient:
    @staticmethod
    def verify_id_and_face(id_file, live_file, manual_dob=""):
        url = f"{FACE_AGE_API_URL}/verify_id_and_face"
        try:
            files = {
                "id_file": (id_file.name, id_file.getvalue(), id_file.type),
                "live_file": (live_file.name, live_file.getvalue(), live_file.type)
            }
            data = {"manual_dob": manual_dob} if manual_dob else {}
            r = requests.post(url, files=files, data=data, timeout=60)
            if r.status_code == 200:
                return r.json(), None
            return None, r.text
        except Exception as e:
            return None, str(e)
