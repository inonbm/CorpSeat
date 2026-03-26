import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'corpseat.db')

def get_db_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    # CRITICAL — SQLite Foreign Key Configuration:
    # Every database connection MUST execute the following immediately after opening:
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DB_PATH):
    conn = get_db_connection(db_path)
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
