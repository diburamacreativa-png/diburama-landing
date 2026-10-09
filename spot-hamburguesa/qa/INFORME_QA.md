# DIBURAMA — spot hamburguesa · Informe de calidad y limitaciones

**Estado:** primer máster completo para validación. Imagen, grafismo y estructura sonora cerrados. **El foley gastronómico es provisional (sintetizado) y debe sustituirse** antes de la emisión (ver §4).

## 1. Entregables

| # | Archivo | Especificación |
|---|---|---|
| 1 | `renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_30FPS.mp4` | 1080×1920 · 30 fps · 25,00 s · H.264 High CRF 18 (≈23 Mbps) · AAC 320k 48 kHz estéreo · -14,2 LUFS · -1,3 dBTP |
| 2 | `renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_24FPS.mp4` | Igual, 24 fps nativos (cadencia de los originales) |
| 3 | `renders/DIBURAMA_HAMBURGUESA_PREVIEW.mp4` | 720×1280 con timecode y nº de frame incrustados, para revisión |
| 4 | `renders/DIBURAMA_HAMBURGUESA_CONTACT_SHEET.jpg` | 4 fotogramas por segundo de toda la película |
| 5 | `project/` | Proyecto fuente editable y reproducible (`build.sh`) |
| 6 | `audio/` | Mezcla 24 bit, 4 stems, generador, `CUE_SHEET.md` |
| 7 | `project/edit_decisions.json` | EDL: in/out, rampas, movimientos, transiciones, grade |
| 8 | Este informe | |
| + | `renders/..._30FPS_VARIANTE_DESCRIPTOR.mp4` | Variante con "VÍDEOS PARA EMPRESAS" bajo el logo. **No es la opción principal**; ver §6 |

QA adicional: `qa/transitions_24fps/` y `qa/transitions_30fps/` (8 fotogramas consecutivos en cada transición), `qa/analysis/` (hojas de contacto por clip con nº de frame, métricas de movimiento), `qa/audio_analysis.png` (espectrograma, sonoridad, stems).

## 2. Incidencias del material recibido

1. **El ZIP llegó incompleto.** Se recibieron `.z01` y `.z02`, pero no el `.zip` final. Recuperé todos los archivos leyendo las cabeceras locales del ZIP: 12 clips, logos, referencias y brief están íntegros (CRC verificado).
2. **`plano 9C.mp4` está truncado**: 1,59 de 2,45 MB. Solo se decodifican **31 de 50 frames (1,29 s)**. Se usan todos; el plato vacío dura 1,29 s + fundido a negro. Para un plato más largo, reenviad el clip completo (el montaje lo absorbe cambiando una línea del EDL).
3. **Cadencia irregular en 5 clips**: tienen frames duplicados (tirones). 1B y 2A son ≈20 fps rellenados a 24; 4A, 5A y 9A ≈18–19 fps. El motor elimina los duplicados y reconstruye el movimiento con interpolación por flujo óptico. Revisado a 100 %: sin deformaciones en comida.
4. **9B no contiene el instante del mordisco**: la boca ya está sobre el pan y el movimiento es mínimo. El mordisco se construye con una rampa 3x en los primeros 4 frames (la hamburguesa sube contra los labios) + punch-in de 2 frames + micro-sacudida sincronizados con el CRUNCH. No he simulado varios mordiscos.
5. **La identidad de la hamburguesa varía**: la de 2A (una carne, cebolla arriba, queso amarillo) no es la de 9A/9B (doble carne, bacon, salsa blanca). El dissolve de 8A→9A y el ritmo lo disimulan, pero un ojo atento lo nota. Arreglarlo exige regenerar 2A o 9A.
6. **Resolución**: 11 de 13 clips son 720×1280, escalados ×1,5 (Lanczos + nitidez suave). Se nota algo de blandura en los planos de 720p comparados con 1A/1B, sobre todo en 9C (que ya está desenfocado de origen).

## 3. Decisiones de montaje (resumen; el detalle está en el EDL)

| Tiempo | Plano | Transición de entrada y tratamiento |
|---|---|---|
| 0,00–1,00 | 1A | Arranca en el frame 12 (la carne ya está en cuadro). Rampa 1,0→1,3x hacia el impacto |
| 1,00–2,00 | 1B | Corte en acción sobre la llamarada + punch-in 3,5 % + sacudida de 4 frames |
| 2,00–3,58 | 2A | Corte sincronizado con vapor. Travelling digital final hacia el pan (×2, con motion blur de obturador) |
| 3,42–6,08 | 3A | Match dissolve de 4 frames pan→macro del pan. Rampa 1,5x / 2,2x / 2,4x / 1,4x |
| 5,92–7,63 | 4A | Match dissolve de 4 frames con empuje sobre la boca del túnel |
| 7,38–9,33 | 5A | Transición luminosa: el queso aparece a través de los haces de luz del rodaje |
| 9,17–10,88 | 6A | Match dissolve de 4 frames (hebras y cinta magenta coinciden) |
| 10,63–12,31 | 6B | Transición luminosa: el engranaje nace de los brillos del queso. Empuje final para casar escalas |
| 12,19–13,96 | 7A | Match dissolve de 3 frames rodamiento→rodamiento |
| 13,58–15,83 | 8A | Cortinilla orgánica diagonal (de abajo-izquierda a arriba-derecha, siguiendo verdes y magentas) |
| 15,67–17,00 | 9A | Dissolve de 4 frames: la hamburguesa ilustrada se "recompone" en la real + ligero pull-back |
| 17,00–18,50 | 9B | Corte con sonido anticipatorio. Mordisco construido (ver §2.4) |
| 18,50–19,79 | 9C | Corte elíptico seco + silencio. Fundido a negro de 6 frames |
| 19,79–25,00 | Cierre | Copy en dos golpes → logo (la gota cae y aterriza en su sitio) → CTA → URL |

Sin flashes, glitches ni transiciones de plantilla. Dos movimientos digitales de empuje (2A→3A, 3A→4A) y uno en 6B; ninguno se repite como recurso.

**Look**: curva fílmica con hombro en altas luces, sombras desaturadas hacia grafito, contención selectiva del naranja saturado (-14 %), magenta Diburama ligeramente acentuado (+6 %), glow cálido muy leve, viñeta 16 %, grano común a toda la película. Ajuste de exposición y saturación por plano para igualar la secuencia.

**Logo**: se usa el archivo oficial `logo_alfa.png` sin alterar su forma. Para el fondo grafito, el gris de las letras pasa a #F1F1F1, el mismo tratamiento de la variante para fondo oscuro que el propio cliente entrega (`logo_diburama.png`). La gota (con su cara) y el punto conservan sus píxeles magenta originales. La gota solo se anima por traslación (cae y se asienta); su posición final es la del original.

**Tipografía del copy**: Inter Display (OFL), mayúsculas, con el punto final en magenta (eco del punto del logotipo). 126 px de cuerpo en 1080 de ancho, legible en móvil. Todo el texto queda dentro de la zona segura de Reels/TikTok, sin tocar la columna de iconos de la derecha ni la zona de pie de texto.

## 4. Sonido — lo que es y lo que NO es

- **No tuve acceso a foley grabado ni a librerías con licencia** (la red de este entorno solo permite GitHub/PyPI). Todos los sonidos de comida (chisporroteo, impacto, llamarada, vapor, crunch, migas, hojas, lápiz) están **sintetizados por procedimiento**: modelos estocásticos de micro-impulsos, resonadores y síntesis modal. Están bien colocados en tiempo, dinámica y espacio, pero **no son foley realista** y no pueden competir con una grabación con micro cercano. Van marcados como **PROV** en `audio/CUE_SHEET.md`, con timecode y frame a 24/30 fps, y en su propio stem (`01_PROV_FOLEY_ASMR.wav`) para sustituirlos uno a uno.
- **La música es original**, generada aquí (120 BPM, Re menor → Fa mayor). El concepto "la hamburguesa crea su banda sonora" está aplicado literalmente: el hi-hat es la misma señal del chisporroteo cortada a semicorcheas; la caja es un golpe de "espátula"; los graves son gotas; los risers son vapor. **Si se sustituye el chisporroteo por foley real, conviene regenerar el hi-hat a partir de esa grabación** (el script lo hace automáticamente si se reemplaza la función `sizzle`).
- Arco dinámico medido (sonoridad momentánea): ASMR inicial ≈ -18,6 LUFS (íntimo) → impacto -9,7 → música -13 → **CRUNCH -8,9, el momento más fuerte de la pieza** → plato ≈ -50 (silencio real) → cierre -20 con picos en la firma. Integrado -14,1 LUFS en el WAV y -14,2 en los másters, LRA 8,3 LU, true peak -1,3 dBTP en los másters.
- Bucle: el chisporroteo vuelve en los últimos 0,9 s al mismo nivel con el que arranca la pieza.
- Graves: filtro de paso alto a 32 Hz; bombo y bajo saturados para generar armónicos audibles en altavoces de móvil.

## 5. Limitaciones de la revisión

- **No he podido escuchar la mezcla ni ver la película en reproducción.** La revisión ha sido fotograma a fotograma (contact sheets, tiras de transición a 24 y 30 fps, recortes al 100 %) y objetiva para el audio (espectrograma, sonoridad por tramos, picos y duración). Hace falta **al menos un visionado humano con sonido** en móvil y en auriculares, usando la PREVIEW con timecode para anotar cambios.
- Verificado de forma automática: duración exacta (25,00 s en vídeo y audio), resolución, fps, espacio de color BT.709, sin frames negros accidentales (el único negro, 4 frames, es el intencionado entre plato y copy), sin congelados, sonoridad y picos.
- 30 fps frente a 24 fps: el máster de 30 se genera remuestreando la misma línea de tiempo con interpolación compensada en movimiento y obturador de 180°, no con pulldown. En los recortes revisados no he visto artefactos, pero no he revisado los 750 frames a 100 %. Comparad las dos versiones; si la de 30 muestra algún halo en llamas o humo, el EDL permite poner `"interp": "nearest"` en ese plano.
- Pesos: unos 70 MB por máster (≈23 Mbps), sobre todo por el grano. Instagram y TikTok recomprimen; si se prefiere un archivo más ligero para subir, se puede recodificar desde el intermedio sin pérdidas con un CRF más alto (no lo he medido).

## 6. Variante con descriptor

Desde mi punto de vista, **"Vídeos para empresas" es recomendable para público frío** (anuncios pagados a personas que no conocen Diburama): ni el copy ni el logo dicen qué vende la marca, y "¿COCINAMOS EL TUYO?" puede leerse como un mensaje de restauración si no se ha entendido la metáfora. Para orgánico entre seguidores, el cierre aprobado funciona sin él. Entrego las dos.

## 7. Versiones secundarias (pendientes de vuestra aprobación del vertical)

Todo el material de origen es vertical 9:16. Estimación:
- **4:5 (1080×1350)**: viable recomponiendo plano a plano (se pierde el 30 % de la altura). Puntos delicados: 1A (la carne entra por arriba a la izquierda), 9B (la nariz y la boca quedan arriba).
- **1:1**: viable en la mayoría de planos con un reencuadre por plano (se pierde el 44 % de la altura). 2A y 9A recortarán pan superior o base.
- **16:9 (1920×1080)**: **no es viable con un recorte digno**: solo se vería el 32 % de la altura de cada plano, a una resolución efectiva de 720 px de ancho escalada ×2,7. Las alternativas honestas son (a) composición diseñada con el vídeo vertical como panel central y una banda grafito con tipografía y marca, o (b) regenerar los planos en horizontal. No entrego un recorte deficiente.
