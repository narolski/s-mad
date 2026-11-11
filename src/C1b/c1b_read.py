"""C1b: is the FRLL expression imbalance used by detectors?  Zero GPU; existing per-image eval scores only.

(a) within-person neutral-above-smiling AUC (102 FRLL persons, person bootstrap B = 10,000);
(b) per cell EER and BPCER@APCER 5 / 10 % with genuine = all / neutral-only / smiling-only, paired differences with the
    two-way (pigeonhole) person bootstrap of AD1 (first 2,000 rows of the same draw);
(c) rank tables for the imbalanced cells.
Corrected-MAD22 cells are left out (no scores exist); the eval.csv mad22 rows (old subset) are never read.
Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/C1b/c1b_read.py [--smoke]
"""
import csv, hashlib, json, pathlib, re, sys
from multiprocessing import Pool
import numpy as np
from scipy.stats import binomtest, kendalltau

sys.path.insert(0, "/home/narolski/smad-next/src/AD1")
from ad1_read import wauc  # noqa: E402  (weighted Mann-Whitney AUC, verbatim from a36_read)

MC = pathlib.Path("/home/narolski/mambamorph-code")
S = MC / "smadcvpr_runs/A12_scored"
EVAL = MC / "smadcvpr_data/manifests/eval.csv"
EVAL_SHA = "86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9"
NETS = MC / "experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv"
OUT = pathlib.Path("/home/narolski/smad-next/experiments/C1b")
BIG = pathlib.Path("/mnt/t7/smad_next/C1b")
SMOKE = "--smoke" in sys.argv
SEED = 20261111
BA, BB = (50, 50) if SMOKE else (10000, 2000)

FRLLM = ("amsl", "facemorpher", "opencv", "stylegan", "webmorph")
DIM = ("dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s")
IMBAL = [f"frllm/{f}" for f in FRLLM] + [f"dim/{f}" for f in DIM]


def pers(name):
    """(persons), (expressions) from an eval file name."""
    n = pathlib.PurePath(name).name
    m = re.match(r"^morph_(\d{3})_(\d{2})_and_(\d{3})_(\d{2})_", n)
    if m:
        return (m.group(1), m.group(3)), (m.group(2), m.group(4))
    m = re.match(r"^(\d{3})_(\d{3})_orig", n)
    if m:
        return (m.group(1), m.group(2)), (None, None)
    m = re.match(r"^(\d{3})_(\d{2})_orig", n)
    if m:
        return (m.group(1),), (m.group(2),)
    raise ValueError(n)


def cells():
    assert hashlib.sha256(EVAL.read_bytes()).hexdigest() == EVAL_SHA
    rows = [r for r in csv.DictReader(open(EVAL)) if r["variant"] == "orig" and r["set"] in ("frllm", "dim", "mordiff")]
    C = {}
    for st, fams, bf in (("frllm", FRLLM, "frll_bona"), ("dim", DIM, "dim_bona"), ("mordiff", ("mordiff",), "mordiff_bona")):
        b = [r for r in rows if r["set"] == st and r["family"] == bf and r["label"] == "0"]
        for f in fams:
            C[f"{st}/{f}"] = ([r for r in rows if r["set"] == st and r["family"] == f and r["label"] == "1"], b)
    if SMOKE:
        C = {k: C[k] for k in ("frllm/amsl", "mordiff/mordiff")}
    return C


def detectors():
    """(row label, group, file, key, checkpoint)"""
    rel = [("MADation ViT-B/16 release", "rel-clip", "A12REL/madation_vitb16"), ("MADation ViT-L/14 release", "rel-clip", "A12REL/madation_vitl14"),
           ("MADation FE ViT-B/16 release", "rel-clip", "A12REL/madation_fe_vitb16"), ("MADation FE ViT-L/14 release", "rel-clip", "A12REL/madation_fe_vitl14"),
           ("MADation FS ViT-B/16 release", "rel-clip", "A12REL/madation_fs_vitb16"), ("MADation FS ViT-L/14 release", "rel-clip", "A12REL/madation_fs_vitl14"),
           ("SelfMAD release, our pipeline (desc.)", "rel-selfmad", "A12REL/selfmad_hrnet_w18"),
           ("MixFaceNet-MAD release, our frames (desc.)", "rel-cnn", "A12REL/mixfacenet_mad_smdd")]
    D = [(lab, g, S / d / "scores_eval.npz", "score_noTTA", "release") for lab, g, d in rel]
    D.insert(6, ("SelfMAD release, own preprocessing", "rel-selfmad", MC / "experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz", "score", "release"))
    for ln in open(NETS):
        if ln.startswith("#") or not ln.strip():
            continue
        run, ck, _s, grp, method, arm, seed = ln.rstrip("\n").split("\t")
        if grp != "primary":
            continue
        name = run.rsplit("/", 1)[1]
        rid = method.split()[0]
        g = "rec-clip" if rid in ("M3", "M3L") else "rec-cnn"
        for c in ("es", "last"):
            D.append((f"{rid} s{seed} {c}", g, S / "A12BR" / name / f"scores_eval_{c}.npz", "score", c))
    if SMOKE:
        D = [d for d in D if d[0].startswith(("MADation ViT-L/14 release", "M3 s1 last"))]
    return D


class Draw:
    """Pigeonhole person draw (as AD1 / a41_read): counts ~ Multinomial(n, 1/n); photo weight = count of its person,
    morph weight = product of its contributors' counts."""

    def __init__(self, per, B, seed):
        self.per = sorted(per)
        self.pos = {p: i for i, p in enumerate(self.per)}
        n = len(self.per)
        self.C = np.random.default_rng(seed).multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64)

    def w(self, pp, B=None):
        C = self.C if B is None else self.C[:B]
        a = np.array([self.pos[p[0]] for p in pp])
        b = np.array([self.pos[p[-1]] for p in pp])
        w = C[:, a] * C[:, b]
        same = a == b
        w[:, same] = C[:, a[same]]
        return w


def err_rates(b, m, wb, wm):
    """weighted EER (%), BPCER@APCER 5 % and 10 % (%) for each weight row; flag = score >= t."""
    T = np.unique(np.r_[b, m])
    ob, om = np.argsort(b, kind="stable"), np.argsort(m, kind="stable")
    bs, ms = b[ob], m[om]
    Cb = np.concatenate([np.zeros((wb.shape[0], 1)), np.cumsum(wb[:, ob], 1)], 1)
    Cm = np.concatenate([np.zeros((wm.shape[0], 1)), np.cumsum(wm[:, om], 1)], 1)
    Wb, Wm = Cb[:, -1:], Cm[:, -1:]
    fpr = 1 - Cb[:, np.searchsorted(bs, T, "left")] / Wb      # genuine with score >= t
    fnr = Cm[:, np.searchsorted(ms, T, "left")] / Wm          # morphs with score < t
    i = np.argmin(np.abs(fpr - fnr), 1)
    r = np.arange(len(i))
    eer = 100 * (fpr[r, i] + fnr[r, i]) / 2
    out = [eer]
    ap = Cm[:, np.searchsorted(ms, ms, "left")] / Wm          # APCER at t = each morph score
    for a in (0.05, 0.10):
        k = np.maximum((ap <= a + 1e-12).sum(1) - 1, 0)
        t = ms[k]
        out.append(100 * (1 - Cb[r, np.searchsorted(bs, t, "left")] / Wb[:, 0]))
    return out


def q(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


G = {}


def init(g):
    G.update(g)


def run_detector(det):
    lab, grp, f, key, ck = det
    z = np.load(f, allow_pickle=False)
    if "manifest_sha256" in z.files and "selfmad_own" not in str(f):
        assert str(z["manifest_sha256"]) == EVAL_SHA, f
    sc = dict(zip(z["id"].tolist(), z[key].astype(np.float64)))
    D, C = G["D"], G["C"]
    res = {"label": lab, "group": grp, "ckpt": ck, "file": str(f), "key": key, "a": {}, "b": {}}
    reps = {}
    # (a) within-person AUC on the two genuine frame sets
    for gs, cell in (("frll_bona", next(k for k in C if not k.startswith("mordiff"))), ("mordiff_bona", "mordiff/mordiff")):
        if cell not in C:
            continue
        br = C[cell][1]
        pn = {pers(r["path"])[0][0]: sc[r["id"]] for r in br if pers(r["path"])[1][0] == "03"}
        ps = {pers(r["path"])[0][0]: sc[r["id"]] for r in br if pers(r["path"])[1][0] == "08"}
        P = sorted(set(pn) & set(ps))
        ind = np.array([1.0 if pn[p] > ps[p] else 0.5 if pn[p] == ps[p] else 0.0 for p in P])
        cnt = D.C[:, [D.pos[p] for p in P]]
        rep = (cnt * ind).sum(1) / cnt.sum(1)
        sn, ss = np.array([pn[p] for p in P]), np.array([ps[p] for p in P])
        pooled = float(wauc(sn, ss, np.ones((1, len(sn))), np.ones((1, len(ss))))[0])
        rep_pool = wauc(sn, ss, cnt, cnt)
        k = int((ind == 1).sum()); n = int((ind != 0.5).sum())
        res["a"][gs] = {"n_persons": len(P), "auc_wp": float(ind.mean()), "ci": q(rep), "n_neutral_above": k, "n_ties": int((ind == 0.5).sum()),
                        "sign_p": float(binomtest(k, n, 0.5).pvalue) if n else None, "auc_pooled": pooled, "ci_pooled": q(rep_pool),
                        "mean_diff_neu_minus_smi": float((sn - ss).mean())}
    # (b) error rates per cell
    for cn, (mr, br) in C.items():
        sm = np.array([sc[r["id"]] for r in mr]); sb = np.array([sc[r["id"]] for r in br])
        ex = np.array([pers(r["path"])[1][0] for r in br])
        wm, wb = G["wm"][cn], G["wb"][cn]
        o = {}
        for gn, sel in (("all", np.ones(len(sb), bool)), ("neu", ex == "03"), ("smi", ex == "08")):
            pt = err_rates(sb[sel], sm, np.ones((1, sel.sum())), np.ones((1, len(sm))))
            bt = err_rates(sb[sel], sm, wb[:, sel], wm)
            o[gn] = {"eer": float(pt[0][0]), "bpcer5": float(pt[1][0]), "bpcer10": float(pt[2][0]),
                     "auc": float(wauc(sm, sb[sel], np.ones((1, len(sm))), np.ones((1, sel.sum())))[0])}
            reps[(cn, gn)] = bt
        for gn in ("neu", "smi"):
            for j, mname in enumerate(("eer", "bpcer5", "bpcer10")):
                d = reps[(cn, gn)][j] - reps[(cn, "all")][j]
                o[f"{gn}-all_{mname}"] = [o[gn][mname] - o["all"][mname]] + q(d)
        if cn == "mordiff/mordiff":
            exm = np.array([pers(r["path"])[1][0] for r in mr])
            o["2x2_auc"] = {f"M{a}/G{g}": float(wauc(sm[exm == a], sb[ex == g], np.ones((1, (exm == a).sum())), np.ones((1, (ex == g).sum())))[0])
                            for a in ("03", "08") for g in ("03", "08")}
        res["b"][cn] = o
    eer_reps = {f"{cn}|{gn}": reps[(cn, gn)][0].astype(np.float32) for cn in C for gn in ("all", "neu", "smi")}
    print(lab, json.dumps({k: [round(v["auc_wp"], 3)] + [round(x, 3) for x in v["ci"]] for k, v in res["a"].items()}), flush=True)
    return res, eer_reps


def main():
    C = cells()
    allp = sorted({p for m, b in C.values() for r in m + b for p in pers(r["path"])[0]})
    genp = sorted({pers(r["path"])[0][0] for m, b in C.values() for r in b})
    assert set(allp) == set(genp) and len(genp) == (102 if not SMOKE else len(genp)), (len(allp), len(genp))
    D = Draw(allp, BA, SEED)
    wm = {cn: D.w([pers(r["path"])[0] for r in mr], BB) for cn, (mr, br) in C.items()}
    wb = {cn: D.w([pers(r["path"])[0] for r in br], BB) for cn, (mr, br) in C.items()}
    dets = detectors()
    print(len(C), "cells;", len(dets), "detectors;", len(allp), "persons; B", BA, BB, flush=True)
    for d in dets:
        assert d[2].exists(), d
    with Pool(1 if SMOKE else 8, initializer=init, initargs=({"D": D, "C": C, "wm": wm, "wb": wb},)) as pool:
        R = pool.map(run_detector, dets, chunksize=1)
    res = [r for r, _ in R]
    reps = {r["label"]: e for r, e in R}
    # (c) rank tables on the imbalanced cells: releases + recipe-checkpoint seed means
    rows = {}
    for r in res:
        if r["ckpt"] == "release":
            rows[r["label"]] = [r]
        else:
            rows.setdefault(f"{r['label'].split()[0]} {r['ckpt']} (seed mean)", []).append(r)
    ranks = {}
    for cn in [c for c in IMBAL if c in C]:
        tab = {}
        for rn, L in rows.items():
            tab[rn] = {gn: float(np.mean([x["b"][cn][gn]["eer"] for x in L])) for gn in ("all", "neu")}
        names = list(tab)
        ra = {n: i + 1 for i, n in enumerate(sorted(names, key=lambda n: tab[n]["all"]))}
        rn_ = {n: i + 1 for i, n in enumerate(sorted(names, key=lambda n: tab[n]["neu"]))}
        flips = []
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if np.sign(tab[a]["all"] - tab[b]["all"]) * np.sign(tab[a]["neu"] - tab[b]["neu"]) < 0:
                    fl = {"pair": [a, b], "gap_all": tab[a]["all"] - tab[b]["all"], "gap_neu": tab[a]["neu"] - tab[b]["neu"]}
                    if len(rows[a]) == 1 and len(rows[b]) == 1:
                        ga = reps[a][f"{cn}|all"] - reps[b][f"{cn}|all"]
                        gn = reps[a][f"{cn}|neu"] - reps[b][f"{cn}|neu"]
                        ca, cn2, cd = q(ga), q(gn), q(gn - ga)
                        fl.update(ci_gap_all=ca, ci_gap_neu=cn2, ci_change=cd,
                                  beyond_noise=bool((ca[0] > 0 and cn2[1] < 0) or (ca[1] < 0 and cn2[0] > 0)))
                    flips.append(fl)
        tau = kendalltau([tab[n]["all"] for n in names], [tab[n]["neu"] for n in names]).statistic
        ranks[cn] = {"table": {n: {**tab[n], "rank_all": ra[n], "rank_neu": rn_[n]} for n in names}, "kendall_tau": float(tau),
                     "moved": {n: [ra[n], rn_[n]] for n in names if ra[n] != rn_[n]}, "flips": flips}
    out = {"B_a": BA, "B_b": BB, "seed": SEED, "cells": list(C), "n": {cn: [len(m), len(b)] for cn, (m, b) in C.items()},
           "mad22": "left out: no score exists on the corrected MAD22; eval.csv mad22 rows (old subset) not read",
           "detectors": res, "ranks": ranks}
    if SMOKE:
        print(json.dumps(out["detectors"][0]["b"], indent=0)[:3000])
        print("smoke ok")
        return
    json.dump(out, open(OUT / "c1b_read.json", "w"), indent=1)
    BIG.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(BIG / "c1b_eer_bootstrap_reps.npz", **{f"{lab}||{k}": v for lab, e in reps.items() for k, v in e.items()})
    with open(OUT / "c1b_within_person.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["detector", "group", "ckpt", "frames", "auc_wp", "lo", "hi", "n_neutral_above", "n_ties", "sign_p", "auc_pooled", "pooled_lo", "pooled_hi"])
        for r in res:
            for gs, a in r["a"].items():
                w.writerow([r["label"], r["group"], r["ckpt"], gs, f"{a['auc_wp']:.4f}", f"{a['ci'][0]:.4f}", f"{a['ci'][1]:.4f}", a["n_neutral_above"], a["n_ties"],
                            f"{a['sign_p']:.2e}", f"{a['auc_pooled']:.4f}", f"{a['ci_pooled'][0]:.4f}", f"{a['ci_pooled'][1]:.4f}"])
    with open(OUT / "c1b_cells.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        hdr = ["detector", "group", "ckpt", "cell"] + [f"{m}_{g}" for g in ("all", "neu", "smi") for m in ("eer", "bpcer5", "bpcer10", "auc")]
        hdr += [f"{g}-all_{m}{s}" for g in ("neu", "smi") for m in ("eer", "bpcer5", "bpcer10") for s in ("", "_lo", "_hi")]
        w.writerow(hdr)
        for r in res:
            for cn, o in r["b"].items():
                w.writerow([r["label"], r["group"], r["ckpt"], cn] + [f"{o[g][m]:.3f}" for g in ("all", "neu", "smi") for m in ("eer", "bpcer5", "bpcer10", "auc")]
                           + [f"{x:.3f}" for g in ("neu", "smi") for m in ("eer", "bpcer5", "bpcer10") for x in o[f"{g}-all_{m}"]])
    print("done", flush=True)


if __name__ == "__main__":
    main()
