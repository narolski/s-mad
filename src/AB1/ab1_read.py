"""Protocol ablation and replication (AB1): the single registered read (prereg.md sections 4, 5, 6), development data only.

Inputs: result tars AB1_<arm>_s<seed>.tar (+ .sha256) for A, Sb, B, Sp, SbZ, SbH, SbS, AS (and SbL if run), all in --res
(default /mnt/t7/smad_next/AB1/results; registered branch R: AB1's own A and Sb, no SE1 network is read); the AB1 evaluation manifest ab1_eval.csv (pinned); the landmark_combined cue file
a14_lcomb.npz (pinned). C2P quantities use the unchanged functions of src/PN1/c2p_read.py (holdout, net_stats, fauc).
  python3 -I ab1_read.py --branch W|R --out OUT.json   (once; W = A and Sb are SE1's WCSS H100 fits, R = AB1's own)
  python3 -I ab1_read.py --mock [--mock-drop Sb_s408,Sb_s409] --out MOCK.json   (random scores; code path only)
Pre-run review fixes (13 Nov): F1 branch and H100-only reuse, F3 seed counting, F4 seed-mean decider, F7 provenance."""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import pathlib
import re
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("c2p_read", HERE.parent / "PN1" / "c2p_read.py")
C2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C2)
C2P_SHA = "45e72914d960214131a5b4a11aefd2e301a2236e908d77d20d94136c1d7d5840"

EVAL = pathlib.Path("/mnt/t7/smad_next/AB1/manifests/ab1_eval.csv")
EVAL_SHA = "93a5ba234f91e57951829c5536fabbe0f792ee4ad0a293f074aaca72f7465bd5"
FLOOR = pathlib.Path("/mnt/t7/smad_next/PN1/cues/a14_lcomb.npz")
FLOOR_SHA_FILE = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/tier1_a14/a14_lcomb_floor.sha256")
SEEDS = (408, 409, 410, 411, 412)
OWN = ("B", "Sp", "SbZ", "SbH", "SbS", "AS", "SbL")
PACK = "96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004"
OVERLAY = {"AB1": "171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149",
           "SE1": "de26d6ce3facc90a439209d690b099fea351ace91808a5256ba5bdee5ba27a7c"}   # SE1 registration c8bbaf0
MANDIR = pathlib.Path("/mnt/t7/smad_next/AB1/manifests")
FSMAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests")
T_CRIT4 = 2.7764451051977987                                    # Student t, 4 df, two-sided 95%
SIZES = C2.SIZES


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def tar_for(res, arm, s, branch):
    """Branch W: A and Sb are SE1's WCSS H100 fits (SE1_<arm>_s<seed>.tar). Branch R: AB1's own (AB1_<arm>_s<seed>.tar);
    SE1's networks are never read. Every other arm: the AB1 tar."""
    if arm in ("A", "Sb") and branch == "W":
        return res / f"SE1_{arm}_s{s}.tar", "SE1"
    return res / f"AB1_{arm}_s{s}.tar", "AB1"


def manifest_rows(arm):
    p = (FSMAN / f"train_{arm}.csv") if arm in ("A", "B", "Sb", "SbL") else (MANDIR / f"train_{arm}.csv")
    if arm == "SbL":
        p = FSMAN / "train_Sb.csv"
    return list(csv.DictReader(open(p)))


def load(tar, origin, arm):
    """(scores, train_scores, info) if the tar verifies and its provenance is right; else (None, None, why)."""
    shf = tar.parent / (tar.name + ".sha256")
    if not tar.exists() or not shf.exists():
        return None, None, "missing"
    if sha(tar) != shf.read_text().split()[0]:
        return None, None, "sha256 mismatch"
    T = tar.name[:-4]
    try:
        with tarfile.open(tar) as t:
            z = np.load(io.BytesIO(t.extractfile(f"{T}/scores_eval.npz").read()))
            zt = np.load(io.BytesIO(t.extractfile(f"{T}/scores_train.npz").read()))
            gpu = t.extractfile(f"{T}/gpu.txt").read().decode(errors="replace")
            ti = t.extractfile(f"{T}/task_info.txt").read().decode(errors="replace")
            log = t.extractfile(f"{T}/train.log").read().decode(errors="replace")
            meta = json.loads(t.extractfile(f"{T}/meta.json").read())
            env = t.extractfile(f"{T}/task.env").read().decode(errors="replace")
    except KeyError as e:
        return None, None, f"member missing: {e}"
    if "H100" not in gpu:
        return None, None, f"not an H100: {gpu.strip()}"
    steps = 12500 if arm == "SbL" else 6250
    if f"steps {steps} limit 0" not in ti or f"pack_sha256 {PACK}" not in ti:
        return None, None, f"task_info off: {ti.strip()}"
    if f"overlay_sha256 {OVERLAY[origin]}" not in ti:
        return None, None, f"overlay off: {ti.strip()}"
    if f"ARM={arm}" not in env:
        return None, None, f"task.env arm off: {env.strip()}"
    if int(meta.get("n_items", -1)) != len(manifest_rows(arm)) or int(meta.get("steps", -1)) != steps:
        return None, None, f"meta off: n_items {meta.get('n_items')} steps {meta.get('steps')}"
    losses = [float(x) for x in re.findall(r"loss[ =:]+(-?(?:inf|nan)|[-+0-9.eE]+)", log, flags=re.I)]
    if not losses or not all(math.isfinite(v) for v in losses):
        return None, None, "no finite loss in train.log"
    sc = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
    tr = dict(zip([str(i) for i in zt["id"]], zt["logit"].astype(float)))
    return sc, tr, gpu.strip()


def pools(M):
    def ids(**kw):
        return [r["id"] for r in M if all(r[k] == v for k, v in kw.items())]
    P = dict(
        lc_m=ids(fam="ffhq_lcomb", rung="landmark_combined_orig"), lc_g=ids(fam="ffhq_lcomb", rung="landmark_combined_resmatch"),
        S3=ids(fam="splice", role="dev", rung="S3"), S0=ids(fam="splice", role="dev", rung="S0"), S4=ids(fam="splice", role="dev", rung="S4"),
        R2w=ids(fam="ladder", role="dev", rung="R2w", tool="opencv", strength=""),
        R2w4=ids(fam="ladder", role="dev", rung="R2w4", tool="opencv", strength=""),
        zero=ids(fam="af0", role="dev", rung="zero"),
        halves=ids(fam="af0", role="dev", rung="halfA") + ids(fam="af0", role="dev", rung="halfB"),
        soft61=ids(fam="ladder", role="dev", rung="R0", strength="61") + ids(fam="af0", role="dev", rung="photo", strength="61"),
        soft112=ids(fam="ladder", role="dev", rung="R0", strength="112") + ids(fam="af0", role="dev", rung="photo", strength="112"),
        camera=ids(fam="ladder", role="dev", rung="R0", strength="") + ids(fam="af0", role="dev", rung="photo", strength=""),
    )
    P["warp"] = P["R2w"] + P["R2w4"] + P["zero"]
    P["soft"] = P["soft61"] + P["soft112"]
    n = {k: len(v) for k, v in P.items()}
    assert (n["lc_m"], n["lc_g"], n["S3"], n["S0"], n["S4"], n["warp"], n["halves"], n["soft"], n["camera"]) == \
        (1000, 2000, 100, 100, 100, 371, 610, 452, 226), n
    return P


def share(x, ids):
    return float(np.mean([x[i] > 0 for i in ids]))


def verdict(k_sup, k_fal, n):
    if n <= 3:
        return "not read (too few seeds)"
    need = 4
    if (n == 5 and k_sup >= need) or (n == 4 and k_sup == 4):
        return "supported"
    if (n == 5 and k_fal >= need) or (n == 4 and k_fal == 4):
        return "falsified"
    return "inconclusive, no claim"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="/mnt/t7/smad_next/AB1/results")
    ap.add_argument("--out", required=True)
    ap.add_argument("--branch", choices=("R",))          # branch W (SE1 reuse) was dropped at registration
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-drop", default="")
    a = ap.parse_args()
    assert a.mock or a.branch, "--branch W|R is required for the real read (prereg section 3)"
    drop = set(x for x in a.mock_drop.split(",") if x)
    assert sha(HERE.parent / "PN1" / "c2p_read.py") == C2P_SHA, "c2p_read.py not at its pin"
    assert sha(EVAL) == EVAL_SHA
    assert sha(FLOOR) == FLOOR_SHA_FILE.read_text().split()[0]
    M = list(csv.DictReader(open(EVAL)))
    P = pools(M)
    natp, natm, pairs, mpairs = C2.holdout(M)
    rng = np.random.default_rng(C2.RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(C2.B_BOOT)] for z in SIZES}
    z = np.load(FLOOR)
    cid = {str(i): c for i, c in zip(z["ids"], z["cues"])}
    CM = np.array([cid[i] for i in P["lc_m"]]); CG = np.array([cid[i] for i in P["lc_g"]])
    rng2 = np.random.default_rng(20261118)
    draws = [(rng2.integers(0, len(CM), len(CM)), rng2.integers(0, len(CG), len(CG))) for _ in range(2000)]

    def fmax(im, ig):
        v = [C2.fauc(CM[im, j], CG[ig, j]) for j in range(CM.shape[1])]
        return max(max(u, 1 - u) for u in v)
    fdraw = np.array([fmax(im, ig) for im, ig in draws])
    R = dict(mock=a.mock, branch=a.branch, mock_drop=sorted(drop), floor_best_auc=fmax(np.arange(len(CM)), np.arange(len(CG))), baseline27_s_lad=0.814,
             networks={}, status={})
    res = pathlib.Path(a.res)
    need_c2p = set(natp) | set(natm) | {f"{i}_{zz}" for zz in SIZES for i in pairs[zz]} | \
        {f"{i}_{zz}" for zz in SIZES for i in mpairs[zz]}
    need = need_c2p | {i for k in ("lc_m", "lc_g", "S3", "S0", "S4", "warp", "halves", "soft", "camera") for i in P[k]}
    nets = {}
    for arm in ("A", "Sb") + OWN:
        for s in SEEDS:
            key = f"{arm}_s{s}"
            if a.mock:
                if arm == "SbL" or key in drop:
                    R["status"][key] = "mock: dropped"
                    continue
                r = np.random.default_rng(s * 100 + sum(map(ord, arm)))
                shift = 1.0 if arm in ("A", "SbS") else 0.05          # storage reaction for A (and SbS), as c2p_read's mock
                x = {rr["id"]: float(r.normal((1.0 if rr["label"] == "1" else -2.0) +
                                              (shift if rr["fam"] == "ms1ffhq" and rr["strength"] in SIZES and rr["label"] == "0" else 0.0), 1.5))
                     for rr in M}
                xtr = {}
                why = "mock"
            else:
                tp, origin = tar_for(res, arm, s, a.branch)
                x, xtr, why = load(tp, origin, arm)
            if x is None:
                R["status"][key] = why
                continue
            if not need <= set(x) or not all(math.isfinite(x[i]) for i in need):
                R["status"][key] = "incomplete or non-finite scores"
                continue
            R["status"][key] = f"read ({why})"
            m = np.array([x[i] for i in P["lc_m"]]); g = np.array([x[i] for i in P["lc_g"]])
            sd = np.array([C2.fauc(m[im], g[ig]) for im, ig in draws])
            st = dict(
                lcomb_auc=C2.fauc(m, g), lcomb_ci=[float(np.percentile(sd, 2.5)), float(np.percentile(sd, 97.5))],
                lcomb_minus_floor_lo=float(np.percentile(sd - fdraw, 2.5)),
                S3=share(x, P["S3"]), S0=share(x, P["S0"]),
                S0_vs_S4_auc=C2.fauc([x[i] for i in P["S4"]], [x[i] for i in P["S0"]]),
                warp=share(x, P["warp"]), warp_R2w=share(x, P["R2w"]), warp_R2w4=share(x, P["R2w4"]), warp_zero=share(x, P["zero"]),
                halves=share(x, P["halves"]), camera=share(x, P["camera"]),
                soft=share(x, P["soft"]), soft61=share(x, P["soft61"]), soft112=share(x, P["soft112"]),
                ffhq_native_photo_flag=share(x, natp))
            st["dsoft"] = st["soft"] - st["camera"]          # "development storage rise" (review F2 wording)
            if xtr:
                kinds = {r["id"]: r["kind"] for r in manifest_rows(arm)}
                st["train_flag_by_kind"] = {k: float(np.mean([xtr[i] > 0 for i in xtr if kinds.get(i) == k]))
                                            for k in sorted(set(kinds.values())) if any(kinds.get(i) == k for i in xtr)}
            st["c2p"] = C2.net_stats(x, natp, natm, pairs, mpairs, boot)
            nets[(arm, s)] = st
            R["networks"][key] = st

    def ok(*ks):
        return all(k in nets for k in ks)
    V = {}
    # A's C2P control and the C2P X rule (C2P.3, unchanged)
    ctrl = {zz: {s: ok(("A", s)) and nets[("A", s)]["c2p"][zz]["d_flag"] >= 0.05 and nets[("A", s)]["c2p"][zz]["d_mean_sd"] > 0
                 for s in SEEDS} for zz in SIZES}

    def xpass(X, base, s, zz):
        if not ctrl[zz][s] or not ok((X, s)):
            return False
        x, A = nets[(X, s)]["c2p"][zz], nets[(base, s)]["c2p"][zz]
        return bool(x["d_flag"] <= A["d_flag"] / 3 and abs(x["d_mean_sd"]) <= A["d_mean_sd"] / 3
                    and x["d_flag"] <= 0.05 and x["d_flag_upper95"] <= 0.08)

    def c2p_verdict(X):
        """C2P.3 unchanged (a lost seed keeps the denominator 5 and counts as not passing), gated by the section-5 seed
        count (review F3): with 3 or fewer read seeds of X among A's control seeds at either size, "not read"."""
        per = {zz: {s: xpass(X, "A", s, zz) for s in SEEDS} for zz in SIZES}
        npass = {zz: sum(per[zz].values()) for zz in SIZES}
        nctl = {zz: sum(ctrl[zz].values()) for zz in SIZES}
        nread = {zz: sum(1 for s in SEEDS if ctrl[zz][s] and ok((X, s))) for zz in SIZES}
        if any(nctl[zz] <= 3 for zz in SIZES):
            v = "uninformative"
        elif any(nread[zz] <= 3 for zz in SIZES):
            v = "not read (too few seeds)"
        elif all(npass[zz] >= 4 for zz in SIZES):
            v = "passes"
        elif any(npass[zz] <= 1 and nctl[zz] >= 4 for zz in SIZES):
            v = "fails"
        else:
            v = "inconclusive, no claim"
        return dict(per_seed=per, n_pass=npass, n_control=nctl, n_read=nread, verdict=v)
    V["A_control"] = ctrl
    for X in ("Sb", "B"):
        c = c2p_verdict(X)
        # amendment 1 (13 Nov, review REVIEW_PN1_C2P_20261113.md F7/Q5): no earlier C2P pass exists, so R1 is a first test
        V[f"R1_{X}"] = dict(c2p=c, verdict={"passes": "first test at seeds 408-412: passed",
                                            "fails": "first test at seeds 408-412: not passed",
                                            "uninformative": "first test at seeds 408-412: uninformative"}.get(c["verdict"], c["verdict"]))
        vals = {zz: {s: nets[(X, s)]["c2p"][zz]["d_mean_att_sd"] for s in SEEDS if ok((X, s))} for zz in SIZES}
        sup = any(sum(1 for v in vals[zz].values() if v <= -0.20) >= 4 for zz in SIZES)
        fal = all(sum(1 for v in vals[zz].values() if v >= -0.10) >= 4 for zz in SIZES)
        hv = "supported" if sup else ("falsified" if fal else "inconclusive")
        if any(len(vals[zz]) <= 3 for zz in SIZES):
            hv = "not read (too few seeds)"
        V[f"H_new_1_{X}"] = dict(values=vals, verdict=hv)
    # R2 contrast 1 (FS1 v4)
    rd = [s for s in SEEDS if ok(("A", s), ("B", s), ("Sb", s))]
    t1 = [s for s in rd if nets[("B", s)]["lcomb_auc"] < 0.95]
    meets = {s: bool(nets[("Sb", s)]["lcomb_auc"] - nets[("B", s)]["lcomb_auc"] >= 0.05 and
                     nets[("Sb", s)]["lcomb_auc"] - nets[("A", s)]["lcomb_auc"] >= -0.02) for s in t1}
    k, n = sum(meets.values()), len(t1)
    c1 = "not read (too few seeds)" if n <= 3 else ("replicated" if (n == 5 and k >= 4) or (n == 4 and k == 4)
                                                     else ("not replicated" if k <= 1 else "inconclusive, no claim"))
    floor_all = bool(t1) and all(nets[("Sb", s)]["lcomb_minus_floor_lo"] > 0 for s in t1)
    V["R2_contrast1"] = dict(read_seeds=rd, testable=t1, meets=meets, verdict=c1, floor_exceeded_all=floor_all)
    # H-ab1 (ratio rule) and H-ab1s (AS as an X against A)
    rho = {zz: {s: (nets[("SbS", s)]["c2p"][zz]["d_flag"] / nets[("A", s)]["c2p"][zz]["d_flag"])
                for s in SEEDS if ctrl[zz][s] and ok(("SbS", s))} for zz in SIZES}
    nctl = {zz: sum(ctrl[zz].values()) for zz in SIZES}
    def k_of(n, k):
        return (n == 5 and k >= 4) or (n == 4 and k == 4)
    if any(nctl[zz] <= 3 for zz in SIZES):
        h1 = "uninformative"
    elif any(len(rho[zz]) <= 3 for zz in SIZES):
        h1 = "not read (too few seeds)"
    elif all(k_of(len(rho[zz]), sum(v >= 0.5 for v in rho[zz].values())) for zz in SIZES):
        h1 = "supported"
    elif all(k_of(len(rho[zz]), sum(v <= 1 / 3 for v in rho[zz].values())) for zz in SIZES):
        h1 = "falsified"
    else:
        h1 = "inconclusive, no claim"
    V["H_ab1"] = dict(rho=rho, verdict=h1, SbS_c2p=c2p_verdict("SbS"))
    cas = c2p_verdict("AS")
    V["H_ab1s"] = dict(c2p=cas, verdict={"passes": "supported", "fails": "falsified"}.get(cas["verdict"], cas["verdict"]),
                       lcomb_minus_A={s: nets[("AS", s)]["lcomb_auc"] - nets[("A", s)]["lcomb_auc"] for s in SEEDS if ok(("AS", s), ("A", s))})

    def rise_rule(X, getter, up=0.05, lo=0.01, base="Sb"):
        """Decider (review F4): seed mean of the paired rise with a Student-t 95% interval over read seeds; supported if
        mean >= +0.05 and lower bound > 0; falsified if upper bound < +0.05; otherwise inconclusive; n <= 3: not read.
        The per-seed rule (>= +0.05 / <= +0.01 on 4 of 5) is printed as a secondary verdict."""
        rs = {s: getter(nets[(X, s)]) - getter(nets[(base, s)]) for s in SEEDS if ok((X, s), (base, s))}
        n = len(rs)
        out = dict(rise=rs, n=n, per_seed_verdict=verdict(sum(v >= up for v in rs.values()), sum(v <= lo for v in rs.values()), n))
        if n <= 3:
            out.update(verdict="not read (too few seeds)")
            return out
        v = np.array(list(rs.values()))
        t = {5: T_CRIT4, 4: 3.182446305284263}[n]
        mu, half = float(v.mean()), float(t * v.std(ddof=1) / math.sqrt(n))
        out.update(mean=mu, ci=[mu - half, mu + half],
                   verdict="supported" if (mu >= up and mu - half > 0) else ("falsified" if mu + half < up else "inconclusive, no claim"))
        return out
    V["H_ab2"] = rise_rule("SbZ", lambda t: t["warp"])
    V["H_ab3"] = rise_rule("SbH", lambda t: t["dsoft"])
    V["H_ab3s"] = rise_rule("SbS", lambda t: t["dsoft"])
    # H-ab4: the registered Sp predictions at 408-412
    p = {}
    for s in SEEDS:
        if ok(("Sp", s), ("Sb", s)):
            sp, sb = nets[("Sp", s)], nets[("Sb", s)]
            p[s] = dict(pred1=bool(sp["S0"] >= max(2 * sb["S0"], sb["S0"] + 0.10)),
                        pred2=bool(sp["S0_vs_S4_auc"] <= sb["S0_vs_S4_auc"] - 0.05), S3_rise=sp["S3"] - sb["S3"])
    V["H_ab4"] = dict(per_seed=p, verdict=verdict(sum(v["pred1"] and v["pred2"] for v in p.values()),
                                                   sum((not v["pred1"]) and (not v["pred2"]) for v in p.values()), len(p)))
    # attribution table (secondary)
    reads = dict(c2p_fm61=lambda t: t["c2p"]["fm61"]["d_flag"], c2p_amsl112=lambda t: t["c2p"]["amsl112"]["d_flag"],
                 warp=lambda t: t["warp"], dsoft=lambda t: t["dsoft"], S3=lambda t: t["S3"], S0=lambda t: t["S0"])
    lab = {"supported": "removing it brings the reaction back", "falsified": "not needed for it, given the others"}
    tab = {}
    for X in ("SbZ", "SbH", "SbS", "Sp"):
        for rn, g in reads.items():
            c = rise_rule(X, g)
            c["label"] = lab.get(c["verdict"], c["verdict"])
            tab[f"{X}|{rn}"] = c
    V["attribution_table_secondary"] = tab
    V["cost_lcomb_minus_Sb"] = {X: {s: nets[(X, s)]["lcomb_auc"] - nets[("Sb", s)]["lcomb_auc"] for s in SEEDS if ok((X, s), ("Sb", s))}
                                for X in ("B", "Sp", "SbZ", "SbH", "SbS", "SbL")}
    # conditional SbL
    if any(("SbL", s) in nets for s in SEEDS):
        rs = {s: (nets[("SbL", s)]["S3"] - nets[("Sb", s)]["S3"], nets[("SbL", s)]["lcomb_auc"] - nets[("Sb", s)]["lcomb_auc"])
              for s in SEEDS if ok(("SbL", s), ("Sb", s))}
        V["SbL"] = dict(per_seed=rs, verdict=verdict(sum(d3 <= -0.10 and da >= 0.02 for d3, da in rs.values()),
                                                      sum(abs(d3) < 0.03 and da < 0.01 for d3, da in rs.values()), len(rs)),
                        above_0886={s: nets[("SbL", s)]["lcomb_auc"] > 0.886 for s in rs}, c2p_guard=c2p_verdict("SbL"))
    else:
        V["SbL"] = "not run (condition not met)"
    R["verdicts"] = V
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    short = {k: (v["verdict"] if isinstance(v, dict) and "verdict" in v else None) for k, v in V.items()}
    print(json.dumps({k: v for k, v in short.items() if v}, indent=1))
    print("not read:", {k: v for k, v in R["status"].items() if not v.startswith("read")})


if __name__ == "__main__":
    main()
