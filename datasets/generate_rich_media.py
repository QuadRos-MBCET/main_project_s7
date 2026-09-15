import cv2
import numpy as np
import os
import imageio

def draw_adult_scene(frame, frame_idx):
    # Night club background gradient
    h, w, _ = frame.shape
    # Draw neon lights / disco circles
    cv2.circle(frame, (100 + (frame_idx * 5) % 400, 120), 40, (255, 0, 200), -1)
    cv2.circle(frame, (450 - (frame_idx * 5) % 400, 150), 60, (200, 0, 255), -1)
    
    # Draw cocktail glass graphic
    pt1 = (500, 300)
    pt2 = (560, 300)
    pt3 = (530, 360)
    cv2.line(frame, pt1, pt2, (255, 255, 255), 3)
    cv2.line(frame, pt1, pt3, (255, 255, 255), 3)
    cv2.line(frame, pt2, pt3, (255, 255, 255), 3)
    cv2.line(frame, (530, 360), (530, 420), (255, 255, 255), 3)
    cv2.line(frame, (500, 420), (560, 420), (255, 255, 255), 3)
    # Cocktail drink fill
    cv2.fillConvexPoly(frame, np.array([pt1, pt2, pt3]), (100, 50, 255))
    
    # Draw couple silhouette heads
    cv2.circle(frame, (150, 330), 30, (20, 20, 40), -1)
    cv2.ellipse(frame, (150, 420), (45, 60), 0, 0, 360, (20, 20, 40), -1)
    
    cv2.circle(frame, (200, 340), 28, (40, 20, 50), -1)
    cv2.ellipse(frame, (200, 420), (40, 55), 0, 0, 360, (40, 20, 50), -1)

def draw_gambling_scene(frame, frame_idx):
    # Slot machine box
    cv2.rectangle(frame, (180, 100), (460, 320), (30, 30, 30), -1)
    cv2.rectangle(frame, (180, 100), (460, 320), (0, 215, 255), 4)
    
    # Reels
    reels_symbols = ["777", "$$$", "BAR"]
    sym = reels_symbols[(frame_idx // 5) % 3]
    cv2.rectangle(frame, (200, 130), (270, 290), (255, 255, 255), -1)
    cv2.rectangle(frame, (285, 130), (355, 290), (255, 255, 255), -1)
    cv2.rectangle(frame, (370, 130), (440, 290), (255, 255, 255), -1)
    
    cv2.putText(frame, "7", (215, 220), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 4)
    cv2.putText(frame, "$", (300, 220), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 180, 0), 4)
    cv2.putText(frame, sym[0], (385, 220), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 0, 0), 4)
    
    # Gold Coins
    cv2.circle(frame, (100, 380), 35, (0, 215, 255), -1)
    cv2.putText(frame, "$", (90, 395), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 100, 150), 3)
    
    cv2.circle(frame, (540, 370), 40, (0, 215, 255), -1)
    cv2.putText(frame, "$", (528, 388), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 100, 150), 3)

def draw_violence_scene(frame, frame_idx):
    # Red danger flashes
    # Crossed Swords / Combat Knife graphics
    cv2.line(frame, (100, 150), (250, 350), (200, 200, 200), 8)
    cv2.line(frame, (250, 150), (100, 350), (200, 200, 200), 8)
    # Hilt
    cv2.line(frame, (90, 340), (120, 370), (100, 100, 100), 12)
    cv2.line(frame, (260, 340), (230, 370), (100, 100, 100), 12)
    
    # Crosshair Target
    cx, cy = 480, 240
    cv2.circle(frame, (cx, cy), 50, (0, 0, 255), 3)
    cv2.circle(frame, (cx, cy), 20, (0, 0, 255), 2)
    cv2.line(frame, (cx - 70, cy), (cx + 70, cy), (0, 0, 255), 2)
    cv2.line(frame, (cx, cy - 70), (cx, cy + 70), (0, 0, 255), 2)

def draw_scam_scene(frame, frame_idx):
    # Money Bag
    cv2.circle(frame, (160, 260), 60, (50, 180, 50), -1)
    cv2.rectangle(frame, (140, 170), (180, 210), (30, 120, 30), -1)
    cv2.putText(frame, "$$", (140, 275), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
    
    # Rising Arrow Chart
    pts = np.array([[320, 360], [400, 260], [480, 280], [560, 160]], np.int32)
    cv2.polylines(frame, [pts], False, (0, 255, 255), 5)
    cv2.arrowedLine(frame, (480, 280), (560, 160), (0, 255, 255), 6, tipLength=0.3)

def draw_safe_python_scene(frame, frame_idx):
    # Python Logo branding (blue & yellow interlocking graphics)
    # Laptop screen graphic
    cv2.rectangle(frame, (180, 140), (460, 320), (220, 220, 220), -1)
    cv2.rectangle(frame, (200, 160), (440, 300), (30, 30, 50), -1)
    # Laptop base
    cv2.rectangle(frame, (140, 320), (500, 340), (180, 180, 180), -1)
    
    # Code text lines on laptop screen
    cv2.putText(frame, "def learn_python():", (210, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 255, 50), 1)
    cv2.putText(frame, "    print('Hello Kids!')", (210, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 50), 1)
    cv2.putText(frame, "    shapes = ['circle', 'square']", (210, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 100, 255), 1)
    cv2.putText(frame, "    return True", (210, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 200, 255), 1)
    
    # Geometric shapes (Triangle, Circle, Square)
    cv2.circle(frame, (90, 240), 30, (255, 100, 50), -1)
    cv2.rectangle(frame, (530, 210), (590, 270), (50, 100, 255), -1)

TEST_MEDIA_RICH = [
    {
        "filename": "adult_18plus_ad.mp4",
        "img_filename": "adult_18plus_ad.jpg",
        "title": "Intimacy Night Club",
        "lines": ["ADULT 18+ ONLY", "Intimacy, romance & sensual night", "Exclusive adult dating party"],
        "bg_color": (30, 15, 35),
        "draw_fn": draw_adult_scene
    },
    {
        "filename": "gambling_satta_ad.mp4",
        "img_filename": "gambling_satta_ad.jpg",
        "title": "Grand Casino Satta",
        "lines": ["MEGA CASINO JACKPOT", "Play slots, bet & win real cash", "Online satta khelo aur jeeto"],
        "bg_color": (15, 35, 15),
        "draw_fn": draw_gambling_scene
    },
    {
        "filename": "violence_combat_ad.mp4",
        "img_filename": "violence_combat_ad.jpg",
        "title": "Blood & Guns Action",
        "lines": ["ACTION THRILLER: BLOOD & GUNS", "Ultimate fight with weapons", "Shoot, stab & combat trailer"],
        "bg_color": (40, 10, 10),
        "draw_fn": draw_violence_scene
    },
    {
        "filename": "scam_paisa_double_ad.mp4",
        "img_filename": "scam_paisa_double_ad.jpg",
        "title": "Paisa Double Scheme",
        "lines": ["GET RICH FAST - PAISA DOUBLE", "Earn cash fast in 24 hours", "Guaranteed returns giveaway"],
        "bg_color": (45, 35, 10),
        "draw_fn": draw_scam_scene
    },
    {
        "filename": "safe_python_ad.mp4",
        "img_filename": "safe_python_ad.jpg",
        "title": "Python Coding Course",
        "lines": ["PYTHON FOR BEGINNERS & KIDS", "Learn coding step by step", "Simple geometry & math tutorial"],
        "bg_color": (25, 35, 45),
        "draw_fn": draw_safe_python_scene
    }
]

def generate_rich_visual_media(output_dir: str = "datasets/samples"):
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("  GENERATING RICH VISUAL MEDIA (GRAPHICS + OBJECTS + COPY)   ")
    print("=" * 60)
    
    for item in TEST_MEDIA_RICH:
        vid_path = os.path.join(output_dir, item["filename"])
        img_path = os.path.join(output_dir, item["img_filename"])
        
        # 1. Create H.264 Video Writer
        writer = imageio.get_writer(vid_path, fps=10, codec="libx264", pixelformat="yuv420p")
        
        # Render 30 animated frames (3 sec)
        for i in range(30):
            frame = np.ones((480, 640, 3), dtype=np.uint8)
            frame[:, :] = item["bg_color"]
            
            # Draw visual scene objects/graphics
            item["draw_fn"](frame, i)
            
            # Draw text overlays
            cv2.putText(frame, item["title"], (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
            cv2.line(frame, (30, 60), (610, 60), (200, 200, 200), 2)
            
            for idx, line in enumerate(item["lines"]):
                cv2.putText(frame, line, (30, 410 + (idx * 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
            writer.append_data(frame)
            if i == 15:
                # Save middle frame as JPG Image
                cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                
        writer.close()
        vsize = os.path.getsize(vid_path) / 1024
        isize = os.path.getsize(img_path) / 1024
        print(f"  [OK] Generated Rich Video: {item['filename']} ({vsize:.1f} KB)")
        print(f"  [OK] Generated Rich Image: {item['img_filename']} ({isize:.1f} KB)")
        
    print("=" * 60)
    print(f"Rich visual media saved successfully to: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    generate_rich_visual_media()
