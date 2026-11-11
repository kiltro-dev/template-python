"""Agente con herramientas propias y traza de decisión (Bloque 21).

Dos herramientas de soporte postventa: consultar_estado_pedido (dónde
está un pedido) y calcular_reembolso (cuánto dinero se devuelve). El
agente decide por sí mismo cuál usar según la entrada, o ninguna.

Ejecutar desde la raíz del repositorio:
    python src/agente_con_herramientas.py
"""

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

MODELO = "gemini-3.5-flash-lite"


@tool
def consultar_estado_pedido(numero_seguimiento: str) -> str:
    """Consulta dónde está un pedido a partir de su número de
    seguimiento. Usar cuando el usuario pregunta por el estado
    o la ubicación de su pedido."""
    pedidos = {
        "PED1001": "en tránsito, llega en 2 días",
        "PED1002": "entregado ayer a las 15:40",
        "PED1003": "en preparación en bodega",
    }
    try:
        return pedidos[numero_seguimiento]
    except KeyError:
        return (
            f"No se encontró un pedido con el número {numero_seguimiento}."
        )


@tool
def calcular_reembolso(monto_pagado: float, dias_uso: int) -> str:
    """Calcula cuánto dinero se devuelve por una compra según el
    monto pagado y los días de uso, aplicando la política de
    devoluciones. Usar cuando el usuario pregunta por un
    reembolso o devolución de dinero."""
    if monto_pagado < 0 or dias_uso < 0:
        return "El monto y los días deben ser valores positivos."
    if dias_uso <= 30:
        monto, tramo = monto_pagado, "completo, dentro de los 30 días"
    elif dias_uso <= 60:
        monto, tramo = monto_pagado * 0.5, "parcial del 50%, entre 31 y 60 días"
    else:
        monto, tramo = 0.0, "sin reembolso, más de 60 días de uso"
    return f"Reembolso {tramo}: ${monto:.2f}."


def construir_ejecutor(modelo):
    """Arma el agente con sus 2 herramientas y devuelve el ejecutor,
    con traza programática activada (sin ejecutar nada todavía)."""
    herramientas = [consultar_estado_pedido, calcular_reembolso]
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


def herramienta_usada(resultado):
    """Nombre de la primera herramienta invocada, o None si no usó ninguna."""
    pasos = resultado["intermediate_steps"]
    return pasos[0][0].tool if pasos else None


def texto_respuesta(salida):
    """Extrae el texto de output (con la versión instalada viene como
    lista de bloques de contenido, no como string plano)."""
    if isinstance(salida, str):
        return salida
    return "".join(
        bloque.get("text", "")
        for bloque in salida
        if isinstance(bloque, dict) and bloque.get("type") == "text"
    )


if __name__ == "__main__":
    load_dotenv()
    ejecutor = construir_ejecutor(ChatGoogleGenerativeAI(model=MODELO))

    casos = [
        ("¿Dónde está mi pedido PED1001?", "consultar_estado_pedido"),
        (
            "Pagué $20000 por unos audífonos y los usé 45 días, "
            "¿cuánto me devuelven?",
            "calcular_reembolso",
        ),
        ("¿Cómo puedo contactar a soporte?", None),
    ]
    for entrada, esperada in casos:
        resultado = ejecutor.invoke({"entrada": entrada})
        usada = herramienta_usada(resultado)
        print(f"entrada: {entrada}")
        print(f"herramienta: {usada} (esperada: {esperada})")
        print(f"respuesta: {texto_respuesta(resultado['output'])}")
        print()
        assert usada == esperada, f"esperaba {esperada}, usó {usada}"
    print("3 validaciones manuales OK")
