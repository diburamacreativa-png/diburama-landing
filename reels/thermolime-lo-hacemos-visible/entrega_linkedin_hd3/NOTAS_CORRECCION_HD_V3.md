# LinkedIn HD V3 — corrección de los segundos 3, 4 y 19

Base: HD V2 (mismo montaje, cortes, gráficos, titulares, audio y cierre). Máster H.264 High, CRF 16, preset slow,
1920×1080, 25 fps, 600 fotogramas, 24,00 s, AAC 48 kHz · 18 MB (no requiere copia optimizada).

## Fuentes recibidas (ZIP) y localización en el original
| Archivo del ZIP | Tramo del original | Uso |
|---|---|---|
| THERMOLINE_01_CRISTALES_HD.mp4 | 00:07,00–00:09,12 | 2,68–3,32 s (cristales) e iris de 3,32 s |
| THERMOLINE_02_PARTICULA_HD.mp4 | 00:38,16–00:39,72 | 4,00–4,68 s (destello de revelación) |
| THERMOLINE_03_PARTICULA_FINAL_HD.mp4 | 00:39,32–00:42,60 | 4,68–5,32 s (partícula resultante) y 18,68–19,68 s (clímax) |

Alineación exacta al fotograma. El ZIP no contenía la guía de utilización y los nombres difieren de los citados en el encargo.

## Cambios (solo en esos planos)
- Fuente HD en lugar de la de 1 Mbps; se muestra a 1:1 (el fotograma renderizado es idéntico píxel a píxel a la fuente).
- Retirados los empujes de escala de 3–4 % que reescalaban la imagen (2,68–3,32 s, 4,00 s y 18,68 s).
- Destello del segundo 4: a 0,7× se mezclaban dos fotogramas por cada fotograma de salida (fantasma); ahora se usa el
  fotograma original más próximo. Arranca en 38,16 s (antes 38,12 s, un fotograma fuera del clip HD).
- Segundo 19: nueva perspectiva posterior de la partícula (41,48–42,04 s, 1×), con la estructura azul más visible y los
  rótulos originales ya estables; distinta de los fotogramas del segundo 4. A partir de 42,08 s el original anima una
  tercera cartela con letras aleatorias, así que la ventana del clímax mantiene el fotograma de 42,04 s durante 0,36 s.
- Cristales: se conserva el tramo 7,20–7,80 s. El enfoque del original se desplaza después hacia los granos del primer
  plano y el racimo de cristales protagonista pierde nitidez, aunque la nitidez global medida suba.

## Verificación (fotogramas de los MP4 exportados V2 y V3, misma escala)
| Momento | Detalle fino | Bloques 8×8 |
|---|---|---|
| 00:03,00 cristales | +28 % | 1,06 → 1,17 (ver limitación) |
| 00:04,50 partícula | +36 % | 1,17 → 1,11 |
| 00:19,00 partícula | +106 % | 1,06 → 1,03 |

Fuera de los planos corregidos el vídeo es igual a la V2 (diferencia media 0,03–0,5 niveles; cortes idénticos).
Bitrate en las secuencias microscópicas: 9,7 Mb/s (cristales), 7,8 Mb/s (partícula); media 5,9 Mb/s.

## Limitaciones de la fuente original
- Cristales: el plano usa profundidad de campo; el fondo desenfocado de la propia fuente HD ya tiene bloques suaves de
  su codificación (índice 1,185 en el archivo recibido). La V3 no los aumenta (1,171 tras exportar, PSNR 39,8 dB respecto al
  render); la V2 los ocultaba con el reescalado, que también borraba el detalle.
- 4,68 s: la cartela original «Aislamiento superior» aparece con su animación de letras aleatorias (igual que en V2).
- Siguen con la fuente anterior de 1 Mbps los planos sin fragmento HD: termografía (0–2,68 s, 5,32–8,68 s y 19,69–20,36 s)
  y el recorrido de partículas de 3,32–4,00 s (00:36,30).
