"""Compara dos modelos Gemini: latencia, costo, calidad y disponibilidad.

Evidencia para docs/tarea_modulo1_bloque9/decision-arquitectura.md.
Reusa armar_peticion, enviar_peticion, extraer_texto y calcular_costo.
"""

import json
import os
import time

from consumir_gemini import (
    armar_peticion,
    calcular_costo,
    enviar_peticion,
    extraer_texto,
)

MODELO_ECONOMICO = "gemini-2.5-flash"
MODELO_CAPAZ = "gemini-3.6-flash"

# Precios reales por token (USD). Página oficial de precios de Google AI
# (ai.google.dev/gemini-api/docs/pricing), consultada el 2026-10-20.
# Estándar pagado: cotizado por 1M de tokens, convertido a por token (/ 1_000_000).
FECHA_CONSULTA_PRECIOS = "2026-10-20"
PRECIOS = {
    MODELO_ECONOMICO: {
        "precio_entrada": 0.30 / 1_000_000,
        "precio_salida": 2.50 / 1_000_000,
        "fuente": "ai.google.dev/gemini-api/docs/pricing (Standard, USD/1M tokens)",
    },
    MODELO_CAPAZ: {
        "precio_entrada": 0.75 / 1_000_000,
        "precio_salida": 3.75 / 1_000_000,
        "fuente": "ai.google.dev/gemini-api/docs/pricing (Standard, USD/1M tokens, "
        "precio promocional vigente hasta 2026-12-31; duplica desde 2027-01-01)",
    },
}

INTENTOS_LATENCIA = 4
PREGUNTA_LATENCIA = "Confirma en una frase corta que esta conexión funciona"

PREGUNTAS_CALIDAD = [
    "¿Qué es un token en un modelo de lenguaje? Responde en una sola frase.",
    "Explica en dos frases por qué una respuesta larga tarda más en generarse que una corta.",
    "Propón un título corto para una miniaplicación que responde preguntas con IA.",
]


def medir_latencia(modelo):
    """Corre INTENTOS_LATENCIA peticiones y devuelve cada intento y su promedio."""
    intentos = []
    for numero in range(1, INTENTOS_LATENCIA + 1):
        registro = {"intento": numero}
        try:
            url, body, headers = armar_peticion(PREGUNTA_LATENCIA, modelo=modelo)
            inicio = time.perf_counter()
            datos = enviar_peticion(url, body, headers)
            fin = time.perf_counter()
            registro["latencia_segundos"] = fin - inicio
            registro["texto"] = extraer_texto(datos)
            registro["tokens_entrada"] = datos["usageMetadata"]["promptTokenCount"]
            registro["tokens_salida"] = datos["usageMetadata"]["candidatesTokenCount"]
            registro["costo_usd"] = calcular_costo(
                datos,
                PRECIOS[modelo]["precio_entrada"],
                PRECIOS[modelo]["precio_salida"],
            )
            registro["estado"] = "ok"
            print(f"  Intento {numero}: {registro['latencia_segundos']:.2f} segundos")
        except Exception as error:
            registro["estado"] = "fallido"
            registro["error"] = f"{type(error).__name__}: {error}"
            print(f"  Intento {numero}: FALLIDO ({registro['error']})")
        intentos.append(registro)

    exitosos = [i["latencia_segundos"] for i in intentos if i["estado"] == "ok"]
    promedio = sum(exitosos) / len(exitosos) if exitosos else None
    return intentos, promedio


def evaluar_calidad(modelo):
    """Responde las preguntas de calidad y guarda cada respuesta."""
    resultados = []
    for pregunta in PREGUNTAS_CALIDAD:
        registro = {"pregunta": pregunta}
        try:
            url, body, headers = armar_peticion(pregunta, modelo=modelo)
            datos = enviar_peticion(url, body, headers)
            registro["respuesta"] = extraer_texto(datos)
            registro["estado"] = "ok"
        except Exception as error:
            registro["respuesta"] = None
            registro["estado"] = "fallido"
            registro["error"] = f"{type(error).__name__}: {error}"
        resultados.append(registro)
    return resultados


def resumir_disponibilidad(intentos):
    """Cuenta intentos fallidos y agrupa sus causas (p.ej. 503, 429)."""
    fallidos = [i for i in intentos if i["estado"] == "fallido"]
    causas = {}
    for intento in fallidos:
        causa = intento.get("error", "desconocida")
        # Agrupa por el mensaje corto del servicio: "503 UNAVAILABLE", "429 ..." etc.
        clave = causa.split("):")[0] if "):" in causa else causa
        causas[clave] = causas.get(clave, 0) + 1
    return {
        "intentos_totales": len(intentos),
        "intentos_fallidos": len(fallidos),
        "causas": causas,
    }


def comparar():
    evidencia = {
        "fecha_medicion": time.strftime("%Y-%m-%d"),
        "fecha_consulta_precios": FECHA_CONSULTA_PRECIOS,
        "pregunta_latencia": PREGUNTA_LATENCIA,
        "intentos_por_modelo": INTENTOS_LATENCIA,
        "modelos": {},
    }

    for modelo in (MODELO_ECONOMICO, MODELO_CAPAZ):
        print(f"\n=== {modelo} ===")
        print(f"Latencia ({INTENTOS_LATENCIA} intentos):")
        intentos, promedio = medir_latencia(modelo)
        if promedio:
            print(f"  Latencia promedio: {promedio:.2f} segundos")
        else:
            print("  Sin intentos exitosos")
        print("Calidad:")
        calidad = evaluar_calidad(modelo)
        for registro in calidad:
            print(f"  [{registro['estado']}] {registro['pregunta'][:50]}...")

        disponibilidad = resumir_disponibilidad(intentos + calidad)
        fallidos = disponibilidad["intentos_fallidos"]
        total = disponibilidad["intentos_totales"]
        print(f"Disponibilidad: {total - fallidos}/{total} intentos ok", end="")
        if fallidos:
            print(f" | fallidos: {disponibilidad['causas']}")
        else:
            print()

        evidencia["modelos"][modelo] = {
            "precios_por_token_usd": {
                "entrada": PRECIOS[modelo]["precio_entrada"],
                "salida": PRECIOS[modelo]["precio_salida"],
                "fuente": PRECIOS[modelo]["fuente"],
            },
            "latencia": {
                "intentos": intentos,
                "promedio_segundos": promedio,
            },
            "calidad": calidad,
            "disponibilidad": disponibilidad,
        }

    ruta_salida = os.path.join(
        os.path.dirname(__file__),
        "..",
        "docs",
        "tarea_modulo1_bloque9",
        "comparativa_modelos.json",
    )
    ruta_salida = os.path.normpath(ruta_salida)
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    with open(ruta_salida, "w") as archivo:
        json.dump(evidencia, archivo, indent=2, ensure_ascii=False)
    print(f"\nEvidencia guardada en {ruta_salida}")
    return evidencia


if __name__ == "__main__":
    comparar()
