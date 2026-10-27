# Miniaplicación con API de Gemini

> **Especialización en Desarrollo con IA Generativa (Accenture) — Gate 1 aprobado · Módulo 2 en curso**
>
> Miniaplicación que envía preguntas a la API de Gemini vía REST y devuelve la respuesta. El proyecto incluye además el cálculo del costo real por petición, manejo de errores, prompts de sistema, salida JSON estructurada, un banco de prompts con validación de consistencia y un cliente modular con reintento y clasificación de errores.

Este repositorio es el proyecto único del programa: nace como esta miniaplicación (Módulo 1) y crece hasta la aplicación generativa completa del Gate 3 (Módulo 2: LangChain, agentes y RAG · Módulo 3: FastAPI, Docker y QA).

---

## Requisitos

- Python 3.12+ · Git · una API key de [Google AI Studio](https://aistudio.google.com/apikey)

## Instalación

```bash
git clone https://github.com/kiltro-dev/template-python.git
cd template-python

python3 -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env              # Windows: Copy-Item .env.example .env
```

Abrir `.env` y completar `GEMINI_API_KEY` con tu credencial real — es la única variable que usa el código. `.env` nunca se sube a Git (excluido en `.gitignore`); solo `.env.example` viaja en el repositorio.

## Ejecutar

```bash
python src/main.py
```

```
Confirmado: la conexión funciona.
```

✅ Éxito = respuesta del modelo impresa y proceso terminado sin `Traceback` (el texto varía en cada corrida).

## Estructura del repositorio

```
├── src/
│   ├── consumir_gemini.py     # módulo principal: cliente REST de la API
│   ├── cliente.py             # cliente modular: consultar_modelo con reintento y clasificación de errores
│   ├── main.py                # punto de entrada de la miniaplicación
│   ├── probar_costo.py        # pruebas de calcular_costo
│   ├── comparar_modelos.py    # medición de latencia/costo/calidad (evidencia del ADR)
│   ├── monolitico.py          # legado de bloques previos
│   └── test_conexion.py       # legado de bloques previos
├── prompts/                   # banco de 5 prompts + validación de consistencia
├── docs/                      # diagrama de arquitectura, decisión de modelo, evidencias
├── tests/                     # reservado para pruebas automatizadas (Módulo 2)
├── requirements.txt
├── .env.example
└── .gitignore
```

## Comandos disponibles

Desde la raíz del repositorio, con el entorno virtual activo:

| Comando | Qué hace | Evidencia |
| :--- | :--- | :--- |
| `python src/main.py` | Miniaplicación: pregunta → respuesta | consola |
| `python src/cliente.py` | Ensayo de rate limit: 10 consultas seguidas con reintento y costo | consola |
| `python src/probar_costo.py` | Pruebas de `calcular_costo` (datos sintéticos + petición real) | consola |
| `python src/comparar_modelos.py` | Latencia, costo y calidad de 2 modelos | `docs/tarea_modulo1_bloque9/comparativa_modelos.json` |
| `python prompts/test_consistencia.py` | Banco de prompts, 3 repeticiones c/u | `prompts/registro_resultados.json` |

## El módulo (`src/consumir_gemini.py`)

Cliente REST con funciones separadas y su propio manejo de errores: `armar_peticion` (arma la petición, acepta `system_instruction` y `response_schema`), `enviar_peticion` (envía, clasifica el error y expone el detalle real de la API), `extraer_texto` (camino texto), `calcular_costo` (camino costo, desde `usageMetadata`), `parsear_respuesta_json` (camino JSON) y `obtener_dato_de_prueba` (orquesta el flujo principal). Cada consumidor usa el subconjunto que necesita: la miniaplicación usa el flujo texto; los scripts usan costo y JSON.

**Clasificación de errores (Módulo 2):** `enviar_peticion` distingue lo que no se resuelve reintentando (`ValueError`: credencial inválida o sin permiso) de lo que es temporal (`TimeoutError`: límite de uso, falla del proveedor o de red).

## El cliente modular (`src/cliente.py`)

Punto de entrada único `consultar_modelo(pregunta, system_instruction="", modelo="gemini-2.5-flash")`: arma la petición, la envuelve en `con_reintento` (3 intentos, backoff exponencial con tope de 30 s y jitter cuando el error es temporal), registra el costo de cada operación con `registrar_costo` (entrada y salida por separado con los precios del modelo, acumulado de sesión), extrae el texto y traduce los reintentos agotados a un `RuntimeError` con mensaje claro. El `ValueError` de credencial se propaga sin reintentar.

## Documentación y evidencias

- 🏗️ **[Diagrama de arquitectura](docs/tarea_modulo1_bloque8/diagrama_arquitectura.png)** — flujo completo, credenciales, errores y cálculo de costo
- ⚖️ **[Decisión de modelo](docs/tarea_modulo1_bloque9/decision-arquitectura.md)** — `gemini-2.5-flash` elegido con datos reales de costo, latencia, calidad y disponibilidad
- 🧩 **[Banco de prompts](prompts/README.md)** — 5 prompts, consistencia 3/3 medida contra la API

## Seguridad

```bash
git ls-files | grep .env         # debe listar solo .env.example
git log --all --oneline -- .env  # no debe devolver nada
```

## Registro del ensayo de instalación limpia

- **Fecha:** 2026-10-22
- **Método:** clonado del repositorio remoto a una carpeta limpia, entorno virtual nuevo desde cero, instalación únicamente desde `requirements.txt`, y ejecución siguiendo los pasos de este README
- **Encontrado:** sin hallazgos
- **Resultados:**
  - entorno virtual nuevo: solo `pip 24.0` antes de instalar (Python 3.12.3) — sin librerías heredadas
  - `pip install -r requirements.txt`: 26 paquetes instalados sin errores
  - `python src/main.py`: respuesta del modelo, proceso terminado sin errores
  - seguridad en la copia clonada: `git status` no lista `.env` · `git ls-files | grep .env` solo `.env.example` · `git log --all -- .env` sin resultados (la credencial nunca se commiteó)
- **Corregido:** —

## Registro del ensayo de rate limit (Bloque 13)

- **Fecha:** 2026-10-26 · **Modelo:** `gemini-3.6-flash` (cupos más bajos que el modelo por defecto; elegido a propósito para provocar el límite)
- **Peticiones enviadas:** 10 (bucle de `python src/cliente.py`, sin esperas entre llamadas)
- **Petición donde apareció el primer 429:** la número 2 (Respuesta 1) — reintento exitoso
- **Esperas observadas:** `2.2s` · `2.0s → 4.1s` · `2.0s → 4.4s` · `2.0s → 4.0s` · `2.0s` — crecimiento exponencial con jitter (2 → 4), correcto
- **Costo total del ensayo:** `$0.001223 USD` — registrado solo en las 8 peticiones que completaron
- **Resultado:** 8/10 con éxito (2 de ellas tras reintentar); 2 agotaron los 3 intentos y terminaron en `RuntimeError` con mensaje claro. Las peticiones fallidas no registraron costo. Se observó además un 429 real en vivo con backoff funcionando (esperas 2 → 4 s).

## Qué sigue

Módulo 2 (LangChain, agentes, RAG) → Módulo 3 (FastAPI, Docker, QA) → Gate 3.
