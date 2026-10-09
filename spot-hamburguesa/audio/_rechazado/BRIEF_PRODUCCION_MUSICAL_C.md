# Versión C: composición, maqueta y qué falta para la producción final

## Qué está hecho (definitivo como composición)
- **Motivo Diburama** (4 notas, "Di-bu-ra-MA": tres cortas que suben a una larga)
  - Re menor: La4 – Re5 – Mi5 – **Fa5**. Mundo interior de la hamburguesa: curiosidad y tensión.
  - Fa mayor: Do5 – Fa5 – Sol5 – **La5**. Resolución: la marca.
- **Apariciones del motivo** (tiempos de máster):

  | Tiempo | Qué ocurre |
  |---|---|
  | 3,50 s | Nace en el pan: solo 3 notas, lentas (queda incompleto). |
  | 5,50 s | En el bajo, sobre la dominante La: prepara T2. |
  | 7,50 s | Gancho completo con respuesta, en el drop. |
  | 9,50 s | Secuencia sobre Si♭. |
  | 10,75 s | Versión metálica aumentada desde el bloqueo del engranaje. |
  | 13,5 s | Fa mayor, orgánico. |
  | 19,95 s y 20,90 s | El copy lleva las notas 1-2 y 3. |
  | **22,85 s** | La última nota cae con la gota del logo. |

- **Armonía:** Rem – La (prepara T2) ‖ Rem – Si♭ – Solm/La (prepara T3) ‖ Si♭ – Do – Dosus4 → Do (prepara T4) ‖ Fa – Fa add9.
- **Groove:** 120 BPM; el compás 1 empieza a 3,5 s. Swing del 56 % en semicorcheas, capas de intensidad, muestras alternas (cada golpe es una grabación distinta), notas fantasma y redoble acelerado antes de T3.
- **Preparación musical de las transformaciones:**
  - **T1 (3,43 s):** el motivo nace del plato.
  - **T2 (7,5 s):** dominante La, motivo en el bajo, subida de vapor y 150 ms de respiración antes del drop.
  - **T3 (10,66–10,75 s):** armonía de dominante y redoble de cubiertos acelerado; el golpe coincide con el bloqueo.
  - **T4 (13,62 s):** la percusión desaparece y Dosus4 → Do eleva hacia Fa mayor.
- **MIDI:** `audio/v3/DIBURAMA_V3_C_COMPOSICION.mid`, con pistas motivo / armonía / bajo / percusión y marcadores de cada punto de sincronía.

## Qué es MAQUETA (no es producción final)
Los instrumentos de esta mezcla están hechos en casa: cuerdas y resonadores afinados excitados por vuestro foley real (plato → celesta, gel → kalimba, golpe metálico → campanas, vapor y chisporroteo → acordes sostenidos, cubiertos → bajo pulsado), más un sub senoidal. La idea, que la música nazca de la hamburguesa, es válida. **El acabado tímbrico no es el de una producción profesional.**

## Material externo necesario para el acabado premium
Para cada parte: qué necesito y especificación de entrega (WAV 48 kHz / 24 bits, empezando en t = 0 del spot, 120 BPM, compás 1 en 3,5 s):

| Parte (`audio/v3/external/<parte>.wav`) | Qué pedir | Referencia de sonido |
|---|---|---|
| `motivo.wav` | El motivo interpretado según el MIDI | Celesta o piano preparado con mucho detalle, tratado con delay. En 3D, campanas o tubular bells procesadas. En Fa mayor, kalimba o marimba suave. |
| `armonia.wav` | La progresión del MIDI | Cuerdas en *sul tasto* o un pad analógico de calidad, con movimiento de filtro. |
| `bajo.wav` | La línea de bajo del MIDI | Sintetizador analógico real o bajo eléctrico con compresión, con sub limpio. |
| `percusion.wav` | El patrón del MIDI con un kit orgánico y electrónico | Mantener el chisporroteo como hi-hat. Puede reemplazarse solo el bombo y la caja. |
| `texturas.wav` | Opcional: risers y texturas en las transiciones | — |

**Quién puede hacerlo:** un productor con un DAW profesional, a partir del MIDI y este documento, en 1–2 días. O stems con licencia comercial adaptados a este tempo y estructura.

**Integración:** se copian los WAV en `audio/v3/external/` y se ejecuta `python3 audio/v3/compose_c.py`. Cada parte externa sustituye automáticamente a su maqueta, y el foley, la mezcla y el máster se recalculan igual.

## Sonoridad (decisión consciente, ver regla 9)
- **Medidas de la preview:** -16 LUFS integrados, LRA 12,5 LU y -1,4 dBTP tras AAC.
- **Mordisco:** sin saturación. Un recortador de picos de 4 ms afina solo las puntas de los chasquidos: más de 3 dB durante 9 ms en total. El limitador general apenas lo toca (≤ 0,7 dB).
- **Límite físico:** un crunch natural tiene unos 14 dB entre pico y cuerpo. A -16 LUFS integrados queda al nivel de los bloques musicales (±1–2 dB) y destaca por contraste: 0,4 s de silencio musical antes y el regreso 2 dB por debajo.
- **Alternativas:** si se quiere que sea además el sonido de más nivel del spot, caben dos opciones: masterizar a -18 LUFS (más dinámica, más bajo en redes) o comprimir el crunch, que es lo que la regla 9 quiere evitar.
