from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/endpoint-real', methods=['GET'])
def minha_api():
    return jsonify({"message": "OK"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
