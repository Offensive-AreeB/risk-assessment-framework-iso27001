import streamlit as st
from utils.auth import authenticate_user, login_user, get_user_count, create_initial_admin
from utils.audit import log_action

def render_login_page():
    """Render the login or first-run setup page."""
    st.title("🛡️ Risk Assessment Framework")
    st.markdown("ISO/IEC 27001 Aligned GRC Platform")
    
    # Check if we need first-run setup
    if get_user_count() == 0:
        st.info("First-run initialization: Please create the primary administrator account.")
        with st.form("setup_form"):
            st.subheader("Administrator Setup")
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submitted = st.form_submit_button("Create Administrator")
            if submitted:
                if not username or not password or not full_name:
                    st.error("All fields are required.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, msg = create_initial_admin(username, password, full_name)
                    if success:
                        log_action("User Created", "Authentication", f"Created initial administrator: {username}")
                        st.success(msg + " You may now login.")
                        st.rerun()
                    else:
                        st.error(msg)
        return

    # Normal Login Flow
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Authentication Required")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    success, result = authenticate_user(username, password)
                    if success:
                        login_user(result)
                        log_action("Successful Login", "Authentication", f"User {username} logged in successfully.")
                        st.rerun()
                    else:
                        log_action("Failed Login", "Authentication", f"Failed login attempt for username: {username}")
                        st.error(result)
