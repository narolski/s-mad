"""CN0 (lead's addition 1, registered 11 Nov before any of its numbers): clean-negative test of the image-level class
definition on the AR1 ladder (pool frgcferet).

Image-level head: StandardScaler + L2 logistic regression (C = 1) on mean-pooled frozen patch tokens, R2 (0) vs R4 (1),
trained on one tool and tested on the other, 5 folds by host person (seeded permutation of the 536 hosts).
(a) at the threshold that flags 10% of the test persons' R2 of the test tool (per fold), the rate at which it flags
    the untouched source photos of the test persons (R0) and the FRLL E7 genuine photos (existing 'resmatch' frames,
    every fold's model; opencv + facemorpher frames, and all four families);  repeated with R2w as the negative class.
(b) best single-cue AUC for R2 vs R4 (and R2w vs R4) per tool among the 26 cue_floor statistics
    (smadcvpr/cue_floor.stats, imported unchanged) plus PNG byte size; folded AUC = max(AUC, 1 - AUC).
Verdict (fixed by the lead): the image-level class definition fails if (a) > 20% on either genuine set or any single cue
> 0.80; stands if both rates <= 15% and no cue > 0.65; mixed otherwise.
The same reads (a) for the dense head's mean prediction (no AR1 training; same folds and thresholds rule).
  python3 -I cn0.py cues --workers 4        (cue matrix, cached)
  python3 -I cn0.py read --backbones clip224,clip336,dinov3_512 --dense-tag full
"""
import argparse
import collections
import json
import os
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402

TOOLS = ("facemorpher", "opencv")


def ar1_rows():
    return [r for r in L.rows("ar1") if r["cell"] == "frgcferet"]


def _cue(p):
    import cue_floor as CF
    import cv2
    rgb = cv2.imread(p)[:, :, ::-1]
    return CF.stats(rgb)


def cues(a):
    os.environ["OMP_NUM_THREADS"] = "1"
    sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")
    R = [r for r in ar1_rows() if r["rung"] in ("R2", "R2w", "R4")]
    from multiprocessing import Pool
    with Pool(a.workers) as p:
        C = np.stack(p.map(_cue, [r["path"] for r in R], chunksize=8))
    size = np.array([os.path.getsize(r["path"]) for r in R], float)
    import cue_floor as CF
    np.savez(L.OUT / "cn0_cues.npz", ids=np.array([r["id"] for r in R]), cues=C, png_bytes=size,
             names=np.array(list(CF.NAMES)))
    print(C.shape)


def pooled(bb, name, n=None):
    tok, ids, done = L.load_tokens(bb, name)
    n = done if n is None else n
    out = np.concatenate([np.asarray(tok[s:min(s + 64, n)]).astype(np.float32).mean(1) for s in range(0, n, 64)])
    return dict(zip(ids[:n], out))


def read(a):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    R = ar1_rows()
    hosts = sorted({r["p1"] for r in R})
    perm = np.random.default_rng(401).permutation(len(hosts))
    fold = {hosts[i]: k % 5 for k, i in enumerate(perm)}
    by = collections.defaultdict(dict)        # (tool, rung) -> {host: id}
    for r in R:
        by[(r["tool"], r["rung"])][r["p1"]] = r["id"]
    B = [r for r in L.rows("bench_s") if r["cell"].startswith("frllm_") and r["rung"] == "e7"]
    res = {}
    # ---- (b) single cues
    z = np.load(L.OUT / "cues" / "ar1.npz")          # cues_all.py: 26 cue_floor statistics + PNG bytes
    cidx = {i: k for k, i in enumerate(z["ids"])}
    feats = z["cues"]
    names = list(z["names"])
    cue = {}
    for tool in TOOLS:
        for neg in ("R2", "R2w"):
            pos_i = [cidx[i] for i in by[(tool, "R4")].values()]
            neg_i = [cidx[i] for i in by[(tool, neg)].values()]
            aucs = {}
            for j, nm in enumerate(names):
                x = feats[:, j]
                if not np.isfinite(x[pos_i + neg_i]).all() or np.ptp(x[pos_i + neg_i]) == 0:
                    aucs[nm] = 0.5
                    continue
                au = L.stats().auc(x[pos_i], x[neg_i])
                aucs[nm] = max(au, 1 - au)
            best = max(aucs, key=aucs.get)
            cue[f"{tool}_{neg}vsR4"] = dict(best=best, best_folded_auc=round(aucs[best], 4),
                                            top5={k: round(v, 4) for k, v in sorted(aucs.items(), key=lambda kv: -kv[1])[:5]})
    res["cues"] = cue
    # ---- (a) image-level heads
    for bb in a.backbones.split(","):
        P = pooled(bb, "ar1")
        PB = pooled(bb, "bench_s") if (L.OUT / "feat" / bb / "bench_s.done").exists() else {}
        e7_ids = [r["id"] for r in B if r["id"] in PB]
        e7_lm = [r["id"] for r in B if r["id"] in PB and r["tool"] in TOOLS]
        out = {}
        for tr_tool, te_tool in ((TOOLS[0], TOOLS[1]), (TOOLS[1], TOOLS[0])):
            for neg in ("R2", "R2w"):
                oof = collections.defaultdict(list)
                rates = collections.defaultdict(list)
                for k in range(5):
                    trh = [h for h in hosts if fold[h] != k]
                    teh = [h for h in hosts if fold[h] == k]
                    Xn = [P[by[(tr_tool, neg)][h]] for h in trh if by[(tr_tool, neg)].get(h) in P]
                    Xp = [P[by[(tr_tool, "R4")][h]] for h in trh if by[(tr_tool, "R4")].get(h) in P]
                    X = np.stack(Xn + Xp)
                    y = np.r_[np.zeros(len(Xn)), np.ones(len(Xp))]
                    sc = StandardScaler().fit(X)
                    clf = LogisticRegression(C=1.0, max_iter=5000).fit(sc.transform(X), y)
                    f = lambda ids: clf.decision_function(sc.transform(np.stack([P[i] for i in ids]))) if ids else np.array([])  # noqa
                    tn = [by[(te_tool, neg)][h] for h in teh if by[(te_tool, neg)].get(h) in P]
                    tp = [by[(te_tool, "R4")][h] for h in teh if by[(te_tool, "R4")].get(h) in P]
                    t0 = [by[("none", "R0")][h] for h in teh if by[("none", "R0")].get(h) in P]
                    sn, sp, s0 = f(tn), f(tp), f(t0)
                    thr = np.quantile(sn, 0.9)
                    oof["neg"] += list(sn)
                    oof["pos"] += list(sp)
                    rates["R0_flag"].append((int((s0 >= thr).sum()), len(s0)))
                    if e7_ids:
                        se = clf.decision_function(sc.transform(np.stack([PB[i] for i in e7_ids])))
                        sl = clf.decision_function(sc.transform(np.stack([PB[i] for i in e7_lm])))
                        rates["E7all_flag"].append(float((se >= thr).mean()))
                        rates["E7lm_flag"].append(float((sl >= thr).mean()))
                auc = L.stats().auc(oof["pos"], oof["neg"])
                r0 = sum(x for x, _ in rates["R0_flag"]) / max(1, sum(n for _, n in rates["R0_flag"]))
                out[f"train_{tr_tool}_test_{te_tool}_{neg}"] = dict(
                    oof_auc_R4_vs_neg=round(auc, 4), R0_flag_rate=round(r0, 4),
                    E7_lm_flag_rate=round(float(np.mean(rates["E7lm_flag"])), 4) if rates["E7lm_flag"] else None,
                    E7_all_flag_rate=round(float(np.mean(rates["E7all_flag"])), 4) if rates["E7all_flag"] else None,
                    n_E7=[len(e7_lm), len(e7_ids)])
        res[f"logreg_{bb}"] = out
    # ---- (a) for the dense heads (mean prediction, trained on AF0 only)
    if a.dense_tag:
        for bb in a.backbones.split(","):
            d = L.OUT / "heads" / bb / a.dense_tag
            for p in sorted(d.glob("pred_*_ar1.npz")):
                head = p.name[5:-8]
                if head == "logreg":
                    continue
                z = np.load(p)
                S = dict(zip(z["ids"], z["score"]))
                pb = d / f"pred_{head}_bench_s.npz"
                SB = dict(zip(np.load(pb)["ids"], np.load(pb)["score"])) if pb.exists() else {}
                out = {}
                for te_tool in TOOLS:
                    for neg in ("R2", "R2w"):
                        r0n, r0d, e7l, e7a = 0, 0, [], []
                        for k in range(5):
                            teh = [h for h in hosts if fold[h] == k]
                            sn = np.array([S[by[(te_tool, neg)][h]] for h in teh if by[(te_tool, neg)].get(h) in S])
                            s0 = np.array([S[by[("none", "R0")][h]] for h in teh if by[("none", "R0")].get(h) in S])
                            thr = np.quantile(sn, 0.9)
                            r0n += int((s0 >= thr).sum())
                            r0d += len(s0)
                            if SB:
                                e7l.append(float(np.mean([SB[r["id"]] >= thr for r in B if r["tool"] in TOOLS])))
                                e7a.append(float(np.mean([SB[r["id"]] >= thr for r in B])))
                        out[f"test_{te_tool}_{neg}"] = dict(R0_flag_rate=round(r0n / max(r0d, 1), 4),
                                                            E7_lm_flag_rate=round(float(np.mean(e7l)), 4) if e7l else None,
                                                            E7_all_flag_rate=round(float(np.mean(e7a)), 4) if e7a else None)
                res[f"dense_{bb}_{head}"] = out
    # ---- verdict per image-level line
    for key, v in list(res.items()):
        if not key.startswith("logreg_"):
            continue
        worst_rate = max(max(x["R0_flag_rate"], x["E7_lm_flag_rate"] or 0) for x in v.values())
        worst_cue = max(c["best_folded_auc"] for c in res["cues"].values())
        verdict = "fails" if (worst_rate > 0.20 or worst_cue > 0.80) else (
            "stands" if (worst_rate <= 0.15 and worst_cue <= 0.65) else "mixed")
        res[key + "_verdict"] = dict(worst_flag_rate=worst_rate, worst_cue_auc=worst_cue, verdict=verdict)
    json.dump(res, open(L.RES / "cn0.json", "w"), indent=1)
    print(json.dumps(res, indent=1)[:6000])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("cues", "read"))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--backbones", default="clip224")
    ap.add_argument("--dense-tag", default=None)
    a = ap.parse_args()
    cues(a) if a.cmd == "cues" else read(a)
