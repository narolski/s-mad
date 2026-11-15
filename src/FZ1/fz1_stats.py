"""FZ1 P4: simple-statistic floors for B vs D and B20 vs D20 (A43).

Statistics per image: high-frequency energy share (luma FFT power above half Nyquist), Laplacian variance (cv2, ksize 1,
luma), mean |image - mirror| (RGB), per-channel std (R, G, B), PNG size (bytes of the stored A43 file). Views: the 224
loader input (common.ImageItems(res=224), primary) and the central 256 x 256 of the 512 frame (descriptive, border-free).
AUC of each alone (oriented by its point estimate = folded; marked), logistic on all seven with the P2 probe routine and
folds (seed 401), paired bootstrap difference against the P2 CLIP-L/14 (MADation input) probe.
Run: OMP_NUM_THREADS=1 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/FZ1/fz1_stats.py [--smoke]
"""
import json, os, pathlib, sys
import numpy as np
import cv2
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")
import fz1_common as K
import fz1_probe as PR
from common import ImageItems  # noqa: E402

NAMES = ("hf_energy", "laplacian_var", "mirror_mad", "std_R", "std_G", "std_B", "png_bytes")
CONTRASTS = (("B", "D"), ("B20", "D20"))


def stats(img, png):
    I = img.astype(np.float64)
    Y = 0.299 * I[..., 0] + 0.587 * I[..., 1] + 0.114 * I[..., 2]
    Yc = Y - Y.mean()
    P = np.abs(np.fft.fft2(Yc)) ** 2
    fy, fx = np.meshgrid(np.fft.fftfreq(Y.shape[0]), np.fft.fftfreq(Y.shape[1]), indexing="ij")
    hf = float(P[np.sqrt(fx ** 2 + fy ** 2) > 0.25].sum() / max(P.sum(), 1e-12))
    lap = float(cv2.Laplacian(Y, cv2.CV_64F, ksize=1).var())
    mir = float(np.abs(I - I[:, ::-1]).mean())
    sd = I.reshape(-1, 3).std(0)
    return [hf, lap, mir, float(sd[0]), float(sd[1]), float(sd[2]), float(png)]


def main():
    smoke = "--smoke" in sys.argv
    rows = K.a43_rows()
    g = K.a43_groups(rows)
    arms = ("B", "D", "B20", "D20")
    ii = [i for a in arms for i in (g[a][:30] if smoke else g[a])]
    png = {}
    for i in ii:
        r = rows[i]
        sz = os.path.getsize(K.A43_ROOT / r["stored_path"])
        assert sz == int(r["file_bytes"]), (r["id"], sz, r["file_bytes"])
        png[i] = sz
    ds224 = ImageItems([(str(K.a43_path(rows[i])), 0) for i in ii], res=224, root="/")
    ds512 = ImageItems([(str(K.a43_path(rows[i])), 0) for i in ii], res=512, root="/")
    S = {"view224": {}, "center256": {}}
    for k, i in enumerate(ii):
        x224 = (ds224[k][0].permute(1, 2, 0).numpy() * 255.0)
        x512 = (ds512[k][0].permute(1, 2, 0).numpy() * 255.0)[128:384, 128:384]
        S["view224"][i] = stats(x224, png[i])
        S["center256"][i] = stats(x512, png[i])
    allp = sorted({p for r in rows for p in K.pers_a43(r)})
    D = K.Draw(allp, 200 if smoke else 10000, K.SEED_A43)
    preps = None if smoke else np.load(K.BIG / "probe_reps_a43.npz")
    pjson = None if smoke else json.load(open(K.OUT / "p2_probe.json"))
    out = {}
    for view in S:
        for a, b in CONTRASTS:
            ia = g[a][:30] if smoke else g[a]
            ib = g[b][:30] if smoke else g[b]
            Xa = np.array([S[view][i] for i in ia])
            Xb = np.array([S[view][i] for i in ib])
            P = [K.pers_a43(rows[i]) for i in ia + ib]
            w = D.w(P)
            wa, wb = w[:, :len(ia)], w[:, len(ia):]
            key = f"clip_mad__{a}_vs_{b}"
            pr = None if smoke else preps[key]
            res = {}
            for j, nm in enumerate(NAMES):
                raw = K.auc(Xa[:, j], Xb[:, j])
                rep = K.wauc(Xa[:, j], Xb[:, j], wa, wb)
                flip = raw < 0.5
                fa, frep = (1 - raw, 1 - rep) if flip else (raw, rep)
                d = {"auc_raw": raw, "auc_folded": fa, "ci_folded": K.ci(frep), "direction": "morph lower" if flip else "morph higher",
                     "mean_morph": float(Xa[:, j].mean()), "mean_recon": float(Xb[:, j].mean())}
                if pr is not None:
                    diff = pr - frep
                    d["probe_minus_stat"] = {"point": pjson[f"clip_mad|{a} vs {b}"]["auc"] - fa, "ci": K.ci(diff)}
                    d["matches_probe"] = bool(K.ci(diff)[0] <= 0)
                res[nm] = d
            X = np.r_[Xa, Xb]
            y = np.r_[np.ones(len(ia)), np.zeros(len(ib))].astype(int)
            oof, cs = PR.cv_a43(X, y, P, 401)
            rep = K.wauc(oof[y == 1], oof[y == 0], wa, wb)
            lg = {"auc": K.auc(oof[y == 1], oof[y == 0]), "ci": K.ci(rep), "Cs": cs}
            if pr is not None:
                lg["probe_minus_logistic"] = {"point": pjson[f"clip_mad|{a} vs {b}"]["auc"] - lg["auc"], "ci": K.ci(pr - rep)}
                lg["matches_probe"] = bool(K.ci(pr - rep)[0] <= 0)
            res["logistic_all7"] = lg
            out[f"{view}|{a} vs {b}"] = res
            print(f"== {view} {a} vs {b}: logistic all7 {lg['auc']:.3f} [{lg['ci'][0]:.3f}, {lg['ci'][1]:.3f}]"
                  + (f" probe-minus {lg['probe_minus_logistic']['point']:+.3f} {np.round(lg['probe_minus_logistic']['ci'], 3)}" if pr is not None else ""))
            for nm in NAMES:
                d = res[nm]
                print(f"   {nm:14s} folded {d['auc_folded']:.3f} [{d['ci_folded'][0]:.3f}, {d['ci_folded'][1]:.3f}] ({d['direction']})"
                      + (f" matches probe: {d['matches_probe']}" if pr is not None else ""))
    if not smoke:
        json.dump(out, open(K.OUT / "p4_stats.json", "w"), indent=1)
        np.savez(K.BIG / "p4_stats_values.npz", ids=np.array([rows[i]["id"] for i in ii]),
                 view224=np.array([S["view224"][i] for i in ii]), center256=np.array([S["center256"][i] for i in ii]))


if __name__ == "__main__":
    main()
