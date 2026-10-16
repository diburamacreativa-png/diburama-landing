# ALSINA — Reel cinematográfico 9:16

Pieza de 6,4 s (160 fotogramas, 25 fps progresivo, 1080×1920) producida y renderizada por código:
Python + NumPy/OpenCV para la proyección esférica, la composición y el motion graphics; FFmpeg para
la codificación. En el entorno no hay After Effects, Cinema 4D ni Blender, así que el "proyecto
editable" es el propio script (`tools/reel.py`): todos los tiempos, curvas, encuadres y colores son
parámetros con nombre al principio del archivo y en la clase `Curves`.

## Entregables

| Archivo | Descripción |
|---|---|
| `out/Alsina_Reel_Final_1080x1920.mp4` | H.264 High, CRF 12, BT.709, 4:2:0, sin audio |
| `build/Alsina_Reel_Master.mov` | ProRes 422 HQ 10 bits (no se versiona en git por tamaño; se regenera con `tools/encode.sh`) |
| `out/control_frames/` | Fotogramas de control en t = 0,5 · 1,5 · 2,75 · 3,35 · 3,85 · 5,0 s y hoja de contactos |
| `tools/` | Proyecto: render, análisis del vídeo, codificación y pipeline completo |
| `assets/source/` | Originales utilizados (panorámica DJI, `pano.mp4`, `LOGO VERTICAL.mp4`, PNG del logo y del punto, referencias) |

Reproducir desde cero: `bash tools/run_all.sh` (requisitos: ffmpeg con libx264/prores_ks; Python 3 con
`numpy`, `opencv-python-headless`, `scipy`). Un render completo tarda ~30–40 min en 4 núcleos de CPU.

## Cómo está construida (un solo sistema de coordenadas vertical)

1. **0–0,75 s · Dentro de la obra.** Fotogramas reales del ascenso del dron (`pano.mp4`, f0–f16),
   girados 90° para que el 16:9 nativo llene el 9:16 a resolución nativa (sin recorte ni reescalado
   apreciable: 1,02× → 1,0×). Parallax real del dron, micro-giro de 0,6° que se amortigua.
   Interpolación por flujo óptico (DIS) entre fotogramas para la cámara lenta.
2. **0,75–1,95 s · Salida acelerada.** Una única curva de velocidad (log-escala del centro de imagen)
   con subida gaussiana gobierna tanto el vídeo (remapeo temporal f16→f240) como la panorámica. Pico
   de velocidad en t ≈ 1,97 s, justo en el empalme vídeo→panorámica (morph de flujo óptico de gran
   escala bajo motion blur).
3. **1,90–2,36 s · Formación de la esfera, sin pausa.** La cámara virtual hace un único dolly-out
   continuo: distancia de proyección d = 0 (gnomónica, dentro de la panorámica) → d = 1
   (estereográfica, tiny planet a 2,30 s) → d → ∞ (ortográfica, la bola vista desde fuera). Una
   segunda rampa de alejamiento arranca a 2,28 s, antes de que el planeta termine de formarse: la
   velocidad nunca llega a cero. Gira 56° y el planeta sube a la mitad superior del cuadro.
4. **2,36–3,00 s · Esfera → punto, continuo.** El cielo se envuelve detrás del planeta: el borde del
   disco visible entra por las esquinas a 2,36 s y avanza ~250 px por fotograma, desacelerando, hasta
   cerrarse sobre la bola a 2,64 s. El rojo llega como consecuencia del propio alejamiento, sin flash
   ni fundido. Solo entonces la bola, con la obra aún visible, se comprime, se transforma con un morph
   radial a superelipse en el rectángulo exacto del punto y se sobreexpone a blanco (2,60–2,76 s). A
   partir de 2,40 s cae acelerando (potencia 2,6) hacia el centro exacto del cuadro. El punto llega a
   1,6× el tamaño del logo para que tenga protagonismo.
5. **3,00–3,18 s · Impacto.** Llega a (540, 960) con velocidad; aplastamiento del 7 % durante
   un fotograma y rebote amortiguado de 5 px (muelle con amortiguación de 60 ms), asentado a 3,18 s.
6. **3,15–3,42 s · Palo de la «i».** Sale del propio punto: su borde inferior baja delante
   (quint-out) y el superior le sigue, abriendo el hueco entre punto y palo: una sola pieza que se
   desdobla.
7. **3,40–3,80 s · «n» y «s» por máscara**, saliendo de detrás del palo de la «i» hacia cada lado. A la
   vez, el grupo empieza a asentarse: escala 1,6 → 1,0 y desplazamiento al encuadre final (curva
   ease-in-out de 3,36 a 4,30 s, sin overshoot).
8. **3,76–4,25 s · Resto de letras por máscara**, en cadencia hacia fuera: «l» y «a» (3,76/3,79),
   trazo largo de la «A» (3,86) y pata corta que cierra la «A» (3,97–4,25). Sin guías, contornos ni
   ningún otro elemento.
9. **4,30–6,4 s · Hold**: logo blanco original sobre #AA192D, estático (2,1 s), en la posición exacta
   del cierre de `LOGO VERTICAL.mp4` (centrado horizontalmente; la banda de altura de x centrada en el
   eje vertical del cuadro).

El logo se reconstruye en vectorial a partir del PNG oficial (trazado a 8×, diferencia media 0,36 %
frente al original) y se rasteriza con supermuestreo 4×4, para que siga nítido mientras se escala.

Todo se compone en luz lineal en coma flotante de 32 bits y se exporta a PNG de 16 bits. Motion blur
real por supermuestreo temporal (obturador de 180°, hasta 20 subfotogramas por fotograma). La
panorámica se muestrea con mipmapping por huella angular para evitar aliasing al encogerse.

## Limitaciones conocidas (honestas)

- La panorámica JPG y el vídeo no se tomaron desde la misma posición ni altura (en la JPG la cámara
  está junto a la grúa y por debajo de su punta). Un empalme píxel-exacto es imposible sin
  reconstrucción 3D; el empalme se alinea por hitos del suelo (base de la grúa, panel verde, muros
  azules) y se oculta en el pico de velocidad con morph de flujo y desenfoque de movimiento.
- La JPG es de 2000×1000 px (no 2048×1024 como indicaba el encargo); en los fotogramas de máxima
  curvatura la periferia gnomónica está muy estirada y se ve blanda, enmascarada por el blur.
- Sin audio: la pista de `LOGO VERTICAL.mp4` está sincronizada con otra animación y no he podido
  escucharla para validar un reajuste; el encargo prefiere exportar sin audio a meter una pista mediocre.
- En el MP4 el rojo se decodifica como (169, 24, 44) frente a (170, 25, 45) del original: diferencia de 1 código
  por redondeo YUV, invisible. La diferencia media con el fotograma final de referencia es 0,7/255.
- La intro hereda la cadencia algo irregular del vídeo original del dron (2–3 px por fotograma).
- El rojo #AA192D está medido en el vídeo comprimido; si el manual de marca da otro valor, se cambia
  en `RED_SRGB` (`tools/reel.py`) y se vuelve a renderizar.
