import streamlit as st
import os
from frontend.services.safead_client import SafeAdClient

def admin_dashboard():
    st.header("🛡️ Admin Human Review Dashboard")
    st.write("Review flagged advertisements, inspect AI evidence, and make the final policy decision.")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Refresh Queue", use_container_width=True):
            st.rerun()
            
    ads, err = SafeAdClient.get_pending_reviews()
    if err:
        st.error(f"Failed to load reviews: {err}")
    elif not ads:
        st.info("Queue is empty. No pending reviews.")
    else:
        st.subheader(f"Pending Reviews ({len(ads)})")
        
        for ad in ads:
            with st.expander(f"Review Required: {ad.get('title')} (ID: {ad.get('id')})"):
                c1, c2 = st.columns(2)
                
                with c1:
                    st.markdown("#### Advertisement Media")
                    filepath = ad.get("file_path")
                    if filepath and os.path.exists(filepath):
                        if ad.get("media_type") == "video":
                            st.video(filepath)
                        else:
                            st.image(filepath, use_container_width=True)
                    else:
                        st.warning("Media missing.")
                    st.write(f"**Caption:** {ad.get('caption')}")
                
                with c2:
                    st.markdown("#### AI Classification Evidence")
                    st.metric("SafeAd AI Classification", ad.get("classification"))
                    if ad.get("risk_score"):
                        st.metric("Risk Score", f"{ad.get('risk_score')}/100")
                        
                    st.write("**XAI Explanation:**")
                    st.info(ad.get("explanation"))
                    
                    st.write("**Current Policy Status:**")
                    st.warning(ad.get("status"))
                    
                    st.markdown("#### Human Decision")
                    notes = st.text_input("Reviewer Notes", key=f"notes_{ad.get('id')}")
                    
                    rc1, rc2 = st.columns(2)
                    with rc1:
                        if st.button("✅ ACCEPT", key=f"acc_{ad.get('id')}", use_container_width=True):
                            res, e = SafeAdClient.override_ad(ad.get("id"), "APPROVE", notes or "Human accepted")
                            if e: st.error(e)
                            else: st.success("Accepted!"); st.rerun()
                    with rc2:
                        if st.button("❌ REJECT", key=f"rej_{ad.get('id')}", use_container_width=True):
                            res, e = SafeAdClient.override_ad(ad.get("id"), "REJECT", notes or "Human rejected")
                            if e: st.error(e)
                            else: st.success("Rejected!"); st.rerun()
