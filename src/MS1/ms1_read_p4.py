"""MS1 part 4 reader (WCSS H100; registered in prereg.md part 4 before any part-4 fit): G2 (dilution vs diversity) and
G3 (splice share), guards and printed reads. All scores come from the fit jobs (pn1_score.py, TF32 on, H100).

Input: result tars MS1P4_<arm>_s<seed>.tar (scores_eval.npz, scores_train.npz) in --results; the part-4 evaluation
manifest (pack pn1_pack_ms2.tar). Arms Sb, Sb63, SbM3, SbM3S; seeds 403-407.
  python3 -I ms1_read_p4.py --results DIR --out OUT.json      |  --mock
"""
import argparse
import csv
import hashlib
import io
import json
import math
import pathlib
import re
import sys
import tarfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ms1_part3 as P3  # noqa: E402
import ms1_part3b as P3B  # noqa: E402
import ms1_read as R1  # noqa: E402

ARMS = ("Sb", "Sb63", "SbM3", "SbM3S")
SEEDS = (403, 404, 405, 406, 407)
EVAL = pathlib.Path("/mnt/t7/smad_next/MS1/pack_tree_ms2/pn1/data/manifests/pn1_eval.csv")
MAN = {"Sb": P3.MAN["Sb"], "Sb63": P3.MAN["Sb"], "SbM3": P3.MAN["SbM3"],
       "SbM3S": pathlib.Path("/mnt/t7/smad_next/MS1/manifests/train_SbM3S.csv")}


EXPECT_MAN = {"Sb": "2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a",
              "Sb63": "2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a",
              "SbM3": "885dff9d267aafbf0ecba86f128a4bfd252c5a06d8cb4b8fcd6cf5fa0194162c",
              "SbM3S": "eaefef80c3a2d2167bbcd65e9da9815347af4c42f7803576736bb2c89ec731e5"}
EXPECT_STEPS = {"Sb": 6250, "Sb63": 3938, "SbM3": 6250, "SbM3S": 6250}


def text(tar, member):
    with tarfile.open(tar) as t:
        m = [x for x in t.getmembers() if x.name.endswith(member)]
        return t.extractfile(m[0]).read().decode(errors="replace") if m else ""


def config_ok(tar, arm):
    """registered per-tar check (pre-run F2): steps and limit 0 (task_info.txt), training manifest sha256 (manifest.txt,
    written by run_p4.sh), H100 (gpu.txt); returns (ok, env)."""
    info, log, gpu, env = (text(tar, x) for x in ("task_info.txt", "manifest.txt", "gpu.txt", "env.txt"))
    st = re.search(r"steps (\d+)", info)
    lim = re.search(r"limit (\d+)", info)
    man = re.search(r"train\.csv = \S+ sha256 ([0-9a-f]{64})", log)
    ok = bool(st and int(st.group(1)) == EXPECT_STEPS[arm] and lim and int(lim.group(1)) == 0 and man
              and man.group(1) == EXPECT_MAN[arm] and "H100" in gpu)
    return ok, env.strip()


def load(tar, member):
    with tarfile.open(tar) as t:
        m = [x for x in t.getmembers() if x.name.endswith(member)][0]
        return np.load(io.BytesIO(t.extractfile(m).read()))


def lower_rule(x, ref, floor):
    """registered P1-S-style rule: x lower than ref. Returns dict with verdict."""
    mx, mr = float(np.median(x)), float(np.median(ref))
    mw = R1.mw_less(x, ref)
    if mr < floor:
        v = "untestable (floor)"
    elif mx <= 0.5 * mr and mw["p"] <= 0.025:
        v = "supported"
    elif mx >= 0.8 * mr or mw["p"] > 0.5:
        v = "falsified"
    else:
        v = "inconclusive, no claim"
    return dict(median=mx, median_ref=mr, ratio=(mx / mr if mr > 0 else float("nan")), mw=mw, verdict=v)


def net(E, M):
    def v(f):
        return np.array([E[r["id"]] for r in M if f(r) and r["id"] in E], float)
    cfd = v(lambda r: r["fam"] == "cfd")
    s4 = v(lambda r: r["fam"] == "splice" and r["role"] == "dev" and r["rung"] == "S4")
    s03 = v(lambda r: r["fam"] == "splice" and r["role"] == "dev" and r["rung"] in ("S0", "S3"))
    lc = v(lambda r: r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig")
    tt1 = {k: v(lambda r, k=k: r["fam"] == "tt1" and r["cell"] == k) for k in R1.TT1}
    hp = v(lambda r: r["fam"] == "ms1ffhq" and r["rung"] == "photo" and r["strength"] == "")
    cam = v(lambda r: r["fam"] == "af0" and r["role"] == "dev" and r["rung"] == "photo" and r["strength"] == "")
    return dict(cfd_flag=float((cfd > 0).mean()), cfd_n=len(cfd), s4_vs_s03_auc=R1.fauc(s4, s03),
                lcomb_miss=float((lc <= 0).mean()), tt1_F=float(np.mean([(tt1[k] > 0).mean() for k in R1.TT1])),
                holdout_flag=float((hp > 0).mean()), cfd_auc_vs_cam=R1.fauc(cfd, cam),
                cfd_minus_cam=float(cfd.mean() - cam.mean()), kdef_flag=float((v(lambda r: r["fam"] == "kdef") > 0).mean()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-g3", action="store_true", help="mock in which SbM3 < Sb on the S4 read and SbM3S recovers")
    a = ap.parse_args()
    M = list(csv.DictReader(open(EVAL)))
    rng = np.random.default_rng(3)
    ev, tr, status, envs = {}, {}, {}, {}
    for arm in ARMS:
        man = {r["path"]: r for r in csv.DictReader(open(MAN[arm]))}
        for s in SEEDS:
            if a.mock:
                sh = {"Sb": 0.0, "Sb63": -0.3, "SbM3": -1.0, "SbM3S": -0.9}[arm]
                s4sh = {"Sb": 0.0, "Sb63": 0.0, "SbM3": -0.6, "SbM3S": -0.02}[arm] if a.mock_g3 else 0.0

                def mu(r):
                    if r["label"] == "0":
                        if r["fam"] == "cfd":
                            return -1.8 + 2 * sh
                        if r["fam"] == "splice" and r["rung"] in ("S0", "S3"):
                            return 0.5
                        return -3
                    if r["fam"] == "splice" and r["rung"] == "S4":
                        return 2.0 + s4sh
                    return 3
                ev[(arm, s)] = {r["id"]: float(rng.normal(mu(r), 1.0)) for r in M}
                tr[(arm, s)] = [(p, float(rng.normal(-3.2 if x["label"] == "0" else 3.2, 0.3)), x["kind"], x["db"])
                                for p, x in man.items()]
                status[f"{arm}_{s}"] = "mock"
                continue
            p = pathlib.Path(a.results) / f"MS1P4_{arm}_s{s}.tar"
            sp = pathlib.Path(str(p) + ".sha256")
            if not (p.exists() and sp.exists()) or hashlib.sha256(open(p, "rb").read()).hexdigest() != open(sp).read().split()[0]:
                status[f"{arm}_{s}"] = "missing or unverified"
                continue
            ok, envt = config_ok(p, arm)
            envs[(arm, s)] = envt
            if not ok:
                status[f"{arm}_{s}"] = "config mismatch (infrastructure failure)"
                continue
            z = load(p, "scores_eval.npz")
            E = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
            if not all(math.isfinite(x) for x in E.values()):
                status[f"{arm}_{s}"] = "non-finite"
                continue
            ev[(arm, s)] = E
            z = load(p, "scores_train.npz")
            rows = []
            for q, lg in zip([str(x) for x in z["path"]], z["logit"].astype(float)):
                key = q[q.index("train/"):] if "train/" in q else q
                x = man.get(key)
                if x is not None:
                    rows.append((key, lg, x["kind"], x["db"]))
            tr[(arm, s)] = rows
            status[f"{arm}_{s}"] = "read"
    if len(set(envs.values())) > 1:
        out_env = sorted(set(envs.values()))
        for k in list(ev):
            status[f"{k[0]}_{k[1]}"] += " (env.txt differs across tars)"
    else:
        out_env = sorted(set(envs.values()))
    N = {k: net(E, M) for k, E in ev.items()}
    out = dict(status=status, mock=a.mock, env_txt_distinct=out_env,
               per_network={f"{k[0]}_s{k[1]}": v for k, v in N.items()})

    def seeds_with(arms):
        return [s for s in SEEDS if all((x, s) in N for x in arms)]

    def col(arm, key, ss):
        return [N[(arm, s)][key] for s in ss]
    # G2
    s2 = seeds_with(("Sb", "Sb63", "SbM3"))
    G2 = dict(read_seeds=s2)
    if len(s2) >= 4:
        G2["control_SbM3"] = lower_rule(col("SbM3", "cfd_flag", s2), col("Sb", "cfd_flag", s2), 0.02)
        G2["primary_Sb63"] = lower_rule(col("Sb63", "cfd_flag", s2), col("Sb", "cfd_flag", s2), 0.02)
        if G2["control_SbM3"]["verdict"] == "untestable (floor)":
            G2["verdict"] = "untestable (floor)"
        elif G2["control_SbM3"]["verdict"] == "supported":
            G2["verdict"] = G2["primary_Sb63"]["verdict"]
        else:
            G2["verdict"] = "uninformative (positive control not met)"
        fs, f63, fm = (np.median(col(x, "cfd_flag", s2)) for x in ("Sb", "Sb63", "SbM3"))
        G2["printed"] = dict(fraction_explained=float((fs - f63) / (fs - fm)) if fs != fm else None,
                             paired_Sb63_minus_Sb=[N[("Sb63", q)]["cfd_flag"] - N[("Sb", q)]["cfd_flag"] for q in s2],
                             cfd_auc_vs_dev_camera={x: col(x, "cfd_auc_vs_cam", s2) for x in ("Sb", "Sb63", "SbM3")},
                             cfd_minus_camera_mean={x: col(x, "cfd_minus_cam", s2) for x in ("Sb", "Sb63", "SbM3")})
    else:
        G2["verdict"] = "not read (too few seeds)"
    # G3
    s3 = seeds_with(("Sb", "SbM3", "SbM3S"))
    G3 = dict(read_seeds=s3)
    if len(s3) >= 4:
        a_sb, a_m3, a_m3s = (col(x, "s4_vs_s03_auc", s3) for x in ("Sb", "SbM3", "SbM3S"))
        n = len(s3)
        below = sum(1 for i in range(n) if a_m3[i] < a_sb[i])
        delta = float(np.median(a_sb) - np.median(a_m3))
        ctrl = (below >= (n - 1 if n == 5 else n)) and delta >= 0.006
        rec = float(np.median(a_m3s) - np.median(a_m3))
        G3.update(control_SbM3_below_Sb_seeds=below, delta=delta, control_met=bool(ctrl), recovery=rec,
                  median_auc=dict(Sb=float(np.median(a_sb)), SbM3=float(np.median(a_m3)), SbM3S=float(np.median(a_m3s))),
                  printed=dict(median_cfd_flag_SbM3S=float(np.median(col("SbM3S", "cfd_flag", s3))),
                               cfd_flag_SbM3S_le_0_01=bool(np.median(col("SbM3S", "cfd_flag", s3)) <= 0.01),
                               lcomb_miss_SbM3S=col("SbM3S", "lcomb_miss", s3), lcomb_miss_SbM3=col("SbM3", "lcomb_miss", s3)))
        if not ctrl:
            G3["verdict"] = "uninformative (cost not replicated)"
        elif rec >= 0.5 * delta and np.median(a_m3s) >= np.median(a_sb) - 0.005:
            G3["verdict"] = "supported"
        elif rec <= 0.25 * delta:
            G3["verdict"] = "falsified"
        else:
            G3["verdict"] = "inconclusive, no claim"
    else:
        G3["verdict"] = "not read (too few seeds)"
    # guards: own-rule miss on FFHQ landmark_combined (unseen pipeline) for each new arm vs Sb
    guards = {}
    for arm in ("Sb63", "SbM3", "SbM3S"):
        ss = seeds_with(("Sb", arm))
        if len(ss) < 4:
            guards[arm] = "not read"
            continue
        x, r = col(arm, "lcomb_miss", ss), col("Sb", "lcomb_miss", ss)
        ok = (np.median(x) <= np.median(r) + 0.05) and sum(1 for i in range(len(ss)) if x[i] - r[i] > 0.10) <= 1
        guards[arm] = dict(median=float(np.median(x)), median_Sb=float(np.median(r)), per_seed=x, Sb_per_seed=r,
                           holds=bool(ok), parent_sex_strata="not available (no sex labels for FFHQ parents)")
    ss = seeds_with(("SbM3", "SbM3S"))
    guards["SbM3S_vs_SbM3_printed"] = dict(median_SbM3S=float(np.median(col("SbM3S", "lcomb_miss", ss))) if ss else None,
                                            median_SbM3=float(np.median(col("SbM3", "lcomb_miss", ss))) if ss else None)
    out.update(G2=G2, G3=G3, miss_guard=guards)
    # printed: rank-AUC memorisation (part 3b rules), within-sex CFD reads, other pools
    ram = {}
    for (arm, s), rows in tr.items():
        E = ev[(arm, s)]
        g = {}
        for kind, sel in P3.HELD.items():
            t = [lg for _, lg, k, db in rows if k == kind and db in ("frgc", "feret")]
            h = [E[r["id"]] for r in M if sel(r) and r["id"] in E]
            if t and h:
                g[kind] = P3B.rank_auc(t, h) if kind in P3.ATTACK else P3B.rank_auc([-x for x in t], [-x for x in h])
        ram[f"{arm}_s{s}"] = dict(per_kind=g, A=float(np.mean(list(g.values()))), kinds_below_0_5=sum(1 for x in g.values() if x < 0.5))
    out["rank_auc_memorisation"] = ram
    out["rank_auc_paired_vs_Sb"] = {arm: {str(q): ram[f"{arm}_s{q}"]["A"] - ram[f"Sb_s{q}"]["A"] for q in SEEDS
                                         if f"{arm}_s{q}" in ram and f"Sb_s{q}" in ram} for arm in ("Sb63", "SbM3", "SbM3S")}
    norm = P3.norming()
    model_of = {}
    for r in csv.DictReader(open(P3.CFD_POOL)):
        mm = re.search(r"CFD-([ABLW][FM]-\d+)-\d+-N\.jpg$", r["raw"])
        if mm and r["aligned"] == "1" and "/CFD/" in r["raw"]:
            model_of[r["id"]] = mm.group(1)
    ids = [i for i in sorted(model_of) if model_of[i] in norm and isinstance(norm[model_of[i]]["Feminine"], float)]
    ws = {}
    for (arm, s), E in ev.items():
        d = {}
        for sx in "FM":
            gi = [i for i in ids if model_of[i][1] == sx and i in E]
            d[sx] = dict(n=len(gi), rho_feminine=P3.spearman([E[i] for i in gi], [norm[model_of[i]]["Feminine"] for i in gi]),
                         n_flagged=int(sum(E[i] > 0 for i in gi)))
        ws[f"{arm}_s{s}"] = d
    out["within_sex_cfd"] = ws
    out["within_sex_paired_vs_Sb"] = {arm: {str(q): {sx: dict(rho_diff=ws[f"{arm}_s{q}"][sx]["rho_feminine"] - ws[f"Sb_s{q}"][sx]["rho_feminine"],
                                                             n_flagged=ws[f"{arm}_s{q}"][sx]["n_flagged"],
                                                             n_flagged_Sb=ws[f"Sb_s{q}"][sx]["n_flagged"]) for sx in "FM"}
                                            for q in SEEDS if f"{arm}_s{q}" in ws and f"Sb_s{q}" in ws}
                                      for arm in ("Sb63", "SbM3", "SbM3S")}
    out["training_margin"] = {f"{k[0]}_s{k[1]}": dict(neg=float(np.median([lg for _, lg, kk, _ in rows if kk not in P3.ATTACK and not kk.startswith("lad_S4")])),
                                                      att=float(np.median([lg for _, lg, kk, _ in rows if kk in P3.ATTACK])))
                              for k, rows in tr.items()}
    json.dump(out, open(a.out, "w"), indent=1, default=float)
    print(json.dumps(dict(G2=G2["verdict"], G3=G3["verdict"],
                          guards={k: v.get("holds", "printed") if isinstance(v, dict) else v for k, v in guards.items()})))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
