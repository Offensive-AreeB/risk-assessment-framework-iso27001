from utils.auth import get_current_user

# Define valid roles
ROLES = ["ADMINISTRATOR", "RISK ANALYST", "VIEWER"]

# Define actions
PERMISSIONS = {
    "ADMINISTRATOR": [
        "VIEW_DASHBOARD", "MANAGE_ASSETS", "MANAGE_RISKS", "MANAGE_MAPPINGS",
        "MANAGE_TREATMENTS", "VIEW_REPORTS", "GENERATE_REPORTS", 
        "MANAGE_USERS", "VIEW_AUDIT_LOGS"
    ],
    "RISK ANALYST": [
        "VIEW_DASHBOARD", "MANAGE_ASSETS", "MANAGE_RISKS", "MANAGE_MAPPINGS",
        "MANAGE_TREATMENTS", "VIEW_REPORTS", "GENERATE_REPORTS"
    ],
    "VIEWER": [
        "VIEW_DASHBOARD", "VIEW_REPORTS"
    ]
}

def has_permission(action: str) -> bool:
    """Check if the current logged in user has a specific permission."""
    user = get_current_user()
    if not user:
        return False
    
    role = user.get("role")
    if role not in PERMISSIONS:
        return False
        
    return action in PERMISSIONS[role]

def is_admin() -> bool:
    """Convenience method to check if current user is an administrator."""
    user = get_current_user()
    return user is not None and user.get("role") == "ADMINISTRATOR"
