"""PD1 DiffAE family: score the AD1b mirror mixes (photo mixed with its own mirror image, 20 steps, 256 lossless) with the
saved final heads (no refit). FRLL persons: diagnostic only.

For every feature set and variant with saved heads: AUC of mirror mix (xm) against the same photo's 20-step
reconstruction re-rendered in the AD1b job (D20r), paired share s(xm) > s(D20r), and AUC of xm against the A43 D20
reconstructions and against the photo (a256), with the FRLL person bootstrap (AD1's draw). Also the Q1 share of the
mirror step along the training same-person mixing direction, and its cosine with that direction.
Run: OMP_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/diffae/pd1_mirror.py
Writes experiments/PD1_signal-isolation-paired-differences/diffae/mirror.json and mirror.csv
"""
import csv, json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_common as K

VARIANTS = ("none", "soft1", "soft5", "pipe", "soft1+pipe")


def main():
    rows = K.items()
    byset = {}
    for r in rows:
        byset.setdefault((r["set"], r["arm"]), []).append(r)
    out, flat = {"source": sorted({r["split"] for r in byset.get(("ad1b", "PAF"), [])})}, []
    D = K.Draw(K.frll_persons(), 10000, K.SEED_FRLL)
    for feat in K.FEATS:
        F = K.load_feats(feat, ("ad1b", "f256", "tr"))
        if not any(r["id"] in F for r in byset.get(("ad1b", "PAF"), [])):
            continue
        xm = [r for r in byset[("ad1b", "PAF")] if r["id"] in F]
        d20r = {pathlib.PurePath(r["path"]).stem: r for r in byset[("ad1b", "D20r")] if r["id"] in F}
        d20 = [r for r in byset[("f256", "D20")] if r["id"] in F]
        a256 = [r for r in byset[("f256", "a256")] if r["id"] in F]
        # mixing direction of the training hosts (all hosts), Q1-style share for the mirror step
        hosts = K.training_pool(rows)
        u = np.mean([F[h["x2"]] - F[h["x1"]] for h in hosts], 0)
        u /= np.linalg.norm(u)
        pairs = [(F[r["id"]], F[d20r[pathlib.PurePath(r["path"]).stem]["id"]]) for r in xm if pathlib.PurePath(r["path"]).stem in d20r]
        dm = np.stack([a - b for a, b in pairs])
        mdir = dm.mean(0) / np.linalg.norm(dm.mean(0))
        res = {"n_mirror": len(xm), "n_pairs": len(pairs), "share_along_training_mixing": float(((dm @ u) > 0).mean()),
               "cos_mirror_dir_with_training_mixing": float(mdir @ u), "heads": {}}
        for var in VARIANTS:
            for h in ("H1", "H2"):
                p = K.BIG / "heads" / f"{feat}_{var}_{h}.npz"
                if not p.exists():
                    continue
                z = np.load(p, allow_pickle=False)
                U = z["U"] if z["U"].size else None

                def sc(rr):
                    X = np.stack([F[r["id"]] for r in rr])
                    if U is not None:
                        X = X - (X @ U) @ U.T
                    return ((X - z["mu"]) / z["sd"]) @ z["w"]
                s_m = sc(xm)
                s_r = sc([d20r[pathlib.PurePath(r["path"]).stem] for r in xm if pathlib.PurePath(r["path"]).stem in d20r])
                cell = {}
                for name, neg in (("xm_vs_D20r", [d20r[k] for k in sorted(d20r)]), ("xm_vs_D20_A43", d20), ("xm_vs_photo_a256", a256)):
                    sn = sc(neg)
                    Wp = D.w([K.persons_of(r) for r in xm])
                    Wn = D.w([K.persons_of(r) for r in neg])
                    pt = K.auc(s_m, sn)
                    rep = K.wauc(s_m, sn, Wp, Wn)
                    cell[name] = dict(auc=pt, ci=K.ci(rep), n=[len(xm), len(neg)])
                    flat.append(dict(feature=feat, variant=var, head=h, contrast=name, auc=pt, lo=K.ci(rep)[0], hi=K.ci(rep)[1], n_pos=len(xm), n_neg=len(neg)))
                cell["paired_share_xm_gt_D20r"] = float(np.mean(s_m[:len(s_r)] > s_r)) if len(s_r) == len(s_m) else None
                res["heads"][f"{var}/{h}"] = cell
        out[feat] = res
    K.dump(out, "mirror.json")
    if flat:
        with open(K.OUT / "mirror.csv", "w", newline="") as f:
            w = csv.DictWriter(f, list(flat[0].keys()))
            w.writeheader()
            w.writerows(flat)
    print(json.dumps({k: (v if k == "source" else {kk: vv for kk, vv in v.items() if kk != "heads"}) for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
