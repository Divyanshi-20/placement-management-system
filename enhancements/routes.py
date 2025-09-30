# enhancements/routes.py
import os
import json
import sqlite3
from datetime import datetime
from openai import OpenAI 
import httpx

from flask import (
    Blueprint, request, jsonify, render_template,
    redirect, url_for, session, flash, current_app, send_from_directory
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from .api_jobs import fetch_api_jobs
from .resume_checker import analyze_resume
from .db import get_db_conn  # ✅ central db helpers
 

http_client = httpx.Client(proxies="http://your-proxy:port")
client = OpenAI(api_key="...", http_client=http_client)


# ----------------- Blueprint -----------------
enhancements_bp = Blueprint("enhancements", __name__, template_folder="../templates")

# ----------------- Config -----------------
DEFAULT_UPLOAD_FOLDER = os.environ.get("RESUME_UPLOAD_FOLDER", "uploads/resumes")
os.makedirs(DEFAULT_UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXT = {".pdf", ".docx", ".doc", ".txt"}


def get_upload_folder():
    """Return upload folder from config or fallback"""
    try:
        return current_app.config.get("RESUME_UPLOAD_FOLDER", DEFAULT_UPLOAD_FOLDER)
    except RuntimeError:
        return DEFAULT_UPLOAD_FOLDER


# ------------------ Auth pages ------------------

@enhancements_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "student")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("enhancements.register"))

        hashed_password = generate_password_hash(password)

        conn = get_db_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                (username, email, hashed_password, role),
            )
            conn.commit()
            flash("✅ Registration successful! Please log in.", "success")
            return redirect(url_for("enhancements.login"))
        except sqlite3.IntegrityError:
            flash("⚠️ Username or email already exists.", "warning")
            return redirect(url_for("enhancements.register"))

    return render_template("register.html")


@enhancements_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, username, email, password, role 
            FROM users WHERE email=? OR username=?
        """, (login_id, login_id))
        user = cur.fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["username"] = user["username"]

            if user["role"] == "admin":
                return redirect(url_for("enhancements.admin_dashboard"))
            else:
                return redirect(url_for("enhancements.student_dashboard"))
        else:
            flash("❌ Invalid credentials!", "danger")
            return redirect(url_for("enhancements.login"))

    return render_template("login.html")


# ------------------ Admin Pages ------------------

@enhancements_bp.route("/admin_dashboard")
def admin_dashboard():
    conn = get_db_conn()
    cur = conn.cursor()

    # Count students
    cur.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    student_count = cur.fetchone()[0]

    # Count placements
    cur.execute("SELECT COUNT(*) FROM placements")
    placement_count = cur.fetchone()[0]

    # Count applications
    cur.execute("SELECT COUNT(*) FROM applications")
    application_count = cur.fetchone()[0]

    conn.close()

    counts = {
        "students": student_count,
        "placements": placement_count,
        "applications": application_count
    }

    username = session.get("username", "Admin")
    return render_template("admin_dashboard.html", counts=counts, username=username)
@enhancements_bp.route("/admin/students")
def admin_students():
    conn = get_db_conn()
    cur = conn.cursor()
    # Only select columns that exist in your table
    cur.execute("SELECT id, email FROM users WHERE role='student'")
    students = cur.fetchall()
    conn.close()
    return render_template("admin/students.html", students=students)

@enhancements_bp.route("/admin/placements")
def admin_placements():
    conn = get_db_conn()
    cur = conn.cursor()
    # Select only columns that exist in your placements table
    cur.execute("SELECT id, company, role FROM placements")
    placements = cur.fetchall()
    conn.close()
    return render_template("admin/placements.html", placements=placements)
@enhancements_bp.route("/admin/applications")
def admin_applications():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            a.id,
            u.email AS student_email,
            p.company AS placement_name,
            a.status,
            a.applied_at
        FROM applications a
        JOIN users u ON a.user_id = u.id
        JOIN placements p ON a.placement_id = p.id
        ORDER BY a.applied_at DESC
    """)
    applications = cur.fetchall()
    conn.close()
    return render_template("admin/applications.html", applications=applications)





# ---------------- Manage Students ----------------
from flask import request, redirect, url_for, flash

# ✅ Manage Students (list all)
@enhancements_bp.route("/manage_students")
def manage_students():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, email 
        FROM users 
        WHERE role = 'student'
        ORDER BY created_at DESC
    """)
    students = cur.fetchall()
    conn.close()
    return render_template("manage_students.html", students=students)


# ✅ Edit Student
@enhancements_bp.route("/students/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    conn = get_db_conn()
    cur = conn.cursor()

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        cur.execute("UPDATE users SET username=?, email=? WHERE id=?", 
                    (username, email, student_id))
        conn.commit()
        conn.close()
        flash("Student updated successfully!", "success")
        return redirect(url_for("enhancements.manage_students"))

    cur.execute("SELECT id, username, email FROM users WHERE id=?", (student_id,))
    student = cur.fetchone()
    conn.close()
    return render_template("students/edit_student.html", student=student)


# ✅ Delete Student
@enhancements_bp.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    flash("Student deleted successfully!", "success")
    return redirect(url_for("enhancements.manage_students"))


# ✅ View Student Resumes
@enhancements_bp.route("/students/student_resumes/<int:student_id>")
def student_resumes(student_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM resumes WHERE user_id=?", (student_id,))
    resumes = cur.fetchall()
    conn.close()
    return render_template("students/student_resumes.html", resumes=resumes)
# ---------------- Student Applications ----------------
@enhancements_bp.route("/students/<int:student_id>/applications")
def student_applications(student_id):   # 🔥 renamed
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, p.company, p.role, a.status, a.applied_at
        FROM applications a
        JOIN placements p ON a.placement_id = p.id
        WHERE a.user_id = ?
        ORDER BY a.applied_at DESC
    """, (student_id,))
    applications = cur.fetchall()
    conn.close()
    return render_template("students/student_applications.html", applications=applications)


# ---------------- Placement Applications ----------------
@enhancements_bp.route("/view_applications/<int:pid>", methods=["GET"])
def view_applications(pid):   # 🔥 renamed
    conn = get_db_conn()
    cur = conn.cursor()

    # Fetch placement
    cur.execute("SELECT * FROM placements WHERE id = ?", (pid,))
    placement = cur.fetchone()
    if not placement:
        flash("❌ Placement not found.", "danger")
        conn.close()
        return redirect(url_for("enhancements.manage_placements"))

    # Fetch applications + join with users
    cur.execute("""
        SELECT a.id, a.status, a.applied_at,
               u.username, u.email, r.filename AS resume
        FROM applications a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN resumes r ON r.user_id = u.id
        WHERE a.placement_id = ?
        ORDER BY a.applied_at DESC
    """, (pid,))
    rows = cur.fetchall()
    conn.close()

    applications = [
        {
            "id": row["id"],
            "status": row["status"],
            "applied_at": row["applied_at"],
            "username": row["username"],
            "email": row["email"],
            "resume": row["resume"]
        }
        for row in rows
    ]

    return render_template(
        "view_applications.html",
        placement=placement,
        applications=applications
    )

@enhancements_bp.route("/admin/questions1")
def admin_questions():
    return render_template("admin/questions1.html")


@enhancements_bp.route("/manage_placements", methods=["GET", "POST"])
def manage_placements():
    conn = get_db_conn()
    cur = conn.cursor()

    if request.method == "POST":
        company = request.form.get("company")
        role = request.form.get("role")
        location = request.form.get("location")
        description = request.form.get("description")
        link = request.form.get("link")

        if company and role and location:
            cur.execute("""
                INSERT INTO placements (company, role, location, description, link)
                VALUES (?, ?, ?, ?, ?)
            """, (company, role, location, description, link))
            conn.commit()
            flash("✅ Placement added successfully!", "success")
        else:
            flash("⚠️ Company, Role, and Location are required.", "danger")

        return redirect(url_for("enhancements.manage_placements"))

    # for GET → fetch all placements
    cur.execute("SELECT * FROM placements ORDER BY created_at DESC")  # ⚠️ requires created_at column
    placements = cur.fetchall()
    conn.close()
    return render_template("manage_placements.html", placements=placements)


@enhancements_bp.route("/edit_placement/<int:pid>", methods=["GET", "POST"])
def edit_placement(pid):
    conn = get_db_conn()
    cur = conn.cursor()

    if request.method == "POST":
        company = request.form.get("company")
        role = request.form.get("role")
        location = request.form.get("location")
        eligibility = request.form.get("eligibility")
        deadline = request.form.get("deadline")
        description = request.form.get("description")
        link = request.form.get("link")

        cur.execute("""
            UPDATE placements 
            SET company=?, role=?, location=?, eligibility=?, deadline=?, description=?, link=? 
            WHERE id=?
        """, (company, role, location, eligibility, deadline, description, link, pid))
        conn.commit()
        conn.close()

        flash("✅ Placement updated!", "success")
        return redirect(url_for("enhancements.manage_placements"))

    cur.execute("SELECT * FROM placements WHERE id=?", (pid,))
    placement = cur.fetchone()
    conn.close()

    return render_template("edit_placement.html", p=placement)


@enhancements_bp.route("/delete_placement/<int:pid>", methods=["POST"])
def delete_placement(pid):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM placements WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    flash("❌ Placement deleted.", "info")
    return redirect(url_for("enhancements.manage_placements"))



@enhancements_bp.route("/reports")
def reports():
    conn = get_db_conn()
    cur = conn.cursor()

    # Total counts
    cur.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM placements")
    total_placements = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM applications")
    total_applications = cur.fetchone()[0]

    # Application status breakdown
    cur.execute("""
        SELECT status, COUNT(*) as count
        FROM applications
        GROUP BY status
    """)
    status_data = cur.fetchall()
    status_counts = {row["status"]: row["count"] for row in status_data}

    # Success rate: count students with at least 1 'Selected'
    cur.execute("""
        SELECT COUNT(DISTINCT user_id)
        FROM applications
        WHERE status = 'Selected'
    """)
    placed_students = cur.fetchone()[0]

    success_rate = (placed_students / total_students * 100) if total_students > 0 else 0

    conn.close()

    return render_template(
        "reports.html",
        total_students=total_students,
        total_placements=total_placements,
        total_applications=total_applications,
        status_counts=status_counts,
        success_rate=round(success_rate, 2)
    )



# ------------------ Student Dashboard ------------------

@enhancements_bp.route("/student_dashboard")
def student_dashboard():
    if session.get("role") != "student":
        flash("Access denied!", "danger")
        return redirect(url_for("enhancements.login"))
    return render_template("student_dashboard.html", username=session.get("username"))


# ------------------ Placement search & apply ------------------

@enhancements_bp.route("/apply/<int:pid>", methods=["POST"])
def apply(pid):
    if "user_id" not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for("enhancements.login"))

    user_id = session["user_id"]

    conn = get_db_conn()
    cur = conn.cursor()

    # ✅ Check if already applied
    cur.execute(
        "SELECT id FROM applications WHERE placement_id=? AND user_id=?",
        (pid, user_id),
    )
    already_applied = cur.fetchone()

    if already_applied:
        flash("⚠️ You have already applied for this placement.", "warning")
    else:
        # ✅ Insert new application
        cur.execute(
            "INSERT INTO applications (placement_id, user_id, status, applied_at) VALUES (?,?,?,CURRENT_TIMESTAMP)",
            (pid, user_id, "Applied"),
        )
        conn.commit()
        flash("🎉 Application submitted successfully!", "success")

    conn.close()
    return redirect(url_for("enhancements.placements"))
@enhancements_bp.route("/placements")
def placements():
    query = request.args.get("q", "")
    location = request.args.get("location", "")
    user_id = session.get("user_id")

    conn = get_db_conn()
    cur = conn.cursor()

    # fetch jobs
    sql = "SELECT * FROM placements WHERE 1=1"
    params = []
    if query:
        sql += " AND (company LIKE ? OR role LIKE ? OR description LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
    if location:
        sql += " AND location LIKE ?"
        params.append(f"%{location}%")
    cur.execute(sql, params)
    jobs = cur.fetchall()

    # ✅ convert rows to list of dicts
    jobs_list = []
    for j in jobs:
        cur.execute(
            "SELECT 1 FROM applications WHERE placement_id=? AND user_id=?",
            (j["id"], user_id),
        )
        applied = cur.fetchone() is not None
        jobs_list.append({**dict(j), "applied": applied})

    conn.close()
    return render_template("placements.html", jobs=jobs_list, query=query)


@enhancements_bp.route('/api/search_placements')
def api_search_placements():
    """
    API endpoint for live search of placements.
    Returns JSON results.
    """
    query = request.args.get("q", "").strip().lower()
    conn = get_db_conn()
    cursor = conn.cursor()

    if query:
        cursor.execute(
            "SELECT id, title, company, description FROM placements WHERE lower(title) LIKE ? OR lower(company) LIKE ? OR lower(description) LIKE ?",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
    else:
        cursor.execute("SELECT id, title, company, description FROM placements")

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "title": row["title"],
            "company": row["company"],
            "description": (row["description"][:120] + "...") if row["description"] else ""
        })

    return jsonify({"results": results})



# ------------------ Profile ------------------

PROFILE_PIC_FOLDER = os.path.join("uploads", "profile_pics")
RESUME_FOLDER = os.path.join("uploads", "resumes")
os.makedirs(PROFILE_PIC_FOLDER, exist_ok=True)
os.makedirs(RESUME_FOLDER, exist_ok=True)


@enhancements_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("enhancements.login"))

    conn = get_db_conn()
    cur = conn.cursor()

    if request.method == "POST":
        # Get fields from form
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        skills = request.form.get("skills", "").strip()

        # Handle profile picture
        profile_pic_file = request.files.get("profile_pic")
        profile_pic_filename = None
        if profile_pic_file and profile_pic_file.filename:
            profile_pic_filename = secure_filename(profile_pic_file.filename)
            profile_pic_file.save(os.path.join(PROFILE_PIC_FOLDER, profile_pic_filename))

        # Handle resume
        resume_file = request.files.get("resume")
        resume_filename = None
        if resume_file and resume_file.filename:
            resume_filename = secure_filename(resume_file.filename)
            resume_file.save(os.path.join(RESUME_FOLDER, resume_filename))

        # Update DB
        cur.execute("""
            UPDATE users
            SET username=?, email=?, phone=?, skills=?,
                profile_pic=COALESCE(?, profile_pic),
                resume=COALESCE(?, resume)
            WHERE id=?
        """, (username, email, phone, skills,
              profile_pic_filename, resume_filename,
              session["user_id"]))
        conn.commit()
        flash("✅ Profile updated successfully!", "success")
        return redirect(url_for("enhancements.profile"))

    # GET → fetch user data
    cur.execute("""
        SELECT id, username, email, phone, skills, profile_pic, resume
        FROM users WHERE id = ?
    """, (session["user_id"],))
    row = cur.fetchone()
    conn.close()

    user = None
    if row:
        user = {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "phone": row["phone"],
            "skills": row["skills"],
            "profile_pic": row["profile_pic"],
            "resume": row["resume"]
        }

    return render_template("profile.html", user=user)



# ------------------ File Routes ------------------

@enhancements_bp.route('/uploads/profile_pics/<filename>')
def uploaded_profile_pic(filename):
    if os.path.exists(os.path.join(PROFILE_PIC_FOLDER, filename)):
        return send_from_directory(PROFILE_PIC_FOLDER, filename)
    abort(404)


@enhancements_bp.route('/uploads/resumes/<filename>')
def uploaded_resume(filename):
    if os.path.exists(os.path.join(RESUME_FOLDER, filename)):
        return send_from_directory(RESUME_FOLDER, filename)
    abort(404)


# ------------------ Resume Review ------------------

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXT


@enhancements_bp.route("/resume_review", methods=["GET", "POST"])
def resume_review():
    if request.method == "GET":
        return render_template("resume_review.html")

    file = request.files.get("resume")
    user_id = session.get("user_id")

    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        return jsonify({"error": "File type not allowed"}), 400

    save_path = os.path.join(
        get_upload_folder(),
        f"{int(datetime.utcnow().timestamp())}_{filename}"
    )
    file.save(save_path)

    result = analyze_resume(save_path)

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO resumes (user_id, filename, storage_path, verdict, details) VALUES (?, ?, ?, ?, ?)",
        (user_id, filename, save_path, result.get("verdict"), json.dumps(result))
    )
    conn.commit()
    conn.close()

    return jsonify({"result": result})


@enhancements_bp.route("/update_status/<int:app_id>", methods=["POST"])
def update_status(app_id):
    status = request.form.get("status")
    if status not in ["Applied", "Shortlisted", "Selected", "Rejected"]:
        flash("⚠️ Invalid status.", "danger")
        return redirect(request.referrer or url_for("enhancements.admin_dashboard"))

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))
    conn.commit()
    conn.close()

    flash("✅ Application status updated.", "success")
    return redirect(request.referrer or url_for("enhancements.admin_dashboard"))


@enhancements_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    folder = current_app.config.get('RESUME_UPLOAD_FOLDER', 'uploads/resumes')
    return send_from_directory(folder, filename, as_attachment=False)


# ------------------ Chatbot ------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@enhancements_bp.route("/ask", methods=["GET", "POST"])
def ask_question():
    if request.method == "GET":
        return render_template("ask.html")

    data = request.get_json() or {}
    user_question = data.get("question", "").strip()

    if not user_question:
        return jsonify({"answer": "⚠️ Please enter a question."})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful college placement assistant."},
                {"role": "user", "content": user_question}
            ],
            max_tokens=300,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"⚠️ Error fetching answer: {str(e)}"})
@enhancements_bp.route('/chat', methods=['POST'])
def chat_alias():
    """
    Backward compatibility route.
    Proxies requests from /chat to /ask.
    """
    data = request.get_json() or {}
    if "message" in data:
        data["question"] = data.pop("message")
    # Reuse ask_question logic
    return ask_question()


# ------------------ Practice ------------------

@enhancements_bp.route("/practice")
def practice_page():
    return render_template("practice.html")


@enhancements_bp.route("/check_resume", methods=["POST"])
def check_resume():
    try:
        if "resume" not in request.files:
            return jsonify({"error": "No resume uploaded"}), 400

        file = request.files["resume"]

        try:
            text = file.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return jsonify({"error": f"Failed to read file: {str(e)}"}), 400

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an ATS (Applicant Tracking System)."},
                {"role": "user", "content": f"Analyze this resume:\n\n{text}"}
            ]
        )

        feedback = response.choices[0].message.content
        return jsonify({"result": feedback})

    except Exception as e:
        print("❌ Error in check_resume:", str(e))
        return jsonify({"error": str(e)}), 500


# ------------------ Feedback / Rating ------------------

@enhancements_bp.route("/rate", methods=["GET", "POST"])
def rate():
    conn = get_db_conn()
    cur = conn.cursor()

    if request.method == "POST":
        rating = int(request.form.get("rating", 0))
        comment = request.form.get("comment", "").strip()
        user_id = session.get("user_id")

        if not user_id:
            flash("You must be logged in to rate.", "warning")
            return redirect(url_for("enhancements.login"))

        if 1 <= rating <= 5:
            cur.execute(
                "INSERT INTO feedback (user_id, rating, comment) VALUES (?, ?, ?)",
                (user_id, rating, comment),
            )
            conn.commit()
            flash("Thanks for your feedback! ⭐", "success")
        else:
            flash("Invalid rating. Please select between 1 and 5 stars.", "danger")

        conn.close()
        return redirect(url_for("enhancements.rate"))

    feedbacks = cur.execute(
        "SELECT f.id, f.rating, f.comment, f.created_at, u.username "
        "FROM feedback f LEFT JOIN users u ON f.user_id = u.id "
        "ORDER BY f.created_at DESC"
    ).fetchall()
    conn.close()

    return render_template("rate.html", feedbacks=feedbacks)


# ------------------ Misc ------------------

@enhancements_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("enhancements.login"))


@enhancements_bp.route("/about")
def about():
    return render_template("about.html")


@enhancements_bp.route("/settings")
def settings():
    return render_template("settings.html")


@enhancements_bp.route("/status")
def status():

    return render_template("status.html")            

