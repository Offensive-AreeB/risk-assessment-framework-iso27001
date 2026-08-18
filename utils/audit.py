from database.db import execute_query
from utils.auth import get_current_user

def log_action(action: str, module: str, description: str, record_type: str = None, record_id: str = None):
    """
    Log an action to the audit_logs table.
    Uses the currently authenticated user if available.
    """
    user = get_current_user()
    user_id = user['id'] if user else None
    username = user['username'] if user else 'SYSTEM'
    
    execute_query(
        """
        INSERT INTO audit_logs 
        (user_id, username, action, module, record_type, record_id, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, username, action, module, record_type, str(record_id) if record_id else None, description)
    )

def get_audit_logs(limit=100):
    """Retrieve recent audit logs."""
    return execute_query("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,), fetch_all=True)
