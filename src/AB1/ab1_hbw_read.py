"""AB1 amendment 3c (post hoc): H-hb1 read with the adversary's inverse-probability weights over all 3,000
landmark_combined rows (round-0 surround-only score plus pre_ied; stabilised and trimmed by the adversary). AB1 H100
fit-job scores of A, B, Sb at seeds 408-412 (ab1_read.load, provenance-checked).

Inputs (each committed in git, unmodified, at the sha256 passed on the command line from the adversary's commit):
  --weights CSV   columns id, weight (all 3,000 landmark_combined ids; weights > 0)
  --regional CSV  experiments/ADV_shortcut-floors/floors/lcomb_regional_heldout.csv (round-0 held-out surround_logreg,
                  surround_gbt, face_logreg, face_gbt; fixed input)
Gate (else "not read"): effective sample size (sum w)^2 / sum w^2 >= 300 in each class; weighted AUC of the round-0
surround_logreg and surround_gbt scores <= 0.60 for both (computed here with the weights; folded: max(u, 1 - u)).
Guard: if the weighted face floor (max of face_logreg and face_gbt weighted AUC, folded) is below 0.80, a supported outcome
reads "gain lost under weighting, not attributable to history alone".
Rule (exclusive, as amendment 3b): per seed g_full = AUC(Sb) - AUC(B) unweighted on the 3,000 rows; g_w = weighted AUC
difference. shrinks if g_full > 0 and g_w <= 1/2 g_full; stays if g_w >= +0.10 and g_w > 1/2 g_full; supported if >= 4 of
5 shrink, falsified if >= 4 of 5 stay, otherwise inconclusive; <= 3 read seeds "not read". Sb - A secondary.
Printed: weighted AUC per arm and seed with a weighted row bootstrap (2,000 draws of rows within class with replacement,
weights kept, rng 20261119, the same draws for all arms and seeds); paired weighted gain with its interval; a null from
2,000 random re-assignments of the weights within class (rng 20261117), percentile of each seed's g_w and of the seed
mean; the probit-scale gain sqrt(2) * Phi^-1(AUC).
  python3 -I ab1_hbw_read.py --weights F --weights-sha H --regional-sha H --out OUT.json
  python3 -I ab1_hbw_read.py --mock --out MOCK.json"""
import argparse
import csv
import hashlib
import importlib.util
import json
import pathlib
import subprocess
from math import sqrt
from statistics import NormalDist

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ab1_read", HERE / "ab1_read.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
AB1_READ_SHA = "74ecdf7a2ecb35812dcf4e5d5b9f5c3b1f095fc6846ae6f4813bfb28404d035b"
REGIONAL = "/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/lcomb_regional_heldout.csv"
SEEDS = A.SEEDS


def committed(path, want):
    p = pathlib.Path(path)
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    assert h == want, f"{p.name}: sha256 {h[:16]} != {want[:16]}"
    d = str(p.parent)
    assert subprocess.run(["git", "-C", d, "ls-files", "--error-unmatch", p.name], capture_output=True).returncode == 0, "not tracked"
    assert subprocess.run(["git", "-C", d, "diff", "--quiet", "HEAD", "--", p.name]).returncode == 0, "modified against HEAD"


def wauc(sp, wp, sn, wn):
    """weighted AUC: sum_i sum_j wp_i wn_j ([sp_i > sn_j] + 0.5 [sp_i == sn_j]) / (sum wp * sum wn)."""
    sp, wp, sn, wn = map(lambda v: np.asarray(v, float), (sp, wp, sn, wn))
    order = np.argsort(sn, kind="mergesort")
    sn_s, wn_s = sn[order], wn[order]
    cw = np.concatenate([[0.0], np.cumsum(wn_s)])
    lo = np.searchsorted(sn_s, sp, side="left")
    hi = np.searchsorted(sn_s, sp, side="right")
    below = cw[lo]
    ties = cw[hi] - cw[lo]
    return float(np.sum(wp * (below + 0.5 * ties)) / (wp.sum() * wn.sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights"); ap.add_argument("--weights-sha"); ap.add_argument("--regional-sha")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    assert A.sha(HERE / "ab1_read.py") == AB1_READ_SHA
    M = list(csv.DictReader(open(A.EVAL)))
    P = A.pools(M)
    pos, neg = P["lc_m"], P["lc_g"]
    if a.mock:
        r0 = np.random.default_rng(3)
        w = {i: float(r0.uniform(0.2, 3.0)) for i in pos + neg}
        reg = {i: dict(surround_logreg=float(r0.normal()), surround_gbt=float(r0.normal()),
                       face_logreg=float(r0.normal(1.0 if i in set(pos) else 0.0)), face_gbt=float(r0.normal(1.0 if i in set(pos) else 0.0)))
               for i in pos + neg}
    else:
        committed(a.weights, a.weights_sha)
        committed(REGIONAL, a.regional_sha)
        W = {r["id"]: float(r["weight"]) for r in csv.DictReader(open(a.weights))}
        assert set(W) == set(pos + neg) and all(v > 0 for v in W.values()), "weights must cover the 3,000 rows, > 0"
        w = W
        reg = {r["id"]: {k: float(r[k]) for k in ("surround_logreg", "surround_gbt", "face_logreg", "face_gbt")}
               for r in csv.DictReader(open(REGIONAL))}
    wp, wn = np.array([w[i] for i in pos]), np.array([w[i] for i in neg])
    ess = lambda v: float(v.sum() ** 2 / (v ** 2).sum())
    fold = lambda u: max(u, 1 - u)
    wsur = {k: fold(wauc([reg[i][k] for i in pos], wp, [reg[i][k] for i in neg], wn)) for k in ("surround_logreg", "surround_gbt")}
    wface = {k: fold(wauc([reg[i][k] for i in pos], wp, [reg[i][k] for i in neg], wn)) for k in ("face_logreg", "face_gbt")}
    gate = dict(ess_morph=ess(wp), ess_genuine=ess(wn), weighted_surround_floor=wsur, weighted_face_floor=wface)
    gate["ok"] = bool(gate["ess_morph"] >= 300 and gate["ess_genuine"] >= 300 and all(v <= 0.60 for v in wsur.values()))
    face_floor = max(wface.values())
    R = dict(mock=a.mock, gate=gate, status={}, networks={}, seeds={})
    nets = {}
    for arm in ("A", "B", "Sb"):
        for s in SEEDS:
            key = f"{arm}_s{s}"
            if a.mock:
                r = np.random.default_rng(s * 10 + len(arm))
                x = {i: float(r.normal(1.0 if i in set(pos) else -1.0, 1.5)) for i in pos + neg}
            else:
                x, _, why = A.load(pathlib.Path("/mnt/t7/smad_next/AB1/results") / f"AB1_{arm}_s{s}.tar", "AB1", arm)
                if x is None:
                    R["status"][key] = why
                    continue
            R["status"][key] = "read"
            nets[(arm, s)] = (np.array([x[i] for i in pos]), np.array([x[i] for i in neg]))
    rng = np.random.default_rng(20261119)
    draws = [(rng.integers(0, len(pos), len(pos)), rng.integers(0, len(neg), len(neg))) for _ in range(2000)]
    pr = lambda u: sqrt(2) * NormalDist().inv_cdf(min(max(u, 1e-6), 1 - 1e-6))
    for (arm, s), (sp, sn) in nets.items():
        boot = [wauc(sp[i], wp[i], sn[j], wn[j]) for i, j in draws]
        R["networks"][f"{arm}_s{s}"] = dict(auc_full=wauc(sp, np.ones(len(sp)), sn, np.ones(len(sn))), auc_w=wauc(sp, wp, sn, wn),
                                            auc_w_ci=[float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))])
    rd = [s for s in SEEDS if all((arm, s) in nets for arm in ("A", "B", "Sb"))]
    rngn = np.random.default_rng(20261117)
    perms = [(rngn.permutation(len(pos)), rngn.permutation(len(neg))) for _ in range(2000)]
    for s in rd:
        rec = {}
        for o in ("B", "A"):
            (sps, sns), (spo, sno) = nets[("Sb", s)], nets[(o, s)]
            nf = R["networks"]
            gf = nf[f"Sb_s{s}"]["auc_full"] - nf[f"{o}_s{s}"]["auc_full"]
            gw = nf[f"Sb_s{s}"]["auc_w"] - nf[f"{o}_s{s}"]["auc_w"]
            dd = [wauc(sps[i], wp[i], sns[j], wn[j]) - wauc(spo[i], wp[i], sno[j], wn[j]) for i, j in draws]
            nul = [wauc(sps, wp[pi], sns, wn[pj]) - wauc(spo, wp[pi], sno, wn[pj]) for pi, pj in perms]
            rec[f"Sb_minus_{o}"] = dict(g_full=gf, g_w=gw, g_w_ci=[float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))],
                                        null_percentile=float(np.mean(np.array(nul) <= gw) * 100),
                                        probit=dict(full=pr(nf[f"Sb_s{s}"]["auc_full"]) - pr(nf[f"{o}_s{s}"]["auc_full"]),
                                                    weighted=pr(nf[f"Sb_s{s}"]["auc_w"]) - pr(nf[f"{o}_s{s}"]["auc_w"])),
                                        shrinks=bool(gf > 0 and gw <= 0.5 * gf), stays=bool(gw >= 0.10 and gw > 0.5 * gf))
            rec[f"Sb_minus_{o}"]["_null"] = nul
        R["seeds"][str(s)] = rec
    V = {}
    for o in ("B", "A"):
        k_s = sum(R["seeds"][str(s)][f"Sb_minus_{o}"]["shrinks"] for s in rd)
        k_f = sum(R["seeds"][str(s)][f"Sb_minus_{o}"]["stays"] for s in rd)
        v = A.verdict(k_s, k_f, len(rd)) if gate["ok"] else "not read (weights gate: ESS or weighted surround floor)"
        if v == "supported" and face_floor < 0.80:
            v = "supported: gain lost under weighting, not attributable to history alone (weighted face floor < 0.80)"
        if rd:
            sm = float(np.mean([R["seeds"][str(s)][f"Sb_minus_{o}"]["g_w"] for s in rd]))
            nm = np.mean([R["seeds"][str(s)][f"Sb_minus_{o}"]["_null"] for s in rd], axis=0)
            seed_mean = dict(mean=sm, null_percentile=float(np.mean(nm <= sm) * 100))
        else:
            seed_mean = None
        V[f"H_hb1w_Sb_minus_{o}"] = dict(read_seeds=rd, k_shrinks=k_s, k_stays=k_f, verdict=v, seed_mean=seed_mean,
                                         role="registered (H-hb1, weighted)" if o == "B" else "secondary")
    for s in rd:
        for o in ("B", "A"):
            R["seeds"][str(s)][f"Sb_minus_{o}"].pop("_null")
    R["verdicts"] = V
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    print(json.dumps({k: v["verdict"] for k, v in V.items()}, indent=1))
    print("gate:", gate)


if __name__ == "__main__":
    main()
