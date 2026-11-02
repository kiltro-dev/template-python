"""Pruebas unitarias de las métricas de evaluación (Bloque 16).

Sin mocks ni red: funciones puras sobre listas de tokens. Incluye el
ejemplo calculado a mano de la lección (el gato en el sofá) y los guards
de listas vacías.

Ejecutar desde la raíz del repositorio:
    python -m pytest tests/test_metricas.py -v
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from metricas import (  # noqa: E402
    calcular_metricas,
    calcular_precision_cobertura_f1,
    contar_coincidencias,
    resumir_metricas,
)


def test_contar_coincidencias_toma_minimos():
    referencia = ["el", "gato", "duerme", "en", "el", "sofa"]
    respuesta = ["el", "gato", "duerme", "en", "el", "sillon", "todo", "el", "dia"]

    assert contar_coincidencias(referencia, respuesta) == 5


def test_precision_cobertura_f1_ejemplo_mano():
    referencia = ["el", "gato", "duerme", "en", "el", "sofa"]
    respuesta = ["el", "gato", "duerme", "en", "el", "sillon", "todo", "el", "dia"]

    resultado = calcular_precision_cobertura_f1(referencia, respuesta)

    assert resultado["precision"] == pytest.approx(5 / 9)
    assert resultado["cobertura"] == pytest.approx(5 / 6)
    assert resultado["f1"] == pytest.approx(0.6667, abs=1e-3)


def test_listas_vacias_devuelven_ceros():
    assert calcular_precision_cobertura_f1([], ["el", "gato"]) == {
        "precision": 0.0,
        "cobertura": 0.0,
        "f1": 0.0,
    }
    assert calcular_precision_cobertura_f1(["el", "gato"], []) == {
        "precision": 0.0,
        "cobertura": 0.0,
        "f1": 0.0,
    }


def test_calcular_metricas_procesa_texto_crudo():
    resultado = calcular_metricas("El Gato.", "el gato!")

    assert resultado == {"precision": 1.0, "cobertura": 1.0, "f1": 1.0}


def test_resumir_metricas_promedia_y_vacio():
    resultados = [
        {"precision": 1.0, "cobertura": 0.5, "f1": 0.5},
        {"precision": 0.5, "cobertura": 1.0, "f1": 0.5},
    ]

    resumen = resumir_metricas(resultados)

    assert resumen == {
        "precision_promedio": 0.75,
        "cobertura_promedio": 0.75,
        "f1_promedio": 0.5,
    }
    assert resumir_metricas([]) == {
        "precision_promedio": 0,
        "cobertura_promedio": 0,
        "f1_promedio": 0,
    }
