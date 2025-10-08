import sqlite3
from flask import g, current_app

def get_db_conn():
    if "db_conn" not in g:
        g.db_conn = sqlite3.connect(
            current_app.config.get("DATABASE", "placement.db"),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db_conn.row_factory = sqlite3.Row
    return g.db_conn

def close_db(e=None):
    db = g.pop("db_conn", None)
    if db is not None:
        db.close()

def init_db():
    """
    Create required tables and add missing columns if needed.
    Seed sample placements if empty.
    """
    db = get_db_conn()
    cur = db.cursor()
        # --- Add missing columns to users if needed ---
    cur.execute("PRAGMA table_info(users)")
    user_columns = [row["name"] for row in cur.fetchall()]
    if "phone" not in user_columns:
        cur.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    if "skills" not in user_columns:
        cur.execute("ALTER TABLE users ADD COLUMN skills TEXT")
    if "profile_pic" not in user_columns:
        cur.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
    if "resume" not in user_columns:
        cur.execute("ALTER TABLE users ADD COLUMN resume TEXT")

    # Create tables if not exist
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('student','admin')) NOT NULL DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS placements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        role TEXT NOT NULL,
        location TEXT NOT NULL,
        description TEXT,
        link TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        storage_path TEXT,
        verdict TEXT,
        details TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        placement_id INTEGER NOT NULL,
        status TEXT CHECK(status IN ('Applied','Shortlisted','Selected','Rejected')) NOT NULL DEFAULT 'Applied',
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(placement_id) REFERENCES placements(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        quiz_name TEXT,
        category TEXT,
        score INTEGER,
        total INTEGER,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # --- Add missing columns to placements if needed ---
    cur.execute("PRAGMA table_info(placements)")
    existing_columns = [row["name"] for row in cur.fetchall()]
    if "eligibility" not in existing_columns:
        cur.execute("ALTER TABLE placements ADD COLUMN eligibility TEXT")
    if "deadline" not in existing_columns:
        cur.execute("ALTER TABLE placements ADD COLUMN deadline TEXT")

    # Seed sample placements if empty
    cur.execute("SELECT COUNT(*) AS cnt FROM placements")
    row = cur.fetchone()
    cnt = row[0] if row else 0
    if cnt == 0:
        cur.executescript("""
        INSERT INTO placements (company, role, location, description, link, eligibility, deadline) VALUES
        ('Google', 'Software Engineer', 'Bangalore', 'Work on scalable systems', 'https://careers.google.com', 'B.Tech/B.E in CS', '2025-12-31'),
        ('TCS', 'System Analyst', 'Mumbai', 'Client projects and solutions', 'https://www.tcs.com', 'Any Graduate', '2025-12-31'),
        ('Infosys', 'Java Developer', 'Hyderabad', 'Backend application development', 'https://www.infosys.com', 'B.Tech/B.E in IT', '2025-12-31');
        """)

    db.commit()

