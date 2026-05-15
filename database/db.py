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

    # ==================================================
    # USERS TABLE
    # ==================================================
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

    # ==================================================
    # NOTES TABLE
    # ==================================================
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

        views INTEGER DEFAULT 0,
        downloads INTEGER DEFAULT 0,

        share_id TEXT UNIQUE,

        file_size INTEGER DEFAULT 0,
        file_type TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # ==================================================
    # SETTINGS TABLE
    # ==================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        site_name TEXT DEFAULT 'Notes Hub',

        allow_upload INTEGER DEFAULT 1
    )
    """)

    # ==================================================
    # SAFE MIGRATION SYSTEM
    # ==================================================
    def safe_add_column(column_def):

        try:
            cur.execute(f"ALTER TABLE notes ADD COLUMN {column_def}")
            print(f"✅ Added column: {column_def}")

        except Exception as e:

            if "duplicate column" not in str(e).lower():
                print(f"⚠️ Migration Error: {e}")

    # ---------------- SAFE COLUMNS ----------------
    safe_add_column("unit TEXT")
    safe_add_column("teacher TEXT")

    safe_add_column("views INTEGER DEFAULT 0")
    safe_add_column("downloads INTEGER DEFAULT 0")

    safe_add_column("share_id TEXT")

    safe_add_column("file_size INTEGER DEFAULT 0")
    safe_add_column("file_type TEXT")

    # ==================================================
    # PERFORMANCE INDEXES
    # ==================================================
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_notes_subject
    ON notes(subject)
    """)

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_notes_semester
    ON notes(semester)
    """)

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_notes_share_id
    ON notes(share_id)
    """)

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_notes_views
    ON notes(views)
    """)

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_notes_downloads
    ON notes(downloads)
    """)

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_notes_created
    ON notes(created_at)
    """)

    # ==================================================
    # DEFAULT ADMIN
    # ==================================================
    cur.execute(
        "SELECT * FROM users WHERE email=?",
        ("admin@gmail.com",)
    )

    if not cur.fetchone():

        cur.execute("""
        INSERT INTO users(name,email,mobile,role)
        VALUES(?,?,?,?)
        """, (
            "Admin",
            "admin@gmail.com",
            "9999999999",
            "admin"
        ))

        print("✅ Default admin created")

    # ==================================================
    # DEFAULT SETTINGS
    # ==================================================
    cur.execute("SELECT * FROM settings")

    if not cur.fetchone():

        cur.execute("""
        INSERT INTO settings(site_name, allow_upload)
        VALUES(?,?)
        """, (
            "Notes Hub",
            1
        ))

        print("✅ Default settings created")

    # ==================================================
    # GENERATE SHARE IDS FOR OLD DATA
    # ==================================================
    notes = cur.execute("""
    SELECT id
    FROM notes
    WHERE share_id IS NULL
    OR share_id=''
    """).fetchall()

    for note in notes:

        share_id = generate_unique_share_id(cur)

        cur.execute("""
        UPDATE notes
        SET share_id=?
        WHERE id=?
        """, (
            share_id,
            note["id"]
        ))

    if notes:
        print(f"✅ Generated share IDs for {len(notes)} old notes")

    conn.commit()
    conn.close()

    print("✅ Database Initialized Successfully")


# ==================================================
# GENERATE UNIQUE SHARE ID
# ==================================================
def generate_unique_share_id(cur):

    while True:

        share_id = uuid.uuid4().hex[:10]

        exists = cur.execute(
            "SELECT id FROM notes WHERE share_id=?",
            (share_id,)
        ).fetchone()

        if not exists:
            return share_id


# ==================================================
# CREATE NOTE
# ==================================================
def create_note(
    title,
    filename,
    subject,
    semester,
    user_id,
    unit=None,
    teacher=None,
    file_size=0,
    file_type=None
):

    conn = get_db()
    cur = conn.cursor()

    share_id = generate_unique_share_id(cur)

    cur.execute("""
    INSERT INTO notes(

        title,
        filename,
        subject,
        semester,

        unit,
        teacher,

        user_id,

        share_id,

        file_size,
        file_type

    )

    VALUES(?,?,?,?,?,?,?,?,?,?)
    """, (

        title,
        filename,

        subject,
        semester,

        unit,
        teacher,

        user_id,

        share_id,

        file_size,
        file_type
    ))

    conn.commit()
    conn.close()

    return share_id


# ==================================================
# INCREMENT VIEW
# ==================================================
def increment_view(filename):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    UPDATE notes
    SET views = views + 1
    WHERE filename=?
    """, (filename,))

    conn.commit()
    conn.close()


# ==================================================
# INCREMENT DOWNLOAD
# ==================================================
def increment_download(filename):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    UPDATE notes
    SET downloads = downloads + 1
    WHERE filename=?
    """, (filename,))

    conn.commit()
    conn.close()


# ==================================================
# GET TRENDING NOTES
# ==================================================
def get_trending_notes(limit=10):

    conn = get_db()
    cur = conn.cursor()

    notes = cur.execute("""
    SELECT *
    FROM notes
    WHERE status='approved'
    ORDER BY downloads DESC
    LIMIT ?
    """, (limit,)).fetchall()

    conn.close()

    return notes


# ==================================================
# GET MOST VIEWED NOTES
# ==================================================
def get_most_viewed_notes(limit=10):

    conn = get_db()
    cur = conn.cursor()

    notes = cur.execute("""
    SELECT *
    FROM notes
    WHERE status='approved'
    ORDER BY views DESC
    LIMIT ?
    """, (limit,)).fetchall()

    conn.close()

    return notes


# ==================================================
# GET LATEST NOTES
# ==================================================
def get_latest_notes(limit=10):

    conn = get_db()
    cur = conn.cursor()

    notes = cur.execute("""
    SELECT *
    FROM notes
    WHERE status='approved'
    ORDER BY created_at DESC
    LIMIT ?
    """, (limit,)).fetchall()

    conn.close()

    return notes