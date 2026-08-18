import bcrypt
import streamlit as st
from database.db import execute_query

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def authenticate_user(username, password):
    """Attempt to authenticate a user. Returns (bool, user_dict_or_msg)."""
    user_row = execute_query("SELECT * FROM users WHERE username = ?", (username,), fetch_one=True)
    if not user_row:
        return False, "Invalid username or password."
    
    user = dict(user_row)
    if not user['is_active']:
        return False, "Account is disabled."
        
    if verify_password(password, user['password_hash']):
        return True, user
    return False, "Invalid username or password."

def login_user(user):
    """Store user in session state."""
    st.session_state['authenticated'] = True
    st.session_state['user'] = {
        'id': user['id'],
        'username': user['username'],
        'full_name': user['full_name'],
        'role': user['role']
    }

def logout_user():
    """Clear session state."""
    st.session_state['authenticated'] = False
    if 'user' in st.session_state:
        del st.session_state['user']

def is_authenticated():
    """Check if the current session is authenticated."""
    return st.session_state.get('authenticated', False)

def get_current_user():
    """Get the current authenticated user dictionary."""
    return st.session_state.get('user', None)

def get_user_count():
    """Check how many users exist to determine if setup is needed."""
    row = execute_query("SELECT COUNT(*) as c FROM users", fetch_one=True)
    return row['c'] if row else 0

def create_initial_admin(username, password, full_name):
    """Create the very first administrator account safely."""
    if get_user_count() > 0:
        return False, "Users already exist. Setup disabled."
    
    password_hash = hash_password(password)
    execute_query(
        "INSERT INTO users (username, password_hash, full_name, role, is_active) VALUES (?, ?, ?, ?, ?)",
        (username, password_hash, full_name, "ADMINISTRATOR", 1)
    )
    return True, "Administrator created successfully."
