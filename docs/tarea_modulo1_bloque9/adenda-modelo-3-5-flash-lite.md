# Adenda: uso operativo de `gemini-3.5-flash-lite` (cuota)

> **Nota del 2026-11-02:** el modo transitorio descrito aquí pasó a ser la decisión permanente en [cambio-decision-modelo.md](cambio-decision-modelo.md). Lo de abajo se conserva intacto como registro de la semana en que convivieron ambos regímenes.

**Fecha de la adenda:** 2026-10-30
**Alcance:** modelo usado en las corridas de evaluación (Bloques 15-17) y en adelante.
**No modifica** la decisión del 2026-10-20 (`gemini-2.5-flash` sigue siendo el modelo elegido y el default del código): la registra como sigue vigente y agrega un modo operativo por restricción de cuota.

## Qué cambia

- `src/cliente.py` suma `gemini-3.5-flash-lite` a `PRECIOS` (0.30/2.50 USD por 1M de tokens entrada/salida, mismos que 2.5-flash; sin promoción con vencimiento; fuente: `ai.google.dev/gemini-api/docs/pricing`, consultada el 2026-10-30).
- Las corridas de evaluación que choquen con la cuota de 2.5-flash usan `modelo="gemini-3.5-flash-lite"` por parámetro. El default del código no cambia.
- `tests/test_cliente.py` suma 2 pruebas con el lite (acepta el modelo, registra costo con sus precios).

## Por qué

Cuota del free tier agotada en `gemini-2.5-flash`, medida en el dashboard de AI Studio (proyecto Default Gemini Project, 2026-10-30): RPM 8/5 y **RPD 27/20** (el diario resetea a medianoche hora del Pacífico). Con el diario pasado, ningún backoff la recupera en el día: 9 casos seguidos fallaron sus 3-6 reintentos.

`gemini-3.5-flash-lite` tenía a esa fecha RPM 0/10, TPM 0/250K y RPD 0/20: margen completo. A igual precio que 2.5-flash, el cambio no altera la economía del proyecto.

## Qué se conserva del ADR original

- La comparación de costo/latencia/calidad/disponibilidad del 2026-10-20 y su conclusión.
- `gemini-2.5-flash` como default en `armar_peticion` y `consultar_modelo`.
- El descarte de `gemini-3.6-flash` (además saturado: RPD 22/20 el mismo día).

## Consecuencia registrada

La evaluación del Bloque 17 quedó en modelo mixto: 13 respuestas con 2.5-flash y 7 con 3.5-flash-lite. Consta en `docs/limites_metrica.md` como condición de la medición, no como defecto.
