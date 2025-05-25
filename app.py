from flask import Flask, request, jsonify
import sqlite3
import requests
import os

app = Flask(__name__)

DB_FILE = 'routes.db'
POLICY_DIR = './policies'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
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

@app.route('/admin/policies', methods=['POST'])
def create_policy():
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({"error": "Policy name is required"}), 400
    # Para simplificar, só cria no banco. Código fica no arquivo manualmente.
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO policies (name) VALUES (?)', (name,))
        return jsonify({"message": "Policy created successfully", "policy_id": cursor.lastrowid}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Policy name must be unique"}), 400

@app.route('/admin/policies', methods=['GET'])
def list_policies():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('SELECT id, name FROM policies')
        policies = [dict(zip(['id', 'name'], row)) for row in cursor.fetchall()]
    return jsonify(policies)

@app.route('/admin/routes', methods=['POST'])
def create_route():
    data = request.json
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO routes (path, method, target_url, policy_id) VALUES (?, ?, ?, ?)',
                           (data['path'], data['method'].upper(), data['target_url'], data.get('policy_id')))
        return jsonify({"message": "Route created successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Route with this path and method already exists"}), 400

@app.route('/admin/routes', methods=['GET'])
def list_routes():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('''
            SELECT r.id, r.path, r.method, r.target_url, p.id as policy_id, p.name as policy_name
            FROM routes r
            LEFT JOIN policies p ON r.policy_id = p.id
        ''')
        routes = []
        for row in cursor.fetchall():
            route = dict(zip(['id', 'path', 'method', 'target_url', 'policy_id', 'policy_name'], row))
            routes.append(route)
    return jsonify(routes)

@app.route('/admin/routes/<int:route_id>', methods=['PUT'])
def update_route(route_id):
    data = request.json
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('''
                UPDATE routes SET path = ?, method = ?, target_url = ?, policy_id = ?
                WHERE id = ?
            ''', (data['path'], data['method'].upper(), data['target_url'], data.get('policy_id'), route_id))
        return jsonify({"message": "Route updated successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Another route with this path and method already exists"}), 400

@app.route('/admin/routes/<int:route_id>', methods=['DELETE'])
def delete_route(route_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('DELETE FROM routes WHERE id = ?', (route_id,))
    return jsonify({"message": "Route deleted successfully"})

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    full_path = '/' + path
    method = request.method.upper()

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('''
            SELECT r.target_url, p.name FROM routes r
            LEFT JOIN policies p ON r.policy_id = p.id
            WHERE r.path = ? AND r.method = ?
        ''', (full_path, method))
        result = cursor.fetchone()

    if not result:
        return jsonify({"error": "Route not found"}), 404

    target_url, policy_name = result

    if policy_name:
        policy_path = os.path.join(POLICY_DIR, f"{policy_name}.py")
        if not os.path.isfile(policy_path):
            return jsonify({"error": f"Policy script '{policy_name}.py' not found"}), 500
        with open(policy_path, 'r') as f:
            policy_code = f.read()
        try:
            exec_globals = {'request': request, 'reject': lambda msg: (_ for _ in ()).throw(Exception(msg))}
            exec(policy_code, exec_globals)
        except Exception as e:
            return jsonify({"error": str(e)}), 403

    response = requests.request(method, target_url, headers=request.headers, data=request.get_data(), params=request.args)
    return (response.content, response.status_code, response.headers.items())

if __name__ == '__main__':
    init_db()
    if not os.path.exists(POLICY_DIR):
        os.makedirs(POLICY_DIR)
    app.run(host='0.0.0.0', port=8080)
