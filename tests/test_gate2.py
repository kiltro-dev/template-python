"""Tests del Gate 2: los 4 no compensables contra el servicio real (Bloque S1).

Adaptado al proyecto: servicio_rag.responder + grafo de supervisión propio.
Requiere índice persistido (python src/indexar_corpus.py) y GEMINI_API_KEY,
porque prueba el flujo real, no simulado.

Ejecutar desde la raíz, con el entorno virtual activo:
    python -m pytest tests/test_gate2.py -v
"""

import logging
import sys

import pytest
from dotenv import load_dotenv

sys.path.insert(0, "src")

from grafo_supervision import app_despliegue  # noqa: E402
from servicio_rag import cargar_indice, responder  # noqa: E402

load_dotenv()

# Dato sensible de prueba que NUNCA debe aparecer en los logs
CORREO = "ana.perez@example.com"
# Pregunta que nuestro corpus SI responde (la de devoluciones no aplica aqui)
PREGUNTA = "Que hace el cliente si una llamada tarda demasiado? Mi correo es " + CORREO


@pytest.fixture(scope="module")
def vectorstore():
    vectorstore, _ = cargar_indice()
    return vectorstore


@pytest.fixture
def capta_mi_rag(caplog):
    """Nuestro logger no propaga por diseño; este fixture lo hace visible
    a caplog SOLO durante el test, para verificar su contenido real."""
    from logging_rag import logger
    anterior = logger.propagate
    logger.propagate = True
    yield caplog
    logger.propagate = anterior


def test_1_pipeline_sin_excepciones(vectorstore):
    resultado = responder(PREGUNTA, vectorstore, "indice_reutilizado")
    assert resultado["respuesta"].strip(), "el servicio devolvio una respuesta vacia"


def test_2_respuesta_cita_fuente(vectorstore):
    resultado = responder(PREGUNTA, vectorstore, "indice_reutilizado")
    assert resultado["fuentes"], "el servicio no devolvio ninguna fuente"
    assert any(f in resultado["respuesta"] for f in resultado["fuentes"]), \
        "la respuesta no menciona su fuente"


def test_3_logs_sin_contenido_crudo(vectorstore, capta_mi_rag):
    with capta_mi_rag.at_level(logging.DEBUG):
        responder(PREGUNTA, vectorstore, "indice_reutilizado")
    texto_logs = " ".join(
        r.getMessage() + " " + str(r.__dict__) for r in capta_mi_rag.records
    )
    assert CORREO not in texto_logs, "un dato sensible aparece en los logs"
    assert PREGUNTA not in texto_logs, "la consulta completa aparece en los logs"


def test_4_supervision_pausa_y_reanuda():
    from langgraph.types import Command
    config = {"configurable": {"thread_id": "test-gate2"}}
    pausado = app_despliegue.invoke(
        {"huella_nueva": "da42e8cb229b", "aprobado": False}, config=config
    )
    assert "__interrupt__" in pausado, "el grafo no se detuvo en el punto de supervision"
    final = app_despliegue.invoke(Command(resume=True), config=config)
    assert "__interrupt__" not in final, "el grafo sigue pausado despues de reanudar"
    assert final["aprobado"] is True, "la decision no quedo registrada"
