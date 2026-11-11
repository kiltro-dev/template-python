"""Agente con supervisión humana y traza persistente (Bloque 23).

Extiende el agente postventa con una herramienta de riesgo alto
(generar_reembolso: irreversible, exige aprobación con tiempo límite)
y registra cada interacción en trazas_agente.jsonl para revisión
posterior. Las herramientas de riesgo bajo se reutilizan sin duplicar.

Ejecutar desde la raíz del repositorio (pide aprobación por teclado
en el caso de riesgo alto):
    python src/agente_supervision.py
    echo s | python src/agente_supervision.py   # aprobar no interactivo
"""

import json
import select
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from agente_con_herramientas import (
    MODELO,
    calcular_reembolso,
    consultar_estado_pedido,
    texto_respuesta,
)

RUTA_TRAZAS = "trazas_agente.jsonl"

registro_aprobaciones = []


def esperar_aprobacion(mensaje: str, tiempo_limite_segundos: int = 300) -> bool:
    """Pide aprobación por teclado con límite de tiempo.

    Sin respuesta a tiempo devuelve False (default-deny: para una
    acción de riesgo alto, lo seguro es NO ejecutar). En Linux/macOS
    usa select sobre stdin; en Windows haría falta otra estrategia.
    """
    print(mensaje)
    listo, _, _ = select.select([sys.stdin], [], [], tiempo_limite_segundos)
    if not listo:
        return False
    respuesta = sys.stdin.readline()
    return respuesta.strip().lower() == "s"


def registrar_aprobacion(herramienta: str, argumentos: dict, aprobado: bool) -> None:
    """Guarda quién aprobó qué, cuándo y con qué resultado (en memoria;
    en producción, base de datos)."""
    registro_aprobaciones.append(
        {
            "herramienta": herramienta,
            "argumentos": argumentos,
            "aprobado": aprobado,
            "momento": datetime.now(timezone.utc).isoformat(),
        }
    )


class ArgumentosGenerarReembolso(BaseModel):
    numero_pedido: str = Field(
        description="Número del pedido a reembolsar. Por ejemplo PED1001."
    )
    monto: float = Field(
        description="Monto a reembolsar, en pesos. Por ejemplo 15000."
    )


@tool(args_schema=ArgumentosGenerarReembolso)
def generar_reembolso(numero_pedido: str, monto: float) -> str:
    """Genera un reembolso para un pedido, moviendo dinero de forma
    irreversible. Usar SOLO cuando el usuario pide explícitamente que
    se genere o ejecute un reembolso (no cuando pregunta cuánto sería).
    Requiere aprobación humana antes de ejecutarse."""
    mensaje = (
        f"El agente quiere reembolsar ${monto} "
        f"para el pedido {numero_pedido}. "
        f"¿Aprobar? (s/n): "
    )
    aprobado = esperar_aprobacion(mensaje)
    registrar_aprobacion(
        herramienta="generar_reembolso",
        argumentos={"numero_pedido": numero_pedido, "monto": monto},
        aprobado=aprobado,
    )
    if not aprobado:
        return "Reembolso no aprobado por el supervisor humano."
    return f"Reembolso de ${monto} generado para el pedido {numero_pedido}."


def registrar_traza(session_id: str, entrada: str, resultado: dict) -> None:
    """Agrega una interacción como línea JSON en trazas_agente.jsonl.

    Sin intermediate_steps (ejecutor sin traza activada), acciones queda
    vacía en vez de fallar.
    """
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion,
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuesta_final": texto_respuesta(resultado["output"]),
    }
    with open(RUTA_TRAZAS, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def marcar_repeticiones_sospechosas(archivo: str = RUTA_TRAZAS) -> None:
    """Marca sesiones donde la misma herramienta se usó dos veces
    seguidas: candidato a revisión humana, no conclusión."""
    try:
        with open(archivo, encoding="utf-8") as f:
            registros = [json.loads(linea) for linea in f]
    except FileNotFoundError:
        print(
            f"No se encontró '{archivo}'. Corre registrar_traza al menos "
            "una vez antes de revisar repeticiones."
        )
        return
    for registro in registros:
        herramientas = [a["herramienta"] for a in registro.get("acciones", [])]
        for i in range(1, len(herramientas)):
            if herramientas[i] == herramientas[i - 1]:
                print(
                    f"Revisar: {registro['session_id']} usó "
                    f"'{herramientas[i]}' dos veces seguidas"
                )
                break


def construir_ejecutor_supervision(modelo):
    """Arma el agente con sus 3 herramientas (2 bajo + 1 alto riesgo)
    y traza programática activada (sin ejecutar nada todavía)."""
    herramientas = [consultar_estado_pedido, calcular_reembolso, generar_reembolso]
    prompt_agente = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres un asistente de soporte postventa que responde "
                "preguntas usando las herramientas disponibles cuando "
                "las necesites.",
            ),
            ("human", "{entrada}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)
    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        return_intermediate_steps=True,
    )


if __name__ == "__main__":
    load_dotenv()
    ejecutor = construir_ejecutor_supervision(ChatGoogleGenerativeAI(model=MODELO))
    casos = [
        ("demo_bajo", "¿Dónde está mi pedido PED1001?"),
        ("demo_alto", "Reembolsa el pedido PED1001 por $15000."),
    ]
    for session_id, entrada in casos:
        resultado = ejecutor.invoke({"entrada": entrada})
        registrar_traza(session_id, entrada, resultado)
        print(f"{session_id}: {texto_respuesta(resultado['output'])}")
    print("trazas + aprobaciones registradas OK")
    print("registro:", registro_aprobaciones)
