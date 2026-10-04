import sqlite3
import os
import json
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent.parent / "users.db"

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initializes and migrates the database schema safely while preserving existing data."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create users table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                full_name TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if users table needs migration (check if columns exist)
        cursor.execute("PRAGMA table_info(users)")
        user_cols = [row["name"] for row in cursor.fetchall()]
        if "full_name" not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT DEFAULT ''")
        if "created_at" not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT ''")

        # Create history table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                risk INTEGER NOT NULL,
                risk_level TEXT DEFAULT 'Moderate',
                details TEXT DEFAULT '{}',
                timestamp TEXT NOT NULL
            )
        """)
        
        # Check if history table has id column
        cursor.execute("PRAGMA table_info(history)")
        history_cols = [row["name"] for row in cursor.fetchall()]
        
        # If legacy history table without 'id' exists
        if "id" not in history_cols:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    risk INTEGER NOT NULL,
                    risk_level TEXT DEFAULT 'Moderate',
                    details TEXT DEFAULT '{}',
                    timestamp TEXT NOT NULL
                )
            """)
            cursor.execute("""
                INSERT INTO history_new (username, risk, risk_level, details, timestamp)
                SELECT username, risk, 
                    CASE 
                        WHEN risk <= 30 THEN 'Low'
                        WHEN risk <= 50 THEN 'Moderate'
                        ELSE 'High'
                    END,
                    '{}', timestamp 
                FROM history
            """)
            cursor.execute("DROP TABLE history")
            cursor.execute("ALTER TABLE history_new RENAME TO history")
        else:
            if "risk_level" not in history_cols:
                cursor.execute("ALTER TABLE history ADD COLUMN risk_level TEXT DEFAULT 'Moderate'")
            if "details" not in history_cols:
                cursor.execute("ALTER TABLE history ADD COLUMN details TEXT DEFAULT '{}'")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_username ON history(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp DESC)")
