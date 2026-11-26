"""Verifica entorno para la corrida final del Gate 2 (Bloque S1).

Muestra versiones y estado sin imprimir nunca la clave. Termina con
código 1 si algo falta. Ejecutar desde la raíz del repositorio:
    python verificar_entorno.py
"""

import os
import sys
from importlib.metadata import version, PackageNotFoundError

PAQUETES = [
    "langchain-core",
    "langchain-chroma",
    "langchain-google-genai",
    "langgraph",
    "python-dotenv",
    "pytest",
]
VARIABLES = ["GEMINI_API_KEY"]
INDICE_DIR = "vectorstore"  # carpeta del índice persistido propio

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

problemas = []
print("Python:", sys.version.split()[0])
if sys.version_info < (3, 10):
    problemas.append("usar Python 3.10 o superior")

for paquete in PAQUETES:
    try:
        print(f"{paquete}: {version(paquete)}")
    except PackageNotFoundError:
        print(f"{paquete}: NO instalado")
        problemas.append(f"instalar {paquete}")

for nombre in VARIABLES:
    estado = "definida" if os.getenv(nombre) else "FALTA"
    print(f"{nombre}: {estado}")
    if estado == "FALTA":
        problemas.append(f"definir {nombre} en el archivo .env")

if os.path.isdir(INDICE_DIR) and os.listdir(INDICE_DIR):
    print(f"indice en {INDICE_DIR}/: ok")
else:
    print(f"indice en {INDICE_DIR}/: NO existe o esta vacio")
    problemas.append("indexar el corpus (python src/indexar_corpus.py)")

print()
if problemas:
    print("Pendiente: " + "; ".join(problemas))
    sys.exit(1)
print("Entorno listo para la corrida final")
