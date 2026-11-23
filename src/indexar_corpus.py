"""Indexación del corpus con chunking, embeddings y persistencia en Chroma (Bloques 24 y 26).

Corpus propio sobre la miniaplicación (errores, costo, agente, pruebas y
chains), partido con chunking recursivo, indexado con embeddings reales de
Gemini y persistido en disco para consultas sin re-indexar. Desde el Bloque 26
cada chunk lleva metadata (fuente) e id predecible para citas y evaluación.

Ejecutar desde la raíz del repositorio, con el entorno virtual activo:
    python src/indexar_corpus.py
"""

import os
import sys

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

MODELO_EMBEDDINGS = "models/gemini-embedding-001"
CHUNK_SIZE = 200
CHUNK_OVERLAP = 30
DIR_VECTORSTORE = "vectorstore/"


def construir_corpus():
    """Documentos propios y relacionados: la miniaplicación de este repo."""
    return [
        "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera "
        "exponencial con techo de 30 segundos y jitter del 10%.",
        "Los errores de autenticación nunca se reintentan: una credencial "
        "inválida falla de inmediato con ValueError, sin ninguna espera.",
        "El costo de cada llamada se calcula desde usageMetadata (tokens de "
        "entrada y salida) con los precios vigentes, y se acumula en "
        "costo_total_sesion.",
        "El agente de soporte postventa decide por sí mismo qué herramienta "
        "usar según la descripción de cada una: consultar_estado_pedido para "
        "ubicar pedidos, calcular_reembolso para montos según días de uso, "
        "y generar_reembolso para reembolsos reales. Cada vuelta del ciclo "
        "razonar-actuar-observar es una llamada al modelo, y la traza "
        "programática permite verificar qué herramienta eligió en cada caso.",
        "Las pruebas unitarias del cliente usan mocks para el modelo y la "
        "clasificación, de forma que la suite completa de 30 pruebas corre "
        "en menos de un segundo sin gastar tokens ni depender de la red.",
        "Las chains de LangChain encadenan plantillas, modelo y parser con "
        "el operador |, donde la salida de un paso alimenta la entrada del "
        "siguiente. El enrutamiento condicional clasifica cada mensaje y "
        "elige una ruta con RunnableBranch, mientras que cada ruta de "
        "destino lleva su propio fallback y un try/except general protege "
        "el flujo completo.",
    ]


def construir_splitter():
    """Recursivo: respeta párrafos y oraciones; overlap ~15% del tamaño."""
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )


def construir_metadatas(corpus):
    """Una fuente por documento, en la misma posición (el splitter la
    propaga a cada chunk que salga de ese documento)."""
    return [{"fuente": f"doc{i}.md"} for i in range(len(corpus))]


def indexar_corpus(corpus, splitter, embeddings, persist_directory):
    """Parte documento por documento (para ids trazables), calcula un
    embedding por chunk y persiste con metadata e ids (sin ejecutar nada
    fuera de esta llamada: recibe splitter y embeddings inyectados)."""
    metadatas = construir_metadatas(corpus)
    chunks = []
    ids = []
    for i, documento in enumerate(corpus):
        subchunks = splitter.create_documents(
            [documento], metadatas=[metadatas[i]]
        )
        for j, chunk in enumerate(subchunks):
            chunks.append(chunk)
            ids.append(f"doc{i}" if len(subchunks) == 1 else f"doc{i}_c{j}")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        ids=ids,
        persist_directory=persist_directory,
    )
    return vectorstore, len(chunks)


if __name__ == "__main__":
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit(
            'Falta GEMINI_API_KEY. Defínela en tu archivo ".env" '
            "y vuelve a ejecutar."
        )

    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)
    try:
        _, total = indexar_corpus(
            construir_corpus(),
            construir_splitter(),
            embeddings,
            DIR_VECTORSTORE,
        )
    except Exception as error:
        mensaje = str(error)
        if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
            print("Límite de peticiones alcanzado. Espera un minuto y vuelve a ejecutar.")
        elif "API key" in mensaje or "401" in mensaje or "403" in mensaje:
            print('La API rechazó tu clave. Revisa el valor de GEMINI_API_KEY en tu ".env".')
        else:
            print("No se pudo indexar el corpus:", type(error).__name__)
        print("Detalle técnico:", mensaje)
        raise SystemExit(1)

    print(f"Indexados {total} chunks en {DIR_VECTORSTORE} (con metadata e ids)")
