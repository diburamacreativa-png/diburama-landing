# ALSINA CHILE · Reel 9:16 · Informe de audio v2 (revisión exclusivamente sonora)

Vídeo: `Alsina_Reel_Chile_ref_01.mp4`, 1080×1920, 25 fps, 631 fotogramas, 25,240 s.
**La imagen no se ha tocado**: el flujo de vídeo del MP4 final es idéntico al original bit a bit (MD5 de paquetes) y fotograma a fotograma (MD5 de los 631 fotogramas decodificados).
Material: `Groovy Good Vibes.mp3` (pista original) y los WAV originales del pack. No se ha reconstruido nada a partir de la mezcla anterior.

## 1. Entregables (`out/`)

| Archivo | Contenido |
|---|---|
| `ALSINA_REEL_CHILE_FINAL.mp4` | Vídeo original copiado sin recodificar + nueva mezcla AAC-LC 48 kHz 320 kb/s |
| `ALSINA_REEL_MEZCLA_FINAL_48k24.wav` | Mezcla final estéreo, 48 kHz / 24 bit, 25,240 s |
| `ALSINA_REEL_MUSICA_STEM_48k24.wav` | Solo música, tal como suena en la mezcla (con ducking) |
| `ALSINA_REEL_SFX_STEM_48k24.wav` | Solo efectos (incluye la resonancia del impacto) |
| `ALSINA_REEL_MUSICA_EDIT_SIN_DUCKING_48k24.wav` | Edición musical sin automatizaciones, para remezclar |
| `CUES_FINAL_25FPS.csv` | 67 cues: fotograma, archivo, alineación, nivel, procesado y cambio respecto a v1 |
| `DUCKING_25FPS.csv` | Las 18 automatizaciones de ducking por bandas |
| `revision/REVISION_1x…mp4` · `REVISION_50pct…mp4` | **Solo para revisión** (recodificados): fotograma, cue activo y formas de onda |
| `revision/ESPECTROGRAMA_VIAJE_E_IMPACTO.png` | Espectrograma de 20,1–23,0 s (efectos arriba, mezcla abajo) |

`MUSICA_STEM + SFX_STEM = MEZCLA`, salvo en el único transitorio que toca el limitador (22,14 s, −1 dB).

## 2. Golpe final sincronizado con el punto de la «i» (prioridad máxima)

**Fotograma del impacto: f553 (22,12 s).** Lo localicé siguiendo los píxeles del punto blanco a resolución completa:

| Fotogramas | Movimiento del punto |
|---|---|
| f538–544 | aparece y sube encogiéndose |
| f544–547 | queda suspendido |
| f547–552 | cae acelerando (y = 509 → 523 → 549 → 593 → 672 → 842 px) |
| **f553** | **se funde en el punto de la «i» de «Alsina» y se completa la palabra** |

**Antes (v1):** el golpe musical más fuerte del tema (144,711 s del original) caía en 22,46 s, **8,5 fotogramas tarde**.

**Edición musical v2.** Sigue siendo un tramo continuo, sin cortes ni saltos: **122,022 → 147,9 s del original, con un +2,55 % de tempo** (rubberband, tono intacto, dentro del ±3 % del brief).
- No hice un corte para recuperar esos 0,34 s porque no es un múltiplo de beat (0,62 beats). Habría creado un tropiezo rítmico audible, justo lo que pides evitar.
- El ajuste elegido es el que mejor encaja **todo** el reel, no solo el final.

**Resultado medido:**
- **Ataque del golpe musical: 22,1313 s. Ataque del impacto SFX: 22,1307 s.** Ambos caen en el fotograma 553, coincidiendo entre sí a 0,6 ms.
- **Vacío previo.** La canción trae un hueco natural de ~95 ms (−40/−50 dBFS) que ahora cae exactamente antes del impacto. Lo refuerzo de tres formas:
  - el riser se corta 70 ms antes;
  - el aire invertido de la caída se corta 55 ms antes;
  - la música baja 7 dB en las tres bandas entre 22,02 y 22,12 s.
- **Capas del impacto** (todas del pack):

| Capa | Función |
|---|---|
| `HIT_03` | subgrave cinematográfico |
| `HIT_07` | cuerpo en 150–300 Hz, audible en móvil |
| `HIT_04` (solo sus parciales metálicos) | precisión metálica, **afinada a F**, la fundamental del acorde final Fmaj7 |
| `LOGO_04` | ataque definido |
| Resonancia | bus propio, corto (RT60 1,25 s) y oscuro (140 Hz–3,8 kHz) |
| `LOGO_02` | soplo de aire con filtro que se cierra |

- **Jerarquía.** El impacto es el momento más fuerte del reel: +7,0 dB sobre los picos del groove en banda completa y +10,3 dB en agudos, frente a +5,4 dB de «NO», el siguiente.
- **Detalles posteriores, sin competir:**
  - f557: tick al aparecer «×», el icono y «ASÍ SE CONSTRUYE EN»;
  - f561: trazo de aire suave al revelarse «GRAN VÍA»;
  - f567: confirmación al completarse el icono ALTIUS, **afinada a C**, la quinta del acorde.

## 3. Zoom out: viaje de cámara (20,36–22,12 s)

| Tramo | Imagen | Sonido |
|---|---|---|
| hasta f510 | arranque del giro | succión: aire invertido que se abre en estéreo |
| f509–520 | giro acelerado | whoosh de rotación con paneo izquierda → derecha (+9 dB respecto a v1) |
| f519–537 | **alejamiento** | capa nueva: `RISER_03` invertido y comprimido a 0,8 s, con Doppler continuo de +3 a −10 semitonos, paso bajo que se cierra de 16 kHz a 650 Hz (absorción del aire con la distancia) y anchura estéreo que colapsa de 1,6 a 0,1 (el sonido se va al fondo) |
| f520–527 | se forma el planeta | masa de aire grave (−5 st con Doppler). La propia música hace aquí un *stop* (20,88–20,96 s) en el que **la succión domina +7 dB** sobre la música; su golpe de 21,04 s cae con el planeta ya formado (a 27 ms) |
| f533 | último tirón | whoosh con Doppler descendente y estéreo que se cierra |
| f534 | corte a rojo | **boom lejano y oscuro** (paso bajo 420 Hz). Deliberadamente menor: la intensidad máxima se reserva al punto |
| f538–552 | el punto vuela, se suspende y cae | riser ascendente (−2 → +4 st, cada vez más fino y abierto) + aire invertido descendente en la caída |
| 22,02–22,12 | — | **vacío** |
| **f553** | **impacto** | — |

Durante el viaje, la música recibe ducking suave en medios y agudos (−1,5/−2,5 dB) para que el aire tenga espacio sin perder el groove.

## 4. Revisión de efectos en todo el reel

- **Whooshes de las transiciones principales** (4,28 · 7,40 · 9,68 · 12,92 · 16,00 · 19,14 s): +2,5 a +8 dB efectivos, con apertura estéreo o paneo dinámico y ducking de agudos de la música (−2/−3 dB) mientras pasan.
  - En 4,28 s se añade una capa de aire grave.
  - El brazo de grúa que cruza delante de cámara en 12,92 s recibe masa de aire grave como **movimiento de maquinaria**, sin foley de maquinaria real.
- **Capas metálicas cortas**, solo donde tienen sentido: GRÚA (f46), PLUS (f197), la cota de 2,40 m (f286), la GRÚA roja (f374) y el impacto final.
- **Impactos tipográficos:**
  - GRÚA +2,5 dB y CALIDAD +3,5 dB.
  - PLUS y SIMPLE bajan 1,5 dB. Se oían casi tan fuertes como el impacto final y rompían la jerarquía.
- **Pops y ticks**: +1/+2 dB de presencia.
- **Sin acumulación.** De 51 a 67 cues; los 16 nuevos son capas de los momentos clave, no efectos en cada movimiento.

## 5. Mezcla

**Ducking por bandas.** 18 automatizaciones (ver `DUCKING_25FPS.csv`), con crossover lineal en fase a 160 Hz y 2,5 kHz:

| Momento | Graves | Medios | Agudos |
|---|---|---|---|
| Impactos | −2/−3,5 dB | −1/−2 dB | −0,5/−1,5 dB |
| Whooshes | 0/−1 dB | −1/−1,5 dB | −2/−3 dB |
| Vacío previo al golpe | −7 dB | −7 dB | −7 dB |

**Separación de frecuencias:**
- Hits: HPF ~40 Hz, −1,5 dB en 70 Hz y +3/+3,5 dB en 200 Hz, para que el cuerpo se traduzca a móvil.
- Capa metálica: HPF 300 Hz, +4 dB en 1,8 kHz.
- Whooshes: HPF 70–180 Hz y −1,5 dB en 9 kHz.

**Presencia sin tapar.** La sonoridad media de la mezcla es igual a la de la música sola (−0,06 LU). Los efectos destacan por contraste en su banda, no por volumen. El único instante en que suben claramente la sonoridad es el impacto final (+1,6 LU).

**Mono.** Correlación L/R 0,82 y plegado a mono sin pérdida (0,00 dB). La anchura estéreo se fabrica con un lado sintético que se cancela al sumar a mono.

## 6. Master

| | Integrado | Pico verdadero | LRA |
|---|---|---|---|
| WAV | **−14,1 LUFS** | **−1,2 dBTP** | 1,4 LU |
| AAC del MP4 | −14,1 LUFS | −1,4 dBTP | — |

- **Limitador**: de pico verdadero, sin latencia (la sincronía no se mueve), sobremuestreado ×4. **Actúa una sola vez**, en el transitorio del impacto (22,14 s), con **1,0 dB durante ~40 ms**. No aplasta la dinámica. La alternativa sin limitador era bajar toda la mezcla 1 dB y quedarse en −15,1 LUFS.
- **Mezcla y música**: 0 clics y 0 discontinuidades, con detección por agudos y por segunda derivada. En la pista de efectos aislada solo quedan detecciones a −141 dBFS, ruido numérico inaudible.
- **Inicio y final**: el audio empieza con un fade de 6 ms y se cierra con un fundido de 0,3 s sobre la cola residual. La última muestra es silencio y no hay nada más allá de 25,24 s.

## 7. Encaje música–imagen (edición v2)

| Evento | Acento musical más cercano | Fuerza |
|---|---|---|
| NO | −5 ms | 3,6 |
| GRÚA | +29 ms | 5,1 |
| corte 4,28 | +7 ms | 4,6 |
| corte 7,40 | −37 ms | 7,1 |
| PLUS | +19 ms | 4,2 |
| corte 9,68 | −23 ms | 3,8 |
| corte 12,92 | −41 ms | 3,5 |
| GRÚA roja | +67 ms | 3,9 |
| corte 16,00 | −45 ms | 6,1 |
| SIMPLE | +27 ms | 8,0 |
| CALIDAD | +51 ms | 3,2 |
| corte 19,16 | +13 ms | 10,2 |
| planeta formado (f527) | −27 ms | 9,3 |
| **IMPACTO (f553)** | **+7 ms** | **11,6** (el mayor del reel) |

Contrapartida honesta: el corte a rojo (21,36 s) ya no coincide con un golpe musical. En v1 sí, porque entonces el golpe gordo iba al rojo. Lo cubren el boom lejano y el final del Doppler; la prioridad era el punto.

## 8. Límites y pendientes

- **No puedo escuchar audio.** Todo está verificado con medidas: sincronía al milisegundo, prominencia por bandas, sonoridad, picos, clics y mono, más la revisión de imagen fotograma a fotograma. Recomiendo una escucha en auriculares y en móvil con `REVISION_50pct` antes de publicar.
- **Tempo:** +2,55 % respecto al original (antes +0,55 %). Está dentro de tu límite, pero es el precio de clavar el impacto sin mover la imagen ni cortar la música.
- **Efectos:** solo los WAV del pack, procesados (pitch, Doppler, filtros, estéreo, resonancia). Los CC0 externos siguen sin descargar: el entorno bloquea `sfxmint.com`.
- **Música:** etiquetada «made with suno». Confirma la licencia comercial antes de publicar.
- **Reconstrucción:** `tools/build_audio.py` + `tools/cues.py` regeneran todo en ~20 s.
