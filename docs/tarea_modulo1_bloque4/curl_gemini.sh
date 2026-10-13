#!/usr/bin/env bash
# Cargar variable de entorno desde .env si existe
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
elif [ -f ../../.env ]; then
  export $(grep -v '^#' ../../.env | xargs)
fi

echo "=================================================================="
echo " Opción 1: Endpoint Tradicional (models/gemini-2.5-flash:generateContent)"
echo "=================================================================="
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

echo -e "\n\n=================================================================="
echo " Opción 2: Endpoint Unificado (Interactions API /v1beta/interactions)"
echo "=================================================================="
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -d '{
     "model": "gemini-2.5-flash",
     "input": "Hola, ¿puedes confirmar que esta conexión funciona?"
   }'
echo ""
