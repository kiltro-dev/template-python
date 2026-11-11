# Límites de autonomía: agente postventa con supervisión

Agente de soporte postventa (`src/agente_supervision.py`, Bloque 23):
responde preguntas usando 3 herramientas, con una de riesgo alto
protegida por aprobación humana y traza persistente en
`trazas_agente.jsonl`. Cierra la Unidad 2.4.

## Herramientas y nivel de riesgo

- consultar_estado_pedido: bajo (solo lee el estado de un pedido;
  lo peor es una respuesta equivocada, no modifica nada)
- calcular_reembolso: bajo (solo calcula un monto con la política;
  no mueve dinero ni toca sistemas externos)
- generar_reembolso: alto (mueve dinero de forma irreversible; un
  monto o pedido equivocado tiene costo directo)

## Herramientas que requieren aprobación humana

- generar_reembolso: por su nivel alto. Antes de ejecutar, llama a
  `esperar_aprobacion` (300 s, default-deny: sin respuesta no se
  ejecuta) y guarda la decisión con `registrar_aprobacion`
  (herramienta, argumentos, aprobado, momento). Verificado en
  `src/agente_supervision.py` con
  `grep -n "esperar_aprobacion(" src/agente_supervision.py`.
- Las de riesgo bajo NO piden aprobación: aprobar todo genera
  fatiga y aprobación por costumbre. Se revisan por traza.

## Revisión de trazas

- Frecuencia: muestra pequeña semanal de `trazas_agente.jsonl` +
  TODAS las trazas donde se usó `generar_reembolso` (sin muestreo).
- Qué se busca (patrones del Bloque 23):
  - misma herramienta dos veces seguidas (script
    `marcar_repeticiones_sospechosas`: candidato, no conclusión);
  - `generar_reembolso` sin entrada correspondiente en
    `registro_aprobaciones` (supervisión rota);
  - respuesta final que afirma algo que ninguna observación devolvió
    (inventado, no consultado).
- Verificación real al entregar: `trazas_agente.jsonl` con 2 líneas
  (casos demo_bajo y demo_alto) y `generar_reembolso` presente 1 vez.

## Qué hacer ante un comportamiento inesperado

1. Ubicar la sesión en `trazas_agente.jsonl` y leer qué herramienta
   usó, con qué argumentos y qué observó (no solo la respuesta final).
2. Si usó la herramienta equivocada: reescribir su docstring pensando
   en qué pregunta debería dispararla (causa más común).
3. Si ejecutó `generar_reembolso` sin aprobación registrada: revisar
   que la tool llame a `esperar_aprobacion` y no aceptar el flujo
   hasta corregirlo (fallo de supervisión, no de prompt).
4. Si inventó datos (monto, estado): confirmar que la observación
   traía el dato; si la tool devolvió vacío/ambiguo, mejorar su texto.
5. Si repite la misma tool en bucle: revisar observaciones ambiguas
   o tools que compiten; `max_iterations=15` corta, no corrige.
