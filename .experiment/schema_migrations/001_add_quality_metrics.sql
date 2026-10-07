CREATE TABLE IF NOT EXISTS quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    task_id TEXT NOT NULL,
    accuracy REAL,
    first_pass INTEGER,
    revision_count INTEGER,
    complexity_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES runs(session_id)
);
