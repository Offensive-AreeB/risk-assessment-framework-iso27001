# FUTURE PRODUCT RESEARCH
**Project:** Risk Assessment Framework Mapped to ISO/IEC 27001 (ZYNVEX-CERT-0666)

*Note: All items below represent PROPOSED FUTURE enhancements for Chapter 14. None of these exist in the current implementation.*

### Phase 2: Enterprise Readiness
*   **PostgreSQL Migration:** 
    *   *Why:* SQLite locks the entire database on writes, preventing concurrent multi-user usage. PostgreSQL provides row-level locking.
    *   *Challenge:* Requires setting up a database server and utilizing SQLAlchemy or a similar ORM to manage complex migrations.
*   **Authentication & RBAC:**
    *   *Why:* Necessary to differentiate between 'Administrators' (managing frameworks) and 'Analysts' (logging risks).
    *   *Security Implication:* Requires secure session management, password hashing (e.g., bcrypt), and JWT/OAuth2.

### Phase 3: Multi-Framework GRC
*   **NIST CSF 2.0 & SOC 2:**
    *   *Why:* Organizations rarely adhere to just one standard.
    *   *Approach:* Abstract the `iso_controls` table into a generic `framework_controls` table and build a many-to-many crosswalk table to map ISO controls to NIST equivalents.

### Phase 4: Security Tool Integration
*   **Vulnerability Scanners (e.g., Nessus, Qualys):**
    *   *Why:* Manual vulnerability identification is subjective. Ingesting CVEs automates technical risk registration.
    *   *Technical:* Requires building REST API endpoints to consume JSON payloads from scanners.

### Phase 5: Intelligent GRC
*   **AI-Assisted Treatment Recommendations:**
    *   *Why:* Helps junior analysts determine the best mitigation strategy based on historical organizational data.
    *   *Approach:* Integrating an LLM API to analyze the "Threat" and "Vulnerability" fields and suggest Annex A controls.

### Phase 6: Product / SaaS Evolution
*   **Multi-Tenancy:**
    *   *Why:* To offer the software as a B2B SaaS platform.
    *   *Challenge:* Requires complete architectural redesign for logical data separation (Tenant IDs on every row) or physical separation (database-per-tenant), significantly increasing complexity.
