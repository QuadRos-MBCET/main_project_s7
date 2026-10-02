import os
import time
import streamlit as st
from services.review_service import review_service
from services.moderation_service import moderation_service
from config.default_config import settings

def render_reviewer_portal():
    """
    Renders the Professional Human Reviewer / Moderation Portal.
    Distinct operational/cyber-security dark slate styling.
    """
    st.markdown("""
        <style>
        .reviewer-header {
            background: rgba(255, 255, 255, 0.07);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 28px;
            color: #ffffff;
            margin-bottom: 24px;
            border-left: 6px solid #f59e0b;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(245, 158, 11, 0.2);
        }
        .reviewer-title {
            font-size: 28px;
            font-weight: 800;
            color: #ffffff;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .reviewer-subtitle {
            font-size: 14px;
            color: #e9d5ff;
            margin-top: 6px;
        }
        .hitl-alert {
            background: rgba(245, 158, 11, 0.15);
            backdrop-filter: blur(12px);
            border: 1px solid #f59e0b;
            padding: 16px 20px;
            border-radius: 14px;
            color: #fef08a;
            margin-bottom: 20px;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="reviewer-header">
            <div class="reviewer-title">🛡️ SafeAd Human-in-the-Loop (HITL) Moderation Portal</div>
            <div class="reviewer-subtitle">Content Audit Review, Advertiser Dispute Resolution & Final Decision Override</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="hitl-alert">
            ⚡ <strong>Critical Reviewer Policy:</strong> Any manual classification applied by a human reviewer strictly overrides the initial AI prediction. The reviewer decision becomes the platform's <code>final_classification</code> governing live ad delivery.
        </div>
    """, unsafe_allow_html=True)

    # Fetch queued ads
    pending_ads = review_service.get_pending_reviews()

    if not pending_ads:
        st.success("🎉 No advertisements currently pending manual review. The queue is clear!")
        st.info("Advertisements appear here when flagged for review due to low model confidence, conflicting modalities, or advertiser disputes.")
    else:
        st.subheader(f"Pending Review Queue ({len(pending_ads)} items)")

        for ad in pending_ads:
            ad_id = ad.get("id")
            title = ad.get("title", f"Ad #{ad_id}")
            caption = ad.get("caption", "")
            file_path = ad.get("file_path", "")
            media_type = ad.get("media_type", "image")
            status = ad.get("status", "HUMAN_REVIEW")
            ai_cls = ad.get("classification", "REQUIRES_HUMAN_REVIEW")
            confidence = ad.get("confidence", 0.50)
            risk_score = ad.get("risk_score", 50.0)
            explanation = ad.get("explanation", "Queued for human evaluation.")

            with st.expander(f"📌 Ad #{ad_id}: {title} — Current Status: {status}", expanded=True):
                col_media, col_details = st.columns(2)

                with col_media:
                    st.markdown("#### Advertisement Media")
                    if file_path and os.path.exists(file_path):
                        ext = os.path.splitext(file_path)[1].lower()
                        if ext in [".mp4", ".mov", ".avi"]:
                            st.video(file_path)
                        else:
                            st.image(file_path, use_container_width=True)
                    else:
                        st.warning(f"Media file not found at: {file_path}")

                    st.markdown(f"**Caption:** {caption}")

                with col_details:
                    st.markdown("#### AI Moderation Telemetry")
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("AI Prediction", settings.BACKEND_TO_APP_MAP.get(ai_cls, ai_cls))
                    with m2:
                        st.metric("Risk Score", f"{risk_score:.1f}/100" if risk_score is not None else "N/A")
                    with m3:
                        st.metric("AI Confidence", f"{confidence:.1%}")

                    st.markdown(f"**Reason / Notes:** {explanation}")

                    st.markdown("---")
                    st.markdown("#### ⚖️ Human Moderator Final Decision")
                    
                    target_decision = st.selectbox(
                        "Set Final Classification:",
                        ["SAFE FOR ALL", "14+", "18+", "UNSAFE FOR ALL"],
                        key=f"target_cls_{ad_id}"
                    )
                    
                    moderator_notes = st.text_area(
                        "Moderator Rationale / Policy Justification:",
                        placeholder="e.g. Content contains mild non-harmful action suitable for 14+ audience. Overriding 18+ false alarm.",
                        key=f"mod_notes_{ad_id}"
                    )

                    override_btn = st.button(
                        f"🔒 Finalize Decision for Ad #{ad_id}",
                        type="primary",
                        key=f"btn_override_{ad_id}",
                        use_container_width=True
                    )

                    if override_btn:
                        res = review_service.submit_override_decision(
                            ad_id=ad_id,
                            target_category=target_decision,
                            moderator_notes=moderator_notes
                        )
                        if res.get("success"):
                            st.success(f"Decision saved! Final classification set to: **{target_decision}**.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(res.get("error"))
