"""Threshold transfer on unseen genuine sources (TT1), FS1 block: registered reader (prereg_fs1_block.md).
Reuses the registered TT1 reader's statistics unchanged (tt1_read.py: pools, bootstrap weights, read_net, family_ci;
same draws, default_rng(20261122)) and applies the 5-seed rules of the FS1 block. Networks: A, B, Sb at seeds 403-407.
A network that failed the per-network gate (gate_fs.json) is missing; an arm statement needs >= 4 of 5 seeds that
passed AND agree; with fewer than 4 passing seeds for an arm every decision involving it is "not available (failed
platform gate)"; never read on one seed.
  python -I tt1_read_fs.py --scores DIR --nets DIR --gate gate_fs.json --out OUT.json [--mock]"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tt1common as T  # noqa: E402
import tt1_read as TR  # noqa: E402

ARMS = ("A", "B", "Sb")
SEEDS = (403, 404, 405, 406, 407)
NA = "not available (failed platform gate)"


def tau_cam_fs(netdir):
    ev = list(csv.DictReader(open(T.PN1T / "data" / "manifests" / "pn1_eval.csv")))
    z = np.load(pathlib.Path(netdir) / "scores_eval.npz")
    m = dict(zip(z["id"].tolist(), z["logit"].tolist()))
    th = []
    for f in (lambda r: r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R0" and r["strength"] == "",
              lambda r: r["fam"] == "af0" and r["rung"] == "photo" and r["strength"] == ""):
        v = np.sort(np.array([m[r["id"]] for r in ev if f(r)]))
        th.append(float(next(x for x in v if np.mean(v > x) <= 0.05)))
    return max(th)


def extra_reads(L, P):
    """printed reads registered in the FS1 block (review leads): F at cut-offs; geo/border flags; R_cam spread."""
    g = lambda pool: np.array([L[i] for i, _ in P[pool]])
    fam_src = {f: ([f] if f != "lfw_calfw" else ["lfw", "calfw"]) for f in T.FAMILIES}
    fu = {f: np.concatenate([g(f"U:{s}") for s in fam_src[f]]) for f in T.FAMILIES}
    cam = g("R_cam")
    return dict(Fbar_at={str(t): float(np.mean([np.mean(fu[f] > t) for f in T.FAMILIES])) for t in (0, -0.5, -1, -2)},
                geo_flag={gg: float(np.mean(g(f"Rgeo:{gg}") > 0)) for gg in ("g224", "g112")},
                border_flag={f: float(np.mean(g(f"Rcb:{f}") > 0)) for f in T.FAMILIES},
                R_cam_p05_p95=[float(np.percentile(cam, 5)), float(np.percentile(cam, 95))],
                unseen_family_median_minus_cam={f: float(np.median(fu[f]) - np.median(cam)) for f in T.FAMILIES})


def arm_rule(per_seed, value_fn, label_fn=None):
    """per_seed: {seed: per-network result or None (failed gate or required partner failed)}; value_fn -> bare
    per-seed verdict; agreement is counted on the bare verdict; label_fn(s, r) -> label appended if any seed has it."""
    ok = {s: r for s, r in per_seed.items() if r is not None}
    if len(ok) < 4:
        return dict(verdict=NA + f" ({5 - len(ok)} of 5 seeds unavailable)", seeds={})
    vs = {s: value_fn(s, r) for s, r in ok.items()}
    best = max(set(vs.values()), key=lambda v: list(vs.values()).count(v))
    n = list(vs.values()).count(best)
    v = best if n >= 4 else f"mixed ({n} of {len(ok)} seeds '{best}')"
    labels = sorted({label_fn(s, r) for s, r in ok.items() if label_fn and label_fn(s, r)})
    if labels:
        v += " [" + "; ".join(labels) + "]"
    return dict(verdict=v, seeds=vs, n_passing=len(ok))


def verdicts(R):
    net = lambda a, s: R.get(f"PN1_{a}_s{s}")
    V = {}

    def h1(a):
        need = 4 if a == "A" else 2

        def f(s, r):
            fails = [x for x in T.FAMILIES if max(0.0, r["fam_flag_ci"][x][0]) > 0.05]
            if all(r["fam_flag_ci"][x][1] <= 0.10 for x in T.FAMILIES):
                return "transfers (all upper <= 10%)"
            return "fails as predicted" if len(fails) >= need else "not as predicted"
        lab = lambda s, r: "uninformative: R_cam share > 5% on a seed" if r["pools"]["R_cam"]["flag"] > 0.05 else None
        return arm_rule({s: net(a, s) for s in SEEDS}, f, lab)
    V["TT-H1"] = {a: h1(a) for a in ARMS}

    def h2(s, r):
        a90 = sum(r["auc"][x]["a"]["auc"] >= 0.90 for x in T.SOURCES)
        a75 = sum(r["auc"][x]["a"]["auc"] >= 0.75 for x in T.SOURCES)
        return "supported" if a90 >= 6 else ("falsified" if a75 <= 3 else "not supported as predicted")
    V["TT-H2"] = {a: arm_rule({s: net(a, s) for s in SEEDS}, h2) for a in ARMS}

    def h3(s, r):
        fs = {f: ([f] if f != "lfw_calfw" else ["lfw", "calfw"]) for f in T.FAMILIES}
        fa = {f: np.mean([r["auc"][x]["a"]["auc"] for x in fs[f]]) for f in T.FAMILIES}
        fc = {f: np.mean([r["auc"][x]["c"]["auc"] for x in fs[f]]) for f in T.FAMILIES}
        e = {f: r["auc"]["e_cam_border"][f]["auc"] for f in T.FAMILIES}
        d = r["auc"]["d_ffhq_border"]["auc"]
        if sum(fc[f] <= fa[f] - 0.10 for f in T.FAMILIES) >= 4 and sum(e[f] >= 0.65 for f in T.FAMILIES) >= 4 and d >= 0.65:
            return "border material"
        if sum(abs(fc[f] - fa[f]) <= 0.03 for f in T.FAMILIES) >= 6 and sum(e[f] <= 0.55 for f in T.FAMILIES) >= 6 and d <= 0.55:
            return "border not material"
        return "inconclusive"
    V["TT-H3"] = {a: arm_rule({s: net(a, s) for s in SEEDS}, h3) for a in ARMS}
    packs = ["lfw", "calfw", "cfp_ff", "agedb_30"]

    def h4(a):
        def f(s, r):
            ok = [p for p in packs if not r["r4"][p]["floor_tied"]]
            if len(ok) < 3:
                return "not read (floor)"
            if sum(r["r4"][p]["rho"] >= 0 for p in ok) >= 3:
                return "falsified"
            if a == "A":
                return "supported" if sum(r["r4"][p]["rho"] <= -0.15 for p in ok) >= 3 else "not as predicted"
            ra = net("A", s)
            return "supported (|rho| below A's)" if sum(abs(r["r4"][p]["rho"]) < abs(ra["r4"][p]["rho"]) for p in packs) >= 3 else "not as predicted"
        need_a = a != "A"
        return arm_rule({s: (net(a, s) if (not need_a or net("A", s) is not None) else None) for s in SEEDS}, f)
    V["TT-H4"] = {a: h4(a) for a in ARMS}

    def h5(s, r):
        g = {x: r["auc"][x]["g"] for x in T.SOURCES}
        if sum(g[x]["auc"] >= 0.75 and g[x]["ci"][0] > 0.65 for x in T.SOURCES) >= 2:
            return "source matters beyond geometry"
        if sum(0.40 <= g[x]["auc"] <= 0.60 for x in T.SOURCES) >= 6:
            return "geometry explains"
        return "inconclusive"
    weak = lambda s, r: "geo reference weak" if any(r["auc"]["f_geo"][gg]["auc"] <= 0.55 for gg in ("g224", "g112")) else None
    V["TT-H5"] = {a: arm_rule({s: net(a, s) for s in SEEDS}, h5, weak) for a in ARMS}
    h6 = {}
    for x, y in (("B", "A"), ("Sb", "A"), ("Sb", "B"), ("B", "Sb")):
        per = {}
        for s in SEEDS:
            rx, ry = net(x, s), net(y, s)
            if rx is None or ry is None:
                per[s] = None
                continue
            d = rx["r5"]["Fbar"] - ry["r5"]["Fbar"]
            ci = TR.interval(d, [p["Fbar"] - q["Fbar"] for p, q in zip(rx["r5"]["_draws"], ry["r5"]["_draws"])])
            per[s] = dict(dFbar=d, ci=ci, lower=bool(d <= -0.03 and ci[1] < 0))
        ok = {s: v for s, v in per.items() if v is not None}
        if len(ok) < 4:
            sent = NA
        else:
            sent = (f"{x} has lower genuine flag rates than {y} on seeds 403-407" if sum(v["lower"] for v in ok.values()) >= 4
                    else "not distinguished on seeds 403-407")
        dv = [v["dFbar"] for v in ok.values()]
        h6[f"{x}-{y}"] = dict(seeds={str(k): v for k, v in per.items()}, sentence=sent,
                              across_seeds=dict(n=len(dv), mean=float(np.mean(dv)) if dv else None,
                                                sd=float(np.std(dv, ddof=1)) if len(dv) > 1 else None,
                                                n_negative=int(sum(d < 0 for d in dv))))
    V["TT-H6"] = dict(pairs=h6, label="descriptive; intervals capture image sampling only; no arm, seed or threshold is chosen "
                                      "from TT1; the -0.03 bar equals the size of the 401/402 B-A effect")
    summ = {}
    for x in ARMS:
        rs = [net(x, s) for s in SEEDS if net(x, s) is not None]
        summ[x] = {k: dict(n=len(rs), mean=float(np.mean([r["r5"][k] for r in rs])) if rs else None,
                           sd=float(np.std([r["r5"][k] for r in rs], ddof=1)) if len(rs) > 1 else None)
                   for k in ("Fbar", "Fmax", "S_F", "Abar")}
    V["across_seed_summary"] = summ
    return V


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--nets", required=True)
    ap.add_argument("--gate", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    P, tt = TR.load_pools()
    W = TR.boot_weights(P, np.random.default_rng(TR.SEED))
    ap_mock_drop = {"PN1_Sb_s405", "PN1_A_s404", "PN1_A_s406"}     # mock: A missing on 2 seeds, Sb on 1
    passed = set(json.load(open(a.gate))["passed"]) if not a.mock else {f"PN1_{x}_s{s}" for x in ARMS for s in SEEDS} - ap_mock_drop
    R = {}
    for x in ARMS:
        for s in SEEDS:
            n = f"PN1_{x}_s{s}"
            if n not in passed:
                continue
            if a.mock:
                ids = [i for v in P.values() for i, _ in v]
                mr = np.random.default_rng(s * 10 + ARMS.index(x))
                L = {i: float(np.clip(mr.normal(-3.0, 1.2), -3.87, 3.87)) for i in ids}
                for i, _ in P["M_ffhq"]:
                    L[i] = float(np.clip(mr.normal(3.0, 1.0), -3.87, 3.87))
                floor, tc = -3.87, -3.6
            else:
                L = {}
                for fam in ("gate", "tt1"):
                    z = np.load(pathlib.Path(a.scores) / f"{n}__{fam}.npz")
                    L.update(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
                floor = TR.head_floor(pathlib.Path(a.nets) / n)
                tc = tau_cam_fs(pathlib.Path(a.nets) / n)
            r = TR.read_net(L, P, W, tt, floor, tc)
            TR.family_ci(r, P, W, L)
            r["printed"] = extra_reads(L, P)
            corr = {}
            for f_ in T.FAMILIES:
                srcs = [f_] if f_ != "lfw_calfw" else ["lfw", "calfw"]
                xx = np.concatenate([np.array([L[i] for i, _ in P[f"U:{q}"]]) > 0 for q in srcs])
                lo, hi = r["fam_flag_ci"][f_]
                corr[f_] = dict(boot_ci_clipped=[max(0.0, lo), hi], cp=TR.cp(int(xx.sum()), len(xx)), zero_event=bool(xx.sum() == 0))
            r["family_flag_corrected"] = corr
            if not a.mock:
                zs = np.load(pathlib.Path(a.nets) / n / "scores_eval.npz")
                ms = dict(zip(zs["id"].tolist(), zs["logit"].astype(float).tolist()))
                dd = np.array([L[i] - ms[i] for i, _ in P["R_cam"]])
                r["tf32_split_R_cam"] = dict(max_abs=float(np.abs(dd).max()), median_abs=float(np.median(np.abs(dd))),
                                             flips=int(sum((L[i] > 0) != (ms[i] > 0) for i, _ in P["R_cam"])))
            r["tau_cam_label"] = "saturated band; from the stored TF32-on scores, applied to TF32-off logits (printed only)"
            R[n] = r
            print("read", n, flush=True)
    V = verdicts(R)
    for r in R.values():
        r["r5"].pop("_draws", None)
    res = dict(registration="TT1 FS1 block (prereg_fs1_block.md)", mock=a.mock, gate_passed=sorted(passed),
               nets=R, verdicts=V)
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(V, indent=1, default=float)[:4000])


if __name__ == "__main__":
    main()
