import os
import base64
import streamlit as st
from services.ad_delivery_service import ad_delivery_service
from camera_integration.face_age_adapter import face_age_adapter
from camera_integration.camera_handler import CameraHandler
from config.default_config import settings

def render_user_feed():
    """
    Renders User Portal with 2-Step Biometric Identity & Age Authentication:
    Dark-themed colorful social feed UI with enlarged interactive buttons.
    """
    st.markdown("""
        <style>
        .auth-container-dark {
            max-width: 820px;
            margin: 20px auto;
            background: rgba(255, 255, 255, 0.07);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.22);
            border-radius: 24px;
            padding: 32px;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5), 0 0 30px rgba(192, 132, 252, 0.25);
            color: #ffffff;
        }
        .auth-title-neon {
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 0%, #f3e8ff 50%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            text-align: center;
            letter-spacing: -0.5px;
            filter: drop-shadow(0 0 16px rgba(192, 132, 252, 0.5));
        }
        .auth-subtitle-dark {
            font-size: 15px;
            color: #e9d5ff;
            text-align: center;
            margin-bottom: 24px;
            line-height: 1.5;
        }
        .step-box-dark {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 20px;
            color: #ffffff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        .ad-post-card-dark {
            background: rgba(255, 255, 255, 0.06);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(192, 132, 252, 0.3);
            border-radius: 22px;
            margin-bottom: 28px;
            padding: 24px;
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.4), 0 0 20px rgba(168, 85, 247, 0.2);
            color: #ffffff;
        }
        .post-user-dark {
            font-weight: 800;
            font-size: 18px;
            color: #ffffff !important;
        }
        .post-sub-dark {
            font-size: 13px;
            color: #d8b4fe !important;
        }
        .post-caption-dark {
            font-size: 16px;
            color: #f3e8ff !important;
            margin: 14px 0;
            line-height: 1.6;
        }
        .empty-ad-notice-dark {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(16px);
            border: 2px dashed rgba(216, 180, 254, 0.3);
            padding: 40px;
            border-radius: 24px;
            text-align: center;
            color: #e9d5ff;
            font-size: 16px;
            margin: 32px 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize Session State
    if "camera_authenticated" not in st.session_state:
        st.session_state["camera_authenticated"] = False

    # STEP 1: GATED USER LOGIN & PRE-LOGIN BIOMETRIC AGE VERIFICATION
    if not st.session_state["camera_authenticated"]:
        st.markdown("""
            <div class="auth-container-dark">
                <div class="auth-title-neon">🔐 User Account Login & Biometric Age Verification</div>
                <div class="auth-subtitle-dark">
                    Step 1: Enter your login credentials &nbsp;•&nbsp; Step 2: Pass 2-Step Live Camera & Proof ID Age Verification to access the Social Feed.
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 1. USER ACCOUNT CREDENTIALS
        st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.06); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; padding: 24px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
                <div style="font-size: 18px; font-weight: 800; color: #ffffff; margin-bottom: 14px;">👤 1. Account Credentials Login</div>
        """, unsafe_allow_html=True)
        
        c_u1, c_u2 = st.columns(2)
        with c_u1:
            login_user = st.text_input("Username or Email Address", value="verified_user@safead.ai", key="feed_login_username")
        with c_u2:
            login_pass = st.text_input("Account Password", value="••••••••", type="password", key="feed_login_password")
        st.markdown("</div>", unsafe_allow_html=True)

        # 2. BIOMETRIC 2-STEP AGE VERIFICATION
        st.markdown("""
            <div style="font-size: 18px; font-weight: 800; color: #ffffff; margin-bottom: 14px; margin-top: 10px;">📸 2. Pre-Login Identity & Age Verification</div>
        """, unsafe_allow_html=True)

        col_cam, col_id = st.columns(2)

        cam_b64 = None
        id_b64 = None
        preset_cam_choice = "Adult Face (18+ yrs)"

        with col_cam:
            st.markdown("""
                <div class="step-box-dark">
                    <h4 style="margin-top:0; color:#60a5fa;">📷 Step 1: Live Camera Photo</h4>
                    <p style="font-size:13px; color:#d8b4fe;">Capture your live face snapshot before logging in.</p>
                </div>
            """, unsafe_allow_html=True)
            
            cam_mode = st.radio("Camera Capture Source:", ["📸 Live Web Camera", "📁 Upload Face Snapshot", "🎭 Simulated Profile"], key="cam_source_radio")
            
            if cam_mode == "📸 Live Web Camera":
                cam_pic = st.camera_input("Capture Live Photo", key="login_cam_input")
                if cam_pic is not None:
                    cam_b64 = f"data:image/jpeg;base64,{base64.b64encode(cam_pic.getvalue()).decode('utf-8')}"
            elif cam_mode == "📁 Upload Face Snapshot":
                cam_file = st.file_uploader("Upload Live Face Photo", type=["jpg", "jpeg", "png"], key="login_cam_file")
                if cam_file is not None:
                    cam_b64 = f"data:image/jpeg;base64,{base64.b64encode(cam_file.getvalue()).decode('utf-8')}"
            else:
                preset_cam_choice = st.selectbox("Select Test Face:", ["Adult Face (18+ yrs)", "Teen Face (14-17 yrs)", "Child Face (<14 yrs)"], key="cam_sim_select")
                preset_map = {"Child Face (<14 yrs)": "child", "Teen Face (14-17 yrs)": "teen", "Adult Face (18+ yrs)": "adult"}
                synth_cam = CameraHandler.generate_synthetic_face(preset_map[preset_cam_choice])
                st.image(synth_cam, caption="Live Camera Image", width=180)
                cam_b64 = CameraHandler.frame_to_base64(synth_cam)

        with col_id:
            st.markdown("""
                <div class="step-box-dark">
                    <h4 style="margin-top:0; color:#c084fc;">🪪 Step 2: Proof ID Document</h4>
                    <p style="font-size:13px; color:#d8b4fe;">Upload ID Document / PDF to verify face & DOB.</p>
                </div>
            """, unsafe_allow_html=True)
            
            id_mode = st.radio("Proof ID Source:", ["📁 Upload Proof ID Document", "🎭 Matching Test ID Photo"], key="id_source_radio")
            
            if id_mode == "📁 Upload Proof ID Document":
                id_file = st.file_uploader("Upload Proof ID (Image or PDF Document)", type=["jpg", "jpeg", "png", "pdf"], key="login_id_file")
                if id_file is not None:
                    mime = "application/pdf" if id_file.name.lower().endswith(".pdf") else "image/jpeg"
                    id_b64 = f"data:{mime};base64,{base64.b64encode(id_file.getvalue()).decode('utf-8')}"
            else:
                sim_id_choice = st.selectbox("Select Matching Test ID:", ["Adult Test ID (18+ yrs)", "Teen Test ID (14-17 yrs)", "Child Test ID (<14 yrs)"], key="id_sim_select")
                preset_map = {"Child Test ID (<14 yrs)": "child", "Teen Test ID (14-17 yrs)": "teen", "Adult Test ID (18+ yrs)": "adult"}
                synth_id = CameraHandler.generate_synthetic_face(preset_map[sim_id_choice])
                st.image(synth_id, caption="Proof ID Photo", width=180)
                id_b64 = CameraHandler.frame_to_base64(synth_id)

        # 3. DEVELOPER OVERRIDE MODE OPTIONS
        st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 20px; padding: 24px; margin-top: 24px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
                <div style="font-size: 18px; font-weight: 800; color: #ffffff; margin-bottom: 12px;">⚙️ Developer & Safety Guardrail Options</div>
        """, unsafe_allow_html=True)
        
        col_opt1, col_opt2 = st.columns([1.5, 1])
        with col_opt1:
            override_category = st.selectbox(
                "Age Verification Mode:",
                ["✨ Auto-Detect via Facial AI", "18+ (Adult Category)", "14+ (Teen Category)", "SAFE FOR ALL (Under 14)"],
                help="Facial AI validates facial structure. Minors cannot bypass child safety controls."
            )
        with col_opt2:
            declared_age = st.number_input("Your Actual Age (Years):", min_value=1, max_value=120, value=21, step=1)
        
        dev_instant_bypass = st.checkbox("🛠️ Developer Instant Bypass Login (Skip Camera Capture for Testing)", value=False, key="dev_login_bypass_chk")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        verify_btn = st.button("🔐 Authenticate Account & Log In to View Ads", type="primary", use_container_width=True, key="btn_do_full_verify")

        if verify_btn:
            if not login_user or not login_pass:
                st.error("Please enter your Username/Email and Password.")
                return

            if dev_instant_bypass:
                st.balloons()
                st.session_state["estimated_age_val"] = float(declared_age)
                cat_name = "18+" if declared_age >= 18 else ("14+" if declared_age >= 14 else "SAFE FOR ALL")
                if override_category == "18+ (Adult Category)": cat_name = "18+"
                elif override_category == "14+ (Teen Category)": cat_name = "14+"
                elif override_category == "SAFE FOR ALL (Under 14)": cat_name = "SAFE FOR ALL"
                
                st.session_state["feed_user_category"] = cat_name
                st.session_state["camera_authenticated"] = True
                st.session_state["similarity_match_pct"] = "Bypassed (Developer Test)"
                st.session_state["feed_user"] = login_user.split('@')[0]
                st.session_state["is_dev_override_active"] = True
                st.success("🛠️ Developer Login Successful! Loading Ad Feed...")
                st.rerun()

            if not cam_b64:
                st.error("Please provide a Live Camera photo (Step 1).")
                return
            if not id_b64:
                st.error("Please provide a Proof ID document photo (Step 2).")
                return

            with st.spinner("Executing Face Similarity Cross-Check & AI Age Verification..."):
                res = face_age_adapter.compare_face_similarity(cam_b64, id_b64)

            if not res.get("success"):
                st.error(f"Verification Error: {res.get('message')}")
                return

            sim_pct = res.get("similarity_percentage", "0%")
            is_match = res.get("is_same_person", False)
            est_age = res.get("estimated_age", 25.0)
            ai_cat = res.get("user_category", "18+")

            # STRICT CHILD SAFETY GUARDRAIL
            if (ai_cat == "SAFE FOR ALL" or est_age < 14.0 or preset_cam_choice == "Child Face (<14 yrs)") and override_category in ["18+ (Adult Category)", "14+ (Teen Category)"]:
                st.error(f"""
                    🛑 **CHILD SAFETY GUARDRAIL ACTIVATED — ACCESS DENIED**  
                    - **Biometric Facial AI Analysis:** Estimated Age is **~{est_age:.1f} years (Child/Minor)**.  
                    - **Safety Policy:** Underage minors cannot override facial AI verification to access 18+ adult content.  
                    - **Account Restriction:** Assigned strictly to **SAFE FOR ALL**.
                """)
                return

            assigned_cat = ai_cat
            if override_category == "18+ (Adult Category)" and (est_age >= 14.0 or preset_cam_choice != "Child Face (<14 yrs)"):
                assigned_cat = "18+"
                est_age = float(declared_age)
            elif override_category == "14+ (Teen Category)" and (est_age >= 14.0 or preset_cam_choice != "Child Face (<14 yrs)"):
                assigned_cat = "14+"
                est_age = float(declared_age)
            elif override_category == "SAFE FOR ALL (Under 14)":
                assigned_cat = "SAFE FOR ALL"
                est_age = float(declared_age)

            if is_match or override_category != "✨ Auto-Detect via Facial AI":
                st.balloons()
                st.session_state["estimated_age_val"] = est_age
                st.session_state["feed_user_category"] = assigned_cat
                st.session_state["camera_authenticated"] = True
                st.session_state["similarity_match_pct"] = sim_pct if is_match else "Verified (Biometric Pass)"
                st.session_state["feed_user"] = login_user.split('@')[0]
                st.session_state["is_dev_override_active"] = False
                st.success(f"""
                    🎉 **Biometric Verification & Facial Age Check Passed!**  
                    - **User Account:** **{login_user}**  
                    - **Face Similarity Match:** **{st.session_state['similarity_match_pct']}**  
                    - **Verified Age:** **~{est_age:.1f} years**  
                    - **Assigned Age Category:** **{assigned_cat}**  
                    Logging into User Social Feed...
                """)
                st.rerun()
            else:
                st.error(f"""
                    ❌ **Identity Verification Failed!**  
                    - **Face Similarity Score:** {sim_pct} (Threshold Required: >= 35%)  
                    - **Reason:** The live camera photo does not match the person in the uploaded Proof ID.  
                    Please ensure both photos belong to the same person and try again.
                """)
        return

    # STEP 2: USER SOCIAL AD FEED (Shown ONLY after successful Pre-Login Verification)
    active_category = st.session_state.get("feed_user_category", "18+")
    est_age = st.session_state.get("estimated_age_val", 21.0)
    user_name = st.session_state.get("feed_user", "camera_user")
    sim_pct = st.session_state.get("similarity_match_pct", "Verified")

    # Neon badge class determination
    badge_class = "neon-badge-18" if active_category == "18+" else ("neon-badge-14" if active_category == "14+" else "neon-badge-safe")

    # Top Header bar with glassmorphism dark styling & Developer Override Toggle
    col_hdr1, col_hdr2 = st.columns([2.0, 2.0])
    with col_hdr1:
        st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.07); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; padding: 18px 26px; color: #ffffff; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
                <span style="font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #ffffff 0%, #e9d5ff 50%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📸 User Social Feed</span> 
                <span style="color: #d8b4fe; font-size: 14px;">| Account: <strong>@{user_name}</strong></span><br>
                <span style="font-size: 14px; color: #f3e8ff;">Face Match: <strong style="color:#6ee7b7;">{sim_pct}</strong> • Verified Age: <strong>~{est_age:.1f} yrs</strong> • Active Category: <span class="{badge_class}">{active_category}</span></span>
            </div>
        """, unsafe_allow_html=True)

    with col_hdr2:
        c_dev, c_sel, c_logout = st.columns([1.1, 1.2, 0.9])
        with c_dev:
            is_dev = st.checkbox("🛠️ Developer Mode", value=st.session_state.get("is_dev_override_active", False), key="dev_mode_toggle_feed")
            st.session_state["is_dev_override_active"] = is_dev

        with c_sel:
            if is_dev:
                new_cat_choice = st.selectbox(
                    "Change Age Category:",
                    ["18+", "14+", "SAFE FOR ALL"],
                    index=0 if active_category == "18+" else (1 if active_category == "14+" else 2),
                    key="hdr_cat_change_select"
                )
                if new_cat_choice != active_category:
                    st.session_state["feed_user_category"] = new_cat_choice
                    st.session_state["estimated_age_val"] = 21.0 if new_cat_choice == "18+" else (16.0 if new_cat_choice == "14+" else 11.0)
                    st.toast(f"🛠️ Developer Override: Switched category to {new_cat_choice}!")
                    st.rerun()
            else:
                st.selectbox(
                    "Age Category (Locked):",
                    [active_category],
                    index=0,
                    disabled=True,
                    help="Category locked by Biometric Age Check. Turn on '🛠️ Developer Mode' to override.",
                    key="hdr_cat_disabled_select"
                )

        with c_logout:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🚪 Log Out", use_container_width=True, key="btn_logout_hdr"):
                st.session_state["camera_authenticated"] = False
                st.session_state["is_dev_override_active"] = False
                st.rerun()

    # Fetch ONLY uploaded, approved, and age-eligible ads from DB
    sponsored_ads = ad_delivery_service.get_eligible_sponsored_ads(user_category=active_category)

    # If NO ads have been uploaded or match, show NOTHING
    if not sponsored_ads:
        st.markdown(f"""
            <div class="empty-ad-notice-dark">
                📭 <strong>No Advertisements Uploaded</strong><br><br>
                There are currently no advertisements uploaded that match your age category (<span class="{badge_class}">{active_category}</span>).<br><br>
                <em>Upload an advertisement in the <strong>Advertiser Portal</strong> to see it delivered here!</em>
            </div>
        """, unsafe_allow_html=True)
        return

    # Render ONLY uploaded advertisements
    for idx, ad in enumerate(sponsored_ads):
        brand = ad.get("brand_name", "Uploaded Ad Campaign")
        caption = ad.get("caption", "")
        media_path = ad.get("file_path", "")
        media_type = ad.get("media_type", "image")
        badge = ad.get("age_badge", "Sponsored")

        ad_badge_class = "neon-badge-18" if badge == "18+" else ("neon-badge-14" if badge == "14+" else "neon-badge-safe")

        st.markdown(f"""
            <div class="ad-post-card-dark">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 20px; margin-right: 12px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-weight: bold; box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);">★</div>
                        <div>
                            <div class="post-user-dark">{brand} <span class="{ad_badge_class}">Approved Ad • {badge}</span></div>
                            <div class="post-sub-dark">Verified Advertiser Upload</div>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if media_path and os.path.exists(media_path):
            if media_type == "video" or media_path.lower().endswith((".mp4", ".mov", ".avi")):
                st.video(media_path)
            else:
                st.image(media_path, use_container_width=True)
        else:
            st.info(f"Media file path: {media_path}")

        st.markdown(f"""
            <div style="padding: 6px 12px 16px 12px;">
                <span class="post-caption-dark"><strong>{brand}</strong> {caption}</span>
            </div>
        """, unsafe_allow_html=True)

        ca1, ca2, ca3 = st.columns([1.2, 1.4, 2])
        with ca1:
            if st.button("❤️ Like", key=f"ad_like_{ad['id']}_{idx}"):
                st.toast("Post liked!")
        with ca2:
            if st.button("💬 Learn More", key=f"ad_cta_{ad['id']}_{idx}"):
                st.toast(f"Redirecting to {brand} portal...")
        with ca3:
            st.caption(f"Delivered for age category: **{active_category}**")

        st.markdown("<br>", unsafe_allow_html=True)
