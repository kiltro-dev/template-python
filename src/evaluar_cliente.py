"""Genera las 20 respuestas reales de la actividad core (Bloque 17).

Recorre consultas fijas con su referencia, llama a consultar_modelo,
calcula métricas y guarda incrementalmente en resultados_metricas.json
(guardar dentro del ciclo: si el ciclo muere a mitad, lo procesado no se
pierde). Cada caso va en try/except propio: un caso lento no mata el
registro de los demás.

Uso desde la raíz del repositorio:
    venv/bin/python src/evaluar_cliente.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cliente import consultar_modelo  # noqa: E402
from metricas import calcular_metricas  # noqa: E402

CASOS = [
    ("¿Qué es Python?", "Python es un lenguaje de programación interpretado."),
    ("¿Cuándo se creó Python?", "Python fue creado en 1991."),
    ("¿Qué es una lista en Python?", "Una lista es una colección ordenada y modificable."),
    ("¿Cuál es la capital de Chile?", "Santiago es la capital de Chile."),
    ("¿De qué color es el cielo?", "El cielo es azul."),
    ("¿Cuál es la fórmula química del agua?", "La fórmula química del agua es H2O."),
    ("¿Quién escribió Don Quijote?", "Miguel de Cervantes escribió Don Quijote."),
    ("¿Cuántos días tiene un año bisiesto?", "Un año bisiesto tiene 366 días."),
    ("¿Qué planeta es el más cercano al Sol?", "Mercurio es el planeta más cercano al Sol."),
    ("¿En qué año llegó el hombre a la Luna?", "El hombre llegó a la Luna en 1969."),
    ("¿Qué es la fotosíntesis?", "La fotosíntesis es el proceso con que las plantas producen su alimento."),
    ("¿Cuál es el océano más grande?", "El océano Pacífico es el más grande."),
    ("¿Quién pintó la Mona Lisa?", "Leonardo da Vinci pintó la Mona Lisa."),
    ("¿Cuántos continentes hay?", "Hay siete continentes."),
    ("¿Qué gas necesitamos respirar para vivir?", "Necesitamos respirar oxígeno para vivir."),
    ("¿Cuál es el río más largo del mundo?", "El río más largo del mundo es el Amazonas."),
    ("¿En qué año cayó el muro de Berlín?", "El muro de Berlín cayó en 1989."),
    ("¿Qué instrumento mide la temperatura?", "El termómetro mide la temperatura."),
    ("¿Cuál es la capital de Francia?", "París es la capital de Francia."),
    ("¿Qué significa ADN?", "ADN significa ácido desoxirribonucleico."),
]

SALIDA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "resultados_metricas.json",
)


def main():
    resultados = []
    for i, (consulta, referencia) in enumerate(CASOS, start=1):
        try:
            # 6 intentos en vez de 3: la evaluación por lotes tolera esperas
            # largas ante cuota; el uso interactivo sigue con el default.
            respuesta = consultar_modelo(consulta + " Responde en una frase.", intentos=6)
            metricas = calcular_metricas(referencia, respuesta)
            resultados.append({"consulta": consulta, "respuesta": respuesta, **metricas})
            print(f"Caso {i}: f1={metricas['f1']:.2f} OK", flush=True)
        except ValueError as error:
            print(f"Caso {i}: ERROR DE CONFIGURACION: {error}", flush=True)
            break
        except RuntimeError as error:
            resultados.append({
                "consulta": consulta,
                "respuesta": "",
                "precision": 0.0,
                "cobertura": 0.0,
                "f1": 0.0,
                "error": str(error),
            })
            print(f"Caso {i}: FALLO TRAS REINTENTOS", flush=True)
        with open(SALIDA, "w", encoding="utf-8") as archivo:
            json.dump(resultados, archivo, indent=2, ensure_ascii=False)
    print(f"LISTO: {len(resultados)} casos en resultados_metricas.json", flush=True)


if __name__ == "__main__":
    main()
