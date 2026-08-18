# MASTER DOCUMENTATION SPECIFICATION
## Comprehensive Academic & Technical Project Documentation

**Project Title:** Risk Assessment Framework Mapped to ISO/IEC 27001  
**Project ID:** ZYNVEX-CERT-0666  
**Student:** Areeb Amjad Khan  
**Status:** Feature-Frozen / Documentation Phase  
**Target Length:** 40–60 pages  

---

### 1. ROLE AND OBJECTIVE
This specification serves as the absolute blueprint for generating a comprehensive academic and technical report suitable for university final-year project submission, technical review, and professional cybersecurity portfolio presentation. 

### 2. CRITICAL EVIDENCE-FIRST RULE
The report is grounded entirely in the actual source code and implementation artifacts. The application natively supports:
- **Core Workflow:** Asset Management, Risk Registration, ISO/IEC 27001 Control Mapping, Statement of Applicability (SoA) generation, Risk Treatment, and Residual Risk calculation.
- **Reporting:** Live Plotly dashboards, dynamic ReportLab PDF exports, and openpyxl Excel exports.
- **Backend:** A local SQLite database utilizing parameterized SQL and explicitly enforced foreign key constraints.

### 3. CLAIM CLASSIFICATION POLICY
All claims in the final report must be strictly classified:
- **CATEGORY A (Implemented Fact):** Proven by the source code (e.g., "Risk is calculated as Likelihood × Impact").
- **CATEGORY B (Research/Standard-Backed Fact):** Supported by authoritative literature (e.g., "ISO/IEC 27001 defines requirements for an ISMS").
- **CATEGORY C (Limitation):** Explicitly identifying capabilities not present (e.g., "No RBAC or multi-user architecture").
- **CATEGORY D (Future Work):** Clearly labeled proposed functionality (e.g., "PostgreSQL migration, AI-assisted risk identification").

### 4. RESEARCH & SOURCING REQUIREMENTS
- **Authoritative Sources:** Priority given to official ISO/IEC standards (27001, 27005), NIST frameworks, peer-reviewed academic literature, and official technology documentation.
- **Citation Style:** IEEE-style numbered in-text citations (e.g., [1], [2]).
- **Honesty:** No fabricated sources, papers, or DOIs. The research approach combines literature review, standards analysis, software design, and testing validation.

---

## REQUIRED REPORT STRUCTURE (40–60 Pages)

### PRELIMINARY PAGES
1. **Title Page** (Title, ID, Student, placeholders for University/Supervisor)
2. **Declaration of Originality**
3. **Approval / Certification Placeholder**
4. **Acknowledgement**
5. **Abstract** (200-300 words covering Problem, Motivation, Solution, Methodology, Results, Limitations)
6. **Table of Contents, List of Figures, List of Tables, List of Abbreviations** (GRC, ISMS, ISO, NIST, SoA, etc.)

---

### CHAPTER 1 — INTRODUCTION
1.1 Background
1.2 Information Security Risk
1.3 Cybersecurity Governance, Risk and Compliance
1.4 Importance of Risk Assessment
1.5 Challenges in Manual Risk Management
1.6 Problem Context
1.7 Problem Statement
1.8 Motivation
1.9 Project Aim
1.10 Project Objectives
1.11 Research Questions
1.12 Project Scope
1.13 Project Contributions
1.14 Organization of the Report

---

### CHAPTER 2 — BACKGROUND AND LITERATURE REVIEW
*(Heavily researched, differentiating theoretical concepts from implementation)*
2.1 Information Security Risk Management
2.2 Assets
2.3 Threats & 2.4 Vulnerabilities
2.5 Risk & 2.6 Likelihood & 2.7 Impact
2.8 Risk Scoring Models
2.9 Inherent Risk & 2.10 Residual Risk
2.11 Risk Treatment (Mitigate, Accept, Transfer, Avoid)
2.12 GRC & 2.13 ISMS
2.14 ISO/IEC 27001 & 2.15 ISO/IEC 27005
2.16 Statement of Applicability
2.17 NIST Cybersecurity Framework 2.0 & 2.18 NIST Risk Management Framework
2.19 Risk Automation & 2.20 Spreadsheet-Based Risk Management
2.21 Research Gap & 2.22 Chapter Summary

---

### CHAPTER 3 — EXISTING SOLUTIONS AND COMPARATIVE ANALYSIS
*(Academic, unsupported claims excluded. Framework positioned as a transparent educational/practical prototype)*
3.1 Introduction
3.2 Manual Spreadsheet-Based Risk Assessment
3.3 Commercial GRC Platforms (General comparison)
3.4 Microsoft/Enterprise GRC Solutions
3.5 ServiceNow GRC
3.6 ISO-Based Manual Assessment Approaches
3.7 NIST-Based Risk Management Approaches
3.8 Comparison Criteria (Cost, Deployment, Reporting, etc.)
3.9 Comparative Feature Matrix (Table placeholder)
3.10 Strengths of Existing Approaches
3.11 Limitations/Gaps Relevant to This Project
3.12 Positioning of the Proposed Framework
3.13 Comparative Analysis Discussion & 3.14 Chapter Summary

---

### CHAPTER 4 — PROBLEM AND PROPOSED SOLUTION
4.1 Existing Problem
4.2 Proposed Solution & 4.3 System Goals
4.4 Target Users & 4.5 Scope
4.6 Core Workflow (Asset → Threat → Vuln → Likelihood/Impact → Inherent Risk → ISO Mapping → SoA → Risk Treatment → Residual Risk → Reporting)
4.7 System Benefits
4.8 Assumptions, 4.9 Constraints & 4.10 Boundaries

---

### CHAPTER 5 — REQUIREMENTS ANALYSIS
5.1 Functional Requirements (FR-01 to FR-14 Table placeholder)
5.2 Non-Functional Requirements (Usability, Local Execution, etc. Table placeholder)
5.3 User Roles / Intended User Model
5.4 Use Cases & 5.5 Use Case Descriptions (Table placeholder)
5.6 Data Requirements & 5.7 Security Requirements
5.8 Reporting Requirements & 5.9 Usability Requirements
5.10 Constraints

---

### CHAPTER 6 — SYSTEM DESIGN AND ARCHITECTURE
6.1 Architectural Overview & 6.2 Technology Stack
6.3 Application Architecture
6.4 Presentation Layer (Streamlit)
6.5 Application/Business Logic (Modules)
6.6 Database Layer (SQLite)
6.7 Reporting Layer (ReportLab, openpyxl)
6.8 Utility Layer
6.9 Data Flow (Figure: Application Data Flow)
6.10 Database Architecture
6.11 Entity Relationships (Figure: ER Diagram for assets, risks, iso_controls, mapping, treatments)
6.12 Module Relationships
6.13 Security Considerations (Parameterized SQL, unique mapping constraints)
6.14 Deployment Architecture & 6.15 Local Deployment Model
*(Figures: High-Level Architecture, Data Flow, ER Diagram)*

---

### CHAPTER 7 — RISK ASSESSMENT METHODOLOGY
7.1 Risk Assessment Concept
7.2 Asset Identification
7.3 Threat Identification & 7.4 Vulnerability Identification
7.5 Likelihood (1-5) & 7.6 Impact (1-5)
7.7 Risk Score (Likelihood × Impact)
7.8 Risk Classification (1-4 Low, 5-9 Medium, 10-16 High, 17-25 Critical)
7.9 5×5 Matrix (Figure & Table placeholder)
7.10 Inherent Risk & 7.11 Risk Prioritization
7.12 Example Calculation

---

### CHAPTER 8 — ISO/IEC 27001 INTEGRATION
8.1 ISO/IEC 27001 Overview & 8.2 Annex A
8.3 ISO/IEC 27001:2022 Control Structure & 8.4 Four Control Themes
8.5 Control Library in the Application (93 controls total)
8.6 Risk-to-Control Mapping
8.7 Applicability & 8.8 Justification & 8.9 Implementation Status
8.10 Statement of Applicability
8.11 Relationship Between Risk and Controls
8.12 Limitations of the Mapping
8.13 Certification Disclaimer (Application aligns with ISO concepts but does not grant certification).

---

### CHAPTER 9 — SYSTEM IMPLEMENTATION
9.1 Development Environment
9.2 Python Backend & 9.3 Streamlit Interface
9.4 SQLite Database
9.5 Plotly Visualizations
9.6 PDF Generation & 9.7 Excel Generation
9.8 Database Operations & 9.9 Validation
9.10 Error Handling (e.g., `sqlite3.IntegrityError`)
9.11 Session State & 9.12 Auto Reload Configuration

---

### CHAPTER 10 — APPLICATION MODULES
*(Detailed Purpose, Inputs, Processing, Outputs, User Workflow, Validation, and Screenshots per module)*
10.1 Dashboard
10.2 Asset Management
10.3 Risk Register
10.4 ISO 27001 Controls
10.5 Risk-Control Mapping
10.6 Statement of Applicability
10.7 Risk Treatment
10.8 Reports
10.9 About / Methodology

---

### CHAPTER 11 — TESTING AND VALIDATION
11.1 Testing Strategy
11.2 Unit/Logic Testing & 11.3 Database Integrity Testing
11.4 Integration Testing & 11.5 Report Generation Testing
11.6 Security-Oriented Code Checks
11.7 Automated QA (Passed all defined checks)
11.8 Manual Acceptance Testing
11.9 Test Cases & 11.10 Test Results (15/15 tests passed)
11.11 Defect Handling & 11.12 Final Validation

---

### CHAPTER 12 — RESULTS AND DISCUSSION
12.1 System Implementation Results
12.2 Risk Assessment Results
12.3 Dashboard Results
12.4 ISO Mapping Results
12.5 SoA Results
12.6 Treatment Results
12.7 Residual Risk Results
12.8 Reporting Results
12.9 Usability Observations
12.10 Comparison With Initial Objectives (Table: Objective vs Evidence)
12.11 Discussion & 12.12 Overall Outcome

---

### CHAPTER 13 — LIMITATIONS
13.1 Local SQLite Architecture
13.2 Single-user Orientation
13.3 No Authentication & 13.4 No RBAC
13.5 No Multi-Tenant Architecture & 13.6 No Cloud Deployment
13.7 No Automated Threat Intelligence & 13.8 No Vulnerability Scanner Integration
13.9 No SIEM Integration & 13.10 No External API Integration
13.11 Manual Risk Input
13.12 Simplified Risk Scoring
13.13 No Advanced Statistical Risk Modeling
13.14 No Full Enterprise Audit Trail
13.15 ISO Certification Limitation

---

### CHAPTER 14 — FUTURE DEVELOPMENT AND PRODUCT ROADMAP
*(All labeled clearly as FUTURE PROPOSED capabilities)*
- **Phase 1: Current Prototype** (Streamlit, SQLite, Dashboard, Reports)
- **Phase 2: Enterprise Readiness** (PostgreSQL, Authentication, RBAC, Audit Logging)
- **Phase 3: Multi-Framework GRC** (NIST CSF 2.0, NIST RMF, CIS, SOC 2, cross-framework mapping)
- **Phase 4: Security Tool Integration** (SIEM, vulnerability scanners, asset discovery)
- **Phase 5: Intelligent GRC** (AI-assisted risk identification and treatment recommendations)
- **Phase 6: Product / SaaS Evolution** (SaaS deployment, APIs, continuous monitoring)

---

### CHAPTER 15 — CONCLUSION
Summary of the original problem, proposed Streamlit/SQLite solution, methodology alignment, 15/15 manual testing results, project contribution, honest limitations, and the future roadmap vision.

---

### FIGURE AND TABLE INVENTORY
- **Figures Planned:** 1. System Architecture, 2. Application Flow, 3. ER Diagram, 4. Risk Workflow, 5. 5×5 Matrix, 6. Mapping Workflow, 7. SoA Workflow, 8. Treatment Workflow, 9-19. Screenshots of UI Modules (Dashboard through Reports).
- **Tables Planned:** 1. Tech Stack, 2. Functional Reqs, 3. Non-Functional Reqs, 4. Use Cases, 5. Classification Bounds, 6. Control Themes, 7. DB Tables, 8. Existing Solutions Comparison, 9. Traceability, 10. Test Cases, 11. Test Results, 12. Objective vs Evidence, 13. Limitations, 14. Roadmap.
