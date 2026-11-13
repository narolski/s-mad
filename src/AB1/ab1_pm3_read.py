"""AB1 amendment 7 (batch C, post-freeze ablation rows; copy of ab1_pm2_read.py 77ace4b3 with --pair C added): the amendment-4 contrasts (rule unchanged, plus the registered handling of unreadable
bootstrap draws) for
  --pair Sp   Sb - Sp at seeds 408-412 (AB1 H100 fit-job scores), and
  --pair FS1  Sb - B and Sb - A at seeds 403-407 (the FS1 block: the frozen networks' own seeds; A100 PCIe fit-job scores,
              /mnt/t7/smad_next/PN1/results_fs/PN1_<arm>_s<seed>.tar, sha256 against .sha256, gpu.txt names an A100,
              task_info steps 6250 limit 0, pack 96c31ae2).
Host sets, D-stratified statistic, contrasts, component bootstrap (2,000 draws, rng 20261120, the same draws for all
networks and seeds) and the present / absent / inconclusive rule are those of ab1_pm_read.py (amendments 4, 4b).
Deciding statistic (amendment 5b, fixed from the score-free draw counts): primary R4 vs R3 decides on the stratified
statistic with 4b's unstratified-agreement condition; S4 vs S3 on the 80 clean hosts decides on the unstratified seed-mean
gain and its bootstrap interval, and "present" also requires the stratified seed-mean gain on the full 80 hosts > 0. The
unreadable-draw share is printed; 99.5% intervals are printed as a sensitivity check (10 verdicts in the family). A seed with an unreadable stratified statistic on the full host set counts as not readable
(fewer than 4 readable seeds: "not read").
  python3 -I ab1_pm2_read.py --pair Sp|FS1 --out OUT.json
  python3 -I ab1_pm2_read.py --pair Sp|FS1 --mock --out MOCK.json"""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import pathlib
import sys
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PM = _mod("ab1_pm_read", HERE / "ab1_pm_read.py")
A = PM.A
C2 = A.C2
K = PM.K
PM_SHA = "ba6efdada789c2a42ef47fa1fa39e707012f66641be40b6346ce9b45b067ed5e"
C_OVERLAY = "62712bb9d5066443d5737c84da852d055ab248930d5f38fc8b77ba0074a34c68"
C_MANDIR = pathlib.Path("/mnt/t7/smad_next/AB1/c/manifests")
FS1_RES = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
FS1_EVAL = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
FS1_EVAL_SHA = "f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045"


FSMAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests")
SP_MAN = pathlib.Path("/mnt/t7/smad_next/PN1/manifests_sp/train_Sp.csv")


def load_fs1(arm, s):
    T = f"PN1_{arm}_s{s}"
    tar = FS1_RES / f"{T}.tar"
    shf = FS1_RES / f"{T}.tar.sha256"
    if not tar.exists() or not shf.exists():
        return None, "missing"
    if hashlib.sha256(tar.read_bytes()).hexdigest() != shf.read_text().split()[0]:
        return None, "sha256 mismatch"
    with tarfile.open(tar) as t:
        z = np.load(io.BytesIO(t.extractfile(f"{T}/scores_eval.npz").read()))
        zt = np.load(io.BytesIO(t.extractfile(f"{T}/scores_train.npz").read()))
        gpu = t.extractfile(f"{T}/gpu.txt").read().decode()
        ti = t.extractfile(f"{T}/task_info.txt").read().decode()
        log = t.extractfile(f"{T}/train.log").read().decode(errors="replace")
        env = t.extractfile(f"{T}/task.env").read().decode()
    pack_ok = ("pack_sha256 96c31ae2" in ti) or (arm == "Sp" and "pack_sha256 76528f16" in ti)
    if "A100" not in gpu or "steps 6250 limit 0" not in ti or not pack_ok:
        return None, f"provenance off: {gpu.strip()} | {ti.strip()}"
    if str(z["manifest_sha256"]) != FS1_EVAL_SHA:
        return None, "eval manifest off"
    man = SP_MAN if arm == "Sp" else FSMAN / f"train_{arm}.csv"            # check A5 F5
    if str(zt["manifest_sha256"]) != hashlib.sha256(man.read_bytes()).hexdigest():
        return None, "train manifest off"
    if f"ARM={arm}" not in env:
        return None, "task.env arm off"
    import re as _re
    losses = [float(v) for v in _re.findall(r"loss[ =:]+(-?(?:inf|nan)|[-+0-9.eE]+)", log, flags=_re.I)]
    if not losses or not all(math.isfinite(v) for v in losses):
        return None, "no finite loss"
    return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float))), "read"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", choices=("Sp", "FS1", "C"), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    assert A.sha(HERE / "ab1_pm_read.py") == PM_SHA
    seeds = (408, 409, 410, 411, 412) if a.pair in ("Sp", "C") else (403, 404, 405, 406, 407)
    arms = {"Sp": ("Sb", "Sp", "B", "A"), "FS1": ("Sb", "B", "A", "Sp"), "C": ("Sb", "B", "Sp", "SpV", "BN")}[a.pair]
    # (first, second, role): verdict-bearing pairs, then printed pairs
    if a.pair == "C":
        pairs = [("Sb", "SpV", "verdict"), ("BN", "B", "verdict"), ("Sb", "BN", "printed (interaction)"),
                 ("SpV", "Sp", "printed (volume)"), ("Sb", "Sp", "printed (amendment-5 re-print)"), ("Sb", "B", "printed (amendment-4 re-print)")]
    elif a.pair == "Sp":
        pairs = [("Sb", "Sp", "verdict"), ("Sp", "B", "printed (decomposition)"), ("Sb", "B", "printed (amendment-4 re-print)"),
                 ("Sb", "A", "printed (amendment-4 re-print)")]
    else:
        pairs = [("Sb", "B", "verdict"), ("Sb", "A", "verdict"), ("Sb", "Sp", "printed, descriptive, not read (403-405 only)")]
    lad, _ = K.split_tables()
    dev = sorted(h for h, x in lad.items() if x["role"] == "dev")
    test = sorted(h for h, x in lad.items() if x["role"] == "test" and x["test_read"] == "1")
    clean = sorted(r["host"] for r in csv.DictReader(open(PM.CLEAN)))
    assert len(dev) == 100 and len(test) == 191 and len(clean) == 80 and set(clean) <= set(test)   # check A5 F5
    assert hashlib.sha256(PM.CLEAN.read_bytes()).hexdigest() == "814c44861d706553bd827e5dd5634817ee289c0b12bc45a553c5d759b8362358"
    assert hashlib.sha256(PM.DVAL.read_bytes()).hexdigest() == "cf2ba3fa87f434f72d195a6c6e96df6ad9b99ee0b7f887ff44625b9712177725"
    linked = sorted({lad[h]["partner_B"] for h, x in lad.items() if x["role"] == "train" and lad[h]["partner_B"] in set(test)})
    assert len(linked) == 32
    clean69 = [h for h in clean if h not in set(linked)]
    test159 = sorted(set(test) - set(linked))
    sets = {"dev+clean80": dev + clean, "dev": dev, "clean80": clean, "dev+clean69": dev + clean69, "test191": test, "test159": test159}
    D = {(r["rung"], r["host"]): float(r["D"]) for r in csv.DictReader(open(PM.DVAL))}
    man = FS1_EVAL if a.pair == "FS1" else A.EVAL
    row = {}
    for r in csv.DictReader(open(man)):
        if r["strength"] != "":
            continue
        if r["fam"] == "ladder" and r["rung"] in ("R4", "R3") and r["tool"] in ("opencv", "facemorpher"):
            row[(r["rung"], r["tool"], r["host"])] = r["id"]
        if r["fam"] == "splice" and r["rung"] in ("S4", "S3"):
            row[(r["rung"], "opencv", r["host"])] = r["id"]
    contrasts = {"R4_vs_R3_opencv": ("R4", "R3", "opencv"), "S4_vs_S3": ("S4", "S3", "opencv"),
                 "R4_vs_R3_facemorpher": ("R4", "R3", "facemorpher")}
    R = dict(pair=a.pair, seeds=seeds, mock=a.mock, status={}, contrasts={},
             label=("recipe at replication seeds 408-412, development plus clean test hosts, post hoc, not held-out"
                    if a.pair == "Sp" else ("post-freeze ablation rows at seeds 408-412, development plus clean test hosts, not held-out"
                                            if a.pair == "C" else "frozen networks' own seeds, development plus clean test hosts, post hoc")))
    nets = {}
    for arm in arms:
        for s in seeds:
            if a.mock:
                r = np.random.default_rng(s * 10 + {"A": 1, "B": 2, "Sb": 3, "Sp": 4, "SpV": 5, "BN": 6}[arm])
                x = {i: float(r.normal((1.0 if arm == "Sb" else 0.5) if rk[0] in ("R4", "S4") else 0.0, 1.0)) for rk, i in row.items()}
                why = "read"
            elif a.pair == "C" and arm in ("SpV", "BN"):
                sv = (A.OVERLAY["AB1"], A.MANDIR)
                A.OVERLAY["AB1"], A.MANDIR = C_OVERLAY, C_MANDIR
                try:
                    x, _, why = A.load(pathlib.Path("/mnt/t7/smad_next/AB1/c/results") / f"AB1C_{arm}_s{s}.tar", "AB1", arm)
                finally:
                    A.OVERLAY["AB1"], A.MANDIR = sv
                why = "read" if x is not None else why
            elif a.pair in ("Sp", "C"):
                x, _, why = A.load(pathlib.Path("/mnt/t7/smad_next/AB1/results") / f"AB1_{arm}_s{s}.tar", "AB1", arm)
                why = "read" if x is not None else why
            else:
                if arm == "Sp" and s not in (403, 404, 405):
                    continue
                x, why = load_fs1(arm, s)
            R["status"][f"{arm}_s{s}"] = why
            if x is not None:
                assert all(i in x and math.isfinite(x[i]) for i in row.values()), f"{arm}_s{s}: rows missing"
                nets[(arm, s)] = x

    def arrays(hosts, cname, x):
        pr, nr, tool = contrasts[cname]
        ph = [h for h in hosts if (pr, tool, h) in row and ("S4", h) in D]
        nh = [h for h in hosts if (nr, tool, h) in row and ("S3", h) in D]
        return (np.array([x[row[(pr, tool, h)]] for h in ph]), np.array([D[("S4", h)] for h in ph]),
                np.array([x[row[(nr, tool, h)]] for h in nh]), np.array([D[("S3", h)] for h in nh]))

    def components(hosts):
        hs = set(hosts)
        par = {h: h for h in hosts}

        def f(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x
        for h in hosts:
            p = lad[h]["partner_B"]
            if p in hs:
                par[f(h)] = f(p)
        comp = {}
        for h in hosts:
            comp.setdefault(f(h), []).append(h)
        return list(comp.values())
    rng = np.random.default_rng(20261120)
    for cname in contrasts:
        for sname, hosts in sets.items():
            comps = components(hosts)
            decides = (cname == "R4_vs_R3_opencv" and sname == "dev+clean80") or (cname == "S4_vs_S3" and sname == "clean80")
            draws = [rng.integers(0, len(comps), len(comps)) for _ in range(2000)] if decides else []
            res = dict(per_seed={}, n_components=len(comps))
            for (arm, s), x in nets.items():
                ps, pd, ns, nd = arrays(hosts, cname, x)
                res["per_seed"][f"{arm}_s{s}"] = dict(strat=PM.strat_auc(ps, pd, ns, nd), unstrat=C2.fauc(ps, ns), n_pos=len(ps), n_neg=len(ns))
            for first, o, role in pairs:
                rd = [s for s in seeds if (first, s) in nets and (o, s) in nets and res["per_seed"][f"{first}_s{s}"]["strat"] is not None
                      and res["per_seed"][f"{o}_s{s}"]["strat"] is not None]
                g = {s: res["per_seed"][f"{first}_s{s}"]["strat"] - res["per_seed"][f"{o}_s{s}"]["strat"] for s in rd}
                gu = {s: res["per_seed"][f"{first}_s{s}"]["unstrat"] - res["per_seed"][f"{o}_s{s}"]["unstrat"] for s in rd}
                out = dict(role=role, read_seeds=rd, gain=g, seed_mean=float(np.mean(list(g.values()))) if g else None,
                           unstrat_gain=gu, unstrat_seed_mean=float(np.mean(list(gu.values()))) if gu else None)
                need = 4 if role == "verdict" else 3
                if draws and len(rd) >= need:
                    bs, bu, n_unread = [], [], 0
                    for dr in draws:
                        hs = [h for k in dr for h in comps[k]]
                        vs, vu, ok = [], [], True
                        for s in rd:
                            st, un = [], []
                            for arm in (first, o):
                                ps, pd, ns, nd = arrays(hs, cname, nets[(arm, s)])
                                st.append(PM.strat_auc(ps, pd, ns, nd))
                                un.append(C2.fauc(ps, ns))
                            if None in st:
                                ok = False
                            else:
                                vs.append(st[0] - st[1])
                            vu.append(un[0] - un[1])
                        bu.append(np.mean(vu))
                        if ok:
                            bs.append(np.mean(vs))
                        else:
                            n_unread += 1
                    use_unstrat = (cname == "S4_vs_S3")          # amendment 5b: fixed, not data-dependent
                    if use_unstrat:
                        mean, gg, arr = out["unstrat_seed_mean"], gu, bu
                        extra_ok = out["seed_mean"] is not None and out["seed_mean"] > 0
                    else:
                        mean, gg, arr = out["seed_mean"], g, bs
                        extra_ok = out["unstrat_seed_mean"] > 0
                    lo, hi = float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))
                    npos = sum(v > 0 for v in gg.values())
                    present = mean >= 0.03 and lo > 0 and ((len(rd) == 5 and npos >= 4) or (len(rd) == 4 and npos == 4)) and extra_ok
                    v = "present" if present else ("absent" if hi < 0.03 else "inconclusive")
                    if role != "verdict":
                        v = "printed only: " + v
                    out.update(unreadable_draws=n_unread, unreadable_share=n_unread / len(draws),
                               decided_on="unstratified" if use_unstrat else "stratified", decision_seed_mean=mean,
                               ci=[lo, hi], ci995=[float(np.percentile(arr, 0.25)), float(np.percentile(arr, 99.75))],
                               ci_half_width=(hi - lo) / 2, n_positive=npos, verdict=v,
                               unstrat_ci=[float(np.percentile(bu, 2.5)), float(np.percentile(bu, 97.5))],
                               strat_ci_readable_draws=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else None)
                elif draws:
                    out["verdict"] = "not read (too few readable seeds)"
                res[f"{first}_minus_{o}"] = out
            R["contrasts"][f"{cname}|{sname}"] = res
    for first, o, role in pairs:
        prim = R["contrasts"]["R4_vs_R3_opencv|dev+clean80"][f"{first}_minus_{o}"]
        md = R["contrasts"]["R4_vs_R3_opencv|dev"][f"{first}_minus_{o}"]["seed_mean"]
        mc = R["contrasts"]["R4_vs_R3_opencv|clean80"][f"{first}_minus_{o}"]["seed_mean"]
        prim["dev_vs_clean80_seed_means"] = [md, mc]
        if md is not None and mc is not None and (md > 0) != (mc > 0) and str(prim.get("verdict", "")).endswith(("present", "absent")):
            prim["verdict_before_cap"] = prim["verdict"]
            prim["verdict"] = "inconclusive (sign disagreement between development and clean test hosts)"
    R["verdicts"] = {f"{first}_minus_{o}": dict(role=role,
                                                primary_R4_vs_R3=R["contrasts"]["R4_vs_R3_opencv|dev+clean80"][f"{first}_minus_{o}"].get("verdict"),
                                                secondary_S4_vs_S3_clean80=R["contrasts"]["S4_vs_S3|clean80"][f"{first}_minus_{o}"].get("verdict"))
                     for first, o, role in pairs}
    if not a.mock:
        sys.path.insert(0, str(HERE.parent / "adversary"))
        import check
        R["adv_floors"] = {f"{arm}_s{s}": {c: dict(all=check.exceeds(c, x), nuisance=check.exceeds(c, x, floor="nuisance"))
                                          for c in PM.ADV_CONTRASTS} for (arm, s), x in nets.items()}
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    print(json.dumps(R["verdicts"], indent=1))


if __name__ == "__main__":
    main()
