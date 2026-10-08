# Diburama · Macrisal / Winduu — Reel Instagram

Reel de 26 s (1080 × 1920, 25 fps, 650 fotogramas, H.264 yuv420p + AAC 320 kbps, −14 LUFS) que compara la animación técnica e isométrica de Macrisal (A) con la animación ilustrada de Winduu (B).

**Entregable:** `out/Diburama_Macrisal_Reel.mp4`

## Requisitos

Node 18 o superior, FFmpeg y Python 3 con `numpy` y `scipy` (para la banda sonora). Instalación:

```bash
npm install
pip install numpy scipy
```

## Previsualizar

```bash
npm run studio          # Remotion Studio en el navegador (línea de tiempo, scrubbing)
npm run preview         # MP4 rápido a media resolución → out/preview.mp4
npm run stills          # fotogramas de control + hoja de contactos → out/stills/sheet.png
node scripts/stills.mjs 120,300,610   # solo los fotogramas indicados
```

En Studio, el vídeo de las ventanas puede ir a saltos al reproducir, porque cada fotograma se busca con exactitud. El render no se ve afectado.

## Cambiar textos, tiempos y colores

Todo está en **`src/config.ts`**:

| Qué | Dónde |
|---|---|
| Títulos y etiquetas mono de cada tramo | `SEGMENTS` (`title` admite varias líneas: `['Dos formas', 'de contarlo.']`) |
| Frase y marca del cierre | `CLOSING.brand`, `CLOSING.tagline` |
| Logo real | Coloca el archivo en `public/` y pon su ruta en `CLOSING.logo` (por ejemplo `'logo-diburama.svg'`) |
| Colores | `COLORS` (blanco cálido, negro y rojo de acento) |
| Fragmentos de origen (entrada y salida en segundos; la salida es exclusiva) | `CLIPS` |
| Etiquetas dentro de las ventanas | `CARD_LABELS` |
| Duración de las transiciones (fotogramas) | `TIMING` |

Los tamaños de la tipografía están en `TYPE`. Las posiciones y los movimientos de las ventanas están en **`src/choreography.ts`**:

- `LAYOUT`: retículas.
- `CARDS`: entrada, movimientos y fragmento que reproduce cada ventana.
- `NUMBERS`: los números grandes «01» y «02».
- `RULES`: las líneas rojas.
- `DARK_RANGES`: tramos con fondo oscuro.
- `LABEL_RANGES`: tramos en los que se ven etiquetas dentro de las ventanas.

La altura de cada ventana se calcula siempre como ancho × 9/16, así que no se puede deformar.

Si cambias el tiempo de un tramo, actualiza también los `at` correspondientes en `CARDS`.

## Música y efectos

La banda sonora se sintetiza en código: 120 BPM, La menor, sin samples externos.

- **Rejilla:** un compás dura 2 s, así que cada tramo del reel empieza en un primer tiempo. Las ventanas secundarias entran a la corchea y los números rojos al segundo tiempo (`beat()` en `config.ts`).
- **Arreglo:**
  - 0–4 s: gancho de pluck y bombo.
  - 6–8 s: subida y redoble.
  - 8 s: caída, que coincide con el fondo oscuro, con bajo en semicorcheas.
  - 12–20 s: groove más abierto para leer las comparaciones.
  - 20 s: arpegio en la cuadrícula.
  - 22–24 s: tensión, redoble y un silencio de una semicorchea.
  - 24 s: impacto, campanas del cierre y fundido exacto a 26 s.
- **Efectos sincronizados:** `scripts/export-events.ts` lee la coreografía y genera `audio/events.json`. Cada entrada, salida o reorganización de ventana lleva un *whoosh* que se desplaza en estéreo según su dirección. Cada línea de título lleva un golpe seco, y los cortes, números, líneas rojas, barridos de fondo, el gesto de la mano y el cierre tienen su propio sonido.
- **Máster:** sidechain del bajo y el pad con el bombo, compresión suave y EBU R128 a −14 LUFS con pico real ≤ −1 dBTP en el WAV.

```bash
npm run audio           # regenera public/audio/soundtrack.wav a partir de la coreografía
```

Si cambias tiempos o movimientos, `npm run render` regenera el audio automáticamente.

- **Ajustar el sonido:** en `audio/soundtrack.py` están la progresión (`PROG`), la dinámica por compás (`SECTION_GAIN`) y los niveles de cada efecto.
- **Exportar sin sonido:** pon `AUDIO.soundtrack = null` en `config.ts`.

## Exportar

```bash
npm run render          # audio + vídeo → out/Diburama_Macrisal_Reel.mp4 (CRF 16, yuv420p, BT.709, AAC 320 kbps)
```

Los ajustes de exportación están en `remotion.config.ts`. Si existe el Chromium del sistema (`/opt/pw-browsers/...`), se usa ese; si no, Remotion descarga el suyo la primera vez.

## Estructura

```
public/media/   vídeos originales, sin modificar (A y B)
public/fonts/   Geist Medium/SemiBold, IBM Plex Mono 400/500 (licencias OFL en licenses/)
src/config.ts   textos, tiempos, colores y fragmentos
src/choreography.ts  movimiento de las ventanas
src/Reel.tsx    composición (fondo, ventanas, tipografía, cierre)
src/components/ Card (ventana 16:9 con vídeo exacto) y Type (revelados con máscara)
src/lib/motion.ts  muelles sin rebote y track() (un muelle por cambio)
scripts/stills.mjs  fotogramas de control
scripts/export-events.ts  eventos visuales → audio/events.json
audio/soundtrack.py  música + efectos + máster → public/audio/soundtrack.wav
```

## Decisiones técnicas

- **Recortes exactos.** Cada ventana calcula el fotograma de origen como `entrada + (fotograma del reel − inicio del tramo)` y lo congela con `<Freeze>`. Así se reproduce a velocidad original sin derivas. Se ha verificado contra los originales: el desfase es de 0 fotogramas.
- **Salidas.** Cuando una ventana sale después del final de su fragmento, se queda en el último fotograma válido. No muestra material fuera del rango indicado.
- **Movimiento.** Muelles críticamente amortiguados, sin rebote. Las transiciones de ventanas duran 8–10 fotogramas, y los títulos entran con máscara de abajo arriba y salen hacia arriba. No hay fundidos cruzados.
- **Audio.** Los vídeos originales van silenciados. Toda la banda sonora es original y se sintetiza en `audio/soundtrack.py`.
- **Cierre tipográfico.** No había logo de Diburama en los materiales; basta con indicar `CLOSING.logo` para usar el real.
