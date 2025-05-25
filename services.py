from db import get_connection
from models import Policy, Route

def create_policy(name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO policies (name) VALUES (?)', (name,))
        return cursor.lastrowid

def list_policies():
    with get_connection() as conn:
        cursor = conn.execute('SELECT id, name FROM policies')
        return [Policy(id=row[0], name=row[1]) for row in cursor.fetchall()]

def create_route(path, method, target_url, policy_id=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO routes (path, method, target_url, policy_id) VALUES (?, ?, ?, ?)',
            (path, method.upper(), target_url, policy_id)
        )
        return cursor.lastrowid

def list_routes():
    with get_connection() as conn:
        cursor = conn.execute('''
            SELECT r.id, r.path, r.method, r.target_url, p.id, p.name
            FROM routes r LEFT JOIN policies p ON r.policy_id = p.id
        ''')
        routes = []
        for row in cursor.fetchall():
            routes.append(Route(
                id=row[0], path=row[1], method=row[2],
                target_url=row[3], policy_id=row[4], policy_name=row[5]
            ))
        return routes

def get_route_by_path_and_method(path, method):
    with get_connection() as conn:
        cursor = conn.execute('''
            SELECT r.target_url, p.name FROM routes r
            LEFT JOIN policies p ON r.policy_id = p.id
            WHERE r.path = ? AND r.method = ?
        ''', (path, method.upper()))
        return cursor.fetchone()
