import streamlit as st
from services.analytics_service import analytics_service
from services.moderation_service import moderation_service
from backend_integration.backend_client import backend_client

def render_admin_dashboard():
    """
    Renders the System Administrator & Compliance Dashboard.
    Provides operational metrics, live database queries, and audit logs.
    """
    st.markdown("""
        <style>
        .admin-header {
            background: linear-gradient(135deg, #090d16 0%, #1e1b4b 100%);
            padding: 24px;
            border-radius: 12px;
            color: #ffffff;
            margin-bottom: 24px;
            border-left: 6px solid #818cf8;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .admin-title {
            font-size: 26px;
            font-weight: 700;
            color: #ffffff;
            margin: 0;
        }
        .admin-subtitle {
            font-size: 14px;
            color: #c7d2fe;
            margin-top: 6px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="admin-header">
            <div class="admin-title">⚙️ Compliance & System Administration Console</div>
            <div class="admin-subtitle">Platform Observability, Live Database Metrics, and Security Audit History</div>
        </div>
    """, unsafe_allow_html=True)

    # Health check
    health = backend_client.check_health()
    status_icon = "🟢" if health.get("online") else "🔴"
    status_text = "Backend Online (FastAPI + SQLite/MySQL)" if health.get("online") else "Backend Offline"
    
    st.markdown(f"**System Status:** {status_icon} `{status_text}`")

    # Real Database Metrics
    metrics = analytics_service.get_platform_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Advertisements", metrics.get("total_advertisements", 0))
    with col2:
        st.metric("Approved for Delivery", metrics.get("approved_advertisements", 0))
    with col3:
        st.metric("Rejected (Unsafe)", metrics.get("rejected_advertisements", 0))
    with col4:
        st.metric("Pending Human Review", metrics.get("pending_human_review", 0))

    st.markdown("---")

    col_charts, col_users = st.columns(2)
    
    with col_charts:
        st.subheader("📊 Advertisement Category Distribution")
        cat_breakdown = metrics.get("category_breakdown", {})
        for cat, count in cat_breakdown.items():
            st.write(f"**{cat}**: {count} ads")
            st.progress(min(1.0, count / max(1, metrics.get("total_advertisements", 1))))

    with col_users:
        st.subheader("👥 Registered Users by Age Category")
        user_breakdown = metrics.get("user_age_breakdown", {})
        total_u = max(1, metrics.get("total_users", 1))
        for u_cat, u_cnt in user_breakdown.items():
            pct = (u_cnt / total_u) * 100
            st.write(f"**{u_cat}**: {u_cnt} users ({pct:.0f}%)")
            st.progress(min(1.0, u_cnt / total_u))

    st.markdown("---")
    st.subheader("📜 Security Audit Trail Logs")
    logs = moderation_service.get_audit_logs(limit=25)
    
    if not logs:
        st.info("No audit logs recorded yet.")
    else:
        for log in logs:
            st.markdown(f"""
                * `[{log.get('timestamp', 'N/A')}]` **Action:** `{log.get('action')}` | **Ad ID:** #{log.get('ad_id')}  
                  ↳ *Details:* {log.get('details')}
            """)
