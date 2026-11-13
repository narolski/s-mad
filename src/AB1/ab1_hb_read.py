"""AB1 amendment 3 (post hoc): landmark_combined contrasts on the ADVERSARY's history-balanced subset (lcomb_bal) and within
surround-score strata, seeds 408-412, H100 fit-job scores of A, B, Sb (AB1 tars, provenance-checked by ab1_read.load).

Inputs published by ADVERSARY (committed and pinned; this reader asserts that each file is tracked by git, unmodified
against HEAD, and that its sha256 equals the value passed on the command line, taken from the ADV commit):
  --bal CSV       the lcomb_bal row list (column "id" = ab1_eval ids of landmark_combined rows; column "label" if present
                  must agree with the manifest; optional column "weight" is NOT used: the registered read is unweighted)
  --surround CSV  per-row surround-only held-out score for all 3,000 landmark_combined rows (columns "id" and the score
                  column named by --surround-col)
  --learner JSON  (optional, printed) the same-data shortcut learner's AUC on lcomb_bal
Reads (registered in prereg.md amendment 3):
  H-hb1 (the review's H-new-2): per seed g_full = AUC(Sb) - AUC(B) on all 3,000 rows, g_bal = the same on lcomb_bal.
    supported if g_bal <= 0.5 * g_full on >= 4 of 5 seeds; falsified if g_bal >= +0.10 on >= 4 of 5 seeds; otherwise
    inconclusive; <= 3 read seeds: not read. Sb - A by the same rule (secondary).
  printed: per-network AUC on lcomb_bal with a 95% interval (2,000 bootstraps of images within class, rng 20261116),
    paired Sb - B and Sb - A on lcomb_bal with intervals (same draws), and the three differences within quintiles of the
    surround score (quintile edges over the 3,000 rows); the shortcut learner's AUC on lcomb_bal beside Sb's.
  python3 -I ab1_hb_read.py --bal F --bal-sha H --surround F --surround-sha H --surround-col C [--learner F] --out OUT
  python3 -I ab1_hb_read.py --mock --out MOCK.json"""
import argparse
import csv
import hashlib
import importlib.util
import json
import pathlib
import subprocess

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ab1_read", HERE / "ab1_read.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
C2 = A.C2
AB1_READ_SHA = "74ecdf7a2ecb35812dcf4e5d5b9f5c3b1f095fc6846ae6f4813bfb28404d035b"
SEEDS = A.SEEDS


def committed(path, want):
    p = pathlib.Path(path)
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    assert h == want, f"{p.name}: sha256 {h[:16]} != {want[:16]}"
    d = str(p.parent)
    assert subprocess.run(["git", "-C", d, "ls-files", "--error-unmatch", p.name], capture_output=True).returncode == 0, "not tracked"
    assert subprocess.run(["git", "-C", d, "diff", "--quiet", "HEAD", "--", p.name]).returncode == 0, "modified against HEAD"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bal"); ap.add_argument("--bal-sha")
    ap.add_argument("--surround"); ap.add_argument("--surround-sha"); ap.add_argument("--surround-col")
    ap.add_argument("--learner")
    ap.add_argument("--arm", choices=("SbFM", "Sbx"))   # printed only: the follow-up arm on lcomb_bal beside Sb
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    assert A.sha(HERE / "ab1_read.py") == AB1_READ_SHA
    M = list(csv.DictReader(open(A.EVAL)))
    P = A.pools(M)
    lab = {i: 1 for i in P["lc_m"]} | {i: 0 for i in P["lc_g"]}
    allids = P["lc_m"] + P["lc_g"]
    rng0 = np.random.default_rng(1)
    if a.mock:
        bal = [i for i in allids if rng0.random() < 0.5]
        sur = {i: float(rng0.normal()) for i in allids}
        learner = None
    else:
        committed(a.bal, a.bal_sha)
        committed(a.surround, a.surround_sha)
        B = list(csv.DictReader(open(a.bal)))
        bal = [r["id"] for r in B]
        assert len(set(bal)) == len(bal) and all(i in lab for i in bal), "lcomb_bal ids must be landmark_combined rows"
        for r in B:
            if "label" in r and r["label"] != "":
                assert int(r["label"]) == lab[r["id"]], r["id"]
        S = {r["id"]: float(r[a.surround_col]) for r in csv.DictReader(open(a.surround))}
        assert set(S) >= set(allids), "surround score missing for some landmark_combined rows"
        sur = S
        learner = json.loads(pathlib.Path(a.learner).read_text()) if a.learner else None
    bal_m = [i for i in bal if lab[i] == 1]; bal_g = [i for i in bal if lab[i] == 0]
    assert bal_m and bal_g
    rng = np.random.default_rng(20261116)
    draws = [(rng.integers(0, len(bal_m), len(bal_m)), rng.integers(0, len(bal_g), len(bal_g))) for _ in range(2000)]
    edges = np.quantile([sur[i] for i in allids], [0.2, 0.4, 0.6, 0.8])
    qof = {i: int(np.searchsorted(edges, sur[i], side="right")) for i in allids}
    R = dict(mock=a.mock, n_bal=dict(morph=len(bal_m), genuine=len(bal_g)), status={}, networks={}, seeds={})
    nets = {}
    for arm in ("A", "B", "Sb"):
        for s in SEEDS:
            key = f"{arm}_s{s}"
            if a.mock:
                r = np.random.default_rng(s * 10 + len(arm))
                x = {i: float(r.normal(1.0 if lab[i] else -1.0 + 0.3 * sur[i], 1.5)) for i in allids}
            else:
                x, _, why = A.load(pathlib.Path("/mnt/t7/smad_next/AB1/results") / f"AB1_{arm}_s{s}.tar", "AB1", arm)
                if x is None:
                    R["status"][key] = why
                    continue
            R["status"][key] = "read"
            nets[(arm, s)] = x
            m, g = np.array([x[i] for i in bal_m]), np.array([x[i] for i in bal_g])
            bs = [C2.fauc(m[im], g[ig]) for im, ig in draws]
            R["networks"][key] = dict(auc_full=C2.fauc([x[i] for i in P["lc_m"]], [x[i] for i in P["lc_g"]]),
                                      auc_bal=C2.fauc(m, g), auc_bal_ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])

    def auc_ids(x, ids):
        pm = [x[i] for i in ids if lab[i] == 1]; pg = [x[i] for i in ids if lab[i] == 0]
        return C2.fauc(pm, pg) if pm and pg else None
    for s in SEEDS:
        if not all((arm, s) in nets for arm in ("A", "B", "Sb")):
            continue
        rec = {}
        for other in ("B", "A"):
            xs, xo = nets[("Sb", s)], nets[(other, s)]
            gf = R["networks"][f"Sb_s{s}"]["auc_full"] - R["networks"][f"{other}_s{s}"]["auc_full"]
            gb = R["networks"][f"Sb_s{s}"]["auc_bal"] - R["networks"][f"{other}_s{s}"]["auc_bal"]
            ms, gs = np.array([xs[i] for i in bal_m]), np.array([xs[i] for i in bal_g])
            mo, go = np.array([xo[i] for i in bal_m]), np.array([xo[i] for i in bal_g])
            dd = [C2.fauc(ms[im], gs[ig]) - C2.fauc(mo[im], go[ig]) for im, ig in draws]
            strata = {}
            for q in range(5):
                ids = [i for i in allids if qof[i] == q]
                aa, bb = auc_ids(xs, ids), auc_ids(xo, ids)
                strata[str(q)] = dict(n=len(ids), n_morph=sum(lab[i] for i in ids),
                                      diff=None if aa is None or bb is None else aa - bb)
            rec[f"Sb_minus_{other}"] = dict(g_full=gf, g_bal=gb, g_bal_ci=[float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))],
                                            shrinks_by_half=bool(gb <= 0.5 * gf), stays_ge_010=bool(gb >= 0.10),
                                            within_surround_quintiles=strata)
        R["seeds"][str(s)] = rec
    V = {}
    for other in ("B", "A"):
        rd = [s for s in R["seeds"]]
        k_s = sum(R["seeds"][s][f"Sb_minus_{other}"]["shrinks_by_half"] for s in rd)
        k_f = sum(R["seeds"][s][f"Sb_minus_{other}"]["stays_ge_010"] for s in rd)
        V[f"H_hb1_Sb_minus_{other}"] = dict(read_seeds=rd, k_shrinks=k_s, k_stays=k_f, verdict=A.verdict(k_s, k_f, len(rd)))
    V["H_hb1_Sb_minus_B"]["role"] = "registered (the review's H-new-2)"
    V["H_hb1_Sb_minus_A"]["role"] = "secondary, same rule"
    if a.arm and not a.mock:                              # printed: follow-up arm's AUC on lcomb_bal and arm - Sb
        if a.arm == "SbFM":
            spec2 = importlib.util.spec_from_file_location("ab1fm_read", HERE / "ab1fm_read.py")
            F = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(F)
            ld = lambda s: F.load_fm(pathlib.Path("/mnt/t7/smad_next/AB1/fm/results") / f"AB1FM_SbFM_s{s}.tar")[0]
        else:
            spec2 = importlib.util.spec_from_file_location("ab1x_read", HERE / "ab1x_read.py")
            F = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(F)
            ld = lambda s: F.load_x(pathlib.Path("/mnt/t7/smad_next/AB1/x/results") / f"AB1X_Sbx_s{s}.tar")[0]
        R["printed_arm"] = {}
        for s in SEEDS:
            x = ld(s)
            if x is None or f"Sb_s{s}" not in R["networks"]:
                continue
            ab = C2.fauc([x[i] for i in bal_m], [x[i] for i in bal_g])
            af = C2.fauc([x[i] for i in P["lc_m"]], [x[i] for i in P["lc_g"]])
            R["printed_arm"][str(s)] = dict(arm=a.arm, auc_full=af, auc_bal=ab, arm_minus_Sb_full=af - R["networks"][f"Sb_s{s}"]["auc_full"],
                                            arm_minus_Sb_bal=ab - R["networks"][f"Sb_s{s}"]["auc_bal"])
    R["verdicts"] = V
    R["printed_learner_vs_Sb"] = dict(learner=learner, Sb_auc_bal={s: R["networks"].get(f"Sb_s{s}", {}).get("auc_bal") for s in SEEDS})
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    print(json.dumps({k: v["verdict"] for k, v in V.items()}, indent=1))


if __name__ == "__main__":
    main()
