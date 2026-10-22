# Banco de prompts y validación de consistencia

**Unidad U1.5 · Bloque 10 · Actividad core**

Banco de prompts de la miniaplicación, con evidencia de consistencia medida contra la API real.

## Contenido

| Archivo | Qué es |
| :--- | :--- |
| `banco.py` | Banco de **5 prompts** (mínimo pedido: 3). Cada uno con `system_instruction`, ejemplo de entrada, `claves_esperadas` y `response_schema` |
| `test_consistencia.py` | Script de prueba: 3 repeticiones por prompt contra la API real, valida JSON + estructura, y escribe el registro |
| `registro_resultados.json` | Registro de resultados (evidencia versionada) |

## Cómo correrlo

```bash
python prompts/test_consistencia.py                      # todos los prompts
python prompts/test_consistencia.py detectar_idioma      # solo uno
python prompts/test_consistencia.py modelo=gemini-3.5-flash   # otro modelo
```

El registro se mergea entre corridas: cada prompt guarda su propio resultado y el modelo con el que se midió.

## Resultado final (2026-10-21)

| Prompt | Consistencia | Modelo medido |
| :--- | :--- | :--- |
| clasificar_sentimiento | 3/3 | gemini-2.5-flash |
| clasificar_consulta | 3/3 | gemini-2.5-flash |
| extraer_entidades | 3/3 | gemini-2.5-flash |
| generar_resumen | 3/3 | gemini-2.5-flash |
| detectar_idioma | 3/3 | gemini-3.5-flash |

## Iteraciones realizadas (qué se ajustó y cómo mejoró)

**Corrida 1 (pausa de 1 s entre llamadas):** 3/5 prompts en 3/3. Los dos fallos fueron **de API, no de redacción**:
- `clasificar_sentimiento` 0/3 — tres `503 UNAVAILABLE` (alta demanda del servicio).
- `extraer_entidades` 2/3 — un `429 RESOURCE_EXHAUSTED` (cuota corta, `limit: 5`).

**Ajuste 1:** se subió `PAUSA_ENTRE_LLAMADAS` de 1 s a 3 s (la solución que sugiere la lección para 429) y se separaron en el registro los `fallos_api` de los `fallos_estructura`, para poder distinguir un prompt inconsistente de un servicio saturado.

**Corrida 2 (pausa de 3 s):** 4/5 prompts en 3/3, **cero fallos de estructura**. `detectar_idioma` quedó 0/3 por cuota **diaria** de `gemini-2.5-flash` agotada (`limit: 20`, reintento en ~7 h) — el prompt nunca llegó a evaluarse en esa corrida.

**Ajuste 2:** como la cuota es por modelo y `gemini-3.5-flash` tenía cupo disponible, se completó la medición de `detectar_idioma` con ese modelo (3/3). El modelo queda anotado por prompt en el registro, para que la evidencia sea transparente.

**Nota sobre los tipos de fallo:** en ninguna corrida hubo `fallos_estructura` (JSON malformado o claves faltantes). Todos los intentos que llegaron a la API devolvieron JSON válido con las claves esperadas, gracias a `systemInstruction` + `responseSchema` (`generationConfig`). Los únicos fallos fueron de disponibilidad del servicio (503/429).

## Esquemas usados

Los `response_schema` usan el enum real del endpoint `models.generateContent`: `OBJECT`, `STRING`, `NUMBER`, `ARRAY` (verificado contra el discovery document de la API v1beta). El campo de prompt de sistema es `systemInstruction` (camelCase) y el de salida estructurada `generationConfig.responseMimeType` + `generationConfig.responseSchema`.
