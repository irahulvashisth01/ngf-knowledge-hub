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

    # ---------------- NOTES TABLE ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        filename TEXT NOT NULL,
        subject TEXT NOT NULL,
        semester TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        downloads INTEGER DEFAULT 0,
        share_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # ---------------- ADD COLUMN SAFELY ----------------
    try:
        cur.execute("ALTER TABLE notes ADD COLUMN share_id TEXT")
    except:
        pass

    # ---------------- SETTINGS TABLE ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_name TEXT DEFAULT 'Notes Hub',
        allow_upload INTEGER DEFAULT 1
    )
    """)

    # ---------------- INDEXES ----------------
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_subject ON notes(subject)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_semester ON notes(semester)")

    # ---------------- DEFAULT ADMIN ----------------
    cur.execute("SELECT * FROM users WHERE email=?", ("admin@gmail.com",))
    admin = cur.fetchone()

    if not admin:
        cur.execute("""
        INSERT INTO users(name,email,mobile,role)
        VALUES(?,?,?,?)
        """, ("Admin", "admin@gmail.com", "9999999999", "admin"))

    # ---------------- DEFAULT SETTINGS ----------------
    cur.execute("SELECT * FROM settings")
    setting = cur.fetchone()

    if not setting:
        cur.execute("""
        INSERT INTO settings(site_name, allow_upload)
        VALUES(?,?)
        """, ("Notes Hub", 1))

    # ---------------- GENERATE SHARE ID FOR OLD NOTES ----------------
    notes = cur.execute("SELECT id FROM notes WHERE share_id IS NULL").fetchall()

    for note in notes:
        share_id = uuid.uuid4().hex[:10]
        cur.execute("UPDATE notes SET share_id = ? WHERE id = ?", (share_id, note['id']))

    conn.commit()
    conn.close()