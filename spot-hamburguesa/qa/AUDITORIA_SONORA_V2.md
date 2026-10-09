# Auditoría sonora V2 (mezclas A y B): ¿experiencia o sucesión de muestras?

Hecha antes de la escucha del cliente, analizando las pistas reales de cada mezcla. **No sustituye la escucha.** Indica dónde es probable que suene a programación y no a composición.

## Datos

| Indicador | A · ASMR | B · Electrónica | Lectura |
|---|---|---|---|
| Golpes de bombo con la misma muestra exacta | 31% de los pares (A_kick_foley) | 68% (B_kick) | El bombo idéntico en cada golpe es normal en electrónica, pero aquí no tiene variación de velocidad ni de timbre. |
| Clap / caja idénticos | 2 variantes de cubiertos | **100% idénticos** (6 de 6) | Efecto "ametralladora": el oído detecta la repetición literal. |
| Eventos clavados en la rejilla de semicorcheas (±8 ms) | 39% | 78% | B es casi totalmente rígida: sin swing ni humanización. |
| Continuidad armónica sostenida, 7,5–15,6 s | 40% | **22%** | El bloque central es sobre todo percusión con acordes puntuales: no hay una línea musical que lleve al espectador. |
| Cortes bruscos (caída > 18 dB en 20 ms) fuera del plato | ninguno | ninguno | Las uniones no tienen saltos de nivel. |

## Diagnóstico (autocrítica)
1. **No hay tema.** Ninguna de las dos mezclas tiene un motivo melódico reconocible que nazca en la entrada al pan, se desarrolle en el bloque central y vuelva en la firma Diburama. Sin ese hilo, la música es una secuencia de estados y no una pieza. **Es el problema principal.**
2. **Repetición literal de muestras.** Bombo y clap sin alternancia de muestras (*round-robin*), sin variaciones de intensidad y sin acentos dinámicos.
3. **Rejilla rígida en B.** Todo cae exactamente en el tiempo. Le falta *groove*: swing, adelantos y retrasos.
4. **Poca armonía sostenida.** A tiene acordes resonados puntuales y un sub, pero apenas cama entre 7,5 y 13,6 s. En B, la armonía depende de *stabs* cortos.
5. **Transiciones resueltas con efectos, no con música.** Las cuatro uniones tienen un efecto preciso, pero la música no las prepara: no hay subidas armónicas, redobles, cambios de acorde anticipados ni silencios compuestos (salvo el *build* de arpegio de B entre 3,5 y 7,5 s).
6. **El foley y la música conviven, pero no se responden.** En A el foley es literalmente el instrumento (bien), aunque sin frase. En B, el foley va por encima de una base que no lo tiene en cuenta.
7. **Firma Diburama débil.** Es un acorde con la gota. No hay un gesto de 2–3 notas que pueda reconocerse como marca.

## Qué conservaría (a falta de la escucha del cliente)
- Toda la edición de foley: impacto de la carne en cuatro capas, mordisco en cuatro capas, transformaciones T1–T4, silencio del plato y bucle.
- La idea de A: el chisporroteo real convertido en hi-hat y los objetos de cocina convertidos en percusión.
- La energía y la progresión de acordes de B (Rem – Si♭ – Fa – Do) para el bloque central.

## Propuesta para la versión híbrida (pendiente de aprobación; no ejecutada)
1. **Motivo Diburama** de 3–4 notas (por ejemplo, Re–La–Fa–Mi). Nace en el pan, filtrado y tocado por foley afinado (3,4 s). Se convierte en el *hook* del bloque electrónico (7,5–15 s) y vuelve, resuelto en Fa, como firma sonora (22,85 s).
2. Bombo y clap con **alternancia de 4–6 variantes**, intensidad variable y un *swing* del 54–56%.
3. **Cama armónica continua** en 7–15 s (pad o bajo sostenido), con automatización de filtro que respire con la imagen.
4. **Música que prepara cada transición:** subida armónica en T2, compás de tensión antes de T3, cambio de modo (menor → mayor) en T4.
5. Música y foley en diálogo: la música deja huecos donde suena cada golpe físico (impacto, engranaje, mordisco) en lugar de solo bajar de volumen.

## Límites de esta auditoría
No he escuchado las mezclas. Los indicadores miden síntomas típicos de música programada, no la calidad percibida. La decisión es del cliente tras la escucha.

## Materiales de terceros
Los MP3 originales, las pistas aisladas por efecto y los stems FOLEY / SFX / AMBIENTES siguen fuera del repositorio público (`.gitignore`). Las referencias de licencia están en `audio/foley/LICENCIAS.md` y `audio/foley/MAPEO_ORIGINALES.csv`.
