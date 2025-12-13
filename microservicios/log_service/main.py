from flask import Flask, request, jsonify
import datetime
import threading
import pulsar
import os

app = Flask(__name__)
logs = []

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://pulsar:6650")
TOPIC = "persistent://public/default/logs"

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

# ----------------------------------------
# Consumer Pulsar
# ----------------------------------------
def pulsar_consumer():
    client = pulsar.Client(PULSAR_URL)
    consumer = client.subscribe(TOPIC, subscription_name="log_service_sub")
    while True:
        msg = consumer.receive()
        try:
            contenido = msg.data().decode('utf-8')
            print(f"[PULSAR LOG] {contenido}")
            logs.append({"mensaje": contenido, "fecha": datetime.datetime.utcnow().isoformat()})
            consumer.acknowledge(msg)
        except Exception as e:
            consumer.negative_acknowledge(msg)
            print(f"Error procesando mensaje: {e}")

threading.Thread(target=pulsar_consumer, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
