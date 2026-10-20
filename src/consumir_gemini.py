import os
import requests
from dotenv import load_dotenv

load_dotenv()

def armar_peticion(pregunta, modelo="gemini-2.5-flash"):
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        raise RuntimeError("Falta la variable GEMINI_API_KEY en el archivo .env")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    headers = {"x-goog-api-key": api_key}
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    return url, body, headers

def enviar_peticion(url, body, headers):
    try:
        respuesta = requests.post(url, headers=headers, json=body)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
    try:
        datos = respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")
    if not isinstance(datos, dict):
        raise RuntimeError(f"La respuesta del servicio no es un objeto JSON: {str(datos)[:200]}")
    if "error" in datos:
        detalle = datos["error"]
        codigo = detalle.get("code", "?")
        mensaje = detalle.get("message", "sin detalle")
        estado = detalle.get("status", "")
        raise RuntimeError(f"El servicio rechazó la petición ({codigo} {estado}): {mensaje}")
    if "candidates" not in datos:
        raise RuntimeError(
            "La respuesta no trae el bloque 'candidates' que se esperaba. "
            f"Contenido recibido: {str(datos)[:300]}"
        )
    return datos

def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


def calcular_costo(datos, precio_entrada, precio_salida):
    try:
        uso = datos["usageMetadata"]
        tokens_entrada = uso["promptTokenCount"]
        tokens_salida = uso["candidatesTokenCount"]
    except (KeyError, TypeError):
        raise RuntimeError("La respuesta no trae el uso de tokens en el lugar esperado.")
    return (tokens_entrada * precio_entrada) + (tokens_salida * precio_salida)


def obtener_dato_de_prueba(pregunta):
    url, body, headers = armar_peticion(pregunta)
    datos = enviar_peticion(url, body, headers)
    return extraer_texto(datos)


if __name__ == "__main__":
    pregunta = "Confirma en una frase corta que esta conexión funciona"
    try:
        resultado = obtener_dato_de_prueba(pregunta)
        print(resultado)
    except (ValueError, RuntimeError) as error:
        print(f"[ERROR] No se pudo completar la operación: {type(error).__name__}: {error}")
