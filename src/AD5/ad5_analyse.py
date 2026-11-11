"""Retrains of released methods (AD5): readings and fixed verdicts (prereg.md). CPU only, DGX.

Statistics are the own-crop re-score's (RS1): src/RS1/analyse.py is imported unchanged (its sha256 is printed and
stored), with the same person bootstrap (a41_read.Draw, B = 2,000, seed 20261111; FRLL, FEI and FFHQ draws as RS1),
the same EER / AUC / threshold functions (Stats.eer, Stats.auc, flag_block with t5 and t_eer). Every network of one
method (the release scored through the AD5 path and the five retrains) is read on the same draw, so effects are paired.

  python3 -I ad5_analyse.py --scores DIR [--B 2000] [--out-dir experiments/AD5_.../]
DIR holds scores_rel_<name>__ad5.npz (MADation, MixFaceNet-MAD; ids of RS1's athena_manifest.csv) and
scores_own_<name>__ad5.npz (SelfMAD; ids of RS1's manifest.csv). Names: the release name, or <method>_<ARM>_s<seed>.
"""
import argparse
import csv
import glob
import hashlib
import json
import pathlib
import sys

import numpy as np

RS1 = pathlib.Path("/home/narolski/smad-next/src/RS1")
sys.path.insert(0, str(RS1))
import analyse as RA  # noqa: E402  (RS1's analysis module, unchanged)

RES = pathlib.Path("/home/narolski/smad-next/experiments/AD5_retrains-of-released-methods")
ARMS = {"L": ("madation_vitl14", "rel"), "B": ("madation_vitb16", "rel"), "F": ("madation_fe_vitl14", "rel"),
        "X": ("mixfacenet_mad_smdd", "rel"), "S": ("selfmad", "own")}
PREFIX = {"L": "madation", "B": "madation", "F": "madation", "X": "mixfacenet", "S": "selfmad"}
SEEDS = (401, 402, 403, 404, 405)
GATE_CELLS = {"madation_vitl14": ["mordiff", "amsl", "facemorpher", "opencv", "stylegan", "webmorph"]
              + [f"mad22_{f}" for f in RA.FAM22],
              "madation_vitb16": ["mordiff", "amsl", "facemorpher", "opencv", "stylegan", "webmorph"]
              + [f"mad22_{f}" for f in RA.FAM22],
              "madation_fe_vitl14": ["mordiff"] + [f"mad22_{f}" for f in RA.FAM22],
              "mixfacenet_mad_smdd": ["mordiff", "amsl", "facemorpher", "opencv", "stylegan", "webmorph"]
              + [f"mad22_{f}" for f in RA.FAM22],
              "selfmad": ["amsl", "facemorpher", "opencv", "stylegan", "webmorph", "greedy_dim"]}
PRIMARY = [("hist", "mordiff"), ("flag_hist", "mordiff"), ("flag_small", "mordiff"), ("smile", "amsl"),
           ("ladder_E_vs_photo", "mordiff"), ("ladder_D_vs_E", "mordiff"), ("ladder_B_vs_D", "mordiff")]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pools_from(f, man):
    z = np.load(f)
    by = {}
    for i, l in zip(z["id"].tolist(), z["logit_noTTA"]):
        r = man[i]
        by.setdefault(r["set"], []).append((float(l), tuple(r["persons"].split("|")), r["expr"], r["photo"]))
    return {s_: RA.Pool([v[0] for v in L], [v[1] for v in L], [v[2] for v in L], "AD5 " + f.name, "logit",
                        [v[3] for v in L]) for s_, L in by.items()}


def readings(S, P):
    """{(reading, cell): (point, replicates)} for one network; effects have null value 0."""
    out = {}
    for c in RA.CELLS:
        gs, ms, hraw, haln, gal = RA.cell_sets(c)
        if gs not in P or ms not in P:
            continue
        G, Mo = P[gs], P[ms]
        npt, nrep = S.eer(G, Mo)
        out[("native_eer", c)] = (npt, nrep)
        H = P.get(hraw) if hraw else None
        if H is not None:
            hp, hr = S.eer(H, Mo)
            out[("hist", c)] = (hp - npt, hr - nrep)
        elif gal in P and haln in P:                 # aligned-frame cells: aligned E7 minus aligned native (secondary)
            ap_, ar_ = S.eer(P[gal], Mo)
            ep, er = S.eer(P[haln], Mo)
            out[("hist_aligned", c)] = (ep - ap_, er - ar_)
        f0p, f0r, _ = RA.flag_block(S, G, Mo, G)["t5"]
        Hx = H if H is not None else P.get(haln)
        if Hx is not None:
            fp, fr, _ = RA.flag_block(S, G, Mo, Hx)["t5"]
            out[("flag_hist" if H is not None else "flag_hist_aligned", c)] = (100 * (fp - f0p), 100 * (fr - f0r))
        if "a43_E" in P:
            fp, fr, _ = RA.flag_block(S, G, Mo, P["a43_E"])["t5"]
            out[("flag_small", c)] = (100 * (fp - f0p), 100 * (fr - f0r))
        Gn = G.sub(G.ex == "03")
        sp, sr = S.eer(Gn, Mo)
        out[("smile", c)] = (sp - npt, sr - nrep)
    if "a43_E" in P and "G_raw" in P:
        photo = P["G_raw"]
        for key, pos, neg in (("ladder_E_vs_photo", "a43_E", None), ("ladder_D_vs_E", "a43_D", "a43_E"),
                              ("ladder_D20_vs_E", "a43_D20", "a43_E"), ("ladder_B_vs_D", "a43_B", "a43_D"),
                              ("ladder_B20_vs_D20", "a43_B20", "a43_D20")):
            if pos in P and (neg is None or neg in P):
                pt, rep = S.auc(P[pos], photo if neg is None else P[neg])
                out[(key, "mordiff")] = (pt - 0.5, np.asarray(rep) - 0.5)
    return out


def ci(rep):
    return RA.ci(rep)


def agree(rel, ret):
    """prereg: release interval excludes 0 -> same sign and >= half the size (point estimates);
    release interval includes 0 -> the retrain's own interval includes 0."""
    lo, hi = ci(rel[1])
    if lo > 0 or hi < 0:
        return bool(np.sign(ret[0]) == np.sign(rel[0]) and abs(ret[0]) >= 0.5 * abs(rel[0])), "effect"
    rlo, rhi = ci(ret[1])
    return bool(rlo <= 0 <= rhi), "no effect"


def verdict(n_rep, n_agree_rep, n_agree_all):
    if n_rep >= 4:
        v = ("a property of the method" if n_agree_rep >= 4 else "a property of the checkpoint" if n_agree_rep <= 1
             else "mixed")
    else:
        v = f"not determined ({n_rep} of 5 retrains reproduce)"
    sec = ("a property of the method" if n_agree_all >= 4 else "a property of the checkpoint" if n_agree_all <= 1
           else "mixed")
    return v, sec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--out-dir", default=str(RES))
    ap.add_argument("--arms", default="L,B,F,X,S")
    a = ap.parse_args()
    od = pathlib.Path(a.out_dir)
    man = RA.manifest()
    athman = {r["id"]: r for r in csv.DictReader(open(RA.ATH / "athena_manifest.csv"))}
    allman = {**athman, **man}
    allp = {p for r in man.values() for p in r["persons"].split("|")}
    pers = sorted(p for p in allp if p.isdigit())
    assert len(pers) == 102
    Ds = {"frll": RA.M.Draw(pers, a.B, RA.SEED),
          "fei": RA.M.Draw(sorted(p for p in allp if p.startswith("fei")), a.B, RA.SEED + 1),
          "ffhq": RA.M.Draw(sorted(p for p in allp if p.startswith("ffhq")), a.B, RA.SEED + 2)}
    S = RA.Stats(Ds)
    res = dict(rs1_analyse_sha256=sha(RS1 / "analyse.py"), B=a.B, seed=RA.SEED, gate=[], readings=[], verdicts=[])
    for arm in a.arms.split(","):
        rel, mode = ARMS[arm]
        sd = pathlib.Path(a.scores)
        rel_name = "selfmad_hrnet_w18" if arm == "S" else rel
        fr = sd / f"scores_{mode}_{rel_name}__ad5.npz"
        if not fr.exists():
            continue
        nets = {"release": pools_from(fr, allman)}
        for s in SEEDS:
            f = sd / f"scores_{mode}_{PREFIX[arm]}_{arm}_s{s}__ad5.npz"
            if f.exists():
                nets[f"s{s}"] = pools_from(f, allman)
        R = {k: readings(S, P) for k, P in nets.items()}
        # reproduction gate
        relrows = {c: RA.label(rel, c, R["release"][("native_eer", c)][0])[0]
                   for c in GATE_CELLS[rel] if ("native_eer", c) in R["release"]}
        gate_cells = [c for c, lab in relrows.items() if lab != RA.LAB_NO]
        reproduces = {}
        for k in nets:
            ok_g = all(RA.label(rel, c, R[k][("native_eer", c)][0])[0] == RA.LAB_OK for c in gate_cells)
            ok_lit = all(RA.label(rel, c, R[k][("native_eer", c)][0])[0] == RA.LAB_OK for c in relrows)
            reproduces[k] = ok_g
            for c in relrows:
                pt, rep = R[k][("native_eer", c)]
                lab, pub, win = RA.label(rel, c, pt)
                res["gate"].append(dict(method=RA.NAME[rel], arm=arm, network=k, cell=c, native_eer=round(pt, 3),
                                        lo=round(ci(rep)[0], 3), hi=round(ci(rep)[1], 3), published=pub, window=win,
                                        label=lab, gate_cell=c in gate_cells, reproduces_gate=ok_g,
                                        reproduces_literal=ok_lit))
        # readings and verdicts
        keys = sorted(set().union(*[set(R[k]) for k in nets]) - {k for k in R["release"] if k[0] == "native_eer"})
        for key in keys:
            if key not in R["release"]:
                continue
            relv = R["release"][key]
            n_rep = n_ag_rep = n_ag_all = n_all = 0
            for k in nets:
                if k == "release" or key not in R[k]:
                    continue
                g, kind = agree(relv, R[k][key])
                n_all += 1
                n_ag_all += g
                if reproduces[k]:
                    n_rep += 1
                    n_ag_rep += g
                lo, hi = ci(R[k][key][1])
                res["readings"].append(dict(method=RA.NAME[rel], arm=arm, reading=key[0], cell=key[1], network=k,
                                            effect=round(float(R[k][key][0]), 4), lo=round(lo, 4), hi=round(hi, 4),
                                            reproduces=reproduces[k], agrees=g, release_kind=kind))
            lo, hi = ci(relv[1])
            res["readings"].append(dict(method=RA.NAME[rel], arm=arm, reading=key[0], cell=key[1], network="release",
                                        effect=round(float(relv[0]), 4), lo=round(lo, 4), hi=round(hi, 4),
                                        reproduces=None, agrees=None, release_kind=None))
            v, sec = verdict(n_rep, n_ag_rep, n_ag_all)
            res["verdicts"].append(dict(method=RA.NAME[rel], arm=arm, reading=key[0], cell=key[1],
                                        primary=key in PRIMARY, retrains=n_all, reproducing=n_rep,
                                        agreeing_reproducing=n_ag_rep, agreeing_all=n_ag_all, verdict=v,
                                        verdict_all_five=sec))
    od.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(od / "ad5_results.json", "w"), indent=1, default=float)
    for k in ("gate", "readings", "verdicts"):
        if res[k]:
            with open(od / f"ad5_{k}.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(res[k][0]))
                w.writeheader()
                w.writerows(res[k])
    print({k: len(v) for k, v in res.items() if isinstance(v, list)})


if __name__ == "__main__":
    main()
