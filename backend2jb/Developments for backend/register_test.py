import requests

def register():
    url = "http://127.0.0.1:8000/api/v1/auth/register"
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "date_of_birth": "1995-01-01T00:00:00Z"
    }
    try:
        response = requests.post(url, json=data)
        print("Status Code:", response.status_code)
        print("Response:", response.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    register()
