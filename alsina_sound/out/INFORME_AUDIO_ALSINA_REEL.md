# ALSINA CHILE · Reel 9:16 · Informe de audio final

Vídeo: `Alsina_Reel_Chile_ref_01.mp4`, 1080×1920, 25 fps, 631 fotogramas, 25,240 s.
Material: `Groovy Good Vibes.mp3`, `ALSINA_MOTION_SFX_PACK` (32 WAV originales sintetizados).

## 1. Entregables (`out/`)

| Archivo | Contenido |
|---|---|
| `ALSINA_REEL_CHILE_FINAL.mp4` | Montaje completo. Vídeo **copiado sin recodificar** (MD5 de paquetes idéntico al original, 631 fotogramas, 25,240 s) + AAC-LC 48 kHz 320 kb/s |
| `ALSINA_REEL_MEZCLA_FINAL_48k24.wav` | Mezcla final estéreo, 48 kHz / 24 bit, 25,240 s exactos |
| `ALSINA_REEL_MUSICA_STEM_48k24.wav` | Solo música, tal como suena en la mezcla (con ducking) |
| `ALSINA_REEL_SFX_STEM_48k24.wav` | Solo efectos, aislados |
| `ALSINA_REEL_MUSICA_EDIT_SIN_DUCKING_48k24.wav` | Edición musical sin ducking, por si se quiere remezclar |
| `CUES_FINAL_25FPS.csv` | Lista final de cues: fotograma, timecode, archivo, nivel, pan, pitch, EQ y cambio respecto al CSV |
| `revision/REVISION_1x_…mp4` · `REVISION_50pct_…mp4` | **Solo para revisión** (recodificados): nº de fotograma, cue activo y formas de onda música/SFX con cursor |
| `build_stats.json` | Datos técnicos de la construcción |

`MUSICA_STEM + SFX_STEM = MEZCLA` muestra a muestra (error < −130 dBFS). No hay limitador ni compresor en el máster.

## 2. Análisis del vídeo (procedimiento A)

Revisión de los 631 fotogramas, más una métrica de diferencia por fotograma para los cortes. Los cortes del CSV son correctos: f20, f46, f107, f185, f242, f323 (barrido del brazo de grúa en primer plano, f320-329), f400, f479 y f534. Las entradas de texto, en cambio, se desvían en muchos casos entre 4 y 10 fotogramas respecto a la propuesta:

- «¿Y» en f6 (CSV: f12), «SI» en f12, línea curva en f12-19 (CSV: f60).
- NECE / SITA / RAS en f30 / f34 / f38, con 160 ms entre pasos. El UI_08 tiene ~110 ms entre ticks y no encaja, así que se usan 3 ticks sueltos.
- «EN CADA MONTAJE ?» en f67, tras un barrido vertical en f59-66 que no figuraba en el CSV.
- «ALISPLAY» en f113-117 (CSV: f121) y «MANUAL» en f122-127 (CSV: f132). En el vídeo se escribe **ALISPLAY**, no «ALISPLY» como en el brief.
- «240» entra desde la derecha en f187-191 y «PLUS» cae letra a letra hasta f197.
- «DISEÑADO» en f245, «PARA» con desenfoque glitch en f250-253, «EDIFICACIÓN» en f263, «CHILENA» en f268. El contador va de 0,01 a 2,40 m entre f271 y f286.
- ME f338 · NOS f348 · DEPEN f352. «GRÚA» parpadea a rojo en f374 y en f382 (CSV: f381).
- «MONTAJE» en f406, «SIMPLE» completo en f425, «ACABADOS DE» en f431, «CALIDAD.» completo en f455 (CSV: f461).
- Latigazo en f476-479. El giro arranca en f509-510 con pico en f516, el zoom planeta va de f520 a f533 y el corte a rojo es f534.
- Cierre: Alsina se forma en f550-553, «×» e icono ALTIUS en f557, «GRAN VÍA» en f561-566. A partir de f568 todo es estático hasta el final.

El detalle completo está en `CUES_FINAL_25FPS.csv`, incluidos los 6 eventos del CSV eliminados y el motivo de cada uno.

## 3. Música (procedimiento B)

**Tempo real.** Media de 108,6 BPM. El tema **no es de tempo fijo**: acelera suavemente de 108,1 BPM al inicio a 109,0 BPM al final, algo típico de música generada. En el tramo usado el tempo local es de ~108,9 BPM, y con el ajuste de +0,55 % queda en ≈109,5 BPM efectivos.

**Estructura.**
- Intro dispersa de 0 a ~6 s; groove completo a partir de ~6 s.
- Break de 89,5 a 95 s.
- *Stops* de banda en 121,49 s y 143,53 s, entre otros.
- Final real: stop (143,53) → golpe (143,611) → acorde sostenido con el golpe más fuerte del tema (144,711) → *stabs* finales → final seco en 147,17 s, con una cola de reverb residual a −43 dBFS.

**Downbeats (limitación).** No los he podido fijar con fiabilidad. La armonía es un vamp casi estático F#/C# y la percusión es muy sincopada, de modo que bombo/caja y croma no dan un «1» concluyente. Por eso no he numerado compases a ciegas: las decisiones se basan en acentos medidos (onsets a 2 ms), *stops* y la cadencia final.

**Segmento elegido.** Un tramo **continuo de 122,128 s → 147,507 s del original, sin cortes internos**, con un tempo de **+0,55 %** (rubberband, tono intacto; muy por debajo del ±3 % permitido). El reloj del vídeo encaja así con la música:

| Vídeo | Música |
|---|---|
| 0,00 s (f0) | arranca sobre un golpe real del groove (122,133 s), sin «entrar a mitad de nada» |
| 21,36 s (corte a rojo) | *stop* de banda + golpe (143,611 s): la marca entra justo tras el silencio de la banda |
| 22,46 s («GRAN VÍA») | golpe más fuerte del final (144,711 s) |
| 24,63–24,90 s | *stabs* y final real del tema |
| 24,94–25,24 s | fundido de 0,3 s sobre la reverb residual (−43 dBFS) → 0 exacto en 25,24 s |

**Por qué no reordené frases.** Busqué todas las combinaciones de un corte (otro gancho + este final) con validación por similitud rítmico-armónica. Las uniones posibles tenían similitudes ≤ 0,75, lo que haría el corte audible, o rompían el compás, y alineaban peor los acentos que el tramo continuo. También descarté el tramo continuo que obtenía la mejor puntuación global, porque dejaba el golpe gordo 7 fotogramas después del corte a rojo, que es el fallo que menos se perdona en un cierre de marca.

**Ajuste de acentos (música final):**

| Evento | Acento musical más cercano |
|---|---|
| NO | +31 ms |
| GRÚA | −39 ms |
| corte 4,28 | −13 ms |
| corte 7,40 | +3 ms |
| PLUS | +71 ms |
| corte 9,68 | +63 ms |
| corte 12,92 | −41 ms |
| GRÚA roja | −11 ms |
| corte 16,00 | +39 ms |
| SIMPLE | −15 ms |
| CALIDAD | +31 ms |
| corte 19,16 | +13 ms |
| **corte a rojo 21,36** | **+7 ms** |
| **GRAN VÍA** | **+1 ms** |

Los cortes de vídeo no siguen una rejilla regular, así que no pueden caer todos en beat. PLUS (+71 ms) y el corte de 9,68 (+63 ms) son los puntos menos exactos; ahí sincroniza el SFX.

## 4. Diseño de SFX (procedimientos C–E)

- **51 cues**, todos con los WAV originales del pack. No se ha generado ni sustituido ningún sonido; las «capas» son WAV del pack superpuestos.
- **Jerarquía.**
  1. Ticks y clicks (UI_01, UI_02, UI_05, LOGO_03).
  2. Pops por palabra (UI_03, UI_04).
  3. Swishes cortos y whooshes de corte con el pico en el corte.
  4. Reverse y riser que terminan en el corte (4,28, inicio del giro y 21,36).
  5. Impacto de marca acortado (HIT_07 con fundido a 0,30–0,45 s) + 2 confirmaciones digitales (LOGO_01 en f552, LOGO_03 en f557).
- **Coherencia.** Se reutilizan los mismos sonidos con variaciones de pitch de ±0,5–2 st (ticks ascendentes en NECE·SITA·RAS, ME·NOS·DEPEN y en el contador de cota) y de nivel. Las dos «GRÚA» usan la misma familia (HIT_02; la segunda a −1 st y más baja).
- **SIMPLE ≠ CALIDAD.** SIMPLE lleva HIT_01 seco y corto +1 st con un snap brillante. CALIDAD lleva HIT_06 con peso y un pop grave.
- **Omisiones deliberadas («si la música ya golpea, no duplicar»).**
  - Pop de «EN CADA MONTAJE?»: la música golpea en 2,74 s.
  - Clack en «GRAN VÍA»: la música da ahí su golpe más fuerte.
  - Línea roja bajo «GRÚA»: el brief pide no tapar la palabra.
  - Blip doble del cierre y LOGO_02 de salida: el cierre queda limpio con el final propio del tema.
- **Crescendo 19–21 s.** Reverse de aire hasta f510 (−17) → whoosh de giro con pico en f516 (−14) → micro-riser que termina en el corte f534 (−12) → impacto de marca, aprovechando el *stop* de la banda. La sonoridad momentánea sube solo +0,1/+0,5 LU sobre la música, así que no hay saturación.
- **Sincronía medida.** Los cues de ataque caen a ±0,4 ms del fotograma objetivo.

## 5. Mezcla y máster (procedimiento F)

**Calibración de niveles.** Cada cue se ajusta automáticamente contra la música en ese instante: pico de 100 ms ponderado K del SFX frente a la media ponderada K de la música en ±200 ms.

| Familia | Nivel relativo a la música |
|---|---|
| Ticks / clicks | −17,5 a −21 dB |
| Pops | −14,5 a −17 dB |
| Whooshes | −13 a −22 dB |
| Reverse / riser | −12 a −17 dB |
| Marca | −9 dB |
| PLUS / SIMPLE | −8 dB |
| GRÚA roja | −7,5 dB |
| GRÚA | −5,5 dB |
| CALIDAD | −5 dB |
| **NO** | **−3,5 dB** |

**Desviación consciente del rango orientativo de hits (−7/−12 dB).** Los hits del pack son casi solo subgrave (HIT_03 tiene el 98 % de su energía por debajo de 150 Hz), y en el instante de «NO» el bajo funk los enmascaraba. Medido contra los picos del groove de alrededor:

| | Antes | Después |
|---|---|---|
| «NO», graves | −1 dB | 0 dB (iguala al bombo) |
| «NO», medios | +1 dB | **+7,2 dB** |
| «GRÚA», medios | — | +2,8 dB |
| «CALIDAD», medios | — | +2,2 dB |
| Marca | — | +9,7 dB |

La banda de medios es la que se oye en el altavoz de un móvil. Subir más el subgrave no se oiría en móvil y ensuciaría en equipos grandes, así que el refuerzo se hizo con EQ en ~200 Hz y capas de ataque.

**EQ correctiva.**
- Hits: HPF 40–42 Hz, −1/−1,5 dB en 70 Hz, +3/+3,5 dB en ~200 Hz.
- Pops: HPF 140 Hz, −2 dB en 600 Hz para no competir con la guitarra, +3 dB en 2,8 kHz.
- Clicks: HPF 300 Hz.
- Whooshes / risers: HPF 90–180 Hz y high-shelf −1,5 dB en 9 kHz para no pisar charles ni guitarra.

**Ducking suave por bandas** (crossover lineal en fase a 160 Hz):

| Evento | Graves | Resto |
|---|---|---|
| NO, GRÚA, CALIDAD | −2,5 dB | −0,8 dB |
| Marca | −2,0 dB | −0,8 dB |
| PLUS, GRÚA roja, SIMPLE | −1,5 dB | −0,5 dB |
| 2,40 m | −1,0 dB | −0,3 dB |

Envolvente: ataque 8 ms, mantenimiento 90 ms, liberación 280 ms.

**Pan.** Moderado, máximo ±0,2 y siempre siguiendo la posición del texto. Correlación L/R de la mezcla 0,82; el plegado a mono no pierde nivel (0,0 dB). Las fuentes son mono, así que es compatible con mono por construcción.

**Máster.**

| | Integrado | Pico verdadero | LRA |
|---|---|---|---|
| WAV | **−14,0 LUFS** | **−2,3 dBTP** | 1,5 LU |
| AAC del MP4 | −14,1 LUFS | −2,5 dBTP | — |

Ganancia de máster +0,9 dB, sin limitador: ningún transitorio ha sido recortado. Los SFX nunca suben la sonoridad momentánea más de +0,7 LU sobre la música sola, lo que confirma que la música es la protagonista.

**Final.** Sin colas más allá de 25,24 s: la cola de SFX es 0 y la última muestra de audio está a −87 dBFS. No hay corte abrupto.

## 6. Licencias y procedencia

- **SFX:** los 32 WAV del pack son originales sintetizados para este trabajo (según `LEEME_PRIMERO.txt` y `CATALOGO_SFX.csv`). **No son CC0 de terceros.**
- **CC0 de SFXMint:** ejecuté `DESCARGAR_11_SFX_CC0_EN_WINDOWS_O_MAC.py` y **fallaron las 11 descargas** (el proxy de red de este entorno deniega `sfxmint.com`, HTTP 403). **No se ha usado ningún sonido CC0** y no hay URL CC0 que registrar. Si se quieren evaluar, hay que ejecutar el script en un equipo con acceso.
- **Música:** las etiquetas del MP3 indican `comment=made with suno`, `artist=punkmaster098`. La licencia de uso comercial depende del plan de Suno con el que se generó y de quién lo generó. **Conviene confirmarla antes de publicar** el reel corporativo.

## 7. Revisión y límites

- He revisado los 631 fotogramas, la sincronía de cada cue (medida en la pista SFX), la audibilidad por bandas, el mono, la sonoridad y la integridad del vídeo. **No puedo escuchar audio**: el «oído» de esta mezcla son medidas objetivas.
- Por eso entrego `revision/REVISION_1x` y `REVISION_50pct` (el 50 % mantiene el tono). Conviene una escucha final en auriculares y en un móvil, sobre todo de los niveles de los hits y de los ticks.
- Todo se regenera con `tools/build_audio.py` (cues en `tools/cues.py`). Cualquier ajuste de nivel o posición se hace en una línea y se reconstruye en ~15 s.
