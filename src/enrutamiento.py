"""Enrutamiento condicional según la entrada (Bloques 19 y 20).

Un mensaje de soporte se clasifica en pregunta, queja o sugerencia, y una
bifurcación elige la ruta con el prompt adaptado a esa categoría. La ruta
de pregunta es el default: corre ante cualquier categoría no anticipada.

Ejecutar desde la raíz del repositorio:
    python src/enrutamiento.py
"""

import logging

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_google_genai import ChatGoogleGenerativeAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELO = "gemini-3.5-flash-lite"

MENSAJES_DEMO = [
    "¿Cómo cambio mi contraseña?",
    "La app se cierra cada vez que subo una foto.",
    "Estaría bueno que la app tuviera modo oscuro.",
]

respuesta_generica = RunnableLambda(
    lambda x: (
        "Gracias por tu mensaje. Un miembro de nuestro "
        "equipo te va a responder pronto."
    )
)


def limpiar_categoria(texto):
    """Normaliza la categoría antes de comparar (el modelo no siempre
    devuelve minúsculas exactas: puede ser "Queja", "queja." o "Queja \\n")."""
    return texto.strip().lower()


def construir_paso_clasificacion(modelo):
    """Clasifica el mensaje en una palabra: pregunta, queja o sugerencia."""
    plantilla = PromptTemplate.from_template(
        "Clasifica el siguiente mensaje de soporte en una sola "
        "palabra: pregunta, queja o sugerencia. Responde solo "
        "con esa palabra.\n\n{mensaje}"
    )
    return plantilla | modelo | StrOutputParser() | limpiar_categoria


def construir_cadena_pregunta(modelo):
    """Ruta por defecto: responde la pregunta técnica con precisión."""
    plantilla = PromptTemplate.from_template(
        "Responde esta pregunta técnica con precisión:\n\n{mensaje}"
    )
    return plantilla | modelo | StrOutputParser()


def construir_cadena_queja(modelo):
    """Ruta queja: responde con empatía, reconociendo el problema primero."""
    plantilla = PromptTemplate.from_template(
        "Responde a esta queja con empatía, reconociendo el "
        "problema antes de ofrecer una solución:\n\n{mensaje}"
    )
    return plantilla | modelo | StrOutputParser()


def construir_cadena_sugerencia(modelo):
    """Ruta sugerencia: agradece y explica cómo se evaluará."""
    plantilla = PromptTemplate.from_template(
        "Agradece esta sugerencia directamente al usuario y explica cómo "
        "se evaluará dentro del producto. Responde ÚNICAMENTE con la "
        "respuesta al usuario, sin anunciar lo que vas a hacer:\n\n{mensaje}"
    )
    return plantilla | modelo | StrOutputParser()


def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
):
    """Arma la chain con bifurcación, sin ejecutarla todavía.

    Las rutas no recibidas defaultean a RunnablePassthrough: nunca se
    ejecutan si la bifurcación no las elige, así en las pruebas basta
    pasar la ruta que se quiere verificar.
    """
    cadena_queja = cadena_queja or RunnablePassthrough()
    cadena_sugerencia = cadena_sugerencia or RunnablePassthrough()
    cadena_pregunta = cadena_pregunta or RunnablePassthrough()
    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "queja", cadena_queja),
        (lambda x: x["categoria"] == "sugerencia", cadena_sugerencia),
        cadena_pregunta,
    )
    return RunnablePassthrough.assign(categoria=paso_clasificacion) | bifurcacion


def construir_cadena_queja_segura(cadena_queja):
    """Envuelve la ruta queja con un fallback de respuesta razonable."""
    return cadena_queja.with_fallbacks([respuesta_generica])


def procesar_mensaje_seguro(cadena, mensaje):
    """Punto de entrada seguro: ningún fallo deja sin respuesta.

    La cadena entra por parámetro para poder inyectar una falsa en las
    pruebas. El error se registra con logger antes de devolver seguro.
    """
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        logger.error(f"Error procesando mensaje: {error}")
        return (
            "No pudimos procesar tu mensaje en este "
            "momento. Intenta de nuevo más tarde."
        )


if __name__ == "__main__":
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model=MODELO)
    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=construir_paso_clasificacion(modelo),
        cadena_queja=construir_cadena_queja_segura(
            construir_cadena_queja(modelo)
        ),
        cadena_sugerencia=construir_cadena_sugerencia(modelo),
        cadena_pregunta=construir_cadena_pregunta(modelo),
    )

    for mensaje in MENSAJES_DEMO:
        print(procesar_mensaje_seguro(cadena, mensaje))
        print()
