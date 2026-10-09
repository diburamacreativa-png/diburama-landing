"""Momentary loudness (EBU 400 ms, K-weighted) per narrative section, for one or more mixes."""
import sys, numpy as np, soundfile as sf, pyloudnorm as pyln
SECT = [("0-1 caída", 0.0, 0.95), ("impacto", 0.95, 1.5), ("1.5-3.4 ASMR", 1.5, 3.35), ("T1 3.43", 3.3, 3.7),
        ("3.7-7.4 pan/rodaje", 3.7, 7.35), ("T2 7.5", 7.35, 7.8), ("7.8-10.6 motion", 7.8, 10.6), ("T3 10.7", 10.6, 11.0),
        ("11-13.5 3D", 11.0, 13.5), ("T4 13.6", 13.5, 13.9), ("13.9-15.6 ilustr.", 13.9, 15.6), ("regreso", 15.7, 16.9),
        ("MORDISCO", 17.05, 17.6), ("plato", 18.6, 19.7), ("copy", 19.9, 22.3), ("firma/CTA", 22.7, 24.0), ("bucle", 24.3, 25.0)]
def kw(x, sr):
    m = pyln.Meter(sr); y = x.copy()
    for f in m._filters.values(): y = f.apply_filter(y.T if False else y)
    return y
for p in sys.argv[1:]:
    x, sr = sf.read(p); m = pyln.Meter(sr); y = x.copy()
    for f in m._filters.values(): y = f.apply_filter(y)
    w, h = int(0.4 * sr), int(0.05 * sr)
    print("==", p.split("/")[-1], "integrated", round(m.integrated_loudness(x), 2), "LUFS")
    for name, a, b in SECT:
        v = [-0.691 + 10 * np.log10(np.sum(np.mean(y[i:i + w] ** 2, axis=0)) + 1e-12) for i in range(int(a * sr), max(int(a * sr) + 1, int(b * sr) - w), h)]
        print(f"   {name:20s} max {max(v):6.1f}  median {np.median(v):6.1f}")
