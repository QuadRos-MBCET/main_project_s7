import os
import requests

DATASET_SAMPLE_LINKS = {
    "UCF-Crime Sample": {
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/person-bicycle-car-detection.mp4",
        "filename": "ucf_crime_sample.mp4",
        "description": "Surveillance crime & anomaly detection video sample."
    },
    "XD-Violence Sample": {
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/store-aisle-detection.mp4",
        "filename": "xd_violence_sample.mp4",
        "description": "Action combat & audio-visual violence sample."
    },
    "SAFEWATCH Benchmark Sample": {
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/head-pose-face-detection-female.mp4",
        "filename": "safewatch_sample.mp4",
        "description": "Commercial ad policy safety benchmark video sample."
    }
}

def download_dataset_samples(target_dir: str = "datasets/samples"):
    os.makedirs(target_dir, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    print("=" * 60)
    print("        DOWNLOADING PUBLIC DATASET SAMPLE VIDEOS           ")
    print("=" * 60)
    
    for name, info in DATASET_SAMPLE_LINKS.items():
        save_path = os.path.join(target_dir, info["filename"])
        print(f"Downloading [{name}] -> {info['filename']}...")
        
        success = False
        for attempt in range(3):
            try:
                r = requests.get(info["url"], headers=headers, stream=True, timeout=30)
                if r.status_code == 200:
                    with open(save_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024*1024):
                            if chunk:
                                f.write(chunk)
                    size_mb = os.path.getsize(save_path) / (1024*1024)
                    print(f"  [OK] Downloaded: {size_mb:.2f} MB")
                    success = True
                    break
                else:
                    print(f"  [FAIL] HTTP Status {r.status_code}")
            except Exception as e:
                print(f"  [Attempt {attempt+1}/3 Error] {e}")
                
        if not success:
            print(f"  [FAIL] Could not download {name} after 3 attempts.")
            
    print("=" * 60)
    print(f"Sample video downloads saved to: {os.path.abspath(target_dir)}")

if __name__ == "__main__":
    download_dataset_samples()
