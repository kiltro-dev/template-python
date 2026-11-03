"""Chain de tres pasos con LangChain (Bloque 18, actividad core).

Caso: un mensaje de soporte se clasifica por tema, se redacta una
respuesta según esa clasificación y se revisa el tono antes de entregarla.

Ejecutar desde la raíz del repositorio:
    python src/cadena_tres_pasos.py
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

MODELO = "gemini-3.5-flash-lite"

MENSAJE_REAL = (
    "Llevo dos semanas esperando mi pedido número 4521 y nadie responde "
    "mis correos. Quiero una solución hoy mismo."
)


def envolver_clasificacion(clasificacion):
    """Adapta la salida del paso 1 al dict que espera la plantilla del paso 2."""
    return {"clasificacion": clasificacion}


def envolver_borrador(borrador):
    """Adapta la salida del paso 2 al dict que espera la plantilla del paso 3."""
    return {"borrador": borrador}


def construir_paso_clasificacion(modelo):
    """Paso 1: clasifica el mensaje en reclamo, consulta o sugerencia."""
    plantilla = PromptTemplate.from_template(
        "Clasifica el siguiente mensaje de soporte en UNA de estas categorías: "
        "reclamo, consulta o sugerencia. Responde SOLO la categoría, "
        "sin explicación:\n\n{mensaje}"
    )
    return plantilla | modelo | StrOutputParser()


def construir_paso_redaccion(modelo):
    """Paso 2: redacta una respuesta breve según la clasificación recibida."""
    plantilla = PromptTemplate.from_template(
        "Redacta una respuesta de soporte breve (máximo 3 frases) para un "
        "cliente cuyo mensaje fue clasificado como {clasificacion}. Usa tono "
        "empático y ofrece un siguiente paso concreto."
    )
    return plantilla | modelo | StrOutputParser()


def construir_paso_revision(modelo):
    """Paso 3: revisa el tono del borrador y lo corrige si hace falta."""
    plantilla = PromptTemplate.from_template(
        "Toma esta respuesta de soporte y devuélvela con tono profesional "
        "y empático, sin agregar información nueva. Responde ÚNICAMENTE con "
        "la respuesta final, sin comentarios ni explicaciones sobre ella:\n\n{borrador}"
    )
    return plantilla | modelo | StrOutputParser()


def construir_cadena(modelo):
    """Arma y devuelve la chain completa, sin ejecutarla todavía.

    El modelo entra por parámetro para poder inyectar un mock en las
    pruebas (tests/test_cadena_tres_pasos.py).
    """
    return (
        construir_paso_clasificacion(modelo)
        | envolver_clasificacion
        | construir_paso_redaccion(modelo)
        | envolver_borrador
        | construir_paso_revision(modelo)
    )


if __name__ == "__main__":
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model=MODELO)
    cadena = construir_cadena(modelo)

    resultado = cadena.invoke({"mensaje": MENSAJE_REAL})
    print(resultado)
