import os
from flask import Flask, render_template
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# Import blueprint init and db helpers
from enhancements import init_app as init_enhancements
from enhancements.db import close_db, init_db


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # ---------------- Config ----------------
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["DATABASE"] = os.environ.get("DATABASE", "placement.db")
    app.config["RESUME_UPLOAD_FOLDER"] = os.environ.get(
        "RESUME_UPLOAD_FOLDER", "uploads/resumes"
    )
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB limit


    # Ensure upload folder exists
    os.makedirs(app.config["RESUME_UPLOAD_FOLDER"], exist_ok=True)

    # ---------------- Blueprints ----------------
    init_enhancements(app)
    print("✅ Enhancements blueprint registered.")

    # ---------------- Database ----------------
    with app.app_context():
        print(f"👉 Using database file: {app.config['DATABASE']}")  # Debug helper
        init_db()
        print("✅ Database initialized.")

    # Ensure db is closed after each request
    app.teardown_appcontext(close_db)

    # ---------------- Routes ----------------
    @app.route("/")
    def index():
        return render_template("home.html")

    return app

app = create_app()
if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )

