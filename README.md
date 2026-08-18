# Risk Assessment Framework Mapped to ISO/IEC 27001

**Project ID:** ZYNVEX-CERT-0666  
**Author:** Areeb Amjad Khan  
**Status:** Final Release (Phase 7D)

## 1. Project Overview
The Risk Assessment Framework is a professional, web-based Governance, Risk, and Compliance (GRC) application. It automates a practical cybersecurity risk assessment workflow aligned with concepts from ISO/IEC 27001:2022. 

The core workflow replaces fragmented, spreadsheet-based manual processes with a centralized, repeatable system:
`Asset Registration → Threat & Vulnerability Identification → Likelihood & Impact Assessment → Inherent Risk Calculation → Risk Classification → ISO 27001 Control Mapping → Statement of Applicability (SoA) → Risk Treatment → Residual Risk Assessment → Dashboard & Reporting`

## 2. Problem Statement
Historically, many organizations struggle with:
- Managing fragmented, manual spreadsheet-based risk registers.
- Inconsistent risk scoring and classification methodologies.
- Difficulty mapping identified risks to standardized mitigating controls.
- Difficulty maintaining an up-to-date Statement of Applicability (SoA).
- Lack of centralized tracking for risk treatment strategies.
- Cumbersome manual calculation of residual risk.
- Limited visualization and tedious manual report generation.

This framework solves these challenges by providing a unified, centralized application that dynamically integrates assets, risks, and controls into a single persistent database, backed by real-time visualizations and professional automated reporting.

## 3. Objectives
1. Develop a centralized, web-based risk assessment application.
2. Register and manage organizational assets.
3. Identify threats and vulnerabilities associated with assets.
4. Automate Likelihood × Impact risk scoring.
5. Classify risks through an industry-standard 5×5 matrix.
6. Map risks to ISO/IEC 27001:2022 Annex A controls.
7. Generate a dynamic Statement of Applicability.
8. Manage risk treatment plans and target dates.
9. Calculate residual risk post-treatment.
10. Provide a visual, data-driven risk dashboard.
11. Generate professional, fully styled PDF and Excel reports.

## 4. Technology Stack
- **Presentation Layer:** Streamlit
- **Application/Business Logic:** Python 3 Modules
- **Calculation/Validation:** Custom Utilities (`utils/`)
- **Data Layer:** SQLite
- **Reporting Layer:** ReportLab (PDF), openpyxl (Excel)
- **Visualization:** Plotly

## 5. System Architecture
The application follows a clean, decoupled modular architecture.

```
User
  ↓
Streamlit Interface (app.py) + Authentication Gate
  ↓
Application Modules (modules/*.py)
  ↓
Validation / RBAC / Risk Calculation (utils/*.py)
  ↓
SQLite Database (grc_app.db)
  ↓
Dashboard / SoA / Treatment / Reports / Audit Logs
```

## 6. Functional Requirements
- **FR-01 Asset Management:** Create, read, update, and track assets by criticality. (Implemented in `modules/assets.py`)
- **FR-02 Risk Management:** Register risks, threats, and vulnerabilities linked to assets. (Implemented in `modules/risks.py`)
- **FR-03 Risk Calculation:** Automate calculating `Likelihood × Impact`. (Implemented in `utils/risk_calculator.py`)
- **FR-04 Risk Classification:** Automatically classify risks (Low, Medium, High, Critical) based on score. (Implemented in `utils/risk_calculator.py`)
- **FR-05 Risk Filtering/Search:** Filter risks by level, asset, or status. (Implemented in `modules/risks.py`)
- **FR-06 ISO Control Library:** Browse and filter 93 ISO/IEC 27001:2022 controls. (Implemented in `modules/controls.py`)
- **FR-07 Risk-Control Mapping:** Link risks to specific controls with justification. (Implemented in `modules/mapping.py`)
- **FR-08 Statement of Applicability:** Dynamically generate SoA from mappings. (Implemented in `modules/soa.py`)
- **FR-09 Risk Treatment:** Assign treatment strategies and target dates to risks. (Implemented in `modules/treatments.py`)
- **FR-10 Residual Risk:** Calculate post-treatment risk scores and reduction percentage. (Implemented in `modules/treatments.py`)
- **FR-11 Dashboard:** Visualize live KPIs and the 5x5 matrix. (Implemented in `modules/dashboard.py`)
- **FR-12 PDF Reporting:** Export professional, formatted PDF assessments. (Implemented in `modules/reports.py`)
- **FR-13 Excel Reporting:** Export robust Excel workbooks with frozen headers. (Implemented in `modules/reports.py`)
- **FR-14 Authentication & RBAC:** Secure login with bcrypt hashing and Role-Based Access Control. (Implemented in `utils/auth.py`, `utils/rbac.py`)
- **FR-15 User Management:** Admin interface for user provisioning and password resets. (Implemented in `modules/user_management.py`)
- **FR-16 Audit Logging:** Centralized, parameterized tracking of all system events. (Implemented in `utils/audit.py`, `modules/audit_logs.py`)
- **FR-17 Methodology Information:** Provide user guidance on the underlying risk methodology. (Implemented in `modules/about.py`)

## 7. Non-Functional Requirements
- **Usability:** Clean, intuitive UI built with Streamlit's modern design patterns.
- **Maintainability:** Modular architecture separating UI, business logic, and data.
- **Data Integrity:** Strict SQLite schema with foreign keys and unique constraints.
- **Validation:** Front-end form validation and back-end logic to prevent invalid states.
- **Local/Offline Operation:** Entire stack runs locally without external cloud dependencies.
- **Performance:** Lightweight execution suitable for SQLite.

## 8. Database Structure
The application utilizes an SQLite database designed for relational integrity:

1. **`assets`**: Stores organizational assets (PK: `id`).
2. **`risks`**: Stores identified risks. Linked to assets via `asset_id` FK.
3. **`iso_controls`**: Static reference library for the 93 ISO controls.
4. **`risk_control_mapping`**: Junction table mapping risks to controls (FK: `risk_id`, `control_id`). Enforces a UNIQUE constraint per risk-control pair.
5. **`risk_treatments`**: Stores treatment plans linked to risks via `risk_id` FK.
6. **`users`**: Stores user accounts, bcrypt password hashes, and RBAC roles.
7. **`audit_logs`**: Immutable ledger of system events, linked to `users` via `user_id` FK.

## 9. Risk Assessment Methodology
The system employs a standardized quantitative/qualitative hybrid approach:

**Risk Score = Likelihood (1–5) × Impact (1–5)**

**Classification Boundaries:**
- **Low:** 1 – 4
- **Medium:** 5 – 9
- **High:** 10 – 16
- **Critical:** 17 – 25

The 5×5 matrix plots the intersections of these values. 
- **Inherent Risk:** The raw risk score calculated before any mitigating treatments are applied.
- **Residual Risk:** The revised risk score calculated after a Risk Treatment Plan has been implemented or evaluated.

## 10. ISO/IEC 27001:2022 Integration
The framework includes a fully searchable library of the **93** ISO/IEC 27001:2022 Annex A controls grouped by four themes:
- Organizational (37 controls)
- People (8 controls)
- Physical (14 controls)
- Technological (34 controls)

Users map identified risks to relevant controls, specifying:
- **Applicability** (Applicable / Not Applicable)
- **Justification** (Required if Not Applicable)
- **Implementation Status**
- **Notes**

These mappings dynamically aggregate into the overall **Statement of Applicability (SoA)**.

## 11. Risk Treatment & Residual Risk
Users address identified risks by creating Treatment Plans. Supported strategies include:
- **Mitigate**, **Accept**, **Transfer**, **Avoid**

The module tracks treatment descriptions, owners, target dates, and statuses. The system flags overdue treatments. Users input expected residual likelihood and impact, and the system automatically calculates the **Residual Score**, **Residual Risk Level**, and the total **Risk Reduction %**.

## 12. Dashboard & Reporting
- **Dashboard:** Generates live KPIs from SQLite data, displaying total assets, risk distribution, treatment statuses, overdue treatments, and a dynamic 5×5 Risk Matrix.
- **PDF Export:** Produces a highly professional corporate report featuring a dedicated cover page, executive summary, stylized risk matrix, full risk register, SoA, and treatment plans.
- **Excel Export:** Generates an Excel workbook containing multiple clean worksheets (Executive Summary, Asset Register, Risk Register, Risk Treatment, ISO 27001 Controls, Risk-Control Mapping) complete with formatting and frozen headers.

## 13. Security Considerations
- **Relational Integrity:** Foreign keys are explicitly enforced via PRAGMA commands.
- **SQL Injection Prevention:** All queries utilize parameterized values (`?`), fully mitigating basic injection threats.
- **Constraint Enforcement:** Duplicate mapping attempts are trapped gracefully using `sqlite3.IntegrityError` handling.
- **Safe Math:** Risk reduction calculations implement division-by-zero safeguards.
- **Offline Architecture:** Does not rely on external APIs, protecting sensitive organizational data.
- **Authentication:** Local bcrypt password hashing prevents plaintext password storage.
- **Authorization:** Server-side RBAC validation protects endpoints regardless of UI visibility.
- **Auditability:** Core events are logged via parameterized insertion for accountability.

## 14. Testing Results
The application has undergone rigorous evaluation:

**Automated QA: PASS — 0 failures**
**Manual Acceptance Testing: PASS — 15/15 tests**

| Test ID | Test Area | Result |
|---|---|---|
| T-001 | Application Launch | PASS |
| T-002 | Asset Management | PASS |
| T-003 | Risk Register | PASS |
| T-004 | Risk Matrix | PASS |
| T-005 | ISO Controls | PASS |
| T-006 | Risk-Control Mapping | PASS |
| T-007 | SoA | PASS |
| T-008 | Risk Treatment | PASS |
| T-009 | Overdue Logic | PASS |
| T-010 | Dashboard | PASS |
| T-011 | Reporting | PASS |
| T-012 | Report Filters | PASS |
| T-013 | Methodology | PASS |
| T-014 | Navigation & Usability | PASS |
| T-015 | Auto-Reload | PASS |

## 15. Limitations
- **Local Database:** Designed around SQLite, limiting multi-user concurrency.
- **SSO/IdP:** No external Identity Provider integration (e.g., Entra ID, Okta).
- **Practical Scope:** Designed as an educational/practical tool; it does not replace enterprise GRC platforms.
- **No External Integrations:** Does not pull from external threat intelligence feeds.

## 16. Future Enhancements
- Migration to an enterprise relational database (e.g., PostgreSQL).
- Cloud deployment configurations (e.g., Docker/AWS).
- External Identity Provider integration (SSO).
- Real-time external threat intelligence integrations.
- Support for additional compliance frameworks (e.g., NIST CSF, SOC 2).
- Historical risk trending analytics.

## 17. Installation & Usage

1. Clone or download the project repository.
2. Open a terminal in the project directory.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the application:
   ```bash
   streamlit run app.py
   ```
5. Open the displayed local URL in your web browser (typically `http://localhost:8502`).
6. **First Run Setup:** On the first launch, the system will prompt you to create the initial Administrator account. You will use this account to log in and provision other users.

## 18. Project Structure
```
Risk Assessment Framework/
│
├── app.py
├── requirements.txt
├── README.md
│
├── database/
│   ├── schema.sql
│   └── db.py
│
├── modules/
│   ├── dashboard.py
│   ├── assets.py
│   ├── risks.py
│   ├── controls.py
│   ├── mapping.py
│   ├── soa.py
│   ├── treatments.py
│   ├── reports.py
│   ├── about.py
│   ├── login.py
│   ├── user_management.py
│   └── audit_logs.py
│
├── utils/
│   ├── risk_calculator.py
│   ├── validators.py
│   ├── auth.py
│   ├── rbac.py
│   └── audit.py
│
├── data/
│   ├── iso_27001_2022_controls.py
│   └── seed_data.py
│
├── reports/
│   └── generated/
│
└── .streamlit/
    └── config.toml
```

## 19. Disclaimer
This project is a practical/educational Risk Assessment and GRC framework aligned with concepts from ISO/IEC 27001:2022. It is not a substitute for a formal ISO/IEC 27001 certification audit, accredited certification body, professional consultancy, or organization-specific compliance assessment.
