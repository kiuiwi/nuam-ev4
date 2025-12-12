import requests
from django.conf import settings

def obtener_indicadores_service():
    url = f"{settings.MICROSERVICES['indicadores']}/indicadores"
    try:
        resp = requests.get(url, timeout=3)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def enviar_log(mensaje):
    url = f"{settings.MICROSERVICES['logs']}/log"
    try:
        requests.post(url, json={"mensaje": mensaje}, timeout=3)
    except:
        pass  # No bloquear por errores

def enviar_notificacion(usuario, mensaje):
    url = f"{settings.MICROSERVICES['notificaciones']}/notify"
    try:
        requests.post(url, json={"usuario": usuario, "mensaje": mensaje}, timeout=3)
    except:
        pass
