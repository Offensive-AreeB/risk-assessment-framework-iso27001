import streamlit as st
import pandas as pd
from utils.audit import get_audit_logs
from utils.rbac import has_permission

def render_audit_logs():
    if not has_permission("VIEW_AUDIT_LOGS"):
        st.error("You do not have permission to view this page.")
        return

    st.title("📋 System Audit Logs")
    st.markdown("Immutable record of system activities.")

    logs = get_audit_logs(limit=500)
    
    if not logs:
        st.info("No audit logs found.")
        return
        
    df = pd.DataFrame([dict(l) for l in logs])
    
    # Filtering
    col1, col2 = st.columns(2)
    with col1:
        user_filter = st.selectbox("Filter by User", ["All"] + list(df['username'].unique()))
    with col2:
        module_filter = st.selectbox("Filter by Module", ["All"] + list(df['module'].unique()))
        
    if user_filter != "All":
        df = df[df['username'] == user_filter]
    if module_filter != "All":
        df = df[df['module'] == module_filter]
        
    st.dataframe(
        df[['timestamp', 'username', 'action', 'module', 'record_type', 'record_id', 'description']],
        use_container_width=True,
        hide_index=True
    )
