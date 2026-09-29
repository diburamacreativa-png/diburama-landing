# K02 · Persona real a contraluz (13,0–16,0 s)

**Sustituye a:** silueta procedural `drawPersonReal()` en `src/scenes/s05_person.js`.
**Duración a generar:** 5 s, 9:16, 1080×1920, 30 fps. Idealmente **rodaje real de 1 hora** (croma o exterior al amanecer). Kling solo si no hay rodaje.

## Por qué hace falta
Con código solo se consigue una silueta. El 50 % real / 50 % ilustrado solo se ve bien si la mitad real es imagen real de verdad.

## Imagen inicial necesaria
`prompts/refs/K02_start.png` = K01_end (el mismo paisaje) con la persona **fuera de cuadro a la izquierda**.

## Imagen final necesaria
`prompts/refs/K02_end.png` = fotograma **f0479** del máster como guía de pose: persona de perfil mirando a la derecha, de pie en el centro-izquierda (cadera en x≈520, y≈1250), **brazo cercano extendido hacia delante a la altura del pecho con la palma hacia arriba**.

## Prompt definitivo
```
Vertical 9:16 cinematic shot at dawn, same landscape as the reference image, locked-off
camera with a very slow push in. A young adult professional (neutral, gender-ambiguous
styling, dark slim jacket, dark trousers, hair in a low ponytail) walks into frame from
the left in full side profile, walking calmly to the right along the valley road, fully
backlit by the low sun behind the ridge so the figure is an almost-black silhouette with a
thin warm rim light on the hair, shoulders and back. At the center of the frame the person
stops, turns their head slightly toward the horizon and slowly raises the near arm forward
to chest height, opening the hand palm up as if holding something tiny and precious.
Feet visible, full body in frame, head above the horizon line. Naturalistic motion,
35 mm, shallow depth of field, fine grain.
```

## Cámara
Fija con empuje lento (≈4 %). Sin paneo: la persona entra y se detiene.

## Sujeto
Timing a respetar (lo exige la tinta y la música):
- 13,0–13,6 entra caminando desde la izquierda
- 13,6–15,25 camina hasta el centro (≈1 paso por segundo)
- 15,25–15,95 se detiene y levanta la mano, palma arriba
- 15,95–16,0 quieta

## Restricciones
- Perfil puro mirando a la derecha: la rotoscopia 2D y la gota dependen de esa pose.
- Figura completa (pies a cabeza) entre y≈700 y y≈1750.
- Ropa lisa, sin logos, sin colores saturados.

## Negative prompt
```
face close-up, frontal view, extra limbs, deformed hands, six fingers, morphing body,
floating feet, text, logo, bright colored clothing, magenta, crowd, second person,
camera shake, fast motion, cartoon
```

## Consistencia con el máster
1. Rotoscopiar la figura (Roto Brush en After Effects) → máscara de la persona.
2. La versión ilustrada se dibuja **encima del plano real** a 12 fps (animación a mano en "unos"/"doses"), con el trazo y los colores de `drawPersonDrawn()`: línea #16161C de 10 px, chaqueta magenta #E6197D, piel #F4EFE8, pantalón #8A8A94.
3. La frontera real → ilustración ya está animada en código (`boundaryY()`); exportarla como máscara (tiene una pausa en el 50/50 entre 14,25 y 14,85 s).
4. La posición de la palma en 16,0 s tiene que coincidir con `palmPoint(16.0)`: es donde se forma la gota.
