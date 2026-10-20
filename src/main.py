from consumir_gemini import obtener_dato_de_prueba

pregunta = "Confirma en una frase corta que esta conexión funciona"
try:
    resultado = obtener_dato_de_prueba(pregunta)
    print(resultado)
except (ValueError, RuntimeError) as error:
    print(f"[ERROR] No se pudo completar la operación: {type(error).__name__}: {error}")