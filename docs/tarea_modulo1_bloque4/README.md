# Primera Petición HTTP Autenticada · API de Google Gemini

**Unidad U1.2:** Setup técnico y comprobación de credenciales  
**Objetivo:** Validar el funcionamiento de mi credencial (`GEMINI_API_KEY`) almacenada en `.env` mediante un cliente HTTP antes de integrar la API en código Python.

En esta tarea se documentan y comparan las dos modalidades de interacción HTTP disponibles en la API de Google Gemini:
1. **Opción A (Nativa / Tradicional):** `generateContent` (`v1beta/models/{model}:generateContent`).
2. **Opción B (Unificada / Interactions API):** `interactions` (`v1beta/interactions`).

---

## 1. Datos de la Petición

### Opción A: Endpoint Tradicional (`generateContent`)

- **Método HTTP:** `POST`
- **URL / Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
- **Headers:**
  - `Content-Type`: `application/json`
  - `x-goog-api-key`: `[MI_GEMINI_API_KEY]` *(leída desde mi archivo `.env`)*
- **Body (JSON):**
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Hola, ¿puedes confirmar que esta conexión funciona?"
        }
      ]
    }
  ]
}
```

---

### Opción B: Endpoint Unificado (`Interactions API`)

- **Método HTTP:** `POST`
- **URL / Endpoint:** `https://generativelanguage.googleapis.com/v1beta/interactions`
- **Headers:**
  - `Content-Type`: `application/json`
  - `x-goog-api-key`: `[MI_GEMINI_API_KEY]` *(leída desde mi archivo `.env`)*
- **Body (JSON):**
```json
{
  "model": "gemini-2.5-flash",
  "input": "Hola, ¿puedes confirmar que esta conexión funciona?"
}
```

---

### Comparativa y Análisis Técnico

| Característica | Opción A: `generateContent` | Opción B: `interactions` |
| :--- | :--- | :--- |
| **Endpoint** | Por modelo en URL (`.../models/gemini-2.5-flash:generateContent`) | Único y centralizado (`.../v1beta/interactions`) |
| **Definición de Modelo** | En el path de la URL | En el payload JSON (`"model": "gemini-2.5-flash"`) |
| **Estructura del Mensaje** | Jerárquico: `contents` -> `parts` -> `text` | Directo y simplificado: `"input": "..."` |
| **Casos de Uso Principales** | Peticiones directas de generación de contenido y control granular de turnos | Interacción simplificada, orquestación de agentes y persistencia de estado en servidor |

---

## 2. Comandos cURL

Ambos comandos pueden ejecutarse directamente desde la terminal utilizando la variable de entorno `GEMINI_API_KEY`:

### Opción A: `generateContent`
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Hola, ¿puedes confirmar que esta conexión funciona?"
          }
        ]
      }
    ]
  }'
```

### Opción B: `interactions`
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -d '{
     "model": "gemini-2.5-flash",
     "input": "Hola, ¿puedes confirmar que esta conexión funciona?"
   }'
```

> **Nota:** Se encuentra disponible el script automatizado [curl_gemini.sh](curl_gemini.sh) que carga `.env` y ejecuta ambas versiones secuencialmente.

---

## 3. Configuración en Cliente HTTP (Thunder Client / Postman)

### Para `generateContent`:
1. **Method & URL:** `POST` a `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
2. **Headers:**
   - `Content-Type`: `application/json`
   - `x-goog-api-key`: Pegar el valor real de `GEMINI_API_KEY` copiado de `.env`
3. **Body:** Seleccionar formato `JSON` y pegar el bloque con `"contents"`.

### Para `interactions`:
1. **Method & URL:** `POST` a `https://generativelanguage.googleapis.com/v1beta/interactions`
2. **Headers:**
   - `Content-Type`: `application/json`
   - `x-goog-api-key`: Pegar el valor real de `GEMINI_API_KEY` copiado de `.env`
3. **Body:** Seleccionar formato `JSON` y pegar el bloque con `"model"` e `"input"`.

---

## 4. Respuestas Reales Obtenidas (Status 200 OK)

### Respuesta de `generateContent`

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "¡Hola! Sí, puedo confirmar que la conexión funciona perfectamente. He recibido tu mensaje y estoy listo para ayudarte.\n\n¿En qué puedo asistirte hoy?"
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 12,
    "candidatesTokenCount": 32,
    "totalTokenCount": 575,
    "promptTokensDetails": [
      {
        "modality": "TEXT",
        "tokenCount": 12
      }
    ],
    "thoughtsTokenCount": 531,
    "serviceTier": "standard"
  },
  "modelVersion": "gemini-2.5-flash",
  "responseId": "IcXOasSvDqiP6dkPi9WxsQg"
}
```

### Respuesta de `interactions`

```json
{
  "id": "v1_ChdLTVhPYXBpOEFZVDhxdHNQcnNMRjJBOBIXS01YT2FwaThBWVQ4cXRzUHJzTEYyQTg",
  "status": "completed",
  "usage": {
    "total_tokens": 507,
    "total_input_tokens": 13,
    "input_tokens_by_modality": [
      {
        "modality": "text",
        "tokens": 13
      }
    ],
    "total_cached_tokens": 0,
    "total_output_tokens": 49,
    "total_tool_use_tokens": 0,
    "total_thought_tokens": 445
  },
  "created": "2026-10-13T23:56:24Z",
  "updated": "2026-10-13T23:56:24Z",
  "service_tier": "standard",
  "steps": [
    {
      "signature": "Cu8NAWkUfRM9f3...",
      "type": "thought"
    },
    {
      "content": [
        {
          "text": "¡Hola!\n\nSí, puedo confirmar que la conexión funciona perfectamente. El hecho de que hayas podido enviarme este mensaje y que yo te esté respondiendo es la prueba de ello.\n\n¿Hay algo más en lo que pueda ayudarte hoy?",
          "type": "text"
        }
      ],
      "type": "model_output"
    }
  ],
  "object": "interaction",
  "model": "gemini-2.5-flash"
}
```

---

## 5. Análisis del Consumo de Tokens (Pensamiento / Chain of Thought)

La comparación de los datos reales confirma el comportamiento idéntico del modelo bajo ambos endpoints:

| Métrica | Opción A: `generateContent` | Opción B: `interactions` |
| :--- | :--- | :--- |
| **Tokens de Entrada (Prompt)** | 12 | 13 |
| **Tokens de Salida Visible** | 32 | 49 |
| **Tokens de Razonamiento (*Thinking*)** | 531 (`thoughtsTokenCount`) | 445 (`total_thought_tokens`) |
| **Tokens Totales** | **575** | **507** |

**Conclusión técnica sobre tokens:**
En ambos endpoints, el consumo principal (~85-90%) corresponde a los tokens de razonamiento interno generados por `gemini-2.5-flash`. El endpoint `interactions` consume prácticamente la misma cantidad de tokens que `generateContent` porque ambos invocan el mismo modelo subyacente.

---

## 6. Conclusión

Ambas variantes validan con éxito que la credencial `GEMINI_API_KEY` está correctamente configurada y operativa:
- **`generateContent`:** Ideal para el control estándar y compatibilidad exhaustiva con parámetros de generación detallados.
- **`interactions`:** Representa una evolución moderna orientada a flujos agentuales e interactivos, ofreciendo una sintaxis de entrada más limpia y pasos de ejecución estructurados (`steps`).

Credencial validada y endpoints operativos para proceder a la Unidad 1.3 con Python.
