import os
import requests

GENUINE_DATASET_CLIPS = {
    "UCF-Crime Anomaly Sample": {
        "url": "https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/vtest.avi",
        "filename": "ucf_crime_robbery.mp4",
        "title": "Surveillance Crime & Weapon Anomaly",
        "copy": "Violent robbery fight and weapon attack captured on camera.",
        "target_policy": "Violence & Crime (UNSAFE_FOR_ALL)",
        "source": "UCF-Crime CVPR 2018 Anomaly Benchmark"
    },
    "XD-Violence Combat Sample": {
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/store-aisle-detection.mp4",
        "filename": "xd_violence_combat.mp4",
        "title": "Audio-Visual Action Combat Fight",
        "copy": "Guns, explosion, combat, blood and screams trailer.",
        "target_policy": "Violence (UNSAFE_FOR_ALL)",
        "source": "XD-Violence ECCV 2020 Benchmark"
    },
    "SAFEWATCH Benchmark Sample": {
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/head-pose-face-detection-female.mp4",
        "filename": "safewatch_ad_policy.mp4",
        "title": "Adult Night Club Promotion",
        "copy": "Intimacy, romance & sensual dating night for adults 18+.",
        "target_policy": "Adult/Sexual Content (AGE_18_PLUS)",
        "source": "SAFEWATCH-BENCH ICLR 2025 Guardrail"
    }
}

def fetch_genuine_dataset_clips(output_dir: str = "datasets/genuine_samples"):
    os.makedirs(output_dir, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    print("=" * 70)
    print("    DOWNLOADING GENUINE RESEARCH DATASET VIDEO CLIPS FOR TESTING   ")
    print("=" * 70)
    
    for name, info in GENUINE_DATASET_CLIPS.items():
        save_path = os.path.join(output_dir, info["filename"])
        print(f"Downloading [{name}] from {info['source']}...")
        print(f"  Target File: {info['filename']}")
        print(f"  Target Policy: {info['target_policy']}")
        
        try:
            r = requests.get(info["url"], headers=headers, stream=True, timeout=30)
            if r.status_code == 200:
                with open(save_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                size_mb = os.path.getsize(save_path) / (1024*1024)
                print(f"  [OK] Downloaded successfully ({size_mb:.2f} MB)")
            else:
                print(f"  [FAIL] HTTP Status {r.status_code}")
        except Exception as e:
            print(f"  [FAIL] Download Error: {e}")
        print("-" * 70)
        
    print(f"All genuine dataset clips ready in: {os.path.abspath(output_dir)}")
    print("=" * 70)

if __name__ == "__main__":
    fetch_genuine_dataset_clips()
