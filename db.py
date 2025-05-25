import sqlite3

DB_FILE = 'routes.db'

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                method TEXT NOT NULL,
                target_url TEXT NOT NULL,
                policy_id INTEGER,
                UNIQUE(path, method),
                FOREIGN KEY(policy_id) REFERENCES policies(id) ON DELETE SET NULL
            )
        ''')
