import requests


def obtener_datos(url):
    respuesta = requests.get(url)
    return respuesta.json()


url_rota = "https://esta-direccion-no-existe.ejemplo/datos"

try:
    resultado = obtener_datos(url_rota)
except Exception as error:
    resultado = None
    print("No se pudo completar la petición:", error)
