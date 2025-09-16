import sqlite3

DB_NAME = "placement.db"

schema = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat logs for chatbot
CREATE TABLE IF NOT EXISTS chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    sender TEXT CHECK(sender IN ('student','admin','bot')),
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Practice questions
CREATE TABLE IF NOT EXISTS practice_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    type TEXT,
    q TEXT,
    options TEXT,
    answer TEXT
);

-- Practice attempts
CREATE TABLE IF NOT EXISTS practice_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    question_id INTEGER,
    given_answer TEXT,
    correct INTEGER,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES practice_questions(id)
);

-- Resume uploads
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    filename TEXT,
    score INTEGER,
    feedback TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- Ratings
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    rating INTEGER CHECK(rating >=1 AND rating <=5),
    description TEXT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.executescript(schema)
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully with all required tables!")

if __name__ == "__main__":
    init_db()
