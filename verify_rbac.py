import sqlite3
import os
import sys

# Ensure db is initialized
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db, execute_query
from utils.auth import create_initial_admin, authenticate_user
from utils.audit import get_audit_logs

init_db()

print("TEST A: Creating administrator account...")
res, msg = create_initial_admin("admin", "adminpass", "System Administrator")
print(f"Result: {res}, Msg: {msg}")

print("TEST B: Login successfully...")
res, user = authenticate_user("admin", "adminpass")
print(f"Result: {res}, User: {user['username'] if res else ''}")

print("TEST C: Failed login produces an appropriate error...")
res, msg = authenticate_user("admin", "wrongpass")
print(f"Result: {res}, Msg: {msg}")

print("Checking users table...")
users = execute_query("SELECT * FROM users", fetch_all=True)
for u in users:
    print(dict(u))

print("Checking audit logs...")
logs = get_audit_logs(10)
for l in logs:
    print(f"Log: {l['action']} - {l['description']}")

print("All programmatic tests completed.")
