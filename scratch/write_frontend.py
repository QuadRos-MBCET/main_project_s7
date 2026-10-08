import os

files = {
    "frontend/auth/auth_manager.py": """import streamlit as st

def login_page():
    st.markdown("<h3 style='text-align: center;'>Select Login Workspace</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1>🏢</h1>", unsafe_allow_html=True)
        st.markdown("<h4>Advertisement Owner</h4>", unsafe_allow_html=True)
        st.markdown("<p>Submit & analyze ads</p>", unsafe_allow_html=True)
        if st.button("Login as Owner", use_container_width=True):
            st.session_state["role"] = "ADVERTISEMENT_OWNER"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1>👤</h1>", unsafe_allow_html=True)
        st.markdown("<h4>User</h4>", unsafe_allow_html=True)
        st.markdown("<p>Verify & view feed</p>", unsafe_allow_html=True)
        if st.button("Login as User", use_container_width=True):
            st.session_state["role"] = "USER"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1>🛡️</h1>", unsafe_allow_html=True)
        st.markdown("<h4>Admin</h4>", unsafe_allow_html=True)
        st.markdown("<p>Human review</p>", unsafe_allow_html=True)
        if st.button("Login as Admin", use_container_width=True):
            st.session_state["role"] = "ADMIN"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
""",
    "frontend/pages/owner_workspace.py": """import streamlit as st
from frontend.services.safead_client import SafeAdClient

def owner_dashboard():
    st.header("Advertisement Owner Dashboard")
    st.write("Upload advertisement media and submit for SafeAd AI analysis.")
    
    with st.form("upload_ad"):
        title = st.text_input("Advertisement Title")
        caption = st.text_input("Caption/Description")
        uploaded_file = st.file_uploader("Upload Ad Media (Image/Video)", type=["jpg", "jpeg", "png", "mp4"])
        submit = st.form_submit_button("Submit for Analysis")
        
        if submit and uploaded_file:
            with st.spinner("Analyzing advertisement..."):
                res, err = SafeAdClient.moderate_ad(uploaded_file, title, caption)
                if err:
                    st.error(f"Error: {err}")
                else:
                    st.success("Analysis Complete")
                    st.json(res)
""",
    "frontend/pages/user_workspace.py": """import streamlit as st
from frontend.services.face_age_client import FaceAgeClient

def user_dashboard():
    st.header("User Identity & Age Verification")
    
    if "verified_age_category" not in st.session_state:
        st.session_state["verified_age_category"] = None

    if st.session_state["verified_age_category"] is None:
        st.subheader("Step 1: ID Document Upload")
        id_file = st.file_uploader("Upload ID Document (Image/PDF)", type=["jpg", "png", "pdf"])
        
        st.subheader("Step 2: Live Face Verification")
        live_file = st.camera_input("Take a photo")
        
        if st.button("Verify Identity"):
            if id_file and live_file:
                with st.spinner("Processing cross-verification..."):
                    res, err = FaceAgeClient.verify_id_and_face(id_file, live_file)
                    if err:
                        st.error(f"Verification Failed: {err}")
                    else:
                        st.success("Verification Successful!")
                        st.json(res)
                        st.session_state["verified_age_category"] = res.get("age_category", "Unknown")
                        st.rerun()
            else:
                st.warning("Please provide both ID and Live photo.")
    else:
        st.success(f"Verified as: {st.session_state['verified_age_category']}")
        st.subheader("Age-Aware Advertisement Feed")
        st.info("Displaying safe ads for your age group...")
        # TODO: Fetch feed from SafeAdClient
""",
    "frontend/pages/admin_workspace.py": """import streamlit as st
from frontend.services.safead_client import SafeAdClient

def admin_dashboard():
    st.header("Admin Human Review Dashboard")
    
    st.subheader("Pending Reviews")
    if st.button("Refresh Queue"):
        st.rerun()
        
    ads, err = SafeAdClient.get_pending_reviews()
    if err:
        st.error(f"Failed to load reviews: {err}")
    elif not ads:
        st.info("No pending reviews.")
    else:
        for ad in ads:
            with st.expander(f"Review: {ad.get('title')} (ID: {ad.get('id')})"):
                st.write(ad)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Accept", key=f"acc_{ad.get('id')}"):
                        res, e = SafeAdClient.override_ad(ad.get("id"), "APPROVE", "Human accepted")
                        if e: st.error(e)
                        else: st.success("Accepted!"); st.rerun()
                with col2:
                    if st.button("Reject", key=f"rej_{ad.get('id')}"):
                        res, e = SafeAdClient.override_ad(ad.get("id"), "REJECT", "Human rejected")
                        if e: st.error(e)
                        else: st.success("Rejected!"); st.rerun()
""",
    "frontend/services/safead_client.py": """import requests
import os

SAFEAD_API_URL = os.getenv("SAFEAD_API_URL", "http://localhost:8000/api/v1")

class SafeAdClient:
    @staticmethod
    def moderate_ad(file, title, caption):
        url = f"{SAFEAD_API_URL}/moderation/moderate"
        try:
            files = {"file": (file.name, file.getvalue(), file.type)}
            data = {"title": title, "caption": caption, "user_id": 1}
            r = requests.post(url, files=files, data=data, timeout=60)
            if r.status_code == 200:
                return r.json(), None
            return None, r.text
        except Exception as e:
            return None, str(e)
            
    @staticmethod
    def get_pending_reviews():
        url = f"{SAFEAD_API_URL}/admin/pending"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return r.json(), None
            return None, r.text
        except Exception as e:
            return None, str(e)
            
    @staticmethod
    def override_ad(ad_id, action, notes):
        url = f"{SAFEAD_API_URL}/admin/override"
        try:
            data = {"ad_id": ad_id, "action": action, "notes": notes}
            r = requests.post(url, json=data, timeout=10)
            if r.status_code == 200:
                return r.json(), None
            return None, r.text
        except Exception as e:
            return None, str(e)
""",
    "frontend/services/face_age_client.py": """import requests
import os

FACE_AGE_API_URL = os.getenv("FACE_AGE_API_URL", "http://localhost:8001/api")

class FaceAgeClient:
    @staticmethod
    def verify_id_and_face(id_file, live_file, manual_dob=""):
        url = f"{FACE_AGE_API_URL}/verify_id_and_face"
        try:
            files = {
                "id_file": (id_file.name, id_file.getvalue(), id_file.type),
                "live_file": (live_file.name, live_file.getvalue(), live_file.type)
            }
            data = {"manual_dob": manual_dob} if manual_dob else {}
            r = requests.post(url, files=files, data=data, timeout=60)
            if r.status_code == 200:
                return r.json(), None
            return None, r.text
        except Exception as e:
            return None, str(e)
"""
}

for filepath, content in files.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Files created.")
