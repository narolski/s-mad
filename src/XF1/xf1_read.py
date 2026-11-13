"""XF1 registered reads (prereg.md section 5); development data only (FFHQ MS1 hold-out frames, DATA D12a and D1d).
Inputs: /mnt/t7/smad_next/XF1/xf1_rows.csv (pinned) and the Athena result tar XF1_scores.tar (sha256 checked) with
<net>__gate.json and, for gate-passed networks only, <net>__xf1.npz.
Read 1 (blend at matched rendering): AUC of FM(H,B) against FM(H,H) per network; paired gains g_s = AUC(Sb_s) - AUC(X_s),
  X in {B, A}; joint bootstrap over the 12 components of the host-partner pairing (2,000 draws, rng 20261203, the same
  draws for every network); "present" if the seed-mean gain is >= +0.03 AND its lower 95% bound > 0 AND g_s > 0 on >= 4
  of 5 seeds; "absent" if the upper bound < +0.03; otherwise "inconclusive"; fewer than 4 seeds with both networks
  gate-passed: "not read".
Read 2 (render reaction): AUC of FM(H,H) against H per network, seed-mean per arm with the same bootstrap; label
  "no render reaction" if the 95% interval lies inside [0.40, 0.60], "render reaction" if the lower bound > 0.60,
  "reversed render reaction" if the upper bound < 0.40, otherwise "unresolved". Own-rule (logit > 0) flag rates on H,
  FM(H,H), FM(H,B) per network. FM(H,B) against H printed.
Read 3: each network beside the adversary's floors on these rows (check.exceeds, all-cue and nuisance) for contrasts
  xf1_FMHB_vs_FMHH and xf1_FMHH_vs_H when the adversary's pinned files exist; else "floor not delivered".
  python -I xf1_read.py --out xf1_read.json [--mock]"""
import argparse, csv, hashlib, io, json, pathlib, sys, tarfile
import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
ROWS = pathlib.Path("/mnt/t7/smad_next/XF1/xf1_rows.csv")
ROWS_SHA = "ef4adf5ba22847f04ccf40d054fcda5b05b1546be08dde04b277dd2b5266e317"
TAR = pathlib.Path("/mnt/t7/smad_next/XF1/results/XF1_scores.tar")
ARMS, SEEDS = ("A", "B", "Sb"), tuple(range(403, 408))
B = 2000


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def auc(pos, neg):
    s = np.concatenate([pos, neg]); y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    o = np.argsort(s, kind="mergesort"); r = np.empty(len(s)); xs = s[o]; i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and xs[j + 1] == xs[i]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    p = len(pos)
    return float((r[y == 1].sum() - p * (p + 1) / 2) / (p * len(neg)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    assert sha(ROWS) == ROWS_SHA
    rows = list(csv.DictReader(open(ROWS)))
    hosts = sorted({r["host"] for r in rows}); comp = {r["host"]: int(r["cell"]) for r in rows}
    rid = {(r["klass"], r["host"]): r["id"] for r in rows}
    assert len(hosts) == 299 and len(rid) == 897
    L, gate = {}, {}
    if a.mock:
        for arm in ARMS:
            for s in SEEDS:
                rr = np.random.default_rng(s * 7 + ARMS.index(arm))
                n = f"PN1_{arm}_s{s}"; L[n] = {r["id"]: float(rr.normal()) for r in rows}; gate[n] = dict(byte_identical=True, mock=True)
    else:
        want = (TAR.parent / "XF1_scores.tar.sha256").read_text().split()[0]; assert sha(TAR) == want
        with tarfile.open(TAR) as tf:
            for arm in ARMS:
                for s in SEEDS:
                    n = f"PN1_{arm}_s{s}"
                    gate[n] = json.load(tf.extractfile(f"XF1_scores/scores/{n}__gate.json"))
                    if gate[n]["byte_identical"]:
                        z = np.load(io.BytesIO(tf.extractfile(f"XF1_scores/scores/{n}__xf1.npz").read()))
                        L[n] = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
                        assert set(L[n]) == {r["id"] for r in rows}
    ug = sorted(set(comp.values())); members = {k: [h for h in hosts if comp[h] == k] for k in ug}
    rng = np.random.default_rng(20261203)
    draws = [np.concatenate([members[k] for k in rng.choice(ug, len(ug), replace=True)]) for _ in range(B)]

    def stat(n, pos, neg, hs):
        return auc(np.array([L[n][rid[(pos, h)]] for h in hs]), np.array([L[n][rid[(neg, h)]] for h in hs]))

    out = dict(mock=a.mock, n_hosts=len(hosts), n_components=len(ug), component_sizes=sorted(len(v) for v in members.values()),
               gate={n: gate[n] for n in sorted(gate)}, gate_passed=sorted(L))
    per = {}
    for n in sorted(L):
        v = np.array([L[n][rid[(k, h)]] for k in ("H", "FMHH", "FMHB") for h in hosts]).reshape(3, -1)
        per[n] = dict(FMHB_vs_FMHH=stat(n, "FMHB", "FMHH", hosts), FMHH_vs_H=stat(n, "FMHH", "H", hosts),
                      FMHB_vs_H=stat(n, "FMHB", "H", hosts), flag_H=float((v[0] > 0).mean()), flag_FMHH=float((v[1] > 0).mean()),
                      flag_FMHB=float((v[2] > 0).mean()), median_logit=dict(H=float(np.median(v[0])), FMHH=float(np.median(v[1])), FMHB=float(np.median(v[2]))))
    out["per_network"] = per
    boot = {}   # (net, contrast) -> array over draws
    for n in L:
        for c, (p, q) in (("FMHB_vs_FMHH", ("FMHB", "FMHH")), ("FMHH_vs_H", ("FMHH", "H"))):
            boot[(n, c)] = np.array([stat(n, p, q, d) for d in draws])
    arms = {}
    for arm in ARMS:
        ns = [f"PN1_{arm}_s{s}" for s in SEEDS if f"PN1_{arm}_s{s}" in L]
        if not ns:
            arms[arm] = "not read (no gate-passed network)"; continue
        r = dict(n_seeds=len(ns))
        for c in ("FMHB_vs_FMHH", "FMHH_vs_H"):
            m = float(np.mean([per[n][c] for n in ns])); bb = np.mean([boot[(n, c)] for n in ns], axis=0)
            r[c] = dict(seed_mean=m, ci=[float(np.percentile(bb, 2.5)), float(np.percentile(bb, 97.5))], per_seed={n[-4:]: per[n][c] for n in ns})
        lo, hi = r["FMHH_vs_H"]["ci"]
        r["render_label"] = ("no render reaction" if lo >= 0.40 and hi <= 0.60 else "render reaction" if lo > 0.60
                             else "reversed render reaction" if hi < 0.40 else "unresolved")
        for k in ("flag_H", "flag_FMHH", "flag_FMHB"):
            r[k] = [float(min(per[n][k] for n in ns)), float(max(per[n][k] for n in ns))]
        arms[arm] = r
    out["arms"] = arms
    gains = {}
    for X in ("B", "A"):
        ss = [s for s in SEEDS if f"PN1_Sb_s{s}" in L and f"PN1_{X}_s{s}" in L]
        if len(ss) < 4:
            gains[f"Sb_minus_{X}"] = dict(verdict="not read", n_seeds=len(ss)); continue
        g = [per[f"PN1_Sb_s{s}"]["FMHB_vs_FMHH"] - per[f"PN1_{X}_s{s}"]["FMHB_vs_FMHH"] for s in ss]
        gb = np.mean([boot[(f"PN1_Sb_s{s}", "FMHB_vs_FMHH")] - boot[(f"PN1_{X}_s{s}", "FMHB_vs_FMHH")] for s in ss], axis=0)
        m, lo, hi = float(np.mean(g)), float(np.percentile(gb, 2.5)), float(np.percentile(gb, 97.5))
        npos = int(sum(x > 0 for x in g))
        v = "present" if (m >= 0.03 and lo > 0 and npos >= 4) else "absent" if hi < 0.03 else "inconclusive"
        gains[f"Sb_minus_{X}"] = dict(verdict=v, seed_mean=m, ci=[lo, hi], per_seed={str(s): x for s, x in zip(ss, g)}, n_positive=npos, n_seeds=len(ss))
    out["read1_gains"] = gains
    adv = {}
    try:
        from check import exceeds
        for c, (p, q) in (("xf1_FMHB_vs_FMHH", ("FMHB", "FMHH")), ("xf1_FMHH_vs_H", ("FMHH", "H"))):
            if not (pathlib.Path("/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors") / f"{c}.json").exists():
                adv[c] = "floor not delivered"; continue
            adv[c] = {}
            for n in sorted(L):
                sc = {rid[(k, h)]: L[n][rid[(k, h)]] for k in (p, q) for h in hosts}
                adv[c][n] = {}
                for fl in ("all", "nuisance"):
                    try:
                        adv[c][n][fl] = exceeds(c, sc, floor=fl)
                    except AssertionError as ex:
                        adv[c][n][fl] = dict(error=str(ex))
            for arm in ARMS:
                ok = [adv[c][n]["all"].get("exceeds") for n in sorted(L) if n.startswith(f"PN1_{arm}_") and "exceeds" in adv[c][n]["all"]]
                adv[c][f"{arm}_exceeds_all_cue_learner_seeds"] = f"{sum(bool(x) for x in ok)} of {len(ok)}"
    except ImportError as ex:
        adv["error"] = str(ex)
    out["read3_adversary"] = adv
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(dict(gate_passed=len(L), gains=gains, arms={k: (v if isinstance(v, str) else {kk: vv for kk, vv in v.items() if kk != "per_seed"}) for k, v in arms.items()},
                          adv={c: (v if isinstance(v, str) else {k: x for k, x in v.items() if k.endswith("seeds")}) for c, v in adv.items()}), default=float)[:4000])


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()
