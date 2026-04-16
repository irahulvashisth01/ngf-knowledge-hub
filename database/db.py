import sqlite3
import uuid
from config import Config


# ---------------- DB CONNECTION ----------------
def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- INITIALIZE DATABASE ----------------
def init_db():
    conn = get_db()
    cur = conn.cursor()

    # ---------------- USERS TABLE ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        mobile TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        profile_image TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------- NOTES TABLE (UPGRADED) ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        filename TEXT NOT NULL,
        subject TEXT NOT NULL,
        semester INTEGER NOT NULL,
        unit TEXT,
        teacher TEXT,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        downloads INTEGER DEFAULT 0,
        share_id TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # ---------------- SAFE COLUMN ADD (MIGRATION) ----------------
    def safe_add_column(column_def):
        try:
            cur.execute(f"ALTER TABLE notes ADD COLUMN {column_def}")
            print(f"✅ Added column: {column_def}")
        except Exception as e:
            # Ignore if column exists, print other errors
            if "duplicate column" not in str(e).lower():
                print(f"⚠️ Column add error: {e}")

    safe_add_column("unit TEXT")
    safe_add_column("teacher TEXT")
    safe_add_column("downloads INTEGER DEFAULT 0")
    safe_add_column("share_id TEXT")

    # ---------------- SETTINGS TABLE ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_name TEXT DEFAULT 'Notes Hub',
        allow_upload INTEGER DEFAULT 1
    )
    """)

    # ---------------- INDEXES (PERFORMANCE BOOST) ----------------
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_subject ON notes(subject)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_semester ON notes(semester)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_share_id ON notes(share_id)")

    # ---------------- DEFAULT ADMIN ----------------
    cur.execute("SELECT * FROM users WHERE email=?", ("admin@gmail.com",))
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO users(name,email,mobile,role)
        VALUES(?,?,?,?)
        """, ("Admin", "admin@gmail.com", "9999999999", "admin"))

    # ---------------- DEFAULT SETTINGS ----------------
    cur.execute("SELECT * FROM settings")
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO settings(site_name, allow_upload)
        VALUES(?,?)
        """, ("Notes Hub", 1))

    # ---------------- GENERATE SHARE IDs FOR OLD DATA ----------------
    notes = cur.execute(
        "SELECT id FROM notes WHERE share_id IS NULL OR share_id=''"
    ).fetchall()

    for note in notes:
        share_id = generate_unique_share_id(cur)

        cur.execute(
            "UPDATE notes SET share_id=? WHERE id=?",
            (share_id, note["id"])
        )

    conn.commit()
    conn.close()


# ---------------- GENERATE UNIQUE SHARE ID ----------------
def generate_unique_share_id(cur):
    while True:
        share_id = uuid.uuid4().hex[:10]

        exists = cur.execute(
            "SELECT id FROM notes WHERE share_id=?",
            (share_id,)
        ).fetchone()

        if not exists:
            return share_id


# ---------------- CREATE NOTE (SAFE INSERT) ----------------
def create_note(title, filename, subject, semester, user_id, unit=None, teacher=None):
    conn = get_db()
    cur = conn.cursor()

    share_id = generate_unique_share_id(cur)

    cur.execute("""
    INSERT INTO notes(title, filename, subject, semester, unit, teacher, user_id, share_id)
    VALUES(?,?,?,?,?,?,?,?)
    """, (title, filename, subject, semester, unit, teacher, user_id, share_id))

    conn.commit()
    conn.close()

    return share_id


# ---------------- INCREMENT DOWNLOAD ----------------
def increment_download(share_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE notes SET downloads = downloads + 1 WHERE share_id=?",
        (share_id,)
    )

    conn.commit()
    conn.close()