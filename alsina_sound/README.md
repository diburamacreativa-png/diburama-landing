# ALSINA CHILE · audio del reel 9:16

- Entregables e informe: `out/` (empieza por `out/INFORME_AUDIO_ALSINA_REEL.md`).
- Reconstrucción (requiere ffmpeg con rubberband y numpy):

```
python3 -I tools/build_audio.py --music "Groovy Good Vibes.mp3" \
    --pack <ALSINA_MOTION_SFX_PACK descomprimido> \
    --video Alsina_Reel_Chile_ref_01.mp4 --out out
python3 -I tools/make_review.py --video Alsina_Reel_Chile_ref_01.mp4 --out out
```

- Cues editables en `tools/cues.py` (fotograma, archivo, nivel relativo a la música, pan, pitch, EQ).
