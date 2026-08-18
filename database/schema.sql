CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    description TEXT,
    owner TEXT,
    criticality TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    risk_title TEXT NOT NULL,
    threat TEXT,
    vulnerability TEXT,
    existing_controls TEXT,
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    impact INTEGER NOT NULL CHECK (impact BETWEEN 1 AND 5),
    risk_score INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    risk_owner TEXT,
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS iso_controls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    control_id TEXT NOT NULL UNIQUE,
    control_name TEXT NOT NULL,
    control_category TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS risk_control_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    risk_id INTEGER NOT NULL,
    control_id TEXT NOT NULL,
    applicability TEXT,
    justification TEXT,
    implementation_status TEXT,
    implementation_notes TEXT,
    FOREIGN KEY (risk_id) REFERENCES risks(id) ON DELETE CASCADE,
    FOREIGN KEY (control_id) REFERENCES iso_controls(control_id) ON DELETE CASCADE
);

-- Ensure a risk can only be mapped to a specific control once
CREATE UNIQUE INDEX IF NOT EXISTS idx_risk_control_mapping ON risk_control_mapping(risk_id, control_id);

CREATE TABLE IF NOT EXISTS risk_treatments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    risk_id INTEGER NOT NULL,
    treatment_option TEXT NOT NULL,
    treatment_description TEXT,
    treatment_owner TEXT,
    target_date DATE,
    treatment_status TEXT,
    residual_likelihood INTEGER CHECK (residual_likelihood BETWEEN 1 AND 5),
    residual_impact INTEGER CHECK (residual_impact BETWEEN 1 AND 5),
    residual_score INTEGER,
    residual_risk_level TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (risk_id) REFERENCES risks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    action TEXT NOT NULL,
    module TEXT,
    record_type TEXT,
    record_id TEXT,
    description TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
