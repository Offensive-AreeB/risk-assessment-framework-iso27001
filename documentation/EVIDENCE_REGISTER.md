# EVIDENCE REGISTER
**Project:** Risk Assessment Framework Mapped to ISO/IEC 27001 (ZYNVEX-CERT-0666)

| ID | Claim | Evidence Source | Status | Notes |
|----|-------|-----------------|--------|------|
| EV-001 | Risk Score = Likelihood × Impact | `utils/risk_calculator.py` line 8 | IMPLEMENTED | Bounds strictly validated (1-5). |
| EV-002 | 5×5 Risk Matrix Visualization | `modules/dashboard.py` (Plotly heatmap) | IMPLEMENTED | Dynamically aggregates risk scores. |
| EV-003 | 93 Annex A Controls | `data/iso_27001_2022_controls.py` | IMPLEMENTED | Contains exactly 93 controls from the 2022 standard across 4 themes. |
| EV-004 | SQLite Backend | `database/db.py` line 9 | IMPLEMENTED | Connects natively to `grc_app.db`. |
| EV-005 | Parameterized SQL | `database/db.py` line 45 | IMPLEMENTED | Uses `?` execution tuples to prevent SQL injection. |
| EV-006 | Foreign Key Enforcement | `database/db.py` line 12 | IMPLEMENTED | Executes `PRAGMA foreign_keys = ON`. |
| EV-007 | Duplicate Mapping Protection | `modules/mapping.py` line 63 | IMPLEMENTED | Handles `sqlite3.IntegrityError` to prevent duplicate maps. |
| EV-008 | PDF Generation | `modules/reports.py` line 870 | IMPLEMENTED | Uses `reportlab.platypus` for dynamic document building. |
| EV-009 | Excel Generation | `modules/reports.py` line 1050 | IMPLEMENTED | Uses `openpyxl` with styled headers. |
| EV-010 | Residual Risk Calculation | `modules/treatments.py` line 153 | IMPLEMENTED | Handles division-by-zero securely. |
| EV-011 | Risk Treatment Strategies | `modules/treatments.py` | IMPLEMENTED | Supports Mitigate, Accept, Transfer, Avoid. |
| EV-012 | Authentication & RBAC | Source Inspection | LIMITATION | Hard limitation; single-user architecture without login. |
| EV-013 | Multi-user / Cloud Deployment | Source Inspection | LIMITATION | Requires local `streamlit run`. |
| EV-014 | Automated API Integrations | Source Inspection | LIMITATION | Entirely isolated; no outbound integrations. |
| EV-015 | Enterprise SaaS & Multi-Tenancy | Architectural Review | FUTURE | Proposed for later lifecycle phases. |
| EV-016 | AI-assisted Threat Identification | Architectural Review | FUTURE | Proposed for future 'Intelligent GRC' phase. |
