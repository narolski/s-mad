"""XF1 revision b registered reads (prereg.md "Revision b" and "Revision b2"); post-freeze development diagnostic,
registered after the sealed read; development data only (FFHQ MS1 hold-out frames; DATA D12a, D12b; XF1 face-only copies).
Inputs (all pinned): xf1b_rows.csv (1,495 rows: klass FMHB / WARP / H x form whole / face), xf1b_ring.csv (halo-ring share),
the adversary's xf1b_rows_scores.csv (stage-14 pins; learners on each arm's training list and floors, per form), and the
Athena result tar XF1_scores.tar (sha256 checked) with <net>__gate.json and, for gate-passed networks only, <net>__xf1.npz.
Contrast: FM(H,B) (klass FMHB, 1) against W (klass WARP, 0), selected by klass and form. Decision form: face-only.
Bootstrap: 64 cycle blocks (`block`), 2,000 draws, numpy default_rng(20261203), the same draws for every network, form
and comparison source. Sensitivities printed: leave-one-component-out range, host bootstrap.
Rules (face-only):
  gains Sb - B (primary) and Sb - A (secondary; A has no warp-only negatives): g_s = AUC(Sb_s) - AUC(X_s); "present" if the
  seed-mean >= +0.03 AND lower 95% bound > 0 AND g_s > 0 on >= 4 of 5 seeds; "absent" if the upper bound < +0.03; else
  "inconclusive"; fewer than 4 seeds with both networks gate-passed: "not read". Precedence: "not read", then
  "all arms at ceiling" (every gate-passed arm's lower bound >= 0.95), then "ceiling, not informative" (X's seed-mean
  >= 0.97), then the gain rule.
  floor: an arm whose 95% interval contains 0.50: "does not separate blend from warp".
  licences per arm: (a) interval contains 0.50 or lies below it: "this blend is not what the networks flag"; (b) lower
  bound > 0.50 and not (c): "consistent with blending and noise averaging; no evidence beyond low-level statistics";
  (c) the network exceeds its own training list's same-data learner (gbt, the gate's model) on the block bootstrap
  (2.5% bound of AUC_net - AUC_learner > 0) on >= 4 of 5 seeds: "beyond hand-made statistics trained on the same list".
  No outcome licenses "detects identity mixing".
Printed only: whole-frame form (surround-dominated), whole-minus-face per arm (blanking-shift control), terciles of
exactly-one-black share, |IED gap|, halo-ring share and cos_HB, own-rule flag rates (logit > 0) on H, W, FM(H,B), every
adversary source beside each network.
  python -I xf1_read.py --out xf1_read.json [--mock random|ceiling|ceilB|sbgain|gatefail]"""
import argparse, csv, hashlib, io, json, pathlib, sys, tarfile
import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
X1 = pathlib.Path("/mnt/t7/smad_next/XF1")
ADVF = pathlib.Path("/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/xf1b_rows_scores.csv")
PINS = {X1 / "xf1b_rows.csv": "4adcf914fba651f3b1b1ccfc5ea4b3e03155357aa5c84804180513da5925b271",
        X1 / "xf1b_ring.csv": "23f51cf3e8f90543ed05042e70355228794fdc45b9829c775a08a71efe9d69a6",
        ADVF: "86f61826d4ae9cf603780b69ae513e26de357a736c508f6838ddd00d2cd85d2a"}
ADV_CHECK = {("learner_Sb_gbt", "face"): 0.8591179069585352, ("floor_all_cue_gbt", "face"): 0.9166004854531828,
             ("floor_file_single", "face"): 0.6661670451113523}
TAR = X1 / "results/XF1_scores.tar"
ARMS, SEEDS, FORMS = ("A", "B", "Sb"), tuple(range(403, 408)), ("face", "whole")
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


def ci(v):
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--mock", choices=("random", "ceiling", "ceilB", "sbgain", "gatefail"), default=None)
    a = ap.parse_args()
    for p, h in PINS.items():
        assert sha(p) == h, p
    import check
    assert check._pinned("xf1b_rows_scores.csv")          # committed stage pins (raises otherwise)
    rows = list(csv.DictReader(open(X1 / "xf1b_rows.csv")))
    rid = {(r["klass"], r["form"], r["host"]): r["id"] for r in rows}
    hosts = sorted({r["host"] for r in rows}); assert len(hosts) == 299 and len(rid) == 1495
    meta = {r["host"]: r for r in rows if r["klass"] == "FMHB" and r["form"] == "face"}
    ring = {r["host"]: r for r in csv.DictReader(open(X1 / "xf1b_ring.csv"))}
    block = {h: int(meta[h]["block"]) for h in hosts}; comp = {h: int(meta[h]["component"]) for h in hosts}
    # adversary sources, per form, as {source: {id: score}}
    src = {f: {} for f in FORMS}
    for r in csv.DictReader(open(ADVF)):
        if r["source"].startswith("learner_"):
            src[r["form"]].setdefault(r["source"] + "_logreg", {})[r["id"]] = float(r["score"])
            src[r["form"]].setdefault(r["source"] + "_gbt", {})[r["id"]] = float(r["score_gbt"])
        else:
            src[r["form"]].setdefault(r["source"], {})[r["id"]] = float(r["score"])
    # networks
    L, gate = {}, {}
    if a.mock:
        for arm in ARMS:
            for s in SEEDS:
                n = f"PN1_{arm}_s{s}"; rr = np.random.default_rng(1000 * s + ARMS.index(arm))
                fail = a.mock == "gatefail" and arm == "B" and s in (404, 405)
                gate[n] = dict(byte_identical=not fail, mock=a.mock)
                if fail:
                    continue
                shift = 6.0 if a.mock == "ceiling" or (a.mock == "ceilB" and arm == "B") else 0.5 if (a.mock == "sbgain" and arm == "Sb") else 0.0
                L[n] = {r["id"]: float(rr.normal()) + (shift if r["klass"] == "FMHB" else 0.0) for r in rows}
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
    ub = sorted(set(block.values())); mem = {k: [h for h in hosts if block[h] == k] for k in ub}
    rng = np.random.default_rng(20261203)
    draws = [[h for k in rng.choice(ub, len(ub), replace=True) for h in mem[k]] for _ in range(B)]
    hrng = np.random.default_rng(20261204)
    hdraws = [list(hrng.choice(hosts, len(hosts), replace=True)) for _ in range(B)]
    uc = sorted(set(comp.values()))

    def stat(sc, form, hs):
        return auc(np.array([sc[rid[("FMHB", form, h)]] for h in hs]), np.array([sc[rid[("WARP", form, h)]] for h in hs]))

    out = dict(mock=a.mock, label="post-freeze development diagnostic, registered after the sealed read",
               n_hosts=len(hosts), n_blocks=len(ub), n_components=len(uc), gate={n: gate[n] for n in sorted(gate)}, gate_passed=sorted(L))
    # adversary source AUCs (check against the committed json values)
    adv = {f: {k: stat(v, f, hosts) for k, v in src[f].items()} for f in FORMS}
    for (k, f), v in ADV_CHECK.items():
        assert abs(adv[f][k] - v) < 1e-9, (k, f, adv[f][k])
    out["adversary_auc"] = adv
    obs, boot, hb = {}, {}, {}
    for n in L:
        for f in FORMS:
            obs[(n, f)] = stat(L[n], f, hosts)
            boot[(n, f)] = np.array([stat(L[n], f, d) for d in draws])
            hb[(n, f)] = np.array([stat(L[n], f, d) for d in hdraws])
    sboot = {(k, f): np.array([stat(src[f][k], f, d) for d in draws]) for f in FORMS for k in src[f]}
    per = {}
    for n in sorted(L):
        v = {k: np.array([L[n][rid[k + (h,)]] for h in hosts]) for k in (("H", "whole"), ("WARP", "whole"), ("FMHB", "whole"), ("WARP", "face"), ("FMHB", "face"))}
        own = f"learner_{n.split('_')[1]}_gbt"
        per[n] = dict(auc={f: obs[(n, f)] for f in FORMS}, whole_minus_face=obs[(n, "whole")] - obs[(n, "face")],
                      flags={"_".join(k): float((x > 0).mean()) for k, x in v.items()},
                      median_logit={"_".join(k): float(np.median(x)) for k, x in v.items()},
                      vs_adversary={f: {k: dict(diff=obs[(n, f)] - adv[f][k], ci=ci(boot[(n, f)] - sboot[(k, f)]),
                                               exceeds=bool(ci(boot[(n, f)] - sboot[(k, f)])[0] > 0)) for k in src[f]} for f in FORMS},
                      own_learner=own, exceeds_own_learner_face=bool(ci(boot[(n, "face")] - sboot[(own, "face")])[0] > 0))
    out["per_network"] = per
    terc = {"excl_border": {h: int(meta[h]["excl_border_t"]) for h in hosts}, "ied_gap": {h: int(meta[h]["ied_gap_t"]) for h in hosts},
            "ring_share": {h: int(ring[h]["ring_share_t"]) for h in hosts}}
    cq = np.quantile([float(meta[h]["cos_HB"]) for h in hosts], [1 / 3, 2 / 3])
    terc["cos_HB"] = {h: int(np.searchsorted(cq, float(meta[h]["cos_HB"]), side="right")) for h in hosts}
    arms = {}
    for arm in ARMS:
        ns = [f"PN1_{arm}_s{s}" for s in SEEDS if f"PN1_{arm}_s{s}" in L]
        if not ns:
            arms[arm] = dict(n_seeds=0, status="not read (no gate-passed network)"); continue
        r = dict(n_seeds=len(ns))
        for f in FORMS:
            bb = np.mean([boot[(n, f)] for n in ns], axis=0)
            r[f] = dict(seed_mean=float(np.mean([obs[(n, f)] for n in ns])), ci=ci(bb),
                        host_bootstrap_ci=ci(np.mean([hb[(n, f)] for n in ns], axis=0)),
                        loco_range=[float(min(x)), float(max(x))] if (x := [np.mean([stat(L[n], f, [h for h in hosts if comp[h] != k]) for n in ns]) for k in uc]) else None,
                        per_seed={n[-4:]: obs[(n, f)] for n in ns})
        wmf = np.mean([boot[(n, "whole")] - boot[(n, "face")] for n in ns], axis=0)
        r["whole_minus_face"] = dict(seed_mean=float(np.mean([per[n]["whole_minus_face"] for n in ns])), ci=ci(wmf))
        lo, hi = r["face"]["ci"]
        r["floor_rule"] = "does not separate blend from warp" if lo <= 0.50 <= hi else "below 0.50 (reversed)" if hi < 0.50 else "separates"
        nex = sum(per[n]["exceeds_own_learner_face"] for n in ns)
        r["exceeds_own_learner_seeds"] = f"{nex} of {len(ns)}"
        if hi < 0.50 or lo <= 0.50 <= hi:
            r["licence"] = "(a) this blend is not what the networks flag"
        elif nex >= 4:
            r["licence"] = "(c) beyond hand-made statistics trained on the same list"
        else:
            r["licence"] = "(b) consistent with blending and noise averaging; no evidence beyond low-level statistics"
        r["strata_face"] = {t: {str(k): float(np.mean([stat(L[n], "face", [h for h in hosts if terc[t][h] == k]) for n in ns])) for k in (0, 1, 2)} for t in terc}
        r["flags"] = {k: [float(min(per[n]["flags"][k] for n in ns)), float(max(per[n]["flags"][k] for n in ns))] for k in per[ns[0]]["flags"]}
        arms[arm] = r
    out["arms"] = arms
    read = [arm for arm in ARMS if arms[arm]["n_seeds"]]
    all_ceiling = bool(read) and all(arms[arm]["face"]["ci"][0] >= 0.95 for arm in read)
    gains = {}
    for X, role in (("B", "primary"), ("A", "secondary (A has no warp-only negatives)")):
        ss = [s for s in SEEDS if f"PN1_Sb_s{s}" in L and f"PN1_{X}_s{s}" in L]
        g = dict(role=role, n_seeds=len(ss))
        if len(ss) < 4:
            g["verdict"] = "not read"; gains[f"Sb_minus_{X}"] = g; continue
        d = [obs[(f"PN1_Sb_s{s}", "face")] - obs[(f"PN1_{X}_s{s}", "face")] for s in ss]
        gb = np.mean([boot[(f"PN1_Sb_s{s}", "face")] - boot[(f"PN1_{X}_s{s}", "face")] for s in ss], axis=0)
        m, (lo, hi) = float(np.mean(d)), ci(gb)
        npos = int(sum(x > 0 for x in d))
        loco = [np.mean([stat(L[f"PN1_Sb_s{s}"], "face", hs) - stat(L[f"PN1_{X}_s{s}"], "face", hs) for s in ss])
                for hs in ([h for h in hosts if comp[h] != k] for k in uc)]
        g.update(seed_mean=m, ci=[lo, hi], per_seed={str(s): x for s, x in zip(ss, d)}, n_positive=npos,
                 loco_range=[float(min(loco)), float(max(loco))],
                 host_bootstrap_ci=ci(np.mean([hb[(f"PN1_Sb_s{s}", "face")] - hb[(f"PN1_{X}_s{s}", "face")] for s in ss], axis=0)))
        if all_ceiling:
            g["verdict"] = "all arms at ceiling"
        elif arms[X]["face"]["seed_mean"] >= 0.97:
            g["verdict"] = "ceiling, not informative"
        else:
            g["verdict"] = "present" if (m >= 0.03 and lo > 0 and npos >= 4) else "absent" if hi < 0.03 else "inconclusive"
        gains[f"Sb_minus_{X}"] = g
    out["gains_face"] = gains
    out["all_arms_at_ceiling"] = all_ceiling
    out["no_licence"] = "No outcome licenses 'detects identity mixing'."
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(dict(gate_passed=len(L), gains={k: {kk: vv for kk, vv in v.items() if kk != "per_seed"} for k, v in gains.items()},
                          arms={k: {kk: (vv if kk not in FORMS else {x: y for x, y in vv.items() if x != "per_seed"}) for kk, vv in v.items()
                                    if kk in FORMS + ("floor_rule", "licence", "exceeds_own_learner_seeds", "status", "whole_minus_face")} for k, v in arms.items()},
                          all_arms_at_ceiling=all_ceiling), default=float)[:6000])


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()
