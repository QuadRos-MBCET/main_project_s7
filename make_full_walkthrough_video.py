import asyncio
import os
import time
import math
import subprocess
import imageio_ffmpeg
import edge_tts
from playwright.sync_api import sync_playwright

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
VOICE_PATH = "full_walkthrough_voiceover.mp3"
RAW_VIDEO_DIR = "raw_record_full"
FINAL_VIDEO_PATH = "safead_ai_full_walkthrough_60fps.mp4"

# ---------------------------------------------------------------------------
# 1. GENERATE COMPREHENSIVE NEURAL VOICEOVER
# ---------------------------------------------------------------------------
async def generate_voiceover():
    print("[1/3] Generating synchronized full neural voiceover...")
    script = (
        "Welcome to SafeAd AI, an enterprise-grade multimodal ad safety and policy compliance platform. "
        "From our dark SaaS command center, teams monitor live telemetry, screened volume, and automated policy compliance across all ad distribution channels. "
        "Let us first explore the User Platform. "
        "SafeAd enforces rigorous identity onboarding with a three-step biometric KYC pipeline, combining official ID document OCR with real-time facial age estimation. "
        "Once authenticated, users access an age-verified social feed. "
        "Here, general audience content and short-form reels are strictly filtered, ensuring mature or restricted brand ads are only delivered to verified adult profiles. "
        "Next, we enter Advertiser Studio, where brand owners perform creative pre-flight audits. "
        "Powered by Strategy D hierarchical safety fusion, the engine couples deep semantic reasoning with a thirty-three dimensional local Random Forest veto. "
        "Advertisers upload images, videos, or PDFs to receive immediate threat indexing, risk scorecards, and evidence breakdowns across visual NSFW, video violence, and deceptive scam claims. "
        "Finally, the Compliance Admin desk provides human-in-the-loop oversight. "
        "Compliance officers review flagged policy escalations, inspect immutable audit logs, and maintain tamper-proof governance across campaigns. "
        "SafeAd AI: multimodal safety, biometric integrity, and automated compliance."
    )
    communicate = edge_tts.Communicate(script, "en-US-ChristopherNeural", rate="+6%")
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
        
        # Subtle natural hand arc
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
# 3. RECORD THE COMPREHENSIVE WALKTHROUGH (~92 SECONDS)
# ---------------------------------------------------------------------------
def record_walkthrough():
    print("[2/3] Recording comprehensive full project walkthrough...")
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
        # ACT 1: LANDING PAGE & LIVE TELEMETRY SHOWCASE (0s - 13s)
        # -------------------------------------------------------------------
        page.goto("http://localhost:8501")
        page.wait_for_timeout(2500)
        walker.ensure_cursor()

        # Hover over hero title & Safety Intelligence Monitor frame
        walker.move_to(960, 430, duration=0.9)
        time.sleep(1.2)
        walker.move_to(760, 480, duration=0.7)  # Over Policy Breakdown
        time.sleep(1.0)
        walker.move_to(1160, 480, duration=0.7) # Over Real-time Stream sparkline
        time.sleep(1.2)

        # Smooth scroll down to "Who we help" role directory
        walker.smooth_scroll(400, duration=1.0)
        time.sleep(1.0)

        # Move to User Platform card button & click
        btn_user = page.get_by_role("button", name="Access User Experience")
        walker.human_click(btn_user, pre_wait=0.1, post_wait=1.2)

        # -------------------------------------------------------------------
        # ACT 2: BIOMETRIC KYC & IDENTITY ONBOARDING (13s - 30s)
        # -------------------------------------------------------------------
        page.wait_for_timeout(1000)
        walker.ensure_cursor()

        # Click "New User? Register Now" to demonstrate KYC onboarding
        btn_goto_reg = page.locator('.st-key-btn_goto_register button')
        if btn_goto_reg.count() > 0:
            walker.human_click(btn_goto_reg.first, pre_wait=0.1, post_wait=1.4)
            walker.ensure_cursor()
            
            # Showcase 3-step KYC Stepper: Credentials, Official ID, Biometrics
            walker.move_to(960, 240, duration=0.8)  # KYC Stepper
            time.sleep(1.2)
            
            # Scroll down to show ID document scan & live biometric camera UI
            walker.smooth_scroll(380, duration=1.0)
            time.sleep(1.5)
            walker.move_to(650, 450, duration=0.7)  # Official ID Scan upload
            time.sleep(1.0)
            walker.move_to(1250, 450, duration=0.7) # Live ArcFace camera section
            time.sleep(1.2)

            # Return to Login via bottom return button or sidebar
            btn_ret = page.locator('.st-key-btn_back_to_signin_bottom button')
            if btn_ret.count() > 0:
                walker.smooth_scroll(200, duration=0.6)
                walker.human_click(btn_ret.first, pre_wait=0.1, post_wait=1.2)
            else:
                btn_sidebar_login = page.get_by_role("button", name="🔑 Log In").first
                walker.human_click(btn_sidebar_login, pre_wait=0.1, post_wait=1.2)

        # -------------------------------------------------------------------
        # ACT 3: SECURE USER LOGIN & AGE-GUARDED FEED (30s - 48s)
        # -------------------------------------------------------------------
        page.wait_for_timeout(800)
        walker.ensure_cursor()

        # Fill verified credentials for @joseph
        input_user = page.locator('input[type="text"]').first
        input_pwd = page.locator('input[type="password"]').first
        if input_user.count() > 0:
            box_u = input_user.bounding_box()
            if box_u:
                walker.move_to(box_u["x"] + 80, box_u["y"] + box_u["height"]/2, duration=0.45)
            input_user.fill("joseph")
            time.sleep(0.2)
            input_pwd.fill("jb")
            time.sleep(0.2)
            btn_login = page.get_by_role("button", name="Log In").last
            walker.human_click(btn_login, pre_wait=0.1, post_wait=1.5)

        # Verified user feed view: examine verified badge (@joseph ✓ AGE_18_PLUS)
        walker.ensure_cursor()
        walker.move_to(320, 210, duration=0.7)  # Over @joseph verified badge
        time.sleep(1.0)

        # Scroll curated social feed
        walker.smooth_scroll(260, duration=0.8)
        time.sleep(1.0)

        # Switch to Short-Form Reels
        btn_reels = page.get_by_role("button", name="Short-Form Reels")
        if btn_reels.count() > 0:
            walker.human_click(btn_reels, pre_wait=0.1, post_wait=1.0)
            walker.ensure_cursor()
            
            # Cycle filters: Organic Reels
            btn_organic = page.get_by_role("button", name="Organic Reels")
            if btn_organic.count() > 0:
                walker.human_click(btn_organic, pre_wait=0.1, post_wait=1.0)
                time.sleep(0.8)

            # Cycle filters: Brand Owner Ads
            btn_ads = page.get_by_role("button", name="Brand Owner Ads")
            if btn_ads.count() > 0:
                walker.human_click(btn_ads, pre_wait=0.1, post_wait=1.0)
                time.sleep(0.8)

        # -------------------------------------------------------------------
        # ACT 4: ADVERTISER STUDIO & LIVE MULTIMODAL PRE-FLIGHT (48s - 1m12s)
        # -------------------------------------------------------------------
        walker.ensure_cursor()
        seg_owner = page.get_by_text("Advertiser Studio").first
        walker.human_click(seg_owner, pre_wait=0.1, post_wait=1.5)
        walker.ensure_cursor()

        # Pre-Flight Audit View: fill creative title
        title_box = page.get_by_label("Creative Title")
        if title_box.count() > 0:
            walker.human_click(title_box, pre_wait=0.1, post_wait=0.2)
            title_box.fill("Fresh Orchard Apple Juice Campaign")
            time.sleep(0.3)

        # Upload asset: apples_ad.jpg
        ad_asset = os.path.abspath("apples_ad.jpg")
        if os.path.exists(ad_asset):
            page.locator('input[type="file"]').first.set_input_files(ad_asset)
            page.wait_for_timeout(2000)
            walker.ensure_cursor()

        # Scroll down through asset manifest and threat detector parameters
        walker.smooth_scroll(280, duration=0.8)
        time.sleep(1.0)

        # Click ANALYZE ADVERTISEMENT to run live pipeline!
        btn_analyze = page.get_by_role("button", name="ANALYZE ADVERTISEMENT")
        if btn_analyze.count() > 0:
            walker.human_click(btn_analyze.first, pre_wait=0.1, post_wait=0.5)
            # Wait for 4-stage pipeline execution
            page.wait_for_timeout(7500)
            walker.ensure_cursor()

            # Examine Scorecard: Risk Score Gauge, Verdict Badge, Evidence Matrix
            walker.smooth_scroll(280, duration=0.8)
            time.sleep(1.2)
            walker.move_to(820, 520, duration=0.6)  # Over Safety Evidence Matrix
            time.sleep(1.5)

            # Click Accept AI Decision
            btn_accept = page.get_by_role("button", name="ACCEPT AI DECISION")
            if btn_accept.count() > 0:
                walker.human_click(btn_accept.first, pre_wait=0.1, post_wait=0.8)

        # -------------------------------------------------------------------
        # ACT 5: COMPLIANCE ADMIN GOVERNANCE DESK (1m12s - 1m26s)
        # -------------------------------------------------------------------
        walker.ensure_cursor()
        seg_admin = page.get_by_text("Compliance Admin").first
        walker.human_click(seg_admin, pre_wait=0.1, post_wait=1.5)
        walker.ensure_cursor()

        # Inspect HITL Queue, Reviewed Cases, and System Performance Analytics
        walker.smooth_scroll(320, duration=1.0)
        time.sleep(1.2)
        walker.move_to(750, 440, duration=0.7)
        time.sleep(1.5)
        walker.smooth_scroll(280, duration=0.8)
        time.sleep(1.5)

        # -------------------------------------------------------------------
        # ACT 6: TELEMETRY SYNC & CLOSING OUTRO (1m26s - 1m32s)
        # -------------------------------------------------------------------
        # Return to landing showcase
        btn_pill = page.locator('.st-key-top_portal_pill_btn button')
        if btn_pill.count() > 0:
            walker.human_click(btn_pill.first, pre_wait=0.1, post_wait=0.8)
        else:
            page.goto("http://localhost:8501")

        walker.ensure_cursor()
        walker.smooth_scroll(-800, duration=0.8)
        walker.move_to(960, 420, duration=0.7)  # Over live updated Safety Monitor
        time.sleep(2.0)
        walker.move_to(960, 310, duration=0.6)  # Rest on SafeAd title
        time.sleep(2.5)

        context.close()
        browser.close()

    raw_files = [f for f in os.listdir(RAW_VIDEO_DIR) if f.endswith(".webm")]
    if not raw_files:
        raise RuntimeError("No raw video was generated by Playwright.")
    raw_video_path = os.path.join(RAW_VIDEO_DIR, raw_files[0])
    print(f"Raw video captured at: {raw_video_path}")
    return raw_video_path

# ---------------------------------------------------------------------------
# 4. ENCODE TO SILKY 60 FPS MP4 WITH SYNCHRONIZED AUDIO
# ---------------------------------------------------------------------------
def assemble_final_video(raw_video_path):
    print("[3/3] Assembling final 60 FPS video with synchronized neural voiceover...")
    proc = subprocess.run([FFMPEG_EXE, "-i", VOICE_PATH], stderr=subprocess.PIPE, text=True)
    audio_dur = 91.87
    for line in proc.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            audio_dur = float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
            break

    print(f"Sync target duration: {audio_dur:.2f}s at 60.0 FPS")

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
    print(f"SUCCESS: High-FPS Full Walkthrough video created at: {FINAL_VIDEO_PATH}")

if __name__ == "__main__":
    asyncio.run(generate_voiceover())
    raw_vid = record_walkthrough()
    assemble_final_video(raw_vid)
