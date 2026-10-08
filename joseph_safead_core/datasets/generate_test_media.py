import cv2
import numpy as np
import os
import imageio
from PIL import Image

TEST_MEDIA = [
    {
        "base_filename": "adult_18plus_ad",
        "title": "Intimacy Night Club",
        "lines": ["ADULT 18+ ONLY", "Intimacy, romance & sensual night", "Exclusive adult dating party"],
        "bg_color": (50, 20, 30),
        "text_color": (255, 100, 200)
    },
    {
        "base_filename": "gambling_satta_ad",
        "title": "Grand Casino Satta",
        "lines": ["MEGA CASINO JACKPOT", "Play slots, bet & win real cash", "Online satta khelo aur jeeto"],
        "bg_color": (10, 50, 10),
        "text_color": (100, 255, 50)
    },
    {
        "base_filename": "violence_combat_ad",
        "title": "Blood & Guns Action",
        "lines": ["ACTION THRILLER: BLOOD & GUNS", "Ultimate fight with weapons", "Shoot, stab & combat trailer"],
        "bg_color": (50, 10, 10),
        "text_color": (255, 100, 100)
    },
    {
        "base_filename": "scam_paisa_double_ad",
        "title": "Paisa Double Scheme",
        "lines": ["GET RICH FAST - PAISA DOUBLE", "Earn cash fast in 24 hours", "Guaranteed returns giveaway"],
        "bg_color": (50, 40, 10),
        "text_color": (255, 255, 100)
    },
    {
        "base_filename": "safe_python_ad",
        "title": "Python Coding Course",
        "lines": ["PYTHON FOR BEGINNERS & KIDS", "Learn coding step by step", "Simple geometry & math tutorial"],
        "bg_color": (30, 40, 50),
        "text_color": (255, 255, 255)
    }
]

def generate_universal_h264_media(output_dir: str = "datasets/samples"):
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("   GENERATING UNIVERSAL H.264 MP4 & JPG POLICY TEST MEDIA  ")
    print("=" * 60)
    
    for item in TEST_MEDIA:
        vid_filename = f"{item['base_filename']}.mp4"
        img_filename = f"{item['base_filename']}.jpg"
        
        vid_path = os.path.join(output_dir, vid_filename)
        img_path = os.path.join(output_dir, img_filename)
        
        # 1. Generate Frame (640x480)
        frame = np.ones((480, 640, 3), dtype=np.uint8)
        frame[:, :] = item["bg_color"]
        
        cv2.putText(frame, item["title"], (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.line(frame, (30, 80), (610, 80), (200, 200, 200), 2)
        
        for idx, line in enumerate(item["lines"]):
            cv2.putText(frame, line, (40, 160 + (idx * 60)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, item["text_color"], 2)
            
        # 2. Save JPG Image
        cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        
        # 3. Save Universal H.264 MP4 Video (libx264, yuv420p)
        writer = imageio.get_writer(vid_path, fps=10, codec="libx264", pixelformat="yuv420p")
        for _ in range(30):  # 3 second clip
            writer.append_data(frame)
        writer.close()
        
        vsize = os.path.getsize(vid_path) / 1024
        isize = os.path.getsize(img_path) / 1024
        print(f"  [OK] Generated H.264 Video: {vid_filename} ({vsize:.1f} KB)")
        print(f"  [OK] Generated JPG Image: {img_filename} ({isize:.1f} KB)")
        
    print("=" * 60)
    print(f"All media saved successfully to: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    generate_universal_h264_media()
