#!/usr/bin/env bash
# Cargar variable de entorno desde .env si existe
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
elif [ -f ../../.env ]; then
  export $(grep -v '^#' ../../.env | xargs)
fi

# Disparo a la API de Google Gemini (generateContent)
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
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
