from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

logs = []

@app.post("/log")
def registrar_log():
    entry = {
        "mensaje": request.json.get("mensaje"),
        "fecha": datetime.datetime.utcnow().isoformat()
    }
    logs.append(entry)
    return jsonify({"status": "ok"})

@app.get("/logs")
def listar_logs():
    return jsonify(logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
