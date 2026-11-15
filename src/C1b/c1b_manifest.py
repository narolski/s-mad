"""C1b/C1c documentation: sha256 of every input score file, the FRLL raw photos, the frames read, outputs and code.
No statistics; reads bytes only. Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/C1b/c1b_manifest.py"""
import csv, hashlib, pathlib, sys
sys.path.insert(0, "/home/narolski/smad-next/src/C1b")
import c1b_read as C  # noqa: E402
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()
OUT = pathlib.Path("/home/narolski/smad-next/experiments/C1b")
rows = [(lab, grp, ck, key, str(f), sha(f)) for lab, grp, f, key, ck in C.detectors()]
ad4 = pathlib.Path("/mnt/t7/smad_next/AD4/zero_step/m3/scores_eval.npz")
rows.append(("AD4 untrained ViT-B/16 (zero-step, seed 401)", "untrained", "zero", "score", str(ad4), sha(ad4)))
with open(OUT / "c1b_input_scores_sha256.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["detector", "group", "ckpt", "key", "path", "sha256"]); w.writerows(rows)
raw = sorted(pathlib.Path("/mnt/t7/Datasety/downloads/frll_base/extracted").glob("*_front/*.jpg"))
with open(OUT / "c1b_frll_raw_sha256.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["path", "sha256"]); w.writerows([(str(p), sha(p)) for p in raw])
print(len(rows), "score files;", len(raw), "raw FRLL photos")
