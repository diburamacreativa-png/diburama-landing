# ALSINA REEL CHILE · DEMO 6 · «Build Momentum (1)» (versión completa)

## 0. Material

- **Vídeo**: `VIDEO REEL CHILE_DEMO 6(4).mp4`. Es el mismo archivo que el DEMO 6 anterior (MD5 idéntico): 1080×1920, 25 fps, 885 fotogramas, 35,400 s.
  - **No se ha tocado.** El MP4 final copia el flujo de vídeo sin recodificar.
  - Comprobado: MD5 de paquetes idéntico y los 885 fotogramas decodificados idénticos (framemd5).
- **Música**: `Build Momentum (1)(1).mp3` es una versión nueva y completa del tema (173,23 s), no la de 21 s de la entrega anterior.
  - Medido: 126 BPM, tonalidad de Sol.
  - Armonía de la sección final: Sol (4 compases), Fa (2), Do (2), Sol, y un golpe final con acorde de Sol.

## 1. Análisis visual (antes de editar)

**Método**:
1. Estimación automática del movimiento global por fotograma (escala y traslación por correlación de fase), más residuo y cambio de histograma, para detectar cortes, zooms, aceleraciones y frenadas.
2. Revisión manual en hojas de contacto de cada zona, fotograma a fotograma, para fijar el instante perceptible: la llegada o asentamiento, no el máximo de movimiento.

La lista completa está en `LISTA_DE_ACENTOS.csv`: fotograma, tiempo, acción, fuerza y lo que suena, incluidos los eventos que se dejan **sin** golpe. Principales:

| Fotograma | Tiempo (s) | Acción visual | Fuerza |
|---|---|---|---|
| f7 | 0,28 | **Impulso de cámara 1** (alejamiento brusco) + MONTAJES | FUERTE |
| f23 | 0,92 | Salto intermedio del zoom + SIN | MEDIO |
| f31 | 1,24 | **Impulso de cámara 2** + NECESIDAD | FUERTE |
| f79–83 | 3,16–3,32 | Latigazo con desenfoque y **corte a DE GRÚA** | FUERTE |
| f127–131 | 5,08–5,24 | Paneo que acelera y corte a ALISPLAY | MEDIO |
| f141 / f151 | 5,64 / 6,04 | ALISPLAY / MANUAL se asientan | LIGERO |
| f227–230 | 9,08–9,20 | Latigazo y **corte a 240 PLUS** | FUERTE |
| f243 | 9,72 | PLUS completa su caída | LIGERO |
| f298 | 11,92 | Corte a DISEÑADO PARA (se asienta en f304) | MEDIO |
| f393 | 15,72 | El contador se detiene en 2,40 m | LIGERO |
| f425–433 | 17,00–17,32 | El cubo de la grúa barre el plano (corte oculto en f430) | MEDIO |
| f503 | 20,12 | GRÚA destella en rojo | LIGERO |
| f563 / f582 | 22,52 / 23,28 | SIMPLE / CALIDAD. aterrizan | MEDIO |
| f668–670 | 26,72–26,80 | Latigazo y **corte a la toma cenital** | FUERTE |
| f708–737 | 28,32–29,48 | Alejamiento que acelera y cierre del iris | anticipación |
| f738 | 29,52 | Negro: nace el punto (cuadrado blanco) | LIGERO |
| **f753** | **30,12** | **El punto se asienta en la «i»: «Alsina» completo** | **ANCLA** |

Se dejan **sin golpe**, por jerarquía y para que el montaje respire:
- la frenada del paneo (f89);
- CHILENA;
- MENOS DEPENDENCIA DE GRÚA;
- MONTAJE;
- ACABADOS DE;
- la entrada de «x», ALTIUS y el lema final.

## 2. El punto de la «i»

Recorrido del punto (ver `revision/PUNTO_I_f747-f756.png`, `PUNTO_I_f753_completo.png` y `SYNC_CIERRE.png`):

| Fotogramas | Qué ocurre |
|---|---|
| f735–737 | El iris se cierra. |
| f738 (29,52 s) | Pantalla negra: nace el punto, un cuadrado blanco. |
| f738–752 | El punto cae y se encoge; en f750–752 se ensamblan las letras. |
| **f752** | El punto aún está por encima de la palabra incompleta. |
| **f753 (30,120–30,160 s)** | El punto entra en la «i» y «Alsina» queda completo. |
| f754–766 | Aparecen «x» y ALTIUS. |
| f764–774 | Aparece el lema «ASÍ SE CONSTRUYE EN / CHILE \| GRAN VÍA». |

**Ancla: f753.** Es distinta de la aparición del punto (f738) y de la entrada del resto del logo (f754 en adelante).

## 3. Reedición de la música

**Sin cambios de tempo ni de tono.**
- Se evaluaron ajustes de tempo de ±3 %. El mejor solo mejoraba la puntuación de sincronía de 10,3 a 14,0, y no justificaba procesar el tema.
- Los bloques se unen en posiciones de la propia rejilla del tema (compás, tiempo o semicorchea), con fundidos de igual potencia de 12 ms, 6 ms antes del transitorio entrante.

| Vídeo (s) | Tema (s) | Contenido |
|---|---|---|
| 0,000–5,244 | 139,49–144,73 | Groove (compases 73–75). Durante los impulsos suena con paso alto, sin bombo ni bajo; el groove completo entra en 1,552 s (primer tiempo). |
| 5,244–9,178 | 148,54–152,47 | **Subida filtrada** (78–79). El groove se corta en la semicorchea que coincide con el corte de f131. |
| 9,178–14,891 | 152,47–158,19 | **Drop** (80–82). Transitorio a 9,173 s, en el latigazo hacia 240 PLUS. |
| 14,891–26,330 | 156,28–167,72 | 82–87: Sol, **Fa en 18,70 s**, **Do en 22,52 s** (= SIMPLE). Se repite el compás 82 (Sol) para cuadrar. |
| 26,330–26,804 | 165,82–166,29 | Un tiempo del compás 87. |
| 26,804–35,400 | 168,20 → final | Resolución propia del tema. Empieza en el corte a cenital (26,80 s): la batería se retira y sigue el acorde. |

**Resolución propia del tema**: compás 88, sin batería; compás 89, sin subgrave; **golpe final (compás 90)** en el punto de la «i»; y la cola del acorde.

**Por qué no hay música en los dos impulsos.** La rejilla del tema, fijada por el ancla, deja el bombo 150–170 ms antes de cada zoom: kick … golpe sonaba como un doble ataque.
- Solución: un paso alto de fase lineal sobre la música hasta el siguiente primer tiempo, con +2 dB de compensación. El ritmo, la base y los sintetizadores siguen; los golpes de zoom llevan solos el grave.
- Medido: intro −15,4 LUFS frente a −13,9 del groove, una subida intencionada.

## 4. Diseño de los acentos

**Familia única**: impactos, whooshes, risers y pops del pack Alsina.
- **Afinación**: los impactos con cuerpo (HIT_02/03/06/07) se afinaron a Sol (+1,6 st; su cola acaba en ~89 Hz → 98 Hz), HIT_01 a Re y el metal a Sol.
- **EQ**: realza 190–200 Hz y 1–3 kHz, para que los golpes se oigan en móvil y no dependan del subgrave.
- **Reverb**: sin reverberación en los golpes rítmicos.

**Jerarquía**, medida en sonoridad K de 150 ms:

| Nivel | Acentos | Sonoridad K (150 ms) |
|---|---|---|
| Ancla | punto de la «i» | −8,7 |
| Fuerte | drop 240 | −10,3 |
| Fuerte | impulso 1 / impulso 2 | −12,1 / −11,8 |
| Fuerte | DE GRÚA | −11,9 |
| Medio | textos principales y cortes secundarios | −14 a −15 |

Excepción: SIMPLE mide −10,9 porque coincide con el cambio a Do del propio tema; el golpe añadido es medio. Los ligeros son pops discretos.

**Anticipación y llegada**: los whooshes y aspiraciones empiezan con el movimiento (latigazos f79–82, f127–130, f227–229, f668–669) y desembocan en el golpe del fotograma de llegada.

**Sin dobles ataques**. Donde el tema ya tiene un transitorio en el instante correcto, el golpe se funde con él en lugar de duplicarlo:
- drop 240, GRÚA roja, SIMPLE y punto de la «i»;
- DE GRÚA (+19 ms) y SIN (+37 ms), siempre dentro de su fotograma;
- el contador (+39 ms), al final de su fotograma.

Una comprobación automática no deja golpes a 12–60 ms de un transitorio fuerte del tema, salvo los pops ligeros: quedan a 40–55 ms de una semicorchea y suenan como posiciones rítmicas distintas.

**Ducking**: bajadas breves por bandas en los impulsos, DE GRÚA, el cubo, CALIDAD, el corte a cenital y el punto (de 1,5 a 3 dB, con 0,15–0,45 s de recuperación).

## 5. Cierre

| Momento | Sonoridad K |
|---|---|
| Alejamiento | −14 LUFS |
| Negro, cae el punto | −19 LUFS |
| **Golpe en f753** | **−10 LUFS** |
| Cola | −12 LUFS, y después baja suave |

**Vacío**: al cerrarse el iris (f738) la música se retira (−3, −6 y −7 dB en graves, medios y agudos) mientras cae el punto, con un aire invertido que termina justo antes del golpe. La música vuelve entera 10 ms antes del ataque.

**Golpe**: el ataque del golpe del tema está en 30,129 s y todas las capas de impacto se fundieron con él.
- **Pico de la mezcla**: 30,212 s, el cuerpo grave del acorde ya iniciado.
- Es el momento más fuerte de la pieza en ventanas de 100, 150 y 400 ms.

**Cola**: no hay golpes nuevos después del punto. El acorde final del tema decae solo, prolongado por una reverberación oscura (RT60 4,2 s, paso alto de 70 Hz) que solo empieza en el golpe.

| Tiempo | Nivel de la cola |
|---|---|
| 32 s | −37 dB |
| 33 s | −50 dB |
| 34 s | −65 dB |

Después se apaga con el fundido a negro del vídeo (f874–883). La pieza termina en silencio a los 35,400 s.

## 6. Control

| | Integrado | Pico verdadero | LRA |
|---|---|---|---|
| WAV 48 kHz / 24 bits | −14,1 LUFS | −1,2 dBTP | 3,5 LU |
| AAC 320 kb/s del MP4 | −14,1 LUFS | −1,3 dBTP | 3,5 LU |

- **Limitador**: actúa solo en el impulso 1 (0,5 dB) y en el golpe final (≤ 1,95 dB).
- **Sincronía del MP4**: desfase AAC/WAV de 0 muestras, medido por correlación en 0,2 s, 9 s y 30 s.
- **Duración**: 35,400 s en ambos flujos.
- **Limpieza**: 0 clics en la mezcla y en la música. Uniones sin saltos ni huecos de energía.
- **Pistas de 00:00 a 35,400 s**: la percusión/SFX y la música tienen 1 699 200 muestras exactas. Mezcla = música + percusión, salvo el limitador del master.

## 7. Límites (léelos)

- **No puedo escuchar.** Todo está verificado por medición, imágenes de sincronía y revisión fotograma a fotograma. Haz una escucha final con `revision/REVISION_50pct_BUILD_MOMENTUM_FINAL_sync.mp4`.
- **Drop de 240 PLUS**: llega 27 ms antes del corte (en el último fotograma del latigazo, f229). Moverlo exigiría estirar la música; está por debajo del umbral habitual de adelanto de audio (~45 ms).
- **Desfases dentro del fotograma**: SIN, DE GRÚA y el contador suenan +37, +19 y +39 ms tras el inicio de su fotograma, para fundirse con el tema sin doble ataque.
- **Intro**: el tema suena con paso alto durante los impulsos (0–1,55 s). Si prefieres el groove completo desde el fotograma 0, es una línea (`INTRO_HP_HZ` en `music_bm2.py`), pero el bombo volvería a sonar justo antes de cada zoom.
- **Acentos ligeros**: son discretos a propósito; el clic del contador y el tick del nacimiento del punto quedan poco por encima de la música.
- **Licencia**: el MP3 lleva «made with suno». Confirma la licencia comercial antes de publicar.

## 8. Archivos (`out_build_momentum_v2/`)

- `ALSINA_REEL_CHILE_DEMO6_BUILD_MOMENTUM_FINAL.mp4`: imagen original copiada sin recodificar + mezcla AAC 48 kHz 320 kb/s.
- `ALSINA_BM2_MEZCLA_FINAL_48k24.wav`: mezcla completa, estéreo, 48 kHz, 24 bits.
- `ALSINA_BM2_PERCUSION_SFX_48k24.wav`: solo percusión y efectos añadidos, desde 00:00 y con la duración del vídeo.
- `ALSINA_BM2_MUSICA_STEM_48k24.wav`: música editada, con ducking y automatización.
- `LISTA_DE_ACENTOS.csv`: análisis visual y acentos.
- `build_stats_bm2.json`: datos del montaje.
- `revision/`: vídeos de revisión a 1× y 50 %; `SYNC_APERTURA.png` y `SYNC_CIERRE.png`, generadas desde el MP4 exportado; fotogramas del punto.
- **Reconstrucción**: `tools/build_bm2.py` + `music_bm2.py` + `cues_bm2.py` (+ `lista_acentos_bm2.py`).
