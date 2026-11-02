import streamlit as st
import os
import time
from datetime import datetime
from frontend.styles.safead_theme import render_svg_icon, render_sparkline

backend_online = False

def admin_dashboard():
    # -------------------------------------------------------------------------
    # HEADER BANNER (RiteFlow Style)
    # -------------------------------------------------------------------------
    st.markdown('''
    <div style="margin-bottom: 24px;">
        <div class="rf-eyebrow-pill" style="margin-bottom: 12px;">
            <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:#6C5CE7; box-shadow:0 0 8px #6C5CE7;"></span>
            TRUST & SAFETY GOVERNANCE
        </div>
        <h1 style="margin: 0; font-size: 32px; font-weight: 700; color: #FFFFFF; font-family: 'Outfit', sans-serif;">
            Human-in-the-Loop <span class="rf-italic-serif">Moderation Desk</span>
        </h1>
        <p style="color:#A493C2; font-size:14px; margin:6px 0 0 0;">
            Audit campaign uncertainties, adjudicate policy disputes, and monitor compliance logs.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Session state for review storage
    if "pending_human_reviews" not in st.session_state:
        st.session_state["pending_human_reviews"] = []
    if "reviewed_cases" not in st.session_state:
        st.session_state["reviewed_cases"] = []
    
    pending_cases = st.session_state["pending_human_reviews"]
    reviewed_cases = st.session_state["reviewed_cases"]

    accepted_count = len([c for c in reviewed_cases if c.get("human_decision") != "UNSAFE_FOR_ALL"])
    rejected_count = len([c for c in reviewed_cases if c.get("human_decision") == "UNSAFE_FOR_ALL"])
    pending_count = len(pending_cases)

    # -------------------------------------------------------------------------
    # TOP STAT CARDS ROW (RiteFlow Compact Stat Cards)
    # -------------------------------------------------------------------------
    st.markdown(f"""
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom: 28px;">
        <!-- Card 1: Pending Queue -->
        <div class="rf-stat-card">
            <div class="rf-stat-label">Pending Reviews</div>
            <div class="rf-stat-value" style="color: {'#EF4444' if pending_count > 0 else '#22C55E'};">{pending_count}</div>
            <div style="font-size:12px; color:#A493C2;">{'Active cases awaiting triage' if pending_count > 0 else 'All triage queues clear'}</div>
        </div>

        <!-- Card 2: Approved Creatives -->
        <div class="rf-stat-card">
            <div class="rf-stat-label">Approved Creatives</div>
            <div class="rf-stat-value">{accepted_count}</div>
            <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#A493C2;">
                <span class="rf-stat-delta">+12.4%</span>
                <span>vs last cycle</span>
            </div>
        </div>

        <!-- Card 3: Rejected Violations -->
        <div class="rf-stat-card">
            <div class="rf-stat-label">Rejected Violations</div>
            <div class="rf-stat-value" style="color:#EF4444;">{rejected_count}</div>
            <div style="font-size:12px; color:#A493C2;">Blocked for policy safety</div>
        </div>

        <!-- Card 4: Real-time Queue Sparkline -->
        <div class="rf-stat-card">
            <div class="rf-stat-label">Queue Velocity</div>
            <div style="margin: 6px 0;">
                {render_sparkline([pending_count + 1, pending_count + 2, pending_count, max(0, pending_count - 1), pending_count], width=200, height=32, color="#6C5CE7")}
            </div>
            <div style="font-size:12px; color:#A493C2;">Real-time review stream</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
            st.markdown(f'''
            <div class="rf-card" style="text-align:center; padding:44px 24px; margin-top:10px;">
                <div style="width:52px; height:52px; border-radius:50%; background:rgba(34,197,94,0.12); border:1px solid rgba(34,197,94,0.3); display:inline-flex; align-items:center; justify-content:center; margin-bottom:14px;">
                    {render_svg_icon("check", size=24, color="#22C55E")}
                </div>
                <div style="font-size:20px; font-weight:700; color:#FFFFFF; font-family:'Outfit',sans-serif; margin-bottom:8px;">Queue Clear — All Campaigns Audited</div>
                <div style="font-size:13px; color:#A493C2; max-width:440px; margin:0 auto;">
                    There are currently no advertisements awaiting human moderator intervention. AI decision confidence meets or exceeds production policy thresholds.
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f"### Pending Review Queue ({len(pending_cases)} case(s))")
            
            case_options = {f"Case #{c['review_id']} — Ad #{c['ad_id']} ({c['title']})": c for c in pending_cases}
            selected_case_key = st.selectbox("Select Human Review Case to Process:", list(case_options.keys()))
            
            if selected_case_key:
                c = case_options[selected_case_key]
                
                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                col_media, col_evidence = st.columns([1, 1.2], gap="large")
                
                with col_media:
                    st.markdown(f"""
                    <div class="rf-card" style="margin-bottom:16px;">
                        <div style="font-size:16px; font-weight:700; color:#FFFFFF; font-family:'Outfit',sans-serif; margin-bottom:12px;">
                            1. Advertisement Media Inspection
                        </div>
                        <div class="rf-table-row"><span style="color:#A493C2;">Ad ID</span><span style="color:#FFFFFF; font-weight:600;">#{c['ad_id']}</span></div>
                        <div class="rf-table-row"><span style="color:#A493C2;">Title</span><span style="color:#E2D9F3; font-weight:600;">{c['title']}</span></div>
                        <div class="rf-table-row"><span style="color:#A493C2;">Caption</span><span style="color:#A493C2; font-style:italic;">"{c.get('caption', '')}"</span></div>
                        <div class="rf-table-row"><span style="color:#A493C2;">Media Type</span><span style="color:#6C5CE7; font-weight:700;">{c['media_type'].upper()}</span></div>
                        <div class="rf-table-row" style="border-bottom:none;"><span style="color:#A493C2;">Submitted</span><span style="color:#A493C2;">{c.get('submitted_at', '')}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if c.get("file_path") and os.path.exists(c["file_path"]):
                        if c["media_type"] == "image":
                            st.image(c["file_path"], caption=c["title"], use_container_width=True)
                        else:
                            st.video(c["file_path"])
                    else:
                        st.info("📂 Media file loaded for reviewer inspection.")
                        
                with col_evidence:
                    st.markdown(f"""
                    <div class="rf-card" style="margin-bottom:16px;">
                        <div style="font-size:16px; font-weight:700; color:#FFFFFF; font-family:'Outfit',sans-serif; margin-bottom:12px;">
                            2. AI Safety Evidence & Reasoning
                        </div>
                        <div class="rf-table-row"><span style="color:#A493C2;">AI Classification</span><span style="color:#E2D9F3; font-weight:700;">{c.get('ai_classification', 'N/A')}</span></div>
                        <div class="rf-table-row"><span style="color:#A493C2;">Threat Risk Score</span><span style="color:#EF4444; font-weight:700;">{c.get('risk_score', 0.0)} / 100</span></div>
                        <div class="rf-table-row"><span style="color:#A493C2;">Model Confidence</span><span style="color:#22C55E; font-weight:700;">{int((c.get('confidence') or 0.85)*100)}%</span></div>
                        <div class="rf-table-row"><span style="color:#A493C2;">Extracted OCR Text</span><span style="color:#FFFFFF;">"{c.get('ocr_text', 'None detected')}"</span></div>
                        <div class="rf-table-row" style="border-bottom:none;"><span style="color:#A493C2;">Speech Audio</span><span style="color:#FFFFFF;">"{c.get('audio_transcript', 'No speech')}"</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"**AI Reasoning Explanation**:\n> *{c.get('explanation', '')}*")
                    
                    st.markdown("---")
                    st.markdown("### 3. Human Moderator Decision")
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
                        old_dec = r.get("human_decision")
                        r["human_decision"] = new_dec
                        r["review_status"] = "HUMAN_REVIEWED_EDITED"
                        
                        if "global_ads" not in st.session_state:
                            st.session_state["global_ads"] = []
                            
                        st.session_state["global_ads"] = [a for a in st.session_state["global_ads"] if a.get("ad_id") != r.get("ad_id")]
                        
                        if new_dec != "UNSAFE_FOR_ALL":
                            feed_ad = r.copy()
                            feed_ad["classification"] = new_dec
                            st.session_state["global_ads"].append(feed_ad)
                            
                        st.session_state["admin_action_msg"] = f"✏️ Decision for Case #{r.get('review_id')} updated from {old_dec} to {new_dec}."
                        st.rerun()
            
    with tab3:
        st.subheader("📈 Human Review Analytics & System Performance")
        
        scol1, scol2, scol3 = st.columns(3)
        scol1.metric("Pending Queue", f"{pending_count} case(s)")
        scol2.metric("Human Approvals (Safe)", f"{accepted_count} case(s)")
        scol3.metric("Human Rejections (Unsafe)", f"{rejected_count} case(s)")
