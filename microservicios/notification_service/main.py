from flask import Flask, request, jsonify
import threading
import pulsar
import os

app = Flask(__name__)
notificaciones = []

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://pulsar:6650")
TOPIC = "persistent://public/default/notifications"

@app.post("/notify")
def notify():
    usuario = request.json.get("usuario")
    mensaje = request.json.get("mensaje")

    notificaciones.append({
        "usuario": usuario,
        "mensaje": mensaje
    })

    print(f"Notificación a {usuario}: {mensaje}")
    return jsonify({"status": "sent"})

@app.get("/notifications")
def get_notifications():
    return jsonify(notificaciones)

# ----------------------------------------
# Consumer Pulsar
# ----------------------------------------
def pulsar_consumer():
    client = pulsar.Client(PULSAR_URL)
    consumer = client.subscribe(TOPIC, subscription_name="notification_service_sub")
    while True:
        msg = consumer.receive()
        try:
            contenido = msg.data().decode('utf-8')
            print(f"[PULSAR NOTIFICACION] {contenido}")
            notificaciones.append({"usuario": "admin", "mensaje": contenido})
            consumer.acknowledge(msg)
        except Exception as e:
            consumer.negative_acknowledge(msg)
            print(f"Error procesando mensaje: {e}")

threading.Thread(target=pulsar_consumer, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002)
