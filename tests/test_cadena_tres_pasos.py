"""Pruebas de la chain de tres pasos (Bloque 18, actividad core).

Con mock: sin API real, sin tokens, sin esperas. La suite completa
corre en milisegundos.

Ejecutar desde la raíz del repositorio:
    python -m pytest tests/test_cadena_tres_pasos.py -v
"""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from cadena_tres_pasos import construir_cadena  # noqa: E402
from langchain_core.messages import AIMessage  # noqa: E402


def test_cadena_conecta_los_tres_pasos():
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="reclamo"),
        AIMessage(content="Lamentamos la demora, revisaremos tu pedido hoy."),
        AIMessage(content="Lamentamos la demora; revisaremos tu pedido hoy mismo."),
    ]
    cadena = construir_cadena(modelo_falso)
    resultado = cadena.invoke({"mensaje": "mensaje de prueba"})
    assert modelo_falso.call_count == 3
    assert "pedido" in resultado
