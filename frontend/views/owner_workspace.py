import streamlit as st
import os
import sys
import time
import requests
from datetime import datetime

# Inject backend2jb into sys.path to allow Joseph's true modules to load exactly as they do in his branch
jb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "joseph_safead_core/backend2jb"))
if jb_dir not in sys.path:
    sys.path.insert(0, jb_dir)

# Try importing the local fallback inference directly as done in his UI
try:
    from ai.pipeline import run_safead_inference
except ImportError:
    run_safead_inference = None

try:
    from backend.app.services.ai_client_service import AIClientService
except ImportError:
    AIClientService = None

try:
    from frontend.services.safead_client import SafeAdClient
except ImportError:
    SafeAdClient = None

from frontend.styles.safead_theme import render_risk_gauge, render_svg_icon, render_html

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8002/api/v1")

def check_backend_online():
    try:
        resp = requests.get("http://127.0.0.1:8002/health", timeout=1.0)
        return resp.status_code == 200
    except Exception:
        return False


def owner_dashboard():
    # -------------------------------------------------------------------------
    # HEADER BANNER (RiteFlow Style)
    # -------------------------------------------------------------------------
    render_html('''
    <div style="margin-bottom: 24px;">
        <div class="rf-eyebrow-pill" style="margin-bottom: 12px;">
            <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:#6C5CE7; box-shadow:0 0 8px #6C5CE7;"></span>
            ENTERPRISE CAMPAIGN SAFETY
        </div>
        <h1 style="margin: 0; font-size: 32px; font-weight: 700; color: #FFFFFF; font-family: 'Outfit', sans-serif;">
            Creative <span class="rf-italic-serif">Pre-Flight Audit</span>
        </h1>
        <p style="color:#A493C2; font-size:14px; margin:6px 0 0 0;">
            Pre-screen ad creative assets across multimodal threat detectors before deployment.
        </p>
    </div>
    ''')
    
    if "owner_action_msg" in st.session_state and st.session_state["owner_action_msg"]:
        msg = st.session_state["owner_action_msg"]
        if "Pending" in msg:
            st.info(msg)
        elif "Unsafe" in msg:
            st.error(msg)
        else:
            st.success(msg)
        st.session_state["owner_action_msg"] = None
        
    col_up, col_res = st.columns([1, 1.25], gap="large")
    
    with col_up:
        render_html(f"""
        <div class="rf-card" style="margin-bottom: 16px;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
                <div style="width:32px; height:32px; border-radius:8px; background:rgba(108,92,231,0.18); border:1px solid rgba(108,92,231,0.3); display:flex; align-items:center; justify-content:center;">
                    {render_svg_icon("cpu", size=16, color="#6C5CE7")}
                </div>
                <div>
                    <div style="font-size:16px; font-weight:700; color:#FFFFFF; font-family:'Outfit',sans-serif;">Upload Advertisement Creative</div>
                    <div style="font-size:12px; color:#A493C2;">Provide media assets and metadata for AI pre-flight scan</div>
                </div>
            </div>
        </div>
        """)
        
        ad_title = st.text_input("Creative Title", placeholder="e.g. Organic Apple Juice / Casino Slot Promo / Paisa Double Scheme")
        ad_caption = st.text_area("Ad Copy / Caption", placeholder="e.g. Double your money guaranteed / Fresh organic apples")
        uploaded_file = st.file_uploader("Select Image or Video Media File", type=["jpg", "jpeg", "png", "webp", "mp4", "avi", "mov"])
        
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            file_size_kb = round(len(file_bytes) / 1024.0, 1)
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            media_type = "video" if file_ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"] else "image"
            
            render_html(f"""
            <div style="background:rgba(17,23,38,0.7); border:1px solid rgba(108,92,231,0.2); border-radius:10px; padding:12px 14px; margin: 12px 0;">
                <div style="font-size:12px; font-weight:700; color:#E2D9F3; margin-bottom:6px; letter-spacing:0.04em; text-transform:uppercase;">Asset Manifest</div>
                <div class="rf-table-row"><span style="color:#A493C2;">Filename</span><span style="color:#FFFFFF; font-family:monospace;">{uploaded_file.name}</span></div>
                <div class="rf-table-row"><span style="color:#A493C2;">Media Type</span><span style="color:#E2D9F3; font-weight:600;">{media_type.upper()} ({file_ext})</span></div>
                <div class="rf-table-row"><span style="color:#A493C2;">Payload Size</span><span style="color:#E2D9F3;">{file_size_kb} KB</span></div>
                <div class="rf-table-row" style="border-bottom:none;"><span style="color:#A493C2;">Timestamp</span><span style="color:#A493C2;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span></div>
            </div>
            """)
            
            # PRIVACY REQUIREMENT: Do NOT render media player or image on Brand Owner page
            
            # Moderation Pipeline Mode Configuration (Including Qwen3-VL & Strategy D)
            st.markdown("#### ⚙️ Moderation Engine Configuration")
            mode_options = [
                "🛡️ Strategy D: Hierarchical Safety Fusion (Qwen3-VL + Learned RF)",
                "⚡ Qwen3-VL-8B Multimodal VLM (Google Colab A100)",
                "Learned Random Forest (Default Experimental)",
                "Safety-Prioritized Moderation (Learned RF + HITL Uncertainty Gate)",
                "Candidate B (Enhanced Alcohol Heuristic)",
                "Production Baseline (Frozen Heuristic)",
            ]
            selected_mode_label = st.selectbox(
                "Select Moderation Pipeline Mode",
                mode_options,
                index=0,
                help="Strategy D combines cloud Qwen3-VL semantic reasoning with 33-dim local Random Forest safety veto. Learned Random Forest runs 100% locally."
            )
            mode_map = {
                "🛡️ Strategy D: Hierarchical Safety Fusion (Qwen3-VL + Learned RF)": "strategy_d",
                "⚡ Qwen3-VL-8B Multimodal VLM (Google Colab A100)": "qwen3_vl",
                "Learned Random Forest (Default Experimental)": "learned_rf",
                "Safety-Prioritized Moderation (Learned RF + HITL Uncertainty Gate)": "learned_rf_hitl",
                "Candidate B (Enhanced Alcohol Heuristic)": "candidate_b",
                "Production Baseline (Frozen Heuristic)": "production",
            }
            active_pipeline_mode = mode_map.get(selected_mode_label, "strategy_d")

            # Google Colab Qwen3-VL Server Configuration Card
            needs_colab = active_pipeline_mode in ["qwen3_vl", "strategy_d"]
            with st.expander("⚡ Google Colab Qwen3-VL GPU Server Settings", expanded=needs_colab):
                st.caption(
                    "Connects the frontend to an external **NVIDIA A100 / T4 GPU on Google Colab** running "
                    "`tools/qwen3_vl_colab_server.py`. If Colab is offline, the system safely falls back to local Learned Random Forest."
                )
                colab_input = st.text_input(
                    "Google Colab Public Tunnel URL (ngrok / localtunnel)",
                    value=st.session_state.get("colab_tunnel_url", os.getenv("COLAB_API_URL", "")),
                    placeholder="https://xxxx-xx-xx-xx-xx.ngrok-free.app",
                    help="Run the SafeAd Qwen3-VL notebook in Google Colab, copy the ngrok public tunnel URL, and paste it here."
                )
                st.session_state["colab_tunnel_url"] = colab_input.strip()

                col_t1, col_t2 = st.columns([1, 1.8])
                with col_t1:
                    if st.button("🔌 Ping Colab Server", use_container_width=True):
                        if not colab_input.strip():
                            st.warning("Please provide a Colab URL first.")
                        else:
                            with st.spinner("Testing Colab GPU connection..."):
                                check_res = None
                                err = None
                                if AIClientService:
                                    check_res = AIClientService.test_colab_connection(colab_input.strip())
                                elif SafeAdClient:
                                    check_res, err = SafeAdClient.check_colab_health(colab_input.strip())
                                
                                if check_res and check_res.get("status") == "online":
                                    st.session_state["colab_status"] = "online"
                                    st.session_state["colab_info"] = check_res
                                else:
                                    st.session_state["colab_status"] = "offline"
                                    st.session_state["colab_info"] = err or check_res

                with col_t2:
                    current_status = st.session_state.get("colab_status", "unknown")
                    if current_status == "online":
                        c_info = st.session_state.get("colab_info", {})
                        st.success(f"🟢 **Connected**: {c_info.get('gpu', 'NVIDIA GPU')} ({c_info.get('model', 'Qwen3-VL-8B')})")
                    elif current_status == "offline":
                        st.error("🔴 **Offline / Unreachable** (Graceful Local RF Fallback Active)")
                    else:
                        st.info("⚪ Not Verified / Local Fallback Active")
            
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 ANALYZE ADVERTISEMENT", type="primary", use_container_width=True):
                if not ad_title:
                    st.error("Please provide a Creative Title before starting analysis.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    progress_bar.progress(15)
                    status_text.info("[1/4] Validating File & Extracting Media Keyframes...")
                    
                    progress_bar.progress(40)
                    status_text.info("[2/4] Running EasyOCR & Llama Guard Visual Safety...")
                    
                    progress_bar.progress(70)
                    if active_pipeline_mode in ["qwen3_vl", "strategy_d"]:
                        status_text.info("[3/4] Querying Google Colab Qwen3-VL-8B Vision-Language Model...")
                    else:
                        status_text.info("[3/4] VideoMAE Violence, Falconsai NSFW, & Whisper Speech Transcription...")
                    
                    progress_bar.progress(90)
                    status_text.info("[4/4] Executing Two-Stage Policy Engine & Ad Risk Analysis...")
                    
                    uploads_dir = os.path.join(jb_dir, "uploads")
                    temp_path = os.path.join(uploads_dir, f"upload_{int(time.time())}_{uploaded_file.name}")
                    os.makedirs(uploads_dir, exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(file_bytes)
                        
                    report = None
                    effective_colab_url = st.session_state.get("colab_tunnel_url", "").strip()

                    if check_backend_online():
                        try:
                            files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type or "video/mp4")}
                            data = {"title": ad_title, "caption": ad_caption, "user_id": 1}
                            resp = requests.post(f"{BACKEND_URL}/advertisements/upload", files=files, data=data, timeout=30)
                            if resp.status_code == 200:
                                ad_data = resp.json()
                                st.session_state["current_ad_id"] = ad_data["id"]
                                
                                analyze_params = {"pipeline_mode": active_pipeline_mode}
                                if effective_colab_url:
                                    analyze_params["colab_url"] = effective_colab_url

                                analyze_resp = requests.post(
                                    f"{BACKEND_URL}/advertisements/{ad_data['id']}/analyze",
                                    params=analyze_params,
                                    timeout=600
                                )
                                if analyze_resp.status_code == 200:
                                    report = analyze_resp.json()
                        except Exception as backend_err:
                            print(f"[Owner Workspace] Backend API call error: {backend_err}")

                    if not report:
                        # Direct local service fallback
                        if AIClientService:
                            try:
                                report = AIClientService.process_advertisement(
                                    temp_path,
                                    ad_title,
                                    ad_caption,
                                    pipeline_mode=active_pipeline_mode,
                                    colab_url=effective_colab_url
                                )
                                st.session_state["current_ad_id"] = report.get("ad_id", 101)
                                st.session_state["last_temp_path"] = temp_path
                                st.session_state["last_ad_title"] = ad_title
                                st.session_state["last_ad_caption"] = ad_caption
                            except Exception as ai_err:
                                print(f"[Owner Workspace] AIClientService error: {ai_err}")

                        if not report and run_safead_inference:
                            try:
                                report = run_safead_inference(
                                    temp_path,
                                    ad_title,
                                    ad_caption,
                                    pipeline_mode=active_pipeline_mode
                                )
                                st.session_state["current_ad_id"] = report.get("ad_id", 101)
                                st.session_state["last_temp_path"] = temp_path
                                st.session_state["last_ad_title"] = ad_title
                                st.session_state["last_ad_caption"] = ad_caption
                            except Exception as infer_err:
                                st.error(f"Inference processing error: {infer_err}")
                                report = {
                                    "classification": "REQUIRES_HUMAN_REVIEW",
                                    "publication_action": "HUMAN_REVIEW",
                                    "risk_score": 50.0,
                                    "confidence": 0.5,
                                    "explanation": f"Automated processing interrupted: {infer_err}. Routed to Human Review.",
                                    "detected_categories": ["Processing Interrupted"],
                                    "policy_stage": "Fail-Safe Human Review"
                                }

                    progress_bar.progress(100)
                    status_text.success("Analysis Complete!")
                    st.session_state["moderation_report"] = report
                    st.session_state["confirm_delete"] = False
                    
    with col_res:
        if "moderation_report" in st.session_state and st.session_state["moderation_report"]:
            rep = st.session_state["moderation_report"]
            
            classification = rep.get("classification", "UNSAFE_FOR_ALL")
            action = rep.get("publication_action", "REJECT")
            risk_score = float(rep.get("risk_score", 0.0) or 0.0)
            confidence = float(rep.get("confidence", 0.85) or 0.85)
            requires_hitl = rep.get("requires_human_review", False) or action == "HUMAN_REVIEW"
            ad_id = st.session_state.get("current_ad_id", rep.get("ad_id", 1))

            # Display Colab Fallback Notification if triggered
            if rep.get("colab_fallback"):
                st.warning(
                    rep.get("colab_warning") or
                    "⚠️ Google Colab GPU was offline or unreachable. Automatically executed local Learned Random Forest fallback."
                )

            # -----------------------------------------------------------------
            # RITEFLOW BROWSER FRAME FOR SCORECARD
            # -----------------------------------------------------------------
            render_html(f"""
            <div class="rf-browser-frame">
                <div class="rf-browser-header">
                    <div class="rf-browser-dots">
                        <span class="rf-dot red"></span>
                        <span class="rf-dot yellow"></span>
                        <span class="rf-dot green"></span>
                    </div>
                    <div class="rf-browser-url">safead.ai/decision-engine/audit-report#{ad_id}</div>
                    <div style="width: 52px;"></div>
                </div>
                <div class="rf-browser-body">
            """)

            # Circular Risk Gauge with RiteFlow Theme
            render_risk_gauge(risk_score, label="Multimodal Threat Index")
            render_html("<div style='height:12px;'></div>")

            # Dual-Encoded Verdict Badge (Icon + Text + Tint)
            if classification == "UNSAFE_FOR_ALL" or action == "REJECT":
                st.markdown("<div class='badge-danger'>✕ &nbsp;UNSAFE FOR ALL — REJECT (DO NOT PUBLISH)</div>", unsafe_allow_html=True)
            elif classification == "SAFE_18_PLUS":
                st.markdown("<div class='badge-warning'>⚠ &nbsp;AGE RESTRICTED — 18+ AUDIENCE ONLY</div>", unsafe_allow_html=True)
            elif classification == "SAFE_14_PLUS":
                st.markdown("<div class='badge-14'>ℹ &nbsp;AGE RESTRICTED — 14+ AUDIENCE ONLY</div>", unsafe_allow_html=True)
            elif classification == "REQUIRES_HUMAN_REVIEW":
                st.markdown("<div class='badge-hitl'>⚑ &nbsp;HUMAN REVIEW REQUIRED (UNCERTAINTY GATE)</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='badge-safe'>✓ &nbsp;SAFE FOR ALL — APPROVED FOR BROADCAST</div>", unsafe_allow_html=True)
                
            # Engine Stage and Mode indicator
            mode_badge = str(rep.get("pipeline_mode", active_pipeline_mode)).upper()
            st.caption(f"🔧 **Moderation Engine**: `{mode_badge}` | **Policy Stage**: `{rep.get('policy_stage', 'Standard Fusion')}`")

            # Metrics Row (RiteFlow Cards)
            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.metric("Risk Score", f"{risk_score:.1f} / 100")
            with mcol2:
                is_learned_rf = "learned_rf" in str(rep.get("pipeline_mode", "")).lower()
                if is_learned_rf and not rep.get("pipeline_mode") == "strategy_d":
                    st.metric("RF Vote Share", f"{int(confidence * 100)}% (Uncalibrated)")
                else:
                    st.metric("Confidence", f"{int(confidence * 100)}%")
            with mcol3:
                st.metric("Latency", f"{float(rep.get('total_processing_time_seconds', 0.0) or 0.0):.2f}s")
            
            if is_learned_rf and not rep.get("pipeline_mode") == "strategy_d":
                st.caption("ℹ️ *Note: Random Forest vote share represents tree ensemble consensus and is not a calibrated posterior probability.*")

            # Strategy D Arbitration Badge
            if rep.get("fusion_rule_applied"):
                st.info(f"⚡ **Strategy D Arbitration**: `{rep.get('fusion_rule_applied')}`")

            # Qwen3-VL Vision-Language CoT Reasoning Display
            vlm_cot = rep.get("vlm_reasoning") or rep.get("reasoning")
            if vlm_cot and rep.get("pipeline_mode") in ["qwen3_vl", "strategy_d"]:
                st.markdown("### 🧠 Qwen3-VL Vision-Language Model CoT Reasoning")
                st.info(f"**VLM Semantic Analysis (Google Colab A100)**:\n\n{vlm_cot}")

            # Random Forest Probability Distribution
            if rep.get("rf_probabilities"):
                st.markdown("##### 🌲 Random Forest Feature Distribution")
                rf_p = rep.get("rf_probabilities", {})
                p_c1, p_c2, p_c3, p_c4 = st.columns(4)
                p_c1.metric("Safe For All", f"{float(rf_p.get('SAFE_FOR_ALL', 0.0))*100:.1f}%")
                p_c2.metric("Safe 14+", f"{float(rf_p.get('SAFE_14_PLUS', 0.0))*100:.1f}%")
                p_c3.metric("Safe 18+", f"{float(rf_p.get('SAFE_18_PLUS', 0.0))*100:.1f}%")
                p_c4.metric("Unsafe", f"{float(rf_p.get('UNSAFE_FOR_ALL', 0.0))*100:.1f}%")

            st.markdown(f"**Explanation**:\n\n{rep.get('explanation', '')}")
            
            # Central SafeAdAssessment Matrix Summary (RiteFlow Revenue Summary Style)
            st.markdown("### 📊 Safety Evidence Summary")
            ev = rep.get("evidence", {})
            matrix = ev if "visual" in ev else rep.get("assessment_matrix", {})
            
            ocr_text_clean = str(rep.get('extracted_ocr', '') or 'None detected').replace('"', '&quot;')
            audio_text_clean = str(rep.get('audio_transcript', '') or 'No audio').replace('"', '&quot;')
            vis_status = 'UNSAFE' if matrix.get('visual', {}).get('unsafe') else 'SAFE'
            vis_color = '#EF4444' if vis_status == 'UNSAFE' else '#22C55E'

            render_html(f"""
            <div style="background:rgba(11,15,28,0.7); border:1px solid rgba(108,92,231,0.22); border-radius:12px; padding:14px 18px; margin-bottom:14px;">
                <div class="rf-table-row">
                    <span style="color:#A493C2;">Extracted OCR Text</span>
                    <span style="color:#FFFFFF; font-weight:500; max-width:65%; text-align:right;">"{ocr_text_clean}"</span>
                </div>
                <div class="rf-table-row">
                    <span style="color:#A493C2;">Visual Safety Guard</span>
                    <span style="color:{vis_color}; font-weight:700;">{vis_status}</span>
                </div>
                <div class="rf-table-row">
                    <span style="color:#A493C2;">Adult / NSFW Index</span>
                    <span style="color:#E2D9F3; font-weight:600;">{float(matrix.get('visual', {}).get('adult', 0.0)):.2f}</span>
                </div>
                <div class="rf-table-row">
                    <span style="color:#A493C2;">Speech Audio Transcript</span>
                    <span style="color:#FFFFFF; font-weight:500; max-width:65%; text-align:right;">"{audio_text_clean}"</span>
                </div>
                <div class="rf-table-row">
                    <span style="color:#A493C2;">Video Kinetic Violence</span>
                    <span style="color:#E2D9F3; font-weight:600;">{float(matrix.get('video', {}).get('violence', 0.0)):.2f}</span>
                </div>
                <div class="rf-table-row" style="border-bottom:none;">
                    <span style="color:#A493C2;">Scam / Deceptive Claim</span>
                    <span style="color:#E2D9F3; font-weight:600;">{float(matrix.get('advertisement_risks', {}).get('scam', 0.0)):.2f}</span>
                </div>
            </div>
            """)

            # Close Browser Body & Frame
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            # BRAND OWNER WORKFLOW ACTIONS
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            st.markdown("### ⚡ Brand Owner Actions")
            st.info("ℹ️ **Policy Enforcement**: The AI safety classification cannot be manually overridden by the Brand Owner.")
            
            can_publish = classification not in ["UNSAFE_FOR_ALL", "REQUIRES_HUMAN_REVIEW"] and rep.get("publishable", True)
            if not can_publish:
                if classification == "UNSAFE_FOR_ALL":
                    st.error("🚨 **Prohibited Content**: This advertisement was rejected and cannot be published to any user feed.")
                elif classification == "REQUIRES_HUMAN_REVIEW" or not rep.get("publishable", True):
                    st.warning("⏳ **Human Review Required**: Publication is withheld pending human moderator decision. Please send for review below.")

            b_act1, b_act2 = st.columns(2)
            b_act3, b_act4 = st.columns(2)
            
            with b_act1:
                accept_type = "primary" if can_publish else "secondary"
                if st.button("✅ ACCEPT AI DECISION", use_container_width=True, type=accept_type, disabled=not can_publish):
                    if check_backend_online():
                        try:
                            requests.post(f"{BACKEND_URL}/advertisements/{ad_id}/accept-ai", timeout=5)
                        except Exception:
                            pass
                    
                    if "global_ads" not in st.session_state:
                        st.session_state["global_ads"] = []
                        
                    ad_exists = any(a.get("ad_id") == ad_id for a in st.session_state["global_ads"])
                    
                    if not ad_exists and can_publish:
                        feed_ad = {
                            "ad_id": ad_id,
                            "classification": classification,
                            "title": rep.get("title", st.session_state.get("last_ad_title", "Advertisement")),
                            "caption": rep.get("caption", st.session_state.get("last_ad_caption", "")),
                            "file_path": st.session_state.get("last_temp_path", "")
                        }
                        st.session_state["global_ads"].append(feed_ad)

                    st.session_state["owner_action_msg"] = f"✅ Advertisement accepted and moved to the {classification} feed."
                    st.session_state["moderation_report"] = None
                    st.session_state["current_ad_id"] = None
                    st.rerun()
                        
            with b_act2:
                if st.button("🗑️ DELETE ADVERTISEMENT", use_container_width=True):
                    st.session_state["confirm_delete"] = True
                    
            with b_act3:
                if st.button("🔄 UPLOAD ANOTHER ADVERTISEMENT", use_container_width=True):
                    st.session_state["moderation_report"] = None
                    st.session_state["current_ad_id"] = None
                    st.session_state["confirm_delete"] = False
                    st.rerun()
                    
            with b_act4:
                if st.button("📥 SEND FOR HUMAN REVIEW", use_container_width=True, type="primary" if (not can_publish and classification == "REQUIRES_HUMAN_REVIEW") else "secondary"):
                    if check_backend_online():
                        try:
                            requests.post(f"{BACKEND_URL}/advertisements/{ad_id}/human-review", json={"user_id": 1, "reason": "Brand owner requested review"}, timeout=5)
                        except Exception:
                            pass
                            
                    if "pending_human_reviews" not in st.session_state:
                        st.session_state["pending_human_reviews"] = []
                        
                    review_case = {
                        "review_id": int(time.time()),
                        "ad_id": ad_id,
                        "title": rep.get("title", st.session_state.get("last_ad_title", "")),
                        "caption": rep.get("caption", st.session_state.get("last_ad_caption", "")),
                        "file_path": rep.get("file_path", st.session_state.get("last_temp_path", "")),
                        "media_type": "video" if str(st.session_state.get("last_temp_path", "")).lower().endswith(('.mp4', '.avi', '.mov')) else "image",
                        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ai_classification": classification,
                        "risk_score": risk_score,
                        "confidence": confidence,
                        "explanation": rep.get("explanation", ""),
                        "ocr_text": rep.get("extracted_ocr", ""),
                        "audio_transcript": rep.get("audio_transcript", "")
                    }
                    if not any(c["ad_id"] == ad_id for c in st.session_state["pending_human_reviews"]):
                        st.session_state["pending_human_reviews"].append(review_case)
                        
                    st.session_state["owner_action_msg"] = "⏳ Advertisement is Pending for Human Review in the Admin Dashboard."
                    st.session_state["moderation_report"] = None
                    st.session_state["current_ad_id"] = None
                    st.rerun()
                    
            # Confirmation modal for delete action
            if st.session_state.get("confirm_delete", False):
                st.warning("🚨 Are you sure you want to delete this advertisement?")
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    if st.button("❌ Cancel Delete", use_container_width=True):
                        st.session_state["confirm_delete"] = False
                        st.rerun()
                with col_del2:
                    if st.button("🗑️ Confirm Delete", type="primary", use_container_width=True):
                        if check_backend_online():
                            try:
                                requests.delete(f"{BACKEND_URL}/advertisements/{ad_id}", timeout=5)
                            except Exception:
                                pass
                        st.session_state["moderation_report"] = None
                        st.session_state["current_ad_id"] = None
                        st.session_state["confirm_delete"] = False
                        st.success("Advertisement deleted successfully.")
                        st.rerun()
        else:
            # Elegant RiteFlow Browser Frame Empty State
            render_html(f"""
            <div class="rf-browser-frame">
                <div class="rf-browser-header">
                    <div class="rf-browser-dots">
                        <span class="rf-dot red"></span>
                        <span class="rf-dot yellow"></span>
                        <span class="rf-dot green"></span>
                    </div>
                    <div class="rf-browser-url">safead.ai/decision-engine/ready</div>
                    <div style="width: 52px;"></div>
                </div>
                <div class="rf-browser-body" style="text-align: center; padding: 48px 24px;">
                    <div style="width: 56px; height: 56px; border-radius: 50%; background: rgba(108, 92, 231, 0.14); border: 1px solid rgba(108, 92, 231, 0.3); display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                        {render_svg_icon("cpu", size=26, color="#6C5CE7")}
                    </div>
                    <h3 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 700; color: #FFFFFF; font-family: 'Outfit', sans-serif;">
                        Awaiting Creative Asset
                    </h3>
                    <p style="margin: 0 auto; max-width: 420px; font-size: 13px; color: #A493C2; line-height: 1.5;">
                        Upload an advertisement image or video asset on the left and click <b>ANALYZE ADVERTISEMENT</b> to inspect the real-time AI safety scorecard, multimodal threat index, and policy classification.
                    </p>
                </div>
            </div>
            """)
