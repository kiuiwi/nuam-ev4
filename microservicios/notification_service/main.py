from flask import Flask, request, jsonify

app = Flask(__name__)

# Lista para almacenar las notificaciones en memoria
notificaciones = []

@app.post("/notify")
def notify():
    usuario = request.json.get("usuario")
    mensaje = request.json.get("mensaje")

    # Guardamos la notificación
    notificaciones.append({
        "usuario": usuario,
        "mensaje": mensaje
    })

    print(f"Notificación a {usuario}: {mensaje}")
    return jsonify({"status": "sent"})

# Nuevo endpoint para ver notificaciones como JSON
@app.get("/notifications")
def get_notifications():
    return jsonify(notificaciones)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002)
