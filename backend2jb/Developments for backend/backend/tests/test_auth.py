from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "SafeAd Backend is running"}

def test_register_user_missing_fields():
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "email": "test@example.com"}
    )
    assert response.status_code == 422 # Unprocessable Entity (Missing password, dob)
