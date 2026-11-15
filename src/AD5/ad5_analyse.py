"""Retrains of released methods (AD5): readings and fixed verdicts (prereg.md with amendment 1). CPU only, DGX.

Statistics are the own-crop re-score's (RS1): src/RS1/analyse.py is imported unchanged (its sha256 is stored), with
the same person bootstrap (a41_read.Draw, B = 2,000, seed 20261111; FRLL, FEI and FFHQ draws as RS1) and the same EER /
AUC / threshold functions (Stats.eer, Stats.auc, flag_block: t5 on the native raw genuine photos, recomputed per
replicate). Every network of one method (the release scored through the AD5 path and the five retrains) is read on
the same draw, so effects are paired.

  python3 -I ad5_analyse.py --scores DIR [--B 2000] [--out-dir DIR] [--arms L,B,F,X,S]
DIR holds scores_rel_<name>__ad5v1.npz / __ad5v2.npz (MADation, MixFaceNet-MAD; RS1 athena_manifest ids; crop
variant 1 = authors' SMDD script, primary; variant 2 = corrected crop) and scores_own_<name>__ad5.npz (SelfMAD; RS1
manifest ids). Names: the release name, or <method>_<ARM>_s<seed>.
Writes ad5_gate.csv, ad5_readings.csv, ad5_verdicts.csv, ad5_rule05.csv, ad5_results.json.
"""
import argparse
import csv
import hashlib
import json
import pathlib
import sys

import numpy as np

RS1 = pathlib.Path("/home/narolski/smad-next/src/RS1")
sys.path.insert(0, str(RS1))
import analyse as RA  # noqa: E402  (RS1's analysis module, unchanged)

RES = pathlib.Path("/home/narolski/smad-next/experiments/AD5_retrains-of-released-methods")
ARMS = {"L": "madation_vitl14", "B": "madation_vitb16", "F": "madation_fe_vitl14", "X": "mixfacenet_mad_smdd",
        "S": "selfmad"}
PREFIX = {"L": "madation", "B": "madation", "F": "madation", "X": "mixfacenet", "S": "selfmad"}
SEEDS = (401, 402, 403, 404, 405)
FRLL5 = ["amsl", "facemorpher", "opencv", "stylegan", "webmorph"]
M22 = [f"mad22_{f}" for f in RA.FAM22]
PUBLISHED_CELLS = {"madation_vitl14": ["mordiff"] + FRLL5 + M22, "madation_vitb16": ["mordiff"] + FRLL5 + M22,
                   "madation_fe_vitl14": ["mordiff"] + M22, "mixfacenet_mad_smdd": ["mordiff"] + FRLL5 + M22,
                   "selfmad": FRLL5 + ["greedy_dim"]}
# amendment 1, item 2: primary cell = first listed cell whose release row is not "not reproduced"
PRIMARY_LISTS = {"hist": ["mordiff", "greedy_dim", "dim_a"], "flag_hist": ["mordiff", "greedy_dim", "dim_a"],
                 "smile": ["amsl", "webmorph", "opencv", "facemorpher", "stylegan", "greedy_dim"]}
PRIMARY_NOCELL = ["flag_small", "flag_jpeg50", "flag_resample50", "ladder_E_vs_photo", "ladder_D_vs_E",
                  "ladder_B_vs_D"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# RS1 README "For the retrains experiment (AD5)": the unchanged SMDD crop script (variant 1) fails on these sets
# (MorDIFF strips, A43 arms, 34% of FRLL FaceMorpher dropped); their variant-1 rows are not used (variant 2 is).
V1_INVALID = {"M_mordiff", "M_facemorpher", "a43_A", "a43_B", "a43_B20", "a43_C", "a43_C20", "a43_D", "a43_D20", "a43_E"}


def pools_from(f, man, drop=()):
    z = np.load(f)
    by = {}
    for i, l in zip(z["id"].tolist(), z["logit_noTTA"]):
        r = man[i]
        if r["set"] in drop:
            continue
        by.setdefault(r["set"], []).append((float(l), tuple(r["persons"].split("|")), r["expr"], r["photo"]))
    return {s_: RA.Pool([v[0] for v in L], [v[1] for v in L], [v[2] for v in L], "AD5 " + f.name, "logit",
                        [v[3] for v in L]) for s_, L in by.items()}


def rule05(S, X):
    """flag rate (point, replicates) at the network's own rule: probability of morph > 0.5, i.e. logit > 0."""
    w = S.w(X)
    return float(np.mean(X.s > 0)), RA.flag_rate(X.s, w, np.zeros(len(w)), True)


def readings(S, P, neutral_genuine=False):
    """{(reading, cell): (point, replicates)}; effects have null value 0. native_eer is a level, not an effect."""
    out = {}
    for c in RA.CELLS:
        gs, ms, hraw, haln, gal = RA.cell_sets(c)
        if gs not in P or ms not in P:
            continue
        G, Mo = P[gs], P[ms]
        if neutral_genuine:
            G = G.sub(G.ex == "03")
        npt, nrep = S.eer(G, Mo)
        out[("native_eer", c)] = (npt, nrep)
        if neutral_genuine:
            continue
        H = P.get(hraw) if hraw else None
        if H is not None:
            hp, hr = S.eer(H, Mo)
            out[("hist", c)] = (hp - npt, hr - nrep)
        elif gal in P and haln in P:
            ap_, ar_ = S.eer(P[gal], Mo)
            ep, er = S.eer(P[haln], Mo)
            out[("hist_aligned", c)] = (ep - ap_, er - ar_)
        f0p, f0r, _ = RA.flag_block(S, G, Mo, G)["t5"]
        Hx = H if H is not None else P.get(haln)
        if Hx is not None:
            fp, fr, _ = RA.flag_block(S, G, Mo, Hx)["t5"]
            out[("flag_hist" if H is not None else "flag_hist_aligned", c)] = (100 * (fp - f0p), 100 * (fr - f0r))
        Gn = G.sub(G.ex == "03")
        sp, sr = S.eer(Gn, Mo)
        out[("smile", c)] = (sp - npt, sr - nrep)
        mp_, mr_ = rule05(S, Mo)
        out[("miss05", c)] = (100 * (1 - mp_), 100 * (1 - mr_))          # descriptive level
    if neutral_genuine:
        return out
    if "G_raw" in P and "M_mordiff" in P:                           # t5 of the native FRLL photos (cell-independent)
        G, Mo = P["G_raw"], P["M_mordiff"]
        f0p, f0r, _ = RA.flag_block(S, G, Mo, G)["t5"]
        for key, X in (("flag_small", P.get("a43_E")),):
            if X is not None:
                fp, fr, _ = RA.flag_block(S, G, Mo, X)["t5"]
                out[(key, "-")] = (100 * (fp - f0p), 100 * (fr - f0r))
        if "Galn_frll" in P:
            a0p, a0r, _ = RA.flag_block(S, G, Mo, P["Galn_frll"])["t5"]
            for key, nm in (("flag_jpeg50", "Gjpeg50_frll"), ("flag_resample50", "Gresample50_frll")):
                if nm in P:
                    fp, fr, _ = RA.flag_block(S, G, Mo, P[nm])["t5"]
                    out[(key, "-")] = (100 * (fp - a0p), 100 * (fr - a0r))
        g5p, g5r = rule05(S, G)
        out[("flag05_native", "-")] = (100 * g5p, 100 * g5r)              # descriptive level
        for key, nm, ref in (("flag05_hist", "E7raw_mordiff", None), ("flag05_small", "a43_E", None),
                             ("flag05_jpeg50", "Gjpeg50_frll", "Galn_frll")):
            if nm in P and (ref is None or ref in P):
                xp, xr = rule05(S, P[nm])
                bp, br = (g5p, g5r) if ref is None else rule05(S, P[ref])
                out[(key, "-")] = (100 * (xp - bp), 100 * (xr - br))
    if "a43_E" in P and "G_raw" in P:
        photo = P["G_raw"]
        for key, pos, neg in (("ladder_E_vs_photo", "a43_E", None), ("ladder_D_vs_E", "a43_D", "a43_E"),
                              ("ladder_D20_vs_E", "a43_D20", "a43_E"), ("ladder_B_vs_D", "a43_B", "a43_D"),
                              ("ladder_B20_vs_D20", "a43_B20", "a43_D20")):
            if pos in P and (neg is None or neg in P):
                pt, rep = S.auc(P[pos], photo if neg is None else P[neg])
                out[(key, "-")] = (pt - 0.5, np.asarray(rep) - 0.5)
    return out


LEVELS = ("native_eer", "miss05", "flag05_native")


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


def rule(k, n_agree):
    if k < 4:
        return f"not determined ({k} seeds)"
    return "a property of the method" if n_agree >= 4 else "a property of the checkpoint" if n_agree <= 1 else "mixed"


def window(ref):
    return max(1.5, 0.25 * ref)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--out-dir", default=str(RES))
    ap.add_argument("--arms", default="L,B,F,X,S")
    a = ap.parse_args()
    od, sd = pathlib.Path(a.out_dir), pathlib.Path(a.scores)
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
    res = dict(rs1_analyse_sha256=sha(RS1 / "analyse.py"), script_sha256=sha(__file__), B=a.B, seed=RA.SEED,
               gate=[], readings=[], verdicts=[], k_of_5=[])
    for arm in a.arms.split(","):
        rel = ARMS[arm]
        variants = [("own", "")] if arm == "S" else [("v1", "v1"), ("v2", "v2")]
        for var, suf in variants:
            mode = "own" if arm == "S" else "rel"
            relname = "selfmad_hrnet_w18" if arm == "S" else rel
            fr = sd / f"scores_{mode}_{relname}__ad5{suf}.npz"
            if not fr.exists():
                continue
            drop = V1_INVALID if var == "v1" else ()
            nets = {"release": pools_from(fr, allman, drop)}
            for s in SEEDS:
                f = sd / f"scores_{mode}_{PREFIX[arm]}_{arm}_s{s}__ad5{suf}.npz"
                if f.exists():
                    nets[f"s{s}"] = pools_from(f, allman, drop)
            seeds = [k for k in nets if k != "release"]
            R = {k: readings(S, P) for k, P in nets.items()}
            defs = {"all photos": R}
            if arm == "S":                                  # RS1 amendment 2c: both genuine-class definitions
                defs["neutral-only photos"] = {k: readings(S, P, neutral_genuine=True) for k, P in nets.items()}
            # gate labels per seed and cell (amendment 1, item 1)
            lab = {}                                        # (definition, network, cell) -> (published label, matches)
            for dn, RR in defs.items():
                for c in PUBLISHED_CELLS[rel]:
                    if ("native_eer", c) not in RR["release"]:
                        continue
                    relpt = RR["release"][("native_eer", c)][0]
                    for k in nets:
                        pt, rep = RR[k][("native_eer", c)]
                        lb, pub, win = RA.label(rel, c, pt)
                        match = abs(pt - relpt) <= window(relpt)
                        lab[(dn, k, c)] = (lb, match)
                        res["gate"].append(dict(method=RA.NAME[rel], arm=arm, crop=var, genuine=dn, network=k, cell=c,
                                                native_eer=round(pt, 3), lo=round(ci(rep)[0], 3), hi=round(ci(rep)[1], 3),
                                                published=pub, window=win, label=lb, release_eer=round(relpt, 3),
                                                release_window=round(window(relpt), 3), matches_release=match))
                rel_not = [c for c in PUBLISHED_CELLS[rel] if (dn, "release", c) in lab
                           and lab[(dn, "release", c)][0] == RA.LAB_NO]
                gate_cells = [c for c in PUBLISHED_CELLS[rel] if (dn, "release", c) in lab and c not in rel_not]
                k_all = sum(all(lab[(dn, k, c)][0] == RA.LAB_OK for c in gate_cells) for k in seeds)
                res["k_of_5"].append(dict(method=RA.NAME[rel], arm=arm, crop=var, genuine=dn, seeds_finished=len(seeds),
                                          k=k_all, sentence=f"{k_all} of 5 retrains with the authors' code reproduce the "
                                          f"published numbers", cells=" ".join(gate_cells),
                                          excluded_release_not_reproduced=" ".join(rel_not)))
            # primary cells (amendment 1, item 2), from the release row of crop variant 1 (or own for SelfMAD)
            prim = {}
            for rd, lst in PRIMARY_LISTS.items():
                ok = [c for c in lst if ("native_eer", c) in R["release"]
                      and RA.label(rel, c, R["release"][("native_eer", c)][0])[0] != RA.LAB_NO]
                prim[rd] = ok[0] if ok else lst[0]
            # readings and verdicts
            keys = sorted(k for k in R["release"] if k[0] not in LEVELS)
            for key in keys:
                relv = R["release"][key]
                lo, hi = ci(relv[1])
                res["readings"].append(dict(method=RA.NAME[rel], arm=arm, crop=var, reading=key[0], cell=key[1],
                                            network="release", effect=round(float(relv[0]), 4), lo=round(lo, 4),
                                            hi=round(hi, 4), agrees=None, release_kind=None))
                ag = {}
                for k in seeds:
                    if key not in R[k]:
                        continue
                    g, kind = agree(relv, R[k][key])
                    ag[k] = g
                    rlo, rhi = ci(R[k][key][1])
                    res["readings"].append(dict(method=RA.NAME[rel], arm=arm, crop=var, reading=key[0], cell=key[1],
                                                network=k, effect=round(float(R[k][key][0]), 4), lo=round(rlo, 4),
                                                hi=round(rhi, 4), agrees=g, release_kind=kind))
                cell = key[1]
                primary = (key[0] in PRIMARY_NOCELL) or (key[0] in prim and prim[key[0]] == cell)
                if len(seeds) < 5:
                    head = f"incomplete ({len(seeds)} seeds)"
                else:
                    head = rule(len(ag), sum(ag.values()))
                row = dict(method=RA.NAME[rel], arm=arm, crop=var, reading=key[0], cell=cell, primary=primary,
                           seeds=len(ag), agreeing=sum(ag.values()), verdict_all_seeds=head)
                cc = cell if cell != "-" else ("mordiff" if ("all photos", "release", "mordiff") in lab else None)
                for dn in defs:
                    for nm, sel in (("reproduced", lambda k: lab.get((dn, k, cc), ("", False))[0] == RA.LAB_OK),
                                    ("matches_release", lambda k: lab.get((dn, k, cc), ("", False))[1])):
                        sub = [k for k in ag if cc is not None and (dn, k, cc) in lab and sel(k)]
                        tag = f"{nm} ({dn})" if len(defs) > 1 else nm
                        row[f"k_{tag}"] = len(sub)
                        row[f"verdict_{tag}"] = (f"incomplete ({len(seeds)} seeds)" if len(seeds) < 5 else
                                                 rule(len(sub), sum(ag[k] for k in sub)) if cc else "no cell")
                res["verdicts"].append(row)
            for k in nets:
                for key, (pt, rep) in R[k].items():
                    if key[0] in LEVELS:
                        lo, hi = ci(rep)
                        res.setdefault("levels", []).append(dict(method=RA.NAME[rel], arm=arm, crop=var, network=k,
                                                                 quantity=key[0], cell=key[1], value=round(pt, 3),
                                                                 lo=round(lo, 3), hi=round(hi, 3)))
    od.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(od / "ad5_results.json", "w"), indent=1, default=float)
    for k in ("gate", "readings", "verdicts", "k_of_5", "levels"):
        rows = res.get(k) or []
        if rows:
            cols = []
            for r in rows:
                cols += [c for c in r if c not in cols]
            with open(od / f"ad5_{k}.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=cols)
                w.writeheader()
                w.writerows(rows)
    print({k: len(v) for k, v in res.items() if isinstance(v, list)})


if __name__ == "__main__":
    main()
