"""Evaluación de la recuperación: precisión y recall (Bloque 27).

Corre un conjunto de preguntas etiquetadas a mano contra el retriever real
y promedia precisión y recall, guardando el registro para comparar futuras
corridas. Etiquetado hecho leyendo el corpus, antes de ver al retriever.

Ejecutar desde la raíz del repositorio, con el entorno virtual activo:
    python src/evaluacion_recuperacion.py
"""

import os
from datetime import date

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

MODELO_EMBEDDINGS = "models/gemini-embedding-001"
DIR_VECTORSTORE = "vectorstore/"
K = 3  # cuantos chunks recupera el retriever y cuantos evalua la funcion

# Conjunto de evaluación: 11 preguntas, ids etiquetados leyendo el corpus.
# Incluye un caso multi-relevante (herramientas del agente), uno de dos
# chunks encadenados (verificación) y uno sin respuesta (vacaciones).
casos_evaluacion = [
    {"pregunta": "que hace el cliente si una llamada tarda demasiado",
     "ids_relevantes": {"doc0"}},
    {"pregunta": "que pasa si la clave de api es invalida",
     "ids_relevantes": {"doc1"}},
    {"pregunta": "como se calcula el costo de una llamada",
     "ids_relevantes": {"doc2"}},
    {"pregunta": "como decide el agente que herramienta usar",
     "ids_relevantes": {"doc3_c0"}},
    {"pregunta": "que herramientas tiene el agente de postventa",
     "ids_relevantes": {"doc3_c0", "doc3_c1"}},
    {"pregunta": "cuantas llamadas al modelo implica cada accion del agente",
     "ids_relevantes": {"doc3_c1"}},
    {"pregunta": "como se verifica que herramienta eligio el agente en cada caso",
     "ids_relevantes": {"doc3_c1", "doc3_c2"}},
    {"pregunta": "cuanto tarda la suite de pruebas en correr",
     "ids_relevantes": {"doc4"}},
    {"pregunta": "que operador conecta los pasos de una chain",
     "ids_relevantes": {"doc5_c0"}},
    {"pregunta": "que protege el flujo completo si falla un paso",
     "ids_relevantes": {"doc5_c1"}},
    {"pregunta": "cual es la politica de vacaciones de la empresa",
     "ids_relevantes": set()},
]


def precision_at_k(ids_recuperados, ids_relevantes):
    """Fraccion de los ids recuperados que son relevantes (0.0 si no hay ninguno)."""
    if not ids_recuperados:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)


def recall_at_k(ids_recuperados, ids_relevantes):
    """Fraccion de los ids relevantes que se recuperaron (None si el caso no tiene ninguno)."""
    if not ids_relevantes:
        return None
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)


def promediar(valores):
    """Promedio que ignora los None y evita dividir por cero."""
    validos = [v for v in valores if v is not None]
    return sum(validos) / len(validos) if validos else 0.0


def evaluar_recuperacion(retriever, casos, k=3):
    """Corre cada caso contra el retriever real y promedia precision y recall."""
    resultados = []
    for caso in casos:
        chunks = retriever.invoke(caso["pregunta"])
        ids_recuperados = [c.id for c in chunks][:k]
        p = precision_at_k(ids_recuperados, caso["ids_relevantes"])
        r = recall_at_k(ids_recuperados, caso["ids_relevantes"])
        resultados.append({"pregunta": caso["pregunta"], "precision": p, "recall": r})

    precision_promedio = promediar(x["precision"] for x in resultados)
    recall_promedio = promediar(x["recall"] for x in resultados)
    return resultados, precision_promedio, recall_promedio


if __name__ == "__main__":
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit(
            'Falta GEMINI_API_KEY. Defínela en tu archivo ".env" '
            "y vuelve a ejecutar."
        )

    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)
    vectorstore = Chroma(
        persist_directory=DIR_VECTORSTORE, embedding_function=embeddings
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": K})

    resultados, precision_promedio, recall_promedio = evaluar_recuperacion(
        retriever, casos_evaluacion, k=K
    )

    for r in resultados:
        recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
        print(f"{r['precision']:.2f}  {recall_txt}  {r['pregunta']}")
    print(f"\npromedio -> precision: {precision_promedio:.3f}  recall: {recall_promedio:.3f}")

    with open("resultados_evaluacion.txt", "w", encoding="utf-8") as archivo:
        archivo.write(f"Fecha: {date.today()}\n")
        archivo.write(f"Configuracion: k={K}, chunk_size=200, chunk_overlap=30\n\n")
        for r in resultados:
            recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
            archivo.write(f"{r['precision']:.2f}  {recall_txt}  {r['pregunta']}\n")
        archivo.write(
            f"\npromedio -> precision: {precision_promedio:.3f}  recall: {recall_promedio:.3f}\n"
        )
    print("Resultados guardados en resultados_evaluacion.txt")
