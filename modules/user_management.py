import streamlit as st
import pandas as pd
from database.db import execute_query
from utils.auth import hash_password
from utils.rbac import has_permission, ROLES
from utils.audit import log_action

def render_user_management():
    if not has_permission("MANAGE_USERS"):
        st.error("You do not have permission to view this page.")
        return

    st.title("👥 User Management")
    st.markdown("Manage system access and roles.")

    # List Users
    st.subheader("Current Users")
    users = execute_query("SELECT id, username, full_name, role, is_active, created_at FROM users", fetch_all=True)
    if users:
        df = pd.DataFrame([dict(u) for u in users])
        df['is_active'] = df['is_active'].apply(lambda x: "Yes" if x else "No")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No users found.")

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New User")
        with st.form("create_user_form"):
            new_username = st.text_input("Username")
            new_fullname = st.text_input("Full Name")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ROLES)
            
            if st.form_submit_button("Create User"):
                if not new_username or not new_password or not new_fullname:
                    st.error("All fields are required.")
                else:
                    try:
                        password_hash = hash_password(new_password)
                        user_id = execute_query(
                            "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                            (new_username, password_hash, new_fullname, new_role)
                        )
                        log_action("User Created", "User Management", f"Created user {new_username} with role {new_role}", "users", user_id)
                        st.success(f"User {new_username} created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating user: Usernames must be unique.")

    with col2:
        st.subheader("Manage Existing User")
        if users:
            usernames = [u['username'] for u in users]
            selected_username = st.selectbox("Select User", usernames)
            selected_user = next(u for u in users if u['username'] == selected_username)
            
            with st.form("edit_user_form"):
                update_role = st.selectbox("New Role", ROLES, index=ROLES.index(selected_user['role']))
                update_active = st.checkbox("Account Active", value=bool(selected_user['is_active']))
                
                if st.form_submit_button("Update User"):
                    # Prevent disabling the last admin
                    if selected_user['role'] == "ADMINISTRATOR" and (update_role != "ADMINISTRATOR" or not update_active):
                        admin_count = execute_query("SELECT COUNT(*) as c FROM users WHERE role='ADMINISTRATOR' AND is_active=1", fetch_one=True)['c']
                        if admin_count <= 1:
                            st.error("Cannot disable or downgrade the last active administrator.")
                            st.stop()

                    execute_query(
                        "UPDATE users SET role = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (update_role, 1 if update_active else 0, selected_user['id'])
                    )
                    log_action("User Updated", "User Management", f"Updated user {selected_username}: role={update_role}, active={update_active}", "users", selected_user['id'])
                    st.success("User updated successfully!")
                    st.rerun()
                    
            with st.form("reset_password_form"):
                st.markdown("**Reset Password**")
                reset_password = st.text_input("New Password", type="password")
                if st.form_submit_button("Reset Password"):
                    if not reset_password:
                        st.error("Password cannot be empty.")
                    else:
                        password_hash = hash_password(reset_password)
                        execute_query("UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (password_hash, selected_user['id']))
                        log_action("Password Reset", "User Management", f"Reset password for user {selected_username}", "users", selected_user['id'])
                        st.success("Password reset successfully!")
