from flask import Flask, jsonify
import requests
import threading
import pulsar
import os
from datetime import datetime, timedelta

app = Flask(__name__)

MINDICADOR = "https://mindicador.cl/api"
PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://pulsar:6650")
TOPIC = "persistent://public/default/indicadores"

# ----------------------------------------
# Función para obtener JSON
# ----------------------------------------
def get_json(url):
    try:
        r = requests.get(url, timeout=4)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

# ----------------------------------------
# Endpoint HTTP
# ----------------------------------------
@app.route("/indicadores", methods=["GET"])
def indicadores():
    data = get_json(MINDICADOR)
    if not data:
        return jsonify({"error": "No se pudo conectar a mindicador"}), 500

    dolar = data.get("dolar", {}).get("valor")
    uf = data.get("uf", {}).get("valor")
    tpm = data.get("tpm", {}).get("valor")

    # Obtener tasas de cambio (USD -> PEN y USD -> COP)
    fx = get_json("https://open.er-api.com/v6/latest/USD")
    pen = None
    cop = None

    if fx:
        usd_to_pen = fx.get("rates", {}).get("PEN")
        usd_to_cop = fx.get("rates", {}).get("COP")

        if dolar and usd_to_pen:
            pen = dolar / usd_to_pen

        if dolar and usd_to_cop:
            cop = dolar / usd_to_cop

    # Histórico del dólar
    historico_dolar = data.get("dolar", {}).get("serie") or []
    if not historico_dolar:
        hoy = datetime.today()
        historico_dolar = [
            {"fecha": (hoy - timedelta(days=i)).strftime("%Y-%m-%d"), "valor": 900 + i*2}
            for i in range(9, -1, -1)
        ]
    else:
        historico_dolar = historico_dolar[:10]

    return jsonify({
        "dolar": dolar,
        "uf": uf,
        "tpm": tpm,
        "clp_pen": pen,
        "clp_cop": cop,
        "historico_dolar": [{"fecha": d["fecha"], "valor": d["valor"]} for d in historico_dolar]
    })

# ----------------------------------------
# Consumer Pulsar
# ----------------------------------------
def pulsar_consumer():
    client = pulsar.Client(PULSAR_URL)
    consumer = client.subscribe(TOPIC, subscription_name="indicadores_service_sub")
    while True:
        msg = consumer.receive()
        try:
            contenido = msg.data().decode('utf-8')
            print(f"[PULSAR INDICADORES] {contenido}")
            consumer.acknowledge(msg)
        except Exception as e:
            consumer.negative_acknowledge(msg)
            print(f"Error procesando mensaje: {e}")

# Ejecutar consumer en hilo
threading.Thread(target=pulsar_consumer, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
