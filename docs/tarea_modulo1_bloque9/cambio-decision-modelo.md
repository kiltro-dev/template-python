# Cambio de decisión: `gemini-3.5-flash-lite` como modelo por defecto

**Fecha del cambio:** 2026-11-02
**Estado:** vigente.
**Reemplaza a** [`decision-arquitectura.md`](decision-arquitectura.md) (2026-10-20), que se conserva intacta como historia.
**Absorbe a** [`adenda-modelo-3-5-flash-lite.md`](adenda-modelo-3-5-flash-lite.md) (2026-10-30): el modo operativo transitorio pasa a ser la decisión permanente.

## Decisión

**`gemini-3.5-flash-lite` es desde ahora el modelo por defecto**, en `consultar_modelo` (`src/cliente.py`) y en `armar_peticion` (`src/consumir_gemini.py`), siempre cambiable por parámetro. `gemini-2.5-flash` sigue soportado en `PRECIOS`; no se elimina.

## Contexto

El 2026-10-30 la cuota gratuita de `gemini-2.5-flash` se agotó a mitad de la evaluación (RPD 27/20): 9 casos seguidos fallaron sus reintentos y 7 se corrieron con el lite por parámetro, registrando el modo transitorio en la adenda. Las mediciones del 2026-11-02 permiten convertir ese modo en decisión definitiva, con una sorpresa (latencia) que queda registrada abajo tal cual.

## Evidencia nueva (lite vs 2.5-flash)

| Criterio | gemini-2.5-flash | gemini-3.5-flash-lite |
|---|---|---|
| Precio oficial (USD/1M, entrada/salida) | 0,30 / 2,50 | 0,30 / 2,50 (mismo; sin promo con vencimiento) |
| Latencia, misma ventana 2026-11-02 (4 intentos) | 5,78 s promedio (5,08 – 6,48) | 29,08 s promedio (22,65 – 36,02) |
| Costo observado por petición, misma ventana | 0,000013 – 0,000021 USD | 0,000026 – 0,000036 USD (~2×, por más tokens de salida: 9–13 vs 4–7) |
| Calidad en la evaluación (Bloque 17) | 13 casos, F1 prom. 0,85 | 7 casos, F1 prom. 0,71; cero errores factuales y cero contradicciones según rúbrica |
| Disponibilidad observada | 4/4 en la ventana del 02/11; RPD 27/20 el 30/10 (cuota llena) | 7/7 en eval + 4/4 en latencia; RPD 10/500 (margen amplio) |
| Cuota diaria gratuita (RPD) | 20 | 500 (25×) |

**Método de la ventana del 02/11:** misma pregunta corta de `comparar_modelos.py`, 4 intentos por modelo **alternados** (2.5, lite, 2.5, …) para repartir la carga del proveedor, timeout de 60 s en vez de 10 s porque el lite superaba los 10 s en todos los intentos. Las respuestas del lite traían `thoughtSignature`, indicio (sin confirmar) de pensamiento activado como causa del sobrecosto en tiempo y tokens.

**Transparencia:** el F1 promedio por modelo no es comparable limpiamente porque cada modelo respondió preguntas distintas; los puntajes bajos del lite (0,33 y 0,38) están explicados por verbosidad en la revisión manual, no por errores. La latencia del lite viene de una sola ventana y debe **re-medirse** antes de tratarla como definitiva; lo que sí es firme es que en esa ventana perdió el vértice por ~5× de forma consistente (los 4 intentos lentos con los del 2.5 intercalados rápidos).

## Justificación

El mismo criterio que decidió la original: **costo por interacción y disponibilidad combinados**. En tarifa empatan; en disponibilidad el lite gana por 25× de cuota frente a un 2.5 que ya demostró agotarse a mitad del trabajo. En free tier, un modelo rápido sin cuota sirve menos que uno lento con cuota: la decisión original descartó al 3.6-flash por exactamente esa razón (RPD 20), y el 2.5 tiene el mismo techo.

Se **cede el vértice latencia explícitamente**, y más caro que en la decisión original: 29 s no es "unos pocos segundos". Es el costo conocido del cambio, a re-medir; si una medición futura muestra al lite competitivo en velocidad, se registra sin cambiar la decisión (la disponibilidad seguiría decidiendo igual).

## Consecuencias

- Default en `consultar_modelo` y `armar_peticion` → `gemini-3.5-flash-lite`. Los scripts que usan el default (`main.py`, `evaluar_cliente.py`, `probar_costo.py`, `pipeline_texto.py`) usan el lite sin cambios.
- `tests/test_cliente.py`: 2 pruebas del lite (existentes) + 1 que fija el nuevo default. Suite 22/22.
- README actualizado en las líneas que describen el presente (firma y decisión de modelo); los ensayos fechados no se tocan.
- Evidencia histórica intacta: los 13 casos con 2.5-flash, `comparativa_modelos.json` y la decisión del 20/10 siguen siendo válidos para lo que midieron. `docs/limites_metrica.md` ya registra la condición mixta de la medición.
