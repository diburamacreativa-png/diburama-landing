# ALSINA REEL CHILE · DEMO 5 (38,68 s) · Informe de adaptación de música y efectos

**Imagen:** `VIDEO REEL CHILE_DEMO 5.mp4` (1080×1920, 25 fps, 967 fotogramas, 38,680 s). **No se ha tocado.** El flujo de vídeo del MP4 entregado es idéntico al original bit a bit (MD5 de paquetes) y fotograma a fotograma (MD5 de los 967 fotogramas decodificados). El primer y el último fotograma son los del original.

**Fuentes:** `Groovy Good Vibes.mp3` (pista original) y los WAV originales del pack, con el mismo diseño sonoro de la v2 del reel de 25,24 s. He comprobado que el `ALSINA_REEL_CHILE_FINAL.mp4` que me enviaste es idéntico a nuestra v2 (mismo MD5), así que he trabajado desde las pistas originales, no desde esa mezcla. No se ha usado ninguna separación de fuentes.

## 1. Entregables (`out_demo5/`)

| Archivo | Contenido |
|---|---|
| `ALSINA_REEL_CHILE_DEMO5_FINAL.mp4` | Imagen original copiada sin recodificar + nueva mezcla AAC-LC 48 kHz 320 kb/s |
| `ALSINA_DEMO5_MEZCLA_FINAL_48k24.wav` | Mezcla final estéreo, 48 kHz / 24 bit, 38,680 s |
| `ALSINA_DEMO5_MUSICA_STEM_48k24.wav` | Solo música, tal como suena en la mezcla |
| `ALSINA_DEMO5_SFX_STEM_48k24.wav` | Solo efectos |
| `ALSINA_DEMO5_MUSICA_EDIT_SIN_DUCKING_48k24.wav` | Reedición musical sin automatizaciones |
| `CUES_DEMO5_25FPS.csv` · `DUCKING_DEMO5_25FPS.csv` | 92 cues y 19 automatizaciones, con fotograma, archivo, nivel y procesado |
| `revision/REVISION_1x…` · `REVISION_50pct…` | **Solo para revisión** (recodificados): fotograma, cue activo y formas de onda |
| `revision/ESPECTROGRAMA_ZOOM_E_IMPACTO_DEMO5.png` | 31,4–35,0 s: efectos arriba, mezcla abajo |

## 2. Reedición musical

**Sin cambios de tempo ni de tono en ninguna parte rítmica** (la v2 tenía +2,55 %; ahora la canción suena a su tempo original, ≈108,9 BPM). Se ha alargado mediante material del propio tema y edición por compases:

| Vídeo | Fuente (MP3 original) | Qué es |
|---|---|---|
| 0,000 – 27,074 s | 106,899 → 133,979 s | Groove completo desde el primer fotograma (+ las mismas secciones de la v2, ampliadas hacia atrás) |
| 27,074 s | salto de 2 compases (8 beats, 4,404 s) | Empalme de 12 ms, 6 ms antes de dos golpes de batería equivalentes (afinado por correlación, −0,75 ms). Similitud rítmico-armónica entre ambos lados: 0,935 |
| 27,074 – 33,698 s | 138,383 → 145,00 s | El final real del tema: *stop* de banda, golpe, espacio y **gran golpe 144,713 s → f835** |
| 33,698 – 35,90 s | acorde 145,00–145,92 prolongado +2 beats | «Fermata»: el acorde sostenido tras el golpe se alarga 1,10 s (sin ritmo dentro: no hay cambio de tempo perceptible) para acompañar «CHILE \| GRAN VÍA» |
| 35,90 – 38,68 s | 145,92 → final | *Stabs* finales, botón del tema (~36,9 s) y cola natural, que se apaga con el fundido a negro del vídeo (f956–f965) |

Por qué esta estructura:
- **Al anclar el gran golpe en f835, el resto del tema se alinea solo.** La banda hace su *stop* justo cuando arranca el alejamiento (32,2 s), golpea dentro del zoom, deja espacio mientras el planeta se convierte en punto y estalla con el logotipo.
- **El salto de 2 compases** se eligió entre todas las ediciones posibles por compases, puntuando la coincidencia de acentos musicales con los 21 eventos visuales y la naturalidad del empalme. Los acentos en los 8 cortes principales pasan de 19,1 a 25,6 respecto a usar el tramo continuo.
- **No hay repeticiones** de material: solo se omiten 2 compases de un vamp que se repite.

**Encaje con la imagen.** Todos los eventos visuales tienen un acento musical a ±60 ms o menos. La entrada desde el blanco cae en beat (0,349 s).

## 3. Impacto del logotipo (máxima prioridad)

**Fotograma del impacto: f835 (33,40 s).** Seguí los píxeles del punto a resolución completa:

| Fotogramas | Imagen |
|---|---|
| f817–819 | el planeta se encoge |
| f820 | punto sobre negro |
| f820–826 | sube encogiéndose |
| f826–829 | queda suspendido |
| f829–834 | cae acelerando (y = 608 → 635 → 668 → 710 → 770 → 887 px) |
| **f835** | aterriza y se completa «Alsina» |

**Sincronía medida:** golpe musical en 33,4148 s y golpe de efectos en 33,4177 s, ambos dentro del fotograma 835 (33,400–33,440).

| Fase | Diseño |
|---|---|
| Anticipación | riser ascendente del punto (f821→) + aire invertido de la caída, cortados 70 y 55 ms antes del golpe |
| Vacío | hueco natural del tema + música −7 dB en las tres bandas durante 100 ms |
| Impacto | subgrave (`HIT_03`) + cuerpo 150–300 Hz audible en móvil (`HIT_07`) + contacto metálico afinado a F, la fundamental del acorde final (`HIT_04`) + ataque definido (`LOGO_04`) |
| Resonancia | bus corto y oscuro (RT60 1,25 s, 140 Hz–3,8 kHz) + soplo de aire filtrado (`LOGO_02`). No enturbia la lectura |
| Marca | f839 «×» e icono ALTIUS · f842/f847 letras ALTIUS · f849 la composición sube con un trazo de aire · f854 «CHILE \| GRAN VÍA» con una confirmación afinada a C (quinta del acorde) |
| Resolución | fermata del acorde → *stabs* y botón del tema → cola que se apaga con el fundido a negro |

**Jerarquía comprobada.** El impacto es el momento más intenso de toda la pieza: −8,7 dB (nivel ponderado K en 100 ms), frente a −9,9 del golpe musical del zoom y −10,0 de CALIDAD.

## 4. Zoom de alejamiento (30,1–33,4 s)

| Fotogramas | Imagen | Sonido |
|---|---|---|
| f763–803 | la toma cenital empieza a moverse | tensión: riser con paso alto que sube y estéreo que se abre |
| f803 | arranca el alejamiento | succión (aire invertido) + *stop* de la propia banda |
| f803–813 | acelera con giro | whoosh de rotación que barre de izquierda a derecha |
| f805–825 | **alejamiento** | capa Doppler: riser invertido con tono de +3 a −10 semitonos, paso bajo que se cierra de 16 kHz a 650 Hz y estéreo que colapsa de 1,6 a 0,1. El sonido «se va» hacia la distancia |
| f808–816 | la obra se convierte en planeta | masa de aire grave (−5 st, con Doppler) |
| f817–819 | el planeta se encoge | último tirón con Doppler descendente |
| f820 | punto sobre negro | boom lejano y oscuro (paso bajo 420 Hz), deliberadamente por debajo del impacto |
| f821–835 | — | riser del punto → vacío → **impacto** |

## 5. Efectos recolocados

Se mantiene el mismo lenguaje sonoro: los mismos sonidos, capas y EQ de la v2. Cada uno se ha recolocado en el movimiento real del DEMO 5. Hay 92 cues en total, con 8 de ellos para el contador de cota.

| Bloque | Tratamiento |
|---|---|
| Apertura (f0–26) | succión desde el blanco y whoosh con cuerpo en la aparición (f9–10); tecleo de MONTAJES con ticks ascendentes (f11, f16, f21) y pop + acento al completarse (f25) |
| SIN NECESIDAD (f87) | barrido + succión hacia el corte; **golpe héroe** con capa de ataque y capa metálica (el papel que tenía «NO» en la v2) |
| DE GRÚA (f150) | barrido lateral + golpe con cuerpo, snap y metal en el corte |
| ALISPLAY MANUAL (f213–232) | barrido de corte, micro-swishes y pops técnicos |
| 240 PLUS (f312–325) | transición con energía; «240» entra con swish; clicks en las letras que caen (P f319, L f321, U f323) y **hit seco + metal** cuando aterriza la S (f325) |
| DISEÑADO PARA / EDIFICACIÓN CHILENA (f380–475) | corte principal con aire grave; pops por palabra; contador 0,02→2,40 m con 8 clicks ascendentes (cada 4 fotogramas) y tope metálico en 2,40 m (f475) |
| Maquinaria (f506–515) | el cubo naranja de la grúa cruza delante de cámara: aire con paneo de derecha a izquierda, masa grave y resonancia metálica |
| MENOS DEPENDENCIA DE GRÚA (f520–591) | ticks por bloque de texto; **golpe + metal** en el destello rojo de GRÚA (f585) y acento menor en el segundo destello (f591) |
| MONTAJE SIMPLE / ACABADOS DE CALIDAD (f627–664) | corte reforzado (antes quedaba tapado); SIMPLE seco y corto (f645); CALIDAD con peso (f664), diferenciados |
| Motivo de línea | cada línea roja que se dibuja lleva el mismo trazo de aire, discreto |

## 6. Mezcla y máster

**Ducking por bandas.** 19 automatizaciones (ver `DUCKING_DEMO5_25FPS.csv`):

| Momento | Ajuste |
|---|---|
| Golpes principales | −2/−3,5 dB en graves |
| Whooshes | −2/−3 dB en agudos |
| Vacío previo al impacto | −7 dB |

**Fundido final.** Coincide con el fundido a negro del vídeo (38,24–38,62 s). La última muestra es silencio y no hay cola más allá de 38,68 s.

| | Integrado | Pico verdadero | LRA |
|---|---|---|---|
| WAV | **−14,0 LUFS** | **−1,2 dBTP** | 1,4 LU |
| AAC del MP4 | −14,1 LUFS | −1,1 dBTP | — |

- **Limitador**: de pico verdadero, sin latencia. Actúa solo en el impacto, con 0,96 dB.
- **Calidad**: 0 clics y 0 discontinuidades en mezcla, música y efectos. Correlación L/R 0,79 y plegado a mono sin pérdida.

## 7. Límites

- **No puedo escuchar audio.** Todo está verificado con medidas: sincronía al milisegundo, prominencia por bandas, sonoridad, picos, clics y mono, más la revisión de los 967 fotogramas. Recomiendo una escucha con `REVISION_50pct` antes de publicar.
- **Fermata**: es la única manipulación temporal y afecta solo a un acorde sostenido sin ritmo (+1,10 s). Si al escucharla no te convence, la alternativa es dejar que el tema termine en 35,8 s con su duración original y cerrar con 2,4 s de cola y resonancia.
- **CC0**: los efectos externos siguen sin usarse (el entorno bloquea `sfxmint.com`).
- **Licencia de la música**: la pista está etiquetada «made with suno»; confirma la licencia comercial.
- **Reconstrucción**: `tools/build_demo5.py` + `tools/music_demo5.py` + `tools/cues_demo5.py` regeneran todo en ~25 s.
