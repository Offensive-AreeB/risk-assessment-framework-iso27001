import streamlit as st
import os
import sys

# Add the root directory to path to allow absolute imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db
from data.seed_data import seed_database
from modules.dashboard import render_dashboard
from modules.assets import render_assets_page
from modules.risks import render_risks_page
from modules.controls import render_controls_page
from modules.mapping import render_mapping_page
from modules.soa import render_soa_page
from modules.treatments import render_treatments_page
from modules.reports import render_reports_page
from modules.about import render_about_page

from modules.login import render_login_page
from modules.user_management import render_user_management
from modules.audit_logs import render_audit_logs

from utils.auth import is_authenticated, get_current_user, logout_user
from utils.rbac import has_permission
from utils.audit import log_action

# Initialize database on startup
init_db()

# Seed database with sample data if it's empty
seed_database()

st.set_page_config(
    page_title="Risk Assessment Framework (ISO/IEC 27001)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if not is_authenticated():
    render_login_page()
    st.stop()

# Authenticated routing
user = get_current_user()

st.sidebar.title("🛡️ RAF Navigation")
st.sidebar.markdown(f"**Logged in as:**\n{user['full_name']}")
st.sidebar.markdown(f"**Role:**\n{user['role']}")

if st.sidebar.button("Logout"):
    log_action("Logout", "Authentication", f"User {user['username']} logged out.")
    logout_user()
    st.rerun()

st.sidebar.markdown("---")

nav_options = [
    "Dashboard", 
    "Asset Management", 
    "Risk Register",
    "ISO 27001 Controls",
    "Risk-Control Mapping",
    "Statement of Applicability",
    "Risk Treatment",
    "Reports",
    "About / Methodology"
]

if has_permission("MANAGE_USERS"):
    nav_options.append("User Management")
if has_permission("VIEW_AUDIT_LOGS"):
    nav_options.append("Audit Logs")

page = st.sidebar.radio("Go to", nav_options)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='font-size:0.78em; color:#a0aab4; line-height:1.7; padding: 4px 0;'>
    <b style='color:#c8d6e5;'>ZYNVEX-CERT-0666</b><br>
    Risk Assessment Framework<br>
    ISO/IEC 27001 Aligned GRC Platform<br>
    <span style='color:#2ecc71;'>● System Operational</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Page Routing
if page == "Dashboard":
    render_dashboard()
elif page == "Asset Management":
    render_assets_page()
elif page == "Risk Register":
    render_risks_page()
elif page == "ISO 27001 Controls":
    render_controls_page()
elif page == "Risk-Control Mapping":
    render_mapping_page()
elif page == "Statement of Applicability":
    render_soa_page()
elif page == "Risk Treatment":
    render_treatments_page()
elif page == "Reports":
    render_reports_page()
elif page == "About / Methodology":
    render_about_page()
elif page == "User Management" and has_permission("MANAGE_USERS"):
    render_user_management()
elif page == "Audit Logs" and has_permission("VIEW_AUDIT_LOGS"):
    render_audit_logs()
