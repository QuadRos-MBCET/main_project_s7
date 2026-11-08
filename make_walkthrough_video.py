import asyncio
import os
import time
import math
import subprocess
import imageio_ffmpeg
import edge_tts
from playwright.sync_api import sync_playwright

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
VOICE_PATH = "walkthrough_voiceover.mp3"
RAW_VIDEO_DIR = "raw_record"
FINAL_VIDEO_PATH = "safead_ai_walkthrough_60fps.mp4"

# ---------------------------------------------------------------------------
# 1. GENERATE PROFESSIONAL NEURAL VOICEOVER
# ---------------------------------------------------------------------------
async def generate_voiceover():
    print("[1/3] Generating synchronized 30s neural voiceover...")
    script = (
        "Welcome to SafeAd AI, an enterprise multimodal content safety platform. "
        "The User Platform features biometric age verification, serving verified feeds and short-form reels with dynamic safety filters. "
        "In Advertiser Studio, brand owners audit creatives across images, videos, and PDFs with real-time risk scoring. "
        "The Compliance Admin desk provides human-in-the-loop oversight to adjudicate policy escalations. "
        "SafeAd AI: smarter ad moderation starts here."
    )
    # Calibrated rate for crystal clear pacing
    communicate = edge_tts.Communicate(script, "en-US-ChristopherNeural", rate="+11%")
    await communicate.save(VOICE_PATH)
    print(f"Voiceover saved to {VOICE_PATH}")

# ---------------------------------------------------------------------------
# 2. INJECTED REALISTIC HUMAN POINTER CURSOR
# ---------------------------------------------------------------------------
CURSOR_INJECTION_JS = """
(() => {
    let c = document.getElementById('__human_cursor__');
    if (!c) {
        c = document.createElement('div');
        c.id = '__human_cursor__';
        c.innerHTML = `
            <svg width="26" height="26" viewBox="0 0 28 28" fill="none" style="filter: drop-shadow(0 2px 6px rgba(0,0,0,0.55));">
                <path d="M6 3L22 15L15 16.5L19 25L15.5 26.5L11.5 18L6 23.5V3Z" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.8" stroke-linejoin="round"/>
            </svg>
            <div id="__cursor_ripple__" style="position:absolute; top:-7px; left:-7px; width:40px; height:40px; border-radius:50%; border:2.5px solid #818CF8; opacity:0; pointer-events:none; transform: scale(0.3); transition: none;"></div>
        `;
        c.style.cssText = 'position:fixed; top:0; left:0; z-index:2147483647; pointer-events:none; will-change:transform; transform: translate(960px, 450px);';
        document.documentElement.appendChild(c);
    }

    window.__setCursorPos = (x, y) => {
        const el = document.getElementById('__human_cursor__');
        if (el) el.style.transform = `translate(${x}px, ${y}px)`;
    };

    window.__triggerCursorRipple = () => {
        const r = document.getElementById('__cursor_ripple__');
        if (r) {
            r.style.transition = 'none';
            r.style.transform = 'scale(0.3)';
            r.style.opacity = '1';
            requestAnimationFrame(() => {
                r.style.transition = 'transform 0.38s cubic-bezier(0.1, 0.9, 0.2, 1), opacity 0.38s ease-out';
                r.style.transform = 'scale(1.5)';
                r.style.opacity = '0';
            });
        }
    };
})();
"""

class HumanWalker:
    def __init__(self, page):
        self.page = page
        self.curr_x = 960
        self.curr_y = 450

    def ensure_cursor(self):
        try:
            self.page.evaluate(CURSOR_INJECTION_JS)
            self.page.evaluate(f"window.__setCursorPos({self.curr_x}, {self.curr_y})")
        except Exception:
            pass

    def move_to(self, target_x, target_y, duration=0.7, steps=32):
        self.ensure_cursor()
        start_x, start_y = self.curr_x, self.curr_y
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        
        # Subtle organic hand arc
        curvature = min(35.0, dist * 0.12) if dist > 80 else 0
        mid_x = (start_x + target_x) / 2 - (dy / (dist + 1e-5)) * curvature
        mid_y = (start_y + target_y) / 2 + (dx / (dist + 1e-5)) * curvature

        step_delay = duration / max(1, steps)
        for i in range(1, steps + 1):
            t = i / steps
            ease_t = t * t * (3.0 - 2.0 * t)  # Smooth cubic ease
            inv = 1.0 - ease_t
            x = inv * inv * start_x + 2.0 * inv * ease_t * mid_x + ease_t * ease_t * target_x
            y = inv * inv * start_y + 2.0 * inv * ease_t * mid_y + ease_t * ease_t * target_y
            
            try:
                self.page.evaluate(f"window.__setCursorPos({x:.1f}, {y:.1f})")
            except Exception:
                pass
            time.sleep(step_delay)

        self.curr_x = target_x
        self.curr_y = target_y
        time.sleep(0.04)

    def human_click(self, locator=None, x=None, y=None, pre_wait=0.1, post_wait=0.4):
        self.ensure_cursor()
        if locator is not None:
            box = locator.bounding_box()
            if box:
                tx = box["x"] + box["width"] * 0.5
                ty = box["y"] + box["height"] * 0.5
                self.move_to(tx, ty, duration=0.6)
            time.sleep(pre_wait)
            try:
                self.page.evaluate("window.__triggerCursorRipple()")
            except Exception:
                pass
            locator.click()
        elif x is not None and y is not None:
            self.move_to(x, y, duration=0.6)
            time.sleep(pre_wait)
            try:
                self.page.evaluate("window.__triggerCursorRipple()")
            except Exception:
                pass
            self.page.mouse.click(x, y)
        time.sleep(post_wait)

    def smooth_scroll(self, delta_y, duration=0.8, steps=28):
        self.ensure_cursor()
        step_dy = delta_y / steps
        delay = duration / steps
        for _ in range(steps):
            try:
                self.page.evaluate(f"window.scrollBy({{top: {step_dy}, behavior: 'auto'}})")
            except Exception:
                pass
            time.sleep(delay)
        time.sleep(0.1)

# ---------------------------------------------------------------------------
# 3. RECORD THE 30-SECOND WALKTHROUGH
# ---------------------------------------------------------------------------
def record_walkthrough():
    print("[2/3] Recording high-resolution human walkthrough...")
    os.makedirs(RAW_VIDEO_DIR, exist_ok=True)
    for f in os.listdir(RAW_VIDEO_DIR):
        try:
            os.remove(os.path.join(RAW_VIDEO_DIR, f))
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--hide-scrollbars",
                "--force-device-scale-factor=1"
            ]
        )
        context = browser.new_context(
            record_video_dir=RAW_VIDEO_DIR,
            record_video_size={"width": 1920, "height": 1080},
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        page.add_init_script(CURSOR_INJECTION_JS)

        walker = HumanWalker(page)

        # -------------------------------------------------------------------
        # SCENE 1: LANDING PAGE & SAFETY MONITOR (0s - 6.0s)
        # -------------------------------------------------------------------
        page.goto("http://localhost:8501")
        page.wait_for_timeout(2000)
        walker.ensure_cursor()
        walker.move_to(960, 440, duration=0.8)  # Hover over monitor showcase
        time.sleep(0.8)

        # Smooth scroll down to "Who we help" role directory
        walker.smooth_scroll(380, duration=1.0)
        time.sleep(0.5)

        # Move to User Platform card button & click
        btn_user = page.get_by_role("button", name="Access User Experience")
        walker.human_click(btn_user, pre_wait=0.1, post_wait=1.0)

        # -------------------------------------------------------------------
        # SCENE 2: USER PLATFORM & KYC & REELS (6.0s - 14.5s)
        # -------------------------------------------------------------------
        page.wait_for_timeout(800)
        walker.ensure_cursor()

        input_user = page.locator('input[type="text"]').first
        input_pwd = page.locator('input[type="password"]').first
        if input_user.count() > 0:
            box_u = input_user.bounding_box()
            if box_u:
                walker.move_to(box_u["x"] + 80, box_u["y"] + box_u["height"]/2, duration=0.45)
            input_user.fill("joseph")
            time.sleep(0.15)
            input_pwd.fill("jb")
            time.sleep(0.15)
            btn_login = page.get_by_role("button", name="Log In").last
            walker.human_click(btn_login, pre_wait=0.1, post_wait=1.4)

        # Verified user feed view: browse curated posts
        walker.ensure_cursor()
        walker.smooth_scroll(220, duration=0.8)
        time.sleep(0.6)

        # Switch to Short-Form Reels
        btn_reels = page.get_by_role("button", name="Short-Form Reels")
        if btn_reels.count() > 0:
            walker.human_click(btn_reels, pre_wait=0.1, post_wait=0.8)
            walker.ensure_cursor()
            # Click Organic Reels filter
            btn_organic = page.get_by_role("button", name="Organic Reels")
            if btn_organic.count() > 0:
                walker.human_click(btn_organic, pre_wait=0.1, post_wait=0.8)
            # Click Brand Owner Ads filter
            btn_ads = page.get_by_role("button", name="Brand Owner Ads")
            if btn_ads.count() > 0:
                walker.human_click(btn_ads, pre_wait=0.1, post_wait=0.8)

        # -------------------------------------------------------------------
        # SCENE 3: ADVERTISER STUDIO (14.5s - 22.0s)
        # -------------------------------------------------------------------
        walker.ensure_cursor()
        seg_owner = page.get_by_text("Advertiser Studio").first
        walker.human_click(seg_owner, pre_wait=0.1, post_wait=1.4)
        walker.ensure_cursor()

        # Scroll down through Creative Pre-Flight Audit studio
        walker.smooth_scroll(320, duration=1.0)
        time.sleep(0.8)
        # Hover over engine / threat detector parameters
        walker.move_to(680, 480, duration=0.8)
        time.sleep(1.2)

        # -------------------------------------------------------------------
        # SCENE 4: COMPLIANCE ADMIN GOVERNANCE DESK (22.0s - 27.0s)
        # -------------------------------------------------------------------
        seg_admin = page.get_by_text("Compliance Admin").first
        walker.human_click(seg_admin, pre_wait=0.1, post_wait=1.4)
        walker.ensure_cursor()

        # Inspect HITL Queue / Audit Logs
        walker.smooth_scroll(280, duration=1.0)
        time.sleep(0.8)
        walker.move_to(800, 420, duration=0.7)
        time.sleep(1.0)

        # -------------------------------------------------------------------
        # SCENE 5: RETURN TO HERO / OUTRO (27.0s - 31.0s)
        # -------------------------------------------------------------------
        btn_pill = page.locator('.st-key-top_portal_pill_btn button')
        if btn_pill.count() > 0:
            walker.human_click(btn_pill.first, pre_wait=0.1, post_wait=0.8)
        else:
            page.goto("http://localhost:8501")
            
        walker.ensure_cursor()
        walker.smooth_scroll(-500, duration=0.7)
        walker.move_to(960, 310, duration=0.6)
        time.sleep(2.0)

        context.close()
        browser.close()

    raw_files = [f for f in os.listdir(RAW_VIDEO_DIR) if f.endswith(".webm")]
    if not raw_files:
        raise RuntimeError("No raw video was generated by Playwright.")
    raw_video_path = os.path.join(RAW_VIDEO_DIR, raw_files[0])
    print(f"Raw video captured at: {raw_video_path}")
    return raw_video_path

# ---------------------------------------------------------------------------
# 4. ENCODE TO SILKY 60 FPS MP4 WITH VOICEOVER
# ---------------------------------------------------------------------------
def assemble_final_video(raw_video_path):
    print("[3/3] Assembling final 60 FPS video with synchronized neural voiceover...")
    proc = subprocess.run([FFMPEG_EXE, "-i", VOICE_PATH], stderr=subprocess.PIPE, text=True)
    audio_dur = 30.19
    for line in proc.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            audio_dur = float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
            break

    print(f"Sync target duration: {audio_dur:.2f}s at 60.0 FPS")

    # High-quality 60 FPS video encoding with pristine H.264 & AAC
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", raw_video_path,
        "-i", VOICE_PATH,
        "-filter_complex",
        f"[0:v]fps=60,scale=1920:1080:flags=lanczos,format=yuv420p[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "16",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{audio_dur:.2f}",
        FINAL_VIDEO_PATH
    ]
    subprocess.run(cmd, check=True)
    print(f"SUCCESS: High-FPS Walkthrough video created at: {FINAL_VIDEO_PATH}")

if __name__ == "__main__":
    asyncio.run(generate_voiceover())
    raw_vid = record_walkthrough()
    assemble_final_video(raw_vid)
