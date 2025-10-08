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

    # --- Create tables if not exist ---
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

    # --- Add missing columns to users ---
    cur.execute("PRAGMA table_info(users)")
    existing_columns = [row["name"] for row in cur.fetchall()]
    if "phone" not in existing_columns:
        cur.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    if "skills" not in existing_columns:
        cur.execute("ALTER TABLE users ADD COLUMN skills TEXT")
    if "profile_pic" not in existing_columns:
        cur.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
    if "resume" not in existing_columns:
        cur.execute("ALTER TABLE users ADD COLUMN resume TEXT")

    # --- Add missing columns to placements ---
    cur.execute("PRAGMA table_info(placements)")
    existing_columns = [row["name"] for row in cur.fetchall()]
    if "eligibility" not in existing_columns:
        cur.execute("ALTER TABLE placements ADD COLUMN eligibility TEXT")
    if "deadline" not in existing_columns:
        cur.execute("ALTER TABLE placements ADD COLUMN deadline TEXT")

    # --- Seed sample placements ---
    cur.execute("SELECT COUNT(*) AS cnt FROM placements")
    row = cur.fetchone()
    cnt = row[0] if row else 0
    if cnt == 0:
        cur.executescript("""
        INSERT INTO placements (company, role, location, description, link, eligibility, deadline) VALUES
        ('Google', 'Software Engineer', 'Bangalore', 'Work on scalable systems and new features for global products.', 'https://careers.google.com', 'B.Tech/B.E in CS', '2025-12-31'),
        ('TCS', 'System Analyst', 'Mumbai', 'Client projects and solutions in business systems.', 'https://www.tcs.com', 'Any Graduate', '2025-12-31'),
        ('Infosys', 'Java Developer', 'Hyderabad', 'Backend application development for enterprise clients.', 'https://www.infosys.com', 'B.Tech/B.E in IT', '2025-12-31'),
        ('Amazon', 'Data Engineer', 'Chennai', 'Build and optimize data pipelines and analytics systems.', 'https://www.amazon.jobs', 'B.Tech/B.E in CS or Data Science', '2025-11-30'),
        ('Microsoft', 'Cloud Support Engineer', 'Pune', 'Support Azure customers with cloud deployments and troubleshooting.', 'https://careers.microsoft.com', 'B.Tech/B.E in CS/IT/ECE', '2025-12-15'),
        ('Wipro', 'Cybersecurity Analyst', 'Noida', 'Monitor and protect enterprise infrastructure against threats.', 'https://careers.wipro.com', 'B.Tech/B.E in CS/IT', '2025-12-20'),
        ('Accenture', 'AI Research Intern', 'Gurgaon', 'Work on AI-driven automation and NLP models.', 'https://www.accenture.com', 'B.Tech/B.E/M.Tech in CS or AI', '2025-11-25'),
        ('IBM', 'Software Developer', 'Pune', 'Develop and maintain enterprise-grade software solutions.', 'https://www.ibm.com/careers', 'B.Tech/B.E in CS/IT', '2025-12-10'),
        ('Deloitte', 'Business Technology Analyst', 'Bangalore', 'Support consulting projects using data analytics and business tech.', 'https://www.deloitte.com', 'B.Tech/B.E/MBA', '2025-12-05'),
        ('Capgemini', 'DevOps Engineer', 'Kolkata', 'Automate deployments and CI/CD pipelines using modern tools.', 'https://www.capgemini.com', 'B.Tech/B.E in CS/IT', '2025-12-25'),
        ('Flipkart', 'Frontend Developer', 'Bangalore', 'Design responsive UI for e-commerce platform using React and JS.', 'https://www.flipkartcareers.com', 'B.Tech/B.E in CS/IT', '2025-12-18'),
        ('Adobe', 'UX Designer Intern', 'Noida', 'Design intuitive user experiences and prototypes for creative tools.', 'https://adobe.wd5.myworkdayjobs.com', 'B.Des/B.Tech with UI/UX experience', '2025-12-28'),
        ('Swiggy', 'Backend Developer', 'Bangalore', 'Work on order management and delivery optimization systems.', 'https://careers.swiggy.com', 'B.Tech/B.E in CS/IT', '2025-11-29'),
        ('Paytm', 'Mobile App Developer', 'Noida', 'Develop new features for the Paytm app ecosystem.', 'https://paytm.com/careers', 'B.Tech/B.E in CS/IT', '2025-12-22'),
        ('ISRO', 'Research Scientist', 'Ahmedabad', 'Work on satellite systems and data analysis.', 'https://www.isro.gov.in', 'M.Sc/M.Tech in Physics, CS, or Electronics', '2025-12-31'),
        ('Zomato', 'Machine Learning Engineer', 'Gurgaon', 'Build recommendation and delivery optimization algorithms.', 'https://www.zomato.com/careers', 'B.Tech/B.E in CS or Data Science', '2025-12-12');
        """)

    db.commit()
