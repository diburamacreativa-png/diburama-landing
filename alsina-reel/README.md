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

1. **0–0,75 s · Dentro de la obra.** Fotogramas reales del ascenso del dron (`pano.mp4`, f0–f12),
   girados 90° para que el 16:9 nativo llene el 9:16 a resolución nativa (sin recorte ni reescalado
   apreciable: 1,035× → 1,0×). Parallax real del dron, micro-giro de 1° que se amortigua.
   Interpolación por flujo óptico (DIS) entre fotogramas para la cámara lenta.
2. **0,75–2,6 s · Salida acelerada.** Una única curva de velocidad (log-escala del centro de imagen)
   con subida gaussiana y cola inercial gobierna tanto el vídeo (remapeo temporal f12→f240) como la
   panorámica. Pico de velocidad en t ≈ 1,97 s, justo en el empalme vídeo→panorámica, que se hace
   con morph de flujo óptico de gran escala bajo motion blur. A partir de ahí la cámara virtual pasa
   de proyección gnomónica (d=0) a estereográfica (d=1) mientras gira 56° y desacelera.
3. **2,6–3,1 s · Tiny planet** de la panorámica DJI real: suelo ≈ 50 % del ancho, grúa vertical
   saliendo del planeta, cielo envolvente; rotación residual amortiguada.
4. **3,1–3,52 s · Esfera → punto de la «i».** La proyección continúa hacia ortográfica (d→∞): el
   cielo se envuelve detrás de la bola y el borde del disco visible barre la pantalla desde las
   esquinas, dejando el rojo corporativo (no hay flash ni fundido). La bola se acelera en curva
   Bézier, se comprime, se transforma con un remapeo radial a superelipse (true shape morph) hasta el
   rectángulo exacto del punto (37,0×30,9 px, centro 573,0/860,4) y se sobreexpone a blanco puro.
   Sobreimpulso de 2,5 px y 4 % de escala, asentado en 2 fotogramas.
5. **3,52–4,22 s · Construcción del logo** con las formas blancas originales (8 componentes del PNG
   oficial, colocado en (189, 836), error medio 0,4 % frente al fotograma final de `LOGO VERTICAL.mp4`):
   el fuste de la «i» sale del punto, la «l» sube desde la línea base, «n» y «a» se deslizan desde
   detrás de la letra anterior, la «s» cae desde la altura de x, el trazo largo de la «A» se dibuja a
   lo largo de su eje y la pata corta cierra la «A» en el último golpe. Guías de 2 px al 32 % (línea
   base, altura de x, eje de la «i») que desaparecen antes del cierre.
6. **4,22–6,4 s · Cierre limpio**: logo original blanco sobre #AA192D uniforme (2,2 s).

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
- El rojo #AA192D está medido en el vídeo comprimido; si el manual de marca da otro valor, se cambia
  en `RED_SRGB` (`tools/reel.py`) y se vuelve a renderizar.
