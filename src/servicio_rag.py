"""Servicio RAG integrado del Gate 2 (Bloque S1).

Reutiliza los módulos propios: índice persistido (Bloque 24/26), filtro de
inyección y logging con trace_id (Bloque 31), citas por fuente y punto de
supervisión humana (Bloque 32). Responde {trace_id, respuesta, fuentes,
auditoria} y devuelve SIN_CONTEXTO si todo lo recuperado se descarta.

Ejecutar desde la raíz del repositorio, con el entorno virtual activo:
    python src/servicio_rag.py
"""

import json
import os
import sys
import uuid

sys.path.insert(0, "src")  # se corre siempre desde la raíz del repo

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langgraph.types import Command

from grafo_supervision import app_despliegue
from logging_rag import (
    filtrar_documentos_sospechosos,
    logger,
    registrar_consumo,
    trace_id_var,
)

MODELO_EMBEDDINGS = "models/gemini-embedding-001"
MODELO_CHAT = "gemini-3.5-flash-lite"
DIR_VECTORSTORE = "vectorstore/"
HUELLA_PROMPT_V2 = "da42e8cb229b"  # v2 real de src/registro_prompts.py
SIN_CONTEXTO = "No tengo informacion suficiente y verificada para responder esto."

PROMPT_SERVICIO = """Responde la pregunta usando SOLO el contexto de abajo. Cita cada
afirmacion con su fuente entre corchetes, como [doc0.md]. Si el contexto no
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


def texto_plano(salida):
    """Extrae texto de output (str o lista de bloques de contenido)."""
    if isinstance(salida, str):
        return salida
    return "".join(
        b.get("text", "") for b in salida
        if isinstance(b, dict) and b.get("type") == "text"
    )


def cargar_indice():
    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)
    vectorstore = Chroma(
        persist_directory=DIR_VECTORSTORE, embedding_function=embeddings
    )
    if not vectorstore.get()["ids"]:
        raise SystemExit(
            f"{DIR_VECTORSTORE} está vacío: corre python src/indexar_corpus.py primero."
        )
    return vectorstore, "indice_reutilizado"


def responder(pregunta, vectorstore, estado_indice, k=3):
    token = trace_id_var.set("trace-" + uuid.uuid4().hex[:8])
    auditoria = []
    try:
        auditoria.append({"evento": "consulta_recibida"})
        logger.info("consulta recibida", extra={"extra_data": {
            "evento": "consulta_recibida", "pregunta_len": len(pregunta),
        }})
        auditoria.append({"evento": estado_indice})
        logger.info(estado_indice, extra={"extra_data": {
            "evento": estado_indice,
        }})
        documentos = vectorstore.as_retriever(search_kwargs={"k": k}).invoke(pregunta)
        auditoria.append({"evento": "documentos_recuperados", "n": len(documentos)})
        logger.info("documentos recuperados", extra={"extra_data": {
            "evento": "documentos_recuperados", "n": len(documentos),
        }})
        limpios, descartados = filtrar_documentos_sospechosos(documentos)
        if descartados:
            auditoria.append({"evento": "documentos_descartados", "n": len(descartados)})
        if not limpios:
            auditoria.append({
                "evento": "sin_contexto_confiable",
                "n_recuperados": len(documentos),
                "n_descartados": len(descartados),
            })
            logger.warning("sin contexto confiable", extra={"extra_data": {
                "evento": "sin_contexto_confiable",
                "n_recuperados": len(documentos),
                "n_descartados": len(descartados),
            }})
            return {"trace_id": trace_id_var.get(), "respuesta": SIN_CONTEXTO,
                    "fuentes": [], "auditoria": auditoria}
        contexto = "\n\n".join(
            f"[{d.metadata.get('fuente', 'desconocida')}] {d.page_content}"
            for d in limpios
        )
        respuesta = ChatGoogleGenerativeAI(model=MODELO_CHAT).invoke(
            PROMPT_SERVICIO.format(contexto=contexto, pregunta=pregunta)
        )
        registrar_consumo(respuesta)
        uso = respuesta.usage_metadata or {}
        auditoria.append({
            "evento": "consumo_llm",
            "input_tokens": uso.get("input_tokens"),
            "output_tokens": uso.get("output_tokens"),
        })
        return {"trace_id": trace_id_var.get(),
                "respuesta": texto_plano(respuesta.content),
                "fuentes": sorted({d.metadata.get("fuente", "desconocida")
                                   for d in limpios}),
                "auditoria": auditoria}
    finally:
        trace_id_var.reset(token)


def main():
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit(
            'Falta GEMINI_API_KEY. Defínela en tu archivo ".env" '
            "y vuelve a ejecutar."
        )
    vectorstore, estado_indice = cargar_indice()
    respuesta = responder(
        "que hace el cliente si una llamada tarda demasiado",
        vectorstore, estado_indice,
    )
    print("--- respuesta completa del servicio ---")
    print(json.dumps(respuesta, ensure_ascii=False, indent=2))
    assert respuesta["fuentes"], "la respuesta debe citar al menos una fuente"

    print("--- punto de supervision humana ---")
    config = {"configurable": {"thread_id": "gate2-despliegue-1"}}
    pausado = app_despliegue.invoke(
        {"huella_nueva": HUELLA_PROMPT_V2, "aprobado": False}, config=config
    )
    assert "__interrupt__" in pausado, "el grafo debe pausarse en supervision"
    print("pausado, pendiente:", pausado["__interrupt__"][0].value)
    final = app_despliegue.invoke(Command(resume=True), config=config)
    print("estado final:", final)
    print("Proceso terminado sin errores.")


if __name__ == "__main__":
    main()
