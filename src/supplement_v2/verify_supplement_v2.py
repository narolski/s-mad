"""Verify every number printed in the rewritten supplement (tables and figures).

    python src/supplement_v2/verify_supplement_v2.py [--out WORKTREE]

1. Re-evaluates every registered value (printed_values*.json, written by make_tables.py / make_figures.py) with an
   implementation of EER, AUC and fixed-threshold rates written independently of the release metrics, re-reading
   score files, read records and training lists, and compares at the printed rounding (|diff| < 0.6 units of the last
   printed digit).
2. Checks that each printed string occurs in its generated table file (tables only).
3. Cross-checks: values also printed by the release reproducer reference (FRLL-Morphs grid, Sb per seed on MAD22,
   comparator retrains) must agree; the sealed-read record's per-seed and release EERs must equal the score files.
4. Runs the three release reproducers (Table 1, 1,556 supplement cells, morph-free values); each must exit 0.
Prints a per-table pass/fail with the number of checked cells; exits 1 on any failure."""
import collections, csv, json, os, subprocess, sys
import numpy as np
from scipy.stats import rankdata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import derive as D  # data loaders only (npz / tar / csv / json readers); metrics below are independent  # noqa: E402

OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "/home/narolski/work/smad-cvpr-2027-supp2"
PY = sys.executable
TABFILE = {"A1": "supp2_sources", "B2": "supp2_render", "B3": "supp2_blend", "C1": "supp2_arms", "C2": "supp2_count_balanced",
           "C3": "supp2_ablation", "D1": "supp2_mad22_seeds", "D2": "supp2_fragility", "D3": "supp2_comparators",
           "D4": "supp2_selfmad", "D5": "supp2_frll_compact", "D6": "supp2_frll_full", "E1": "supp2_transfer",
           "F1": "supp2_morph_free", "G1": "supp2_hparams"}


# ---------------- independent metrics ----------------
def my_eer(pos, neg):
    """interpolated EER: ROC over every distinct threshold (ties move FPR and TPR together), crossing FPR = 1 - TPR."""
    s = np.r_[pos, neg]
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    thr = np.unique(s)[::-1]
    tpr = np.r_[0, [(pos >= t).mean() for t in thr]] if len(thr) < 3000 else None
    if tpr is None:  # vectorised for large sets
        ps, ns = np.sort(pos), np.sort(neg)
        tpr = np.r_[0, 1 - np.searchsorted(ps, thr, "left") / len(ps)]
        fpr = np.r_[0, 1 - np.searchsorted(ns, thr, "left") / len(ns)]
    else:
        fpr = np.r_[0, [(neg >= t).mean() for t in thr]]
    fnr = 1 - tpr
    d = fpr - fnr
    k = int(np.argmax(d >= 0))
    if d[k] == d[k - 1]:
        return 100 * fpr[k - 1]
    w = -d[k - 1] / (d[k] - d[k - 1])
    return 100 * (fpr[k - 1] + w * (fpr[k] - fpr[k - 1]))


def my_auc(pos, neg):
    r = rankdata(np.r_[pos, neg])
    return (r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def my_mf_eer(bona, morph):
    best, val = 9, None
    for t in np.unique(np.r_[bona, morph]):
        fpr, fnr = (bona >= t).mean(), (morph < t).mean()
        if abs(fnr - fpr) < best:
            best, val = abs(fnr - fpr), (fnr + fpr) / 2
    return 100 * val


def sel_sup(m, s, v, p):
    M, S, V, P, L = D.sup()
    return L[(M == m) & (S == s) & (V == v) & (P == p)]


def ev(spec):
    k = spec[0]
    if k == "t1eer":
        _, m, s, f, form = spec
        M, S, P, L = D.t1()
        x = (M == m) & (S == s)
        return my_eer(L[x & (P == "morph_" + f)], L[x & (P == ("genuine_raw" if form == "S" else "genuine_history_" + f))])
    if k == "t1count":
        M, S, P, L = D.t1()
        return float(((M == spec[1]) & (S == spec[2]) & (P == spec[3])).sum())
    if k == "supeer":
        return my_eer(sel_sup(*spec[1:4], spec[4]), sel_sup(*spec[1:4], spec[5]))
    if k == "supauc":
        return my_auc(sel_sup(*spec[1:4], spec[4]), sel_sup(*spec[1:4], spec[5]))
    if k == "suprate":
        _, w, m, s, v, pos, neg = spec
        return 100 * ((sel_sup(m, s, v, pos) <= 0).mean() if w == "apcer" else (sel_sup(m, s, v, neg) > 0).mean())
    if k == "supcount":
        return float(len(sel_sup(*spec[1:])))
    if k == "mfeer":
        _, m, s, st, fam, form = spec
        M, S, P, X = D.mf()
        x = (M == m) & (S == s)
        neg = f"{st}:genuine_raw" if form == "native" else f"{st}:{fam}:genuine_history"
        return my_mf_eer(X[x & (P == neg)], X[x & (P == f"{st}:{fam}:morph")])
    if k == "json":
        o = json.load(open(spec[1]))
        for key in spec[2]:
            o = o[key]
        return float(o) * spec[3]
    if k == "tt1flag":
        L = D.tar_scores(D.TT1_TAR, "__tt1.npz")[spec[1]]
        ids = [r["id"] for r in csv.DictReader(open(D.TT1_MANIFEST)) if r["role"] == "tt1" and r["cell"] == spec[2]
               and r["strength"] == "primary" and not r["rung"].startswith("R_")]
        return 100 * sum(L[i] > 0 for i in ids) / len(ids)
    if k == "tt1n":
        return float(sum(1 for r in csv.DictReader(open(D.TT1_MANIFEST)) if r["role"] == "tt1" and r["cell"] == spec[1]
                         and r["strength"] == "primary" and not r["rung"].startswith("R_")))
    if k == "medsflag":
        L = D.tar_scores(D.MEDS_TAR, "__meds.npz")[spec[1]]
        ids = [r["id"] for r in csv.DictReader(open(D.MEDS_MANIFEST)) if r["cell"] == "primary"]
        return 100 * sum(L[i] > 0 for i in ids) / len(ids)
    if k == "medsn":
        return float(sum(1 for r in csv.DictReader(open(D.MEDS_MANIFEST)) if r["cell"] == spec[1]))
    if k == "manifest":
        rows = list(csv.DictReader(open(spec[1])))
        return float({"unique": len({r["path"] for r in rows}), "rows": len(rows), "pos": sum(r["label"] == "1" for r in rows)}[spec[2]])
    if k == "lines":
        return float(len(open(spec[1]).read().splitlines()))
    if k == "ref":
        return float(D.release_ref()[tuple(spec[1:])][0])
    if k in ("mean", "sd", "min", "max", "sum"):
        v = np.array([ev(x) for x in spec[1]])
        return float({"mean": v.mean(), "sd": v.std(ddof=1) if len(v) > 1 else 0.0, "min": v.min(), "max": v.max(), "sum": v.sum()}[k])
    if k == "sub":
        return ev(spec[1]) - ev(spec[2])
    if k == "mul":
        return ev(spec[1]) * spec[2]
    raise ValueError(spec)


def main():
    res = collections.OrderedDict()
    fails = []
    cache = {}
    items = json.load(open(os.path.join(HERE, "printed_values.json"))) + \
        [dict(x, table="Figures") for x in json.load(open(os.path.join(HERE, "printed_values_figures.json")))]
    tex = {t: open(os.path.join(OUT, "tables", f + ".tex")).read().replace("{,}", "") for t, f in TABFILE.items()}
    kinds = collections.Counter()
    for it in items:
        key = json.dumps(it["spec"])
        if key not in cache:
            cache[key] = ev(it["spec"])
        x, d, p = cache[key], it["digits"], it["printed"]
        ok = abs(x - float(p)) < 0.6 * 10 ** (-d)
        if it["table"] in tex:
            ok = ok and p.lstrip("+-") in tex[it["table"]]
        r = res.setdefault(it["table"], [0, 0])
        r[0] += 1
        kinds[it["kind"]] += 1
        if not ok:
            r[1] += 1
            fails.append((it["table"], it["spec"], p, x))
    # cross-checks against the release reference and the sealed-read record
    xc = [0, 0]
    REF = D.release_ref()
    for kk, (val, digits) in REF.items():
        if len(kk) != 4:
            continue
        t, f, name, stat = kk
        if t != "frll_grid" or stat not in ("eer", "auc", "own_apcer", "own_bpcer") or name == "Sb seeds":
            continue
        m, s = {"SelfMAD (release)": ("SelfMAD-RW", 0), "MADation B/16": ("MADation-B16-RW", 0), "MADation L/14": ("MADation-L14-RW", 0),
                "MixFaceNet-MAD": ("MixFaceNet-MAD-RW", 0)}.get(name, ("Sb", int(name[-3:]) if name.startswith("Sb s") else 0))
        v = "own" if m in ("Sb", "SelfMAD-RW") else ("v2" if f == "facemorpher" else "v1")
        pos, neg = sel_sup(m, s, v, "frll_morph_" + f), sel_sup(m, s, v, "frll_genuine_raw")
        got = {"eer": my_eer(pos, neg), "auc": my_auc(pos, neg), "own_apcer": 100 * (pos <= 0).mean(), "own_bpcer": 100 * (neg > 0).mean()}[stat]
        xc[0] += 1
        if abs(got - val) >= 0.6 * 10 ** (-digits):
            xc[1] += 1
            fails.append(("cross-check REF", (f, name, stat), val, got))
    fr = json.load(open(os.path.join(D.EXP, "FINAL_sealed-benchmark-read/final_read.json")))["cells"]
    relk = {"MADation-B16-RW": "madation_vitb16/v1", "MADation-L14-RW": "madation_vitl14/v1", "MixFaceNet-MAD-RW": "mixfacenet_mad_smdd/v1",
            "SelfMAD-RW": "selfmad_hrnet_w18/own_dgx"}
    for form in "SH":
        for f in D.FAMS:
            for s in range(403, 408):
                xc[0] += 1
                a, b = 100 * fr[form][f]["ours"][f"PN1_Sb_s{s}"]["eer"], ev(["t1eer", "Sb", s, f, form])
                if abs(a - b) > 1e-6:
                    xc[1] += 1; fails.append(("cross-check record", (form, f, s), a, b))
            for m, key in relk.items():
                xc[0] += 1
                a, b = 100 * fr[form][f]["releases"][key]["eer"], ev(["t1eer", m, 0, f, form])
                if abs(a - b) > 1e-6:
                    xc[1] += 1; fails.append(("cross-check record", (form, f, m), a, b))
    # release reproducers
    rep = []
    for script in ("evaluation/reproduce_table1.py", "evaluation/reproduce_supplement.py", "morph_free/reproduce_morph_free.py"):
        p = subprocess.run([PY, os.path.join(D.REL, script)], capture_output=True, text=True)
        rep.append((script, p.returncode, p.stdout.strip().splitlines()[-1]))
        if p.returncode:
            fails.append(("release reproducer", script, 0, p.returncode))
    print(f"{'table':10s} {'cells':>6s} {'failed':>7s}  result")
    for t, (n, nf) in res.items():
        print(f"{t:10s} {n:6d} {nf:7d}  {'PASS' if nf == 0 else 'FAIL'}")
    print(f"{'cross':10s} {xc[0]:6d} {xc[1]:7d}  {'PASS' if xc[1] == 0 else 'FAIL'}  (release reference FRLL grid; sealed-read record vs score files)")
    for s, rc, last in rep:
        print(f"release {s}: exit {rc} ({last})")
    print(f"\n{sum(n for n, _ in res.values())} printed or plotted values re-derived; by source kind: {dict(kinds)}")
    for f in fails[:40]:
        print("FAIL", f)
    print("ALL PASS" if not fails else f"{len(fails)} FAILURES")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
