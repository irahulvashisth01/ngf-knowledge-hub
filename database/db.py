import sqlite3
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
        semester INTEGER NOT NULL,
        uploaded_by TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        downloads INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------- SETTINGS TABLE ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_name TEXT DEFAULT 'Notes Hub',
        allow_upload INTEGER DEFAULT 1
    )
    """)

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

    conn.commit()
    conn.close()