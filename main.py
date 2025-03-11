from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api", methods=["GET"])
def getData():
    return jsonify({"message": "GET-request"})

@app.route("/api", methods=["POST"])
def createData():
    data = request.get_json() # Получаем данные в формате JSON
    if not data:
        return jsonify({"error":"Invalid JSON"}), 400
    name = data.get('name', 'Unknown')
    return jsonify({"message":f"Hello, {name}! This is POST-request test"}), 201

if __name__ == "__main__":
    app.run(debug=True)
