# db.py
import psycopg2
import os

def get_db_connection():
    return psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'gateway'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', '5432')
    )

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS policies (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                );
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS routes (
                    id SERIAL PRIMARY KEY,
                    path TEXT NOT NULL,
                    method TEXT NOT NULL,
                    target_url TEXT NOT NULL,
                    policy_id INTEGER REFERENCES policies(id),
                    UNIQUE (path, method),
                    FOREIGN KEY(policy_id) REFERENCES policies(id) ON DELETE SET NULL
                );
            ''')
        conn.commit()
