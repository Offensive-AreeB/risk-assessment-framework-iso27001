from database.db import execute_query
from data.iso_27001_2022_controls import ISO_27001_2022_CONTROLS

def seed_database():
    # 1. Seed ISO Controls (Idempotent)
    existing_controls = execute_query("SELECT count(*) as count FROM iso_controls", fetch_one=True)
    if existing_controls and existing_controls['count'] == 0:
        for ctrl in ISO_27001_2022_CONTROLS:
            execute_query(
                "INSERT INTO iso_controls (control_id, control_name, control_category, description) VALUES (?, ?, ?, ?)",
                (ctrl['id'], ctrl['name'], ctrl['theme'], ctrl['desc'])
            )

    # Check if we already have assets
    existing_assets = execute_query("SELECT count(*) as count FROM assets", fetch_one=True)
    if existing_assets and existing_assets['count'] == 0:
        # Seed Assets
        assets = [
            ("Customer Database", "Database", "Primary database storing all customer PII", "DBA Team", "Critical"),
            ("Web Application", "Application", "Customer facing web portal", "Dev Team", "High"),
            ("Employee Laptops", "Hardware", "Company issued laptops for staff", "IT Support", "Medium"),
            ("Internal Network", "Network", "Corporate LAN and WiFi", "Network Admin", "High"),
            ("Backup Server", "Hardware", "On-premise backup storage", "Storage Team", "High")
        ]
        
        for name, a_type, desc, owner, crit in assets:
            execute_query(
                "INSERT INTO assets (asset_name, asset_type, description, owner, criticality) VALUES (?, ?, ?, ?, ?)",
                (name, a_type, desc, owner, crit)
            )
            
        # Get asset IDs
        db_assets = execute_query("SELECT id, asset_name FROM assets", fetch_all=True)
        asset_map = {row['asset_name']: row['id'] for row in db_assets}
        
        # Seed Risks
        risks = [
            (asset_map["Customer Database"], "Unauthorized Access to Customer Database", "Credential Theft", "Insufficient Access Controls", "Basic password policy", 4, 5, 20, "Critical", "DBA Lead", "Open"),
            (asset_map["Customer Database"], "SQL Injection", "Malicious Actor", "Lack of input sanitization", "WAF", 3, 5, 15, "High", "DevSecOps", "Under Treatment"),
            (asset_map["Web Application"], "Web Application Exploitation", "Automated Scanners", "Unpatched software", "Monthly patching", 4, 4, 16, "High", "Dev Team", "Open"),
            (asset_map["Employee Laptops"], "Malware Infection", "Phishing Emails", "Lack of endpoint protection", "Windows Defender", 3, 3, 9, "Medium", "IT Support", "Open"),
            (asset_map["Internal Network"], "Unauthorized Network Access", "Insider Threat", "Open network ports", "VLAN segregation", 2, 4, 8, "Medium", "Network Admin", "Open"),
            (asset_map["Backup Server"], "Backup Data Theft", "Physical Intrusion", "Lack of encryption at rest", "Locked server room", 2, 5, 10, "High", "Storage Team", "Accepted")
        ]
        
        for r in risks:
            execute_query(
                """INSERT INTO risks 
                   (asset_id, risk_title, threat, vulnerability, existing_controls, 
                    likelihood, impact, risk_score, risk_level, risk_owner, status) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                r
            )
            
    # Seed Demo Mappings
    existing_maps = execute_query("SELECT count(*) as count FROM risk_control_mapping", fetch_one=True)
    if existing_maps and existing_maps['count'] == 0:
        db_risks = execute_query("SELECT id, risk_title FROM risks", fetch_all=True)
        risk_map = {row['risk_title']: row['id'] for row in db_risks}
        
        mappings = [
            # Customer Database: Unauthorized Access
            (risk_map.get("Unauthorized Access to Customer Database"), "5.15", "Applicable", "DB needs strict access control.", "Partially Implemented", "Role-based access partially done."),
            (risk_map.get("Unauthorized Access to Customer Database"), "5.16", "Applicable", "Identity lifecycle must be managed.", "Implemented", "Active Directory integration."),
            (risk_map.get("Unauthorized Access to Customer Database"), "8.5", "Applicable", "Secure authentication needed for DB connections.", "Planned", "MFA to be rolled out."),
            
            # Web Application: Web Application Exploitation
            (risk_map.get("Web Application Exploitation"), "8.25", "Applicable", "SDLC must incorporate security.", "Partially Implemented", "Basic testing in place."),
            (risk_map.get("Web Application Exploitation"), "8.26", "Applicable", "App security requirements defined.", "Implemented", "OWASP Top 10 considered."),
            (risk_map.get("Web Application Exploitation"), "8.8", "Applicable", "Need vulnerability management for web apps.", "Implemented", "Weekly vulnerability scans."),
            
            # Employee Laptops: Malware Infection
            (risk_map.get("Malware Infection"), "8.7", "Applicable", "Malware protection for endpoints.", "Implemented", "Next-gen AV deployed."),
            (risk_map.get("Malware Infection"), "8.1", "Applicable", "User endpoint device protection.", "Implemented", "MDM deployed."),
            (risk_map.get("Malware Infection"), "6.3", "Applicable", "Awareness training for phishing.", "Planned", "Annual training next month."),
            
            # Backup Server: Backup Data Theft
            (risk_map.get("Backup Data Theft"), "8.13", "Applicable", "Information backup is critical.", "Implemented", "Daily backups to encrypted drives."),
            (risk_map.get("Backup Data Theft"), "7.1", "Applicable", "Physical perimeter for server room.", "Implemented", "Keycard access only."),
        ]
        
        for m in mappings:
            # check if risk was found (just in case)
            if m[0] is not None:
                try:
                    execute_query(
                        """INSERT INTO risk_control_mapping 
                           (risk_id, control_id, applicability, justification, implementation_status, implementation_notes)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        m
                    )
                except Exception:
                    pass # Ignore duplicates if re-running
                
    # Seed Demo Treatments
    existing_treats = execute_query("SELECT count(*) as count FROM risk_treatments", fetch_one=True)
    if existing_treats and existing_treats['count'] == 0:
        db_risks = execute_query("SELECT id, risk_title FROM risks", fetch_all=True)
        risk_map = {row['risk_title']: row['id'] for row in db_risks}
        treatments = [
            # Customer Database: Unauthorized Access (Inherent: 4x5=20)
            (risk_map.get("Unauthorized Access to Customer Database"), "Mitigate", "Implement MFA, RBAC, privileged access review, and quarterly access recertification.", "IT Security Team", "2026-09-30", "In Progress", 2, 5, 10, "High"),
            
            # SQL Injection (Inherent: 3x5=15)
            (risk_map.get("SQL Injection"), "Mitigate", "Implement parameterized queries, input validation, secure code review, and regular application security testing.", "DevSecOps", "2026-10-15", "Planned", 1, 5, 5, "Medium"),
            
            # Malware Infection (Inherent: 3x3=9)
            (risk_map.get("Malware Infection"), "Mitigate", "Deploy endpoint protection, email filtering, patch management, and security awareness training.", "IT Support", "2025-01-01", "Implemented", 1, 3, 3, "Low"),
            
            # Backup Data Theft (Inherent: 2x5=10)
            (risk_map.get("Backup Data Theft"), "Mitigate", "Encrypt backups, restrict backup access, and implement secure offline/immutable backup storage.", "Storage Team", "2026-12-01", "Planned", 1, 5, 5, "Medium"),
            
            # Unauthorized Network Access (Inherent: 2x4=8)
            (risk_map.get("Unauthorized Network Access"), "Accept", "Current VLAN segregation is sufficient given the cost of network overhaul.", "Network Admin", "2026-01-01", "Accepted", 2, 4, 8, "Medium")
        ]
        
        for t in treatments:
            if t[0] is not None:
                execute_query(
                    """INSERT INTO risk_treatments 
                       (risk_id, treatment_option, treatment_description, treatment_owner, target_date, treatment_status, residual_likelihood, residual_impact, residual_score, residual_risk_level)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    t
                )
