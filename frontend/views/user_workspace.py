import streamlit as st
import os
import sys
import numpy as np
from PIL import Image

# Use dynamic import to avoid namespace collision with SafeAd's 'website' package
face_age_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sooraj_face_age_core/face-age"))
if face_age_dir not in sys.path:
    sys.path.insert(0, face_age_dir)

import importlib.util
spec = importlib.util.spec_from_file_location("face_age_classifier", os.path.join(face_age_dir, "website", "classifier.py"))
face_age_classifier = importlib.util.module_from_spec(spec)
sys.modules["face_age_classifier"] = face_age_classifier
spec.loader.exec_module(face_age_classifier)

process_pdf_id_document = face_age_classifier.process_pdf_id_document
verify_id_card_and_live_face = face_age_classifier.verify_id_card_and_live_face

from frontend.services.safead_client import SafeAdClient

def user_dashboard():
    st.markdown("""
    <style>
    .metric-lbl { font-size: 12px; color: #64748b; font-weight: 500; margin-top: 2px; }
    </style>""", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%); border-radius: 16px; padding: 24px 30px; color: white; margin-bottom: 24px;">
        <h2 style="margin:0; color:white;">SafeAd AI — Identity Verification Platform</h2>
        <p style="margin:0; font-size:14px; opacity:0.8;">ID Card Biometric Verification & Live Face Cross-Matching</p>
    </div>
    """, unsafe_allow_html=True)
    
    if "verified_age_category" not in st.session_state:
        st.session_state["verified_age_category"] = None
        st.session_state["verified_age_norm"] = None

    if "user_auth_mode" not in st.session_state:
        st.session_state["user_auth_mode"] = "login"
        
    if "user_db" not in st.session_state:
        st.session_state["user_db"] = {
            "demo": {"password": "demo", "category": "18 to 24", "norm": "AGE_18_PLUS"},
            "souravrd": {"password": "loyola", "category": "18 to 24", "norm": "AGE_18_PLUS"}
        }

    if st.session_state["verified_age_category"] is None:
        if st.session_state["user_auth_mode"] == "login":
            st.markdown("### 🔐 User Login")
            st.write("Welcome back! Please enter your credentials to access Instakill.")
            
            l_user = st.text_input("Username")
            l_pass = st.text_input("Password", type="password")
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("Login", type="primary", use_container_width=True):
                    db = st.session_state["user_db"]
                    if l_user in db and db[l_user]["password"] == l_pass:
                        st.session_state["verified_age_category"] = db[l_user]["category"]
                        st.session_state["verified_age_norm"] = db[l_user]["norm"]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            with c_btn2:
                if st.button("New User? Sign In", use_container_width=True):
                    st.session_state["user_auth_mode"] = "register"
                    st.rerun()
                    
        elif st.session_state["user_auth_mode"] == "register":
            st.markdown("### 📝 New User Registration")
            st.write("Please create your account and verify your age to continue.")
            
            r_user = st.text_input("Choose Username", key="reg_usr")
            r_pass = st.text_input("Choose Password", type="password", key="reg_pwd")
            
            if st.button("Already have an account? Login here"):
                st.session_state["user_auth_mode"] = "login"
                st.rerun()
                
            st.markdown("---")
            st.markdown("### 🆔 ID Card Verification & Live Face Cross-Matching")
        
            c_id, c_live = st.columns([1, 1], gap="medium")
        
            id_image_np = None
            manual_dob = None
            pdf_text = None
        
            with c_id:
                st.markdown("#### 1. Upload Official ID Card")
                st.caption("Upload ID (Image or PDF Document)")
                up_id = st.file_uploader("", type=["jpg", "jpeg", "png", "pdf"], label_visibility="collapsed")
                manual_dob = st.text_input("Optional DOB override if text blurry (DD/MM/YYYY)")
            
                if up_id:
                    if up_id.name.lower().endswith(".pdf"):
                        with st.spinner("Rendering PDF page and extracting document text..."):
                            id_image_np, pdf_text = process_pdf_id_document(up_id.getvalue())
                        if id_image_np is not None:
                            st.success(f"📄 PDF Loaded: '{up_id.name}' (First page rendered)")
                        else:
                            st.error("Failed to process PDF.")
                    else:
                        id_image_np = np.array(Image.open(up_id).convert("RGB"))
                    
                    if id_image_np is not None:
                        st.image(id_image_np, caption="Scanned ID Card / PDF Page", use_container_width=True)
                    
            live_image_np = None
            with c_live:
                st.markdown("#### 2. Live Face Camera Scan")
                cam_active = st.toggle("📷 Enable Front Camera Feed", value=True)
                if cam_active:
                    st.caption("🟢 Live Front Camera Feed Active — Tap 'Take Photo' below")
                    cam_img = st.camera_input("Live Camera Feed", label_visibility="collapsed")
                    if cam_img:
                        live_image_np = np.array(Image.open(cam_img).convert("RGB"))
                else:
                    st.markdown("""
                    <div style="border:2px dashed #cbd5e1; border-radius:14px; padding:24px; text-align:center; background:#f8fafc; margin-bottom:12px;">
                        <div style="font-size:32px; margin-bottom:6px;">📷</div>
                        <div style="font-size:15px; font-weight:600; color:#334155;">Camera is Currently Off</div>
                        <div style="font-size:12px; color:#64748b;">Toggle 'Enable Front Camera Feed' above to view feed.</div>
                    </div>
                    """, unsafe_allow_html=True)
                
            if live_image_np is not None:
                st.image(live_image_np, caption="Live Captured Face", use_container_width=True)

            st.markdown("---")
            st.markdown("### 📊 ID vs Live Face Cross-Matching Verdict")
        
            if id_image_np is not None and live_image_np is not None:
                with st.spinner("Executing Face Matching & ViT Age Estimation..."):
                    res = verify_id_card_and_live_face(id_image_np, live_image_np, manual_dob, pdf_text)
                
                    is_spoof = res.get("is_spoof", False)
                    status = res.get("status", "")
                    msg = res.get("message", "")
                
                    if is_spoof:
                        st.error("🚨 **DONT TRY TO PLAY A FOOL WITH ME NIGESH**")
                        st.warning(f"🚫 Photo/Screen Spoof Detected! ({res.get('spoof_reason')})")
                    elif status == "VERIFIED_SUCCESS":
                        st.success(f"✅ {msg}")
                    elif status == "FAILED_FACE_MISMATCH":
                        st.error(f"❌ {msg}")
                    else:
                        st.warning(f"⚠️ {msg}")
                    
                    # Side-by-side face comparison & DOB metrics
                    c_f1, c_f2, c_score = st.columns([1.2, 1.2, 1.6])
                
                    with c_f1:
                        st.markdown("**ID Card Face Photo**")
                        id_face = res.get("id_face")
                        if id_face is not None:
                            st.image(id_face, width=150)
                        else:
                            st.warning("No face detected in ID.")
                        st.markdown(f"<div class='metric-lbl'>ID Card DOB: {res.get('id_dob_str', 'N/A')}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-lbl'>Extracted ID Age: {res.get('id_age', 'Unknown')} yrs ({res.get('id_age_category', 'Unknown')})</div>", unsafe_allow_html=True)

                    with c_f2:
                        st.markdown("**Live Captured Face**")
                        live_face = res.get("live_face")
                        if live_face is not None:
                            st.image(live_face, width=150)
                        else:
                            st.warning("No live face detected.")
                        st.markdown(f"<div class='metric-lbl'>Live ViT Predicted Age: {res.get('live_age_category', 'Unknown')}</div>", unsafe_allow_html=True)

                    with c_score:
                        st.markdown("**Face Similarity Score**")
                        score = res.get("face_similarity", 0)
                        st.markdown(f"<div class='metric-lbl'>Face Match Confidence</div><div style='font-size:32px; font-weight:bold; color:#334155;'>{score*100:.1f}%</div>", unsafe_allow_html=True)
                        st.progress(float(score))
                    
                        if res.get("face_match"):
                            st.success("✅ Facial Biometrics Match!")
                        else:
                            st.error("❌ Facial Mismatch Detected!")
                        
                        if res.get("dob_age_match"):
                            st.success("✅ ID DOB matches Live Face Age!")
                        else:
                            st.error("❌ Age verification mismatch!")

                    # Set session state if successful
                    if status == "VERIFIED_SUCCESS":
                        category = res.get("id_age_category", "UNKNOWN")
                        norm_group = "AGE_18_PLUS"
                        if category == "Less than 14":
                            norm_group = "UNDER_14"
                        elif category == "14 to 17":
                            norm_group = "AGE_14_TO_17"
                        
                        st.markdown("### Complete Registration")
                        if st.button("Create Account & Enter Instakill", type="primary", use_container_width=True):
                            ru = st.session_state.get("reg_usr", "")
                            rp = st.session_state.get("reg_pwd", "")
                        
                            if not ru or not rp:
                                st.error("Please enter a username and password at the top of the form.")
                            elif ru in st.session_state["user_db"]:
                                st.error("Username already taken. Please choose another one.")
                            else:
                                st.session_state["user_db"][ru] = {
                                    "password": rp,
                                    "category": category,
                                    "norm": norm_group
                                }
                                st.session_state["verified_age_category"] = category
                                st.session_state["verified_age_norm"] = norm_group
                                st.success("Account created successfully!")
                                st.rerun()
    else:
        st.markdown("""
        <style>
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
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='ig-header'>📸 Instakill</div>", unsafe_allow_html=True)
        
        # Tabs for Instagram style
        tab_home, tab_reels, tab_msg, tab_profile = st.tabs(["🏠 Home", "🎥 Reels", "✉️ Messages", "👤 Profile"])
        
        user_norm = st.session_state["verified_age_norm"]
        global_ads = st.session_state.get("global_ads", [])
        
        # Filter ads logic based on actual norm strings
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
                    st.markdown(f"<div class='ig-title'>@{ad.get('title').replace(' ', '_').lower()}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='ig-caption'>{ad.get('caption')}</div>", unsafe_allow_html=True)
                    
                    filepath = ad.get("file_path")
                    if filepath and os.path.exists(filepath):
                        if filepath.lower().endswith(('.mp4', '.avi', '.mov')):
                            st.video(filepath)
                        else:
                            st.image(filepath, use_container_width=True)
                    else:
                        st.warning("Media missing.")
                        
                    st.markdown(f"<div class='ig-footer'>❤️ 1.2M &nbsp; 💬 4.5k &nbsp; 🔁 Share &nbsp; | &nbsp; 🛡️ SafeAd Policy: {ad.get('classification')}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
        with tab_home:
            st.subheader("Your Feed")
            st.write("Welcome to your personalized social feed! Check out the **Reels** tab to see age-curated content.")
            # A generic static image for Home
            st.image("https://images.unsplash.com/photo-1611162617474-5b21e879e113?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", use_container_width=True, caption="Welcome to Instakill!")
            
        with tab_msg:
            st.subheader("Direct Messages")
            st.info("You have no new messages.")
            
        with tab_profile:
            st.subheader("Your Profile")
            st.success(f"Verified Age Profile: **{st.session_state['verified_age_category']}**")
            st.write(f"Account Policy Group: `{user_norm}`")
            if st.button("Log Out"):
                st.session_state["verified_age_category"] = None
                st.session_state["user_auth_mode"] = "login"
                st.rerun()
