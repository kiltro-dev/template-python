"""Prueba de consistencia del banco de prompts.

Corre cada prompt del banco varias veces contra la API real, intenta
interpretar cada respuesta como JSON con la estructura esperada, y guarda
el registro de resultados en prompts/registro_resultados.json.

Uso:
  python test_consistencia.py                     # corre todos los prompts
  python test_consistencia.py detectar_idioma     # corre solo ese prompt
  python test_consistencia.py modelo=gemini-3.5-flash   # cambia el modelo
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from consumir_gemini import (  # noqa: E402
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)
from banco import BANCO_DE_PROMPTS  # noqa: E402

INTENTOS_POR_PROMPT = 3
PAUSA_ENTRE_LLAMADAS = 3
MODELO = "gemini-2.5-flash"
RUTA_SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro_resultados.json")


def probar_prompt(prompt, modelo):
    """Corre las repeticiones de un prompt y devuelve el conteo de éxitos."""
    exitos = 0
    fallos_api = []
    fallos_estructura = []
    for intento in range(1, INTENTOS_POR_PROMPT + 1):
        try:
            url, body, headers = armar_peticion(
                prompt["ejemplo_usuario"],
                prompt["system_instruction"],
                prompt.get("response_schema"),
                modelo=modelo,
            )
            respuesta = enviar_peticion(url, body, headers)
            texto = extraer_texto(respuesta)
            datos = parsear_respuesta_json(texto, prompt["claves_esperadas"])
            exitos += 1
            print(f"  intento {intento}: ok -> {datos}")
        except RuntimeError as error:
            fallos_api.append(f"intento {intento}: {error}")
            print(f"  intento {intento} falló (API): {error}")
        except ValueError as error:
            fallos_estructura.append(f"intento {intento}: {error}")
            print(f"  intento {intento} falló (estructura): {error}")
        time.sleep(PAUSA_ENTRE_LLAMADAS)
    return exitos, fallos_api, fallos_estructura


def main():
    modelo = MODELO
    nombres = []
    for argumento in sys.argv[1:]:
        if argumento.startswith("modelo="):
            modelo = argumento.split("=", 1)[1]
        else:
            nombres.append(argumento)

    prompts = [p for p in BANCO_DE_PROMPTS if not nombres or p["nombre"] in nombres]
    if not prompts:
        print(f"No se encontraron prompts para: {nombres}")
        return

    # Se parte del registro ya existente para poder completar corridas parciales.
    registro = {}
    if os.path.exists(RUTA_SALIDA):
        with open(RUTA_SALIDA, encoding="utf-8") as archivo:
            registro = json.load(archivo)

    for prompt in prompts:
        print(f"\n{prompt['nombre']} (modelo: {modelo}):")
        exitos, fallos_api, fallos_estructura = probar_prompt(prompt, modelo)
        print(f"{prompt['nombre']}: {exitos}/{INTENTOS_POR_PROMPT} respuestas válidas")
        registro[prompt["nombre"]] = {
            "modelo": modelo,
            "exitos": exitos,
            "intentos": INTENTOS_POR_PROMPT,
            "fallos_api": fallos_api,
            "fallos_estructura": fallos_estructura,
        }

    with open(RUTA_SALIDA, "w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, indent=2, ensure_ascii=False)
    print(f"\nRegistro guardado en {RUTA_SALIDA}")

    print("\n=== Resumen de consistencia ===")
    for nombre, resultado in registro.items():
        marca = "ok" if resultado["exitos"] == resultado["intentos"] else "AJUSTAR"
        print(f"  {nombre}: {resultado['exitos']}/{resultado['intentos']} [{marca}] ({resultado.get('modelo', 'sin registrar')})")


if __name__ == "__main__":
    main()
