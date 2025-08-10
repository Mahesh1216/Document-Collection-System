DROP TABLE IF EXISTS processes;
DROP TABLE IF EXISTS document_types;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS process_assignments;
DROP TABLE IF EXISTS document_submissions;
DROP TABLE IF EXISTS process_document_requirements;

-- Main Tables
CREATE TABLE IF NOT EXISTS processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    required_fields TEXT, -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS process_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    process_id INTEGER,
    assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',
    completion_percentage REAL DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers (id),
    FOREIGN KEY (process_id) REFERENCES processes (id)
);

CREATE TABLE IF NOT EXISTS document_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    process_id INTEGER,
    document_type_id INTEGER,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_url TEXT,
    ocr_extracted_data TEXT, -- JSON
    validation_status TEXT DEFAULT 'pending',
    FOREIGN KEY (customer_id) REFERENCES customers (id),
    FOREIGN KEY (process_id) REFERENCES processes (id),
    FOREIGN KEY (document_type_id) REFERENCES document_types (id)
);

-- Junction Table
CREATE TABLE IF NOT EXISTS process_document_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER,
    document_type_id INTEGER,
    is_mandatory BOOLEAN DEFAULT 1,
    FOREIGN KEY (process_id) REFERENCES processes (id),
    FOREIGN KEY (document_type_id) REFERENCES document_types (id)
);