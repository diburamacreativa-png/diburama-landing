# DIBURAMA · THERMOLIME · «LO HACEMOS VISIBLE» — Reel 20 s

Primer capítulo de la campaña **LO HACEMOS VISIBLE**. Reel vertical montado íntegramente con material real del proyecto
(vídeo original de 239,32 s), la música de 20 s entregada y los 13 SFX originales.

## Entregables (`entrega/`)

| Archivo | Contenido |
|---|---|
| `DIBURAMA_THERMOLINE_LO_HACEMOS_VISIBLE_FINAL.mp4` | Máster: 1080×1920, 25 fps, **500 fotogramas**, 20,000 s, H.264 High yuv420p, AAC 320 kbps 48 kHz |
| `DIBURAMA_THERMOLINE_LO_HACEMOS_VISIBLE_SIN_MUSICA.mp4` | Mismo vídeo, sólo SFX (mismos niveles que en la mezcla) |
| `DIBURAMA_THERMOLINE_PORTADA.jpg` | Portada 1080×1920; titular + lupa dentro del cuadrado central (recorte 1:1 y 3:4 de la cuadrícula) |
| `DIBURAMA_THERMOLINE_HOJA_CONTACTO.jpg` | Un fotograma cada 0,4 s |
| `audio/*.wav` | Mezcla final y pista de SFX sin música (WAV 48 kHz / 24 bit) + `audio_report.json` |
| `qa_report.json` | Control de calidad automático del máster |

## Línea de tiempo (cortes al fotograma del transitorio real)

| Reel | Fot. | Escena | Origen (vídeo original) | Texto | SFX |
|---|---|---|---|---|---|
| 0,00–1,68 | 0–41 | Gancho: lupa termográfica flotando sobre la pared real (2.5D) | pared 00:55,72 · lupa 00:57,60 | ¿CÓMO MUESTRAS | 01 |
| 1,68–4,02 | 42–99 | Barrido: pared normal → lectura térmica (registro píxel a píxel) e inmersión en la lupa | ídem | LO QUE NO SE VE? | 02, 03 |
| 4,02–6,02 | 100–149 | **Match cut circular** anillo de la lupa → anillo del aerogel; viaje entre partículas | 00:33,52–00:35,48 / campo 00:32,48 | ¿Y SI PUDIERAS… (palabra a palabra en semicorcheas) | 03 (pico en el corte) |
| 6,02–8,68 | 150–216 | Partícula compuesta, pulsos en 6,52/7,02/7,52/8,02 y entrada en el material | 00:39,2–00:41,8 | MOSTRARLO? (capa entre fondo y partícula) | 04, 05 |
| 8,68–12,02 | 217–299 | **Revelación**: apertura real del ladrillo bajo el revoco → dos paneles 2.5D unidos por línea gráfica | 01:09,36–01:12,64 | HACEMOS **VISIBLE** / SU **TECNOLOGÍA** | 06, 07 |
| 12,02–14,02 | 300–349 | Boquilla y chorro (ralentí 0,86×) | 02:52,15–02:53,87 | DE LO COMPLEJO… (contorno) → …A LO CLARO. (macizo) | 08, 09 |
| 14,02–14,69 | 350–366 | Barrido con el propio chorro → operario en obra | 02:49,60 | (continúa) | 10 |
| 14,69–16,02 | 367–399 | Fachada terminada (aérea) | 03:40,60–03:41,92 | AHORA SE ENTIENDE. | — |
| 16,02–17,69 | 400–441 | Micro‑montaje 0,68/0,32/0,32/0,36 s: termografía · partícula · sistema · fachada | 00:57,60 · 00:41,08 · 01:15,00 · 03:38,00 | — | 11 (dividido en 3 golpes) |
| 17,69–20,00 | 442–499 | Cierre DIBURAMA sobre la última imagen oscurecida | — | DIBURAMA / LO DIFÍCIL DE EXPLICAR, LO HACEMOS VISIBLE. / ¿Qué necesitas explicar? | 12, 13 |

## Decisiones que se apartan del brief (y por qué)

1. **Música**: llegó un **MP3**, no el WAV citado. El MP3 trae 40 ms de relleno de codificador antes del primer golpe; se recortan y así
   los transitorios caen exactamente en los tiempos del CSV (1,68 · 4,02 · 8,02 · 12,02 · 16,02 · 17,68…). Pulso medido: 90 BPM exactos.
2. **El golpe de «8,55 s» no existe**: en 8,02 vuelve el sub tras el breakdown, sigue un hueco casi silencioso y el golpe de banda completa
   cae en **8,688 s (f217)**. La revelación principal y el SFX 06 están ahí. El riser 05 muere 15 ms antes.
3. Revelación técnica hasta **12,02** (no 11,90), resultado desde **14,69** (no 14,80): son los golpes reales.
4. **Orden boquilla → operario** (invertido respecto al brief): todos los planos del operario de camiseta blanca llevan rótulos y caja
   de productos incrustados que ningún recorte vertical evita; el operario de chaleco naranja sólo se encuadra limpio sin el chorro.
   Por eso el chorro lo lleva el primer plano de boquilla y el propio chorro hace de barrido hacia el operario.
5. **Rótulos del original**: se han dejado fuera por encuadre o máscara (no se borra ni altera contenido técnico). Se conserva el rótulo
   real «aerogel de sílice». En la partícula compuesta el anillo oliva original se recorta (los rótulos nacen de él) y se sustituye por un
   anillo blanco fino.
6. **Nombre del cliente**: el producto del vídeo es **«thermolime»** (con M). La portada dice `CASO REAL · THERMOLIME`
   (cambiable con `CLIENT_NAME=... python3 cover.py`). Los nombres de archivo mantienen «THERMOLINE» tal como se pidieron.
7. **Logotipo**: no había archivo oficial (la web no es accesible desde el entorno y el logo del repo está marcado como provisional).
   Se usa el nombre DIBURAMA en Space Grotesk 700 (fuente de las piezas anteriores de Diburama en este repo), editable en `scenes.py`.
   Fucsia de marca `#E6197D`, sólo en la capa que añade Diburama (nodos de la línea gráfica y cierre).

## Mezcla de audio

- SFX colocados por **pico** sobre el transitorio medido (desviación ≤ 2 ms); 11 se divide en sus 3 golpes para los cortes del micro‑montaje.
- Graves de los SFX en mono (<150 Hz): el SFX 06 tenía correlación L/R −0,32 y perdía graves en mono.
- Bajo los impactos 01/06/08/13 la música baja 4,5 dB sólo por debajo de 140 Hz (el bombo y el subgrave no compiten).
- Limitador con sobremuestreo 4× a −1,5 dBTP: actúa 0,6 dB como máximo → la dinámica de la música se mantiene (LRA 3,8 LU, igual que el original).

## Control de calidad (máster final)

| Comprobación | Resultado |
|---|---|
| Fotogramas / duración | 500 / 20,000 s; vídeo y audio empiezan en 0,000 |
| Decodificación completa (`-xerror`) | sin errores |
| Fotogramas negros | ninguno (luminancia media mínima 9 %, fondo azul noche del cierre) |
| Cortes detectados | 100, 150, 217, 300, 350, 367, 400, 417, 425, 433, 442 = cues musicales |
| Sonoridad / pico verdadero tras AAC | −10,6 LUFS integrados · **−1,9 dBTP** · 0 muestras recortadas |
| Compatibilidad mono | correlación 0,65; pérdida de nivel en suma mono −0,83 dB |
| Zonas seguras | titulares dentro de x 80–940 y y 230–1600 (fuera de botones y descripción) |

**Límites honestos**: la mezcla se ha verificado con medidas, no escuchando (el entorno no tiene reproducción de audio): conviene una
escucha con auriculares y en el altavoz del móvil; los niveles de cada SFX están en `PLAN` (`proyecto/audio.py`). El original está a
~1 Mbps en 1080p y el formato vertical obliga a ampliar 1,8–2,7×: hay pérdida de nitidez, sobre todo en el micro‑montaje
(compensada con Lanczos, enfoque suave y grano fino).

## Reproducir (`proyecto/`)

```bash
pip install numpy opencv-python-headless pillow scipy soundfile   # Pillow con libraqm para el kerning
```

Copia los archivos de entrada en `proyecto/in/` (ver `in/LEEME.txt`) y ejecuta:

```bash
./build.sh
```

`scenes.py` contiene toda la dirección (cues, encuadres, tipografía, animación) con los tiempos en fotogramas; `lib.py` el motor de
composición; `audio.py` la mezcla; `cover.py` la portada; `qa.py` el control de calidad. Fuentes incluidas con su licencia OFL.
