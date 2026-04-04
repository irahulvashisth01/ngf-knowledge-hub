from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
import sqlite3
import os

from config import Config
from database.db import init_db

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

init_db()


# ---------------- DB HELPER ----------------
def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE DEFAULT ADMIN ----------------
def create_default_admin():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email=?", ("admin@gmail.com",))
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO users(name,email,mobile,role)
        VALUES(?,?,?,?)
        """, ("Admin", "admin@gmail.com", "9999999999", "admin"))
        conn.commit()

    conn.close()

create_default_admin()


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
    return render_template("index.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        mobile = request.form.get("mobile")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        if cur.fetchone():
            conn.close()
            return "⚠️ Email already exists"

        cur.execute(
            "INSERT INTO users(name,email,mobile) VALUES(?,?,?)",
            (name, email, mobile)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()
        conn.close()

        if user and user["name"] == name:
            session["user"] = user["name"]
            session["role"] = user["role"]

            return redirect(request.args.get("next") or url_for("dashboard"))

        return "❌ Invalid details"

    return render_template("login.html")


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
@app.route("/view/<filename>")
def view_file(filename):
    if not login_required():
        return login_required_redirect()

    return send_from_directory(
        Config.UPLOAD_FOLDER,
        filename
    )


# ---------------- DOWNLOAD (LOGIN REQUIRED) ----------------
@app.route("/download/<filename>")
def download_file(filename):
    if not login_required():
        return login_required_redirect()

    conn = get_db_connection()
    conn.execute("""
        UPDATE notes 
        SET downloads = downloads + 1 
        WHERE filename=?
    """, (filename,))
    conn.commit()
    conn.close()

    return send_from_directory(
        Config.UPLOAD_FOLDER,
        filename,
        as_attachment=True
    )


# ---------------- SHARE (PUBLIC) ----------------
from flask import redirect

@app.route('/share/<share_id>')
def share_note(share_id):
    conn = get_db()
    cur = conn.cursor()

    note = cur.execute(
        "SELECT * FROM notes WHERE share_id = ?",
        (share_id,)
    ).fetchone()

    if note:
        return redirect(url_for('static', filename='uploads/' + note['filename']))
    else:
        return "Note not found", 404

# ---------------- UPLOAD (LOGIN REQUIRED) ----------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not login_required():
        return login_required_redirect()

    if request.method == "POST":
        file = request.files.get("file")
        subject = request.form.get("subject")
        semester = request.form.get("semester")

        if not file or file.filename == "":
            return "❌ No file selected"

        filename = file.filename
        file.save(os.path.join(Config.UPLOAD_FOLDER, filename))

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO notes(title, filename, subject, semester, uploaded_by)
            VALUES(?,?,?,?,?)
        """, (filename, filename, subject, semester, session["user"]))

        conn.commit()
        conn.close()

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

    cur.execute("SELECT * FROM notes WHERE status='pending'")
    pending_notes = cur.fetchall()

    cur.execute("SELECT * FROM notes WHERE status='approved'")
    approved_notes = cur.fetchall()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        pending_notes=pending_notes,
        approved_notes=approved_notes,
        users=users
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
        return "⚠️ Cannot remove yourself"

    conn.execute("UPDATE users SET role='user' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- ERROR ----------------
@app.errorhandler(404)
def page_not_found(e):
    return "<h2>404 - Page Not Found</h2>", 404


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