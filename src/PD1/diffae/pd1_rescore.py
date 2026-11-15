"""PD1 DiffAE family: re-score the external sets (FRLL 256 and stored, mirror mixes, softened genuine photos, benchmark
cells) with the saved final heads, using the corrected FRLL person draw (the 102 real FRLL persons, AD1's seed), and
replace the "external" blocks of results_<feat>.json. No head is refitted. Point estimates are unchanged by the fix;
only the bootstrap draw changes (the first runs drew over 140 IDs, 38 of them without images).
Run: OMP_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/diffae/pd1_rescore.py --feats clip_pool,...
"""
import argparse, json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_common as K
import pd1_analysis as A


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feats", default=",".join(K.FEATS))
    a = ap.parse_args()
    rows = K.items()
    for feat in a.feats.split(","):
        p = K.OUT / f"results_{feat}.json"
        if not p.exists():
            print("missing", p)
            continue
        res = json.load(open(p))
        F = K.load_feats(feat, ("f256", "fr512", "ev", "smdd", "ad1b"))
        ids, FX = A.ext_matrix(rows, F, ("f256", "fr512", "ev", "smdd", "ad1b"))
        for var, vv in res["Q3Q4"].items():
            ext = {}
            for h in ("H1", "H2"):
                z = np.load(K.BIG / "heads" / f"{feat}_{var}_{h}.npz", allow_pickle=False)
                U = z["U"] if z["U"].size else None
                X = A.project(FX, U)
                s = ((X - z["mu"]) / z["sd"]) @ z["w"]
                old = vv.get("external", {}).get(h)
                new = A.external(rows, ids, s)
                if old is not None:                      # point estimates must agree with the original run
                    for fam, c in new["bench"].items():
                        assert abs(c["native"]["auc"] - old["bench"][fam]["native"]["auc"]) < 1e-9, (feat, var, h, fam)
                ext[h] = new
            vv["external"] = ext
            vv["external_note"] = "re-scored with saved final heads; FRLL draw over the 102 real persons (pd1_rescore.py)"
        json.dump(res, open(p, "w"), indent=1, default=float)
        print("rescored", feat)


if __name__ == "__main__":
    main()
