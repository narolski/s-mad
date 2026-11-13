"""TT1 MEDS extension reader (prereg_meds_block.md). Per network: MEDS own-rule flag share (primary pool = aligned frames)
with person bootstrap (2,000 draws, default_rng(20261125); persons = MEDS subjects) and Clopper-Pearson; AUC of MEDS
against R_cam and against R_ffhq (references scored in the same job by rescore.py, the 3,417 TT1 fam-gate rows; R_cam
resampled by host, R_ffhq by image, MEDS by person); median logit and its shift from R_cam in logits and in u
(u = median M_ffhq - median R_cam); Spearman of logit with log Laplacian variance and with log enlargement inside MEDS;
flag shares by MEDS part (I/II), by native size group (240x240 vs larger) and on the secondary pool (aligned=0).
Verdicts for the deciding arms A, B, Sb at seeds 403-407 with the 4-of-5 rule; Sp printed only; networks that failed the
gate are missing and every read that needs them is "not available (failed platform gate)".
  python -I tt1_read_meds.py --scores DIR --nets DIR --gate gate_m.json --out OUT.json [--mock]"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np
from scipy.stats import beta, rankdata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import tt1common as T  # noqa: E402
import tt1_read as TR  # noqa: E402

NB = 2000
ARMS = ("A", "B", "Sb")
SEEDS = (403, 404, 405, 406, 407)
SP = [f"PN1_Sp_s{s}" for s in (403, 404, 405)]
NA = "not available (failed platform gate)"
MEDS = pathlib.Path("/mnt/t7/smad_next/TT1/meds/meds_manifest.csv")


def cp(k, n):
    return [0.0 if k == 0 else float(beta.ppf(.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(.975, k + 1, n - k))]


def boot_w(groups, rng):
    ps = sorted(set(groups)); idx = {p: i for i, p in enumerate(ps)}
    m = rng.integers(0, len(ps), size=(NB, len(ps)))
    c = np.stack([np.bincount(m[b], minlength=len(ps)) for b in range(NB)])
    return c[:, [idx[g] for g in groups]].astype(float)


def spear(x, y):
    return float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])


def main():
    ap = argparse.ArgumentParser()
    for k in ("scores", "nets", "gate", "out"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    meds = list(csv.DictReader(open(MEDS)))
    prim = [r for r in meds if r["aligned"] == "1"]
    sec = [r for r in meds if r["aligned"] != "1"]
    lst = [r for r in csv.DictReader(open(T.OUT / "tt1_score.csv")) if r["fam"] == "gate"]
    cam = [r for r in lst if r["rung"] == "R_cam"]; ffq = [r for r in lst if r["rung"] == "R_ffhq"]; mfq = [r for r in lst if r["rung"] == "M_ffhq"]
    rng = np.random.default_rng(20261125)
    Wm = boot_w([r["person"] for r in prim], rng)
    Wc = boot_w([r["host"] for r in cam], rng)
    Wf = boot_w([r["id"] for r in ffq], rng)
    passed = None if a.mock else set(json.load(open(a.gate))["passed"])
    names = [f"PN1_{x}_s{s}" for x in ARMS for s in SEEDS] + SP
    R = {}
    for n in names:
        if not a.mock and n not in passed:
            continue
        if a.mock:
            mr = np.random.default_rng(abs(hash(n)) % 2 ** 32)
            L = {r["id"]: float(np.clip(mr.normal(-3.0, 1.3), -3.87, 3.87)) for r in meds + lst}
            for r in mfq:
                L[r["id"]] = float(np.clip(mr.normal(3.0, 1.0), -3.87, 3.87))
        else:
            L = {}
            for fam in ("gate", "meds"):
                z = np.load(pathlib.Path(a.scores) / f"{n}__{fam}.npz")
                L.update(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
        xm = np.array([L[r["id"]] for r in prim]); xc = np.array([L[r["id"]] for r in cam]); xf = np.array([L[r["id"]] for r in ffq])
        xmf = np.array([L[r["id"]] for r in mfq])
        f = (xm > 0).astype(float)
        bf = (Wm @ f) / Wm.sum(1)
        lo, hi = np.percentile(bf, [2.5, 97.5])
        au_c = TR.wauc(xm, xc); au_f = TR.wauc(xm, xf)
        dc = [TR.wauc(xm, xc, Wm[b], Wc[b]) for b in range(NB)]
        df = [TR.wauc(xm, xf, Wm[b], Wf[b]) for b in range(NB)]
        u = float(np.median(xmf) - np.median(xc))
        lap = np.log(np.array([float(r["lap_var"]) for r in prim])); enl = np.log(np.array([float(r["enlarge"]) for r in prim]))
        part = {p: float(np.mean([L[r["id"]] > 0 for r in prim if r["part"] == p])) for p in ("MEDS-I", "MEDS-II")}
        small = [r for r in prim if r["width"] == "240" and r["height"] == "240"]
        R[n] = dict(n_primary=len(prim), persons=len({r["person"] for r in prim}), flag=float(f.mean()), flag_boot=[max(0.0, float(lo)), float(hi)],
                    flag_cp=cp(int(f.sum()), len(f)), flag_secondary=float(np.mean([L[r["id"]] > 0 for r in sec])) if sec else None,
                    flag_R_cam=float((xc > 0).mean()), flag_R_ffhq=float((xf > 0).mean()),
                    auc_vs_R_cam=au_c, auc_vs_R_cam_ci=[float(np.percentile(dc, 2.5)), float(np.percentile(dc, 97.5))],
                    auc_vs_R_ffhq=au_f, auc_vs_R_ffhq_ci=[float(np.percentile(df, 2.5)), float(np.percentile(df, 97.5))],
                    median_logit=float(np.median(xm)), shift_from_R_cam=float(np.median(xm) - np.median(xc)), u=u,
                    shift_in_u=float((np.median(xm) - np.median(xc)) / u) if u else None,
                    rho_logit_loglap=spear(xm, lap), rho_logit_logenlarge=spear(xm, enl),
                    flag_by_part=part, flag_240px=float(np.mean([L[r["id"]] > 0 for r in small])) if small else None, n_240px=len(small),
                    _bf=bf.tolist())
        print("read", n, flush=True)
    net = lambda x, s: R.get(f"PN1_{x}_s{s}")

    def arm(fn, x):
        ok = {s: net(x, s) for s in SEEDS if net(x, s) is not None}
        if len(ok) < 4:
            return dict(verdict=NA + f" ({5 - len(ok)} of 5 seeds unavailable)")
        vs = {s: fn(r) for s, r in ok.items()}
        best = max(set(vs.values()), key=list(vs.values()).count); k = list(vs.values()).count(best)
        return dict(verdict=best if k >= 4 else f"mixed ({k} of {len(ok)} seeds '{best}')", seeds=vs)
    m1 = lambda r: "fails" if r["flag_boot"][0] > 0.05 else ("transfers" if r["flag_boot"][1] <= 0.10 else "neither")
    m2 = lambda r: "displaced" if r["auc_vs_R_cam"] >= 0.90 else ("not displaced" if r["auc_vs_R_cam"] <= 0.75 else "between")
    V = {"TT-M1": {x: arm(m1, x) for x in ARMS}, "TT-M2": {x: arm(m2, x) for x in ARMS}}
    pairs = {}
    for x, y in (("B", "A"), ("Sb", "A"), ("Sb", "B"), ("B", "Sb")):
        per = {}
        for s in SEEDS:
            rx, ry = net(x, s), net(y, s)
            if rx is None or ry is None:
                per[str(s)] = None; continue
            d = rx["flag"] - ry["flag"]; dd = np.array(rx["_bf"]) - np.array(ry["_bf"])
            ci = [float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))]
            per[str(s)] = dict(d=d, ci=ci, lower=bool(d <= -0.03 and ci[1] < 0))
        ok = [v for v in per.values() if v]
        sent = NA if len(ok) < 4 else (f"{x} has lower MEDS flag rates than {y} on seeds 403-407" if sum(v["lower"] for v in ok) >= 4 else "not distinguished on seeds 403-407")
        dv = [v["d"] for v in ok]
        pairs[f"{x}-{y}"] = dict(seeds=per, sentence=sent, mean=float(np.mean(dv)) if dv else None,
                                 sd=float(np.std(dv, ddof=1)) if len(dv) > 1 else None, n_negative=int(sum(d < 0 for d in dv)))
    V["TT-M3"] = dict(pairs=pairs, label="descriptive; intervals capture image sampling only")
    for r in R.values():
        r.pop("_bf")
    out = dict(registration="TT1-M (prereg_meds_block.md)", mock=a.mock, gate_passed=sorted(passed) if passed else None, nets=R, verdicts=V)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(V, indent=1, default=float)[:3000])


if __name__ == "__main__":
    main()
