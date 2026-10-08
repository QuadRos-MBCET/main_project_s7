import requests

url = "http://localhost:8001/api/verify_id_and_face"
with open("c:/s7/main project/adult_dating.jpg", "rb") as f1, open("c:/s7/main project/apples_ad.jpg", "rb") as f2:
    files = {
        "id_file": ("adult_dating.jpg", f1.read(), "image/jpeg"),
        "live_file": ("apples_ad.jpg", f2.read(), "image/jpeg")
    }
    r = requests.post(url, files=files)
    print("Status:", r.status_code)
    try:
        j = r.json()
        print("Similarity:", j.get("face_similarity"))
    except Exception as e:
        print(r.text[:500])
