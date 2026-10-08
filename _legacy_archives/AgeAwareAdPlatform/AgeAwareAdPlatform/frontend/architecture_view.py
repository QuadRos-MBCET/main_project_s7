import os
import requests
import streamlit as st
from config.default_config import settings

def render_architecture_view():
    """
    Renders the System Architecture, Live Backend Telemetry & Database Console.
    Allows real-time inspection of backend FastAPI API, DB records, and AI models.
    """
    st.markdown("""
        <style>
        .arch-header {
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
        .arch-title {
            font-size: 28px;
            font-weight: 800;
            margin: 0;
            color: #ffffff;
            letter-spacing: -0.5px;
        }
        .arch-subtitle {
            font-size: 14px;
            color: #e9d5ff;
            margin-top: 6px;
        }
        .live-status-card {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 18px;
            padding: 20px;
            margin-bottom: 24px;
            color: #ffffff;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }
        .matrix-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: rgba(255, 255, 255, 0.04);
            border-radius: 12px;
            overflow: hidden;
        }
        .matrix-table th, .matrix-table td {
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 14px;
            text-align: center;
        }
        .matrix-table th {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            font-weight: 700;
        }
        .cell-allowed {
            background-color: rgba(16, 185, 129, 0.25);
            color: #6ee7b7;
            font-weight: 800;
        }
        .cell-blocked {
            background-color: rgba(239, 68, 68, 0.25);
            color: #fca5a5;
            font-weight: 800;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="arch-header">
            <div class="arch-title">⚡ Live Backend Telemetry & Architecture Console</div>
            <div class="arch-subtitle">Real-time Backend API Monitoring, Live Database Table Querying, & Multimodal Specification</div>
        </div>
    """, unsafe_allow_html=True)

    # LIVE BACKEND TELEMETRY BAR
    backend_url = f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}"
    health_online = False
    health_msg = "Checking status..."

    try:
        r = requests.get(f"{backend_url}/health", timeout=3)
        if r.status_code == 200:
            health_online = True
            health_msg = f"FastAPI Server Online (Version: {r.json().get('version', '2.0.0')})"
    except Exception as e:
        health_msg = f"Backend Connection Warning: {str(e)}"

    col_h1, col_h2 = st.columns([2.5, 1.5])
    with col_h1:
        st.markdown(f"""
            <div class="live-status-card">
                <span style="font-size:18px; font-weight:700;">📡 Live Backend Status:</span> 
                <span style="color: {'#166534' if health_online else '#991b1b'}; font-weight:800; font-size:16px;">
                    {'🟢 ONLINE' if health_online else '🔴 OFFLINE'}
                </span><br>
                <span style="font-size:13px; color:#475569;">URL: <code>{backend_url}</code> • {health_msg}</span>
            </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown("**Interactive Live OpenAPI Docs:**")
        st.link_button("📡 Launch Live Swagger API Docs (OpenAPI)", f"{backend_url}/docs", type="primary", use_container_width=True)
        st.link_button("📑 Launch ReDoc Documentation", f"{backend_url}/redoc", type="secondary", use_container_width=True)

    st.markdown("---")

    # LIVE DATABASE TABLES INSPECTOR
    st.subheader("🗄️ Live Database Table Inspector (safead.db)")
    st.markdown("Inspect real-time table records stored in the SQLite database:")

    db_tab1, db_tab2, db_tab3, db_tab4 = st.tabs([
        "📢 Advertisements Table",
        "📊 Moderation Results Table",
        "👥 Users Table",
        "📜 Audit Logs Table"
    ])

    with db_tab1:
        try:
            from backend.app.db.database import SessionLocal
            from backend.app.db.models import Advertisement
            db = SessionLocal()
            ads = db.query(Advertisement).all()
            if not ads:
                st.info("No records in `advertisements` table yet. Upload an ad in the Advertiser Portal to create a row!")
            else:
                ad_data = [{
                    "Ad ID": a.id,
                    "Title": a.title,
                    "Caption": a.caption,
                    "Media Type": a.media_type,
                    "File Path": a.file_path,
                    "Publication Status": a.status,
                    "Created At": str(a.created_at)
                } for a in ads]
                st.dataframe(ad_data, use_container_width=True)
            db.close()
        except Exception as err:
            st.error(f"Error querying Advertisements table: {err}")

    with db_tab2:
        try:
            from backend.app.db.database import SessionLocal
            from backend.app.db.models import ModerationResult
            db = SessionLocal()
            mods = db.query(ModerationResult).all()
            if not mods:
                st.info("No records in `moderation_results` table yet.")
            else:
                mod_data = [{
                    "Ad ID": m.advertisement_id,
                    "Final Classification": m.final_classification.value if m.final_classification else "N/A",
                    "AI Classification": m.ai_classification.value if m.ai_classification else "N/A",
                    "Risk Score": f"{m.risk_score:.1f}/100" if m.risk_score is not None else "N/A",
                    "Model Confidence": f"{m.confidence:.1%}" if m.confidence is not None else "N/A",
                    "Publishable": m.publishable,
                    "Human Reviewed": m.is_human_reviewed,
                    "AI Explanation": m.explanation
                } for m in mods]
                st.dataframe(mod_data, use_container_width=True)
            db.close()
        except Exception as err:
            st.error(f"Error querying Moderation Results table: {err}")

    with db_tab3:
        try:
            from backend.app.db.database import SessionLocal
            from backend.app.db.models import User
            db = SessionLocal()
            users = db.query(User).all()
            if not users:
                st.info("No records in `users` table yet.")
            else:
                usr_data = [{
                    "User ID": u.id,
                    "Username": u.username,
                    "Email": u.email,
                    "Verified Age Group": u.verified_age_group.value if u.verified_age_group else "N/A",
                    "Estimated Facial Age": f"~{u.estimated_age:.1f} yrs" if u.estimated_age else "N/A",
                    "Role": u.role.value if u.role else "USER",
                    "Created At": str(u.created_at)
                } for u in users]
                st.dataframe(usr_data, use_container_width=True)
            db.close()
        except Exception as err:
            st.error(f"Error querying Users table: {err}")

    with db_tab4:
        try:
            from backend.app.db.database import SessionLocal
            from backend.app.db.models import AuditLog
            db = SessionLocal()
            logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(50).all()
            if not logs:
                st.info("No audit logs recorded yet.")
            else:
                log_data = [{
                    "Log ID": l.id,
                    "Ad ID": f"#{l.ad_id}" if l.ad_id else "N/A",
                    "Action": l.action,
                    "Details": l.details,
                    "Timestamp": str(l.timestamp)
                } for l in logs]
                st.dataframe(log_data, use_container_width=True)
            db.close()
        except Exception as err:
            st.error(f"Error querying Audit Logs table: {err}")

    st.markdown("---")

    # SYSTEM ARCHITECTURE & POLICY MATRIX
    st.subheader("📐 System Architecture Specification")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Flow A: Advertisement Moderation Pipeline")
        st.markdown("""
        ```mermaid
        flowchart TD
            A["Advertiser Upload"] --> B["FastAPI Backend /api/v1/advertisements/check"]
            B --> C["SafeAd AI Multi-Modal Engine"]
            C --> D["Visual + OCR + Audio + Fusion Analysis"]
            D --> E{"AI Classification"}
            E -->|"SAFE_FOR_ALL"| F["SAFE FOR ALL"]
            E -->|"SAFE_14_PLUS"| G["14+"]
            E -->|"SAFE_18_PLUS"| H["18+"]
            E -->|"UNSAFE_FOR_ALL"| I["UNSAFE FOR ALL (Rejected)"]
            
            F --> J{"Advertiser Decision"}
            G --> J
            H --> J
            J -->|"Accept"| K["Approved Ad Store"]
            J -->|"Dispute"| L["Human Review Queue"]
            
            L --> M["Human Reviewer Override"]
            M -->|"Sets final_classification"| K
            K --> N["Age-Aware Ad Delivery Engine"]
        ```
        """)

    with col2:
        st.markdown("#### Flow B: Biometric Verification & Delivery")
        st.markdown("""
        ```mermaid
        flowchart TD
            U["User Starts Registration"] --> V["Camera Permission Granted"]
            V --> W["Single Photo Snapshot Captured"]
            W --> X["FaceAgeAdapter: MTCNN + Anti-Spoof + ViT"]
            X --> Y["Estimated Age Computed"]
            Y --> Z{"Age Category Assignment"}
            Z -->|"Under 14"| AA["SAFE FOR ALL"]
            Z -->|"14 to 17"| AB["14+"]
            Z -->|"18 and older"| AC["18+"]
            
            AA --> AD["Save Category to User Account"]
            AB --> AD
            AC --> AD
            AD --> AE["Camera Stops Permanently"]
            AE --> AF["Subsequent Logins: Read Saved Category"]
            AF --> AG["Open Social Feed (AuraFeed)"]
            AG --> N["Age-Aware Ad Delivery Engine"]
        ```
        """)

    st.markdown("---")
    st.subheader("🎯 Age-Aware Ad Delivery Eligibility Matrix")

    st.markdown("""
    <table class="matrix-table">
        <thead>
            <tr>
                <th>User Age Category</th>
                <th>SAFE FOR ALL Ad</th>
                <th>14+ Ad</th>
                <th>18+ Ad</th>
                <th>UNSAFE FOR ALL Ad</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>SAFE FOR ALL (&lt; 14)</strong></td>
                <td class="cell-allowed">✅ SHOWN</td>
                <td class="cell-blocked">⛔ HIDDEN</td>
                <td class="cell-blocked">⛔ HIDDEN</td>
                <td class="cell-blocked">⛔ NEVER DELIVERED</td>
            </tr>
            <tr>
                <td><strong>14+ (14 – 17)</strong></td>
                <td class="cell-allowed">✅ SHOWN</td>
                <td class="cell-allowed">✅ SHOWN</td>
                <td class="cell-blocked">⛔ HIDDEN</td>
                <td class="cell-blocked">⛔ NEVER DELIVERED</td>
            </tr>
            <tr>
                <td><strong>18+ (18+)</strong></td>
                <td class="cell-allowed">✅ SHOWN</td>
                <td class="cell-allowed">✅ SHOWN</td>
                <td class="cell-allowed">✅ SHOWN</td>
                <td class="cell-blocked">⛔ NEVER DELIVERED</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)
