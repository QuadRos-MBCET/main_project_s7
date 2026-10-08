import streamlit as st
import numpy as np
from PIL import Image
import io
import base64
from services.age_registration_service import age_registration_service
from services.auth_service import auth_service
from camera_integration.camera_handler import CameraHandler

def render_registration_view():
    """
    Renders the User Registration & Biometric Age Verification view.
    Ensures camera runs ONLY during registration and stops immediately.
    """
    st.markdown("""
        <style>
        .reg-header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            padding: 24px;
            border-radius: 12px;
            color: #ffffff;
            margin-bottom: 24px;
            text-align: center;
        }
        .reg-title {
            font-size: 28px;
            font-weight: 700;
            margin: 0;
            color: #ffffff;
        }
        .reg-subtitle {
            font-size: 14px;
            color: #e0e7ff;
            margin-top: 6px;
        }
        .privacy-box {
            background-color: #f0fdf4;
            border: 1px solid #bbf7d0;
            padding: 12px 16px;
            border-radius: 8px;
            color: #166534;
            font-size: 13px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="reg-header">
            <div class="reg-title">✨ Create Your AuraFeed Account</div>
            <div class="reg-subtitle">Privacy-Preserving Age-Aware Social Experience</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="privacy-box">
            🔒 <strong>Strict Privacy Notice:</strong> Your camera is accessed <em>only once</em> during this registration step to estimate age group category for age-safe feed delivery. No raw camera frames or biometric images are permanently stored. Detection stops permanently once your account is created.
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("1. Profile Information")
        username = st.text_input("Username", placeholder="e.g. alex_travels", key="reg_uname")
        email = st.text_input("Email Address", placeholder="alex@example.com", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")
        dob = st.date_input("Date of Birth", key="reg_dob")
        dob_str = dob.strftime("%Y-%m-%d")

    with col2:
        st.subheader("2. Age Verification Snapshot")
        cam_method = st.radio(
            "Select Camera Capture Method:",
            ["📸 Live Camera Snapshot", "📁 Upload Face Photo", "🎭 Automated Face Profile (Testing)"]
        )

        image_b64 = None
        preset = None

        if cam_method == "📸 Live Camera Snapshot":
            cam_picture = st.camera_input("Capture Single Verification Photo")
            if cam_picture is not None:
                img_bytes = cam_picture.getvalue()
                image_b64 = f"data:image/jpeg;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
                st.success("Snapshot captured! Camera will stop upon submission.")

        elif cam_method == "📁 Upload Face Photo":
            uploaded_photo = st.file_uploader("Upload clear photo with single face", type=["jpg", "jpeg", "png"])
            if uploaded_photo is not None:
                img_bytes = uploaded_photo.getvalue()
                image_b64 = f"data:image/jpeg;base64,{base64.b64encode(img_bytes).decode('utf-8')}"

        else:
            preset_choice = st.selectbox(
                "Select Simulated Face Profile:",
                ["Child Face (<14)", "Teen Face (14-17)", "Adult Face (18+)"]
            )
            preset_map = {
                "Child Face (<14)": "child",
                "Teen Face (14-17)": "teen",
                "Adult Face (18+)": "adult"
            }
            preset = preset_map[preset_choice]
            synth = CameraHandler.generate_synthetic_face(preset)
            st.image(synth, caption=f"Simulated Profile: {preset_choice}", width=180)
            image_b64 = CameraHandler.frame_to_base64(synth)

    st.markdown("---")
    register_btn = st.button("🚀 Complete Registration & Stop Camera", type="primary", use_container_width=True)

    if register_btn:
        if not username or not email or not password:
            st.error("Please fill in all profile fields.")
            return

        if not image_b64 and not preset:
            st.error("Please provide a facial snapshot for age verification.")
            return

        with st.spinner("Analyzing facial geometry & estimating age category..."):
            res = age_registration_service.register_user_with_age(
                username=username,
                email=email,
                password=password,
                date_of_birth=dob_str,
                image_base64=image_b64,
                preset=preset
            )

        if res.get("success"):
            est_age = res.get("estimated_age", 25)
            cat = res.get("assigned_category", "18+")
            st.balloons()
            st.success(f"""
                🎉 **Account Created Successfully!**  
                - **Username:** {username}  
                - **Estimated Facial Age:** ~{est_age:.1f} years  
                - **Assigned Age Category:** **{cat}**  
                - **Status:** Camera deactivated permanently. You can now log into AuraFeed.
            """)
            st.session_state["feed_user"] = username
            st.session_state["feed_user_category"] = cat
            st.session_state["feed_logged_in"] = True
        else:
            st.error(f"Registration Error: {res.get('message', res.get('error'))}")
