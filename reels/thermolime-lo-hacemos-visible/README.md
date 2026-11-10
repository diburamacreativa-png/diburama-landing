# DIBURAMA · THERMOLIME · «LO HACEMOS VISIBLE» — Reel 20 s

## V5 «VISUAL LAB» definitiva — `entrega_v5/`

| Archivo | Contenido |
|---|---|
| `DIBURAMA_THERMOLINE_VISUAL_LAB_V5_FINAL.mp4` | Máster 1080×1920 · 25 fps · 500 fotogramas · H.264 High CRF 17 · AAC estéreo 48 kHz |
| `DIBURAMA_THERMOLINE_VISUAL_LAB_V5_HOJA_CONTACTOS.jpg` | 25 fotogramas (incluye 12 · 14 · 16 · 16,5 · 17 · 17,5 · 17,8 · 18,5 · 19,5 s) |
| `DIBURAMA_THERMOLINE_COMPARACION_V4_V5.jpg` · `comparacion_v4_v5.json` | V4 y V5 en los mismos instantes + métricas |
| `CLIPS_Y_TIEMPOS_DE_ORIGEN_V5.md` · `audio/` · `qa_report_v5.json` | Relación de clips, mezcla, versión sin música y control de calidad |

Logotipo: `proyecto/assets/DIBURAMA_logo_original_transparente_recortado.png` — el PNG oficial recibido, solo recortado a su
contenido (1065×406). Se compone sin redibujar ni recolorear (alfa premultiplicado), reducido a 880 px (0,826×). Los acentos
gráficos de la V5 usan el rosa exacto medido en el logotipo, **#E50E77**.

### Cambios respecto a la V4
- **0–16 s (misma narrativa y planos)**: ventana principal 960 → **1000 px**, secundaria 848 → **900 px**; márgenes de 40 px.
  Fondos en capas derivadas del propio material: atmósfera del plano + reflejo cromático de otra imagen del proyecto
  (partículas o termografía) con paralaje opuesto + siluetas técnicas difusas (contornos grandes del propio plano; se
  descartan letras y cartelas del original). Cartelas unidas a las ventanas con líneas en la junta.
- **16,02–17,68 s — expansión cinematográfica (nuevo)**: termografía grande con empujón en 16,19 · entra la partícula como
  segunda gran ventana en 16,36 · máscara termografía → sistema multicapa en 16,69 (la superior pasa a 1040 px) · máscara
  partícula → rodillo en 17,02 (la inferior pasa a protagonista) · en 17,36 ambas convergen (880 px) y una línea fucsia las une.
  El fondo cambia de luz en cada golpe.
- **17,69–20 s — cierre nuevo**: las ventanas se pliegan en la línea fucsia; la línea se abre y revela el **logotipo original**
  (104 % → 100 %); eslogan en 18,04–18,64 s («LO HACEMOS VISIBLE.» con más peso y el punto en el rosa del logo). Fondo
  #101A23 → #0D1219 con luz residual de la partícula, siluetas casi imperceptibles y un reflejo fucsia junto a la llama que
  respira con el último acento (19,36 s). Sin pantalla blanca, sin aberración RGB, sin círculo decorativo, sin fundido a negro.
- **Sonido 16–20 s**: barrido (segunda instancia del SFX 02) en la entrada de 16,36; triple golpe en las máscaras de 16,69 · 17,02
  y en la convergencia de 17,36; micro‑riser e impacto en 17,69. Todos por debajo de la música en su punto.

**Corrección de color (V5)**: hasta la V4, `render.py` convertía RGB→YUV con la matriz BT.601 de FFmpeg pero etiquetaba el
vídeo como BT.709; en reproducción los rojos y rosas saturados se desplazaban (rosa del logo #E50E77 → 243,40,118). Desde la
V5 la conversión usa `scale=out_color_matrix=bt709:out_range=tv` (verificado: 227,12,116). Las entregas V1–V4 conservan el
desplazamiento; se corrige volviendo a renderizarlas con el `render.py` actual.

Reproducir: `REEL_SCENES=scenes_v5 REEL_CRF=17 python3 render.py out.mp4` · `REEL_AUDIO=v5 python3 audio.py in/music.mp3 in/sfx out_audio` · `python3 deliver_v5.py hoja|comparar …`.

---

## V4 «VISUAL LAB — LO HACEMOS VISIBLE» — `entrega_v4/`

| Archivo | Contenido |
|---|---|
| `DIBURAMA_THERMOLINE_VISUAL_LAB_V4.mp4` | Máster 1080×1920 · 25 fps · 500 fotogramas · H.264 High CRF 17 · AAC 48 kHz |
| `DIBURAMA_THERMOLINE_PORTADA_V4.jpg` | Portada con la composición de dos ventanas; todo dentro del recorte 3:4 de la cuadrícula |
| `DIBURAMA_THERMOLINE_VISUAL_LAB_V4_HOJA_CONTACTOS.jpg` | 20 fotogramas con las ventanas en pantalla y su origen |
| `CLIPS_Y_TIEMPOS_DE_ORIGEN_V4.md` | Cada ventana, su clip y su tiempo en el original |
| `DIBURAMA_THERMOLINE_COMPARACION_V3_V4.jpg` · `comparacion_v3_v4.json` | V3 y V4 en los mismos instantes + métricas |
| `audio/` · `qa_report_v4.json` | Mezcla, versión sin música e informe de control de calidad |

### Sistema de composición (`proyecto/scenes_v4.py`, construido sobre `scenes_v3.py`)
- Zona de titular y 230–400 · ventana principal 960×540 (y 420–960) · secundaria 848×477 desplazada (y 1013–1490) · cartelas en la junta.
- Toda ventana es una **reducción** del original (≤ 0,5× la principal). Los «detalles» son recortes a resolución nativa (ancho de recorte ≥ ancho de ventana), nunca ampliaciones.
- Recursos usados una o dos veces por bloque: escáner que revela, iris circular, esfera que sale del marco, división, línea descendente, intercambio de protagonismo, mosaico con rotación de protagonista, pliegue conjunto.
- Cartelas `01 / LO INVISIBLE` · `02 / EL MATERIAL` · `03 / LA TECNOLOGÍA` · `04 / LA APLICACIÓN` · `05 / EL RESULTADO`, más `ANTES` / `DESPUÉS`, `APLICACIÓN REAL` / `DETALLE DEL PROCESO`. Sin datos ni propiedades añadidas.

### Cambios respecto a la V3
| Bloque | V3 | V4 |
|---|---|---|
| 0–3,3 s | Una ventana; la lente se abre en iris | Termografía + **segunda ventana** con la microestructura, revelada por escáner en 1,69 s; un círculo une la lente con la estructura |
| 3,3–5,3 s | Partícula sola | Partícula principal (iris desde la lente, esfera que sale del marco en 4,02) + textura azul secundaria atenuada |
| 5,3–8,7 s | Edificio rojo→azul + una termografía con escáner | **Antes / después real en dos ventanas**: un único escáner recorre ambas y revela la lectura térmica de la pared antigua y de la renovada; lentes conectadas; las ventanas se separan antes del golpe |
| 8,7–12 s | Sistema multicapa en una ventana con círculos | Sistema completo arriba + **línea que desciende** al ritmo y revela abajo el **detalle nativo** del mismo componente; cartela técnica en la junta |
| 12–14,7 s | Díptico rodillo + proyección en ventana única | Rodillo grande + spray pequeño → **intercambio** en 13,35 s (el spray pasa a protagonista, el rodillo muestra el plano general del operario) |
| 14,7–16,3 s | Vivienda sola | Vivienda + detalle del acabado (llana) conectado por línea |
| 16,3–17,7 s | Cuatro ventanas sucesivas | **Mosaico** de tres: rotación de protagonista en cada golpe y columna final |
| 17,7–20 s | Cierre | Mismo cierre; las tres ventanas se pliegan a la vez en la línea que revela la marca |

### Notas
- La termografía de apertura se limita a 00:57,40–00:58,58: desde 00:58,62 el original funde la lente. (En la V3 los dos últimos fotogramas de esa escena ya entraban en el fundido, ~7 % de saturación menos; imperceptible, pero queda anotado).
- Logotipo oficial: sigue sin archivo; cierre tipográfico editable. Producto: «thermolime».
- Reproducir: `REEL_SCENES=scenes_v4 REEL_CRF=17 python3 render.py out.mp4` · `REEL_AUDIO=v4 python3 audio.py in/music.mp3 in/sfx out_audio` · `python3 deliver_v4.py portada|hoja|comparar …`.

---

## V3 «VENTANA A LO INVISIBLE» — `entrega_v3/`

| Archivo | Contenido |
|---|---|
| `DIBURAMA_THERMOLINE_VENTANA_INVISIBLE_FINAL.mp4` | Máster 1080×1920 · 25 fps · 500 fotogramas · H.264 High CRF 17 · AAC 48 kHz |
| `DIBURAMA_THERMOLINE_PORTADA.jpg` | Portada con la misma identidad; titular + ventana dentro del recorte 1:1 |
| `DIBURAMA_THERMOLINE_VENTANA_INVISIBLE_HOJA_CONTACTOS.jpg` | 17 fotogramas del máster con tiempo y origen |
| `CLIPS_Y_TIEMPOS_DE_ORIGEN.md` | Relación de clips utilizados y sus tiempos en el original |
| `audio/` · `qa_report_v3.json` | Mezcla WAV, versión sin música e informe de control de calidad |

### Sistema gráfico (reutilizable para futuros Reels: `proyecto/scenes_v3.py`)
- **Ventana panorámica 16:9 completa** de 1000 o 1040 px. El original de 1920 px se **reduce** (×0,52) con filtro de área y se coloca en píxel entero: no hay ampliación ni enfoque artificial, por eso la ventana es más nítida que el propio original (los rótulos técnicos se leen).
- **Fondo** diseñado por escena: atmosférico (copia del plano, desenfoque ≈70 px, oscurecido 50–60 %, desaturado, deriva lenta independiente) o limpio grafito `#101419` / petróleo `#102A39` con retícula técnica del 2–3 %.
- **Capa gráfica**: marcas de esquina finas, sombra suave, filo de 1 px, identificador editorial (número fucsia + etiqueta), lente circular de exploración, línea de escáner que sale de la ventana, círculos y conexión sobre el sistema multicapa.
- **Fucsia provisional `#D64B96`** (cambiar en `FUCHSIA` al recibir el logotipo). Tipografía Inter Display (titulares) y Space Grotesk (firma).

### Montaje (cortes en transitorios medidos)
| Reel (s) | Composición | Contenido |
|---|---|---|
| 0,00–1,68 | A · Cinematic window | Termografía (00:57,40, 0,8×) · lente que se dibuja + línea de exploración · «¿CÓMO MUESTRAS» |
| 1,68–3,32 | C · Immersive | La lente crece y **se abre en iris** al mundo microscópico (00:07,20) · «LO QUE NO SE VE?» |
| 3,32–5,32 | C | Tres componentes (00:36,30) → **destello** en 4,02 (00:38,12, 0,7×) → partícula; la esfera **sale del marco** con máscara circular |
| 5,32–6,48 | B · Tech reveal (petróleo) | Edificio rojo → azul (00:17,00) con corchetes · «Aislamiento térmico» |
| 6,48–8,68 | B | **Escáner antes / después** de la termografía (00:57,60 / 01:03,60, registrado píxel a píxel); la línea sale de la ventana y se lleva el plano antes del golpe |
| **8,68–12,00** | B (ventana 1040 px) | **Sistema multicapa completo**: en el golpe la línea revela el sistema liso → abierto; círculos sobre los dos componentes, conexión y aparición real de sus rótulos (01:10,40–01:15,30, 1,79×) · «LA TECNOLOGÍA, AL DESCUBIERTO.» |
| 12,00–12,84 | Díptico editorial | Rodillo sobre ladrillo (02:12,70) + rodillo cargado (02:10,00) |
| 12,84–14,69 | A alta, grafito | Proyección (03:11,40); la niebla barre hacia el resultado |
| 14,69–16,32 | A baja | Vivienda completa (03:40,60) |
| 16,32–17,68 | Clímax | 4 ventanas que se sustituyen con escáner en 16,36 · 16,69 · 17,02 · 17,36 |
| 17,68–20,00 | Cierre | La última ventana se pliega en una línea; esa línea revela DIBURAMA atravesando la paleta térmica; «LO DIFÍCIL DE EXPLICAR, / LO HACEMOS VISIBLE.» |

### Decisiones y límites
- **Clips**: no llegaron los 8 archivos separados (`01_MACRO_AZUL.mp4`…); se ha trabajado sobre `Thermoline_HD_ESP.mp4`, la misma fuente con mayor calidad. Los tiempos de origen están en `CLIPS_Y_TIEMPOS_DE_ORIGEN.md`.
- **Propiedades (00:23)**: en una ventana de 1000 px los cuatro rótulos medirían ~11 px y no se leerían. Siguiendo tu instrucción, en su lugar va el plano del edificio que cambia de rojo a azul (00:17), cuyo rótulo sí es legible.
- **Termografía**: arranca en 00:57,40 porque antes el rótulo del original está en plena animación de «descodificado» (letras aleatorias).
- **Logotipo**: sigue sin archivo oficial → firma tipográfica editable. **Nombre**: el producto del vídeo es «thermolime»; portada `CASO REAL · THERMOLIME` (`CLIENT_NAME=` para cambiarlo).
- **Mezcla**: verificada por mediciones (no hay reproducción de audio en el entorno): conviene una escucha con auriculares.

Reproducir: `REEL_SCENES=scenes_v3 REEL_CRF=17 python3 render.py out.mp4` · `REEL_AUDIO=v3 python3 audio.py in/music.mp3 in/sfx out_audio` · `python3 cover_v3.py portada.jpg` · `python3 sheet_v3.py final.mp4 dir`.

---

## V2 — `entrega_v2/`

Montaje rehecho a partir de la revisión: más planos, más movimiento y una revelación tecnológica animada.
Mismos 20 s, misma música y mismos 13 SFX, recolocados sobre los nuevos cortes.

| Archivo | Contenido |
|---|---|
| `DIBURAMA_THERMOLINE_LO_HACEMOS_VISIBLE_V2_FINAL.mp4` | Máster V2 · 1080×1920 · 25 fps · 500 fotogramas · H.264 + AAC |
| `DIBURAMA_THERMOLINE_LO_HACEMOS_VISIBLE_V2_SIN_MUSICA.mp4` | Mismo vídeo, sólo SFX |
| `DIBURAMA_THERMOLINE_V2_HOJA_CONTACTOS_SELECCION.jpg` | Cada plano: fotograma del Reel + fotograma original + tiempos de origen |
| `DIBURAMA_THERMOLINE_COMPARACION_V1_V2.jpg` | V1 y V2 en los mismos instantes (cada 0,48 s) |
| `comparacion_v1_v2.json` · `qa_report_v2.json` | Métricas objetivas y control de calidad |

### Estructura V2 (cortes en acentos medidos de la música)

| Reel (s) | Plano | Origen |
|---|---|---|
| 0,00–0,68 | Termografía macro (impacto) | 00:56,96 |
| 0,68–1,68 | La cámara sale de la lupa y descubre la pared real | 00:55,72 + 00:57,0 |
| 1,68–2,68 | **Iris**: el interior de la lupa se abre a la textura microscópica azul | 00:07,20 |
| 2,68–3,32 | Macro de cristales | 00:08,16 |
| 3,32–4,00 | Barrido por los tres componentes | 00:36,30 |
| **4,00–4,68** | **Destello de transformación** (ralentí 0,6×) en el inicio de las semicorcheas | 00:38,12 |
| 4,68–5,32 | Partícula resultante con pulsos en semicorcheas | 00:39,40 |
| 5,32–7,48 | Termografía **antes / después** con cortinilla registrada píxel a píxel (puente térmico → rotura del puente térmico) | 00:57,60 / 01:03,60 |
| 7,48–8,68 | Enfoscado liso (desplazamiento) → la rendija empieza a abrirse (ralentí, empuje acelerado) | 01:09,32–01:09,46 |
| **8,68–9,32** | **Golpe: las capas se abren de golpe** (aceleración del original) + empujón hacia el ladrillo | 01:09,58–01:10,5 |
| 9,32–9,68 | Barrido de cámara entre los dos componentes del sistema | 01:10,62 |
| 9,68–10,52 | Comparación por escaneo enfoscado ↔ ladrillo (registrada) | 01:09,32 / 01:10,98 |
| 10,52–12,00 | Rodillo macro · rodillo sobre ladrillo · llana | 02:10,0 · 02:13,0 · 02:15,4 |
| 12,00–14,52 | General techo · macro boquilla · macro chorro · general obra (barrido con el chorro) | 03:06,7 · 02:52,2 · 03:11,5 · 02:49,6 |
| 14,52–16,68 | Fachada aérea · ventanal iluminado | 03:40,6 · 03:44,9 |
| 16,68–17,68 | Micro‑montaje: calor → aislamiento · edificio rojo → azul · destello | 00:57,6/01:03,6 · 00:17,36 · 00:38,12 |
| **17,68–20,00** | DIBURAMA revelado por una línea de escaneo (las letras pasan por la paleta térmica de la propia termografía) | — |

Textos reducidos a tres bloques: «¿CÓMO MUESTRAS LO QUE NO SE VE?» · «HACEMOS VISIBLE LA TECNOLOGÍA» ·
«DIBURAMA — LO DIFÍCIL DE EXPLICAR, LO HACEMOS VISIBLE.»

### Comparación objetiva V1 → V2

| Métrica | V1 | V2 |
|---|---|---|
| Cortes / cambios visuales | 14 | 27 |
| Cortes en 0–12 s | 6 | 16 |
| Duración media de plano | 1,33 s | 0,71 s |
| Energía de movimiento 0–12 s (dif. media entre fotogramas) | 4,78 | 8,70 (+82 %) |
| Segundos casi estáticos | 10, 18, 19 | 18, 19 (cierre de marca, intencionado) |

### Decisiones V2 que conviene revisar
- La textura azul útil del original está en **00:06,6–00:08,8** (no 00:08–00:11): después hay una transición a blanco.
- La transformación luminosa empieza en **00:38,11**; antes de eso el original muestra el logotipo «thermolime» en el centro, por eso el corte va directo a la luz.
- El plano de fuego (00:22) se descartó tras probarlo: el panel original es estrecho, ampliado 2,7× queda blando y añade una propiedad que el Reel no cuenta. Se sustituyó por la termografía calor → aislamiento.
- 03:12–03:16: los rótulos y la caja de producto del original obligan a encuadrar el chorro en su origen (pistola + niebla), no la mancha sobre la pared.
- Logotipo oficial: sigue sin estar disponible; el cierre es tipográfico y editable (`scenes_v2.py`).

Reproducir V2: `REEL_SCENES=scenes_v2 python3 render.py out.mp4` y `REEL_AUDIO=v2 python3 audio.py ...` (ver `build.sh`).

---

# V1 (anterior) — `entrega/`

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
