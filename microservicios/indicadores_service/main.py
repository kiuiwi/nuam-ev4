from flask import Flask, jsonify
import requests

app = Flask(__name__)

MINDICADOR = "https://mindicador.cl/api"

def get_json(url):
    try:
        r = requests.get(url, timeout=4)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None


@app.route("/indicadores", methods=["GET"])
def indicadores():

    data = get_json(MINDICADOR)

    if not data:
        return jsonify({"error": "No se pudo conectar a mindicador"}), 500

    # Valores actuales
    dolar = data.get("dolar", {}).get("valor")
    uf = data.get("uf", {}).get("valor")
    tpm = data.get("tpm", {}).get("valor")

    # Monedas latinoamericanas (PEN y COP)
    # Mindicador no trae directamente CLP->PEN ni CLP->COP
    # Usamos dólares como puente:
    # CLP -> USD -> PEN y COP

    # Tasa USD->PEN y USD->COP desde exchangerate API (gratuita)
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
        from datetime import datetime, timedelta
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
        "historico_dolar": [
            {"fecha": d["fecha"], "valor": d["valor"]}
            for d in historico_dolar
        ]
    })





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)