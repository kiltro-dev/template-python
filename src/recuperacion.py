"""Recuperación semántica y prompt dinámico con citas (Bloque 26).

Reconecta al índice persistido (sin reindexar), recupera los k chunks más
relevantes para una pregunta y arma un prompt que obliga al modelo a citar
sus fuentes y a admitir cuando el contexto no alcanza.

Ejecutar desde la raíz del repositorio, con el entorno virtual activo:
    python src/recuperacion.py
"""

import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

MODELO_EMBEDDINGS = "models/gemini-embedding-001"
DIR_VECTORSTORE = "vectorstore/"

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


def formatear_contexto(chunks_recuperados):
    """Arma un bloque de contexto numerado para el prompt, y un mapa
    numero -> fuente para reconstruir la cita despues."""
    lineas = []
    citas = {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        fuente = doc.metadata.get("fuente", "desconocida")
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = fuente
    contexto = "\n\n".join(lineas)
    return contexto, citas


def construir_prompt(pregunta, persist_directory, k=3):
    """Recupera los k chunks mas relevantes para la pregunta y arma el prompt
    dinamico con contexto numerado, listo para pasarle al modelo."""
    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    chunks_recuperados = retriever.invoke(pregunta)
    contexto, citas = formatear_contexto(chunks_recuperados)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)
    return prompt, citas


if __name__ == "__main__":
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit(
            'Falta GEMINI_API_KEY. Defínela en tu archivo ".env" '
            "y vuelve a ejecutar."
        )

    for pregunta in [
        "que pasa si mi conexion tarda demasiado",
        "como decide el agente que herramienta usar",
    ]:
        prompt, citas = construir_prompt(pregunta, DIR_VECTORSTORE)
        print(prompt)
        print(citas)
        print("=" * 60)
