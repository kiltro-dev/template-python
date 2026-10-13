# Primera Petición HTTP Autenticada · API de Google Gemini

**Unidad U1.2:** Setup técnico y comprobación de credenciales  
**Objetivo:** Validar el funcionamiento de mi credencial (`GEMINI_API_KEY`) almacenada en `.env` mediante un cliente HTTP antes de integrar la API en código Python.

---

## 1. Datos de la Petición

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

> **Nota técnica:** A diferencia del formato estándar tipo OpenAI (`Authorization: Bearer` y estructura `messages`), la API nativa de Google Gemini requiere autenticación mediante el encabezado `x-goog-api-key`, define el modelo en la URL y utiliza la clave `contents` con objetos `parts`.

---

## 2. Comando cURL

Para reproducir la prueba directamente desde la terminal con mi variable de entorno:

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

*(Script ejecutable disponible en `curl_gemini.sh`)*.

---

## 3. Configuración en Cliente HTTP (Thunder Client / Postman)

1. **Method & URL:** `POST` a `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
2. **Headers:**
   - `Content-Type`: `application/json`
   - `x-goog-api-key`: Pegar el valor real de `GEMINI_API_KEY` copiado de `.env`
3. **Body:** Seleccionar formato `JSON` y pegar el bloque con `"contents"`.

---

## 4. Respuesta Obtenida (Status 200 OK)

La petición fue exitosa y la API retornó la siguiente respuesta:

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

**Conclusión:** Credencial validada y endpoint operativo para proceder a la Unidad 1.3 con Python.
