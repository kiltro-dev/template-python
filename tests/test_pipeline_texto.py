"""Pruebas unitarias del pipeline de limpieza y tokenización (Bloque 15).

Sin mocks: procesar_texto no toca la red ni depende de nada externo, así
que se prueba directo, igual que registrar_costo en el bloque anterior.

Ejecutar desde la raíz del repositorio:
    python -m pytest tests/test_pipeline_texto.py -v
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from pipeline_texto import procesar_texto  # noqa: E402


def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    resultado = procesar_texto("El Cielo, es AZUL!")

    assert resultado == ["el", "cielo", "es", "azul"]


def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    resultado = procesar_texto("¡¡¡...!!!")

    assert resultado == []
