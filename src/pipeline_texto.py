"""Pipeline de limpieza y tokenización de texto (Bloque 15, U2.2).

Prepara texto para medición: normaliza (limpiar_texto), parte en unidades
(tokenizar) y junta ambos pasos en un único punto de entrada
(procesar_texto), para que ninguna métrica mida texto crudo por accidente.

Uso:
  from pipeline_texto import procesar_texto
  tokens = procesar_texto("El Cielo, es AZUL!")
"""

import re

from cliente import consultar_modelo


def limpiar_texto(texto: str) -> str:
    """Normaliza el texto: minúsculas y sin puntuación."""
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera str, no {tipo}")

    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokenizar(texto_limpio: str) -> list[str]:
    """Convierte texto limpio en una lista de tokens."""
    return texto_limpio.split()


def procesar_texto(texto: str) -> list[str]:
    """Limpia y tokeniza en un solo paso: la entrada de toda métrica."""
    texto_limpio = limpiar_texto(texto)
    return tokenizar(texto_limpio)


if __name__ == "__main__":
    # Actividad del Bloque 15: tres respuestas reales de consultar_modelo
    # contra referencias propias, con registro del antes (crudo) y el
    # después (procesado) como evidencia de que el pipeline cambia el resultado.
    casos = [
        ("¿Qué es Python?", "Python es un lenguaje de programación interpretado."),
        ("¿Cuál es la capital de Chile?", "Santiago es la capital de Chile."),
        ("¿De qué color es el cielo?", "El cielo es azul."),
    ]

    for i, (consulta, referencia) in enumerate(casos, start=1):
        respuesta = consultar_modelo(consulta)

        crudo_ref = referencia.split()
        crudo_resp = respuesta.split()
        comunes_crudo = set(crudo_ref) & set(crudo_resp)
        pct_crudo = len(comunes_crudo) / len(set(crudo_ref))

        tokens_ref = procesar_texto(referencia)
        tokens_resp = procesar_texto(respuesta)
        comunes = set(tokens_ref) & set(tokens_resp)
        pct_proc = len(comunes) / len(set(tokens_ref))

        print(f"[Caso {i}] Coincidencia texto crudo: {pct_crudo:.1%}")
        print(f"[Caso {i}] Coincidencia texto procesado: {pct_proc:.1%}")
