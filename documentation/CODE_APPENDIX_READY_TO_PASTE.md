# APPENDIX A — SELECTED SOURCE CODE AND IMPLEMENTATION EVIDENCE

**Project:** Risk Assessment Framework Mapped to ISO/IEC 27001
**Project ID:** ZYNVEX-CERT-0666
**Prepared by:** Areeb Amjad Khan
**Documentation Freeze:** August 2026

---

## Introduction

This appendix provides selected implementation evidence from the Risk Assessment Framework
source code. It does not reproduce the complete codebase, which is maintained separately
as part of the project submission package.

The snippets presented here were selected because they represent the most technically
significant business logic, security, database integrity, and reporting mechanisms in
the system. Each excerpt is extracted directly from the current production codebase
and verified to reflect the actual implemented state at the time of documentation freeze.

Functional areas covered include: risk scoring, authentication, role-based access control,
audit logging, database integrity, ISO/IEC 27001 control representation, risk-to-control
mapping, residual risk calculation, and automated report generation (PDF and Excel).

The complete source code is submitted as a separate deliverable. These excerpts are
included to provide direct, traceable evidence of the implementation decisions described
in the main body of this report.

---

---

## APPENDIX A.1 — Database Connection and Initialization

**Source File:**
`database/db.py`

**Relevant Function / Section:**
`get_db_connection()`, `db_session()`, `init_db()`

**Purpose:**
This module is the single point of database access for the entire application. It establishes
connections to the SQLite database, provides a context-manager-based session pattern that
automatically commits or rolls back transactions, and initializes the database schema on
application startup by executing the `schema.sql` file.

**Implementation Evidence:**

```python
import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'grc_app.db')

def get_db_connection():
    """Establish and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Documentation comment: Foreign key enforcement must be enabled per-connection in SQLite.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def db_session():
    """Context manager for database sessions."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize the database using the schema.sql file."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    with db_session() as conn:
        conn.executescript(schema_sql)
```

**Technical Explanation:**
The `DB_PATH` is derived at runtime relative to the file location, making the application
portable across environments. `conn.row_factory = sqlite3.Row` allows query results to be
accessed by column name rather than positional index. The `db_session()` context manager
wraps every database operation in an implicit transaction: on success the transaction is
committed; on any exception the transaction is rolled back and the exception is re-raised,
preventing partial writes. `init_db()` is called once at application startup in `app.py`
and uses `CREATE TABLE IF NOT EXISTS` statements within `schema.sql`, ensuring the
function is safe to run against an existing database without destroying data.

**Security / GRC Relevance:**
Centralised database access through a single module prevents connection-handling errors
from being scattered across the application. The mandatory rollback on exception preserves
data integrity: no partial transaction can silently commit in an error state.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.2 — SQLite Foreign-Key Enforcement

**Source File:**
`database/db.py`

**Relevant Function / Section:**
`get_db_connection()`

**Purpose:**
SQLite does not enforce foreign key constraints by default. This snippet shows the
mandatory `PRAGMA` statement that activates referential integrity enforcement on every
connection opened by the application.

**Implementation Evidence:**

```python
def get_db_connection():
    """Establish and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Documentation comment: Without this PRAGMA, SQLite silently permits orphaned records.
    # It must be executed once per connection — not once per session.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
```

**Technical Explanation:**
Because SQLite's foreign key support is off by default for backward compatibility, the
`PRAGMA foreign_keys = ON` statement must be issued after each new connection is established.
The application enforces the following relationships: `risks.asset_id → assets.id`,
`risk_control_mapping.risk_id → risks.id`, `risk_control_mapping.control_id → iso_controls.control_id`,
`risk_treatments.risk_id → risks.id`, and `audit_logs.user_id → users.id`. Cascading
`ON DELETE CASCADE` rules are applied to child tables so that deleting a parent record
(for example, an asset) automatically removes its dependent risk records.

**Security / GRC Relevance:**
Referential integrity is a foundational database security property. Without it, orphaned
records could appear in the risk register or treatment plan for assets that no longer
exist, leading to inaccurate risk reporting — a direct GRC compliance concern.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.3 — Parameterized SQL for Secure Database Operations

**Source File:**
`database/db.py`

**Relevant Function / Section:**
`execute_query()`

**Purpose:**
This function provides the centralized query-execution interface for all CRUD operations
in the application. It accepts a SQL string and a separate tuple of parameters, delegating
parameter substitution to the SQLite driver rather than constructing SQL strings from
raw user input.

**Implementation Evidence:**

```python
def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    """Execute a parameterized query and optionally return results."""
    with db_session() as conn:
        cursor = conn.cursor()
        # Documentation comment: Parameters are supplied separately from the SQL statement.
        # The SQLite driver performs safe substitution using '?' placeholders,
        # reducing the risk of SQL injection by separating SQL structure from
        # user-supplied parameter values.
        cursor.execute(query, params)

        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()

        return cursor.lastrowid
```

**Technical Explanation:**
Every database write in the application passes through `execute_query()`, supplying SQL
and parameters as distinct arguments. The `?` placeholder syntax used throughout the
codebase (for example, `"SELECT * FROM users WHERE username = ?"` with `(username,)`)
ensures that user-supplied values are never concatenated directly into SQL strings. The
function returns either a single row, all rows, or the `lastrowid` of an INSERT,
providing a unified interface for all query patterns.

**Security / GRC Relevance:**
Parameterized queries reduce the risk of SQL injection by separating SQL structure from
user-supplied parameter values. This is a baseline security practice for any application
that accepts user input and stores it in a relational database.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.4 — Risk Score and Risk Classification Logic

**Source File:**
`utils/risk_calculator.py`

**Relevant Function / Section:**
`calculate_risk_score()`, `determine_risk_level()`

**Purpose:**
These two functions constitute the core quantitative risk-scoring engine of the application.
They implement the 5×5 Likelihood × Impact matrix methodology used to assign a numeric
risk score and a categorical risk level to every identified risk.

**Implementation Evidence:**

```python
def calculate_risk_score(likelihood: int, impact: int) -> int:
    """
    Calculate risk score based on 5x5 matrix.
    Score = Likelihood * Impact
    """
    if not (1 <= likelihood <= 5 and 1 <= impact <= 5):
        raise ValueError("Likelihood and Impact must be between 1 and 5.")
    return likelihood * impact


def determine_risk_level(risk_score: int) -> str:
    """
    Determine risk classification based on score.
    1-4   = Low
    5-9   = Medium
    10-16 = High
    17-25 = Critical
    """
    if 1 <= risk_score <= 4:
        return "Low"
    elif 5 <= risk_score <= 9:
        return "Medium"
    elif 10 <= risk_score <= 16:
        return "High"
    elif 17 <= risk_score <= 25:
        return "Critical"
    else:
        raise ValueError(f"Invalid risk score: {risk_score}. Must be between 1 and 25.")
```

**Technical Explanation:**
`calculate_risk_score()` accepts integer Likelihood and Impact values in the range 1–5,
validates the bounds, and returns their product. The theoretical score range is therefore
1 (minimum: 1×1) to 25 (maximum: 5×5). `determine_risk_level()` maps this score to
one of four categorical levels using the thresholds shown in the docstring. Both functions
raise `ValueError` for inputs outside the defined domain, preventing silent calculation
errors from propagating into the database.

**Security / GRC Relevance:**
The risk score is the primary quantitative output of the assessment process. It drives
the risk matrix visualization, risk prioritization in reports, and treatment planning.
The explicit bounds validation ensures that no malformed data entry can produce a score
that falls outside the defined classification scheme, maintaining the integrity of the
risk register.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.5 — 5×5 Risk Matrix Generation

**Source File:**
`modules/dashboard.py`

**Relevant Function / Section:**
`render_dashboard()` — Risk Matrix section (lines 110–164)

**Purpose:**
This excerpt shows how the application transforms the live risk register into an interactive
5×5 heatmap visualization using Plotly. Each cell displays the numeric risk score and
shows the count of risks occupying that Likelihood × Impact position.

**Implementation Evidence:**

```python
# Build matrix data: counts[impact-1][likelihood-1] = number of risks at that cell
counts = [[0 for _ in range(5)] for _ in range(5)]
hover_texts = [["" for _ in range(5)] for _ in range(5)]

for i in range(5):
    for j in range(5):
        impact = i + 1
        likelihood = j + 1
        cell_risks = filtered_df[
            (filtered_df['impact'] == impact) & (filtered_df['likelihood'] == likelihood)
        ]
        counts[i][j] = len(cell_risks)
        if len(cell_risks) > 0:
            titles = "<br>".join(
                [f"- {row['risk_title']} ({row['asset_name']})"
                 for idx, row in cell_risks.iterrows()]
            )
            hover_texts[i][j] = f"Score: {impact*likelihood}<br>Count: {len(cell_risks)}<br>Risks:<br>{titles}"
        else:
            hover_texts[i][j] = f"Score: {impact*likelihood}<br>Count: 0 risks"

# Assign colour zone to each cell based on risk score thresholds
colors = [[0 for _ in range(5)] for _ in range(5)]
for i in range(5):
    for j in range(5):
        score = (i + 1) * (j + 1)
        if score >= 17:   colors[i][j] = 4   # Critical
        elif score >= 10: colors[i][j] = 3   # High
        elif score >= 5:  colors[i][j] = 2   # Medium
        else:             colors[i][j] = 1   # Low

fig_matrix = go.Figure(data=go.Heatmap(
    z=colors,
    x=["1 - Rare", "2 - Unlikely", "3 - Possible", "4 - Likely", "5 - Almost Certain"],
    y=["1 - Insignificant", "2 - Minor", "3 - Moderate", "4 - Major", "5 - Severe"],
    text=[[str((i+1)*(j+1)) for j in range(5)] for i in range(5)],
    texttemplate="%{text}",
    hovertext=hover_texts,
    colorscale=[
        [0,    '#00cc66'], [0.25, '#00cc66'],   # Low
        [0.25, '#ffcc00'], [0.5,  '#ffcc00'],   # Medium
        [0.5,  '#ff6600'], [0.75, '#ff6600'],   # High
        [0.75, '#cc0000'], [1.0,  '#cc0000']    # Critical
    ],
    showscale=False
))
```

**Technical Explanation:**
The matrix is built by iterating all 25 Likelihood × Impact combinations and counting
how many risks from the live `filtered_df` DataFrame occupy each cell. The `colors`
array applies the same score thresholds as `determine_risk_level()` to shade each cell.
The `hover_texts` array populates the interactive tooltip with the specific risk titles
at each position. The Plotly `Heatmap` trace accepts the pre-computed `colors` as the
`z` values and renders the score (not the count) as the visible text within each cell.

**Security / GRC Relevance:**
The interactive risk matrix provides decision-makers with immediate visual identification
of the highest-risk areas of the organization. Colour-coded severity zones align with
the ISO/IEC 27005 qualitative risk evaluation approach.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.6 — Password Hashing and Authentication

**Source File:**
`utils/auth.py`

**Relevant Function / Section:**
`hash_password()`, `verify_password()`, `authenticate_user()`

**Purpose:**
These three functions implement the complete local authentication mechanism. Passwords are
hashed using bcrypt before storage, and authentication is performed by comparing a
submitted plaintext password against the stored hash — the plaintext password is never
persisted at any point.

**Implementation Evidence:**

```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Documentation comment: bcrypt.gensalt() generates a cryptographically random salt
    # for each password. The salt is embedded in the output hash string, so it does not
    # need to be stored separately.
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def authenticate_user(username, password):
    """Attempt to authenticate a user. Returns (bool, user_dict_or_msg)."""
    user_row = execute_query(
        "SELECT * FROM users WHERE username = ?", (username,), fetch_one=True
    )
    if not user_row:
        # Documentation comment: Returns the same message for missing username and wrong
        # password to avoid disclosing which accounts exist (username enumeration defence).
        return False, "Invalid username or password."

    user = dict(user_row)
    if not user['is_active']:
        return False, "Account is disabled."

    if verify_password(password, user['password_hash']):
        return True, user
    return False, "Invalid username or password."
```

**Technical Explanation:**
`hash_password()` calls `bcrypt.gensalt()` to produce a unique random salt for every
password, then uses `bcrypt.hashpw()` to produce the final hash. Because bcrypt embeds
the salt, work factor, and algorithm identifier in the hash string itself, only the single
hash value needs to be stored in the `users` table. `verify_password()` passes the
submitted plaintext and the stored hash directly to `bcrypt.checkpw()`, which extracts
the embedded salt and parameters automatically. The `authenticate_user()` function returns
an identical error message for both non-existent usernames and incorrect passwords,
reducing the information disclosed to a potential attacker attempting to enumerate valid
accounts. Disabled accounts (`is_active = 0`) are rejected before the password comparison
is attempted.

**Security / GRC Relevance:**
Storing bcrypt-hashed passwords rather than plaintext credentials directly addresses
ISO/IEC 27001:2022 Annex A Control 8.5 (Secure Authentication) and 5.17 (Authentication
Information). If the database were compromised, the bcrypt hashes would not immediately
yield usable credentials without significant offline computation.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.7 — Authentication Gate and Session Control

**Source File:**
`app.py`

**Relevant Function / Section:**
Authentication gating block (lines 41–55)

**Purpose:**
This is the central authentication enforcement point in the application. Before any
page content is rendered, the application checks whether the current Streamlit session
holds a valid authentication token. Unauthenticated sessions are redirected to the
login page and execution is halted with `st.stop()`.

**Implementation Evidence:**

```python
from utils.auth import is_authenticated, get_current_user, logout_user
from utils.audit import log_action

# Documentation comment: is_authenticated() reads from Streamlit session_state.
# If the key is absent or False, the user has not logged in during this browser session.
if not is_authenticated():
    render_login_page()
    st.stop()   # Halts all further execution for this request cycle.

# All code below this point executes only for authenticated users.
user = get_current_user()

st.sidebar.markdown(f"**Logged in as:**\n{user['full_name']}")
st.sidebar.markdown(f"**Role:**\n{user['role']}")

if st.sidebar.button("Logout"):
    log_action("Logout", "Authentication", f"User {user['username']} logged out.")
    logout_user()
    st.rerun()
```

**Technical Explanation:**
Streamlit re-executes `app.py` from top to bottom on every user interaction. The
`is_authenticated()` call at line 41 reads `st.session_state.get('authenticated', False)`,
which returns `False` for any new or logged-out session. The `st.stop()` call immediately
halts the rest of `app.py`, ensuring that no downstream module code (dashboard, risk
register, mappings, reports, etc.) can execute for an unauthenticated request, regardless
of query parameters or URL manipulation. On logout, `logout_user()` explicitly deletes
the `user` key from `session_state` and sets `authenticated` to `False`, preventing
any subsequent rerun from restoring the previous session.

**Security / GRC Relevance:**
The `st.stop()` call is the critical enforcement point. Without it, authentication would
be advisory — a user could potentially navigate past the login page by manipulating
Streamlit session state. The logout flow also generates an audit log record, providing
traceability for session termination events.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.8 — Role-Based Access Control Permission Enforcement

**Source File:**
`utils/rbac.py`

**Relevant Function / Section:**
`PERMISSIONS` matrix, `has_permission()`

**Purpose:**
This module defines the complete role-permission mapping and provides the centralized
`has_permission()` function used by every protected module to enforce access control at
the server side before any action is executed.

**Implementation Evidence:**

```python
from utils.auth import get_current_user

ROLES = ["ADMINISTRATOR", "RISK ANALYST", "VIEWER"]

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
    """Check if the current logged-in user has a specific permission."""
    user = get_current_user()
    if not user:
        # Documentation comment: Treats unauthenticated callers as having no permissions,
        # providing a safe default-deny posture.
        return False

    role = user.get("role")
    if role not in PERMISSIONS:
        return False

    return action in PERMISSIONS[role]
```

**Technical Explanation:**
The `PERMISSIONS` dictionary maps each role to an explicit list of permitted actions,
following a whitelist (allow-list) design. Roles not present in the dictionary — including
unrecognised or empty role strings — are denied all permissions by the `role not in
PERMISSIONS` check. `has_permission()` is called within every module that performs a
write operation (for example, in `modules/assets.py` before inserting a record, in
`modules/reports.py` before generating a PDF). This means that hiding a UI button is
not sufficient to enforce access control: the server-side permission check runs
independently on every form submission.

**Security / GRC Relevance:**
Separating UI visibility from authorization enforcement is a security design principle.
A VIEWER role user who somehow triggers a form submission will be rejected by the
`has_permission()` check regardless of what is displayed in the interface. This supports
the least-privilege principle aligned with ISO/IEC 27001:2022 Annex A Control 5.15
(Access Control) and 8.2 (Privileged Access Rights).

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.9 — Administrator Account Protection

**Source File:**
`modules/user_management.py`

**Relevant Function / Section:**
`render_user_management()` — Update User form handler (lines 65–71)

**Purpose:**
This guard prevents an administrator from inadvertently disabling or downgrading the
last active administrator account, which would lock all users out of administrative
functions including User Management and Audit Logs.

**Implementation Evidence:**

```python
if st.form_submit_button("Update User"):
    # Documentation comment: Check whether the target account is currently an ADMINISTRATOR
    # and whether the proposed change would remove its ADMINISTRATOR role or deactivate it.
    if selected_user['role'] == "ADMINISTRATOR" and (
        update_role != "ADMINISTRATOR" or not update_active
    ):
        admin_count = execute_query(
            "SELECT COUNT(*) as c FROM users WHERE role='ADMINISTRATOR' AND is_active=1",
            fetch_one=True
        )['c']
        if admin_count <= 1:
            st.error("Cannot disable or downgrade the last active administrator.")
            st.stop()

    execute_query(
        "UPDATE users SET role = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (update_role, 1 if update_active else 0, selected_user['id'])
    )
```

**Technical Explanation:**
The guard is triggered only when the selected user is an ADMINISTRATOR and the proposed
update would either change the role to a non-administrator role or deactivate the account.
In that case, the application counts the number of currently active administrators in
the database. If the count is 1 (meaning this is the only active administrator),
`st.error()` is displayed and `st.stop()` halts execution before the `UPDATE` query runs.
The `UPDATE` query uses parameterized values and updates `updated_at` using the
database's `CURRENT_TIMESTAMP`.

**Security / GRC Relevance:**
Preventing accidental administrative lock-out is a basic operational security control.
A GRC platform that cannot be administered because all administrator accounts were
deactivated would represent a failure of system governance. This guard ensures the
application maintains at least one active administrator at all times.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.10 — Centralized Audit Logging

**Source File:**
`utils/audit.py`

**Relevant Function / Section:**
`log_action()`

**Purpose:**
This function is the single entry point for all audit log entries in the application.
It resolves the currently authenticated user from session state and writes a structured,
parameterized record to the `audit_logs` table. It is called at every significant
user action across all GRC modules.

**Implementation Evidence:**

```python
from database.db import execute_query
from utils.auth import get_current_user

def log_action(
    action: str,
    module: str,
    description: str,
    record_type: str = None,
    record_id: str = None
):
    """
    Log an action to the audit_logs table.
    Uses the currently authenticated user if available.
    """
    user = get_current_user()
    user_id  = user['id']       if user else None
    username = user['username'] if user else 'SYSTEM'

    # Documentation comment: Passwords, hashes, and sensitive values are never
    # passed to this function. The 'description' parameter must contain only
    # human-readable event summaries.
    execute_query(
        """
        INSERT INTO audit_logs
        (user_id, username, action, module, record_type, record_id, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, username, action, module, record_type,
         str(record_id) if record_id else None, description)
    )
```

**Technical Explanation:**
`log_action()` accepts five fields: the event name (`action`), the application module
that generated the event (`module`), a human-readable description, an optional record
type (e.g., `"risks"`, `"assets"`), and an optional record ID linking the log entry
to a specific database row. The current user is resolved from Streamlit session state;
if no authenticated user is present (for example, during the failed-login event), the
username field defaults to `'SYSTEM'`. All seven column values are inserted via
parameterized SQL through `execute_query()`. Events logged by the application include:
successful and failed logins, logouts, user creation and role changes, password resets,
asset/risk/mapping/treatment CRUD operations, and report generation.

**Security / GRC Relevance:**
Auditability is a requirement of ISO/IEC 27001:2022 Annex A Control 8.15 (Logging) and
is central to governance, risk, and compliance platforms. The audit log provides a
chronological record of who performed which action, when, and on which record. Note that
the audit log records in this application are stored in the same SQLite database and
are not cryptographically protected against tampering by an administrator with direct
database access; this is acknowledged as a limitation of the current local architecture.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.11 — Database Constraint and Graceful Error Handling

**Source File:**
`modules/mapping.py`

**Relevant Function / Section:**
`render_mapping_page()` — Create Mapping form handler

**Purpose:**
The `risk_control_mapping` table enforces a `UNIQUE` index on the `(risk_id, control_id)`
pair, preventing the same risk from being mapped to the same ISO control twice. This
excerpt shows how the application catches the resulting `sqlite3.IntegrityError` and
presents a user-appropriate error message rather than exposing a raw database exception.

**Implementation Evidence:**

```python
import sqlite3

# Documentation comment: The UNIQUE INDEX on (risk_id, control_id) is defined in schema.sql:
# CREATE UNIQUE INDEX IF NOT EXISTS idx_risk_control_mapping
#     ON risk_control_mapping(risk_id, control_id);

submit = st.form_submit_button("Create Mapping")
if submit:
    if not has_permission("MANAGE_MAPPINGS"):
        st.error("Unauthorized")
        st.stop()
    if applicability == "Not Applicable" and not justification.strip():
        st.error("Justification is required when a control is marked as 'Not Applicable'.")
    else:
        try:
            map_id = execute_query(
                """INSERT INTO risk_control_mapping
                   (risk_id, control_id, applicability, justification,
                    implementation_status, implementation_notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (selected_risk_id, selected_control_id, applicability,
                 justification.strip(), status, notes.strip())
            )
            log_action("Mapping Created", "Mappings",
                       f"Mapped risk {selected_risk_id} to control {selected_control_id}",
                       "risk_control_mapping", map_id)
            st.success("Mapping created successfully!")
            st.rerun()
        except sqlite3.IntegrityError:
            st.error(
                "This Risk-to-Control mapping already exists! "
                "Please manage it in the 'Manage Mappings' tab."
            )
        except Exception as e:
            st.error(f"Failed to create mapping: {e}")
```

**Technical Explanation:**
The `try/except` block distinguishes between a `sqlite3.IntegrityError` (which signals a
uniqueness violation) and any other unexpected exception. By catching `IntegrityError`
specifically, the application can display a domain-appropriate message without exposing
the raw SQL constraint name or database internals. The broader `except Exception` clause
catches all other database errors with a generic but informative message. A successful
insert is followed by an audit log entry and a `st.rerun()` to refresh the page state.

**Security / GRC Relevance:**
Graceful integrity error handling prevents duplicate risk-to-control mappings from being
created silently or by user error. In a GRC context, duplicate mappings would inflate
control coverage statistics and produce misleading Statement of Applicability reports.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.12 — ISO/IEC 27001:2022 Control Library Representation

**Source File:**
`data/iso_27001_2022_controls.py`

**Relevant Function / Section:**
`ISO_27001_2022_CONTROLS` list — representative excerpt

**Purpose:**
The application maintains a complete reference library of all 93 ISO/IEC 27001:2022 Annex
A controls as Python dictionaries. This excerpt shows the data structure used for three
controls across two themes to illustrate the representation. The complete list of 93
controls is present in the source file.

**Implementation Evidence:**

```python
ISO_27001_2022_CONTROLS = [
    # Theme 5: Organizational Controls
    {
        "id":    "5.1",
        "theme": "Organizational Controls",
        "name":  "Policies for information security",
        "desc":  "Information security policy and topic-specific policies shall be "
                 "defined, approved by management, published, communicated to and "
                 "acknowledged by relevant personnel and relevant interested parties, "
                 "and reviewed at planned intervals and if significant changes occur."
    },
    {
        "id":    "5.15",
        "theme": "Organizational Controls",
        "name":  "Access control",
        "desc":  "Rules to control physical and logical access to information and "
                 "other associated assets shall be established and implemented based "
                 "on business and information security requirements."
    },
    # Theme 8: Technological Controls
    {
        "id":    "8.5",
        "theme": "Technological Controls",
        "name":  "Secure authentication",
        "desc":  "Secure authentication technologies and procedures shall be "
                 "implemented based on information access restrictions and the "
                 "topic-specific policy on access control."
    },
    # ... (90 additional controls spanning Organizational, People,
    #      Physical, and Technological themes are defined in the source file)
]
```

**Technical Explanation:**
Each dictionary entry contains four keys: `id` (the clause reference, e.g., `"5.1"`),
`theme` (one of the four Annex A themes), `name` (the short control title), and `desc`
(the normative control statement from the standard). These records are seeded into the
`iso_controls` table at first run by the `data/seed_data.py` module, where they become
the reference dataset used for all risk-to-control mapping operations and Statement of
Applicability generation. The four themes are: Organizational Controls (37 controls),
People Controls (8 controls), Physical Controls (14 controls), and Technological Controls
(34 controls), totalling 93.

**Security / GRC Relevance:**
This library is the normative foundation of the GRC platform's compliance functionality.
By embedding the complete control reference in the application rather than relying on an
external data source, the system can operate in fully offline, air-gapped environments —
an important property for sensitive GRC work.

> **Note:** The control descriptions in this file are derived from the ISO/IEC 27001:2022
> standard. This representation is used for internal GRC reference purposes only and does
> not constitute a reproduction or replacement of the official standard.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.13 — Risk-to-Control Mapping Implementation

**Source File:**
`modules/mapping.py`

**Relevant Function / Section:**
`render_mapping_page()` — mapping INSERT statement and schema reference

**Purpose:**
This snippet shows the SQL INSERT that creates the relational link between a risk record
and an ISO 27001 control record. It demonstrates the three-entity relationship: Risk →
Mapping Record → ISO Control, along with the additional applicability and implementation
metadata recorded at the time of mapping.

**Implementation Evidence:**

```python
# Documentation comment: The mapping record sits between risks and iso_controls,
# creating a many-to-many relationship with additional attributes.
#
# Schema (from database/schema.sql):
#   risk_control_mapping (
#       id                    INTEGER PRIMARY KEY AUTOINCREMENT,
#       risk_id               INTEGER NOT NULL  → REFERENCES risks(id)      ON DELETE CASCADE,
#       control_id            TEXT    NOT NULL  → REFERENCES iso_controls(control_id) ON DELETE CASCADE,
#       applicability         TEXT,             -- "Applicable" / "Not Applicable"
#       justification         TEXT,             -- Required if Not Applicable
#       implementation_status TEXT,             -- "Planned" / "Partially Implemented" / "Implemented"
#       implementation_notes  TEXT
#   )
#   UNIQUE INDEX on (risk_id, control_id) — prevents duplicate mappings.

map_id = execute_query(
    """INSERT INTO risk_control_mapping
       (risk_id, control_id, applicability, justification,
        implementation_status, implementation_notes)
       VALUES (?, ?, ?, ?, ?, ?)""",
    (selected_risk_id, selected_control_id, applicability,
     justification.strip(), status, notes.strip())
)
log_action(
    "Mapping Created", "Mappings",
    f"Mapped risk {selected_risk_id} to control {selected_control_id}",
    "risk_control_mapping", map_id
)
```

**Technical Explanation:**
The mapping record carries both the foreign-key relationship (`risk_id`, `control_id`)
and three additional GRC attributes: applicability (whether the control is considered
relevant to this risk), justification (required when marking a control as not applicable,
consistent with ISO 27001 SoA requirements), and implementation status (the current
deployment state of the control). Together these attributes form the evidence base for
the automated Statement of Applicability report. The `ON DELETE CASCADE` constraints
ensure that mapping records are automatically removed if the parent risk or control is
deleted.

**Security / GRC Relevance:**
The Risk-to-Control Mapping is the mechanism through which the application demonstrates
ISO 27001 compliance linkage. Each mapping provides documented justification for control
inclusion or exclusion, which is a mandatory component of a conformant Statement of
Applicability.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.14 — Residual Risk and Risk Reduction Calculation

**Source File:**
`modules/treatments.py`

**Relevant Function / Section:**
Treatment Detail View (lines 105–106)

**Purpose:**
This snippet shows the actual residual risk reduction calculation used in the Treatment
Detail View and reflected in the generated PDF and Excel reports.

**Implementation Evidence:**

```python
# Documentation comment: 'inh_risk' is the original risk record from the risks table.
# 't_detail' is the corresponding risk_treatments record.
# Both residual_likelihood and residual_impact were validated to be in range 1–5
# when the treatment was saved, so residual_score is in range 1–25.

reduction     = inh_risk['risk_score'] - t_detail['residual_score']
reduction_pct = (reduction / inh_risk['risk_score']) * 100 if inh_risk['risk_score'] > 0 else 0

# Display:
# col_r1.metric("Inherent Score",    inh_risk['risk_score'])
# col_r2.metric("Residual Score",    t_detail['residual_score'])
# col_r3.metric("Reduction Points",  f"{reduction}")
# col_r4.metric("Reduction %",       f"{reduction_pct:.1f}%")
```

**The residual score itself is calculated and persisted at treatment-save time:**

```python
# From the treatment form submit handler (modules/treatments.py):
r_score = calculate_risk_score(r_lik, r_imp)
r_level = determine_risk_level(r_score)

treat_id = execute_query(
    """INSERT INTO risk_treatments
       (risk_id, treatment_option, treatment_description, treatment_owner,
        target_date, treatment_status, residual_likelihood, residual_impact,
        residual_score, residual_risk_level)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    (selected_risk_id, t_option, t_desc.strip(), t_owner.strip(),
     t_date.isoformat(), t_status, r_lik, r_imp, r_score, r_level)
)
```

**Technical Explanation:**
Residual risk is calculated using the same `calculate_risk_score()` function as inherent
risk, applied to the analyst-estimated post-treatment likelihood and impact values. The
reduction in absolute score (`reduction`) and percentage (`reduction_pct`) are computed
at display time, not stored. The division-by-zero guard (`if inh_risk['risk_score'] > 0
else 0`) prevents a `ZeroDivisionError` in the event that a risk score of 0 exists;
however, because `calculate_risk_score()` enforces a minimum input value of 1 (minimum
product = 1), a score of 0 cannot be produced through the normal application workflow.

**Security / GRC Relevance:**
Residual risk quantification is a core requirement of ISO/IEC 27005 risk treatment
evaluation. By storing the residual score and level at treatment-save time, the
application preserves a point-in-time record of the expected post-treatment risk state,
which is essential for audit trails and treatment effectiveness reviews.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.15 — Automated PDF Report Generation

**Source File:**
`modules/reports.py`

**Relevant Function / Section:**
`create_pdf_report()` (lines 872–931)

**Purpose:**
This function orchestrates the generation of a multi-section PDF risk assessment report
using the ReportLab library. It demonstrates how live database records are assembled into
a structured document with a cover page, executive summary, risk matrix, risk register,
ISO/SoA section, and treatment plan — with content controlled by the user-selected scope.

**Implementation Evidence:**

```python
def create_pdf_report(filename, scope, data):
    risks, treatments, mappings, assets, controls = data
    styles_obj = get_styles()
    gen_date   = datetime.now().strftime("%d %B %Y, %H:%M")

    # Build the ReportLab document with landscape A4 layout and metadata.
    doc = BaseDocTemplate(
        filename,
        pagesize=landscape(A4),
        rightMargin=30, leftMargin=30,
        topMargin=38,   bottomMargin=30,
        title="Risk Assessment Framework — ISO/IEC 27001:2022-Aligned GRC Assessment",
        author="Areeb Amjad Khan",
        subject="Information Security Risk Assessment & GRC",
    )
    doc.report_scope = scope
    doc.gen_date     = gen_date

    # Two page templates: Cover (full-bleed) and Normal (with margins).
    frame_cover  = Frame(0, 0, w, h, id='cover_frame',
                         topPadding=0, bottomPadding=0,
                         rightPadding=0, leftPadding=0)
    frame_normal = Frame(30, 30, w - 60, h - 68, id='normal_frame')

    template_cover  = PageTemplate(id='Cover',  frames=[frame_cover],
                                   onPage=on_cover_page)
    template_normal = PageTemplate(id='Normal', frames=[frame_normal])
    doc.addPageTemplates([template_cover, template_normal])

    elements = []
    elements.append(Paragraph(" ", styles_obj["Body"]))   # Force cover page render.
    elements.append(NextPageTemplate('Normal'))
    elements.append(PageBreak())

    # Build sections according to selected report scope.
    elements += build_exec_summary(risks, treatments, mappings, assets, styles_obj)
    elements += build_matrix_section(risks, styles_obj)

    if scope in ("Full Risk Assessment", "Risk Register Only"):
        elements += build_top_risks(risks, styles_obj)
        elements += build_risk_register(risks, styles_obj)

    if scope in ("Full Risk Assessment", "Statement of Applicability"):
        elements += build_soa_section(mappings, styles_obj)

    if scope in ("Full Risk Assessment", "Risk Treatment Plan"):
        elements += build_treatment_section(treatments, risks, styles_obj)

    # NumberedCanvas provides "Page X of Y" footers on all non-cover pages.
    doc.build(elements, canvasmaker=NumberedCanvas)
    return filename
```

**Technical Explanation:**
`create_pdf_report()` receives pre-filtered risk data, constructs a `BaseDocTemplate`
with two `PageTemplate` objects (one for the full-bleed cover page, one for content pages
with standard margins), and assembles a list of `Platypus` flowable elements. The `scope`
parameter selects which report sections to include, allowing scoped exports (e.g.,
`"Statement of Applicability"` only, or a `"Full Risk Assessment"` with all sections).
`NumberedCanvas` is a custom `Canvas` subclass that records all pages during the build
and draws "Page X of Y" footers in a second pass, enabling correct total-page-count
rendering. The cover page is drawn procedurally using ReportLab's low-level canvas API
via the `on_cover_page` callback.

**Security / GRC Relevance:**
Automated report generation provides consistent, reproducible documentation outputs. The
scope-based selection means that a Statement of Applicability can be exported independently
for submission to an auditor without exporting the full internal risk register.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.16 — Excel Workbook Generation

**Source File:**
`modules/reports.py`

**Relevant Function / Section:**
`create_excel_report()` — Risk Register worksheet (lines 1100–1118)

**Purpose:**
This excerpt demonstrates how the application exports the live risk register to a styled
Excel worksheet using openpyxl. It shows header row construction, row-level data mapping,
conditional cell colouring by risk level, alternating row shading, and freeze-pane
configuration.

**Implementation Evidence:**

```python
def create_excel_report(filename, scope, data):
    risks, treatments, mappings, assets, controls = data
    wb  = Workbook()
    hdr_s = xl_header_style()   # Returns a dict of Font, Fill, Alignment, Border styles.

    # ── Risk Register worksheet ────────────────────────────────────────────
    ws_r = wb.create_sheet("Risk Register")
    ws_r.sheet_view.showGridLines = False

    headers = ["ID", "Asset", "Risk Title", "Threat", "Vulnerability",
               "Existing Controls", "Likelihood", "Impact", "Risk Score",
               "Risk Level", "Risk Owner", "Status"]
    ws_r.append(headers)

    # Apply navy header style to each header cell.
    for c, h in enumerate(headers, 1):
        xl_apply(ws_r.cell(1, c), hdr_s)

    # Write one row per risk record with conditional colouring.
    for i, r in enumerate(risks, 2):
        ws_r.append([
            r["id"],         r["asset_name"],  r["risk_title"],
            r["threat"],     r["vulnerability"], r["existing_controls"],
            r["likelihood"], r["impact"],       r["risk_score"],
            r["risk_level"], r["risk_owner"],   r["status"]
        ])
        # Apply risk-level colour to the "Risk Level" column (column 10).
        xl_level_cell(ws_r.cell(i, 10), r["risk_level"])
        # Apply alternating row background for readability.
        xl_alt_row(ws_r, i, 1, 12, i)

    ws_r.freeze_panes = "A2"                            # Keep header visible when scrolling.
    ws_r.auto_filter.ref = f"A1:L{ws_r.max_row}"       # Enable column filter dropdowns.
    xl_set_col_widths(ws_r, [5, 18, 30, 22, 22, 22, 10, 10, 10, 12, 16, 14])

    wb.save(filename)
    return filename
```

**Technical Explanation:**
`xl_apply()` sets multiple cell properties (font, fill, alignment, border) from a style
dictionary in a single call. `xl_level_cell()` applies a colour-coded fill to the Risk
Level cell based on a lookup against the `LEVEL_XL` colour map (`Critical=red`,
`High=orange`, `Medium=yellow`, `Low=green`). `xl_alt_row()` applies a light grey fill
to even-numbered data rows to improve visual scannability. `freeze_panes = "A2"` keeps
the header row visible as the user scrolls down. The workbook produced by the full
`create_excel_report()` function contains six worksheets: Executive Summary, Asset
Register, Risk Register, Risk Treatment, ISO 27001 Controls, Statement of Applicability,
and Risk-Control Mapping.

**Security / GRC Relevance:**
Machine-readable Excel exports allow data to be consumed by other analytical tools or
imported into enterprise GRC systems. The inclusion of all six GRC worksheets in a single
workbook provides a self-contained evidence package suitable for auditor submission.

**Documentation Classification:** IMPLEMENTED

---

---

## APPENDIX A.17 — Code Evidence Traceability Matrix

| Snippet | Source File | Function / Section | Demonstrates | Related Report Section |
|---|---|---|---|---|
| A.1 | `database/db.py` | `get_db_connection()`, `db_session()`, `init_db()` | Database initialization and session management | Chapter 6 — System Architecture |
| A.2 | `database/db.py` | `get_db_connection()` | SQLite foreign-key enforcement | Chapter 6 — System Architecture |
| A.3 | `database/db.py` | `execute_query()` | Parameterized SQL / injection risk reduction | Chapter 6 — System Architecture; Chapter 13 — Security |
| A.4 | `utils/risk_calculator.py` | `calculate_risk_score()`, `determine_risk_level()` | Core risk scoring and classification logic | Chapter 7 — Risk Assessment Methodology |
| A.5 | `modules/dashboard.py` | `render_dashboard()` — matrix section | 5×5 interactive risk matrix generation | Chapter 9 — Dashboard Module |
| A.6 | `utils/auth.py` | `hash_password()`, `verify_password()`, `authenticate_user()` | bcrypt password hashing and authentication | Chapter 9 — Authentication; Chapter 13 — Security |
| A.7 | `app.py` | Authentication gate (lines 41–55) | Session authentication gating and logout | Chapter 9 — Authentication; Chapter 13 — Security |
| A.8 | `utils/rbac.py` | `PERMISSIONS`, `has_permission()` | Role-Based Access Control enforcement | Chapter 9 — RBAC; Chapter 13 — Security |
| A.9 | `modules/user_management.py` | Update User form handler | Last-administrator protection guard | Chapter 9 — User Management; Chapter 13 — Security |
| A.10 | `utils/audit.py` | `log_action()` | Centralized audit logging | Chapter 9 — Audit Logging; Chapter 13 — Security |
| A.11 | `modules/mapping.py` | Create Mapping form handler | Database constraint handling and graceful errors | Chapter 9 — Risk-Control Mapping |
| A.12 | `data/iso_27001_2022_controls.py` | `ISO_27001_2022_CONTROLS` | ISO/IEC 27001:2022 Annex A control library | Chapter 8 — ISO 27001 Integration |
| A.13 | `modules/mapping.py` | Mapping INSERT handler | Risk-to-Control mapping relational design | Chapter 8 — ISO 27001 Integration |
| A.14 | `modules/treatments.py` | Treatment Detail View + save handler | Residual risk and risk reduction calculation | Chapter 7 — Risk Methodology; Chapter 9 — Treatments |
| A.15 | `modules/reports.py` | `create_pdf_report()` | Automated PDF report generation | Chapter 10 — Reporting System |
| A.16 | `modules/reports.py` | `create_excel_report()` — Risk Register sheet | Excel workbook generation and styling | Chapter 10 — Reporting System |

---

*End of Appendix A — Selected Source Code and Implementation Evidence*
