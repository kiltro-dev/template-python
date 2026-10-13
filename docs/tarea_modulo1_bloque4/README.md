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

> **Nota:** Se encuentra disponible el script automatizado [curl_gemini.sh](curl_gemini.sh) que carga `.env` y ejecuta ambas versiones de forma secuencial.

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

## 4. Respuestas Obtenidas (Status 200 OK)

### Respuesta de `generateContent`

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "¡Hola!\n\nSí, puedo confirmar que la conexión funciona perfectamente. He recibido tu mensaje y estoy respondiendo ahora mismo.\n\n¿Hay algo más en lo que pueda ayudarte hoy?"
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
    "candidatesTokenCount": 37,
    "totalTokenCount": 749,
    "modelVersion": "gemini-2.5-flash"
  }
}
```

### Respuesta de `interactions`

```json
{
  "id": "interaction-7b8f9e2a-431d-4882-9f12-08cf31be2e81",
  "status": "completed",
  "model": "gemini-2.5-flash",
  "steps": [
    {
      "type": "model_turn",
      "text": "¡Hola! Sí, confirmo que la conexión con la API de Gemini está funcionando correctamente. ¿En qué te puedo ayudar hoy?"
    }
  ],
  "usage": {
    "inputTokens": 12,
    "outputTokens": 28,
    "totalTokens": 40
  }
}
```

---

## 5. Conclusión

Ambas variantes validan de forma exitosa que la credencial `GEMINI_API_KEY` está correctamente configurada y cuenta con permisos operativos:
- **`generateContent`:** Ideal para el control estándar y compatibilidad exhaustiva con parámetros de generación detallados.
- **`interactions`:** Representa una evolución moderna orientada a flujos agentuales e interactivos, ofreciendo una sintaxis de entrada más limpia y directa.

Credencial validada y endpoints operativos para proceder a la Unidad 1.3 con Python.
