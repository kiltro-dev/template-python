import json
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

def armar_peticion(pregunta, system_instruction=None, response_schema=None, modelo="gemini-2.5-flash"):
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía")
    if system_instruction is not None and not system_instruction.strip():
        raise ValueError("El system_instruction no puede estar vacío")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        raise RuntimeError("Falta la variable GEMINI_API_KEY en el archivo .env")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    headers = {"x-goog-api-key": api_key}
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    if system_instruction is not None:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }
    return url, body, headers

def enviar_peticion(url, body, headers):
    try:
        respuesta = requests.post(url, headers=headers, json=body, timeout=10)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise TimeoutError("No se pudo contactar al proveedor. Puede ser momentáneo.")
    try:
        datos = respuesta.json()
    except requests.exceptions.JSONDecodeError:
        datos = None
    codigo_http = respuesta.status_code
    error_api = datos.get("error", {}) if isinstance(datos, dict) else {}
    codigo = error_api.get("code", codigo_http)
    estado = error_api.get("status", "")
    mensaje = error_api.get("message", "")
    # Clasificación (Bloque 12): ValueError = credencial, no se reintenta;
    # TimeoutError = temporal (límite de uso o falla del proveedor), sí se reintenta.
    if (
        codigo_http in (401, 403)
        or codigo in (401, 403)
        or estado in ("UNAUTHENTICATED", "PERMISSION_DENIED")
        # Una API key inválida llega como 400 INVALID_ARGUMENT ("API key not valid"),
        # no como 401/403: se detecta por el mensaje del sobre de error.
       # or (codigo_http == 400 and "api key" in mensaje.lower())
    ):
        print(codigo)
        raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.")
    if (
        codigo_http == 429
        or codigo_http >= 500
        or codigo == 429
        or codigo >= 500
        or estado in ("RESOURCE_EXHAUSTED", "UNAVAILABLE")
    ):
        raise TimeoutError("El proveedor no pudo procesar la petición. Hay que esperar y reintentar.")
    if datos is None:
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


def parsear_respuesta_json(texto, claves_esperadas):
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)
    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido.")
    if not isinstance(datos, dict):
        raise ValueError("La respuesta JSON no es un objeto con claves.")
    faltantes = [clave for clave in claves_esperadas if clave not in datos]
    if faltantes:
        raise ValueError(f"La respuesta no tiene la estructura esperada. Faltan claves: {faltantes}")
    return datos


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
