import cv2
import numpy as np
import os
import math

def generate_all_reels():
    out_dir = os.path.join(os.path.dirname(__file__), "reels")
    os.makedirs(out_dir, exist_ok=True)
    
    w, h = 405, 720
    fps = 30
    duration = 5
    total_frames = fps * duration
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # 1. Cyberpunk Synthwave Reel
    p1 = os.path.join(out_dir, "reel_cyberpunk.mp4")
    if not os.path.exists(p1) or os.path.getsize(p1) < 10000:
        w1 = cv2.VideoWriter(p1, fourcc, fps, (w, h))
        for f in range(total_frames):
            t = f / fps
            img = np.zeros((h, w, 3), dtype=np.uint8)
            # Sky gradient
            for y in range(int(h * 0.65)):
                r = y / (h * 0.65)
                img[y, :] = [int(40 + 20*math.sin(t*2 + r*3)), int(10 + 10*r), int(90 - 40*r)]
            # Retro Sun
            sun_y = int(h * 0.45)
            cv2.circle(img, (int(w/2), sun_y), 75, (0, 180, 255), -1)
            cv2.circle(img, (int(w/2), sun_y), 70, (50, 220, 255), -1)
            # Sun blind stripes
            for s in range(5):
                sy = sun_y - 20 + s*16
                if 0 <= sy < h:
                    cv2.rectangle(img, (int(w/2 - 75), sy), (int(w/2 + 75), sy + 4), (30, 15, 60), -1)
            # Perspective Grid
            grid_top = int(h * 0.65)
            cv2.rectangle(img, (0, grid_top), (w, h), (15, 5, 25), -1)
            vanish_x = int(w / 2)
            for gx in range(-w, 2*w, 50):
                target_x = int(vanish_x + (gx - vanish_x) * 2.2)
                cv2.line(img, (vanish_x, grid_top), (target_x, h), (255, 0, 200), 2)
            for gy in range(8):
                frac = (gy + (t * 1.5) % 1.0) / 8.0
                curr_y = int(grid_top + (h - grid_top) * (frac ** 2))
                cv2.line(img, (0, curr_y), (w, curr_y), (255, 50, 150), 2)
            w1.write(img)
        w1.release()

    # 2. Aurora Borealis & Cosmic Night Reel
    p2 = os.path.join(out_dir, "reel_aurora.mp4")
    if not os.path.exists(p2) or os.path.getsize(p2) < 10000:
        w2 = cv2.VideoWriter(p2, fourcc, fps, (w, h))
        np.random.seed(42)
        star_x = np.random.randint(0, w, 120)
        star_y = np.random.randint(0, int(h * 0.8), 120)
        star_b = np.random.randint(150, 255, 120)
        for f in range(total_frames):
            t = f / fps
            img = np.zeros((h, w, 3), dtype=np.uint8)
            # Midnight blue gradient
            for y in range(h):
                r = y / h
                img[y, :] = [int(25 + 15*r), int(10 + 10*r), int(15 + 5*r)]
            # Twinkling stars
            for sx, sy, sb in zip(star_x, star_y, star_b):
                twinkle = int(sb * (0.7 + 0.3 * math.sin(t * 4 + sx)))
                cv2.circle(img, (sx, sy), 1, (twinkle, twinkle, twinkle), -1)
            # Aurora curtain waves
            for x in range(0, w, 2):
                wave_y = int(h * 0.45 + 50 * math.sin(x*0.02 + t*2) + 30 * math.cos(x*0.015 - t*1.5))
                glow = int(120 + 80 * math.sin(x*0.01 + t))
                cv2.line(img, (x, max(0, wave_y - 90)), (x, wave_y + 40), (glow, 220, 40), 2)
            # Mountains silhouette
            pts = [(0, h)]
            for mx in range(0, w + 20, 20):
                my = int(h * 0.8 - 40 * math.sin(mx * 0.03) - 20 * math.cos(mx * 0.01))
                pts.append((mx, my))
            pts.append((w, h))
            cv2.fillPoly(img, [np.array(pts)], (10, 8, 12))
            w2.write(img)
        w2.release()

    # 3. Sunset Ocean Waves Reel
    p3 = os.path.join(out_dir, "reel_sunset_ocean.mp4")
    if not os.path.exists(p3) or os.path.getsize(p3) < 10000:
        w3 = cv2.VideoWriter(p3, fourcc, fps, (w, h))
        for f in range(total_frames):
            t = f / fps
            img = np.zeros((h, w, 3), dtype=np.uint8)
            # Golden hour sky gradient: deep magenta to blazing orange
            for y in range(int(h * 0.55)):
                r = y / (h * 0.55)
                b = int(10 + 30 * (1 - r))
                g = int(80 + 100 * r)
                r_c = int(220 + 35 * r)
                img[y, :] = [b, g, r_c]
            # Sinking sun
            sun_y = int(h * 0.48)
            cv2.circle(img, (int(w/2), sun_y), 45, (120, 240, 255), -1)
            # Water surface with shimmer
            for y in range(int(h * 0.55), h):
                dy = y - int(h * 0.55)
                shimmer = int(35 * math.sin(dy * 0.3 + t * 4))
                wave_b = max(0, min(255, int(150 + dy * 0.2 + shimmer * 0.5)))
                wave_g = max(0, min(255, int(80 + dy * 0.15 + shimmer)))
                wave_r = max(0, min(255, int(40 + dy * 0.1)))
                img[y, :] = [wave_b, wave_g, wave_r]
                # Sunlight path reflection on water
                center_dist = abs(int(w/2) - (w//2))
                ref_w = int(20 + dy * 0.6 + 15 * math.sin(dy * 0.2 + t * 5))
                cv2.line(img, (int(w/2 - ref_w), y), (int(w/2 + ref_w), y), (140, 220, 255), 1)
            w3.write(img)
        w3.release()

    # 4. Urban Light Trails / Street Vibes Reel
    p4 = os.path.join(out_dir, "reel_urban_lights.mp4")
    if not os.path.exists(p4) or os.path.getsize(p4) < 10000:
        w4 = cv2.VideoWriter(p4, fourcc, fps, (w, h))
        for f in range(total_frames):
            t = f / fps
            img = np.zeros((h, w, 3), dtype=np.uint8)
            # Dark city ambient
            for y in range(h):
                img[y, :] = [15, 12, 10]
            # Speed streaks (light trails)
            for i in range(12):
                lane_x = int(w * 0.15 + (i / 12.0) * w * 0.7)
                trail_y = int((h * 0.1 + (i * 90 + t * 450)) % h)
                color = (255, 180, 50) if i % 2 == 0 else (50, 60, 255)
                cv2.line(img, (lane_x, trail_y), (lane_x + int(15 * math.sin(t + i)), min(h, trail_y + 110)), color, 4)
            # Vignette glow
            cv2.circle(img, (int(w/2), int(h/2)), int(w*0.7), (40, 30, 20), 2)
            w4.write(img)
        w4.release()

    print("All 4 reels generated successfully in", out_dir)

if __name__ == "__main__":
    generate_all_reels()
