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
    ap.add_argument("--build"); ap.add_argument("--build-sha")          # check F3: floors/lcomb_bal_build.json
    ap.add_argument("--regional-bal"); ap.add_argument("--regional-bal-sha")  # floors/lcomb_bal_regional.json (face floor)
    ap.add_argument("--balance-py"); ap.add_argument("--balance-sha")   # check F6: src/adversary/balance.py
    ap.add_argument("--surround", default="/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/lcomb_regional_heldout.csv")
    ap.add_argument("--surround-sha"); ap.add_argument("--surround-col", default="surround_logreg")
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
        build = dict(converged=True, n_pos=None, n_neg=None)
        regional_bal = dict(face_floor=dict(auc=0.85))
    else:
        assert a.surround_col == "surround_logreg" and a.surround.endswith("floors/lcomb_regional_heldout.csv"), "check F6: fixed input"
        committed(a.bal, a.bal_sha)
        committed(a.surround, a.surround_sha)
        committed(a.build, a.build_sha)
        committed(a.regional_bal, a.regional_bal_sha)
        committed(a.balance_py, a.balance_sha)
        # balance.py must be committed no later than the rows file
        t_py = int(subprocess.run(["git", "-C", str(pathlib.Path(a.balance_py).parent), "log", "-1", "--format=%ct", "--diff-filter=A", "--", pathlib.Path(a.balance_py).name], capture_output=True, text=True).stdout.strip() or 0)
        t_rows = int(subprocess.run(["git", "-C", str(pathlib.Path(a.bal).parent), "log", "-1", "--format=%ct", "--diff-filter=A", "--", pathlib.Path(a.bal).name], capture_output=True, text=True).stdout.strip() or 0)
        assert 0 < t_py <= t_rows, "balance.py not committed before (or with) the rows file"
        build = json.loads(pathlib.Path(a.build).read_text())
        regional_bal = json.loads(pathlib.Path(a.regional_bal).read_text())
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
    gate = dict(converged=bool(build.get("converged")), n_morph=len(bal_m), n_genuine=len(bal_g),
                equal_classes=(len(bal_m) == len(bal_g)) if not a.mock else True,
                build_counts_match=(build.get("n_pos") in (None, len(bal_m)) and build.get("n_neg") in (None, len(bal_g))),
                min_150=(len(bal_m) >= 150 and len(bal_g) >= 150))
    ff = regional_bal.get("face_floor")
    face_floor = ff.get("auc") if isinstance(ff, dict) else ff
    gate["face_floor_on_bal"] = face_floor
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
                nm = sum(lab[i] for i in ids); ng = len(ids) - nm
                strata[str(q)] = dict(n=len(ids), n_morph=nm, n_genuine=ng,
                                      diff=None if (aa is None or bb is None or nm < 20 or ng < 20) else aa - bb)   # check F5
            rec[f"Sb_minus_{other}"] = dict(g_full=gf, g_bal=gb, g_bal_ci=[float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))],
                                            shrinks_by_half=bool(gf > 0 and gb <= 0.5 * gf), stays_ge_010=bool(gb >= 0.10 and gb > 0.5 * gf),   # check F1
                                            within_surround_quintiles=strata)
        R["seeds"][str(s)] = rec
    V = {}
    ok_gate = gate["converged"] and gate["equal_classes"] and gate["build_counts_match"] and gate["min_150"]
    for other in ("B", "A"):
        rd = [s for s in R["seeds"]]
        k_s = sum(R["seeds"][s][f"Sb_minus_{other}"]["shrinks_by_half"] for s in rd)
        k_f = sum(R["seeds"][s][f"Sb_minus_{other}"]["stays_ge_010"] for s in rd)
        v = A.verdict(k_s, k_f, len(rd)) if ok_gate else "not read (subset gate: " + ", ".join(k for k in ("converged", "equal_classes", "build_counts_match", "min_150") if not gate[k]) + ")"
        if v == "supported" and (face_floor is None or face_floor < 0.80):
            v = "supported: gain lost on the subset, not attributable to history alone (face-region floor < 0.80)"
        V[f"H_hb1_Sb_minus_{other}"] = dict(read_seeds=rd, k_shrinks=k_s, k_stays=k_f, verdict=v)
    R["subset_gate"] = gate
    # check F2 (printed): seed-mean g_bal with a joint row bootstrap, and a null from random class-balanced subsets
    rd = [s for s in R["seeds"]]
    if rd:
        nb_m, nb_g = len(bal_m), len(bal_g)
        def gbal(ids_m, ids_g, s, other):
            xs, xo = nets[("Sb", int(s))], nets[(other, int(s))]
            return C2.fauc([xs[i] for i in ids_m], [xs[i] for i in ids_g]) - C2.fauc([xo[i] for i in ids_m], [xo[i] for i in ids_g])
        jb = {o: [] for o in ("B", "A")}
        for im, ig in draws[:500]:
            mm = [bal_m[k] for k in im]; gg = [bal_g[k] for k in ig]
            for o in ("B", "A"):
                jb[o].append(np.mean([gbal(mm, gg, s, o) for s in rd]))
        rngn = np.random.default_rng(20261117)
        null = {o: [] for o in ("B", "A")}
        null_seed = {o: {s: [] for s in rd} for o in ("B", "A")}
        for _ in range(2000):
            mm = list(rngn.choice(P["lc_m"], nb_m, replace=False)); gg = list(rngn.choice(P["lc_g"], nb_g, replace=False))
            for o in ("B", "A"):
                vals = [gbal(mm, gg, s, o) for s in rd]
                null[o].append(np.mean(vals))
                for s, vv in zip(rd, vals):
                    null_seed[o][s].append(vv)
        R["printed_seed_mean_and_null"] = {}
        for o in ("B", "A"):
            sm = float(np.mean([R["seeds"][s][f"Sb_minus_{o}"]["g_bal"] for s in rd]))
            R["printed_seed_mean_and_null"][f"Sb_minus_{o}"] = dict(
                seed_mean_g_bal=sm, joint_row_bootstrap_ci=[float(np.percentile(jb[o], 2.5)), float(np.percentile(jb[o], 97.5))],
                null_percentile_seed_mean=float(np.mean(np.array(null[o]) <= sm) * 100),
                null_percentile_per_seed={s: float(np.mean(np.array(null_seed[o][s]) <= R["seeds"][s][f"Sb_minus_{o}"]["g_bal"]) * 100) for s in rd},
                note="joint bootstrap uses 500 of the registered draws; null = 2,000 random class-balanced subsets of the same sizes (rng 20261117)")
    # check F4 (printed): covariates retained vs dropped, AUC decomposition, probit-scale gain
    if not a.mock:
        meta = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm_meta.csv"))}
        nu = {r["id"]: float(r["nu_gbt"]) for r in csv.DictReader(open("/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/lcomb_heldout.csv"))}
        reg = {r["id"]: r for r in csv.DictReader(open(a.surround))}
        bset = set(bal)
        cov = {}
        for cls, ids in (("morph", P["lc_m"]), ("genuine", P["lc_g"])):
            for part, sel in (("retained", [i for i in ids if i in bset]), ("dropped", [i for i in ids if i not in bset])):
                row = {}
                for f in ("pre_ied", "pre_w", "pre_png_bytes", "border_frac", "scale", "aligned_png_bytes"):
                    v = np.array([float(meta[i.replace("lcomb_", "")][f]) for i in sel])
                    row[f] = [float(v.mean()), float(v.std())] if len(v) else None
                for f, src in (("nu_gbt", nu), ("face_logreg", None), ("surround_logreg", None)):
                    v = np.array([src[i] if src is not None else float(reg[i][f]) for i in sel])
                    row[f] = [float(v.mean()), float(v.std())] if len(v) else None
                cov[f"{cls}|{part}"] = dict(n=len(sel), **row)
        R["printed_covariates"] = cov
    from math import sqrt
    from statistics import NormalDist
    pr = lambda u: sqrt(2) * NormalDist().inv_cdf(min(max(u, 1e-6), 1 - 1e-6))
    R["printed_decomposition_probit"] = {}
    for s in rd:
        rec = {}
        for arm in ("A", "B", "Sb"):
            x = nets[(arm, int(s))]
            rec[arm] = dict(retained_morph_vs_all_genuine=C2.fauc([x[i] for i in bal_m], [x[i] for i in P["lc_g"]]),
                            all_morph_vs_retained_genuine=C2.fauc([x[i] for i in P["lc_m"]], [x[i] for i in bal_g]))
        for o in ("B", "A"):
            nf = R["networks"]
            rec[f"probit_Sb_minus_{o}"] = dict(full=pr(nf[f"Sb_s{s}"]["auc_full"]) - pr(nf[f"{o}_s{s}"]["auc_full"]),
                                               bal=pr(nf[f"Sb_s{s}"]["auc_bal"]) - pr(nf[f"{o}_s{s}"]["auc_bal"]))
        R["printed_decomposition_probit"][s] = rec
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
    print("subset gate:", gate)


if __name__ == "__main__":
    main()
