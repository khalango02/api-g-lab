from flask import Flask, request, jsonify
from db import init_db
import services
import utils

init_db()

app = Flask(__name__)
    

@app.route('/admin/policies', methods=['POST'])
def create_policy():
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({"error": "Policy name is required"}), 400
    try:
        policy_id = services.create_policy(name)
        return jsonify({"message": "Policy created successfully", "policy_id": policy_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/admin/policies', methods=['GET'])
def list_policies():
    policies = services.list_policies()
    result = [{"id": p.id, "name": p.name} for p in policies]
    return jsonify(result)

@app.route('/admin/routes', methods=['POST'])
def create_route():
    data = request.json
    try:
        route_id = services.create_route(
            data['path'], data['method'], data['target_url'], data.get('policy_id')
        )
        return jsonify({"message": "Route created successfully", "route_id": route_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/admin/routes', methods=['GET'])
def list_routes():
    routes = services.list_routes()
    result = []
    for r in routes:
        result.append({
            "id": r.id,
            "path": r.path,
            "method": r.method,
            "target_url": r.target_url,
            "policy_id": r.policy_id,
            "policy_name": r.policy_name
        })
    return jsonify(result)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    full_path = '/' + path
    method = request.method.upper()

    route = services.get_route_by_path_and_method(full_path, method)
    if not route:
        return jsonify({"error": "Route not found"}), 404

    target_url, policy_name = route

    if policy_name:
        try:
            policy_code = utils.load_policy_code(policy_name)
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 500

        try:
            utils.exec_policy(policy_code, request, lambda msg: (_ for _ in ()).throw(Exception(msg)))
        except Exception as e:
            return jsonify({"error": str(e)}), 403

    import requests
    response = requests.request(method, target_url, headers=request.headers, data=request.get_data(), params=request.args)
    return (response.content, response.status_code, response.headers.items())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
