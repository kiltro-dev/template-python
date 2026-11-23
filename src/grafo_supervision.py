"""Punto de supervisión para desplegar versiones del prompt (Bloque 32, paso 2).

Grafo LangGraph: propone la huella nueva, pausa en interrupt() hasta
aprobación humana explícita, y aplica o rechaza según la decisión.
Demuestra ambos caminos con thread_ids distintos.

Ejecutar desde la raíz del repositorio, con el entorno virtual activo:
    python src/grafo_supervision.py
"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class EstadoDespliegue(TypedDict):
    huella_nueva: str
    aprobado: bool


def proponer(estado: EstadoDespliegue):
    return {}


def supervisar(estado: EstadoDespliegue):
    decision = interrupt({
        "motivo": "aprobar nueva version de prompt en produccion",
        "huella_propuesta": estado["huella_nueva"],
    })
    return {"aprobado": decision}


def aplicar(estado: EstadoDespliegue):
    if estado["aprobado"]:
        print("version", estado["huella_nueva"], "activada")
    else:
        print("version", estado["huella_nueva"], "rechazada, se mantiene la anterior")
    return {}


grafo = StateGraph(EstadoDespliegue)
grafo.add_node("proponer", proponer)
grafo.add_node("supervisar", supervisar)
grafo.add_node("aplicar", aplicar)
grafo.add_edge(START, "proponer")
grafo.add_edge("proponer", "supervisar")
grafo.add_edge("supervisar", "aplicar")
grafo.add_edge("aplicar", END)

app_despliegue = grafo.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    # huella v2 real de src/registro_prompts.py (anti-inyección Bloque 31)
    huella = "da42e8cb229b"

    config = {"configurable": {"thread_id": "mi-despliegue-1"}}
    resultado = app_despliegue.invoke(
        {"huella_nueva": huella, "aprobado": False}, config=config
    )
    print("1) tras invocar:", resultado)
    print("2) pendiente:", app_despliegue.get_state(config).interrupts[0].value)
    resultado = app_despliegue.invoke(Command(resume=True), config=config)
    print("3) tras aprobar:", resultado)

    config2 = {"configurable": {"thread_id": "mi-despliegue-2"}}
    app_despliegue.invoke(
        {"huella_nueva": huella, "aprobado": False}, config=config2
    )
    resultado = app_despliegue.invoke(Command(resume=False), config=config2)
    print("4) tras rechazar:", resultado)
