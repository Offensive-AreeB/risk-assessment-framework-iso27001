# COMPARATIVE ANALYSIS DATA
**Project:** Risk Assessment Framework Mapped to ISO/IEC 27001 (ZYNVEX-CERT-0666)

This document contains objective research for Chapter 3 comparing our framework against existing paradigms.

### 1. Manual Spreadsheet-Based Risk Registers
*   **Deployment:** None (Desktop files)
*   **Cost:** "Free" (Included with Office suites)
*   **Control Mapping:** Error-prone, relies on manual VLOOKUPs or manual entry.
*   **Compliance Workflows:** Difficult to maintain a live SoA; prone to versioning issues.
*   **Collaboration:** High risk of lock conflicts unless using cloud sheets, which lack relational integrity.
*   **Reporting:** Manual, tedious aggregation.

### 2. Enterprise GRC Platforms (e.g., ServiceNow GRC, Microsoft Purview)
*   **Deployment:** Cloud/SaaS or Heavy On-Premises.
*   **Cost:** Commercial pricing varies by deployment, licensing model, and edition (typically highly expensive, enterprise-tier).
*   **Control Mapping:** Advanced, cross-framework mapping (ISO to NIST to CIS).
*   **Compliance Workflows:** Automated, continuous monitoring, policy management, evidence collection.
*   **Collaboration:** Enterprise RBAC, audit trails, workflow approvals.
*   **Integrations:** Vulnerability scanners, SIEM, Identity Providers (Azure AD / Entra ID).
*   **Suitability:** Designed for large enterprises; often overkill and too complex for small teams, students, or SMEs needing a rapid assessment.

### 3. Proposed Framework (ZYNVEX-CERT-0666)
*   **Deployment:** Local / Offline (Lightweight Python environment).
*   **Cost:** Open-source / Educational.
*   **Control Mapping:** Natively integrated ISO/IEC 27001:2022 mapping with unique relational constraints.
*   **Compliance Workflows:** Dynamic SoA generation based directly on risk mapping.
*   **Collaboration:** Single-user (Limitation).
*   **Integrations:** None (Limitation / Scope boundary).
*   **Reporting:** Automated, one-click professional PDF and Excel exports.
*   **Positioning:** A lightweight, highly transparent, locally deployable prototype focused strictly on the core risk-to-control workflow. It serves as an educational bridge between error-prone spreadsheets and overly complex enterprise SaaS.
