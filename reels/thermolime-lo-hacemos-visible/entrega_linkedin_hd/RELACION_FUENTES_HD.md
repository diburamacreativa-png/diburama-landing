# Relación de fuentes — LinkedIn HD V2

## Fragmentos HD recibidos y localizados en el original

| Archivo | Tramo del original | Alineación | Uso en el montaje (segundos del vídeo) |
|---|---|---|---|
| 05_MULTICAPA.mp4 | 01:08,00–01:23,00 | exacta al fotograma (error 0,63) | 8,68–12,00 s (pantalla completa y ventana editorial + detalle) · 19,36–20,40 s (clímax, ventana derecha) |
| 06_RODILLO.mp4 | 02:09,00–02:19,00 | exacta (3,87) | 12,00–15,36 s (pantalla completa y ventana) · 17,00–18,68 s (detalle de la llana) · 20,00–20,40 s (clímax) |
| 07_PROYECCION.mp4 | 02:39,00–02:55,00 | exacta (2,22) | 13,32–15,36 s (operario proyectando) |
| 08_SPRAY.mp4 | 03:11,00–03:19,00 | exacta (1,46) | 15,36–16,00 s (spray a pantalla completa) y barrido hacia el edificio |
| 09_EDIFICIO.mp4 | 03:30,00–03:47,00 | exacta (1,58) | 16,00–18,68 s (pantalla completa y ventana) |

## No recibidos (siguen con la fuente anterior de 1 Mbps)

| Archivo esperado | Planos afectados |
|---|---|
| 01_TEXTURA_AZUL.mp4 | 2,68–3,32 s (textura microscópica) |
| 02_PROPIEDADES.mp4 | no se usa en este montaje |
| 03_PARTICULAS.mp4 | 3,32–5,32 s (iris, transformación, partícula) · 18,68–19,36 s y 19,36–20,00 s (clímax) |
| 04_TERMOGRAFIA.mp4 | 0–2,68 s (apertura) · 5,32–8,68 s (antes/después) · 19,69–20,40 s (clímax) · portada |

En cuanto lleguen, basta con añadirlos a `CLIPS` en `proyecto/hdsource.py` y volver a renderizar.

## Defectos presentes en el material original (no corregibles sin inventar imagen)

- **08_SPRAY**: el plano está desenfocado en origen (profundidad de campo de la propia toma); la versión HD gana poco.
- **06_RODILLO (macro 02:11)**: desenfoque de movimiento del rodillo propio de la toma.
- **05_MULTICAPA**: es el clip de menor bitrate (2,7 Mbps); suficiente porque son superficies renderizadas lisas, sin bloques visibles.
- **Rótulos del original** («THERMOLIME® FIX / PRIMER», «REVOCO FINO FLEXIBLE», etiquetas del sistema) incrustados en las imágenes; se mantienen.
