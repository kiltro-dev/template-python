"""Suite de pruebas unitarias del cliente modular (Bloque 14, actividad core).

Cubre las cuatro funciones del checklist, con mocks: sin API real, sin tokens,
sin esperas de verdad. La suite completa corre en milisegundos.

Ejecutar desde la raíz del repositorio:
    python -m pytest tests/test_cliente.py -v

Los patch apuntan a "cliente.requests.post" y "cliente.time.sleep", tal como
en la lección: el cliente vive en src/cliente.py (con enviar_peticion
duplicada adentro, a pedido del curso, para que el cliente quede autocontenido).
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import cliente  # noqa: E402
from cliente import con_reintento, consultar_modelo, enviar_peticion  # noqa: E402


@pytest.fixture(autouse=True)
def reiniciar_costo_total(monkeypatch):
    """Reinicia el acumulado de sesión antes de cada prueba y fija una API key
    de prueba, para que ninguna prueba dependa del .env del programador."""
    cliente.costo_total_sesion = 0
    monkeypatch.setenv("GEMINI_API_KEY", "clave_de_prueba")
    yield


# ---------- enviar_peticion: clasificación de errores ----------


def test_enviar_peticion_credencial_invalida():
    respuesta_falsa = Mock(status_code=401)

    with patch("cliente.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError):
            enviar_peticion("https://ejemplo.test", {"pregunta": "test"}, {})


def test_enviar_peticion_credencial_sin_permiso():
    respuesta_falsa = Mock(status_code=403)

    with patch("cliente.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError):
            enviar_peticion("https://ejemplo.test", {"pregunta": "test"}, {})


def test_enviar_peticion_limite_de_uso():
    respuesta_falsa = Mock(status_code=429)

    with patch("cliente.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion("https://ejemplo.test", {"pregunta": "test"}, {})


def test_enviar_peticion_error_del_proveedor():
    respuesta_falsa = Mock(status_code=503)

    with patch("cliente.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion("https://ejemplo.test", {"pregunta": "test"}, {})


def test_enviar_peticion_exito():
    respuesta_falsa = Mock(status_code=200)
    # Nuestro enviar_peticion exige que la respuesta traiga "candidates",
    # así que el mock del camino feliz incluye ese bloque.
    respuesta_falsa.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "respuesta simulada"}]}}]
    }

    with patch("cliente.requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion("https://ejemplo.test", {"pregunta": "test"}, {})

    assert resultado == {
        "candidates": [{"content": {"parts": [{"text": "respuesta simulada"}]}}]
    }


# ---------- con_reintento: reintento con backoff ----------


def test_con_reintento_reintenta_y_exito():
    intentos = {"n": 0}

    def funcion_que_falla_una_vez():
        intentos["n"] += 1
        if intentos["n"] == 1:
            raise TimeoutError("simulado")
        return "ok"

    with patch("cliente.time.sleep") as mock_sleep:
        resultado = con_reintento(funcion_que_falla_una_vez)

    assert resultado == "ok"
    # Se llamó exactamente una vez, sin comparar cuántos segundos (el jitter
    # es aleatorio por diseño).
    mock_sleep.assert_called_once()


def test_con_reintento_no_reintenta_value_error():
    def funcion_con_error_de_configuracion():
        raise ValueError("simulado")

    with patch("cliente.time.sleep") as mock_sleep:
        with pytest.raises(ValueError):
            con_reintento(funcion_con_error_de_configuracion)

    # Un error que no es temporal no debe esperar ni reintentar.
    mock_sleep.assert_not_called()


def test_con_reintento_agota_intentos():
    def siempre_falla():
        raise TimeoutError("simulado")

    with patch("cliente.time.sleep") as mock_sleep:
        with pytest.raises(TimeoutError):
            con_reintento(siempre_falla, intentos=3)

    # 3 intentos = 2 esperas entre ellos (no se espera tras el último).
    assert mock_sleep.call_count == 2


# ---------- registrar_costo: costo por operación y acumulado ----------


def test_registrar_costo_acumula():
    respuesta_falsa = {"usageMetadata": {"promptTokenCount": 1000, "candidatesTokenCount": 500}}
    precios = cliente.PRECIOS["gemini-2.5-flash"]

    costo = cliente.registrar_costo(respuesta_falsa, precios["entrada"], precios["salida"])

    # Nuestra fórmula cobra entrada y salida por separado, como hace Gemini.
    esperado = (1000 * precios["entrada"]) + (500 * precios["salida"])
    assert costo == esperado
    assert cliente.costo_total_sesion == esperado


# ---------- consultar_modelo: interfaz pública ----------


def test_consultar_modelo_convierte_error():
    error_simulado = TimeoutError("simulado")

    with patch("cliente.con_reintento", side_effect=error_simulado):
        with pytest.raises(RuntimeError, match="no respondió tras varios intentos"):
            consultar_modelo("pregunta de prueba")


def test_consultar_modelo_propaga_value_error():
    error_simulado = ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.")

    with patch("cliente.con_reintento", side_effect=error_simulado):
        with pytest.raises(ValueError, match="Credencial inválida"):
            consultar_modelo("pregunta de prueba")
