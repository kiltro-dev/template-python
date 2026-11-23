"""Dataset propio para personalización con PEFT (Bloque 29).

Tarea de comportamiento consistente (no de conocimiento): clasificar
mensajes postventa en texto libre a un JSON fijo con tipo y urgencia.
Construcción, balance y validación: todo local, sin llamar a la API.

Ejecutar desde la raíz del repositorio, con el entorno virtual activo:
    python src/dataset_tuning.py
"""

import json
from collections import Counter
from google.genai import types

# 12 ejemplos propios: mensaje postventa -> {"tipo", "urgencia"}.
ejemplos_raw: list[tuple[str, dict]] = [
    ("¿Dónde está mi pedido PED1001? Lo necesito para mañana.",
     {"tipo": "pedido", "urgencia": "alta"}),
    ("Pagué $20000 por unos audífonos y los usé 45 días, ¿cuánto me devuelven?",
     {"tipo": "reembolso", "urgencia": "media"}),
    ("¿Cómo puedo contactar a soporte?",
     {"tipo": "consulta", "urgencia": "baja"}),
    ("La aplicación se cierra sola cada vez que intento subir una foto, ¿qué hago?",
     {"tipo": "consulta", "urgencia": "media"}),
    ("Necesito cancelar mi pedido PED1002 antes de que lo envíen.",
     {"tipo": "pedido", "urgencia": "alta"}),
    ("Mi reembolso de $15000 todavía no llega a mi tarjeta.",
     {"tipo": "reembolso", "urgencia": "alta"}),
    ("¿Cuánto tarda el envío a regiones?",
     {"tipo": "consulta", "urgencia": "baja"}),
    ("El producto llegó dañado, quiero devolverlo y que me devuelvan el dinero.",
     {"tipo": "reembolso", "urgencia": "alta"}),
    ("¿Mi pedido PED1003 ya fue entregado?",
     {"tipo": "pedido", "urgencia": "media"}),
    ("¿Tienen stock del cargador USB-C en color negro?",
     {"tipo": "consulta", "urgencia": "baja"}),
    ("Quiero cambiar la dirección de entrega de mi pedido PED1001.",
     {"tipo": "pedido", "urgencia": "media"}),
    ("Pasaron 10 días hábiles y no recibí mi reembolso, necesito una respuesta hoy.",
     {"tipo": "reembolso", "urgencia": "alta"}),
]

examples: list[types.TuningExample] = [
    types.TuningExample(text_input=texto, output=json.dumps(salida, ensure_ascii=False))
    for texto, salida in ejemplos_raw
]

print(len(examples), "ejemplos construidos")
print(examples[0])


def chequear_balance(ejemplos_raw: list[tuple[str, dict]], clave: str) -> Counter:
    categorias = Counter(salida[clave] for _, salida in ejemplos_raw)
    return categorias


balance_tipo = chequear_balance(ejemplos_raw, "tipo")
print("--- balance por tipo ---")
for categoria, cuenta in balance_tipo.most_common():
    print(f"{categoria}: {cuenta}")

balance_urgencia = chequear_balance(ejemplos_raw, "urgencia")
print("--- balance por urgencia ---")
for categoria, cuenta in balance_urgencia.most_common():
    print(f"{categoria}: {cuenta}")


def validar_dataset(
    examples: list[types.TuningExample], claves_esperadas: tuple[str, ...]
) -> list[str]:
    problemas = []
    vistos = set()
    for i, ej in enumerate(examples):
        if not ej.text_input or not ej.text_input.strip():
            problemas.append(f"ejemplo {i}: text_input vacio")
        if not ej.output or not ej.output.strip():
            problemas.append(f"ejemplo {i}: output vacio")
            continue
        if ej.text_input in vistos:
            problemas.append(f"ejemplo {i}: text_input duplicado")
        vistos.add(ej.text_input)
        try:
            salida = json.loads(ej.output)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: output no es JSON valido")
            continue
        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(f'ejemplo {i}: output no tiene la clave "{clave}"')
    return problemas


problemas = validar_dataset(examples, claves_esperadas=("tipo", "urgencia"))
print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
for p in problemas:
    print(" -", p)
