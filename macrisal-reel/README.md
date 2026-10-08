# Diburama · Macrisal / Winduu — Reel Instagram

Reel de 26 s (1080 × 1920, 25 fps, 650 fotogramas, H.264 yuv420p, sin audio) que compara la animación técnica e isométrica de Macrisal (A) con la animación ilustrada de Winduu (B).

**Entregable:** `out/Diburama_Macrisal_Reel.mp4`

## Requisitos

Node 18 o superior y FFmpeg (solo para las hojas de control). Instalación:

```bash
npm install
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

Las posiciones y los movimientos de las ventanas están en **`src/choreography.ts`**:

- `LAYOUT`: retículas.
- `CARDS`: entrada, movimientos y fragmento que reproduce cada ventana.
- `NUMBERS`: los números grandes «01» y «02».
- `DARK_RANGES`: tramos con fondo oscuro.
- `LABEL_RANGES`: tramos en los que se ven etiquetas dentro de las ventanas.

La altura de cada ventana se calcula siempre como ancho × 9/16, así que no se puede deformar.

Si cambias el tiempo de un tramo, actualiza también los `at` correspondientes en `CARDS`.

## Exportar

```bash
npm run render          # → out/Diburama_Macrisal_Reel.mp4 (CRF 16, yuv420p, BT.709)
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
```

## Decisiones técnicas

- **Recortes exactos.** Cada ventana calcula el fotograma de origen como `entrada + (fotograma del reel − inicio del tramo)` y lo congela con `<Freeze>`. Así se reproduce a velocidad original sin derivas. Se ha verificado contra los originales: el desfase es de 0 fotogramas.
- **Salidas.** Cuando una ventana sale después del final de su fragmento, se queda en el último fotograma válido. No muestra material fuera del rango indicado.
- **Movimiento.** Muelles críticamente amortiguados, sin rebote. Las transiciones de ventanas duran 8–10 fotogramas, y los títulos entran con máscara de abajo arriba y salen hacia arriba. No hay fundidos cruzados.
- **Audio.** Se silencian los dos vídeos. No se aportó pista musical para esta pieza, así que se exporta sin música.
- **Cierre tipográfico.** No había logo de Diburama en los materiales; basta con indicar `CLOSING.logo` para usar el real.
