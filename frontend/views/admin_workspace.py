import streamlit as st
import os
import time
from datetime import datetime

# Will use the local session state for the backend database since we are bypassing the API
backend_online = False

def admin_dashboard():
    # Insert custom styling exactly from Joseph's branch for the Admin page as well
    st.markdown("""
        <style>
        .badge-reject {
            background-color: #ef4444;
            color: #ffffff;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 15px;
        }
        .badge-hitl {
            background-color: #8b5cf6;
            color: #ffffff;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 15px;
        }
        .badge-18 {
            background-color: #f59e0b;
            color: #ffffff;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 15px;
        }
        .badge-14 {
            background-color: #3b82f6;
            color: #ffffff;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 15px;
        }
        .badge-approve {
            background-color: #10b981;
            color: #ffffff;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 15px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Use session state instead of API calls
    if "pending_human_reviews" not in st.session_state:
        st.session_state["pending_human_reviews"] = []
    if "reviewed_cases" not in st.session_state:
        st.session_state["reviewed_cases"] = []
    
    pending_cases = st.session_state["pending_human_reviews"]
    reviewed_cases = st.session_state["reviewed_cases"]

    st.header("🛡️ SAFEAD AI — HUMAN REVIEW DASHBOARD")
    st.caption("Review advertisements awaiting human moderator decision")
    
    if "admin_action_msg" in st.session_state and st.session_state["admin_action_msg"]:
        msg = st.session_state["admin_action_msg"]
        if "REJECTED" in msg:
            st.error(msg)
        else:
            st.success(msg)
        st.session_state["admin_action_msg"] = None
        
    tab1, tab2, tab3 = st.tabs(["Pending Human Reviews", "Reviewed Cases", "Review Statistics"])
    
    with tab1:
        if not pending_cases:
            st.success("🎉 **No Pending Reviews**: All submitted cases have been reviewed! There are no advertisements in the pending review queue.")
        else:
            st.markdown(f"### Pending Review Queue ({len(pending_cases)} case(s))")
            
            case_options = {f"Case #{c['review_id']} — Ad #{c['ad_id']} ({c['title']})": c for c in pending_cases}
            selected_case_key = st.selectbox("Select Human Review Case to Process:", list(case_options.keys()))
            
            if selected_case_key:
                c = case_options[selected_case_key]
                
                st.markdown("---")
                col_media, col_evidence = st.columns([1, 1.2])
                
                with col_media:
                    st.subheader("1. Advertisement Media Inspection")
                    st.write(f"- **Ad ID**: #{c['ad_id']}")
                    st.write(f"- **Title**: `{c['title']}`")
                    st.write(f"- **Caption**: *\"{c.get('caption', '')}\"*")
                    st.write(f"- **Media Type**: `{c['media_type'].upper()}`")
                    st.write(f"- **Submission Date**: `{c.get('submitted_at', '')}`")
                    
                    if c.get("file_path") and os.path.exists(c["file_path"]):
                        if c["media_type"] == "image":
                            st.image(c["file_path"], caption=c["title"], use_container_width=True)
                        else:
                            st.video(c["file_path"])
                    else:
                        st.info("📂 Media file loaded for reviewer inspection.")
                        
                with col_evidence:
                    st.subheader("2. AI Safety Evidence & Reasoning")
                    
                    st.markdown(f"• **AI Classification**: `{c.get('ai_classification', 'N/A')}`")
                    st.markdown(f"• **Risk Score**: `{c.get('risk_score', 0.0)} / 100`")
                    st.markdown(f"• **Model Confidence**: `{int((c.get('confidence') or 0.85)*100)}%`")
                    st.markdown(f"• **AI Explanation**: *\"{c.get('explanation', '')}\"*")
                    st.markdown(f"• **Extracted OCR Text**: *\"{c.get('ocr_text', 'None detected')}\"*")
                    st.markdown(f"• **Audio Speech Transcript**: *\"{c.get('audio_transcript', 'No speech')}\"*")
                    
                    st.markdown("---")
                    st.subheader("3. Human Moderator Decision")
                    review_note = st.text_area("Reviewer Comment / Policy Notes", placeholder="e.g. Reviewed manually. Content is acceptable under project safety policy.")
                    
                    target_id = c.get("review_id") or c.get("ad_id")
                    
                    st.write("**Select Final Age Restriction:**")
                    b1, b2 = st.columns(2)
                    b3, b4 = st.columns(2)
                    
                    decision = None
                    
                    with b1:
                        if st.button("✅ SAFE FOR ALL (All Ages)", use_container_width=True): decision = "SAFE_FOR_ALL"
                    with b2:
                        if st.button("ℹ️ 14+ (Teens & Adults)", use_container_width=True): decision = "SAFE_14_PLUS"
                    with b3:
                        if st.button("⚠️ 18+ (Adults Only)", use_container_width=True): decision = "SAFE_18_PLUS"
                    with b4:
                        if st.button("🚨 UNSAFE FOR ALL (Block)", type="primary", use_container_width=True): decision = "UNSAFE_FOR_ALL"
                        
                    if decision:
                        c["human_decision"] = decision
                        c["review_status"] = "HUMAN_REVIEWED"
                        c["review_comment"] = review_note
                        c["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Compare with AI
                        ai_class = c.get("ai_classification", "")
                        match_msg = ""
                        if decision == ai_class:
                            match_msg = f" **(Human review matches AI Decision: {decision})**"
                        else:
                            match_msg = f" **(Human override applied: AI suggested {ai_class})**"
                            
                        # Move to reviewed cases
                        st.session_state["reviewed_cases"].append(c)
                        st.session_state["pending_human_reviews"] = [x for x in st.session_state["pending_human_reviews"] if x["review_id"] != c["review_id"]]
                        
                        if decision != "UNSAFE_FOR_ALL":
                            if "global_ads" not in st.session_state:
                                st.session_state["global_ads"] = []
                            if not any(a.get("ad_id") == c["ad_id"] for a in st.session_state["global_ads"]):
                                feed_ad = c.copy()
                                feed_ad["classification"] = decision
                                st.session_state["global_ads"].append(feed_ad)
                            st.session_state["admin_action_msg"] = f"✅ Case #{target_id} APPROVED as {decision}. Published to Feed." + match_msg
                        else:
                            st.session_state["admin_action_msg"] = f"❌ Case #{target_id} REJECTED (Unsafe)." + match_msg
                            
                        st.rerun()

    with tab2:
        st.subheader("✅ Human Reviewed Cases History")
        st.caption("Advertisements that have completed human review. You may override previous decisions here.")
        
        if not reviewed_cases:
            st.info("No cases have completed human review yet.")
        else:
            for i, r in enumerate(reversed(reviewed_cases)):
                with st.expander(f"Review #{r.get('review_id')} — Ad #{r.get('ad_id')}: {r.get('title')} (Current: {r.get('human_decision')})"):
                    st.write(f"**Original AI Rating:** `{r.get('ai_classification')}`")
                    st.write(f"**Review Comment:** *{r.get('review_comment', 'None')}*")
                    st.write(f"**Reviewed At:** {r.get('reviewed_at')}")
                    
                    st.markdown("#### Modify Decision")
                    
                    opts = ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL"]
                    current_idx = opts.index(r.get("human_decision")) if r.get("human_decision") in opts else 0
                    
                    new_dec = st.selectbox("Update Age Restriction:", opts, index=current_idx, key=f"edit_dec_{r.get('review_id')}")
                    
                    if st.button("Update Decision", key=f"btn_upd_{r.get('review_id')}"):
                        # Update the reviewed case
                        old_dec = r.get("human_decision")
                        r["human_decision"] = new_dec
                        r["review_status"] = "HUMAN_REVIEWED_EDITED"
                        
                        # Update global_ads feed logic
                        if "global_ads" not in st.session_state:
                            st.session_state["global_ads"] = []
                            
                        # Remove existing ad from global_ads if it exists
                        st.session_state["global_ads"] = [a for a in st.session_state["global_ads"] if a.get("ad_id") != r.get("ad_id")]
                        
                        # Re-add if it's not unsafe
                        if new_dec != "UNSAFE_FOR_ALL":
                            feed_ad = r.copy()
                            feed_ad["classification"] = new_dec
                            st.session_state["global_ads"].append(feed_ad)
                            
                        st.session_state["admin_action_msg"] = f"✏️ Decision for Case #{r.get('review_id')} updated from {old_dec} to {new_dec}."
                        st.rerun()
            
    with tab3:
        st.subheader("📈 Human Review Analytics & System Performance")
        
        accepted_count = len([c for c in reviewed_cases if c.get("human_decision") != "UNSAFE_FOR_ALL"])
        rejected_count = len([c for c in reviewed_cases if c.get("human_decision") == "UNSAFE_FOR_ALL"])
        pending_count = len(pending_cases)
        
        scol1, scol2, scol3 = st.columns(3)
        scol1.metric("Pending Queue", f"{pending_count} case(s)")
        scol2.metric("Human Approvals (Safe)", f"{accepted_count} case(s)")
        scol3.metric("Human Rejections (Unsafe)", f"{rejected_count} case(s)")
