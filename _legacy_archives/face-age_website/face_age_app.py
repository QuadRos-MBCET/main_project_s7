import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys
from pathlib import Path

# Ensure parent directory is in sys.path for website package imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from website.classifier import estimate_age_from_face, detect_and_crop_face, extract_facial_features, estimate_age_from_behavior

st.set_page_config(page_title="Face Age Estimation - SafeAd AI", layout="wide", page_icon="👤")

st.title("👤 Face Age & Behavioral Estimation Framework")
st.markdown("Early detection of age categories (Child vs. Not a Child) for age-aware content moderation.")

tab1, tab2 = st.tabs(["📸 Facial Age Classifier", "📊 Behavioral Age Classifier"])

with tab1:
    st.header("Facial Age Classification")
    input_type = st.radio("Select Input Method:", ["Upload Image File", "Use Webcam Camera", "Simulated Face Preset"])
    
    image_np = None
    
    if input_type == "Upload Image File":
        uploaded_file = st.file_uploader("Choose a photo with a face...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")
            image_np = np.array(image)
            
    elif input_type == "Use Webcam Camera":
        cam_image = st.camera_input("Capture Profile Face Photo")
        if cam_image is not None:
            image = Image.open(cam_image).convert("RGB")
            image_np = np.array(image)
            
    elif input_type == "Simulated Face Preset":
        face_choice = st.selectbox("Select Preset Face Profile", ["Child Face (Round)", "Adult Face (Oval)"])
        dummy_face = np.ones((128, 128, 3), dtype=np.uint8) * 240
        if face_choice == "Child Face (Round)":
            cv2.ellipse(dummy_face, (64, 64), (45, 45), 0, 0, 360, (255, 200, 180), -1)
            cv2.circle(dummy_face, (49, 69), 7, (40, 40, 40), -1)
            cv2.circle(dummy_face, (79, 69), 7, (40, 40, 40), -1)
        else:
            cv2.ellipse(dummy_face, (64, 64), (36, 54), 0, 0, 360, (245, 190, 160), -1)
            cv2.circle(dummy_face, (49, 54), 4, (40, 40, 40), -1)
            cv2.circle(dummy_face, (79, 54), 4, (40, 40, 40), -1)
        image_np = dummy_face
        
    if image_np is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Input Image")
            st.image(image_np, width=350)
            
        with col2:
            st.subheader("Face Detection & Age Analysis")
            cropped_face, bbox = detect_and_crop_face(image_np)
            
            st.image(cropped_face, width=160, caption="Cropped 128x128 Face")
            
            category, confidence = estimate_age_from_face(image_np)
            
            if category == "Child":
                st.warning(f"🚨 Predicted Category: **{category}**")
            else:
                st.success(f"✅ Predicted Category: **{category}**")
                
            st.metric("Child Confidence Score", f"{confidence:.1%}")
            st.progress(float(confidence))

with tab2:
    st.header("Behavioral Age Profiling")
    st.markdown("Analyze user search queries and reel watch duration to classify age group.")
    
    search_queries = st.text_input("Enter Search Queries (comma-separated):", "minecraft speedrun, cartoon videos, fun games")
    gk_watch = st.slider("Educational / GK Video Watch Time (seconds):", 0, 60, 45)
    adult_watch = st.slider("Adult / Ad Video Watch Time (seconds):", 0, 100, 10)
    
    if st.button("Run Behavioral Classification"):
        queries_list = [q.strip() for q in search_queries.split(",") if q.strip()]
        gk_watches = [{"duration_watched": gk_watch, "total_duration": 60}]
        adult_watches = [{"duration_watched": adult_watch, "total_duration": 100}]
        
        category, confidence = estimate_age_from_behavior(queries_list, gk_watches, adult_watches)
        
        st.subheader("Behavioral Analysis Results")
        if category == "Child":
            st.warning(f"🚨 Predicted Category: **{category}**")
        else:
            st.success(f"✅ Predicted Category: **{category}**")
            
        st.metric("Child Behavioral Score", f"{confidence:.1%}")
        st.progress(float(confidence))
