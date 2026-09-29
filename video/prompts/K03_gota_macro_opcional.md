# K03 · (Opcional) Impacto macro de tinta real — 0,6–1,0 s

**Sustituye a:** salpicadura 2D de `drawDropAndSplash()` (s01). La versión en código ya es final y funciona; este plano solo añade fisicidad. **Prioridad baja.**
Mejor opción: rodaje real (tinta magenta con glicerina sobre papel impreso, 240–1000 fps, 100 mm macro). Kling como alternativa.

## Imagen inicial
`frames/f0020.png` (la gota a punto de tocar la palabra "ES").
## Imagen final
`frames/f0034.png` (charco formado, corona de gotas satélite).

## Prompt definitivo
```
Extreme macro, top-down, vertical 9:16. A single glossy magenta ink droplet (#E6197D) falls onto
matte off-white technical drawing paper printed with grey engineering lines and the bold
grey word "ES". The drop hits the center of the word and bursts into a crisp crown splash
with small satellite droplets radiating outward, then settles into a round glossy ink pool
with a slightly darker rim. Ultra slow motion 1000 fps feel, raking side light, paper fiber
texture visible, locked camera.
```
**Duración:** 2 s generados → se retimean a 0,4 s.
**Cámara:** fija, cenital. **Sujeto:** solo la gota y la tinta.
**Restricciones:** la tinta no debe tapar "COMPLICADO."; el charco no debe pasar de ~300 px de diámetro.
**Negative prompt:** `blood, red, purple, paint brush, hand, multiple drops, colored paper, text changes, blur, camera move`
**Consistencia:** componer con modo *multiply* sobre el papel del máster; mantener `ERA` en código (s01 `drawHeadline`).
