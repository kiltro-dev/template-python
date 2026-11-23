"""Matriz de riesgos del sistema propio (Bloque 32, paso 3).

Siete riesgos concretos con probabilidad e impacto puntuados, mitigación
apuntando a lo ya construido (con número de bloque) y punto de supervisión
para los ALTO. Incluye chequeo de cercanía al límite de categoría.

Ejecutar desde la raíz del repositorio, con el entorno virtual activo:
    python src/matriz_riesgos.py
"""


def puntaje_riesgo(probabilidad, impacto):
    return probabilidad * impacto


def categoria_riesgo(puntaje):
    if puntaje >= 15:
        return "CRITICO"
    if puntaje >= 9:
        return "ALTO"
    if puntaje >= 4:
        return "MEDIO"
    return "BAJO"


def esta_en_el_limite(probabilidad, impacto):
    categoria_actual = categoria_riesgo(puntaje_riesgo(probabilidad, impacto))
    vecinos = [
        (probabilidad + 1, impacto), (probabilidad - 1, impacto),
        (probabilidad, impacto + 1), (probabilidad, impacto - 1),
    ]
    for p2, i2 in vecinos:
        if not (1 <= p2 <= 5 and 1 <= i2 <= 5):
            continue
        if categoria_riesgo(puntaje_riesgo(p2, i2)) != categoria_actual:
            return True
    return False


mis_riesgos = [
    {"riesgo": "Inyeccion de prompt via documento recuperado",
     "probabilidad": 2,  # corpus propio fijo, no texto de usuarios
     "impacto": 4,  # expondria instrucciones y datos de clientes
     "mitigacion": "Filtro de patrones + delimitacion de contexto (Bloque 31)"},
    {"riesgo": "Filtracion de PII en logs y trazas sin redactar",
     "probabilidad": 3,  # trazas y registros guardan preguntas completas
     "impacto": 4,  # datos personales en disco sin auditar
     "mitigacion": "Huellas y longitudes en logging_rag (Bloque 31)",
     "supervision": "Aprobacion humana antes de ampliar retencion de logs con contenido"},
    {"riesgo": "Dataset de tuning desbalanceado produce sesgo",
     "probabilidad": 2,  # medido 4/4/4 y 5/4/3, max/min 1.7x
     "impacto": 3,  # formato inconsistente en categoria chica
     "mitigacion": "Chequeo de balance por categoria (Bloque 29)"},
    {"riesgo": "Modelo de embeddings deprecado sin aviso",
     "probabilidad": 2,  # proveedores deprecian sin aviso
     "impacto": 4,  # indice completo inutil, reindexar todo
     "mitigacion": "Revision periodica de documentacion oficial (Bloque 28)"},
    {"riesgo": "Respuesta con informacion vieja por chunk no reindexado",
     "probabilidad": 3,  # corpus puede cambiar sin reindexar
     "impacto": 2,  # respuesta desactualizada, citada y verificable
     "mitigacion": "Actualizacion incremental con ids explicitos (Bloque 25)"},
    {"riesgo": "Despliegue de prompt sin revision humana",
     "probabilidad": 3,  # cambios de prompt son frecuentes
     "impacto": 4,  # comportamiento nuevo en produccion sin control
     "mitigacion": "Grafo de supervision con interrupt (Bloque 32)",
     "supervision": "Aprobar huella nueva en el grafo antes de activar"},
    {"riesgo": "Formato JSON degradado con trafico real",
     "probabilidad": 2,  # medido 0/20, pero muestra propia no trafico
     "impacto": 3,  # salidas no parseables aguas abajo
     "mitigacion": "Monitoreo con muestra de 20 (Bloque 30)"},
]

if __name__ == "__main__":
    for r in mis_riesgos:
        r["puntaje"] = puntaje_riesgo(r["probabilidad"], r["impacto"])
        r["categoria"] = categoria_riesgo(r["puntaje"])
        r["al_limite"] = esta_en_el_limite(r["probabilidad"], r["impacto"])

    for r in sorted(mis_riesgos, key=lambda x: -x["puntaje"]):
        marca = " [AL LIMITE]" if r["al_limite"] else ""
        print(f"{r['categoria']:8} ({r['puntaje']:2}) - {r['riesgo']}{marca}")
        if r["categoria"] in ("ALTO", "CRITICO"):
            print(f"           supervision: {r['supervision']}")

    print()
    for r in mis_riesgos:
        if r["al_limite"]:
            print("revisar con otra persona:", r["riesgo"])
