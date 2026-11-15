"""SM1 A15 follow-ups after the review of 12 Nov (REVIEW_SM1_12FITS_A15_20261112.md), on the existing A15 scores.

Post hoc (labelled so): SAME20 table (X20 / SAME20 over REC20, X20 over SAME20, a − e with host bootstrap); H-new-E
calibration (median per-host increment, share of hosts that decrease); H-new-B with the registered per-host paired
estimator (share of hosts whose softened copy scores above its own raw photo, ties one half; e − f).
Registered A17 (H-n3): Laplacian- and θ-stratified X20 over SAME20.

  python3 -I a17_read.py -> RES/a17_read.json
"""
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402

D = K.OUT / "results_rented/dev"
MAN = K.OUT / "dev_a14/sm1_dev_eval.csv"
B = 10000


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    rows = list(csv.DictReader(open(MAN)))
    host = {r["id"]: r["variant"] for r in rows}
    hosts = sorted({r["variant"] for r in rows if r["set"] == "devdiff"})
    hpos = {h: i for i, h in enumerate(hosts)}
    C = np.random.default_rng(K.SEED).multinomial(len(hosts), np.full(len(hosts), 1 / len(hosts)), size=B).astype(float)
    W = lambda ids: C[:, [hpos[host[i]] for i in ids]]  # noqa: E731
    fam = {}
    for r in rows:
        fam.setdefault(r["family"], []).append(r["id"])
    X, SA, REC = fam["X20"], fam["SAME20"], fam["REC20"]
    # strata for A17
    it = {}
    for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")):
        if r["key"] in ("X20", "SAME20"):
            it[f"dev:{r['key']}:{r['host']}"] = r
    th = {}
    for k in range(8):
        f = K.OUT.parent / "DG1/gen" / f"addon_s{k}" / f"out_addon_s{k}" / f"addon_s{k}" / "gen_rows.csv"
        for r in csv.DictReader(open(f)):
            th[(f"addon_s{k}", r["pool"], r["name"])] = float(r["theta_xT"]) if r["theta_xT"] not in ("", "nan") else np.nan
    lap = {i: float(it[i]["lapvar_box"]) for i in X + SA}
    tht = {}
    for i in X + SA:
        r = it[i]
        lst, rest = r["id"].split("/", 1)[0], r["id"]
        parts = rest.split("/")
        tht[i] = th.get((r["list"], parts[-2], parts[-1]), np.nan)
    assert np.isfinite(list(tht.values())).all(), sum(~np.isfinite(list(tht.values())))
    strata = {}
    for nm, v in (("lap", lap), ("theta", tht)):
        q = np.quantile(list(v.values()), [0.2, 0.4, 0.6, 0.8])
        strata[nm] = {i: int(np.searchsorted(q, v[i])) for i in X + SA}
    soft = {st: [r for r in rows if r["family"] == f"R0_soft_{st}"] for st in ("amsl112", "fm61")}
    per = {}
    for f in sorted(D.glob("SM1D_*.tar")):
        T = f.stem
        z = np.load(D / T / "scores_audit.npz")
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        zi = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
        g = lambda ids: np.array([zi[i] for i in ids])  # noqa: E731
        m = {}

        def auc(pos, neg):
            return (float(S.wauc(g(pos), g(neg), np.ones((1, len(pos))), np.ones((1, len(neg))))[0]),
                    S.wauc(g(pos), g(neg), W(pos), W(neg)))
        m["X20_over_REC20"] = auc(X, REC)
        m["SAME20_over_REC20"] = auc(SA, REC)
        m["X20_over_SAME20"] = auc(X, SA)
        for nm, sm in strata.items():
            pt, dr, wt = 0.0, 0.0, 0.0
            for k in range(5):
                xs = [i for i in X if sm[i] == k]
                ss = [i for i in SA if sm[i] == k]
                if not xs or not ss:
                    continue
                a_pt, a_dr = auc(xs, ss)
                w = len(xs) * len(ss)
                pt, dr, wt = pt + w * a_pt, dr + w * a_dr, wt + w
            m[f"X20_over_SAME20_{nm}strat"] = (pt / wt, dr / wt)
        for st, rs in soft.items():
            sids = [r["id"] for r in rs]
            base = [r["src_id"] for r in rs]
            inc = g(sids) - g(base)
            m[f"incE_median_{st}"] = (float(np.median(inc)), None)
            m[f"incE_share_down_{st}"] = (float((inc < 0).mean()), None)
            m[f"incE_share_abs_lt_0.01_{st}"] = (float((np.abs(inc) < 0.01).mean()), None)
            ind = (inc > 0) + 0.5 * (inc == 0)
            Wh = W(sids)
            m[f"pairedAUC_perhost_{st}"] = (float(ind.mean()), (Wh * ind).sum(1) / Wh.sum(1))
        per.setdefault(T.split("_")[1], []).append(m)
    out, vec = {}, {}
    for arm, lst in per.items():
        o = {}
        for k in lst[0]:
            pts = [m[k][0] for m in lst]
            dr = [m[k][1] for m in lst if m[k][1] is not None]
            o[k] = dict(mean=round(float(np.mean(pts)), 4), seeds=[round(x, 4) for x in pts])
            if dr:
                d = np.mean(dr, 0)
                o[k]["ci"] = [round(x, 4) for x in S.ci(d)]
                vec[(arm, k)] = d
        out[arm] = o
    diffs = {}
    for k in ("X20_over_REC20", "SAME20_over_REC20", "X20_over_SAME20", "X20_over_SAME20_lapstrat",
              "X20_over_SAME20_thetastrat"):
        d = vec[("a", k)] - vec[("e", k)]
        diffs[f"a-e:{k}"] = dict(diff=round(out["a"][k]["mean"] - out["e"][k]["mean"], 4), ci=[round(x, 4) for x in S.ci(d)])
    for st in ("amsl112", "fm61"):
        k = f"pairedAUC_perhost_{st}"
        d = vec[("e", k)] - vec[("f", k)]
        diffs[f"e-f:{k}"] = dict(diff=round(out["e"][k]["mean"] - out["f"][k]["mean"], 4), ci=[round(x, 4) for x in S.ci(d)])
    out["differences"] = diffs
    dl = diffs["a-e:X20_over_SAME20_lapstrat"]
    out["A17"] = dict(
        H_n3a=dict(a_minus_e=dl, verdict="supported" if abs(dl["diff"]) <= 0.03 else
                   ("falsified" if dl["ci"][0] > 0 or dl["ci"][1] < 0 else "undecided")),
        H_n3b=dict(theta_strat={a: out[a]["X20_over_SAME20_thetastrat"] for a in ("a", "e", "f")},
                   verdict="supported" if all(out[a]["X20_over_SAME20_thetastrat"]["mean"] <= 0.58 for a in "aef") else
                   ("falsified" if any(out[a]["X20_over_SAME20_thetastrat"]["ci"][0] > 0.58 for a in "aef") else "undecided")))
    hb = [diffs[f"e-f:pairedAUC_perhost_{st}"] for st in ("amsl112", "fm61")]
    out["H-new-B_registered_paired"] = dict(
        e_minus_f=hb, verdict="falsified" if any(abs(x["diff"]) >= 0.10 and (x["ci"][0] > 0 or x["ci"][1] < 0) for x in hb)
        else ("supported" if all(abs(x["diff"]) < 0.05 for x in hb) else "undecided"))
    out["note"] = "SAME20 table, H-new-E calibration, per-host H-new-B: post hoc re-reads; A17 registered (f6b06e2)"
    json.dump(out, open(K.RES / "a17_read.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
