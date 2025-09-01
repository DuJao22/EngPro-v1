-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    subscription_plan TEXT DEFAULT 'free_trial',
    trial_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trial_end_date TIMESTAMP,
    subscription_status TEXT DEFAULT 'trial',
    subscription_start_date TIMESTAMP,
    subscription_end_date TIMESTAMP,
    mercadopago_customer_id TEXT UNIQUE,
    mercadopago_subscription_id TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    start_date DATE,
    end_date DATE,
    budget REAL DEFAULT 0,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    project_id INTEGER,
    due_date DATE,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    assigned_to TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Budget items table
CREATE TABLE IF NOT EXISTS budget_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    category TEXT NOT NULL,
    description TEXT,
    quantity REAL DEFAULT 1,
    unit_cost REAL NOT NULL,
    total_cost REAL NOT NULL,
    supplier_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
);

-- Permits/Licenses table
CREATE TABLE IF NOT EXISTS permits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    name TEXT NOT NULL,
    type TEXT,
    status TEXT DEFAULT 'pending',
    issue_date DATE,
    expiry_date DATE,
    issuing_authority TEXT,
    document_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Safety incidents table
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT DEFAULT 'low',
    date_occurred DATE,
    location TEXT,
    reported_by TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Notes table
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cnpj_id TEXT UNIQUE,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    category TEXT,
    rating REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purchase orders table
CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    supplier_id INTEGER,
    order_number TEXT UNIQUE,
    status TEXT DEFAULT 'pending',
    order_date DATE,
    expected_delivery DATE,
    total_amount REAL,
    items TEXT, -- JSON string for order items
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
);

-- Workers table
CREATE TABLE IF NOT EXISTS workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT,
    email TEXT,
    phone TEXT,
    hire_date DATE,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training courses table
CREATE TABLE IF NOT EXISTS trainings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    duration_hours INTEGER,
    validity_months INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Worker training relationships (many-to-many)
CREATE TABLE IF NOT EXISTS worker_trainings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER,
    training_id INTEGER,
    completion_date DATE,
    expiry_date DATE,
    certificate_path TEXT,
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers (id),
    FOREIGN KEY (training_id) REFERENCES trainings (id)
);

-- Materials table for sustainability tracking
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    unit TEXT,
    carbon_emissions_per_unit REAL DEFAULT 0, -- kg CO2 per unit
    cost_per_unit REAL DEFAULT 0,
    supplier_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
);

-- Material usage logs
CREATE TABLE IF NOT EXISTS material_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    material_id INTEGER,
    quantity REAL NOT NULL,
    date_used DATE,
    total_emissions REAL, -- calculated field
    total_cost REAL, -- calculated field
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id),
    FOREIGN KEY (material_id) REFERENCES materials (id)
);

-- Risk management table
CREATE TABLE IF NOT EXISTS risks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    probability INTEGER DEFAULT 1, -- 1-5 scale
    impact INTEGER DEFAULT 1, -- 1-5 scale
    risk_score INTEGER, -- probability * impact
    responsible_person TEXT,
    mitigation_plan TEXT,
    status TEXT DEFAULT 'identified',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Compliance documents table
CREATE TABLE IF NOT EXISTS compliance_docs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    title TEXT NOT NULL,
    document_type TEXT,
    file_path TEXT,
    status TEXT DEFAULT 'pending',
    issue_date DATE,
    expiry_date DATE,
    responsible_authority TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Field measurements from IoT/drones
CREATE TABLE IF NOT EXISTS field_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    measurement_type TEXT,
    value REAL,
    unit TEXT,
    location TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_id TEXT,
    notes TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Audit log for tracking changes
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER,
    action TEXT NOT NULL, -- INSERT, UPDATE, DELETE
    old_values TEXT, -- JSON string
    new_values TEXT, -- JSON string
    user_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert default admin user (password: admin123)
INSERT OR IGNORE INTO users (username, email, password_hash) 
VALUES ('admin', 'admin@civilsaas.com', 'scrypt:32768:8:1$h3KGT9NSAqQmSBYI$e8c1463526cae2e6c7d9882c34d6480f58cab82c6b54733d98b3b29464819f5cd6ae9272f2cada4c531b6827f5b584c4af18fb72a42c97b0feb46f2cd1df33a8');
