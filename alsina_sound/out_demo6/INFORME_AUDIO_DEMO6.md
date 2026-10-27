# ALSINA REEL CHILE · DEMO 6 (35,40 s) · Nueva apertura

**Imagen:** `VIDEO REEL CHILE_DEMO 6.mp4` (1080×1920, 25 fps, 885 fotogramas, 35,400 s). **No se ha tocado.** El flujo de vídeo del MP4 entregado es idéntico al original bit a bit (MD5 de paquetes) y fotograma a fotograma (MD5 de los 885 fotogramas decodificados).

## 1. Qué ha cambiado en el vídeo (comprobado fotograma a fotograma)

- **Desde f131 (5,24 s), el DEMO 6 es exactamente el DEMO 5 desde f213** (corte a ALISPLAY), adelantado 82 fotogramas = **3,28 s**. Lo confirma la diferencia por fotograma: 0 en la unión y menos de 2/255 después, que es solo la recompresión.
- **0–5,24 s (f0–130) es la apertura nueva**, que sustituye a los 8,52 s de apertura del DEMO 5:

| Fotograma | Imagen |
|---|---|
| f0–6 | obra con grúa |
| **f7 (0,28 s)** | **golpe de zoom 1**: alejamiento brusco, escala ×0,70; entra MONTAJES |
| **f23 (0,92 s)** | **golpe de zoom 2a**: escala ×0,84; aparece «SIN» |
| **f31 (1,24 s)** | **golpe de zoom 2b**: escala ×0,84; aparece «NECESIDAD» |
| f46–78 | línea roja |
| f78–82 | barrido |
| f83 (3,32 s) | corte a «DE GRÚA» (plano nuevo, no el del DEMO 5) |

## 2. Resto del vídeo: sin modificar

Desde **6,000 s**, la mezcla, la pista de música y la de efectos del DEMO 6 son **idénticas muestra a muestra** a las aprobadas del DEMO 5, adelantadas 3,28 s (comparadas en enteros de 24 bits: iguales).
- **Sin cambios**: ni remezcla, ni EQ, ni compresión, ni volumen, ni master.
- **Cierre**: el zoom final, el impacto del logo (ahora en 30,13 s = f753) y la fermata son los aprobados.

La unión está en 6,000 s, entre eventos. La apertura se renderizó con el mismo motor, la misma música y la misma ganancia de master del DEMO 5 (+0,8 dB). Antes de la unión, la diferencia con la mezcla aprobada es de **−138,5 dBFS** (solo cuantización de 24 bits), así que el empalme no existe en la práctica.

## 3. La nueva apertura

**Música.** La misma canción, continua: es exactamente la que sonaba en el DEMO 5, desplazada. Sin cambios de tempo, tono ni estructura.
- **Único ajuste**: la música entra con el primer zoom (0,257 s) en lugar de en el fotograma 0. Antes solo suena la subida de tensión, así que el primer zoom es también la entrada de la música.
- **No hizo falta reeditarla**: la propia canción ya tiene un golpe dentro del fotograma de cada zoom.

| Zoom | Fotograma visual | Golpe de la música | Diferencia |
|---|---|---|---|
| 1 | f7 · 0,280 s | 0,2613 s | −19 ms |
| 2a | f23 · 0,920 s | 0,9376 s | +18 ms |
| 2b | f31 · 1,240 s | 1,2069 s | −33 ms (el golpe musical más fuerte de los tres) |

Cada golpe de efectos se coloca **exactamente sobre el transitorio musical**, de modo que se funden y no suenan «pegados».

**Efectos** (todos del pack original, con el mismo lenguaje sonoro):

| Momento | Capas |
|---|---|
| f0–7 tensión | aire invertido que desemboca en el zoom 1 |
| **Golpe 1 (f7)** | whoosh corto y rápido + golpe grave y seco (`HIT_02`) + contacto metálico discreto; la música baja −3/−2/−1,5 dB durante 90 ms |
| f12–23 tensión | micro-riser con paso alto ascendente |
| Golpe 2a (f23) | whoosh corto + golpe seco (`HIT_01`) + pop de «SIN»: pre-golpe, más ligero |
| f25–31 tensión | aire invertido comprimido entre los dos zooms |
| **Golpe 2b (f31)** | whoosh rápido + **golpe grave cinematográfico (`HIT_03`, el golpe héroe que tenía «SIN» en el DEMO 5)** + metal + snap de «NECESIDAD»; la música baja −3,5/−2,5/−1,5 dB |
| f46 | trazo de la línea roja (motivo de línea) |
| f78–83 | succión + barrido con paneo hacia el corte |
| f83 | «DE GRÚA»: golpe con cuerpo + snap + metal, el mismo tratamiento que en el DEMO 5 |

**Relación entre los golpes, medida:**
- **Orden de intensidad**: 2b > 1 > 2a. El segundo zoom remata con algo más de contundencia que el primero.
- **Sobre el groove**: los dos golpes principales destacan +4/+6 dB en medios y +4,6/+7,3 dB en agudos, y también en graves.
- **Ritmo**: 2a actúa de anacrusa de 2b.

## 4. Master y control

| | Integrado | Pico verdadero |
|---|---|---|
| WAV | **−14,0 LUFS** | −1,2 dBTP |
| AAC del MP4 | −14,0 LUFS | **−1,2 dBTP** |

- **Ajuste de codificación.** Al adelantar 3,28 s, el impacto del logo cae distinto respecto a los bloques del codificador AAC. Codificando en coma flotante, el AAC rebotaba a −0,15 dBTP en ese impacto. Se resolvió codificando desde el WAV de 24 bits entregado, con el mismo codificador de siempre (−1,2 dBTP), **sin tocar la mezcla**.
- **Sincronía**: desfase AAC/WAV de 0 muestras. Duración 35,400 s.
- **Limpieza**: 0 clics y 0 discontinuidades en la apertura. El arranque en t=0 entra con 30 ms de fundido.

## 5. Entregables (`out_demo6/`)

- `ALSINA_REEL_CHILE_DEMO6_FINAL.mp4`: imagen original + mezcla AAC 48 kHz 320 kb/s.
- `ALSINA_DEMO6_MEZCLA_FINAL_48k24.wav` · `ALSINA_DEMO6_MUSICA_STEM_48k24.wav` · `ALSINA_DEMO6_SFX_STEM_48k24.wav`.
- `revision/`: versiones de revisión a 1× y 50 %, y espectrograma de la apertura.
- Reconstrucción: `tools/build_demo6.py` + `tools/cues_demo6.py` (requiere `out_demo5/`).

**Límite:** no puedo escuchar audio. Todo está verificado por medición y revisión de imagen; conviene una escucha final de la apertura con `REVISION_50pct`. Si prefieres que la música suene ya desde el fotograma 0 (como en el DEMO 5) en lugar de entrar con el primer zoom, es un cambio de una línea (`MUSIC_IN` en `cues_demo6.py`).
