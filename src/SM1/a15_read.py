"""SM1 amendment A15 reader (registered 12 Nov, d84a1c2): saved ViT-B/16 a, e, f on development data only.

Input: /mnt/t7/smad_next/SM1/results_rented/dev/SM1D_<arm>_s<seed>.tar (sha256 checked, extracted next to it):
<T>/scores_audit.npz (ids of sm1_dev_eval.csv; logit = log(p / (1 - p)) of the no-TTA score) and <T>/check.json.
Bootstrap unit: the host (person id; X20 and REC20 keyed by host; AR1 rows by p1), B = 10,000, seed 20261111, the same
draws for every fit; 2-seed means of the per-draw values.
- H-new-A: AUC(X20 > AR1 R0) "native" and AUC(X20 > REC20) "history-matched". Prediction: e's history-matched AUC
  <= 0.65 and a's AUC drops >= 0.15 native -> history-matched; falsified if e's history-matched AUC >= 0.80;
  0.65 to 0.80 undecided.
- H-new-E (decided on e only): mean over the 200 hosts of logit(softened R0) - logit(R0), per strength; supported if
  < 0 with the interval below 0 at both strengths; falsified if >= 0 with the interval above 0 at both; else undecided.
- H-new-B AUC part: paired AUC(softened R0 > R0), per strength; e - f difference; prediction |diff| < 0.05; falsified
  if >= 0.10 with an interval excluding 0.

  python3 -I a15_read.py -> RES/a15_read.json
"""
import csv
import json
import pathlib
import sys
import tarfile
import hashlib

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
    host = {}
    for r in rows:
        host[r["id"]] = r["variant"]                          # X20/REC20/SAME20: host; AR1 and AF0 rows: p1
    hosts = sorted({r["variant"] for r in rows if r["set"] == "devdiff"})
    hpos = {h: i for i, h in enumerate(hosts)}
    C = np.random.default_rng(K.SEED).multinomial(len(hosts), np.full(len(hosts), 1 / len(hosts)), size=B).astype(float)
    W = lambda ids: C[:, [hpos[host[i]] for i in ids]]  # noqa: E731
    sel = lambda f: [r["id"] for r in rows if r["family"] == f]  # noqa: E731
    X, REC = sel("X20"), sel("REC20")
    R0 = sel("ar1:frgcferet:none:R0")
    assert all(host[i] in hpos for i in X + REC + R0)
    soft = {st: [r for r in rows if r["family"] == f"R0_soft_{st}"] for st in ("amsl112", "fm61")}
    res, per = {}, {}
    for f in sorted(D.glob("SM1D_*.tar")):
        h = hashlib.sha256(open(f, "rb").read()).hexdigest()
        assert h == open(str(f) + ".sha256").read().split()[0], f
        T = f.stem
        if not (D / T).exists():
            with tarfile.open(f) as t:
                t.extractall(D)
        chk = json.load(open(D / T / "check.json"))
        assert chk["passed"], T
        z = np.load(D / T / "scores_audit.npz")
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        zi = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
        g = lambda ids: np.array([zi[i] for i in ids])  # noqa: E731
        m = {}
        for name, neg in (("native_X20_vs_R0", R0), ("histmatched_X20_vs_REC20", REC)):
            pt = float(S.wauc(g(X), g(neg), np.ones((1, len(X))), np.ones((1, len(neg))))[0])
            m[name] = (pt, S.wauc(g(X), g(neg), W(X), W(neg)))
        for st, rs in soft.items():
            sids = [r["id"] for r in rs]
            base = [r["src_id"] for r in rs]
            inc = g(sids) - g(base)
            Wh = W(sids)
            m[f"incE_{st}"] = (float(inc.mean()), (Wh * inc).sum(1) / Wh.sum(1))
            d = g(sids)[:, None] - g(base)[None, :]
            m[f"pairedAUC_{st}"] = (float(((d > 0) + 0.5 * (d == 0)).mean()),
                                    S.wauc(g(sids), g(base), Wh, W(base)))
        arm = T.split("_")[1]
        per.setdefault(arm, []).append((T, m, chk["max_abs_score_diff"]))
    out = {}
    for arm, lst in per.items():
        o = dict(fits=[t for t, _, _ in lst], check_max_abs=[c for _, _, c in lst])
        for k in lst[0][1]:
            pts = [m[k][0] for _, m, _ in lst]
            dr = np.mean([m[k][1] for _, m, _ in lst], 0)
            o[k] = dict(mean=round(float(np.mean(pts)), 4), seeds=[round(x, 4) for x in pts],
                        ci=[round(x, 4) for x in S.ci(dr)], _d=dr)
        out[arm] = o
    v = {}
    if "e" in out:
        e = out["e"]["histmatched_X20_vs_REC20"]["mean"]
        v["H-new-A"] = dict(e_histmatched=e, a_drop=round(out["a"]["native_X20_vs_R0"]["mean"] -
                                                          out["a"]["histmatched_X20_vs_REC20"]["mean"], 4) if "a" in out else None,
                            verdict="falsified" if e >= 0.80 else ("supported" if e <= 0.65 and "a" in out and
                                     out["a"]["native_X20_vs_R0"]["mean"] - out["a"]["histmatched_X20_vs_REC20"]["mean"] >= 0.15
                                     else "undecided"))
        cis = [out["e"][f"incE_{st}"]["ci"] for st in ("amsl112", "fm61")]
        v["H-new-E"] = dict(e_ci=cis, verdict="supported" if all(c[1] < 0 for c in cis) else
                            ("falsified" if all(c[0] > 0 for c in cis) else "undecided"))
    if "e" in out and "f" in out:
        hb = {}
        for st in ("amsl112", "fm61"):
            d = out["e"][f"pairedAUC_{st}"]["_d"] - out["f"][f"pairedAUC_{st}"]["_d"]
            hb[st] = dict(diff=round(out["e"][f"pairedAUC_{st}"]["mean"] - out["f"][f"pairedAUC_{st}"]["mean"], 4),
                          ci=[round(x, 4) for x in S.ci(d)])
        v["H-new-B_auc"] = dict(e_minus_f=hb, verdict="falsified" if any(abs(x["diff"]) >= 0.10 and (x["ci"][0] > 0 or
                                x["ci"][1] < 0) for x in hb.values()) else ("supported" if all(abs(x["diff"]) < 0.05
                                for x in hb.values()) else "undecided"))
    for o in out.values():
        for k in list(o):
            if isinstance(o[k], dict):
                o[k].pop("_d", None)
    out["verdicts"] = v
    json.dump(out, open(K.RES / "a15_read.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
