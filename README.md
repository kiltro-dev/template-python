# Miniaplicación con API de Gemini

> **Especialización en Desarrollo con IA Generativa (Accenture) — Gate 1 aprobado · Módulo 2 en curso**
>
> Miniaplicación que envía preguntas a la API de Gemini vía REST y devuelve la respuesta. El proyecto incluye además el cálculo del costo real por petición, manejo de errores, prompts de sistema, salida JSON estructurada, un banco de prompts con validación de consistencia y un cliente modular con reintento y clasificación de errores. En el Módulo 2 creció a un servicio RAG con recuperación citada, personalización fundamentada, observabilidad y gobernanza (ver Gate 2).

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
¡Conexión establecida y funcionando al 100%!
```

✅ Éxito = respuesta del modelo impresa y proceso terminado sin `Traceback` (el texto varía en cada corrida). Con red lenta puede fallar con `TimeoutError` (timeout fijo de 10 s, código Gate 1 sin reintento): reintentar.

## Ejecutar el servicio RAG (Gate 2)

```bash
python verificar_entorno.py      # si falta el índice: indexar primero
python src/indexar_corpus.py     # 9 chunks con metadata e ids → vectorstore/
python src/servicio_rag.py       # consulta punta a punta + supervisión
python -m pytest tests/test_gate2.py -v   # 4 no compensables
```

✅ Éxito = `Entorno listo`, respuesta con cita `[docN.md]`, interrupt que pausa y reanuda, `4 passed` y `Proceso terminado sin errores`.

## Estructura del repositorio

```
├── src/
│   ├── consumir_gemini.py     # M1: cliente REST de la API
│   ├── cliente.py             # M2: consultar_modelo con reintento y clasificación
│   ├── main.py                # punto de entrada de la miniaplicación (Gate 1)
│   ├── probar_costo.py        # pruebas de calcular_costo
│   ├── comparar_modelos.py    # medición latencia/costo/calidad (evidencia ADR)
│   ├── monolitico.py          # legado de bloques previos
│   ├── test_conexion.py       # legado de bloques previos
│   ├── pipeline_texto.py      # limpieza, tokenización, bolsa de palabras
│   ├── metricas.py            # precisión, cobertura, F1
│   ├── evaluar_cliente.py     # métricas sobre salidas reales
│   ├── cadena_tres_pasos.py   # chain LangChain clasificar→redactar→revisar
│   ├── enrutamiento.py        # clasificación + RunnableBranch + fallbacks
│   ├── agente_con_herramientas.py  # agente ReAct postventa + memoria
│   ├── agente_supervision.py  # reembolso con aprobación humana + trazas
│   ├── indexar_corpus.py      # chunking + embeddings + Chroma persistido
│   ├── recuperacion.py        # retriever + prompt dinámico con citas
│   ├── evaluacion_recuperacion.py  # P/R sobre 11 casos etiquetados
│   ├── registro_rag.py        # latencia y tokens reales por consulta (JSONL)
│   ├── dataset_tuning.py      # 12 ejemplos postventa para PEFT
│   ├── decision.py            # método de decisión RAG/full/PEFT
│   ├── logging_rag.py         # JSON + trace_id + consumo + filtro inyección
│   ├── registro_prompts.py    # versionado de prompts con huellas
│   ├── grafo_supervision.py   # interrupt/resume para desplegar prompts
│   ├── matriz_riesgos.py      # 7 riesgos puntuados con supervisión
│   └── servicio_rag.py        # Gate 2: servicio integrado punta a punta
├── prompts/                   # banco de 5 prompts + validación de consistencia
├── docs/                      # arquitectura, decisiones, límites, evidencias
├── tests/                     # suite pytest (30 mocks + 4 Gate 2 con API real)
├── vectorstore/               # índice Chroma (generado, no se versiona)
├── resultados_evaluacion.txt  # P 0.364 / R 1.000 (Bloque 27)
├── registros_latencia_costo.jsonl  # corridas instrumentadas (Bloque 28)
├── trazas_agente.jsonl        # trazas del agente supervisado (Bloque 23)
├── revision_manual.py         # rúbrica cualitativa sobre muestra (Bloque 17)
├── revision_manual.json       # veredictos de la revisión manual
├── resultados_metricas.json   # P/C/F1 sobre salidas reales (Bloque 16)
├── verificar_entorno.py       # chequeo pre-corrida del Gate 2
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
| `python src/indexar_corpus.py` | Indexa 9 chunks con metadata e ids | `vectorstore/` |
| `python src/recuperacion.py` | 2 preguntas → longitudes + citas (sin texto crudo) | consola |
| `python src/evaluacion_recuperacion.py` | P/R sobre 11 casos | `resultados_evaluacion.txt` |
| `python src/registro_rag.py` | 3 consultas instrumentadas | `registros_latencia_costo.jsonl` |
| `python src/dataset_tuning.py` | 12 ejemplos + balance + validación | consola |
| `python src/decision.py` | Puntaje RAG/full/PEFT del caso propio | `docs/decision_personalizacion.md` |
| `python src/logging_rag.py` | Demo traza + filtro + consumo | consola (JSON) |
| `python src/registro_prompts.py` | 2 versiones + diff | consola |
| `python src/grafo_supervision.py` | Interrupt: approve + reject | consola |
| `python src/matriz_riesgos.py` | 7 riesgos puntuados | consola |
| `python verificar_entorno.py` | Chequeo pre-corrida Gate 2 | consola, exit 0/1 |
| `python src/servicio_rag.py` | Servicio integrado + supervisión | consola |
| `python -m pytest tests/ -v` | Suite: 30 mocks + 4 Gate 2 (API real) | consola |

## El módulo (`src/consumir_gemini.py`)

Cliente REST con funciones separadas y su propio manejo de errores: `armar_peticion` (arma la petición, acepta `system_instruction` y `response_schema`), `enviar_peticion` (envía, clasifica el error y expone el detalle real de la API), `extraer_texto` (camino texto), `calcular_costo` (camino costo, desde `usageMetadata`), `parsear_respuesta_json` (camino JSON) y `obtener_dato_de_prueba` (orquesta el flujo principal). Cada consumidor usa el subconjunto que necesita: la miniaplicación usa el flujo texto; los scripts usan costo y JSON.

**Clasificación de errores (Módulo 2):** `enviar_peticion` distingue lo que no se resuelve reintentando (`ValueError`: credencial inválida o sin permiso) de lo que es temporal (`TimeoutError`: límite de uso, falla del proveedor o de red).

## El cliente modular (`src/cliente.py`)

Punto de entrada único `consultar_modelo(pregunta, system_instruction="", modelo="gemini-3.5-flash-lite")`: arma la petición, la envuelve en `con_reintento` (3 intentos, backoff exponencial con tope de 30 s y jitter cuando el error es temporal), registra el costo de cada operación con `registrar_costo` (entrada y salida por separado con los precios del modelo, acumulado de sesión), extrae el texto y traduce los reintentos agotados a un `RuntimeError` con mensaje claro. El `ValueError` de credencial se propaga sin reintentar.

## Documentación y evidencias

- 🏗️ **[Diagrama de arquitectura](docs/tarea_modulo1_bloque8/diagrama_arquitectura.png)** — flujo completo, credenciales, errores y cálculo de costo
- ⚖️ **[Decisión de modelo](docs/tarea_modulo1_bloque9/cambio-decision-modelo.md)** — `gemini-3.5-flash-lite` por defecto desde el 2026-11-02 (reemplaza a la [decisión original](docs/tarea_modulo1_bloque9/decision-arquitectura.md) de `gemini-2.5-flash`), con datos reales de costo, latencia, calidad y disponibilidad
- 🧩 **[Banco de prompts](prompts/README.md)** — 5 prompts, consistencia 3/3 medida contra la API
- 🤖 **[Límites de autonomía del agente](docs/limites_autonomia_agente.md)** — riesgos por herramienta, aprobación humana y revisión de trazas
- 🎯 **[Decisión de personalización](docs/decision_personalizacion.md)** — RAG 2-1-0 sobre el caso propio, con evidencia y monitoreo comprometido
- 📏 **[Límites de la métrica](docs/limites_metrica.md)** — documento de límites del pipeline de evaluación

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

## Registro del ensayo del pipeline (Bloque 15)

- **Fecha:** 2026-10-30 · **Modelo:** `gemini-2.5-flash` (por defecto)
- **Comando:** `python src/pipeline_texto.py` (3 consultas reales contra referencias propias, con registro impreso del antes y el después)
- **Resultado por caso:** Caso 1 ("¿Qué es Python?") crudo 85.7% → procesado 100.0% (1 reintento; respuesta de 782 tokens de salida); Caso 2 (capital de Chile) 50.0% → 100.0%; Caso 3 (color del cielo) 75.0% → 100.0%
- **Costo total del ensayo:** `$0.002679 USD` — solo éxitos, como en el Bloque 13
- **Pruebas:** `python -m pytest tests/ -v` → 13 passed en ~0.1 s (11 del cliente modular + 2 del pipeline). Rápida porque todo es mock: nada toca la red.

## Pruebas unitarias (Bloque 14)

- **Qué cubre:** `tests/test_cliente.py`, 11 pruebas con mocks sobre el cliente modular — 5 de `enviar_peticion` (401/403 → `ValueError`, 429/503 → `TimeoutError`, éxito con `candidates`), 3 de `con_reintento` (reintenta `TimeoutError`, no toca `ValueError`, 3 intentos = 2 esperas), 1 de `registrar_costo` (entrada y salida por separado + acumulado igual) y 2 de `consultar_modelo` (`TimeoutError` agotado → `RuntimeError` claro, `ValueError` se propaga).
- **Convención de mocks:** `patch` apunta donde se usa el nombre (`cliente.requests.post`, `cliente.time.sleep`), no donde se define. `enviar_peticion` está duplicada en `src/cliente.py` para que el cliente quede autocontenido (a pedido del curso).

## Gate 2: dónde está cada dimensión

| Dimensión (peso) | Evidencia |
| :--- | :--- |
| Pipeline RAG funcional (25 %) | `src/servicio_rag.py` + `vectorstore/` (9 chunks, metadata e ids) |
| Recuperación y citación (15 %) | `src/recuperacion.py`, `src/evaluacion_recuperacion.py`, `resultados_evaluacion.txt` (P 0.364 / R 1.000) |
| Costo y latencia (10 %) | `src/registro_rag.py`, `registros_latencia_costo.jsonl` (tiempos + tokens reales) |
| Personalización (15 %) | `src/dataset_tuning.py`, `src/decision.py`, `docs/decision_personalizacion.md` |
| Observabilidad (15 %) | `src/logging_rag.py`, `src/registro_prompts.py` (huellas + diff) |
| Seguridad y gobernanza (20 %) | filtro en `src/logging_rag.py`, `src/grafo_supervision.py`, `src/matriz_riesgos.py` |

No compensables: `tests/test_gate2.py` (4 tests contra servicio y grafo reales) · `python src/servicio_rag.py` (traza + interrupt + approve) · sin PII en logs (longitudes y huellas, jamás texto crudo).

## Registro del ensayo limpio Gate 2

- **Fecha:** 2026-11-23
- **Método:** `git archive HEAD` + archivos nuevos a `/tmp/gate2-ensayo`, venv nuevo, `pip install -r requirements.txt` (122 paquetes, sin errores), `.env` con clave propia
- **Encontrado:** `verificar_entorno.py` detectó índice faltante (exit 1) → `indexar_corpus.py` → 9 chunks → `Entorno listo`; pregunta demo de devoluciones no la responde el corpus (el modelo admite sin citar) → se cambió a pregunta del corpus en servicio y tests
- **Resultados:** `servicio_rag.py` exit 0 (respuesta con `[doc0.md]`, interrupt + approve OK) · `test_gate2.py` 4 passed · suite total 34 passed · `main.py` Gate 1 intacto
- **Corregido:** pregunta demo/test al corpus propio; `registro_rag.py` a huella+longitud (sin pregunta cruda); `decision.py` no sobrescribe el doc manual; demo de `recuperacion.py` sin prompt completo en consola

## Qué sigue

Módulo 3 (FastAPI, Docker, QA) → Gate 3.
