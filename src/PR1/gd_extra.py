"""PR1 amendment 4 (post hoc, registered before computing): part A printed control table, part B 27-statistic cue
floors for GD1 and GD2 contrasts. Zero GPU. Development data only.
  python -I gd_extra.py --out gd_extra.json"""
import argparse
import csv
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pr1_read import ARMS, SEEDS, auc, share, sha  # noqa: E402
import gd_read as G  # noqa: E402

PR1 = pathlib.Path("/mnt/t7/smad_next/PR1")
TAR = PR1 / "results" / "PR1_GD_pn1fs.tar"
TAR_SHA = "bf560f534aa951ed164f42dcba0b99ece0991495ffea8fef687647ac44186027"
EXP = pathlib.Path("/home/narolski/smad-next/experiments/PR1_protocol-reads-existing-networks")
CONTRASTS = (("gd1", "X", "REC"), ("gd1", "REC", "G"), ("gd1", "X", "SAME"),
             ("gd2", "R2", "R0"), ("gd2", "R4", "R2"), ("gd2", "R4", "R3"))


def strat(pos, neg, cp, cn, q=5):
    e = np.quantile(np.r_[cp, cn], np.linspace(0, 1, q + 1))
    bp = np.clip(np.searchsorted(e, cp, side="right") - 1, 0, q - 1)
    bn = np.clip(np.searchsorted(e, cn, side="right") - 1, 0, q - 1)
    num = den = 0.0
    for b in range(q):
        p, n = pos[bp == b], neg[bn == b]
        if len(p) >= 10 and len(n) >= 10:
            w = len(p) * len(n)
            num += auc(p, n) * w
            den += w
    return num / den if den else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    assert sha(TAR) == TAR_SHA
    man = list(csv.DictReader(open(G.GDMAN)))
    by = {r["id"]: r for r in man}
    ids = lambda fam, rung: [r["id"] for r in man if r["fam"] == fam and r["rung"] == rung]   # noqa: E731
    S = {}
    with tarfile.open(TAR) as tf:
        for arm in ARMS:
            for s in SEEDS:
                n = f"PN1_{arm}_s{s}"
                d = {}
                for fam in ("gd0", "gd1", "gd2"):
                    z = np.load(io.BytesIO(tf.extractfile(f"PR1_GD_pn1fs/scores/{n}__{fam}.npz").read()))
                    d.update(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
                S[(arm, s)] = d
    out = dict(part_a={}, part_b={})
    # ---------------- part A
    Z = json.load(open(EXP / "z_read.json"))["per_net"]
    Z2 = json.load(open(EXP / "z2b_read.json"))["per_net"]
    pairs = (("gd2", "R3", "R2"), ("gd2", "R3m", "R2"), ("gd2", "R2s", "R0"), ("gd2", "R4", "R2s"), ("gd2", "R3", "R3m"),
             ("gd1", "X", "SAME"), ("gd1", "SAME", "REC"), ("gd1", "MIR", "REC"), ("gd1", "X", "MIR"))
    for (arm, s), d in S.items():
        v = lambda L: np.array([d[i] for i in L])   # noqa: E731
        r = {f"{f}:{x}_vs_{y}": auc(v(ids(f, x)), v(ids(f, y))) for f, x, y in pairs}
        for fam in ("stylegan_wplus", "stylegan_w"):
            m = v(ids("gd0", f"{fam}_orig"))
            r[f"cross:{fam}_vs_gd2R2"] = auc(m, v(ids("gd2", "R2")))
            r[f"cross:{fam}_vs_gd2R0"] = auc(m, v(ids("gd2", "R0")))
            r[f"median:{fam}"] = float(np.median(m))
        for rg in ("R0", "R2", "R4"):
            r[f"median:gd2_{rg}"] = float(np.median(v(ids("gd2", rg))))
        zz, z2 = Z[f"{arm}_s{s}"], Z2[f"PN1_{arm}_s{s}"]
        r["joint_tau5"] = bool(zz["z2a"]["usable"] and z2["G_unseen"] <= 0.10)
        # cut-off max(tau5, 0): recompute G_max / lcomb miss from z_read pools is not possible from summaries for t != tau5;
        # use the stored-score pools via pr1_read at cut-off c
        out["part_a"][f"{arm}_s{s}"] = r
    # cut-off max(tau5,0): recompute from stored FS1 scores and TT1 rows
    import pr1_read as PR
    rows = PR.manifest()
    P = PR.pools(rows)
    sys.path.insert(0, "/home/narolski/smad-next/src/TT1")
    import tt1common as T
    import tt1_read as TR
    PT, _ = TR.load_pools()
    J = json.load(open("/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/tt1_read_fs.json"))
    tt = tarfile.open("/mnt/t7/smad_next/TT1/results/TT1_A100_pn1fs_fs.tar")
    root = tt.getnames()[0].split("/")[0]
    fam_src = {f: ([f] if f != "lfw_calfw" else ["lfw", "calfw"]) for f in T.FAMILIES}
    for arm in ARMS:
        for s in SEEDS:
            n = f"PN1_{arm}_s{s}"
            assert n in J["gate_passed"], n
            N = PR.load_net(arm, s, False, {r["id"] for r in rows}, None)
            e = N["eval"]
            c = max(Z[f"{arm}_s{s}"]["tau5"], 0.0)
            vv = lambda k: np.array([e[i] for i in P[k]])   # noqa: E731
            gk = ("ffhq_bona_eval", "ffhq_lcomplete_resmatch_eval", "ffhq_lcombined_resmatch_eval", "lad_R0_test_nat",
                  "lad_R0_test_61", "lad_R0_test_112")
            gmax = max(share(vv(k), t=c) for k in gk)
            miss = share(vv("lcomb_orig"), gt=False, t=c)
            z = np.load(io.BytesIO(tt.extractfile(f"{root}/scores/{n}__tt1.npz").read()))
            L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
            gu = max(float(np.mean(np.concatenate([np.array([L[i] for i, _ in PT[f"U:{q}"]]) for q in fam_src[f]]) > c))
                     for f in T.FAMILIES)
            out["part_a"][f"{arm}_s{s}"]["cut_max_tau5_0"] = dict(cut=c, G_max=gmax, lcomb_miss=miss, G_unseen=gu,
                                                                 joint=bool(gmax <= 0.10 and miss <= 0.30 and gu <= 0.10))
    # ---------------- part B
    c1, n1 = G.cues(PR1 / "cues" / "gd1.npz")
    c2, n2 = G.cues(PR1 / "cues" / "gd2.npz")
    M, names, chk = G.baseline_models()
    assert n1 == n2 == names
    cues = {**c1, **c2}
    floors = {}
    for fam, x, y in CONTRASTS:
        pi, ni = ids(fam, x), ids(fam, y)
        assert all(i in cues for i in pi + ni), "missing cues"
        Pm, Nm = np.array([cues[i] for i in pi]), np.array([cues[i] for i in ni])
        assert np.isfinite(Pm).all() and np.isfinite(Nm).all()
        single = [max(auc(Pm[:, j], Nm[:, j]), 1 - auc(Pm[:, j], Nm[:, j])) for j in range(Pm.shape[1])]
        jb = int(np.argmax(single))
        comp = dict(best_single=float(single[jb]), best_single_name=names[jb],
                    **{k: auc(m.decision_function(Pm), m.decision_function(Nm)) for k, (m, _, _) in M.items()})
        F = max(comp["best_single"], comp["s_lad"], comp["b_lad"])
        floors[f"{fam}:{x}_vs_{y}"] = dict(F=F, **comp, label=("loader view" if fam == "gd1" else "cues27"))
        for arm in ARMS:
            nets, diffs, st = [], [], []
            for s in SEEDS:
                d = S[(arm, s)]
                p_, n_ = np.array([d[i] for i in pi]), np.array([d[i] for i in ni])
                A_ = auc(p_, n_)
                nets.append(A_)
                diffs.append(A_ - F)
                st.append(strat(p_, n_, Pm[:, jb], Nm[:, jb]))
            ver = ("beyond simple statistics" if sum(x_ >= 0.05 for x_ in diffs) >= 4 else
                   "not beyond simple statistics" if sum(x_ <= 0 for x_ in diffs) >= 4 else "inconclusive, no claim")
            out["part_b"][f"{fam}:{x}_vs_{y}:{arm}"] = dict(auc=nets, minus_floor=diffs, strat_auc_best_single=st, verdict=ver)
    out["floors"] = floors
    out["baseline_check"] = chk
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(floors, indent=0, default=float))
    for k, v in out["part_b"].items():
        print(k, v["verdict"], np.round(v["auc"], 3).tolist(), np.round(v["minus_floor"], 3).tolist())
    for k, v in out["part_a"].items():
        print(k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()})


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()
