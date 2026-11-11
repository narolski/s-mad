"""PN1 amendment 9: bracketing test for every frozen head, DiffAE set-B transfer, spliced-arm seed spread.
  python3 -I bracket.py   -> experiments/PN1_.../bracket/bracket.json, summary printed
Heads are refitted exactly as splice.py (same rows, balance, seeds; deterministic) and scored on the new images."""
import csv
import os
import pathlib
import sys

os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402
import splice as SP  # noqa: E402
import tier0 as T0  # noqa: E402
import cert as CE  # noqa: E402

B = 2000


def share_ci(win, units):
    """win: bool per host; bootstrap over units (partner cycles)."""
    w, u = K.boot_weights(units, B, 20261111)
    ui = {x: i for i, x in enumerate(u)}
    W = w[:, [ui[x] for x in units]]
    d = (W * win[None, :]).sum(1) / W.sum(1)
    return dict(share=float(win.mean()), lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)), n=int(len(win)))


def bracket(S, P, neg1, neg2="T_R2w_opencv_61", pos="T_R4_opencv"):
    a = {r["host"]: S[r["id"]] for r in P[pos]}
    b = {r["host"]: S[r["id"]] for r in P[neg1]}
    c = {r["host"]: S[r["id"]] for r in P[neg2]}
    hs = sorted(set(a) & set(b) & set(c))
    win = np.array([a[h] > b[h] and a[h] > c[h] for h in hs])
    return share_ci(win, [RD.cyc(h) for h in hs]), hs


def main():
    cat = K.catalog()
    cat += T0.soft_cat_rows({r["id"] for r in cat})
    sp = SP.splice_rows()
    sets = T0.train_sets(cat)
    trS4 = [r for r in sp if r["rung"] == "S4" and r["tool"] == "opencv" and r["role"] == "train" and r["train_morph"] == "1"]
    trS0 = [r for r in sp if r["rung"] == "S0" and r["tool"] == "opencv" and r["role"] == "train"]
    trS3 = [r for r in sp if r["rung"] == "S3" and r["tool"] == "opencv" and r["role"] == "train"]
    arms = {"A0": sets["A0"], "B0": sets["B0"], "Bn0": sets["Bn0"], "S-a": trS4 + trS0, "S-b": sets["B0"] + trS4 + trS0 + trS3}
    # cues for the floor: 27 (512) + 12 (224)
    cues, names = {}, None
    for f in [K.AF0 / "cues" / "ar1.npz"] + sorted((K.PN1 / "cues").glob("*.npz")):
        if f.name.startswith(("cert_", "ratio_")) or "_limit" in f.name:
            continue
        z = np.load(f)
        names = [str(n) for n in z["names"]]
        cues.update({str(i): c for i, c in zip(z["ids"], z["cues"])})
    c224 = CE.load_cues("c224")
    cues = {i: np.r_[v, c224[i]] for i, v in cues.items() if i in c224}
    names = names + [n + "@224" for n in CE.PIX]
    dg = list(csv.DictReader(open(K.PN1 / "lists" / "dg1_test.csv")))
    zc = np.load(K.PN1 / "cues" / "cert_dg1_test.npz")
    dgc = {str(i): np.r_[a, b] for i, a, b in zip(zc["ids"], zc["c224"], zc["c512"])}
    dpool = {}
    for r in dg:
        dpool.setdefault(r["rung"], []).append(r)
    out = {}
    # statistic floors (head-independent): bracketing and DiffAE
    idx0, _, _ = K.load_features("clip224")
    P0 = RD.pools([r for r in cat if r["id"] in idx0])
    floors = {}
    for neg1 in ("T_R2w_opencv", "T_R2w4_opencv"):
        best = (-1, None, None)
        for j, n in enumerate(names):
            Sx = {i: v[j] for i, v in cues.items()}
            if not all(r["id"] in Sx for p in ("T_R4_opencv", neg1, "T_R2w_opencv_61") for r in P0[p]):
                continue
            sgn = 1 if RD.paired(Sx, P0, "T_R4_opencv", neg1).get("auc", 0.5) >= 0.5 else -1
            S2 = {i: sgn * v for i, v in Sx.items()}
            res, _ = bracket(S2, P0, neg1)
            if res["share"] > best[0]:
                best = (res["share"], n, res)
        floors[f"bracket_floor_{neg1}"] = dict(stat=best[1], **best[2])
    for neg in ("REC", "G", "SAME", "MIR"):
        sp_, sn_ = dpool["X"], dpool[neg]
        bs = max((max(K.auc([dgc[r["id"]][j] for r in sp_], [dgc[r["id"]][j] for r in sn_]),
                      1 - K.auc([dgc[r["id"]][j] for r in sp_], [dgc[r["id"]][j] for r in sn_])), j) for j in range(24))
        floors[f"dg1_X_vs_{neg}_floor"] = dict(auc=bs[0], cue=(CE.PIX + [n + "@256" for n in CE.PIX])[bs[1]])
    out["floors"] = floors
    for bb in ("clip224", "dinov3_512"):
        idx, X, _ = K.load_features(bb)
        P = RD.pools([r for r in cat if r["id"] in idx])
        for arm, rows in arms.items():
            rows = [r for r in rows if r["id"] in idx]
            rows, _ = T0.balance_rows(rows)
            y = np.array([1 if r["klass"] == "attack" else 0 for r in rows])
            Xtr = X[[idx[r["id"]] for r in rows]]
            for seed in (401, 402, 403, 404, 405):
                h = K.fit_head(Xtr, y, [r["persons"] for r in rows], seed)
                ids = list(idx)
                S = dict(zip(ids, K.head_score(h, X[[idx[i] for i in ids]]).tolist()))
                res = {"C": h["C"]}
                for neg1 in ("T_R2w_opencv", "T_R2w4_opencv"):
                    res[f"bracket_{neg1}"], _ = bracket(S, P, neg1)
                for neg in ("REC", "G", "SAME", "MIR"):
                    if all(r["id"] in idx for r in dpool["X"] + dpool[neg]):
                        res[f"dg1_X_vs_{neg}"] = K.unpaired_auc_ci(RD.scores_of(S, dpool["X"]), RD.scores_of(S, dpool[neg]))["auc"]
                if arm.startswith("S"):
                    Psp = dict(P)
                    for r in sp:
                        if r["role"] == "test" and r["tool"] == "opencv" and r["id"] in idx:
                            Psp.setdefault("T_" + r["rung"], []).append(r)
                    for k, (p1, p2) in {"S0_vs_S4": ("T_S4", "T_S0"), "face_only": ("T_S4_bg", "T_S0_bg"),
                                        "R2w_vs_R4_face_blanked": ("T_R4_face", "T_R2w_face")}.items():
                        x = RD.paired(S, Psp, p1, p2)
                        res[k] = (round(x["auc"], 4), round(x["lo"], 4), round(x["hi"], 4))
                out[f"{bb}_{arm}_s{seed}"] = res
                print("DONE", bb, arm, seed, flush=True)
    d = K.RES / "bracket"
    d.mkdir(parents=True, exist_ok=True)
    K.dump(out, d / "bracket.json")


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
