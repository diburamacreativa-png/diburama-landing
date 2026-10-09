# DIBURAMA — EL VÍDEO QUE TE COMES ENTERO · spot hamburguesa

9:16 · 1080×1920 · 25,0 s · másters a 30 fps y 24 fps nativos · audio estéreo 48 kHz · H.264 + AAC.

## Estructura

| Carpeta | Contenido |
|---|---|
| `clips/` | Los 13 MP4 originales (9C llegó truncado, ver informe) |
| `marca/` | Logos oficiales del cliente (fuente de verdad, sin modificar) |
| `referencias/` | Hojas de referencia y notas de montaje entregadas |
| `project/edit_decisions.json` | **EDL**: in/out de máster, rampas de velocidad, movimientos digitales, sacudidas, transiciones, grade por plano, look global |
| `project/tools/engine.py` | Motor de imagen (remapeo temporal, interpolación por flujo, obturador 180°, transiciones, etalonaje, grano) |
| `project/tools/graphics.py` | Cierre: copy, logo oficial, CTA |
| `project/tools/analyze.py` | Análisis de clips (FASE 1): hojas de contacto numeradas, luma, nitidez, flujo óptico, detección de duplicados |
| `project/tools/qa_strips.py`, `audio_qa.py` | QA: tiras de transición, contact sheet, análisis de audio |
| `project/tools/build.sh` | Build completo reproducible |
| `audio/sound_design.py` | Diseño sonoro + música + mezcla |
| `audio/stems/` | Stems de mezcla (post-fader, sin limitador de máster) |
| `audio/DIBURAMA_HAMBURGUESA_MIX_48k.wav` | Mezcla final 24 bit |
| `audio/CUE_SHEET.md` | Lista de eventos sonoros con timecode; los marcados **PROV** son sustituibles |
| `renders/` | Másters, preview, contact sheet |
| `qa/` | Análisis de clips, fotogramas consecutivos en cada transición, análisis de audio, informe |

## Reconstruir

```bash
pip install numpy scipy opencv-python-headless pillow soundfile pyloudnorm matplotlib
project/tools/build.sh
```

Editar el montaje = editar `project/edit_decisions.json` (tiempos, velocidades, transiciones, grade) y volver a lanzar el build.
Fotogramas sueltos para revisar un cambio: `python3 project/tools/engine.py --fps 30 --stills 3.5,6.0`.

Informe de calidad y limitaciones: [`qa/INFORME_QA.md`](qa/INFORME_QA.md).
