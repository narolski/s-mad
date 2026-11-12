"""MS1 reader (prereg part 2, f748da4): the registered reads P1-S (CFD), P1-T (TT1), P2, P3 and guards G1-G3, SbM3
against Sb (co-primaries at p <= 0.025); SbV printed against Sb and SbM3.

Input: result tars MS1_<arm>_s<seed>.tar (scores_eval.npz: id, logit) in --results; held-out scores
MS1H_<arm>_s<seed>_<fam>.npz (rescore.py output: id, logit; fam cfd, kdef, optional tt1ref) in --heldout; the
evaluation manifest of the fit pack. A seed is read only if Sb and SbM3 have verified tars (sha256 beside) and finite
logits.
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
ALL_ARMS = ("Sb", "SbM3", "SbV")
SPLICE_SHARE = {"Sb": 0.1026, "SbM3": 0.0641, "SbV": 0.1050}
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


HM = "/mnt/t7/smad_next/MS1/heldout_tree/pn1/data/manifests/ms1_heldout.csv"


def tt1ref_reads(L, M, out):
    """MS1-D2: printed only. Own-rule flags of TT1's references and AUC(TT1 family k vs R_cam_border(k))."""
    try:
        H = [r for r in csv.DictReader(open(HM)) if r["fam"] == "tt1ref" and r["id"] in L]
    except FileNotFoundError:
        return
    if not H:
        return
    res = {}
    for rung in ("R_cam", "R_cam_geo224", "R_cam_geo112"):
        g = np.array([L[r["id"]] for r in H if r["rung"] == rung], float)
        if len(g):
            res[rung] = dict(n=len(g), flag=float((g > 0).mean()))
    for k in TT1:
        b = np.array([L[r["id"]] for r in H if r["rung"] == "R_cam_border" and r["cell"] == k], float)
        u = np.array([L[r["id"]] for r in M if r["fam"] == "tt1" and r["cell"] == k], float)
        if len(b) and len(u):
            res[f"border_{k}"] = dict(n=len(b), flag=float((b > 0).mean()), auc_tt1_vs_border=fauc(u, b))
        fb = np.array([L[r["id"]] for r in H if r["rung"] == "R_ffhq_border" and r["cell"] == k], float)
        if len(fb):
            res[f"ffhq_border_{k}"] = dict(n=len(fb), flag=float((fb > 0).mean()))
    out["tt1ref"] = res


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
    out["P1T_F_without_msu"] = float(np.mean([f[k]["flag"] for k in TT1 if k != "msu_mfsd"]))
    for hk in ("cfd", "kdef"):
        g = np.array([L[i] for i in L if i.startswith(hk + "_")], float)
        if len(g):
            out[f"{hk}_flag"] = float((g > 0).mean())
            out[f"{hk}_n"] = len(g)
            out[f"{hk}_ci"] = cp(int((g > 0).sum()), len(g))
            out[f"{hk}_flag_tau_cam"] = float((g > tau_cam).mean())
            out[f"{hk}_offset_auc"] = fauc(g, cam)
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
    tt1ref_reads(L, M, out)
    return out


def decide(nets, seeds, nets_all=None):
    nets_all = nets_all if nets_all is not None else nets
    nets_all_seeds = SEEDS
    S = {a: [nets[(a, s)] for s in seeds] for a in ARMS}

    def med(a, k):
        return float(np.median([n[k] for n in S[a]]))

    n = len(seeds)
    R = dict(read_seeds=list(seeds), n=n)
    if n <= 3:
        R["verdict"] = "not read (too few seeds)"
        return R
    def primary(key):
        F = {a: [x[key] for x in S[a]] for a in ARMS}
        mw = mw_less(F["SbM3"], F["Sb"])
        mb = med("Sb", key)
        ratio = med("SbM3", key) / mb if mb > 0 else float("nan")
        if mb < 0.03:
            v = "untestable at the own rule (floor)"
        elif ratio <= 0.5 and mw["p"] <= 0.025:
            v = "supported"
        elif ratio >= 0.8 or mw["p"] > 0.5:
            v = "falsified"
        else:
            v = "inconclusive, no claim"
        return dict(median_Sb=mb, median_SbM3=med("SbM3", key), ratio=ratio, mw=mw, verdict=v, values=F)

    R["P1T"] = primary("P1_F")
    R["P1T"]["families_lower"] = int(sum(
        np.median([x["P1_per_family"][k]["flag"] for x in S["SbM3"]]) <
        np.median([x["P1_per_family"][k]["flag"] for x in S["Sb"]]) for k in TT1))
    R["P1T_without_msu"] = primary("P1T_F_without_msu")
    has_cfd = all("cfd_flag" in x for a in ARMS for x in S[a])
    R["P1S"] = primary("cfd_flag") if has_cfd else dict(verdict="not read (no CFD scores)")
    p1 = R["P1T"]["verdict"]
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
    failed = [k for k, ok in g.items() if not ok]
    cost = (", at a cost in " + ", ".join(failed)) if failed else ""
    sent = {}
    for key, pool, long in (("P1S", "CFD", "a sharp unseen studio source (CFD)"),
                            ("P1T", "TT1", "seven unseen low-resolution sources with black borders (TT1)")):
        v = R[key]["verdict"]
        if v == "supported":
            sent[key] = (f"With the three-source protocol, genuine flag rates at the network's own rule fall on {long}, "
                         f"{n} seeds{cost}.")
        elif v == "falsified":
            sent[key] = f"The three-source protocol does not make the own-rule threshold transfer to {long}."
        elif v.startswith("untestable") and key == "P1T" and p2 == "supported":
            sent[key] = ("No own-rule effect measurable on TT1; scale-free, unseen-source genuine scores move toward "
                         "the training sources' camera photos.")
        else:
            sent[key] = "inconclusive, no claim"
    # SbV (data-volume control), printed only
    vs = [sd for sd in nets_all_seeds if ("SbV", sd) in nets_all and ("Sb", sd) in nets_all]
    V = dict(seeds=vs, splice_share_of_attack_rows=SPLICE_SHARE)
    if len(vs) >= 4:
        for key in ("P1_F", "cfd_flag", "P2_O", "P3_holdout_flag", "G1_lcomb_auc", "G2_R4_vs_R2w_auc"):
            if not all(key in nets_all[(a, sd)] for a in ("Sb", "SbV") for sd in vs):
                continue
            xv = [nets_all[("SbV", sd)][key] for sd in vs]
            xb = [nets_all[("Sb", sd)][key] for sd in vs]
            xm = [nets_all[("SbM3", sd)][key] for sd in vs if ("SbM3", sd) in nets_all]
            V[key] = dict(median_SbV=float(np.median(xv)), median_Sb=float(np.median(xb)),
                          median_SbM3=float(np.median(xm)) if xm else None,
                          mw_SbV_lower_than_Sb=mw_less(xv, xb), mw_SbM3_lower_than_SbV=mw_less(xm, xv) if xm else None)
            if key in ("P1_F", "cfd_flag"):
                r = V[key]["median_SbV"] / V[key]["median_Sb"] if V[key]["median_Sb"] > 0 else float("nan")
                V[key]["SbV_meets_support_rule_vs_Sb"] = bool(V[key]["median_Sb"] >= 0.03 and r <= 0.5 and
                                                              V[key]["mw_SbV_lower_than_Sb"]["p"] <= 0.025)
        for key, k2 in (("P1_F", "P1T"), ("cfd_flag", "P1S")):
            if V.get(key, {}).get("SbV_meets_support_rule_vs_Sb") and sent.get(k2, "").startswith("With the"):
                sent[k2] = sent[k2][:-1] + ("; the data-volume control shows a similar fall, so the effect is not shown "
                                            "to need the third source.")
    else:
        V["note"] = "SbV not read (fewer than 4 seeds with SbV and Sb)"
    R["SbV"] = V
    R["sentences"] = sent
    R["frame"] = ("The effect, if any, belongs to the three-source protocol (photos, morphs, controls, more rows, a "
                  "smaller splice share). Nothing is attributed to source diversity alone.")
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
    ap.add_argument("--heldout")
    ap.add_argument("--out")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    M = list(csv.DictReader(open(a.manifest or "/mnt/t7/smad_next/MS1/pack_tree/pn1/data/manifests/pn1_eval.csv")))
    nets, status = {}, {}
    for arm in ALL_ARMS:
        for s in SEEDS:
            if a.mock:
                rng = np.random.default_rng(hash((arm, s)) % 2 ** 32)
                L = {r["id"]: float(rng.normal(-2 if r["label"] == "0" else 1, 1.5)) for r in M}
                L.update({f"cfd_{i:04d}": float(rng.normal(-1.5, 1.5)) for i in range(831)})
                L.update({f"kdef_{i:04d}": float(rng.normal(-1.5, 1.5)) for i in range(140)})
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
                for fam in ("cfd", "kdef", "tt1ref"):
                    hp = pathlib.Path(a.heldout or "/nonexistent") / f"MS1H_{arm}_s{s}_{fam}.npz"
                    if hp.exists():
                        z = np.load(hp)
                        L.update(dict(zip([str(i) for i in z["id"]], z["logit"].astype(float))))
                if not all(math.isfinite(x) for x in L.values()):
                    status[f"{arm}_{s}"] = "non-finite"
                    continue
            nets[(arm, s)] = net_reads(L, M)
            status[f"{arm}_{s}"] = "read"
    seeds = [s for s in SEEDS if all((arm, s) in nets for arm in ARMS)]
    R = decide({k: v for k, v in nets.items() if k[0] in ARMS}, seeds, nets)
    R["status"] = status
    R["per_network"] = {f"{k[0]}_s{k[1]}": v for k, v in nets.items()}
    R["mock"] = a.mock
    out = a.out or ("/home/narolski/smad-next/experiments/MS1_multi-source-training-set/ms1_read_mock.json" if a.mock
                    else None)
    json.dump(R, open(out, "w"), indent=1, default=float)
    print(json.dumps({k: R.get(k) for k in ("read_seeds", "sentences", "guards")}, default=float))
    print(json.dumps({k: R[k]["verdict"] for k in ("P1S", "P1T", "P1T_without_msu", "P2", "P3") if k in R}))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
