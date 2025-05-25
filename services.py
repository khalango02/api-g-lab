from db import get_db_connection
import psycopg2

def create_policy(name):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO policies (name) VALUES (%s) RETURNING id',
                (name,)
            )
            return cur.fetchone()[0]

def get_policy_script_path(policy_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT script_path FROM policies WHERE id = %s', (policy_id,))
            result = cur.fetchone()
            return result[0] if result else None

def create_route(path, method, target_url, policy_id=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO routes (path, method, target_url, policy_id) VALUES (%s, %s, %s, %s) RETURNING id',
                (path, method.upper(), target_url, policy_id)
            )
            return cur.fetchone()[0]

def list_routes():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id, path, method, target_url, policy_id FROM routes')
            return [dict(zip(['id', 'path', 'method', 'target_url', 'policy_id'], row)) for row in cur.fetchall()]

def update_route(route_id, path, method, target_url, policy_id=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                '''
                UPDATE routes
                SET path = %s, method = %s, target_url = %s, policy_id = %s
                WHERE id = %s
                ''',
                (path, method.upper(), target_url, policy_id, route_id)
            )

def delete_route(route_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM routes WHERE id = %s', (route_id,))

def find_route(path, method):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT target_url, policy_id FROM routes WHERE path = %s AND method = %s',
                (path, method)
            )
            return cur.fetchone()

def find_policy_name(policy_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT name FROM policies WHERE id = %s',
                (policy_id,)
            )
            return cur.fetchone()
