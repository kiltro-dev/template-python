"""Banco de prompts de la miniaplicación.

Cada entrada combina un prompt de sistema (comportamiento estable) con un
ejemplo de entrada de usuario (lo que cambia en cada petición), la estructura
JSON esperada como salida y las claves que la validación debe exigir.
"""

BANCO_DE_PROMPTS = [
    {
        "nombre": "clasificar_sentimiento",
        "system_instruction": (
            "Eres un clasificador de sentimiento. Responde únicamente con un objeto "
            "JSON válido, sin texto adicional y sin bloques de markdown. El JSON debe "
            "tener exactamente estas claves: 'sentimiento' (uno de 'positivo', "
            "'negativo' o 'neutro') y 'confianza' (número entre 0 y 1)."
        ),
        "ejemplo_usuario": "El servicio llegó tarde pero el producto está perfecto.",
        "claves_esperadas": ["sentimiento", "confianza"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "sentimiento": {"type": "STRING"},
                "confianza": {"type": "NUMBER"},
            },
            "required": ["sentimiento", "confianza"],
        },
    },
    {
        "nombre": "clasificar_consulta",
        "system_instruction": (
            "Eres un clasificador de consultas de usuarios. Responde únicamente con un "
            "objeto JSON válido, sin texto adicional y sin bloques de markdown. El JSON "
            "debe tener exactamente estas claves: 'categoria' (uno de 'soporte_tecnico', "
            "'facturacion' o 'general') y 'urgencia' (una de 'alta', 'media' o 'baja')."
        ),
        "ejemplo_usuario": "Necesito ayuda para resetear mi contraseña, no me llega el correo de verificación.",
        "claves_esperadas": ["categoria", "urgencia"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "categoria": {"type": "STRING"},
                "urgencia": {"type": "STRING"},
            },
            "required": ["categoria", "urgencia"],
        },
    },
    {
        "nombre": "extraer_entidades",
        "system_instruction": (
            "Eres un extractor de entidades. Responde únicamente con un objeto JSON "
            "válido, sin texto adicional y sin bloques de markdown. El JSON debe tener "
            "exactamente una clave: 'entidades', con una lista de los nombres propios "
            "de personas, lugares u organizaciones mencionados en el texto. Si no hay "
            "ninguna, devuelve una lista vacía."
        ),
        "ejemplo_usuario": "María viajó de Madrid a Buenos Aires para reunirse con el equipo de Globant.",
        "claves_esperadas": ["entidades"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "entidades": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                },
            },
            "required": ["entidades"],
        },
    },
    {
        "nombre": "generar_resumen",
        "system_instruction": (
            "Eres un asistente de resúmenes. Responde únicamente con un objeto JSON "
            "válido, sin texto adicional y sin bloques de markdown. El JSON debe tener "
            "exactamente estas claves: 'resumen' (un máximo de 2 oraciones) y "
            "'palabras_clave' (lista de 3 a 5 palabras clave del texto)."
        ),
        "ejemplo_usuario": (
            "La empresa anunció el lanzamiento de su nueva plataforma de pagos en línea, "
            "diseñada para pequeños comercios. La herramienta permite cobrar con tarjeta "
            "y billeteras digitales sin comisiones durante los primeros seis meses. "
            "El servicio ya está disponible en Argentina, Chile y Uruguay."
        ),
        "claves_esperadas": ["resumen", "palabras_clave"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "resumen": {"type": "STRING"},
                "palabras_clave": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                },
            },
            "required": ["resumen", "palabras_clave"],
        },
    },
    {
        "nombre": "detectar_idioma",
        "system_instruction": (
            "Eres un detector de idioma. Responde únicamente con un objeto JSON válido, "
            "sin texto adicional y sin bloques de markdown. El JSON debe tener "
            "exactamente estas claves: 'idioma' (nombre del idioma en español) y "
            "'confianza' (número entre 0 y 1)."
        ),
        "ejemplo_usuario": "¿Podrías indicarme dónde queda la estación de tren más cercana?",
        "claves_esperadas": ["idioma", "confianza"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "idioma": {"type": "STRING"},
                "confianza": {"type": "NUMBER"},
            },
            "required": ["idioma", "confianza"],
        },
    },
]
