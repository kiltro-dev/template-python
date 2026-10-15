import os
import requests
from dotenv import load_dotenv

load_dotenv()


# def obtener_dato_de_prueba(pregunta):
#     api_key = os.getenv("GEMINI_API_KEY")
#     modelo = "gemini-3.6-flash"
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
#     headers = {"x-goog-api-key": api_key}
#     body = {"contents": [{"parts": [{"text": pregunta}]}]}
#     respuesta = requests.post(url, headers=headers, json=body)
#     datos = respuesta.json()
#     return datos["candidates"][0]["content"]["parts"][0]["text"]

def armar_peticion(pregunta):
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = "gemini-3.5-flash-lite"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    headers = {"x-goog-api-key": api_key}
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    return url, body, headers

def enviar_peticion(url, body, headers):
    respuesta = requests.post(url, headers=headers, json=body)
    return respuesta.json()

def extraer_texto(datos):
    return datos["candidates"][0]["content"]["parts"][0]["text"]

def obtener_dato_de_prueba(pregunta):
    url, body, headers = armar_peticion(pregunta)
    datos = enviar_peticion(url, body, headers)
    return extraer_texto(datos)

print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona"))