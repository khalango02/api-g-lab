# app.py
from flask import Flask, request, jsonify
import requests

from db import init_db
import services
import utils

app = Flask(__name__)


@app.route('/admin/policies', methods=['POST'])
def create_policy():
    data = request.json
    try:
        policy_id = services.create_policy(data['name'])
        return jsonify({"message": "Policy created successfully", "policy_id": policy_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/admin/routes', methods=['POST'])
def create_route():
    data = request.json
    try:
        services.create_route(data['path'], data['method'], data['target_url'], data.get('policy_id'))
        return jsonify({"message": "Route created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/admin/routes', methods=['GET'])
def list_routes():
    return jsonify(services.list_routes())


@app.route('/admin/routes/<int:route_id>', methods=['PUT'])
def update_route(route_id):
    data = request.json
    try:
        services.update_route(route_id, data['path'], data['method'], data['target_url'], data.get('policy_id'))
        return jsonify({"message": "Route updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/admin/routes/<int:route_id>', methods=['DELETE'])
def delete_route(route_id):
    services.delete_route(route_id)
    return jsonify({"message": "Route deleted successfully"})


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    full_path = '/' + path
    method = request.method.upper()

    route = services.find_route(full_path, method)
    if not route:
        return jsonify({"error": "Route not found"}), 404

    target_url, policy_id = route

    if policy_id:
        policy_name = services.find_policy_name(policy_id)

        try:
            policy_code = utils.load_policy_code(policy_name)
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 500

        try:
            utils.exec_policy(policy_code, request, lambda msg: (_ for _ in ()).throw(Exception(msg)))
        except Exception as e:
            return jsonify({"error": str(e)}), 403

    response = requests.request(method, target_url, headers=request.headers, data=request.get_data(), params=request.args)
    return (response.content, response.status_code, response.headers.items())


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
