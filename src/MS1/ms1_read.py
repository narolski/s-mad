"""MS1 reader (prereg part 2): implements exactly the registered reads P1, P2, P3 and guards G1-G3 for arms Sb and SbM3.

Input: result tars MS1_<arm>_s<seed>.tar (scores_eval.npz: id, logit) in --results; the evaluation manifest of the
pack. A seed is read only if both arms have a verified tar (sha256 file beside it) and finite logits.
  python3 -I ms1_read.py --results DIR --manifest pn1_eval.csv --out OUT.json
  python3 -I ms1_read.py --mock          (random scores; tests the code path only)
"""
import argparse
import csv
import io
import itertools
import json
import math
import pathlib
import sys
import tarfile

import numpy as np

ARMS = ("Sb", "SbM3")
SEEDS = (403, 404, 405, 406, 407)
TT1 = ("replay_attack", "msu_mfsd", "oulu_npu", "casia_fasd", "lfw_calfw", "cfp_ff", "agedb_30")


def fauc(pos, neg):
    """rank AUC, ties half."""
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    allv = np.concatenate([pos, neg])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv))
    s = allv[order]
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def mw_less(x, y):
    """exact one-sided Mann-Whitney p for 'x tends to be lower than y' (ties half), by enumeration of all splits."""
    x, y = list(map(float, x)), list(map(float, y))

    def U(a, b):
        return sum((ai < bi) + 0.5 * (ai == bi) for ai in a for bi in b)

    u_obs = U(x, y)
    pooled = x + y
    n = len(x)
    cnt = tot = 0
    for idx in itertools.combinations(range(len(pooled)), n):
        a = [pooled[i] for i in idx]
        b = [pooled[i] for i in range(len(pooled)) if i not in idx]
        tot += 1
        cnt += U(a, b) >= u_obs - 1e-12
    return dict(U_lower=u_obs, of=len(x) * len(y), p=cnt / tot)


def cp(k, n):
    from scipy.stats import beta
    lo = beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return [float(lo), float(hi)]


def thr5(g):
    """smallest score t with share(g > t) <= 0.05 (EV1 rule)."""
    g = np.sort(np.asarray(g, float))
    for t in g:
        if (g > t).mean() <= 0.05:
            return float(t)
    return float(g[-1])


def net_reads(L, M):
    """L: id -> logit; M: manifest rows. Returns every per-network quantity."""
    def ids(f):
        return [r["id"] for r in M if f(r)]

    def v(f):
        return np.array([L[i] for i in ids(f)], float)

    out = {}
    cam_l = v(lambda r: r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R0" and r["strength"] == "")
    cam_a = v(lambda r: r["fam"] == "af0" and r["role"] == "dev" and r["rung"] == "photo" and r["strength"] == "")
    cam = np.concatenate([cam_l, cam_a])
    tau_cam = max(thr5(cam_l), thr5(cam_a))
    out["tau_cam"] = tau_cam
    f, auc, fcam = {}, {}, {}
    for k in TT1:
        g = v(lambda r, k=k: r["fam"] == "tt1" and r["cell"] == k)
        f[k] = dict(n=len(g), flag=float((g > 0).mean()), ci=cp(int((g > 0).sum()), len(g)))
        fcam[k] = float((g > tau_cam).mean())
        auc[k] = fauc(g, cam)
    out["P1_F"] = float(np.mean([f[k]["flag"] for k in TT1]))
    out["P1_per_family"] = f
    out["P2_O"] = float(np.mean([auc[k] for k in TT1]))
    out["P2_per_family"] = auc
    out["tt1_flag_at_tau_cam"] = fcam
    hp = v(lambda r: r["fam"] == "ms1ffhq" and r["rung"] == "photo" and r["strength"] == "")
    hu = v(lambda r: r["fam"] == "ms1ffhq" and r["rung"] == "u50" and r["strength"] == "")
    out["P3_holdout_flag"] = float((hp > 0).mean())
    out["P3_holdout_n"] = len(hp)
    out["holdout_u50_vs_photo_auc"] = fauc(hu, hp)
    hn2 = v(lambda r: r["fam"] == "ffhq" and r["rung"] == "ffhq_bona_orig")
    out["ffhqm_hn2_genuine_flag"] = float((hn2 > 0).mean())
    lm = v(lambda r: r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig")
    lg = v(lambda r: r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_resmatch")
    out["G1_lcomb_auc"] = fauc(lm, lg)
    r4 = v(lambda r: r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R4" and r["strength"] == "")
    r2w = v(lambda r: r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R2w" and r["strength"] == "")
    u50 = v(lambda r: r["fam"] == "af0" and r["role"] == "dev" and r["rung"] == "u50" and r["strength"] == "")
    out["G2_R4_vs_R2w_auc"] = fauc(r4, r2w)
    out["G2_u50_vs_photo_auc"] = fauc(u50, cam_a)
    att = np.concatenate([r4, u50])
    out["G2_own_rule_miss"] = float((att <= 0).mean())

    def shift(base_f, tag):
        b = {r["id"]: r for r in M if base_f(r)}
        pairs = [(L[i], L[i + tag]) for i in b if (i + tag) in L]
        if not pairs:
            return None
        a = np.array(pairs)
        return float(np.median(a[:, 1] - a[:, 0]) / a[:, 0].std(ddof=1))

    camf = (lambda r: (r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R0" and r["strength"] == "")
            or (r["fam"] == "af0" and r["role"] == "dev" and r["rung"] == "photo" and r["strength"] == ""))
    out["G3_shift_112_cam"] = shift(camf, "_amsl112")
    out["G3_shift_61_cam"] = shift(camf, "_fm61")
    hpf = lambda r: r["fam"] == "ms1ffhq" and r["rung"] == "photo" and r["strength"] == ""   # noqa: E731
    out["shift_112_ms1ffhq"] = shift(hpf, "_amsl112")
    out["shift_61_ms1ffhq"] = shift(hpf, "_fm61")
    # FS1 contrast 2 read (paired storage share), printed
    bona = {r["host"]: L[r["id"]] for r in M if r["fam"] == "ffhq" and r["rung"] == "ffhq_bona_orig"}
    res = {r["host"]: L[r["id"]] for r in M if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_resmatch"}
    keys = sorted(set(bona) & set(res))
    out["fs1_c2_share_rise"] = float(np.mean([res[k] > bona[k] for k in keys])) if keys else None
    return out


def decide(nets, seeds):
    S = {a: [nets[(a, s)] for s in seeds] for a in ARMS}

    def med(a, k):
        return float(np.median([n[k] for n in S[a]]))

    n = len(seeds)
    R = dict(read_seeds=list(seeds), n=n)
    if n <= 3:
        R["verdict"] = "not read (too few seeds)"
        return R
    F = {a: [x["P1_F"] for x in S[a]] for a in ARMS}
    mw = mw_less(F["SbM3"], F["Sb"])
    ratio = med("SbM3", "P1_F") / med("Sb", "P1_F") if med("Sb", "P1_F") > 0 else float("nan")
    if med("Sb", "P1_F") < 0.03:
        p1 = "untestable at the own rule (floor)"
    elif ratio <= 0.5 and mw["p"] <= 0.05:
        p1 = "supported"
    elif ratio >= 0.8 or mw["p"] > 0.5:
        p1 = "falsified"
    else:
        p1 = "inconclusive, no claim"
    R["P1"] = dict(median_Sb=med("Sb", "P1_F"), median_SbM3=med("SbM3", "P1_F"), ratio=ratio, mw=mw, verdict=p1,
                   values=F, families_lower=sum(
                       np.median([x["P1_per_family"][k]["flag"] for x in S["SbM3"]]) <
                       np.median([x["P1_per_family"][k]["flag"] for x in S["Sb"]]) for k in TT1))
    O = {a: [x["P2_O"] for x in S[a]] for a in ARMS}
    mw2 = mw_less(O["SbM3"], O["Sb"])
    d = med("Sb", "P2_O") - med("SbM3", "P2_O")
    p2 = "supported" if d >= 0.05 and mw2["p"] <= 0.05 else ("falsified" if d <= 0 else "inconclusive, no claim")
    R["P2"] = dict(median_Sb=med("Sb", "P2_O"), median_SbM3=med("SbM3", "P2_O"), diff=d, mw=mw2, verdict=p2, values=O)
    p3 = med("SbM3", "P3_holdout_flag")
    R["P3"] = dict(median_SbM3=p3, median_Sb=med("Sb", "P3_holdout_flag"),
                   verdict="supported" if p3 <= 0.05 else ("falsified" if p3 > 0.10 else "inconclusive, no claim"))
    g = {}
    g["G1"] = med("SbM3", "G1_lcomb_auc") >= med("Sb", "G1_lcomb_auc") - 0.03
    g["G2"] = (med("SbM3", "G2_R4_vs_R2w_auc") >= med("Sb", "G2_R4_vs_R2w_auc") - 0.02 and
               med("SbM3", "G2_u50_vs_photo_auc") >= med("Sb", "G2_u50_vs_photo_auc") - 0.02 and
               med("SbM3", "G2_own_rule_miss") <= med("Sb", "G2_own_rule_miss") + 0.05)
    g["G3"] = abs(med("SbM3", "G3_shift_112_cam")) <= abs(med("Sb", "G3_shift_112_cam")) + 0.10
    R["guards"] = g
    R["guard_values"] = {k: {a: med(a, k) for a in ARMS} for k in (
        "G1_lcomb_auc", "G2_R4_vs_R2w_auc", "G2_u50_vs_photo_auc", "G2_own_rule_miss", "G3_shift_112_cam",
        "G3_shift_61_cam", "shift_112_ms1ffhq", "shift_61_ms1ffhq", "fs1_c2_share_rise", "ffhqm_hn2_genuine_flag",
        "holdout_u50_vs_photo_auc")}
    R["guard_mw_SbM3_lower"] = {k: mw_less([x[k] for x in S["SbM3"]], [x[k] for x in S["Sb"]])
                                for k in ("G1_lcomb_auc", "G2_R4_vs_R2w_auc", "G2_u50_vs_photo_auc")}
    if p1 == "supported":
        failed = [k for k, ok in g.items() if not ok]
        R["sentence"] = ("Adding a third capture source, with its own morphs and matched controls, lowers genuine flag "
                         "rates at the network's own rule on seven unseen development sources (%d seeds)." % n)
        if failed:
            R["sentence"] = R["sentence"][:-1] + ", at a cost in " + ", ".join(failed) + "."
    elif p1 == "falsified":
        R["sentence"] = "One added capture source does not make the own-rule threshold transfer to unseen sources."
    elif p1.startswith("untestable") and p2 == "supported":
        R["sentence"] = ("The added source moves unseen-source genuine scores toward the training sources' camera photos "
                         "(scale-free), no own-rule effect measurable.")
    else:
        R["sentence"] = "inconclusive, no claim"
    return R


def load_tar(p):
    with tarfile.open(p) as t:
        m = [x for x in t.getmembers() if x.name.endswith("scores_eval.npz")][0]
        z = np.load(io.BytesIO(t.extractfile(m).read()))
        return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results")
    ap.add_argument("--manifest")
    ap.add_argument("--out")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    M = list(csv.DictReader(open(a.manifest or "/mnt/t7/smad_next/MS1/pack_tree/pn1/data/manifests/pn1_eval.csv")))
    nets, status = {}, {}
    for arm in ARMS:
        for s in SEEDS:
            if a.mock:
                rng = np.random.default_rng(hash((arm, s)) % 2 ** 32)
                L = {r["id"]: float(rng.normal(-2 if r["label"] == "0" else 1, 1.5)) for r in M}
            else:
                p = pathlib.Path(a.results) / f"MS1_{arm}_s{s}.tar"
                sh = pathlib.Path(str(p) + ".sha256")
                if not (p.exists() and sh.exists()):
                    status[f"{arm}_{s}"] = "missing"
                    continue
                import hashlib
                h = hashlib.sha256(open(p, "rb").read()).hexdigest()
                if h != open(sh).read().split()[0]:
                    status[f"{arm}_{s}"] = "sha256 mismatch"
                    continue
                L = load_tar(p)
                if not all(math.isfinite(x) for x in L.values()):
                    status[f"{arm}_{s}"] = "non-finite"
                    continue
            nets[(arm, s)] = net_reads(L, M)
            status[f"{arm}_{s}"] = "read"
    seeds = [s for s in SEEDS if all((arm, s) in nets for arm in ARMS)]
    R = decide(nets, seeds)
    R["status"] = status
    R["per_network"] = {f"{k[0]}_s{k[1]}": v for k, v in nets.items()}
    R["mock"] = a.mock
    out = a.out or ("/home/narolski/smad-next/experiments/MS1_multi-source-training-set/ms1_read_mock.json" if a.mock
                    else None)
    json.dump(R, open(out, "w"), indent=1, default=float)
    print(json.dumps({k: R.get(k) for k in ("read_seeds", "sentence", "guards")}, default=float))
    print(json.dumps({k: R[k]["verdict"] for k in ("P1", "P2", "P3") if k in R}))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
