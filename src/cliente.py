"""Cliente modular de consumo de la API de Gemini (Bloque 12, Módulo 2).

Une las dos piezas del bloque detrás de un único punto de entrada:
- clasificación de errores: ValueError = credencial (no se reintenta),
  TimeoutError = temporal / límite de uso (sí se reintenta);
- con_reintento: repite la operación cuando el error lo justifica.

Uso:
  from cliente import consultar_modelo
  respuesta = consultar_modelo("¿Cuál es la capital de Chile?")
"""

import time
from typing import Any, Callable

from consumir_gemini import armar_peticion, enviar_peticion, extraer_texto


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: int = 2,
) -> Any:
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            print(f"Intento {intento} de {intentos} falló por límite de uso. Reintentando...")
            time.sleep(espera_segundos)


def consultar_modelo(pregunta: str, system_instruction: str = "") -> str:
    url, body, headers = armar_peticion(pregunta, system_instruction or None)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(url, body, headers))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    return extraer_texto(respuesta)


if __name__ == "__main__":
    try:
        respuesta = consultar_modelo("¿Cuál es la capital de Chile?")
        print(respuesta)
    except ValueError as error:
        print(f"Error de configuración: {error}")
    except RuntimeError as error:
        print(f"El servicio no respondió tras varios intentos: {error}")
