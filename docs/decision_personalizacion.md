# Decision de personalizacion

## 1. El problema
Cada mensaje postventa en texto libre debe quedar clasificado con tipo y urgencia en un formato fijo y consistente.

## 2. Resultado del metodo de decision
- RAG: 2 puntos
- PEFT: 1 puntos
- Fine-tuning completo: 0 puntos

## 3. Tecnica elegida y por que
Elijo RAG, ganadora clara del método con 2 puntos (PEFT 1, fine-tuning 0).
Tiene sentido: no hay problema de formato medible (0 de 20 respuestas
reales fallaron el JSON con instrucción explícita), el dataset propio es de
12 ejemplos frente al umbral de 200, la información no cambia y hay una sola
variante. Ninguna técnica de entrenamiento se justifica hoy: el formato ya se
logra con prompt. En concreto, "elegir RAG" aquí significa no entrenar nada y
seguir con clasificación por prompt sobre el índice ya construido (U2.5).
PEFT queda como segunda opción condicionada: si el formato se degrada con
tráfico real o la escala lo exige. Descarto fine-tuning completo por datos
insuficientes, costo, y porque la cuenta ni siquiera tiene tuning habilitado
(501 verificado). Advertencia: mi muestra de 20 la construí yo, no es tráfico
de producción; el formato debe monitorearse ahí antes de darlo por cerrado.

## 4. Que necesitarias para ejecutarla
Para RAG: nada nuevo que indexar para esta tarea (0 documentos faltantes; el
índice actual de 9 chunks ya cubre el dominio y la clasificación no necesita
conocimiento externo). Para activar PEFT si se necesitara: tengo 12 ejemplos
etiquetados y el umbral es 200, así que faltan 188 ejemplos, unas 15,7 horas
de etiquetado a 5 minutos por ejemplo; además la cuenta tendría que habilitar
tuning (hoy responde 501). Monitoreo comprometido: repetir la muestra de 20
sobre tráfico real; si 3 o más fallan el formato, se reabre la decisión.