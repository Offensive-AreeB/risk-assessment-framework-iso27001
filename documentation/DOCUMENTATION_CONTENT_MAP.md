# DOCUMENTATION CONTENT MAP
**Project:** Risk Assessment Framework Mapped to ISO/IEC 27001 (ZYNVEX-CERT-0666)

| Report Section | Topic | Evidence Required | External Sources | Project Evidence |
|---|---|---|---|---|
| **Ch 1: Intro** | Cybersecurity Risk & GRC context | High | SR-001 (ISO 27001), SR-003 (NIST) | N/A (Theoretical) |
| **Ch 2: Literature** | Inherent vs Residual Risk, Likelihood/Impact | High | SR-002 (ISO 27005), SR-004 (NIST 800-30), SR-009 (Hubbard) | N/A (Theoretical) |
| **Ch 3: Comparisons** | Evaluating existing solutions | Medium | Official vendor documentation (Microsoft, ServiceNow) | COMPARATIVE_ANALYSIS_DATA.md |
| **Ch 4-5: Solution** | App Workflow & Requirements | Low | N/A | `README.md`, Source Code Review |
| **Ch 6: Architecture** | Streamlit + SQLite design | Low | SR-006 (Streamlit), SR-007 (SQLite) | `app.py`, `database/schema.sql`, `database/db.py` |
| **Ch 7: Methodology** | 5x5 Matrix & Scoring | Low | SR-004 (NIST 800-30 - matrix context) | `utils/risk_calculator.py` |
| **Ch 8: ISO Integration**| Annex A & SoA mapping | High | SR-001 (ISO 27001:2022) | `data/iso_27001_2022_controls.py`, `modules/soa.py` |
| **Ch 9-10: Modules** | Application Implementation | None | SR-005 (Python), SR-008 (ReportLab) | `modules/*.py`, Screenshots |
| **Ch 11: Testing** | QA and Acceptance Results | None | N/A | Manual Test results (15/15), `run_qa_audit.py` log |
| **Ch 13: Limitations** | Single-user, no APIs | None | N/A | Source Code Architectural Review |
| **Ch 14: Roadmap** | Enterprise & Multi-tenant SaaS | Medium | N/A | FUTURE_PRODUCT_RESEARCH.md |
