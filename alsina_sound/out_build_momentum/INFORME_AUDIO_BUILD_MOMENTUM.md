# ALSINA REEL CHILE · DEMO 6 · «Build Momentum»

**Imagen:** `VIDEO REEL CHILE_DEMO 6.mp4` (1080×1920, 25 fps, 885 fotogramas, 35,400 s). **No se ha tocado.** El vídeo del MP4 entregado es idéntico al original bit a bit (MD5 de paquetes) y fotograma a fotograma (MD5 de los 885 fotogramas decodificados).

**Música:** `Build Momentum.mp3`: 21,24 s, 169,3 BPM, en mi. Solo se ha editado por compases: sin estirar, sin cambio de tempo ni de tono.

## 1. Ancla: el punto de la «i»

- **f752**: el punto todavía cae, por encima de la palabra incompleta.
- **f753 (30,120–30,160 s)**: el punto entra en la «i» y «Alsina» queda completa. Ver `revision/PUNTO_I_f747-f756.png` y `revision/PUNTO_I_f753_completo.png`.

El golpe de resolución del propio tema (19,371 s de la canción: último tresillo del fill + entrada del acorde de subgrave) se ha colocado en **30,125 s**. Todo lo anterior se ha montado hacia atrás desde ahí.
- **Pico de la mezcla**: 30,134 s, dentro de f753.
- **Golpe más fuerte de la pieza**: −8,9 (K-ponderado, 400 ms). El siguiente es −9,5.
- **Antes**: el fill en tresillos del tema (desde 29,65 s) acompaña la caída del punto.
- **Después**: no hay golpes nuevos. El acorde se sostiene con una cola de reverberación limpia (RT60 2,6 s), a unos −46 dB a los 32 s y −72 dB a los 33 s.

## 2. Reedición de la canción

Bloques continuos del tema, unidos siempre en inicio de compás con fundidos de igual potencia de 12 ms, 6 ms antes del golpe entrante:

| Vídeo (s) | Tema (s) | Contenido |
|---|---|---|
| 0,000–6,990 | 0,574–7,564 | sección A (arranca con intención en el fotograma 0) |
| 6,990–14,067 | 10,403–17,480 | A' + transición + A'' |
| 14,067–23,983 | 7,564–17,480 | breakdown (bajo EDIFICACIÓN CHILENA / contador) → **vuelve el tema completo en 16,906 s**, con el cubo de grúa |
| 23,983–26,816 | 14,647–17,480 | A'' (MONTAJE SIMPLE / CALIDAD) |
| 26,816–28,234 | 17,480–18,898 | break de 1 compás, en el corte a cenital (26,80 s) |
| 28,234–fin | 17,480–final | break + fill + **resolución en el punto** + cola |

**Uniones:** el desajuste se comprobó por correlación cruzada. Dos inicios de compás mal detectados (beats 21 y 41) se corrigieron con la mediana regional de transitorios.

**Mezcla y master:**
- El cuerpo de la música va 1,2 dB por debajo y sube durante el break hacia el clímax, para que el punto sea el acento más concluyente.
- Ducking en 3 bandas solo en los golpes principales.

## 3. Puntos de sincronización

La tabla completa está en `PUNTOS_DE_SINCRONIZACION.csv`.

| Momento | Tiempo (s) | Fotograma | Qué suena |
|---|---|---|---|
| Arranque | 0,000 | f0 | golpe de bajo del tema |
| Zoom 1 | 0,300 | f7 | percusión complementaria (la canción no tiene golpe aquí) |
| Zoom 2a | 0,931 | f23 | beat del tema + whoosh |
| Zoom 2b | 1,285 | f31/32 | primer tiempo fuerte + golpe grave (5 ms tras el final de f31) |
| DE GRÚA | 3,309 | f82–83 | acento + golpe con cuerpo |
| ALISPLAY | 5,220 | f130 | whoosh (pico) |
| 240 PLUS | 9,200 | f229–230 | golpe seco + whoosh |
| DISEÑADO PARA | 11,947 | f298 | acento musical + whoosh grave |
| Breakdown | 14,067 | f351 | estructura del tema |
| Vuelve el tema | 16,906 | f422 | primer tiempo, cubo entra en f424 |
| GRÚA en rojo | 20,120 | f503 | contacto metálico |
| MONTAJE SIMPLE | 21,800 | f545 | whoosh |
| SIMPLE | 22,559 | f563 | acento + golpe seco |
| CALIDAD | 23,269 | f581/582 | acento + golpe con peso (11 ms antes de f582) |
| Break | 26,816 | f670 | corte a cenital |
| Fill | 29,652 | f741 | caída del punto |
| **Punto de la «i»** | **30,125** | **f753** | **resolución del tema + impacto (pico 30,134 s)** |
| Fundido | 34,960 | f874 | con el fundido a negro del vídeo |

## 4. Control

| | Integrado | Pico verdadero | LRA |
|---|---|---|---|
| WAV 48 kHz / 24 bits | −14,0 LUFS | −1,2 dBTP | 3,1 |
| AAC 320 kb/s del MP4 | −14,1 LUFS | −1,2 dBTP | — |

- **Sincronía**: desfase AAC/WAV de 0 muestras.
- **Limpieza**: 0 clics en la mezcla y en la música.
- **Compatibilidad**: correlación L/R 0,87, sin pérdidas al sumar a mono.
- **Limitador**: solo toca transitorios aislados, con un máximo de 1,9 dB en el impacto y 1,5 dB en 11,95 s.

## 5. Límites (léelos)

- **No puedo escuchar.** Todo está verificado por medición (curvas de acento, espectro, sonoridad) y revisión fotograma a fotograma. Haz una escucha final con `revision/REVISION_50pct_BUILD_MOMENTUM_sync.mp4`.
- **Repetición de compases.** El tema dura 21,24 s y el vídeo 35,40 s, así que hay compases repetidos: el breakdown + A'/A'' suenan dos veces y el break se dobla. Las uniones son limpias y en compás.
- **Zoom 1.** Los zooms están separados 0,96 s y los acentos del tema 1,07 s, así que la música no puede cubrir los dos. El zoom 2 lleva el tiempo fuerte del tema y el zoom 1 lo lleva percusión complementaria del pack.
- **Licencia.** La canción tiene metadatos «made with suno». Confirma la licencia comercial antes de publicar.

## 6. Archivos

- `ALSINA_REEL_CHILE_DEMO6_BUILD_MOMENTUM.mp4`: vídeo original + mezcla.
- `ALSINA_BM_MEZCLA_FINAL_48k24.wav`, `ALSINA_BM_MUSICA_STEM_48k24.wav`, `ALSINA_BM_SFX_STEM_48k24.wav`.
- `revision/`: vídeos de revisión a 1× y 50 % con marcas de sincronía, curvas de apertura y cierre, y fotogramas del punto.
- **Reconstrucción**: `tools/build_bm.py` + `tools/music_bm.py` + `tools/cues_bm.py`.
