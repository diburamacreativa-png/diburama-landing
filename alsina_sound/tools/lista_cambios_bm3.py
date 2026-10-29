#!/usr/bin/env python3
"""Lista de acentos movidos / sustituidos / nuevos entre el primer montaje (build_stats_bm.json) y
la correccion (build_stats_bm3.json). Tiempos sacados de los builds, no escritos a mano.

Uso: python3 -I lista_cambios_bm3.py <dir_primer_montaje> <dir_corregido>
"""
import csv, json, os, sys

# id en la correccion -> id equivalente en el primer montaje
EQUIV = {"Z1h": "Z1b", "Z2t": "Z2a", "Z2h": "Z2c", "T03": "T03", "T06": "T06", "T05": "T05", "T07": "T07",
         "T09": "T09", "T10": "T10", "T11": "T11", "T12": "T12", "T13": "T13", "T14": "T14", "T15": "T15",
         "T16": "T16", "T17": "T17", "I01": "I01"}


def main():
    a = json.load(open(os.path.join(sys.argv[1], "build_stats_bm.json")))["cues"]
    b = json.load(open(os.path.join(sys.argv[2], "build_stats_bm3.json")))["cues"]
    old = {c["id"]: c for c in a}
    rows = []
    for c in b:
        if not c.get("accion"):
            continue
        o = old.get(EQUIV.get(c["id"], ""))
        t_new = c["event_s"]
        rows.append(dict(
            fotograma=int(round(c["nominal_s"] * 25 - 0.3)),
            momento=c["note"],
            nivel=c.get("tier") or "",
            antes_s=f"{o['event_s']:.3f}".replace(".", ",") if o else "",
            ahora_s=f"{t_new:.3f}".replace(".", ","),
            cambio_ms=f"{(t_new - o['event_s']) * 1000:+.0f}" if o else "",
            sonido=os.path.basename(c["file"])[:-4] + (" (fundido con el tema)" if c["snapped_to_music"] else ""),
            accion=c["accion"]))
    p = os.path.join(sys.argv[2], "ACENTOS_MOVIDOS.csv")
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(p, len(rows))


if __name__ == "__main__":
    main()
