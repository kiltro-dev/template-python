# Límites de la métrica de evaluación


## Qué mide

Coincidencia de palabras entre una respuesta generada y una
referencia, contando repeticiones (precisión, cobertura, F1).


## Modos de falla conocidos

- Respuestas correctas y completas puntúan bajo si agregan contenido
  verdadero: "¿Qué es la fotosíntesis?", f1=0.33, la respuesta suma
  algas, bacterias, luz, agua y CO2 a una referencia de una línea.
- Paráfrasis correctas puntúan medio: "mutable" por "modificable"
  en la lista de Python (f1=0.54); matiz histórico compatible
  (década de 1980 + implementación en 1991) frente a referencia
  simplificada (f1=0.45).
- Omisión del dato central con F1 aceptable: "¿Qué es Python?"
  no dice "interpretado" y aun así llega a f1=0.43 con rasgos
  ciertos pero secundarios.
- En esta muestra no hubo falsos positivos altos: los siete casos
  con f1=1.0 eran coincidencias exactas tras normalizar
  (incluido "Muro" vs "muro", que resuelve la limpieza).


## Muestra revisada

10 casos (los 5 con menor F1 y los 5 con mayor F1) sobre 20
respuestas generadas el 2026-10-30: 13 con gemini-2.5-flash y 7
con gemini-3.5-flash-lite (la cuota diaria del primero se agotó
a mitad de la corrida; ver adenda en docs/tarea_modulo1_bloque9/).


## Recomendación de uso

Usar F1 para comparar en volumen y ordenar qué leer primero
(peores primero), nunca como veredicto. Revisar siempre a mano
respuestas con fechas, cifras o nombres propios; respuestas
largas con F1 medio-bajo (suele ser verbosidad, pero hay que
confirmarlo); y cualquier caso donde se sospeche omisión del
dato central de la referencia.
