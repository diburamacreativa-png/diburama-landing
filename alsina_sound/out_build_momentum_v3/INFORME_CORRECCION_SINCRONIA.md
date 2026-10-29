# ALSINA REEL CHILE · DEMO 6 · «Build Momentum»: corrección de sincronía

**Material corregido**: `ALSINA_REEL_CHILE_DEMO6_BUILD_MOMENTUM.mp4`, el primer montaje con el tema de 21,24 s. Es idéntico (MD5) al entregado en `out_build_momentum/`.
- La corrección parte de sus pistas separadas y del MP3 original, `Build Momentum.mp3`.
- **Vídeo intacto**: flujo copiado sin recodificar. MD5 de paquetes idéntico al original y los 885 fotogramas idénticos (framemd5).

## 1. Diagnóstico del primer montaje

Medido en la mezcla: pico de energía K de 40 ms en la ventana [−200 ; +120 ms] de cada llegada visual, comprobando qué pista lo produce.

**Problema general.** Los efectos estaban mezclados muy por debajo de la música. En casi todos los cambios el acento percibido era un tiempo del tema que caía **antes** de la imagen.

| Evento | Fotograma | Pico de energía (antes → ahora) | Qué pasaba |
|---|---|---|---|
| Impulso 1 | f7 | −41 → **+21 ms** | Un tiempo del tema (0,217 s, platos) sonaba 63 ms antes del zoom; el golpe iba a 0,300 s y quedaba por debajo. |
| Impulso 2 | f31 | +67 → **+23 ms** | El golpe estaba en 1,285 s, en f32: **retrasado**. |
| SIN | f23 | +35 → +35 ms | Ya coincidía con un tiempo del tema; solo se cambia el whoosh por un acento de texto ligero. |
| DE GRÚA | f83 | −108 → **+22 ms** | El golpe estaba 11 ms **antes** del corte y era más débil que el pico del tema en 3,21 s. |
| Corte ALISPLAY | f131 | −125 → **+9 ms** | Sin golpe: solo whoosh. |
| 240 PLUS | f230 | −46 → **+22 ms** | El bombo del tema llegaba 50 ms antes y el whoosh grave largo alargaba la energía hasta ~9,26 s. |
| DISEÑADO | f298 | −190 → −190 ms | El golpe ya estaba fundido con un transitorio del tema en 11,947 s; el pico de −190 ms es un tiempo de la música. **Se conserva.** |
| Llegada tras el cubo | f433 | −141 → **+16 ms** | Sin remate. |
| MONTAJE SIMPLE | f545 | −154 → **+20 ms** | Sin golpe: la llegada dependía del tiempo del tema en 21,64 s. |
| CALIDAD. | f582 | −106 → **+21 ms** | El golpe iba 11 ms **antes** del fotograma. |
| Corte a cenital | f670 | −82 → **+37 ms** | Sin golpe. |
| **Punto blanco** | **f738** | −80 → **+32 ms** | La resolución estaba en 30,125 s (f753), 0,60 s después del punto. |

En SIMPLE (−171 ms) y MENOS (−75 ms) el pico sigue siendo un tiempo del tema, porque son acentos de texto ligeros. Se ha comprobado que el golpe se oye en su banda: +8,7 dB y +10,3 dB en 1–4 kHz.

## 2. Qué se ha hecho

La lista completa está en `ACENTOS_MOVIDOS.csv`, con el tiempo anterior, el nuevo, el cambio en ms, el sonido y la acción.

**Nivel 1: música.**
- Es la misma edición del tema hasta 28,23 s, sin desplazar nada.
- Seis tiempos del tema que adelantaban o doblaban una llegada se **atenúan brevemente** (40–65 ms, de −3 a −6 dB, solo en la banda donde estaba el acento):

| Tiempo del tema | Banda atenuada | Problema |
|---|---|---|
| 0,217 s | medios y agudos (platos) | 63 ms antes del impulso 1 |
| 1,285 s | graves, medios y agudos | 45 ms detrás del impulso 2 (doble ataque) |
| 9,15 s | graves (bombo) | 50 ms antes del corte a 240 |
| 21,64 s | medios y agudos | 160 ms antes de MONTAJE SIMPLE |
| 22,56 s | medios y agudos | semicorchea 40 ms después de SIMPLE |
| 23,27 s | medios y agudos | 13 ms antes de CALIDAD |

**Nivel 2: impactos de cámara y escena.**
- **Movidos** al inicio exacto del fotograma:
  - impulso 1, de 0,300 a 0,282 s;
  - impulso 2, de 1,285 a 1,244 s;
  - DE GRÚA, de 3,309 a 3,322 s.
- **Sustituido**: 240 PLUS pasa de un HIT_01 débil y un whoosh grave largo a un arrastre corto más un HIT_03 en 9,202 s.
- **Nuevos**:
  - corte ALISPLAY, 5,242 s (medio);
  - llegada tras el cubo, 17,322 s (medio);
  - MONTAJE SIMPLE, 21,802 s;
  - corte a cenital, 26,817 s (medio, fundido con la entrada del break).
- Los arrastres (whoosh o aspiración) empiezan con el movimiento y terminan antes de la llegada, no encima de ella.

**Nivel 3: textos** (acentos ligeros en el asentamiento, comprobado fotograma a fotograma).

| Texto | Fotograma | Tiempo (s) | Nota |
|---|---|---|---|
| SIN | f23 | 0,931 | fundido con el tiempo del tema |
| ALISPLAY | f141 | 5,642 | |
| PLUS | f243 | 9,722 | |
| EDIFICACIÓN | f341 | 13,642 | |
| Medida fija en **2,40 m** | f393 | 15,722 | ningún golpe por cifra |
| MENOS | f444 | 17,762 | |
| DEPENDENCIA | f458 | 18,319 | |
| DE GRÚA | f476 | 19,042 | |
| GRÚA en rojo | f503 | — | conservado, más discreto |
| SIMPLE | f563 | 22,524 | movido desde 22,559 |
| CALIDAD. | f582 | 23,282 | movido desde 23,269 |

**Impulsos del inicio.** Los tres saltos son de cámara (escala del fondo −21 %, −17 % y −16,5 % en un fotograma) y cada uno trae una palabra.
- f7 y f31 son los impulsos principales y llevan percusión corta con cuerpo.
- f23 (SIN) es el salto menor: lleva solo el acento de texto, sobre el tiempo del tema.
- Así los tres no pesan igual: impulso 1, −12,1 LUFS; impulso 2, −12,5; SIN, −13,7 (K de 150 ms).

## 3. Cierre

**Ancla confirmada en el vídeo original a 25 fps**:
- en f737 (29,48 s) aún se ve el iris;
- en **f738 (29,520–29,560 s)** aparece el punto blanco aislado sobre negro (ver `revision/PUNTO_BLANCO_f735-f740.png`).

Reconstrucción desde el MP3 original:

| Vídeo | Qué ocurre |
|---|---|
| 26,816 s | Break del tema (compás 49), con el corte a cenital, como antes. |
| 28,234 s | Segunda pasada del break, acortada a dos tiempos. |
| 28,951 s | **Redoble en tresillos** del propio tema bajo la aceleración del alejamiento (f723–f734). Crece con una única textura de aceleración (RISER_03 que se abre en filtro y volumen). Sustituye al Doppler descendente y a las aspiraciones anteriores. |
| 29,425 s | La música se detiene en el último golpe del redoble mientras se cierra el iris: **vacío de 97 ms**. El riser y una aspiración siguen sonando, así que no se pierde el impulso. |
| **29,521 s** | **Golpe principal**: la resolución del tema (acorde con subgrave) fundida con HIT_07 (cuerpo), HIT_03 (grave controlado, afinado en Mi), metal en Mi, cuerpo en medios y un clack de ataque. |
| 29,52–35,40 s | **Cola**: el acorde seco se apaga (30,0–30,7 s) dentro de una reverberación del acorde (RT60 3 s) y de un **lecho ambiental muy discreto**, el espectro del acorde congelado, sin ataques ni ritmo. La caída del punto, su entrada en la «i» (f753) y la formación del logo van solo con esa cola. |

**Nivel de la cola** (K, 40 ms):

| Tiempo | Antes | Ahora |
|---|---|---|
| 31,5 s | −32 dB | −41 dB |
| 32,5 s | −56 dB | −45 dB |
| 33,8 s | −83 dB | −48 dB |
| 34,5 s | −118 dB | −50 dB |

Se funde a cero con el fundido a negro del vídeo (f874–883). No se ha alargado la reverberación: la permanencia la sostiene el lecho.

**Golpe final**: su ataque está en 29,521 s y el máximo de energía, en 29,552 s, ambos dentro de f738. Es el momento más fuerte de la pieza (−9,1 LUFS K de 150 ms; los siguientes, −10,0 en 240 PLUS y −10,1 en ALISPLAY).

## 4. Control

| | Integrado | Pico verdadero | LRA |
|---|---|---|---|
| WAV 48 kHz / 24 bits | −14,0 LUFS | −1,1 dBTP | 2,7 LU |
| AAC 320 kb/s del MP4 | −14,1 LUFS | −1,2 dBTP | 2,7 LU |

- **Limitador**: actúa solo en ataques de golpes, con un máximo de 1,7 dB en unos milisegundos.
- **Limpieza**: 0 clics en la mezcla, la música y los efectos, incluido el vacío antes del punto.
- **Sincronía del MP4**: desfase AAC/WAV de 0 muestras (medido en 0,2 s, 9 s y 29,4 s).
- **Duración**: mezcla, efectos y música tienen 1 699 200 muestras (35,400 s) y empiezan en 00:00.
- **Revisión**: fotograma a fotograma sobre el MP4 exportado (`revision/SYNC_APERTURA.png`, `revision/SYNC_CIERRE.png`).

## 5. Límites

- **No puedo escuchar.** Todo está verificado por medición y revisión de imagen. La escucha final a velocidad normal y al 50 % (`revision/REVISION_*`) la tienes que hacer tú.
- **Golpe en f738, no en f753.** El golpe ya no está en f753, cuando el punto entra en la «i»: lo has fijado en su aparición. Ese asentamiento queda solo con la cola.
- **Pausa de 97 ms antes de la resolución.** El cierre lo exige porque la resolución cae 1/3 de tiempo después de donde la pondría el tema. Va cubierta por el riser, mientras el iris se cierra.
- **Versión completa del tema.** Existe otra entrega con la versión completa (`out_build_momentum_v2/`); esta corrección no la toca.
- **Licencia.** El tema lleva «made with suno»: confirma la licencia comercial.

## 6. Archivos (`out_build_momentum_v3/`)

- `ALSINA_REEL_CHILE_DEMO6_BUILD_MOMENTUM_CORREGIDO.mp4`: imagen original + mezcla.
- `ALSINA_BM3_MEZCLA_FINAL_48k24.wav`: mezcla completa.
- `ALSINA_BM3_EFECTOS_48k24.wav`: solo percusión y efectos, desde 00:00 y con la duración del vídeo.
- `ALSINA_BM3_MUSICA_STEM_48k24.wav`: música editada.
- `ACENTOS_MOVIDOS.csv`: acentos movidos, sustituidos, nuevos y conservados.
- `revision/`: vídeos de revisión a 1× y 50 %, imágenes de sincronía y fotogramas del punto.
- **Reconstrucción**: `tools/build_bm3.py`, `music_bm3.py`, `cues_bm3.py` y `lista_cambios_bm3.py`.
