"""Pruebas de calcular_costo con datos sintéticos, caso de error y una petición real."""

from consumir_gemini import (
    armar_peticion,
    calcular_costo,
    enviar_peticion,
    extraer_texto,
)

# Precios de ejemplo (inventados, solo para verificar la mecánica de la fórmula).
# Los precios reales se confirman en la página de precios vigente del proveedor.
PRECIO_ENTRADA = 0.00000010
PRECIO_SALIDA = 0.00000040


def probar_con_datos_del_ejemplo():
    datos = {
        "usageMetadata": {
            "promptTokenCount": 850,
            "candidatesTokenCount": 320,
            "totalTokenCount": 1170,
        }
    }
    costo = calcular_costo(datos, PRECIO_ENTRADA, PRECIO_SALIDA)
    print("1) Datos del ejemplo de la lección")
    print(f"   850 entrada + 320 salida -> {costo:.6f} USD (esperado: 0.000213)")
    assert abs(costo - 0.000213) < 1e-12, "El costo del ejemplo no coincide con la fórmula"


def probar_que_el_costo_cambia():
    datos = {
        "usageMetadata": {
            "promptTokenCount": 1000,
            "candidatesTokenCount": 500,
            "totalTokenCount": 1500,
        }
    }
    costo_base = calcular_costo(datos, PRECIO_ENTRADA, PRECIO_SALIDA)
    costo_mas_salida = calcular_costo(datos, PRECIO_ENTRADA, PRECIO_SALIDA * 2)
    print("2) El resultado cambia como espera la fórmula")
    print(f"   base: {costo_base:.6f} USD | salida x2: {costo_mas_salida:.6f} USD")
    assert costo_mas_salida > costo_base, "Duplicar el precio de salida debía encarecer la petición"


def probar_error_sin_usage_metadata():
    datos = {"candidates": []}
    try:
        calcular_costo(datos, PRECIO_ENTRADA, PRECIO_SALIDA)
    except RuntimeError as error:
        print("3) Caso de error (sin usageMetadata)")
        print(f"   RuntimeError capturado: {error}")
    else:
        raise AssertionError("Debía lanzar RuntimeError si falta usageMetadata")


def probar_peticion_real():
    print("4) Petición real a la API")
    pregunta = "Confirma en una frase corta que esta conexión funciona"
    url, body, headers = armar_peticion(pregunta)
    datos = enviar_peticion(url, body, headers)
    texto = extraer_texto(datos)
    uso = datos["usageMetadata"]
    costo = calcular_costo(datos, PRECIO_ENTRADA, PRECIO_SALIDA)
    print(f"   Texto: {texto}")
    print(f"   Tokens de entrada: {uso['promptTokenCount']}")
    print(f"   Tokens de salida:  {uso['candidatesTokenCount']}")
    print(f"   Total:             {uso['totalTokenCount']}")
    print(f"   Costo con precios de ejemplo: {costo:.6f} USD")
    return datos


if __name__ == "__main__":
    probar_con_datos_del_ejemplo()
    probar_que_el_costo_cambia()
    probar_error_sin_usage_metadata()
    respuesta_real = probar_peticion_real()
    print("\nTodas las pruebas pasaron.")
