# K01 · Paisaje real — la gráfica se convierte en horizonte (10,5–13,0 s)

**Sustituye a:** paisaje procedural de `src/scenes/s04_horizon.js` (función `landscape(..., {style:'real'})`).
**Duración a generar:** 5 s (se usan 2,5 s: 10,9–13,0 + margen para el 50/50 de la escena 05). 9:16, 1080×1920, 30 fps.

## Imagen inicial necesaria
`prompts/refs/K01_start.png` — exportar el fotograma **f0355** del máster (`frames/f0355.png`). Es la composición exacta: horizonte en y≈900 px con la forma de la curva de la gráfica, sol tras la cresta a x≈770, carretera con punto de fuga en x≈600.

## Imagen final necesaria
`prompts/refs/K01_end.png` — fotograma **f0389** del máster (cámara 5 % más cerca, misma composición).

## Prompt definitivo
```
Cinematic aerial drone shot at dawn, vertical 9:16. A single smooth mountain ridge
defines the horizon exactly across the middle of the frame, its silhouette gentle and
wave-like. Behind it, a pale hazy second ridge with five slender white wind turbines
slowly turning. Low sun just hidden behind the ridge on the right third, warm peach glow,
sky graded from deep blue-black at the top to mauve and soft apricot near the horizon.
In the foreground, dark valley floor with a straight two-lane highway running from the
bottom of the frame to a vanishing point on the horizon slightly right of center; a few
trucks with small headlights travel along it. Mid-ground: a line of steel electricity
pylons with sagging cables crossing the valley. Far left at the base of the ridge: a small
cluster of warm industrial lights. Very slow forward dolly, stable horizon, no roll.
Photographic, anamorphic, fine film grain, low contrast shadows, restrained color palette.
```

## Cámara
Dolly hacia delante muy lento (≈5 % de escala en 2,5 s), altura constante, **horizonte fijo** (no inclinar, no rotar).

## Sujeto
Aspas girando lento; 3–5 camiones con faros; nada más se mueve.

## Restricciones
- El horizonte **no puede moverse** de y≈900 px (±10 px): la línea magenta de la gráfica se compone encima y debe coincidir con la cresta.
- Sin personas, sin texto, sin logos, sin pájaros.
- Nada de colores saturados: el único color intenso del vídeo es el magenta (#E6197D), que se añade en composición.

## Negative prompt
```
text, watermark, logo, people, birds, lens flare streaks, saturated colors, magenta, green grass,
snow, fast camera motion, rotation, horizon tilt, warped turbines, melting vehicles,
cartoon, CGI look, oversharpened, HDR halos
```

## Consistencia con el máster
1. Rastrear (tracking 2D) la cresta y **reemplazar** la línea magenta del máster (`landscape` → `glow`) sobre el plano de Kling; la línea debe seguir exactamente la cresta real.
2. Etalonar: sombras hacia #0D0E14, altas hacia #F6C9A2, saturación −20 %.
3. Grano: el del máster (`src/post.js`, 5,5 % overlay) — no añadir otro.
4. La transición gráfica → horizonte (10,5–11,85 s) se mantiene en código: el plano de Kling entra con la misma máscara que abre desde la línea (`scene04`).
5. Para la escena 05 se necesita el mismo plano limpio hasta 16,0 s (fondo detrás de la persona) → generar 5 s.
