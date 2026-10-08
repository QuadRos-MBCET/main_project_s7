import os
import streamlit as st
import time
from pathlib import Path
from services.advertisement_service import advertisement_service
from services.auth_service import auth_service
from config.default_config import settings

def render_advertiser_portal():
    """
    Renders the Enterprise Advertiser Portal.
    Distinct corporate/enterprise styling with deep blue & slate aesthetics.
    """
    st.markdown("""
        <style>
        .advertiser-header {
            background: rgba(255, 255, 255, 0.07);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 28px;
            color: #ffffff;
            margin-bottom: 24px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(168, 85, 247, 0.2);
        }
        .advertiser-title {
            font-size: 28px;
            font-weight: 800;
            color: #ffffff;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .advertiser-subtitle {
            font-size: 14px;
            color: #e9d5ff;
            margin-top: 6px;
        }
        .ad-card {
            background: rgba(255, 255, 255, 0.06);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 20px;
            color: #ffffff;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }
        .badge-safe {
            background-color: #dcfce7;
            color: #166534;
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 12px;
        }
        .badge-14 {
            background-color: #fef9c3;
            color: #854d0e;
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 12px;
        }
        .badge-18 {
            background-color: #ffedd5;
            color: #9a3412;
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 12px;
        }
        .badge-unsafe {
            background-color: #fee2e2;
            color: #991b1b;
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="advertiser-header">
            <div class="advertiser-title">🏢 Enterprise Advertiser Hub</div>
            <div class="advertiser-subtitle">Pre-Publication Ad Compliance, AI Safety Audit & Campaign Management</div>
        </div>
    """, unsafe_allow_html=True)

    # Session State Authentication for Advertiser
    if "adv_logged_in" not in st.session_state:
        st.session_state["adv_logged_in"] = True
        st.session_state["adv_user"] = "corporate_advertiser"
        st.session_state["adv_user_id"] = 1

    # Main Tabs: 1. Upload & Audit, 2. Campaign Dashboard
    tab_upload, tab_dashboard = st.tabs(["🚀 Upload & Audit Ad", "📊 Campaign Analytics & History"])

    with tab_upload:
        st.subheader("Submit Advertisement Media for Pre-Publication Moderation")
        st.markdown("All media undergoes deterministic multi-modal safety evaluation across visual content, text OCR, and audio transcription.")
        
        col_form, col_preview = st.columns(2)
        
        with col_form:
            st.markdown("### Campaign Details")
            title = st.text_input("Advertisement Campaign Title", value="Global Brand Refresh Campaign", placeholder="e.g. Summer Soda Promo")
            caption = st.text_area("Ad Description & Caption", value="Refresh your senses with 100% natural, crisp mountain flavors. Limited time offer.", height=80)
            
            # Quick Sample Ad Preset Loader
            sample_dir = settings.SAMPLE_MEDIA_DIR
            sample_files = []
            if sample_dir.exists():
                sample_files = [f.name for f in sample_dir.iterdir() if f.is_file()]
                
            use_sample = st.checkbox("📁 Use pre-bundled sample ad from repository", value=False)
            selected_sample = None
            uploaded_file = None
            
            if use_sample and sample_files:
                selected_sample = st.selectbox("Select Benchmark Sample Ad", sample_files)
                st.caption(f"Loaded from: assets/sample_media/{selected_sample}")
            else:
                uploaded_file = st.file_uploader("Upload Ad Media (Image or Video)", type=["png", "jpg", "jpeg", "mp4", "mov", "avi", "webm", "mkv"])

            submit_btn = st.button("🔍 Submit for AI Moderation", type="primary", use_container_width=True)

        with col_preview:
            st.markdown("### Media Preview")
            preview_path = None
            if use_sample and selected_sample:
                preview_path = sample_dir / selected_sample
            elif uploaded_file is not None:
                # Save temp preview
                temp_path = settings.UPLOAD_DIR / f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                preview_path = temp_path

            if preview_path and os.path.exists(preview_path):
                ext = os.path.splitext(preview_path)[1].lower()
                if ext in [".mp4", ".mov", ".avi"]:
                    st.video(str(preview_path))
                else:
                    st.image(str(preview_path), use_container_width=True)
            else:
                st.info("Upload media or select a sample ad to preview here.")

        # Handle Submission
        if submit_btn:
            media_source = None
            filename = ""
            
            if use_sample and selected_sample:
                media_source = sample_dir / selected_sample
                filename = selected_sample
            elif uploaded_file is not None:
                filename = uploaded_file.name
                media_source = uploaded_file.getbuffer()
            else:
                st.error("Please provide an advertisement media file.")
                return

            with st.spinner("Executing SafeAd AI Multi-Modal Moderation Engine (Vision, OCR, Speech, Fusion)..."):
                start_t = time.time()
                res = advertisement_service.upload_advertisement(
                    file_path_or_bytes=media_source,
                    filename=filename,
                    title=title,
                    caption=caption,
                    user_id=st.session_state["adv_user_id"]
                )
                duration = round(time.time() - start_t, 2)

            if res.get("success"):
                data = res["data"]
                st.session_state["latest_ad_submission"] = data
                st.success(f"Audit completed in {duration}s!")
            else:
                st.error(f"Moderation failed: {res.get('error')}")

        # Display AI Moderation Feedback
        if "latest_ad_submission" in st.session_state:
            data = st.session_state["latest_ad_submission"]
            ad_id = data.get("ad_id")
            category = data.get("application_category", "UNSAFE FOR ALL")
            is_rejected = data.get("is_rejected", False)
            risk_score = data.get("risk_score", 0.0)
            confidence = data.get("confidence", 0.85)
            action = data.get("publication_action", "REJECT")
            explanation = data.get("explanation", "Audit completed.")

            st.markdown("---")
            st.subheader(f"📋 AI Moderation Report — Ad #{ad_id}")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Platform Classification", category)
            with c2:
                st.metric("Risk Score", f"{risk_score:.1f} / 100")
            with c3:
                st.metric("Model Confidence", f"{confidence:.1%}")
            with c4:
                status_color = "red" if is_rejected else ("green" if category == "SAFE FOR ALL" else "orange")
                st.metric("Publication Status", action)

            # Rejection Alert for UNSAFE FOR ALL
            if is_rejected:
                st.error(f"""
                    ⛔ **ADVERTISEMENT REJECTED — UNSAFE FOR ALL**  
                    This advertisement violates safety policies and has been classified as **{category}**.  
                    It will **NEVER** enter normal ad delivery and cannot be viewed by users.
                """)
            else:
                st.success(f"✅ Advertisement Pre-Approved with Category: **{category}** ({action}).")

            st.markdown(f"**AI Policy Explanation:** {explanation}")

            # Section 9: Advertiser Decision Flow
            st.markdown("### Advertiser Decision Workflow")
            col_accept, col_dispute = st.columns(2)
            
            with col_accept:
                st.markdown("#### Option A: Accept Classification")
                st.markdown("Proceed with the current AI classification into approved ad delivery store.")
                if st.button("✅ Accept & Finalize Ad", key=f"accept_{ad_id}", use_container_width=True):
                    st.success("Ad classification accepted! Ad is queued for age-appropriate delivery.")

            with col_dispute:
                st.markdown("#### Option B: Request Human Review")
                st.markdown("If you believe the AI classification is incorrect, request manual evaluation by our moderation team.")
                dispute_reason = st.text_input("Reason for human review", placeholder="e.g. Mild cartoon action was misclassified as violence", key=f"disp_reason_{ad_id}")
                if st.button("🛡️ Submit for Human Review", key=f"req_rev_{ad_id}", type="secondary", use_container_width=True):
                    if not dispute_reason.strip():
                        st.warning("Please provide a brief reason for the review request.")
                    else:
                        rev_res = advertisement_service.request_human_review(ad_id, dispute_reason)
                        if rev_res.get("success"):
                            st.info("Advertisement has been moved to the Human Moderation Review Queue.")
                        else:
                            st.error(rev_res.get("error"))

    with tab_dashboard:
        col_title, col_wipe = st.columns([3, 1])
        with col_title:
            st.subheader("Advertiser Campaign Portfolio")
        with col_wipe:
            if st.button("🗑️ Remove All Ads", key="btn_wipe_all_ads", type="secondary", use_container_width=True):
                wipe_res = advertisement_service.delete_all_advertisements()
                if wipe_res.get("success"):
                    st.toast("✅ All uploaded advertisements removed successfully!")
                    st.rerun()
                else:
                    st.error(wipe_res.get("error"))

        history = advertisement_service.get_moderation_history(limit=50)
        
        if not history:
            st.info("No advertisements submitted yet. Use the 'Upload & Audit Ad' tab to start.")
        else:
            for item in history:
                ad_id = item.get("ad_id")
                raw_cls = item.get("final_classification") or item.get("classification")
                app_cat = item.get("application_category", "UNSAFE FOR ALL")
                status = item.get("publication_action", "PENDING")
                is_rej = item.get("is_rejected", False)
                req_rev = item.get("requires_human_review", False)
                
                with st.expander(f"Campaign Ad #{ad_id} — {app_cat} ({status})", expanded=False):
                    c_info, c_action = st.columns([2, 1])
                    with c_info:
                        st.write(f"**Classification:** {app_cat}")
                        st.write(f"**AI Confidence:** {item.get('confidence', 0.85):.1%}")
                        st.write(f"**Risk Score:** {item.get('risk_score', 0.0):.1f}/100")
                        st.write(f"**Explanation:** {item.get('explanation')}")
                        if is_rej:
                            st.markdown("🔴 **STATUS: REJECTED (Unsafe for All Users)**")
                        elif req_rev:
                            st.markdown("🟡 **STATUS: IN HUMAN REVIEW QUEUE**")
                        else:
                            st.markdown("🟢 **STATUS: APPROVED & ACTIVE**")
                    with c_action:
                        if not is_rej and not req_rev:
                            st.caption("Active in Delivery Engine")
                        elif req_rev:
                            st.caption("Awaiting Human Reviewer Decision")
                        else:
                            st.caption("Blocked by Safety Policy")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"🗑️ Delete Ad #{ad_id}", key=f"btn_delete_ad_{ad_id}", use_container_width=True):
                            del_res = advertisement_service.delete_advertisement(ad_id)
                            if del_res.get("success"):
                                st.toast(f"✅ Advertisement #{ad_id} deleted!")
                                st.rerun()
                            else:
                                st.error(del_res.get("error"))
