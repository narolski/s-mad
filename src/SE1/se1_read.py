"""Seam-shortcut training arm (SE1): the registered reader (prereg.md sections 6-8). Run once on the 15 result tars.

Inputs: /mnt/t7/smad_next/SE1/results/SE1_<arm>_s<seed>.tar (scores_eval.npz: id, logit; train.log) for arms A, Sb, SE
and seeds 408-412; the evaluation manifest se_eval.csv (pinned); the 27-statistic baseline file baseline27_se1.json
(computed and committed before any tar is pulled). Storage reads reuse src/PN1/c2p_read.py's functions unchanged.
  python3 -I se1_read.py --out /home/narolski/smad-next/experiments/SE1_seam-shortcut-training-arm/se1_read.json
  python3 -I se1_read.py --mock --out /tmp/...      (random scores; tests the code path only)
"""
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

ARMS = ("A", "Sb", "SE")
SEEDS = (408, 409, 410, 411, 412)
SIZES = ("fm61", "amsl112")
RES = pathlib.Path("/mnt/t7/smad_next/SE1/results")
EVAL = pathlib.Path("/mnt/t7/smad_next/SE1/manifests/se_eval.csv")
EVAL_SHA = "6dcef964d8ca3024d353aaa1e568e42ba2f2454b1f1a36442311aa5f9b598f7c"
BASE = pathlib.Path("/home/narolski/smad-next/experiments/SE1_seam-shortcut-training-arm/baseline27_se1.json")
_spec = importlib.util.spec_from_file_location("c2p", "/home/narolski/smad-next/src/PN1/c2p_read.py")
C2P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C2P)
fauc = C2P.fauc


def cp(k, n, a=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return [lo, hi]


def pools(M):
    def sel(**kw):
        return [r["id"] for r in M if all(r[k] == v for k, v in kw.items())]
    d = dict(role="dev")
    P = {
        # genuine (camera) pools
        "G_devR0": sel(fam="ladder", rung="R0", strength="", **d),
        "G_af0photo": sel(fam="af0", rung="photo", strength="", **d),
        "G_ffhq_bona": sel(fam="ffhq", rung="ffhq_bona_orig"),
        "G_ms1_native": sel(fam="ms1ffhq", rung="photo", strength=""),
        # same-person (target and printed)
        "S3_cv": sel(fam="splice", rung="S3", tool="opencv", **d),
        "S3_fm": sel(fam="splice", rung="S3", tool="facemorpher", **d),
        "R3_cv": sel(fam="ladder", rung="R3", strength="", tool="opencv", **d),
        "R3_fm": sel(fam="ladder", rung="R3", strength="", tool="facemorpher", **d),
        "R3m_cv": sel(fam="ladder", rung="R3m", strength="", tool="opencv", **d),
        "R3m_fm": sel(fam="ladder", rung="R3m", strength="", tool="facemorpher", **d),
        "selfm_af0": sel(fam="af0", rung="selfm", **d),
        "S0_cv": sel(fam="splice", rung="S0", tool="opencv", **d),
        "S0_fm": sel(fam="splice", rung="S0", tool="facemorpher", **d),
        "R2w_cv": sel(fam="ladder", rung="R2w", strength="", tool="opencv", **d),
        "R2w4_cv": sel(fam="ladder", rung="R2w4", strength="", tool="opencv", **d),
        "zero_af0": sel(fam="af0", rung="zero", **d),
        # two-person
        "R4_cv": sel(fam="ladder", rung="R4", strength="", tool="opencv", **d),
        "R4_fm": sel(fam="ladder", rung="R4", strength="", tool="facemorpher", **d),
        "R3_cv61": sel(fam="ladder", rung="R3", strength="61", tool="opencv", **d),
        "R3_cv112": sel(fam="ladder", rung="R3", strength="112", tool="opencv", **d),
        "R4_cv61": sel(fam="ladder", rung="R4", strength="61", tool="opencv", **d),
        "R4_cv112": sel(fam="ladder", rung="R4", strength="112", tool="opencv", **d),
        "S4_cv": sel(fam="splice", rung="S4", tool="opencv", **d),
        "S4_fm": sel(fam="splice", rung="S4", tool="facemorpher", **d),
        "u50_af0": sel(fam="af0", rung="u50", **d),
        "lcomb_m": sel(fam="ffhq_lcomb", rung="landmark_combined_orig"),
        "lcomb_g": sel(fam="ffhq_lcomb", rung="landmark_combined_resmatch"),
        "ffhq_lcomplete_m": sel(fam="ffhq", rung="landmark_complete_orig"),
        "ffhq_lcomplete_resmatch_g": sel(fam="ffhq", rung="landmark_complete_resmatch"),
    }
    expect = dict(G_devR0=100, G_af0photo=126, G_ffhq_bona=2000, G_ms1_native=300, S3_cv=100, S3_fm=100, R3_cv=100,
                  R3_fm=100, R4_cv=100, R4_fm=100, R3_cv61=100, R3_cv112=100, R4_cv61=100, R4_cv112=100, S4_cv=100, S4_fm=100, selfm_af0=126, lcomb_m=1000, lcomb_g=2000)
    for k, n in expect.items():
        assert len(P[k]) == n, (k, len(P[k]))
    return P


BLOCK = {"a100": None}      # set in main: per-arm (results folder, task prefix)


def load(arm, seed, M, mock):
    res, pre = BLOCK["paths"][arm]
    T = f"{pre}_{arm}_s{seed}"
    if mock:
        r = np.random.default_rng(seed * 7 + len(arm))
        L = {}
        for row in M:
            base = -3.0 if row["label"] == "0" else 1.5
            if row["rung"] in ("R3", "R3m", "S3", "selfm") and arm != "SE":
                base = 0.5
            shift = (1.0 if arm == "A" else 0.05) if row["strength"] in ("fm61", "amsl112") and row["label"] == "0" else 0
            if pre == "AB1" and (row["rung"] == "selfm" or (row["fam"] == "splice" and row["tool"] == "facemorpher")):
                continue                              # AB1's ab1_eval.csv has no such rows
            L[row["id"]] = float(r.normal(base + shift, 1.2))
        return L, dict(task=T, mock=True, finite_loss=True)
    tp = res / f"{T}.tar"
    if not tp.exists():
        return None, dict(task=T, missing=True)
    h = hashlib.sha256(tp.read_bytes()).hexdigest()
    ok = (res / f"{T}.tar.sha256").exists() and (res / f"{T}.tar.sha256").read_text().split()[0] == h
    with tarfile.open(tp) as t:
        z = np.load(io.BytesIO(t.extractfile(f"{T}/scores_eval.npz").read()))
        zt = np.load(io.BytesIO(t.extractfile(f"{T}/scores_train.npz").read()))
        log = t.extractfile(f"{T}/train.log").read().decode(errors="replace")
        gpu = t.extractfile(f"{T}/gpu.txt").read().decode(errors="replace").strip()
        ti = t.extractfile(f"{T}/task_info.txt").read().decode(errors="replace")
        env = t.extractfile(f"{T}/env.txt").read().decode(errors="replace").strip()
    L = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
    Ltr = {}                                          # scores_train.npz is keyed by path and carries the row kind
    for k, v in zip([str(x) for x in zt["kind"]], zt["logit"].astype(float)):
        Ltr.setdefault(k, []).append(v)
    losses = [float(x) for x in re.findall(r"loss[ =:]+(-?(?:inf|nan)|[-+0-9.eE]+)", log, flags=re.I)]
    fin = bool(losses) and all(math.isfinite(v) for v in losses) and all(math.isfinite(v) for v in L.values())
    full = " steps 6250 limit 0" in " " + ti.replace("\n", " ")
    prov = {"SE1": "overlay_sha256 de26d6ce3facc90a439209d690b099fea351ace91808a5256ba5bdee5ba27a7c",
            "SE1H": "overlay_sha256 de26d6ce3facc90a439209d690b099fea351ace91808a5256ba5bdee5ba27a7c",
            "AB1": "overlay_sha256 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149"}[pre]
    full = full and prov in ti and "96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004" in ti
    if pre in ("SE1H", "AB1"):
        full = full and "H100" in gpu
    return L, dict(task=T, sha256=h, sha_ok=ok, finite_loss=fin, full_run=full, gpu=gpu, env=env, train_logits=Ltr,
                   last_loss=losses[-1] if losses else None)


def flag(L, ids):
    v = np.array([L[i] for i in ids])
    k = int((v > 0).sum())
    return dict(rate=k / len(v), k=k, n=len(v), ci=cp(k, len(v)))


def miss(L, ids):
    v = np.array([L[i] for i in ids])
    k = int((v <= 0).sum())
    return dict(rate=k / len(v), k=k, n=len(v), ci=cp(k, len(v)))


def auc(L, pos, neg):
    return fauc([L[i] for i in pos], [L[i] for i in neg])


def auc_fast(p, n):
    from scipy.stats import rankdata
    r = rankdata(np.r_[p, n])[: len(p)]
    return float((r.sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n)))


def count(per, n_read):
    """registered seed counting (prereg section 7): returns met / not met / inconclusive / not read."""
    k = sum(1 for v in per.values() if v)
    if n_read == 5:
        return "met" if k >= 4 else ("not met" if k <= 1 else "inconclusive")
    if n_read == 4:
        return "met" if k == 4 else ("not met" if k <= 1 else "inconclusive")
    return "not read (too few seeds)"


def leg(point, lo, hi, bar, kind):
    """seed-mean leg (prereg 7.2 / 7.4): kind 'ge' = point >= bar is met, not met if hi < bar;
    kind 'le' = point <= bar is met, not met if lo > bar; otherwise inconclusive."""
    if kind == "ge":
        v = "met" if point >= bar else ("not met" if hi < bar else "inconclusive")
    else:
        v = "met" if point <= bar else ("not met" if lo > bar else "inconclusive")
    return dict(point=point, ci=[lo, hi], bar=bar, verdict=v)


def combine(vs):
    if all(v == "met" for v in vs):
        return "met"
    if any(v == "not met" for v in vs):
        return "not met"
    if any(v.startswith("not read") for v in vs):
        return "not read (too few seeds)"
    return "inconclusive"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--block", choices=("a100", "h100"), default="a100",
                    help="a100: SE1's own A, Sb, SE (rented A100 PCIe); h100: amendment SE1-A1, SE from SE1 WCSS fits, "
                         "A and Sb from AB1's WCSS H100 fits (ab1_eval.csv rows only)")
    ap.add_argument("--platformcheck", action="append", default=[], help="SE1_platformcheck_*.tar, one per lease (printed only)")
    a = ap.parse_args()
    assert hashlib.sha256(EVAL.read_bytes()).hexdigest() == EVAL_SHA
    if a.block == "a100":
        BLOCK["paths"] = {x: (RES, "SE1") for x in ARMS}
    else:
        ab1 = pathlib.Path("/mnt/t7/smad_next/AB1/results")
        ab1read = sorted(pathlib.Path("/home/narolski/smad-next/experiments/AB1_protocol-ablation-and-replication").glob("ab1_read*.json"))
        ab1read = [q for q in ab1read if "mock" not in q.name]
        if not ab1read and not a.mock:
            raise SystemExit("AB1's registered read (ab1_read*.json) is not there yet: the H100 block is read only after it")
        BLOCK["paths"] = {"A": (ab1, "AB1"), "Sb": (ab1, "AB1"), "SE": (pathlib.Path("/mnt/t7/smad_next/SE1/results_h100"), "SE1H")}
    M = list(csv.DictReader(open(EVAL)))
    P = pools(M)
    base = json.load(open(BASE)) if BASE.exists() else None
    if base is None and not a.mock:
        raise SystemExit("baseline27_se1.json missing: it must be committed before the read")
    natp, natm, pairs, mpairs = C2P.holdout(M)
    rng = np.random.default_rng(C2P.RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(C2P.B_BOOT)] for z in SIZES}
    nets, info, raw = {}, {}, {}
    for arm in ARMS:
        for s in SEEDS:
            L, inf = load(arm, s, M, a.mock)
            Ltr = inf.pop("train_logits", None)
            info[f"{arm}_s{s}"] = inf
            if L is None or not inf.get("finite_loss") or (not a.mock and not (inf.get("sha_ok") and inf.get("full_run"))):
                continue
            if a.block == "h100" and arm != "SE":   # AB1's ab1_eval.csv lacks the FaceMorpher splices and AF0 self-morphs
                need = {i for k, v in P.items() if k not in ("S3_fm", "S0_fm", "S4_fm", "selfm_af0") for i in v} | \
                    {r["id"] for r in M if r["fam"] == "ms1ffhq"}
                missing = [i for i in need if i not in L]
            else:
                missing = [i for i in M if i["id"] not in L]
            if missing:
                inf["missing_rows"] = len(missing)
                continue
            n = {}
            for k in ("G_devR0", "G_af0photo", "G_ffhq_bona", "G_ms1_native", "S3_cv", "S3_fm", "R3_cv", "R3_fm",
                      "R3_cv61", "R3_cv112", "R3m_cv", "R3m_fm", "selfm_af0", "S0_cv", "S0_fm", "R2w_cv", "R2w4_cv",
                      "zero_af0", "ffhq_lcomplete_resmatch_g", "lcomb_g"):
                n[f"flag_{k}"] = flag(L, P[k]) if all(i in L for i in P[k]) else None
            for k in ("R4_cv", "R4_fm", "R4_cv61", "R4_cv112", "S4_cv", "S4_fm", "u50_af0", "lcomb_m", "ffhq_lcomplete_m"):
                n[f"miss_{k}"] = miss(L, P[k]) if all(i in L for i in P[k]) else None
            n["auc_lcomb"] = auc(L, P["lcomb_m"], P["lcomb_g"])
            for t in ("cv", "fm"):
                n[f"auc_R4_vs_R3_{t}"] = auc(L, P[f"R4_{t}"], P[f"R3_{t}"])
                n[f"auc_S4_vs_S3_{t}"] = auc(L, P[f"S4_{t}"], P[f"S3_{t}"]) if all(i in L for i in P[f"S3_{t}"] + P[f"S4_{t}"]) else None
                n[f"auc_R4_vs_R3m_{t}"] = auc(L, P[f"R4_{t}"], P[f"R3m_{t}"])
                n[f"auc_S3_vs_S0_{t}"] = auc(L, P[f"S3_{t}"], P[f"S0_{t}"]) if all(i in L for i in P[f"S3_{t}"] + P[f"S0_{t}"]) else None
            n["storage"] = C2P.net_stats(L, natp, natm, pairs, mpairs, boot)
            if Ltr:                                          # printed (section 9): own-rule flags on training rows by kind
                n["train_rows_flag"] = {k: float(np.mean(np.array(v) > 0)) for k, v in Ltr.items()}
            nets[(arm, s)] = n
            raw[(arm, s)] = L
    read = [s for s in SEEDS if all((x, s) in nets for x in ARMS)]
    R = dict(block=a.block, mock=a.mock, info=info, envs={k: v.get("env") for k, v in info.items()}, read_seeds=read, n_read=len(read),
             per_network={f"{k[0]}_s{k[1]}": v for k, v in nets.items()}, baseline=base)

    def per(fn):
        return {s: bool(fn(s)) for s in read}

    se = lambda s: nets[("SE", s)]  # noqa: E731
    sb = lambda s: nets[("Sb", s)]  # noqa: E731
    # ---- seed means with bootstrap (images within class / hosts; same draws for every network), rng 20261142
    brng = np.random.default_rng(20261142)
    keys = ("lcomb_m", "lcomb_g", "R4_cv", "R4_fm", "S4_cv", "S3_cv", "R3_cv", "G_ffhq_bona", "G_ms1_native")
    draws = {k: [brng.integers(0, len(P[k]), len(P[k])) for _ in range(2000)] for k in keys}

    def arr(arm, s, k):
        return np.array([raw[(arm, s)][i] for i in P[k]])

    def seedmean(stat):
        """stat(arm, s, idx) -> value; returns point (mean over read seeds of SE - Sb) and 95% bootstrap interval"""
        if not read:
            return None
        pt = float(np.mean([stat("SE", s, None) - stat("Sb", s, None) for s in read]))
        bs = [float(np.mean([stat("SE", s, b) - stat("Sb", s, b) for s in read])) for b in range(2000)]
        return pt, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    def sel(arm, s, k, b):
        v = arr(arm, s, k)
        return v if b is None else v[draws[k][b]]

    def sm_abs(stat):
        pt = float(np.mean([stat("SE", s, None) for s in read]))
        bs = [float(np.mean([stat("SE", s, b) for s in read])) for b in range(2000)]
        return pt, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    # section 7.1 target (per seed, counted)
    tgt = per(lambda s: se(s)["flag_S3_cv"]["rate"] <= 0.10 and se(s)["flag_R3_cv"]["rate"] <= 0.10
              and se(s)["flag_R3_cv61"]["rate"] <= 0.20 and se(s)["flag_R3_cv112"]["rate"] <= 0.20)
    half = per(lambda s: 2 * se(s)["flag_S3_cv"]["k"] <= sb(s)["flag_S3_cv"]["k"]
               and 2 * se(s)["flag_R3_cv"]["k"] <= sb(s)["flag_R3_cv"]["k"])
    fmx = per(lambda s: se(s)["flag_S3_fm"]["rate"] <= 0.20 and se(s)["flag_R3_fm"]["rate"] <= 0.20)
    T = count(tgt, len(read))
    T_half = count(half, len(read))
    if T == "met":
        tv = "target met"
    elif T_half == "met":
        tv = "reduced, not removed"
    elif T.startswith("not read"):
        tv = T
    else:
        tv = "not met" if T == "not met" else "inconclusive, no claim"
    R["T_target"] = dict(per_seed=tgt, half_of_Sb_per_seed=half, count=T, count_half=T_half, verdict=tv,
                         heldout_engine=dict(per_seed=fmx, count=count(fmx, len(read))))
    if len(read) >= 1:
        R["T_target"]["seed_mean_SE_minus_Sb"] = {
            k: seedmean(lambda arm, s, b, k=k: float((sel(arm, s, k, b) > 0).mean())) for k in ("S3_cv", "R3_cv")}
    # section 7.2 guard G1 (seed means)
    if len(read) >= 4:
        d_auc = seedmean(lambda arm, s, b: auc_fast(sel(arm, s, "lcomb_m", b), sel(arm, s, "lcomb_g", b)))
        d_ml = seedmean(lambda arm, s, b: float((sel(arm, s, "lcomb_m", b) <= 0).mean()))
        m_r4c = sm_abs(lambda arm, s, b: float((sel(arm, s, "R4_cv", b) <= 0).mean()))
        m_r4f = sm_abs(lambda arm, s, b: float((sel(arm, s, "R4_fm", b) <= 0).mean()))
        d_s4 = seedmean(lambda arm, s, b: float((sel(arm, s, "S4_cv", b) <= 0).mean()))
        legs = dict(auc_lcomb=leg(*d_auc, -0.02, "ge"), miss_lcomb=leg(*d_ml, 0.05, "le"),
                    miss_R4_cv=leg(*m_r4c, 0.05, "le"), miss_R4_fm=leg(*m_r4f, 0.05, "le"),
                    miss_S4_cv=leg(*d_s4, 0.05, "le"))
        R["G1_two_person"] = dict(legs=legs, verdict=combine([v["verdict"] for v in legs.values()]))
    else:
        R["G1_two_person"] = dict(verdict="not read (too few seeds)")
    # section 7.3 guard G2: storage (C2P rule, control on the refit A of the same seed) and storage evasion
    ctrl = {z: {s: bool(nets[("A", s)]["storage"][z]["d_flag"] >= 0.05 and nets[("A", s)]["storage"][z]["d_mean_sd"] > 0)
                for s in read} for z in SIZES}
    c2 = {}
    need = 4 if len(read) == 5 else len(read)
    for X in ("SE", "Sb"):
        res = {}
        for z in SIZES:
            pz = {}
            for s in read:
                x, A = nets[(X, s)]["storage"][z], nets[("A", s)]["storage"][z]
                pz[s] = bool(ctrl[z][s] and x["d_flag"] <= A["d_flag"] / 3 and abs(x["d_mean_sd"]) <= A["d_mean_sd"] / 3
                             and x["d_flag"] <= 0.05 and x["d_flag_upper95"] <= 0.08)
            res[z] = dict(per_seed=pz, n_pass=sum(pz.values()), n_control=sum(ctrl[z].values()))
        if len(read) < 4:
            v = "not read (too few seeds)"
        elif any(res[z]["n_control"] < need for z in SIZES):
            v = "uninformative"
        elif all(res[z]["n_pass"] >= need for z in SIZES):
            v = "passes"
        elif any(res[z]["n_pass"] <= 1 for z in SIZES):
            v = "fails"
        else:
            v = "inconclusive, no claim"
        vals = {z: {s: nets[(X, s)]["storage"][z]["d_mean_att_sd"] for s in read} for z in SIZES}
        sup = any(sum(1 for q in vals[z].values() if q <= -0.20) >= need for z in SIZES)
        fal = all(sum(1 for q in vals[z].values() if q >= -0.10) >= need for z in SIZES) if read else False
        res["verdict"] = v
        res["H_new_1"] = dict(values=vals, verdict="supported" if sup else ("falsified" if fal else "inconclusive"))
        c2[X] = res
    g2se = c2["SE"]["verdict"] == "passes" and c2["SE"]["H_new_1"]["verdict"] == "falsified"
    g2sb = c2["Sb"]["verdict"] == "passes" and c2["Sb"]["H_new_1"]["verdict"] == "falsified"
    if c2["SE"]["verdict"] in ("uninformative", "not read (too few seeds)"):
        g2v = c2["SE"]["verdict"]
    else:
        g2v = "holds" if g2se else ("fails, attributable to SE (Sb holds)" if g2sb else "fails for Sb as well: no attribution")
    R["G2_storage"] = dict(A_control=ctrl, arms=c2, verdict=g2v)
    # section 7.4 guard G3: camera photos (absolute per seed on R0 / AF0 photos; relative seed means on FFHQ / MS1)
    if len(read) >= 4:
        absl = per(lambda s: se(s)["flag_G_devR0"]["rate"] <= 0.05 and se(s)["flag_G_af0photo"]["rate"] <= 0.05)
        absb = per(lambda s: sb(s)["flag_G_devR0"]["rate"] <= 0.05 and sb(s)["flag_G_af0photo"]["rate"] <= 0.05)
        rel = {k: leg(*seedmean(lambda arm, s, b, k=k: float((sel(arm, s, k, b) > 0).mean())), 0.02, "le")
               for k in ("G_ffhq_bona", "G_ms1_native")}
        g3 = combine([count(absl, len(read))] + [v["verdict"] for v in rel.values()])
        if g3 == "not met" and count(absl, len(read)) == "not met" and count(absb, len(read)) != "met":
            g3 = "not met for Sb as well (absolute legs): no attribution"
        R["G3_camera"] = dict(absolute_per_seed=absl, absolute_count=count(absl, len(read)),
                              absolute_count_Sb=count(absb, len(read)), relative=rel, verdict=g3)
    else:
        R["G3_camera"] = dict(verdict="not read (too few seeds)")
    # section 7.5 baseline comparison (claim wording only)
    if base is not None:
        bb = per(lambda s: se(s)["auc_R4_vs_R3_cv"] - base["auc_R4_vs_R3_cv"] >= 0.05
                 and se(s)["auc_S4_vs_S3_cv"] - base["auc_S4_vs_S3_cv"] >= 0.05)
        R["B_baseline"] = dict(per_seed=bb, count=count(bb, len(read)))
    # section 9 printed: FS1 Sb (A100) development flags; platform check
    fs1 = {}
    for s in (403, 404, 405, 406, 407):
        tp = pathlib.Path(f"/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s{s}.tar")
        if tp.exists() and not a.mock:
            with tarfile.open(tp) as t:
                z = np.load(io.BytesIO(t.extractfile(f"PN1_Sb_s{s}/scores_eval.npz").read()))
            Lf = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
            fs1[s] = {k: float(np.mean([Lf[i] > 0 for i in P[k]])) for k in ("S3_cv", "R3_cv", "R3m_cv") if all(i in Lf for i in P[k])}
    R["printed_FS1_Sb_A100"] = fs1
    R["printed_platform_check"] = {}
    for pct in a.platformcheck:
        new = {}
        for fam in ("af0", "ffhq"):
            d = C2P.npz_from_tar(pct, f"PC_PN1_Sb_s403_{fam}.npz")
            new.update(d or {})
        stored = C2P.npz_from_tar("/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s403.tar", "scores_eval.npz") or {}
        gids = [r["id"] for r in csv.DictReader(open(C2P.FS1M)) if r["fam"] in ("af0", "ffhq")]
        g = C2P.gate(new, stored, gids)
        g["label"] = ("precision and GPU together: rescore.py runs with TF32 off, the stored FS1 A100 logits were made with "
                      "TF32 on (REVIEW_PN1_C2P Q5/F6); a miss is not a platform failure of the lease")
        g["sentence"] = ("reproduces FS1 scores (precision and GPU together)" if g.get("passed")
                         else "differs from FS1 scores (precision and GPU together)")
        R["printed_platform_check"][pathlib.Path(pct).name] = g
    # section 8 outcome
    g1v = R["G1_two_person"]["verdict"]
    g3v = R["G3_camera"]["verdict"]
    if len(read) < 4:
        oc = "not read (too few seeds): FINAL unchanged"
    elif tv == "target met" and g1v == "met" and g2v == "holds" and g3v == "met":
        oc = ("primary rule passed: SE is an eligible candidate only if the author registered a selection clause "
              "before this read; otherwise an ablation row; FINAL unchanged by this reader")
    elif tv == "target met" and g1v == "not met":
        oc = "target met, G1 not met (the predicted case): ablation row; FINAL unchanged"
    elif tv == "target met":
        oc = f"target met; G1 {g1v}, G2 {g2v}, G3 {g3v}: ablation row; FINAL unchanged"
    else:
        oc = f"target {tv}: ablation row only; FINAL unchanged"
    R["outcome"] = oc
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    print(json.dumps(dict(read_seeds=read, target=tv, G1=g1v, G2=g2v, G3=g3v,
                          baseline=R.get("B_baseline", {}).get("count"), outcome=oc)))


if __name__ == "__main__":
    main()
