from consumir_gemini import obtener_dato_de_prueba

# Precios por token (USD). Confirmar siempre en la pagina de precios vigente del proveedor.
PRECIO_ENTRADA = 0.30 / 1_000_000
PRECIO_SALIDA = 2.50 / 1_000_000

pregunta = "Confirma en una frase corta que esta conexión funciona"
try:
    resultado = obtener_dato_de_prueba(pregunta, PRECIO_ENTRADA, PRECIO_SALIDA)
    print(resultado["texto"])
    print(f"Costo de la peticion: {resultado['costo']:.6f} USD")
except (ValueError, RuntimeError) as error:
    print(f"[ERROR] No se pudo completar la operación: {type(error).__name__}: {error}")