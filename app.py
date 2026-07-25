from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os

from config import Config
from database.db import init_db, create_user, verify_user, create_note

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

init_db()

# NOTE: the old create_default_admin() here was removed — init_db() in
# db.py already seeds the default admin, and this copy would have crashed
# with a NOT NULL constraint on `password` if it had ever actually run
# (it never inserted a password).

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "ppt", "pptx", "txt", "zip"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ---------------- DB HELPER ----------------
def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- AUTH HELPERS ----------------
def login_required():
    return "user" in session


def admin_required():
    return session.get("role") == "admin"


def login_required_redirect():
    return redirect(url_for("login", next=request.path))


# ---------------- SUBJECT DATA ----------------
SUBJECTS = {
    1: ["Chemistry","BET","M1","English"],
    2: ["Physics","PPS","M2"],
    3: ["ETC","DE","AEC","DSA","M3"],
    4: ["COA","DAA","OS","DM","EVS","ECO"],
    5: ["ACA","Biology","COI","DBMS","FLA","OOPS","S&S","UHV"],
    6: ["CN","DM","HRM","IS","MG","SC","SS"],
    7: ["AI","ML","CD","Cloud","Big Data","Elective-I","Mini Project"],
    8: ["Major Project","Internship","Elective-II","Seminar"]
}


# ---------------- ROUTES ----------------

# HOME
@app.route("/")
def home():
    query = request.args.get("q", "")
    semester = request.args.get("semester", "")
    subject = request.args.get("subject", "")
    page = int(request.args.get("page", 1))
    per_page = 20   # 🔥 number of notes per page

    conn = get_db_connection()
    cur = conn.cursor()

    sql = "SELECT * FROM notes WHERE status='approved'"
    params = []

    if query:
        sql += " AND title LIKE ?"
        params.append(f"%{query}%")

    if semester:
        sql += " AND semester=?"
        params.append(int(semester))

    if subject:
        sql += " AND subject=?"
        params.append(subject)

    # 🔥 Pagination logic
    offset = (page - 1) * per_page
    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    cur.execute(sql, params)
    notes = cur.fetchall()

    # 🔥 Total count (for page numbers)
    count_sql = "SELECT COUNT(*) FROM notes WHERE status='approved'"
    cur.execute(count_sql)
    total_notes = cur.fetchone()[0]

    total_pages = (total_notes + per_page - 1) // per_page

    conn.close()

    return render_template(
        "index.html",
        notes=notes,
        subjects=SUBJECTS,
        page=page,
        total_pages=total_pages,
        query=query,
        selected_sem=semester,
        selected_sub=subject
    )


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        mobile = request.form.get("mobile")
        password = request.form.get("password")

        if not name or not email or not mobile or not password:
            return "⚠️ All fields are required"

        user_id = create_user(name, email, mobile, password)

        if user_id is None:
            return "⚠️ Email already exists"

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = verify_user(email, password)

        if user:
            session["user"] = user["name"]
            session["user_id"] = user["id"]
            session["role"] = user["role"]

            return redirect(request.args.get("next") or url_for("dashboard"))

        return "❌ Invalid details"

    return render_template("login.html")

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("profile.html", user=session.get("user"))


    
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ---------------- DASHBOARD (PUBLIC) ----------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ---------------- SEARCH (PUBLIC) ----------------
@app.route("/search")
def search():
    query = request.args.get("q", "")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM notes
        WHERE status='approved'
        AND (title LIKE ? OR subject LIKE ?)
        ORDER BY downloads DESC
    """, (f"%{query}%", f"%{query}%"))

    results = cur.fetchall()
    conn.close()

    return render_template("search.html", results=results, query=query)


# ---------------- BTECH (PUBLIC) ----------------
@app.route("/btech")
def btech():
    return render_template("btech.html")


# ---------------- SEMESTER (PUBLIC) ----------------
@app.route("/semester/<int:sem>")
def semester(sem):
    return render_template(
        "subjects.html",
        subjects=SUBJECTS.get(sem, []),
        sem=sem
    )


# ---------------- NOTES (PUBLIC) ----------------
@app.route("/notes/<subject>/<int:sem>")
def notes(subject, sem):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM notes 
        WHERE subject=? AND semester=? AND status='approved'
    """, (subject, sem))

    notes = cur.fetchall()
    conn.close()

    return render_template("notes.html", notes=notes, subject=subject)


# ---------------- VIEW (LOGIN REQUIRED) ----------------
@app.route('/view/<filename>')
def view_file(filename):

    # Optional login protection
    # if not login_required():
    #     return login_required_redirect()

    conn = get_db_connection()

    conn.execute(
        "UPDATE notes SET views = views + 1 WHERE filename=?",
        (filename,)
    )

    conn.commit()
    conn.close()

    return send_from_directory(
        Config.UPLOAD_FOLDER,
        filename
    )


# ---------------- DOWNLOAD (PUBLIC) ----------------
@app.route('/download/<filename>')
def download_file(filename):

    conn = get_db_connection()

    conn.execute(
        "UPDATE notes SET downloads = downloads + 1 WHERE filename=?",
        (filename,)
    )

    conn.commit()
    conn.close()

    return send_from_directory(
        Config.UPLOAD_FOLDER,
        filename,
        as_attachment=True
    )

# ---------------- SHARE (PUBLIC) ----------------
@app.route('/share/<share_id>')
def share_note(share_id):

    mode = request.args.get("mode")

    conn = get_db_connection()

    note = conn.execute(
        "SELECT * FROM notes WHERE share_id=?",
        (share_id,)
    ).fetchone()

    conn.close()

    # Note not found
    if not note:
        return "❌ Note not found", 404

    # Share URL
    share_url = (
        f"https://btechnotes.online/share/"
        f"{note['share_id']}"
    )

    # Download mode
    if mode == "download":

        return send_from_directory(
            Config.UPLOAD_FOLDER,
            note["filename"],
            as_attachment=True
        )

    # Clean Share Text
    share_text = f"""📚 {note['title']}

📖 Subject: {note['subject']}
🏛️ Semester: {note['semester']}

🌐 Website:
https://btechnotes.online

🔗 Open Note:
{share_url}
"""

    return render_template(
        "share.html",
        note=note,
        share_text=share_text,
        share_url=share_url
    )

# ---------------- UPLOAD (LOGIN REQUIRED) ----------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not login_required():
        return login_required_redirect()

    if request.method == "POST":
        file = request.files.get("file")
        title = request.form.get("title")
        subject = request.form.get("subject")
        semester = request.form.get("semester")
        unit = request.form.get("unit")
        teacher = request.form.get("teacher")

        if not file or file.filename == "":
            return "❌ No file selected"

        if not allowed_file(file.filename):
            return "❌ File type not allowed"

        if not subject or not semester:
            return "❌ Subject and semester are required"

        filename = secure_filename(file.filename)

        # Avoid overwriting an existing file with the same name
        base, ext = os.path.splitext(filename)
        save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        counter = 1
        while os.path.exists(save_path):
            filename = f"{base}_{counter}{ext}"
            save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            counter += 1

        file.save(save_path)

        file_size = os.path.getsize(save_path)
        file_type = ext.lstrip(".").lower()

        create_note(
            title=title or filename,
            filename=filename,
            subject=subject,
            semester=int(semester),
            user_id=session["user_id"],
            unit=unit,
            teacher=teacher,
            file_size=file_size,
            file_type=file_type
        )

        return "✅ Uploaded (Pending Approval)"

    return render_template("upload.html", subjects=SUBJECTS)


# ---------------- ADMIN PANEL ----------------
@app.route("/admin")
def admin():

    if not login_required():
        return login_required_redirect()

    if not admin_required():
        return "⛔ Access Denied"

    conn = get_db_connection()
    cur = conn.cursor()

    # Pending Notes
    cur.execute(
        "SELECT * FROM notes WHERE status='pending'"
    )
    pending_notes = cur.fetchall()

    # Approved Notes
    cur.execute(
        "SELECT * FROM notes WHERE status='approved'"
    )
    approved_notes = cur.fetchall()

    # Users
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    # Total Views
    total_views = cur.execute(
        "SELECT SUM(views) FROM notes"
    ).fetchone()[0] or 0

    # Total Downloads
    total_downloads = cur.execute(
        "SELECT SUM(downloads) FROM notes"
    ).fetchone()[0] or 0

    # Top Viewed Notes
    top_viewed = cur.execute("""
        SELECT *
        FROM notes
        WHERE status='approved'
        ORDER BY views DESC
        LIMIT 5
    """).fetchall()

    # Top Downloaded Notes
    top_downloaded = cur.execute("""
        SELECT *
        FROM notes
        WHERE status='approved'
        ORDER BY downloads DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "admin.html",

        pending_notes=pending_notes,
        approved_notes=approved_notes,
        users=users,

        total_views=total_views,
        total_downloads=total_downloads,

        top_viewed=top_viewed,
        top_downloaded=top_downloaded
    )

# ---------------- ADMIN ACTIONS ----------------
@app.route("/approve/<int:id>")
def approve(id):
    if not admin_required():
        return "Access Denied"

    conn = get_db_connection()
    conn.execute("UPDATE notes SET status='approved' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/delete/<int:id>")
def delete(id):
    if not admin_required():
        return "Access Denied"

    conn = get_db_connection()
    conn.execute("DELETE FROM notes WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/make_admin/<int:id>")
def make_admin(id):
    if not admin_required():
        return "Access Denied"

    conn = get_db_connection()
    conn.execute("UPDATE users SET role='admin' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/remove_admin/<int:id>")
def remove_admin(id):
    if not admin_required():
        return "Access Denied"

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id=?", (id,)).fetchone()

    if user["name"] == session["user"]:
        conn.close()
        return "⚠️ Cannot remove yourself"

    conn.execute("UPDATE users SET role='user' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- LEGAL & INFO PAGES ----------------

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')


# ---------------- ERROR HANDLING ----------------

@app.errorhandler(404)
def page_not_found(e):
    return "<h2>404 - Page Not Found</h2>", 404


@app.errorhandler(500)
def internal_error(e):
    return "<h2>500 - Internal Server Error (Check templates)</h2>", 500

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)