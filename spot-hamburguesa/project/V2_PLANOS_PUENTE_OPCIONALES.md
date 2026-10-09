# V2 — Planos puente opcionales (solo si T3 o T4 no se aprueban en composición 2D)

Las cuatro transiciones de la FASE A están resueltas por composición sobre el material existente.
T3 y T4 simulan una transformación de material y una rotación sin geometría 3D real. Si queréis una
órbita de cámara real alrededor de la pieza, hace falta un plano puente generado. Formato: 9:16,
24 fps, 2–3 s, sin cortes, misma luz cálida y fondo oscuro que el spot. Usar como primer y último
frame los fotogramas indicados (image-to-video con start/end frame en Kling).

## Puente T3 — queso → metal → engranaje
- Start frame: `plano 6A.mp4`, frame 86 · End frame: `plano 6B.mp4`, frame 0
- Prompt: "Macro shot. A glossy ribbon of melted cheese curls into a ring and slowly rotates towards
  the camera. While it turns its material hardens: cheese becomes translucent amber glass, then
  polished dark gunmetal. The ring grows teeth and locks into a mechanical gear. The camera orbits
  45 degrees around it. Warm practical lights, magenta ribbons in the background, shallow depth of
  field, photoreal, no text."

## Puente T4 — rodamiento → nervios → ilustración
- Start frame: `plano 7A.mp4`, frame 44 · End frame: `plano 8A.mp4`, frame 0
- Prompt: "Camera flies forward through the inner ring of a polished bronze ball bearing. The metal
  softens and becomes organic: its machined grooves turn into the veins of a green leaf, the steel
  balls become dew drops, the ring opens like a leaf. Through it we discover an illustrated landscape
  of lettuce hills and fields. Continuous forward camera motion, warm light, photoreal to
  illustration, no text."

Integración: sustituye la ventana `T3` o `T4` en `project/edit_decisions.json` por un segmento con el
clip puente (dissolve de 2 frames en cada extremo). El resto del spot no cambia.
