# Diagrama de Arquitectura de la Miniaplicación

**Unidad U1.4 · Bloque 8 · Arquitectura de una aplicación generativa, paso a paso**
**Tipo:** Actividad práctica

En esta actividad se documenta la arquitectura real de mi miniaplicación de consumo de la API de Gemini: las funciones del módulo `src/consumir_gemini.py`, la ubicación de la credencial, el manejo de errores, y el cálculo del costo a partir de `usageMetadata`.

---

## 1. Contenido de esta carpeta

| Archivo | Qué es |
| :--- | :--- |
| `diagrama_arquitectura.png` | **Entregable.** Diagrama de arquitectura exportado como imagen |
| `diagrama_arquitectura.mmd` | Fuente del diagrama en Mermaid.js (editable y re-exportable) |
| `respuesta_real.json` | Respuesta real de la API capturada al probar el sistema |
| `README.md` | Este documento |

---

## 2. Elementos del diagrama (checklist de la actividad)

| # | Requisito | Cómo aparece en el diagrama |
| :--- | :--- | :--- |
| 1 | Las funciones como cajas separadas, en orden | `armar_peticion` → `enviar_peticion` → `extraer_texto`, además de `calcular_costo` y el orquestador `obtener_dato_de_prueba` |
| 2 | Dónde vive `GEMINI_API_KEY` y dónde se usa | Caja `.env` (amarilla) → se lee con `os.getenv` dentro de `armar_peticion`, y viaja en el header `x-goog-api-key` |
| 3 | Manejo de errores | Cada función muestra su `try` y su `except` con la excepción exacta (ver sección 3) |
| 4 | Dónde entra `usageMetadata` y dónde se calcula el costo | El nodo `datos` bifurca: rama sólida a `extraer_texto`, rama punteada de `usageMetadata` a `calcular_costo` |
| 5 | Cada flecha etiquetada con el dato que transporta | `pregunta (str)`, `GEMINI_API_KEY (str)`, `url · body · headers`, `HTTP POST`, `JSON crudo`, `datos (dict)`, `texto generado (str)`, `costo (float, USD)` |

---

## 3. Manejo de errores (punto 3 del checklist)

Detalle de los `try/except` implementados en `src/consumir_gemini.py`:

| Función | Protege | Excepción capturada | Se convierte en |
| :--- | :--- | :--- | :--- |
| `armar_peticion` | Pregunta vacía | `ValueError` | se propaga (validación de entrada) |
| `armar_peticion` | Falta `GEMINI_API_KEY` | `RuntimeError` | se propaga (configuración ausente) |
| `enviar_peticion` | `requests.post` | `requests.exceptions.ConnectionError` | `RuntimeError` (sin conexión) |
| `enviar_peticion` | `respuesta.json()` | `requests.exceptions.JSONDecodeError` | `RuntimeError` (formato inesperado) |
| `extraer_texto` | Extracción del texto | `(KeyError, IndexError)` | `RuntimeError` (sin texto generado) |
| `calcular_costo` | Lectura de `usageMetadata` | `(KeyError, TypeError)` | `RuntimeError` (sin uso de tokens) |
| `main` / `obtener_dato_de_prueba` | Flujo completo | `(ValueError, RuntimeError)` | mensaje `[ERROR]` amigable |

---

## 4. Función `calcular_costo` (agregada en esta actividad)

Hermana de `extraer_texto`: recibe la misma respuesta cruda `datos` y calcula el costo de la petición a partir de `usageMetadata`:

```python
def calcular_costo(datos, precio_entrada, precio_salida):
    try:
        uso = datos["usageMetadata"]
        tokens_entrada = uso["promptTokenCount"]
        tokens_salida = uso["candidatesTokenCount"]
    except (KeyError, TypeError):
        raise RuntimeError("La respuesta no trae el uso de tokens en el lugar esperado.")
    return (tokens_entrada * precio_entrada) + (tokens_salida * precio_salida)
```

Fórmula:

```
costo = (promptTokenCount * precio_entrada) + (candidatesTokenCount * precio_salida)
```

Los precios se pasan como parámetros (no van fijos en el código) porque cambian según modelo y proveedor, y siempre se confirman en la página de precios vigente.

---

## 5. Pruebas ejecutadas (`src/probar_costo.py`)

Las cuatro pruebas pasaron:

| # | Prueba | Resultado |
| :--- | :--- | :--- |
| 1 | Ejemplo de la lección (850 entrada + 320 salida, precios de ejemplo) | `0.000213 USD` — coincide con la fórmula |
| 2 | El costo cambia al duplicar el precio de salida | `0.000300 USD` → `0.000500 USD` |
| 3 | Sin `usageMetadata` | `RuntimeError` capturado correctamente |
| 4 | Petición real a la API | Ver datos reales abajo |

---

## 6. Datos reales de la petición

Capturados con el módulo propio (`armar_peticion` → `enviar_peticion` → `extraer_texto` → `calcular_costo`) contra el modelo `gemini-3.5-flash-lite`. El JSON completo está en [`respuesta_real.json`](respuesta_real.json).

**Pregunta enviada:** `Confirma en una frase corta que esta conexión funciona`

**Respuesta generada (en `respuesta_real.json`):** `¡Conexión establecida y funcionando al 100%!`

**Consumo real de tokens (`usageMetadata`):**

| Métrica | Valor |
| :--- | --- |
| `promptTokenCount` (entrada) | 10 |
| `candidatesTokenCount` (salida) | 13 |
| `totalTokenCount` | 23 |

**Costo con precios de ejemplo** (`0.00000010` entrada / `0.00000040` salida):

```
costo = (10 * 0.00000010) + (13 * 0.00000040)
      = 0.00000100 + 0.00000520
      = 0.0000062 USD
```

> **Nota:** los precios usados en las pruebas son de ejemplo, para verificar la mecánica de la fórmula. Los precios reales se consultan en la página de precios vigente del proveedor.

**Observación sobre variabilidad:** las pruebas se corrieron varias veces con la misma pregunta. `promptTokenCount` se mantuvo estable en 10, pero `candidatesTokenCount` varió entre corridas (10, 13, ...), porque la longitud de la respuesta generada no es idéntica entre peticiones. Es exactamente la razón por la que el costo se calcula en vivo con `usageMetadata` y no se estima por adelantado.

---

## 7. Herramienta usada

El diagrama se generó con **Mermaid.js** (librería de diagramas en JavaScript), a partir del archivo fuente `diagrama_arquitectura.mmd`, y se exportó a PNG. El archivo `.mmd` queda versionado para poder editar y re-exportar el diagrama cuando la arquitectura cambie (por ejemplo, en el Bloque 9).

---

## 8. Cómo re-exportar el diagrama

```bash
npm install --no-save @mermaid-js/mermaid-cli
npx mmdc -i docs/tarea_modulo1_bloque8/diagrama_arquitectura.mmd \
         -o docs/tarea_modulo1_bloque8/diagrama_arquitectura.png \
         -b white -s 2
```
