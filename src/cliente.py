"""Cliente modular de consumo de la API de Gemini (Bloques 12-13, Módulo 2).

Único punto de entrada: consultar_modelo. Detrás quedan escondidos:
- clasificación de errores: ValueError = credencial (no se reintenta),
  TimeoutError = temporal / límite de uso (sí se reintenta);
- con_reintento: reintenta con backoff exponencial (espera que crece, con
  tope y jitter) cuando el error lo justifica;
- registrar_costo: costo de cada operación y acumulado de la sesión.

Uso:
  from cliente import consultar_modelo
  respuesta = consultar_modelo("¿Cuál es la capital de Chile?")
"""

import random
import time
from typing import Any, Callable

import requests

from consumir_gemini import (
    armar_peticion,
    calcular_costo,
    extraer_texto,
)

# Precios reales por token (USD). Página oficial de precios de Google AI
# (ai.google.dev/gemini-api/docs/pricing), consultada el 2026-10-20.
# Cotizado por 1M de tokens, convertido a por token (/ 1_000_000).
PRECIOS = {
    "gemini-2.5-flash": {"entrada": 0.30 / 1_000_000, "salida": 2.50 / 1_000_000},
    "gemini-3.6-flash": {"entrada": 0.75 / 1_000_000, "salida": 3.75 / 1_000_000},
}

costo_total_sesion = 0.0


def enviar_peticion(url, body, headers):
    """Copia de consumir_gemini.enviar_peticion (el curso pide el cliente
    autocontenido en un solo archivo). Clasificación de errores del Bloque 12:
    ValueError = credencial, no se reintenta; TimeoutError = temporal, sí."""
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
    if (
        codigo_http in (401, 403)
        or codigo in (401, 403)
        or estado in ("UNAUTHENTICATED", "PERMISSION_DENIED")
        # Una API key inválida llega como 400 INVALID_ARGUMENT ("API key not valid"),
        # no como 401/403: se detecta por el mensaje del sobre de error.
        or (codigo_http == 400 and "api key" in mensaje.lower())
    ):
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


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            espera = min(espera_base * (2 ** (intento - 1)), espera_maxima)
            espera_con_jitter = espera + random.uniform(0, espera * 0.1)
            print(f"Intento {intento} de {intentos} falló. Reintentando en {espera_con_jitter:.1f}s...")
            time.sleep(espera_con_jitter)


def registrar_costo(respuesta: dict, precio_entrada: float, precio_salida: float) -> float:
    """Registra el costo de una operación exitosa y lo acumula en la sesión.

    Se llama solo después de confirmar que la respuesta llegó con éxito:
    una respuesta de error no trae usageMetadata.
    """
    global costo_total_sesion
    costo = calcular_costo(respuesta, precio_entrada, precio_salida)
    costo_total_sesion += costo
    uso = respuesta["usageMetadata"]
    print(
        f"Operación: {uso['promptTokenCount']} tokens de entrada + "
        f"{uso['candidatesTokenCount']} de salida -> ${costo:.6f} USD "
        f"(acumulado: ${costo_total_sesion:.6f} USD)"
    )
    return costo


def consultar_modelo(pregunta: str, system_instruction: str = "", modelo: str = "gemini-2.5-flash") -> str:
    precios = PRECIOS.get(modelo)
    if precios is None:
        raise ValueError(
            f"No hay precios registrados para {modelo}. "
            "Confírmalos en la página oficial y agrégalo en PRECIOS."
        )
    url, body, headers = armar_peticion(pregunta, system_instruction or None, modelo=modelo)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(url, body, headers))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    registrar_costo(respuesta, precios["entrada"], precios["salida"])
    return extraer_texto(respuesta)


if __name__ == "__main__":
    # Ensayo de rate limit (Bloque 13): provocar un 429 real a propósito.
    # gemini-3.6-flash tiene cupos más bajos que el modelo por defecto y
    # frena antes con ráfagas seguidas; por eso el ensayo fuerza ese modelo.
    for i in range(10):
        try:
            respuesta = consultar_modelo(f"Pregunta de prueba número {i}", modelo="gemini-3.6-flash")
            print(f"Respuesta {i}: {respuesta[:40]}...")
        except ValueError as error:
            # ValueError no es rate limit: es credencial o configuración.
            print(f"Error de configuración (no es rate limit): {error}")
            break
        except RuntimeError as error:
            print(f"Respuesta {i} falló definitivamente: {error}")

    print(f"Costo total del ensayo: ${costo_total_sesion:.6f} USD")
