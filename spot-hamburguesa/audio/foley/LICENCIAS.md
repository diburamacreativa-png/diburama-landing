# Foley V2: procedencia y comprobación de licencias

**Estado:** comprobación parcial. Integridad verificada; licencia **no verificada en línea**, porque pixabay.com y freesound.org no son accesibles desde el entorno de producción. Antes de publicar, alguien debe abrir cada enlace de la tabla y guardar una captura de la página de descarga como comprobante.

## 1. Integridad
Los 16 archivos de `originales/` coinciden byte a byte (SHA-256) con `MAPEO_ORIGINALES.csv`. Se usan sin recomprimir; todo el procesado ocurre en la mezcla y nunca se modifica el original.

## 2. Procedencia deducida
El patrón de los nombres originales (`autor-titulo-ID.mp3`) es el de las descargas de **Pixabay Sound Effects**. Los autores `freesound_community` son sonidos importados por Pixabay desde Freesound. Los enlaces probables (ID al final) son:

| Archivo | Original | Autor | Página probable |
|---|---|---|---|
| 01_carne_parrilla | adding-bacon-to-frying-pan-29957 | freesound_community | https://pixabay.com/sound-effects/adding-bacon-to-frying-pan-29957/ |
| 02_sizzle_base | frying-pan-hot-sizzle-loop-1-200912 | floraphonic | https://pixabay.com/sound-effects/frying-pan-hot-sizzle-loop-1-200912/ |
| 03_sizzle_detalle | cooking-oil-sizzle-1-171525 | floraphonic | https://pixabay.com/sound-effects/cooking-oil-sizzle-1-171525/ |
| 04_fuego | fire-sounds-356121 | dragon-studio | https://pixabay.com/sound-effects/fire-sounds-356121/ |
| 05_vapor | air-or-steam-pressure-release-29600 | freesound_community | https://pixabay.com/sound-effects/air-or-steam-pressure-release-29600/ |
| 06_queso_textura | mixing-pasta-76522 | freesound_community | https://pixabay.com/sound-effects/mixing-pasta-76522/ |
| 07_queso_elastico | squishing-gel-between-hands-25972 | freesound_community | https://pixabay.com/sound-effects/squishing-gel-between-hands-25972/ |
| 08_engranajes | ancient-mechanical-gears-487670 | dragon-studio | https://pixabay.com/sound-effects/ancient-mechanical-gears-487670/ |
| 09_impacto_metalico | giant-gears-504025 | dragon-studio | https://pixabay.com/sound-effects/giant-gears-504025/ |
| 10_whoosh | whoosh-velocity-383019 | soundreality | https://pixabay.com/sound-effects/whoosh-velocity-383019/ |
| 11_transicion | dramatic-transition-346046 | dragon-studio | https://pixabay.com/sound-effects/dramatic-transition-346046/ |
| 12_mordisco | bite-in-crunchy-bread-46216 | freesound_community | https://pixabay.com/sound-effects/bite-in-crunchy-bread-46216/ |
| 13_crunch_asmr | crispy-and-crunchy-eating-cookies-or-bread-from-a-plate-asmr-8266 | juliush | https://pixabay.com/sound-effects/crispy-and-crunchy-eating-cookies-or-bread-from-a-plate-asmr-8266/ |
| 14_plato | put-to-table-a-dish-80565 | freesound_community | https://pixabay.com/sound-effects/put-to-table-a-dish-80565/ |
| 15_cubiertos | cutlery-on-plate-449635 | oxidvideos | https://pixabay.com/sound-effects/cutlery-on-plate-449635/ |
| 16_impacto_humedo | wet-impact-352440 | universfield | https://pixabay.com/sound-effects/wet-impact-352440/ |

## 3. Qué permite la licencia de Pixabay (según mi conocimiento; verificar el texto vigente)
- **Permite** el uso comercial dentro de una obra (un anuncio) sin atribución obligatoria.
- **No permite** redistribuir los sonidos sueltos (*standalone*), venderlos ni ofrecerlos como sonidos.
- **No permite** usarlos como parte de una marca registrada.

## 4. Decisiones tomadas por la licencia
1. **El repositorio de GitHub es público.** Por eso los MP3 originales, las pistas aisladas por efecto (`audio/v2/*/tracks/`) y los stems FOLEY / SFX / AMBIENTES **no se suben** (están en `.gitignore`). Se entregan directamente al cliente. Al repositorio solo van el código, la música, las mezclas finales y los vídeos, donde los sonidos están integrados en la obra.
2. **Firma sonora:** la "gota" del cierre usa `07_queso_elastico` transpuesto. Sirve para el anuncio, pero **si Diburama quiere registrar la firma sonora como marca, ese elemento debe sustituirse** por una grabación propia.
3. Los sonidos `freesound_community` proceden de Freesound. Si el origen era CC0, no hay ninguna restricción adicional, pero conviene confirmarlo en cada página.

## 5. Efectos que el ZIP no incluía
No había **hojas**, **lápiz**, **migas** ni **tono de sala**. Se han resuelto con grabaciones del propio ZIP, nunca con síntesis, y conviene sustituirlos si se consigue material específico:
- hojas → `06_queso_textura` con paso alto (textura húmeda orgánica);
- migas → dos toques suaves de `14_plato` con paso alto;
- tono de sala → el ruido de fondo de `14_plato`, de 0,1 a 1,8 s.
