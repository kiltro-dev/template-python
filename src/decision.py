"""Método de decisión de personalización sobre el caso propio (Bloque 30).

Responde las 5 preguntas con evidencia del proyecto, calcula puntajes y
genera el esqueleto de docs/decision_personalizacion.md (secciones 3 y 4
se completan a mano).

Ejecutar desde la raíz del repositorio, con el entorno virtual activo:
    python src/decision.py
"""


def recomendar_estrategia(respuestas):
    puntos = {"RAG": 0, "Fine-tuning completo": 0, "PEFT": 0}

    if respuestas["informacion_cambia_seguido"]:
        puntos["RAG"] += 3
    if respuestas["problema_de_formato_o_tono"]:
        puntos["PEFT"] += 2
        puntos["Fine-tuning completo"] += 1
    if respuestas["dataset_grande_y_de_calidad"]:
        puntos["Fine-tuning completo"] += 2
        puntos["PEFT"] += 1
    if respuestas["presupuesto_limitado_o_iterar_rapido"]:
        puntos["RAG"] += 2
        puntos["PEFT"] += 1
    if respuestas["necesita_multiples_variantes"]:
        puntos["PEFT"] += 2

    maximo = max(puntos.values())
    ganadoras = [tecnica for tecnica, p in puntos.items() if p == maximo]
    return puntos, ganadoras


# Respuestas sobre el caso propio (tarea postventa del Bloque 29),
# cada una con la evidencia que la sustenta.
respuestas_mi_caso = {
    # categorías fijas definidas una vez, sin cambios desde su creación
    "informacion_cambia_seguido": False,
    # 0 de 20 respuestas reales fallaron el formato JSON (sonda /tmp, lite)
    "problema_de_formato_o_tono": False,
    # 12 ejemplos propios, muy lejos del umbral de 200
    "dataset_grande_y_de_calidad": False,
    # tuning ni siquiera habilitado en la cuenta; se itera en el día
    "presupuesto_limitado_o_iterar_rapido": True,
    # un solo clasificador postventa para todo el sistema
    "necesita_multiples_variantes": False,
}

if any(valor is None for valor in respuestas_mi_caso.values()):
    raise SystemExit("Completa las cinco respuestas con True o False antes de continuar.")

puntos, ganadoras = recomendar_estrategia(respuestas_mi_caso)
print(puntos)
print("candidatas:", ganadoras)


def generar_esqueleto_decision(problema, puntos, ganadoras):
    empate = len(ganadoras) > 1
    lineas = []
    lineas.append("# Decision de personalizacion")
    lineas.append("")
    lineas.append("## 1. El problema")
    lineas.append(problema)
    lineas.append("")
    lineas.append("## 2. Resultado del metodo de decision")
    for tecnica, p in sorted(puntos.items(), key=lambda x: -x[1]):
        lineas.append(f"- {tecnica}: {p} puntos")
    if empate:
        lineas.append("")
        lineas.append(f"**Empate entre: {', '.join(ganadoras)}**")
    lineas.append("")
    lineas.append("## 3. Tecnica elegida y por que")
    if empate:
        lineas.append(
            "[COMPLETAR: el puntaje no resolvio el empate solo -- "
            "justifica aqui con criterio propio]"
        )
    else:
        lineas.append(f"[COMPLETAR: por que {ganadoras[0]} responde mejor a este caso]")
    lineas.append("")
    lineas.append("## 4. Que necesitarias para ejecutarla")
    lineas.append(
        "[COMPLETAR: corpus faltante, o cantidad de ejemplos etiquetados que faltan]"
    )
    return "\n".join(lineas)


esqueleto = generar_esqueleto_decision(
    "Cada mensaje postventa en texto libre debe quedar clasificado con tipo "
    "y urgencia en un formato fijo y consistente.",
    puntos,
    ganadoras,
)
print(esqueleto)

import os as _os

# no sobrescribir jamás el documento manual: solo se genera si no existe
if not _os.path.exists("docs/decision_personalizacion.md"):
    with open("docs/decision_personalizacion.md", "w", encoding="utf-8") as f:
        f.write(esqueleto)
    print("Esqueleto guardado en docs/decision_personalizacion.md")
else:
    print("docs/decision_personalizacion.md ya existe: no se sobrescribe")
