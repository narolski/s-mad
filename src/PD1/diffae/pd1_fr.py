"""PD1 DiffAE family, Q5: glintr100 embeddings of the training hosts' aligned photos (x0), through AR1's registered
route src/AR1/fr.py (prep_eval.kps unchanged -> insightface norm_crop -> a2f_common.embed_crops('glint')), imported
unchanged. Measurement only; no image is written.

  pd1_fr.py [--limit 8 --tag smoke]
Writes /mnt/t7/smad_next/PD1/diffae/fr/tr_glint[_<tag>].npz (id, emb, found)
Run: nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/diffae/pd1_fr.py
"""
import argparse, csv, pathlib, sys
import numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/AR1")
import fr  # noqa: E402  (AR1, unchanged)

BIG = pathlib.Path("/mnt/t7/smad_next/PD1/diffae")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    rows = [r for r in csv.DictReader(open(BIG / "lists/items.csv")) if r["set"] == "tr" and r["rung"] == "x0"]
    if a.limit:
        rows = rows[:a.limit]
    emb, found = fr.embed_paths([r["path"] for r in rows], chunk=128, log=print)
    (BIG / "fr").mkdir(parents=True, exist_ok=True)
    out = BIG / "fr" / (f"tr_glint_{a.tag}.npz" if a.tag else "tr_glint.npz")
    np.savez(out, id=np.array([r["id"] for r in rows]), emb=emb, found=found)
    print("wrote", out, len(rows), "found", int(found.sum()))


if __name__ == "__main__":
    main()
