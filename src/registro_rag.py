"""Instrumentación de latencia y costo del flujo RAG (Bloque 28, core U2.5).

Corre consultas RAG reales midiendo tiempo por etapa (embed+busqueda y
generacion) y tokens reales (usage_metadata), y agrega una línea JSON por
corrida a registros_latencia_costo.jsonl para comparar a futuro.

Ejecutar desde la raíz del repositorio, con el entorno virtual activo:
    python src/registro_rag.py
"""

import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

MODELO_EMBEDDINGS = "models/gemini-embedding-001"
MODELO_CHAT = "gemini-3.5-flash-lite"  # decisión vigente del repo (la lección usa 2.0-flash)
DIR_VECTORSTORE = "vectorstore/"
ARCHIVO_REGISTROS = "registros_latencia_costo.jsonl"

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


def formatear_contexto(chunks_recuperados):
    lineas = []
    for i, doc in enumerate(chunks_recuperados, start=1):
        lineas.append(f"[{i}] {doc.page_content}")
    return "\n\n".join(lineas)


@contextmanager
def medir(tiempos, etapa):
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio


def registrar_consulta(pregunta, persist_directory, k=3):
    """Corre una consulta RAG real, midiendo tiempo por etapa y tokens reales
    de la respuesta del modelo."""
    tiempos = {}

    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)
    chat_model = ChatGoogleGenerativeAI(model=MODELO_CHAT)

    with medir(tiempos, "embed_y_busqueda"):
        vectorstore = Chroma(
            persist_directory=persist_directory, embedding_function=embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        chunks = retriever.invoke(pregunta)

    contexto = formatear_contexto(chunks)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

    with medir(tiempos, "generacion"):
        respuesta = chat_model.invoke(prompt)

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "tiempos_ms": {etapa: round(s * 1000, 2) for etapa, s in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "tokens": dict(respuesta.usage_metadata) if respuesta.usage_metadata else None,
    }
    return registro


if __name__ == "__main__":
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit(
            'Falta GEMINI_API_KEY. Defínela en tu archivo ".env" '
            "y vuelve a ejecutar."
        )

    preguntas = [
        "que hace el cliente si una llamada tarda demasiado",
        "como se calcula el costo de una llamada",
        "que protege el flujo completo si falla un paso",
    ]
    for pregunta in preguntas:
        registro = registrar_consulta(pregunta, DIR_VECTORSTORE)
        print(json.dumps(registro, indent=2, ensure_ascii=False))

        with open(ARCHIVO_REGISTROS, "a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    print(f"Registros agregados a {ARCHIVO_REGISTROS}")
