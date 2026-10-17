import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

try:
    import torch
    torch.backends.mkldnn.enabled = False
    torch.set_num_threads(1)
except Exception:
    pass

import streamlit as st
import time
import sys
import warnings
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np

warnings.filterwarnings("ignore")

# Setup sys.path to resolve Sooraj's ai.face_age and models without collision
face_age_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sooraj_face_age_core/face-age"))
if face_age_dir not in sys.path:
    sys.path.insert(0, face_age_dir)

import importlib.util
spec = importlib.util.spec_from_file_location("sooraj_classifier", os.path.join(face_age_dir, "website", "classifier.py"))
sooraj_classifier = importlib.util.module_from_spec(spec)
sys.modules["sooraj_classifier"] = sooraj_classifier
spec.loader.exec_module(sooraj_classifier)

estimate_age_from_face = sooraj_classifier.estimate_age_from_face
estimate_detailed_age_from_face = sooraj_classifier.estimate_detailed_age_from_face
detect_and_crop_face = sooraj_classifier.detect_and_crop_face
verify_id_card_and_live_face = sooraj_classifier.verify_id_card_and_live_face
process_pdf_id_document = sooraj_classifier.process_pdf_id_document
extract_dob_and_age_from_id = sooraj_classifier.extract_dob_and_age_from_id
extract_arcface_embedding = sooraj_classifier.extract_arcface_embedding
compute_similarity_from_embeddings = sooraj_classifier.compute_similarity_from_embeddings
detect_photo_spoof = sooraj_classifier.detect_photo_spoof
annotate_live_frame = sooraj_classifier.annotate_live_frame
Realtime30FPSVisionEngine = sooraj_classifier.Realtime30FPSVisionEngine

from frontend.services.safead_client import SafeAdClient

def user_dashboard():
    # Session state initialization
    if "user_page_view" not in st.session_state:
        st.session_state["user_page_view"] = "verification"  # 'verification' or 'feed'

    if "verified_age_category" not in st.session_state:
        st.session_state["verified_age_category"] = None
        st.session_state["verified_age_norm"] = None
        st.session_state["verification_data"] = None

    if "logged_in_username" not in st.session_state:
        st.session_state["logged_in_username"] = None

    if "user_db" not in st.session_state:
        st.session_state["user_db"] = {
            "demo": {"password": "demo", "category": "18 and above", "norm": "AGE_18_PLUS"},
            "souravrd": {"password": "loyola", "category": "18 and above", "norm": "AGE_18_PLUS"}
        }

    # Custom Glassmorphic & Modern CSS from Sooraj's module
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .hero-container {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
        border-radius: 16px;
        padding: 24px 30px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.3);
    }
    .hero-title {
        font-size: 30px;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 15px;
        color: #c7d2fe;
        margin-top: 6px;
    }

    .auth-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }

    .metric-card {
        background: #f8fafc;
        border-radius: 12px;
        padding: 14px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .metric-val {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-lbl {
        font-size: 12px;
        color: #64748b;
        font-weight: 500;
        margin-top: 2px;
    }

    .ig-header {
        font-size: 26px; font-weight: bold; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 15px; color: #e1306c;
    }
    .ig-post {
        border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 20px;
        background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .ig-title { font-weight: bold; font-size: 16px; margin-bottom: 5px; color: #1e293b;}
    .ig-caption { font-size: 14px; color: #334155; margin-bottom: 10px; }
    .ig-footer { font-size: 12px; color: #94a3b8; margin-top: 10px; border-top: 1px solid #f1f5f9; padding-top: 8px;}
    </style>""", unsafe_allow_html=True)

    # =========================================================================
    # VIEW 1: SOORAJ'S FULL VERIFICATION SYSTEM & LOGIN
    # =========================================================================
    if st.session_state["user_page_view"] == "verification":
        # Top Hero Section
        st.markdown("""
            <div class="hero-container">
                <div class="hero-title">🛡️ SafeAd AI — Identity Verification Platform</div>
                <div class="hero-subtitle">ID Card Biometric Verification & Live Face Cross-Matching</div>
            </div>
        """, unsafe_allow_html=True)

        # User Credentials Box
        st.markdown("""
        <div class="auth-card">
            <h4 style="margin-top:0; margin-bottom:8px; color:#1e293b;">👤 Account Credentials</h4>
            <p style="margin:0; font-size:13px; color:#64748b;">Enter your username and password below. Upon freezing the live camera and cross-matching with your ID, your account will be authenticated and accepted to log in.</p>
        </div>
        """, unsafe_allow_html=True)

        col_u1, col_u2, col_u3 = st.columns([1.5, 1.5, 1.2])
        with col_u1:
            username_input = st.text_input("Username", value=st.session_state.get("auth_username", "souravrd"), key="auth_usr_input")
        with col_u2:
            password_input = st.text_input("Password", type="password", value=st.session_state.get("auth_password", ""), key="auth_pwd_input")
        with col_u3:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            # Quick login if already registered
            db = st.session_state.get("user_db", {})
            if username_input in db and password_input and db[username_input].get("password") == password_input:
                if st.button("⚡ Quick Login", use_container_width=True, help="Log in directly with existing password"):
                    st.session_state["logged_in_username"] = username_input
                    st.session_state["verified_age_category"] = db[username_input]["category"]
                    st.session_state["verified_age_norm"] = db[username_input]["norm"]
                    st.session_state["user_page_view"] = "feed"
                    st.rerun()

        st.markdown("---")
        st.markdown("### 🆔 ID Card Verification & Live Face Cross-Matching")
        c_id, c_live = st.columns([1, 1], gap="medium")

        # ---------------------------------------------------------------------
        # 1. UPLOAD OFFICIAL ID CARD
        # ---------------------------------------------------------------------
        with c_id:
            st.markdown("#### 1. Upload Official ID Card")
            up_id = st.file_uploader("Upload ID (Image or PDF Document)", type=["jpg", "jpeg", "png", "pdf"], key="t1_id_file")
            
            id_image_np = None
            id_pdf_text = None
            extracted_dob_str = None
            id_calc_age = None
            id_cat = None
            ocr_log = ""
            
            if up_id:
                try:
                    if up_id.name.lower().endswith('.pdf'):
                        with st.spinner("Rendering PDF page and extracting document text..."):
                            id_image_np, id_pdf_text = process_pdf_id_document(up_id.getvalue())
                        if id_image_np is not None:
                            st.success(f"📄 PDF Loaded: '{up_id.name}' (First page rendered)")
                        else:
                            st.error(f"Failed to process PDF: {id_pdf_text}")
                    else:
                        up_id.seek(0)
                        pil_img = Image.open(up_id)
                        pil_img = ImageOps.exif_transpose(pil_img)
                        id_image_np = np.array(pil_img.convert("RGB"))
                except Exception as e:
                    st.error(f"Error loading uploaded ID: {e}")
                    
            if id_image_np is not None:
                st.image(id_image_np, caption="Scanned ID Card / PDF Page", width="stretch")
                
                # Immediate OCR analysis upon upload
                cache_key = f"{getattr(up_id, 'name', 'id')}_{id_image_np.shape}_{id_image_np.sum() % 1000000}"
                if st.session_state.get("cached_ocr_key") != cache_key or "cached_ocr_res" not in st.session_state:
                    with st.spinner("🔍 Reading ID Card text & Date of Birth via EasyOCR..."):
                        extracted_dob_str, id_calc_age, id_cat, ocr_log = extract_dob_and_age_from_id(id_image_np, pdf_text=id_pdf_text)
                        st.session_state["cached_ocr_key"] = cache_key
                        st.session_state["cached_ocr_res"] = (extracted_dob_str, id_calc_age, id_cat, ocr_log)
                else:
                    extracted_dob_str, id_calc_age, id_cat, ocr_log = st.session_state["cached_ocr_res"]

                # Feedback badge
                if extracted_dob_str and "Estimated" not in extracted_dob_str:
                    st.success(f"✅ **Extracted ID DOB:** **`{extracted_dob_str}`** &nbsp;|&nbsp; Age: **{id_calc_age} yrs** (`{id_cat}`)")
                else:
                    st.warning(f"⚠️ **ID Card DOB:** `{extracted_dob_str or 'Pending OCR'}` &nbsp;|&nbsp; Age: **{id_calc_age or 20} yrs** (`{id_cat or '18 and above'}`)")
                    st.caption("💡 If your ID DOB wasn't recognized cleanly from the scan, please enter your DOB below:")

                # Collapsible OCR raw transcript
                with st.expander("📄 View Raw Extracted ID Text (OCR Log)"):
                    st.text(ocr_log if ocr_log else "No text detected by OCR yet.")

            id_manual_dob = st.text_input("Optional DOB override if text blurry (DD/MM/YYYY)", value="", key="t1_dob_override")

        # ---------------------------------------------------------------------
        # 2. LIVE FACE CAMERA VIDEO STREAM & FREEZE
        # ---------------------------------------------------------------------
        with c_live:
            st.markdown("#### 2. Live Face Camera Video Stream")
            
            def _on_freeze_click():
                if "latest_live_frame" in st.session_state and st.session_state["latest_live_frame"] is not None:
                    st.session_state["frozen_live_frame"] = st.session_state["latest_live_frame"]
                    st.session_state["t1_cam_toggle"] = False
                    if "vision_engine" in st.session_state:
                        try:
                            st.session_state["vision_engine"].stop()
                        except Exception:
                            pass
                        del st.session_state["vision_engine"]

            def _on_clear_click():
                if "frozen_live_frame" in st.session_state:
                    del st.session_state["frozen_live_frame"]

            col_c1, col_c2 = st.columns([1, 1])
            with col_c1:
                st.button("📸 Freeze Current Frame", key="freeze_btn", on_click=_on_freeze_click, help="Lock current live frame for analysis & report")
            with col_c2:
                st.button("🔄 Clear Frozen Frame", key="clear_frozen_btn", on_click=_on_clear_click)

            cam_active = st.toggle("🎥 Start Live Camera Feed", value=False, key="t1_cam_toggle")

            live_image_np = st.session_state.get("frozen_live_frame", None)
            
            video_placeholder = st.empty()
            status_placeholder = st.empty()
            
            if cam_active:
                st.caption("🟢 Live Front Camera Video Active — 30 FPS ArcFace Real-Time Verification")
                
                # Seamlessly reuse or initialize vision engine so that removing or replacing an ID card
                # does NOT recreate the camera hardware session or cause DirectShow COM collisions.
                if "vision_engine" not in st.session_state or not getattr(st.session_state["vision_engine"], "running", False):
                    st.session_state["vision_engine"] = Realtime30FPSVisionEngine(id_image_np=id_image_np, target_fps=30.0)
                else:
                    st.session_state["vision_engine"].update_id_image(id_image_np)

                engine = st.session_state["vision_engine"]
                target_interval = 1.0 / 30.0  # Strict 33.33ms pacing for 30 FPS
                last_card_html = None
                loop_counter = 0
                
                while engine.running:
                    t_frame_start = time.time()
                    loop_counter += 1
                    annotated, raw_rgb, info = engine.get_annotated_frame(target_fps=30.0)
                    
                    if annotated is not None:
                        video_placeholder.image(annotated, caption="Live Front Camera Video (Locked 30 FPS | ArcFace)", width="stretch")
                        
                        is_spoof = info.get("is_spoof", False)
                        match_score = info.get("match_score")
                        is_match = info.get("is_match")
                        
                        card_html = None
                        if is_spoof:
                            score_html = ""
                            if match_score is not None:
                                score_color = "#16a34a" if is_match else "#dc2626"
                                score_tag = "✅ ArcFace Match" if is_match else "❌ ArcFace Mismatch"
                                score_html = f"""
                                <div style="border-top:1px dashed #fca5a5; margin-top:8px; padding-top:8px; display:flex; justify-content:space-between; align-items:center;">
                                    <div>
                                        <span style="font-weight:700; color:#991b1b; font-size:13px;">{score_tag} (Cross-Matched):</span><br>
                                        <span style="font-size:11px; color:#7f1d1d;">ArcFace Biometrics Computed Despite Spoof</span>
                                    </div>
                                    <div style="font-size:22px; font-weight:800; color:{score_color};">{match_score:.1%}</div>
                                </div>
                                """
                            spoof_detail = info.get("spoof_reason", "Screen/Photo Presentation Attack")
                            card_html = f"""
                            <div style="background:#fee2e2; border:1px solid #ef4444; border-radius:10px; padding:12px; margin-top:6px;">
                                <b style="color:#b91c1c; font-size:15px;">🛑 YOU ARE SHOWING A MOBILE SCREEN</b><br>
                                <span style="color:#991b1b; font-size:12px;">Photo/Screen Spoof Detected! ({spoof_detail})</span>
                                {score_html}
                            </div>
                            """
                        elif match_score is not None:
                            color = "#16a34a" if is_match else "#dc2626"
                            tag = "✅ BIOMETRICS MATCH" if is_match else "❌ BIOMETRIC MISMATCH"
                            card_html = f"""
                            <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; padding:10px; margin-top:6px; display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <span style="font-weight:700; color:{color};">{tag}</span><br>
                                    <span style="font-size:12px; color:#64748b;">ArcFace MS1MV3 Confidence [30 FPS]</span>
                                </div>
                                <div style="font-size:22px; font-weight:800; color:{color};">{match_score:.1%}</div>
                            </div>
                            """
                        else:
                            card_html = "WAITING"

                        # Throttle DOM updates to avoid WebSocket flooding and eliminate browser video lag
                        if card_html != last_card_html or (loop_counter % 15 == 0):
                            if card_html == "WAITING":
                                status_placeholder.caption("Face detected. Upload an ID Card on the left to cross-match.")
                            elif card_html is not None:
                                status_placeholder.markdown(card_html, unsafe_allow_html=True)
                            last_card_html = card_html
                            
                        st.session_state["latest_live_frame"] = raw_rgb
                        live_image_np = raw_rgb
                        
                    elapsed = time.time() - t_frame_start
                    sleep_time = max(0.001, target_interval - elapsed)
                    time.sleep(sleep_time)
                    
            else:
                if "vision_engine" in st.session_state:
                    try:
                        st.session_state["vision_engine"].stop()
                    except Exception:
                        pass
                    del st.session_state["vision_engine"]
                    
                if live_image_np is not None:
                    video_placeholder.image(live_image_np, caption="Frozen Live Camera Snapshot", width="stretch")
                else:
                    video_placeholder.markdown("""
                    <div style="border:2px dashed #cbd5e1; border-radius:14px; padding:32px; text-align:center; background:#f8fafc; margin-bottom:12px;">
                        <div style="font-size:36px; margin-bottom:8px;">🎥</div>
                        <div style="font-size:16px; font-weight:600; color:#334155;">Live Camera Feed is Off</div>
                        <div style="font-size:13px; color:#64748b;">Toggle <b>'Start Live Camera Feed'</b> above and click <b>'Freeze Current Frame'</b> to cross-match with your ID.</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Optional fallback camera snap or upload
            with st.expander("📷 Alternate: Snapshot with Camera Input or File Upload"):
                alt_cam = st.camera_input("Take Live Camera Photo", key="alt_cam_input")
                alt_file = st.file_uploader("Or Upload Live Selfie Photo", type=["jpg", "jpeg", "png"], key="alt_selfie_upload")
                if alt_cam:
                    live_image_np = np.array(Image.open(alt_cam).convert("RGB"))
                    st.session_state["frozen_live_frame"] = live_image_np
                    st.session_state["latest_live_frame"] = live_image_np
                elif alt_file:
                    live_image_np = np.array(Image.open(alt_file).convert("RGB"))
                    st.session_state["frozen_live_frame"] = live_image_np
                    st.session_state["latest_live_frame"] = live_image_np

        # =====================================================================
        # STEP 3: CROSS-MATCHING VERIFICATION & LOGIN ACCEPTANCE
        # =====================================================================
        st.markdown("---")
        st.markdown("### 📊 ID vs Live Face Cross-Matching Verdict")
        if live_image_np is None and "latest_live_frame" in st.session_state:
            live_image_np = st.session_state["latest_live_frame"]

        if id_image_np is not None and live_image_np is not None:
            with st.spinner("Cross-matching ID document with live face biometrics..."):
                effective_dob = id_manual_dob.strip() if (id_manual_dob and id_manual_dob.strip()) else (extracted_dob_str if (extracted_dob_str and "Estimated" not in extracted_dob_str) else None)
                res = verify_id_card_and_live_face(id_image_np, live_image_np, effective_dob, id_pdf_text)
            
            # Status & Anti-Spoof Warning
            if res.get("is_spoof"):
                st.error("🛑 **YOU ARE SHOWING A MOBILE SCREEN**")
                st.warning(f"⚠️ Photo/Screen Spoof Detected! ({res.get('spoof_reason')})")
            elif res.get("status") == "VERIFIED_SUCCESS":
                st.success(f"### {res.get('message')}")
            elif res.get("status") == "FAILED_FACE_MISMATCH":
                st.error(f"### {res.get('message')}")
            else:
                st.warning(f"### {res.get('message')}")

            # Side-by-side face comparison & DOB metrics
            vm1, vm2, vm3 = st.columns(3)
            with vm1:
                st.markdown("##### ID Card Face Photo")
                if res.get("id_face") is not None:
                    st.image(res["id_face"], width=130)
                st.caption(f"ID Card DOB: **{res.get('id_dob_str', 'N/A')}**")
                st.caption(f"Extracted ID Age: **{res.get('id_age', 'Unknown')} yrs** (`{res.get('id_age_category', 'Unknown')}`)")
                
            with vm2:
                st.markdown("##### Live Captured Face")
                if res.get("live_face") is not None:
                    st.image(res["live_face"], width=130)
                st.caption(f"Live ViT Predicted Age: **`{res.get('live_age_category', 'Unknown')}`**")
                
            with vm3:
                st.markdown("##### Face Similarity Score")
                st.metric("Face Match Confidence", f"{res.get('face_similarity', 0.0):.1%}")
                st.progress(float(res.get('face_similarity', 0.0)))
                st.caption(f"Biometric Model: **{res.get('model_used', 'ArcFace (MS1MV3)')}**")
                
                if res.get("face_match"):
                    st.success("✅ Facial Biometrics Match!")
                else:
                    st.error("❌ Facial Mismatch Detected!")
                    
                if res.get("dob_age_match"):
                    st.success("✅ ID DOB matches Live Face Age!")
                else:
                    st.warning("⚠️ ID DOB does not match Live Face Age!")

            # -----------------------------------------------------------------
            # ACCEPT LOGIN IF MATCHING
            # -----------------------------------------------------------------
            is_matching = res.get("face_match", False) and not res.get("is_spoof", False)
            
            st.markdown("---")
            if is_matching:
                cat = res.get("id_age_category", "18 and above")
                norm = "AGE_18_PLUS"
                if cat == "Less than 14":
                    norm = "UNDER_14"
                elif cat == "14 to 17":
                    norm = "AGE_14_TO_17"

                st.markdown("""
                <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:12px; padding:18px; margin-bottom:18px;">
                    <h3 style="color:#15803d; margin:0 0 6px 0;">🎉 Biometrics Verified: Login Accepted!</h3>
                    <p style="color:#166534; margin:0; font-size:14px;">Both the uploaded ID document and live camera face match successfully. Confirm or enter your account credentials below to enter Instakill.</p>
                </div>
                """, unsafe_allow_html=True)

                col_in1, col_in2 = st.columns(2)
                with col_in1:
                    login_user = st.text_input("Username to Log In", value=username_input or "souravrd", key="match_login_usr")
                with col_in2:
                    login_pass = st.text_input("Password to Log In", type="password", value=password_input or "", key="match_login_pwd")

                col_act1, col_act2 = st.columns([1.5, 2])
                with col_act1:
                    if st.button("🚀 Log In to Instakill Feed", type="primary", use_container_width=True):
                        if not login_user or not login_pass:
                            st.error("Please provide both Username and Password to log in.")
                        else:
                            if "user_db" not in st.session_state:
                                st.session_state["user_db"] = {}
                            st.session_state["user_db"][login_user] = {
                                "password": login_pass,
                                "category": cat,
                                "norm": norm
                            }
                            st.session_state["logged_in_username"] = login_user
                            st.session_state["verified_age_category"] = cat
                            st.session_state["verified_age_norm"] = norm
                            st.session_state["verification_data"] = res
                            st.session_state["user_page_view"] = "feed"
                            st.success(f"Verified & logged in as @{login_user}! Redirecting...")
                            st.rerun()
                with col_act2:
                    st.info(f"Verified Policy Bracket: `{norm}` ({cat}) | ID DOB: **{res.get('id_dob_str')}**")
            else:
                st.error("❌ **Login Denied**: Facial biometrics do not match or a presentation attack was detected. Please align your face clearly with your ID card and try again.")
        else:
            st.info("👈 Please **Upload an ID Card** on the left AND **Freeze the Live Camera** (or snap photo) on the right to perform biometric cross-matching and log in.")

    # =========================================================================
    # VIEW 2: AGE-AWARE SOCIAL FEED (INSTAKILL)
    # =========================================================================
    elif st.session_state["user_page_view"] == "feed":
        user_norm = st.session_state.get("verified_age_norm", "AGE_18_PLUS")
        user_cat = st.session_state.get("verified_age_category", "18 and above")
        username = st.session_state.get("logged_in_username", "User")

        st.markdown(f"<div class='ig-header'>📸 Instakill Social Feed &nbsp;<span style='font-size:14px; color:#64748b; font-weight:normal;'>Logged in as @{username}</span></div>", unsafe_allow_html=True)

        # Top Bar with Verified Status and Return Button
        c_top1, c_top2 = st.columns([3, 1])
        with c_top1:
            st.info(f"Verified Profile: **@{username}** &nbsp;|&nbsp; Age Category: **{user_cat}** &nbsp;|&nbsp; Content Filtering Policy: `{user_norm}`")
        with c_top2:
            if st.button("🔄 Return to Verification", use_container_width=True):
                st.session_state["user_page_view"] = "verification"
                st.rerun()

        # Tabs for Instagram style
        tab_home, tab_reels, tab_msg, tab_profile = st.tabs(["🏠 Home", "🎥 Reels", "✉️ Messages", "👤 Profile"])
        
        # Load ads from API or session state
        api_ads, _ = SafeAdClient.get_user_feed(user_norm)
        if api_ads and isinstance(api_ads, list):
            ads = api_ads
        else:
            global_ads = st.session_state.get("global_ads", [])
            ads = []
            for ad in global_ads:
                c = ad.get("classification", "")
                allowed = False
                if c == "SAFE_FOR_ALL": 
                    allowed = True
                elif c == "SAFE_14_PLUS" and user_norm in ["AGE_14_TO_17", "AGE_18_PLUS"]: 
                    allowed = True
                elif c == "SAFE_18_PLUS" and user_norm == "AGE_18_PLUS": 
                    allowed = True
                    
                if allowed:
                    ads.append(ad)

        with tab_reels:
            st.subheader("Explore Reels")
            if not ads:
                st.info("No reels currently available for your age category.")
            else:
                for ad in ads:
                    st.markdown("<div class='ig-post'>", unsafe_allow_html=True)
                    title = ad.get('title', 'advertisement')
                    st.markdown(f"<div class='ig-title'>@{title.replace(' ', '_').lower()}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='ig-caption'>{ad.get('caption', '')}</div>", unsafe_allow_html=True)
                    
                    filepath = ad.get("file_path")
                    if filepath and os.path.exists(filepath):
                        if filepath.lower().endswith(('.mp4', '.avi', '.mov')):
                            st.video(filepath)
                        else:
                            st.image(filepath, width="stretch")
                    else:
                        st.warning("Media preview currently unavailable.")
                        
                    st.markdown(f"<div class='ig-footer'>❤️ 1.2M &nbsp; 💬 4.5k &nbsp; 🔁 Share &nbsp; | &nbsp; 🛡️ SafeAd Policy: <b>{ad.get('classification', 'Audited')}</b></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
        with tab_home:
            st.subheader("Your Personalized Social Feed")
            st.write(f"Welcome back, **@{username}**! Check out the **Reels** tab to see age-curated content.")
            st.image("https://images.unsplash.com/photo-1611162617474-5b21e879e113?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", width="stretch", caption="Welcome to Instakill!")
            
        with tab_msg:
            st.subheader("Direct Messages")
            st.info("You have no new messages.")
            
        with tab_profile:
            st.subheader("User Profile")
            st.success(f"Verified Account: **@{username}**")
            st.markdown(f"Verified Age Profile: **{user_cat}**")
            st.markdown(f"Account Policy Group: `{user_norm}`")
            if st.session_state.get("verification_data"):
                v_data = st.session_state["verification_data"]
                st.markdown(f"- Extracted ID Age: **{v_data.get('id_age', 'N/A')} yrs**")
                st.markdown(f"- ID DOB: **{v_data.get('id_dob_str', 'N/A')}**")
                st.markdown(f"- Face Biometric Match: **{v_data.get('face_similarity', 0.0):.1%}**")
            if st.button("Log Out"):
                st.session_state["logged_in_username"] = None
                st.session_state["verified_age_category"] = None
                st.session_state["verified_age_norm"] = None
                st.session_state["verification_data"] = None
                st.session_state["user_page_view"] = "verification"
                st.rerun()
