"""Shared test battery (BATTERY): per-network statistics of the shortcut audit rows, from one network's logits.

Each block reproduces the per-network part of one reviewed reader, calling that reader's own functions (imported unchanged
through legacy.get, sha256-pinned). The few lines of glue in each block are the reader's per-network lines, copied in the
same order with the same random seeds, so that the regression test (regress.py) can require exact equality with the
reviewed JSON files. Nothing here decides anything: there is no verdict, no rule and no threshold choice.

Blocks (reader -> audit rows):
  FS1   PN1/fs_read.py (per-arm record + printed R1-R6 via rreads)           rows 1, 12, 18
  PR1   PR1/pr1_read.py (per-network R: pools, tau5, AUCs, Z1, Z2a, Z3, Z6)  rows 6, 7, 8, 9, 17, 19, 20
  AB1   AB1/ab1_read.py (per-network st, with c2p_read.net_stats)            rows 1, 2, 6, 8, 9, 18
  C2P   PN1/c2p_read.py (net_stats + H-new-2 counts)                         rows 1, 2
  TT1   TT1/tt1_read.py + tt1_read_fs.py (read_net, family_ci, extra_reads)  rows 4, 5, 10, 17, 19
  MEDS  TT1/meds/tt1_read_meds.py (per-network record)                       row 4
  GD    PR1/gd_read.py (GD0, GD1, GD2 per network)                           rows 13, 14
  BD1   BD1/bd1_read.py (per-network record)                                 row 8

Inputs of every block are dicts id -> logit (float). A block whose rows are missing returns
{"not_computed": reason}; it never substitutes other rows."""
import copy
import csv
import math
import pathlib

import numpy as np

from . import legacy

_CTX = {}


def _finite(L, ids):
    return all(i in L and math.isfinite(L[i]) for i in ids)


def _missing(L, ids):
    return sum(1 for i in ids if i not in L or not math.isfinite(L[i]))


# --------------------------------------------------------------------------- FS1 (PN1/fs_read.py)
def ctx_fs1():
    if "fs1" in _CTX:
        return _CTX["fs1"]
    F, K, RD = legacy.get("fs_read"), legacy.get("pn1lib"), legacy.get("reads")
    assert F.sha(F.EVAL) == F.EVAL_SHA
    assert F.sha(F.FLOOR) == F.FLOOR_SHA.read_text().split()[0]
    man = list(csv.DictReader(open(F.EVAL)))
    lc_m = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"]
    lc_g = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_resmatch"]
    nat = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "ffhq_bona_orig"}
    rm = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_resmatch"}
    keys = sorted(set(nat) & set(rm))
    lad = [dict(r, fam="ladder", _splice=True) if r["fam"] == "splice" else r for r in man if r["fam"] in ("ladder", "splice", "af0")]
    # fs_read takes persons and pool from pn1lib.catalog(), which opens benchmark lists. Neither field is used by
    # reads.pools / reads.paired / reads.unit (only fam, role, rung, tool, strength, field, host), so the battery sets
    # the reader's own fallbacks and never calls catalog(); the regression test checks the outputs are identical.
    for r in lad:
        r["persons"] = (r["host"],)
        r["neutral"] = False
        r.setdefault("field", "")
        r["pool"] = "ladder"
    P = RD.pools([r for r in lad if not r.get("_splice")])
    for r in lad:
        if r.get("_splice"):
            P.setdefault(("T_" if r["role"] == "test" else "D_") + r["rung"], []).append(r)
    z = np.load(F.FLOOR)
    cid = {str(i): c for i, c in zip(z["ids"], z["cues"])}
    CM = np.array([cid[i] for i in lc_m]); CG = np.array([cid[i] for i in lc_g])
    rng = np.random.default_rng(20261118)
    draws = [(rng.integers(0, len(lc_m), len(lc_m)), rng.integers(0, len(lc_g), len(lc_g))) for _ in range(2000)]

    def fmax(im, ig):
        v = [F.fauc(CM[im, j], CG[ig, j]) for j in range(CM.shape[1])]
        return max(max(u, 1 - u) for u in v)
    fdraw = np.array([fmax(im, ig) for im, ig in draws])
    names = [str(n) for n in z["names"]]
    cmp_m = [r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"]
    cmp_g = [r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_resmatch"]
    hc = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"}
    hb_ = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"}
    pk = [(hc[k], hb_[k]) for k in sorted(set(hc) & set(hb_))]
    c = dict(F=F, RD=RD, man=man, ids=[r["id"] for r in man], lc_m=lc_m, lc_g=lc_g, nat=nat, rm=rm, keys=keys, P=P,
             cid=cid, draws=draws, fdraw=fdraw, rng_state=copy.deepcopy(rng.bit_generator.state),
             floor_best_auc=float(fmax(np.arange(len(lc_m)), np.arange(len(lc_g)))), names=names, cmp_m=cmp_m,
             cmp_g=cmp_g, pk=pk)
    _CTX["fs1"] = c
    return c


def fresh_fs1_rng():
    """the bootstrap stream of fs_read.py's share_rising interval as it stands for the first network it reads. fs_read
    draws this interval for 15 networks from ONE stream in a fixed order; a single new network gets the first position."""
    c = ctx_fs1()
    rng = np.random.default_rng(20261118)
    rng.bit_generator.state = copy.deepcopy(c["rng_state"])
    return rng


def block_fs1(x, rng=None):
    c = ctx_fs1()
    if not _finite(x, c["ids"]):
        return dict(not_computed=f"{_missing(x, c['ids'])} FS1 evaluation rows missing or non-finite")
    F, RD, P, draws, fdraw = c["F"], c["RD"], c["P"], c["draws"], c["fdraw"]
    rng = rng if rng is not None else fresh_fs1_rng()
    lc_m, lc_g, rm, nat, keys = c["lc_m"], c["lc_g"], c["rm"], c["nat"], c["keys"]
    # --- fs_read.main, per arm (lines 204-218 at the pin)
    m = np.array([x[i] for i in lc_m]); g = np.array([x[i] for i in lc_g])
    sd = np.array([F.fauc(m[im], g[ig]) for im, ig in draws])
    d = np.array([x[rm[k]] - x[nat[k]] for k in keys])
    pb = [np.mean(d[rng.integers(0, len(d), len(d))] > 0) for _ in range(2000)]
    fo = RD.paired(x, P, "T_S4_bg", "T_S0_bg")
    fb = RD.paired(x, P, "T_R4_face", "T_R2w_face")
    rec = dict(lcomb_auc=float(F.fauc(m, g)), lcomb_ci=[float(np.percentile(sd, 2.5)), float(np.percentile(sd, 97.5))],
               lcomb_minus_floor_lo=float(np.percentile(sd - fdraw, 2.5)),
               share_rising=float(np.mean(d > 0)), share_ci=[float(np.percentile(pb, 2.5)), float(np.percentile(pb, 97.5))],
               faceonly_test=fo.get("auc"), faceonly_test_ci=[fo.get("lo"), fo.get("hi")],
               faceonly_dev=RD.paired(x, P, "D_S4_bg", "D_S0_bg").get("auc"),
               faceblanked_test=fb.get("auc"), faceblanked_dev=RD.paired(x, P, "D_R4_face", "D_R2w_face").get("auc"),
               flags_own={p: float(np.mean(RD.scores_of(x, P[p]) > 0)) for p in ("D_R0", "D_R0_61", "D_R0_112", "V_photo") if P.get(p)} |
               {"ffhq_bona_orig": float(np.mean([x[nat[k]] > 0 for k in keys]))})
    # --- fs_read.rreads for this one network (printed R1-R6)
    rr = F.rreads({"net": x}, lc_m, lc_g, c["cid"], c["names"], c["cmp_m"], c["cmp_g"], c["pk"])
    return dict(record=rec, printed_R1_R6=rr["net"], context=dict(floor_best_auc=c["floor_best_auc"],
                R3_base=rr["R3_base"], R5_noise_std_border_auc=rr["R5_noise_std_border_auc"]))


# --------------------------------------------------------------------------- PR1 (PR1/pr1_read.py)
def ctx_pr1():
    if "pr1" in _CTX:
        return _CTX["pr1"]
    PR = legacy.get("pr1_read")
    rows = PR.manifest()
    P = PR.pools(rows)
    ids_eval = {r["id"] for r in rows}
    zl, zs = np.load(PR.CUE_LAD), np.load(PR.CUE_SPL)
    li = list(zl["names"]).index("lapvar_face")
    lap = {str(i): float(c[li]) for i, c in zip(zl["ids"], zl["cues"]) if str(i) in ids_eval}
    lap.update({str(i): float(c[li]) for i, c in zip(zs["ids"], zs["cues"]) if str(i) in ids_eval})
    c = dict(PR=PR, rows=rows, by={r["id"]: r for r in rows}, P=P, ids_eval=ids_eval, lap=lap)
    _CTX["pr1"] = c
    return c


def block_pr1(x, train=None, info=None):
    """x: id -> logit over (at least) the FS1 evaluation rows; train: list of dict(kind, logit) (unique training rows,
    as pn1_score.py stores them) or None."""
    c = ctx_pr1()
    PR, P, by, lap = c["PR"], c["P"], c["by"], c["lap"]
    if not _finite(x, c["ids_eval"]):
        return dict(not_computed=f"{_missing(x, c['ids_eval'])} FS1 evaluation rows missing or non-finite")
    e = {i: x[i] for i in c["ids_eval"]}
    B = PR.B
    rng_seed = 20261141
    # --- pr1_read.main, per network (lines 251-352 at the pin)
    t5, c1r, c2r = PR.tau5(e, P)
    G = PR.z_eval_tables(e, P, t5)
    v = lambda k: np.array([e[i] for i in P[k]])          # noqa: E731
    R = dict(tau5=t5, tau5_cal_flags=dict(c1=c1r, c2=c2r), pools=G)
    A_ = {}
    for role in ("dev", "test"):
        A_[f"S3_vs_S0_{role}"] = PR.auc(v(f"spl_S3_{role}"), v(f"spl_S0_{role}"))
        A_[f"S4_vs_S3_{role}"] = PR.auc(v(f"spl_S4_{role}"), v(f"spl_S3_{role}"))
        A_[f"S4_vs_S0_{role}"] = PR.auc(v(f"spl_S4_{role}"), v(f"spl_S0_{role}"))
        for tool in ("opencv", "facemorpher"):
            r4 = v(f"lad_R4_{tool}_{role}_nat")
            for neg in ("R2w", "R3", "R3m"):
                A_[f"R4_vs_{neg}_{tool}_{role}"] = PR.auc(r4, v(f"lad_{neg}_{tool}_{role}_nat"))
            A_[f"R4_vs_R0_{tool}_{role}"] = PR.auc(r4, v(f"lad_R0_{role}_nat"))
            A_[f"R2w_vs_R0_{tool}_{role}"] = PR.auc(v(f"lad_R2w_{tool}_{role}_nat"), v(f"lad_R0_{role}_nat"))
            A_[f"R3_vs_R0_{tool}_{role}"] = PR.auc(v(f"lad_R3_{tool}_{role}_nat"), v(f"lad_R0_{role}_nat"))
    A_["lcomb_vs_resmatch"] = PR.auc(v("lcomb_orig"), v("ffhq_lcombined_resmatch_all"))
    A_["lcomplete_vs_resmatch"] = PR.auc(v("lcomplete_orig"), v("ffhq_lcomplete_resmatch_all"))
    A_["lcomb_vs_devS3"] = PR.auc(v("lcomb_orig"), v("spl_S3_dev"))
    R["auc"] = A_
    R["auc_ci"] = {k: PR.boot_auc(*pp, 20261141) for k, pp in (
        ("S3_vs_S0_test", (v("spl_S3_test"), v("spl_S0_test"))), ("S4_vs_S3_test", (v("spl_S4_test"), v("spl_S3_test"))),
        ("S4_vs_S0_test", (v("spl_S4_test"), v("spl_S0_test"))), ("S3_vs_S0_dev", (v("spl_S3_dev"), v("spl_S0_dev"))),
        ("S4_vs_S3_dev", (v("spl_S4_dev"), v("spl_S3_dev"))),
        ("R4_vs_R2w_opencv_test", (v("lad_R4_opencv_test_nat"), v("lad_R2w_opencv_test_nat"))),
        ("R4_vs_R3_opencv_test", (v("lad_R4_opencv_test_nat"), v("lad_R3_opencv_test_nat"))),
        ("lcomb_vs_devS3", (v("lcomb_orig"), v("spl_S3_dev"))))}
    s3 = v("spl_S3_dev")
    R["z2c_lcomb_miss_at_S3_flag"] = {str(q): PR.share(v("lcomb_orig"), gt=False, t=float(np.quantile(s3, 1 - q)))
                                      for q in (0.10, 0.20)}
    gk = ("ffhq_bona_eval", "ffhq_lcomplete_resmatch_eval", "ffhq_lcombined_resmatch_eval", "lad_R0_test_nat",
          "lad_R0_test_61", "lad_R0_test_112")
    gmax = max(G[k]["above_t5"] for k in gk)
    R["z2a"] = dict(G_max=gmax, G_max_pool=max(gk, key=lambda k: G[k]["above_t5"]),
                    lcomb_miss_t5=PR.share(v("lcomb_orig"), gt=False, t=t5),
                    usable=bool(gmax <= 0.10 and PR.share(v("lcomb_orig"), gt=False, t=t5) <= 0.30))
    y_own = float(np.mean([PR.share(v(k), gt=False) for k in ("hn4_lad_R4", "hn4_af0_u50", "hn4_spl_S4")]))
    y_t5 = float(np.mean([PR.share(v(k), gt=False, t=t5) for k in ("hn4_lad_R4", "hn4_af0_u50", "hn4_spl_S4")]))
    R["z2rho"] = dict(x_own=PR.share(v("ffhq_bona_all")), y_own=y_own, x_t5=gmax, y_t5=y_t5)
    z3 = {}
    for role in ("test", "dev"):
        hp = {}
        for tool in ("opencv", "facemorpher"):
            for rg in ("R4", "R2w"):
                hp[(tool, rg)] = {by[i]["host"]: e[i] for i in P[f"lad_{rg}_{tool}_{role}_nat"]}
        hosts = sorted(set.intersection(*[set(d) for d in hp.values()]))
        M = {k: np.array([d[h] for h in hosts]) for k, d in hp.items()}
        acv = PR.auc(M[("opencv", "R4")], M[("opencv", "R2w")])
        afm = PR.auc(M[("facemorpher", "R4")], M[("facemorpher", "R2w")])
        rng = np.random.default_rng(rng_seed)
        bs = []
        for _ in range(B):
            ix = rng.integers(0, len(hosts), len(hosts))
            bs.append(PR.auc(M[("opencv", "R4")][ix], M[("opencv", "R2w")][ix])
                      - PR.auc(M[("facemorpher", "R4")][ix], M[("facemorpher", "R2w")][ix]))
        z3[role] = dict(n_hosts=len(hosts), auc_cv=acv, auc_fm=afm, delta=acv - afm,
                        delta_ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                        r4_vs_r0_cv=A_[f"R4_vs_R0_opencv_{role}"], r4_vs_r0_fm=A_[f"R4_vs_R0_facemorpher_{role}"],
                        miss_own_cv=PR.share(M[("opencv", "R4")], gt=False), miss_own_fm=PR.share(M[("facemorpher", "R4")], gt=False),
                        miss_t5_cv=PR.share(M[("opencv", "R4")], gt=False, t=t5),
                        miss_t5_fm=PR.share(M[("facemorpher", "R4")], gt=False, t=t5))
    R["z3"] = z3
    if train is not None:
        tk = {}
        for row in train:
            tk.setdefault(row["kind"], []).append(row["logit"])
        z1 = {k: dict(n=len(xx), above_own=PR.share(xx), median=float(np.median(xx))) for k, xx in tk.items()}
        R["z1"] = dict(kinds=z1)
        if "lad_S3" in tk:
            R["z1"].update(f_tr_S3=PR.share(tk["lad_S3"]), m_tr_S4=PR.share(tk["lad_S4"], gt=False),
                           auc_tr_S3_vs_S0=PR.auc(tk["lad_S3"], tk["lad_S0"]), auc_tr_S4_vs_S3=PR.auc(tk["lad_S4"], tk["lad_S3"]))
    else:
        R["z1"] = dict(not_computed="no training-row scores given")
    R["train_acc_rule0_info"] = (info or {}).get("train_acc_rule0")

    def lv(k):
        ids = [i for i in P[k] if i in lap]
        return np.array([e[i] for i in ids]), np.array([lap[i] for i in ids]), len(P[k]) - len(ids)
    p4, c4, m4 = lv("lad_R4_opencv_test_nat")
    p2, c2, m2 = lv("lad_R2w_opencv_test_nat")
    sa_all, per = PR.stratified_auc(p4, p2, c4, c2)
    sa10, per10 = PR.stratified_auc(p4, p2, c4, c2, q=10)
    good = [xx for xx in per if xx["n_pos"] >= 10 and xx["n_neg"] >= 10]
    cover = sum(xx["n_pos"] + xx["n_neg"] for xx in good) / (len(p4) + len(p2))
    valid = cover >= 0.50
    sa = (sum(xx["auc"] * xx["n_pos"] * xx["n_neg"] for xx in good) / sum(xx["n_pos"] * xx["n_neg"] for xx in good)) if good else None
    s4, cs4, ms4 = lv("spl_S4_test")
    s3_, cs3, ms3 = lv("spl_S3_test")
    sa2, per2 = PR.stratified_auc(s4, s3_, cs4, cs3)
    rho = {}
    for k in ("lad_R0_test_nat", "lad_R2w_opencv_test_nat", "lad_R3_opencv_test_nat", "lad_R4_opencv_test_nat",
              "spl_S0_test", "spl_S3_test", "spl_S4_test"):
        xx, cc, _ = lv(k)
        rho[k] = PR.spearman(xx, np.log(cc + 1e-12))
    R["z6"] = dict(strat_auc_R4_vs_R2w=sa, strat_auc_all_strata=sa_all, cover=cover, strata=per, readable=valid, strat10_auc_R4_vs_R2w=sa10, strata10=per10, auc_R4_vs_R2w=PR.auc(p4, p2),
                   strat_auc_S4_vs_S3=sa2, strata_S=per2, auc_S4_vs_S3=PR.auc(s4, s3_), rho_logit_loglap=rho,
                   missing_cues=dict(R4=m4, R2w=m2, S4=ms4, S3=ms3))
    return R


# --------------------------------------------------------------------------- AB1 (AB1/ab1_read.py) and C2P
def ctx_ab1():
    if "ab1" in _CTX:
        return _CTX["ab1"]
    A = legacy.get("ab1_read")
    C2 = A.C2
    assert A.sha(A.EVAL) == A.EVAL_SHA
    assert A.sha(A.FLOOR) == A.FLOOR_SHA_FILE.read_text().split()[0]
    M = list(csv.DictReader(open(A.EVAL)))
    P = A.pools(M)
    natp, natm, pairs, mpairs = C2.holdout(M)
    rng = np.random.default_rng(C2.RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(C2.B_BOOT)] for z in A.SIZES}
    z = np.load(A.FLOOR)
    cid = {str(i): c for i, c in zip(z["ids"], z["cues"])}
    CM = np.array([cid[i] for i in P["lc_m"]]); CG = np.array([cid[i] for i in P["lc_g"]])
    rng2 = np.random.default_rng(20261118)
    draws = [(rng2.integers(0, len(CM), len(CM)), rng2.integers(0, len(CG), len(CG))) for _ in range(2000)]

    def fmax(im, ig):
        v = [C2.fauc(CM[im, j], CG[ig, j]) for j in range(CM.shape[1])]
        return max(max(u, 1 - u) for u in v)
    fdraw = np.array([fmax(im, ig) for im, ig in draws])
    need_c2p = set(natp) | set(natm) | {f"{i}_{zz}" for zz in A.SIZES for i in pairs[zz]} | \
        {f"{i}_{zz}" for zz in A.SIZES for i in mpairs[zz]}
    need = need_c2p | {i for k in ("lc_m", "lc_g", "S3", "S0", "S4", "warp", "halves", "soft", "camera") for i in P[k]}
    c = dict(A=A, C2=C2, M=M, P=P, natp=natp, natm=natm, pairs=pairs, mpairs=mpairs, boot=boot, draws=draws, fdraw=fdraw,
             need=need, floor_best_auc=fmax(np.arange(len(CM)), np.arange(len(CG))))
    _CTX["ab1"] = c
    return c


def block_ab1(x, train_kinds=None):
    """x over the AB1 evaluation rows (FS1 rows + the 1,480 MS1 FFHQ hold-out rows); train_kinds: kind -> [logits]."""
    c = ctx_ab1()
    A, C2, P, draws, fdraw = c["A"], c["C2"], c["P"], c["draws"], c["fdraw"]
    natp, natm, pairs, mpairs, boot = c["natp"], c["natm"], c["pairs"], c["mpairs"], c["boot"]
    if not _finite(x, c["need"]):
        return dict(not_computed=f"{_missing(x, c['need'])} AB1 evaluation rows (incl. MS1 hold-out) missing or non-finite")
    share = A.share
    # --- ab1_read.main, per network (lines 199-212 at the pin)
    m = np.array([x[i] for i in P["lc_m"]]); g = np.array([x[i] for i in P["lc_g"]])
    sd = np.array([C2.fauc(m[im], g[ig]) for im, ig in draws])
    st = dict(
        lcomb_auc=C2.fauc(m, g), lcomb_ci=[float(np.percentile(sd, 2.5)), float(np.percentile(sd, 97.5))],
        lcomb_minus_floor_lo=float(np.percentile(sd - fdraw, 2.5)),
        S3=share(x, P["S3"]), S0=share(x, P["S0"]),
        S0_vs_S4_auc=C2.fauc([x[i] for i in P["S4"]], [x[i] for i in P["S0"]]),
        S3_vs_S4_auc=C2.fauc([x[i] for i in P["S4"]], [x[i] for i in P["S3"]]),
        warp=share(x, P["warp"]), warp_R2w=share(x, P["R2w"]), warp_R2w4=share(x, P["R2w4"]), warp_zero=share(x, P["zero"]),
        halves=share(x, P["halves"]), camera=share(x, P["camera"]),
        soft=share(x, P["soft"]), soft61=share(x, P["soft61"]), soft112=share(x, P["soft112"]),
        ffhq_native_photo_flag=share(x, natp))
    st["dsoft"] = st["soft"] - st["camera"]
    if train_kinds:
        st["train_flag_by_kind"] = {k: float(np.mean(np.array(v) > 0)) for k, v in sorted(train_kinds.items())}
    st["c2p"] = C2.net_stats(x, natp, natm, pairs, mpairs, boot)
    return st


def ctx_c2p():
    if "c2p" in _CTX:
        return _CTX["c2p"]
    C2 = legacy.get("c2p_read")
    M = list(csv.DictReader(open(C2.MS1M)))
    natp, natm, pairs, mpairs = C2.holdout(M)
    rng = np.random.default_rng(C2.RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(C2.B_BOOT)] for z in C2.SIZES}
    cz = np.load(C2.CUES)
    names = list(cz["names"])
    lap = dict(zip([str(i) for i in cz["ids"]], cz["cues"][:, names.index("lapvar_face")]))
    edges = np.quantile([lap[i] for i in natp], 0.75)
    top = {i for i in natp if lap[i] >= edges}
    need = set(natp) | set(natm) | {f"{i}_{z}" for z in C2.SIZES for i in pairs[z]} | \
        {f"{i}_{z}" for z in C2.SIZES for i in mpairs[z]}
    c = dict(C2=C2, natp=natp, natm=natm, pairs=pairs, mpairs=mpairs, boot=boot, top=top, edges=float(edges), need=need)
    _CTX["c2p"] = c
    return c


def block_c2p(L):
    """L over the MS1 FFHQ hold-out rows (fam ms1ffhq): c2p_read.net_stats plus its H-new-2 counts."""
    c = ctx_c2p()
    C2 = c["C2"]
    if not _finite(L, c["need"]):
        return dict(not_computed=f"{_missing(L, c['need'])} MS1 hold-out rows missing or non-finite")
    st = C2.net_stats(L, c["natp"], c["natm"], c["pairs"], c["mpairs"], c["boot"])
    top, pairs = c["top"], c["pairs"]
    for z in C2.SIZES:          # --- c2p_read.main H-new-2 counts (lines 155-160 at the pin)
        ids = pairs[z]
        up_t = sum(1 for i in ids if i in top and L[i] <= 0 < L[f"{i}_{z}"])
        dn_t = sum(1 for i in ids if i in top and L[i] > 0 >= L[f"{i}_{z}"])
        net = st[z]["up"] - st[z]["down"]
        st[z]["hnew2_top_share"] = float((up_t - dn_t) / net) if net > 0 else None
    st["lapvar_face_q75"] = c["edges"]
    return st


# --------------------------------------------------------------------------- TT1 (TT1/tt1_read.py, tt1_read_fs.py)
def ctx_tt1():
    if "tt1" in _CTX:
        return _CTX["tt1"]
    TR, TF, T = legacy.get("tt1_read"), legacy.get("tt1_read_fs"), legacy.get("tt1common")
    P, tt = TR.load_pools()
    W = TR.boot_weights(P, np.random.default_rng(TR.SEED))
    ids = [i for v in P.values() for i, _ in v]
    c = dict(TR=TR, TF=TF, T=T, P=P, tt=tt, W=W, ids=ids, counts={k: len(v) for k, v in P.items()})
    _CTX["tt1"] = c
    return c


def block_tt1(L, netdir, scores_eval_dir):
    """L over the TT1 list (fam gate + fam tt1 rows of tt1_score.csv); netdir holds last_trainable.pt (head floor);
    scores_eval_dir holds scores_eval.npz of the same network on the FS1 evaluation rows (tau_cam, printed only)."""
    c = ctx_tt1()
    TR, TF, T, P, tt, W = c["TR"], c["TF"], c["T"], c["P"], c["tt"], c["W"]
    if not _finite(L, c["ids"]):
        return dict(not_computed=f"{_missing(L, c['ids'])} TT1 rows missing or non-finite")
    floor = TR.head_floor(pathlib.Path(netdir))
    tc = TF.tau_cam_fs(pathlib.Path(scores_eval_dir))
    # --- tt1_read_fs.main, per network (lines 192-208 at the pin)
    r = TR.read_net(L, P, W, tt, floor, tc)
    TR.family_ci(r, P, W, L)
    r["printed"] = TF.extra_reads(L, P)
    corr = {}
    for f_ in T.FAMILIES:
        srcs = [f_] if f_ != "lfw_calfw" else ["lfw", "calfw"]
        xx = np.concatenate([np.array([L[i] for i, _ in P[f"U:{q}"]]) > 0 for q in srcs])
        lo, hi = r["fam_flag_ci"][f_]
        corr[f_] = dict(boot_ci_clipped=[max(0.0, lo), hi], cp=TR.cp(int(xx.sum()), len(xx)), zero_event=bool(xx.sum() == 0))
    r["family_flag_corrected"] = corr
    zs = np.load(pathlib.Path(scores_eval_dir) / "scores_eval.npz")
    ms = dict(zip(zs["id"].tolist(), zs["logit"].astype(float).tolist()))
    dd = np.array([L[i] - ms[i] for i, _ in P["R_cam"]])
    r["tf32_split_R_cam"] = dict(max_abs=float(np.abs(dd).max()), median_abs=float(np.median(np.abs(dd))),
                                 flips=int(sum((L[i] > 0) != (ms[i] > 0) for i, _ in P["R_cam"])))
    r["tau_cam_label"] = "saturated band; from the stored TF32-on scores, applied to TF32-off logits (printed only)"
    r["r5"].pop("_draws", None)
    return r


# --------------------------------------------------------------------------- MEDS (TT1/meds/tt1_read_meds.py)
def ctx_meds():
    if "meds" in _CTX:
        return _CTX["meds"]
    MD, TR, T = legacy.get("tt1_read_meds"), legacy.get("tt1_read"), legacy.get("tt1common")
    assert T.sha(MD.MEDS) == "3698bcb4ff9e694219a0d1675920621724303eee034692f9374f70400fec6c8d", "meds manifest not at its pin"
    assert T.sha(T.OUT / "tt1_score.csv") == "c0055b51467cf8d001d56cbc4689706d68f0bf35c64066b1ba49fada5cb45761", "tt1_score.csv pin"
    meds = list(csv.DictReader(open(MD.MEDS)))
    prim = [r for r in meds if r["aligned"] == "1"]
    sec = [r for r in meds if r["aligned"] != "1"]
    lst = [r for r in csv.DictReader(open(T.OUT / "tt1_score.csv")) if r["fam"] == "gate"]
    cam = [r for r in lst if r["rung"] == "R_cam"]; ffq = [r for r in lst if r["rung"] == "R_ffhq"]; mfq = [r for r in lst if r["rung"] == "M_ffhq"]
    rng = np.random.default_rng(20261125)
    Wm = MD.boot_w([r["person"] for r in prim], rng)
    Wc = MD.boot_w([r["host"] for r in cam], rng)
    Wf = MD.boot_w([r["id"] for r in ffq], rng)
    c = dict(MD=MD, TR=TR, meds=meds, prim=prim, sec=sec, lst=lst, cam=cam, ffq=ffq, mfq=mfq, Wm=Wm, Wc=Wc, Wf=Wf,
             ids=[r["id"] for r in meds + lst])
    _CTX["meds"] = c
    return c


def block_meds(L):
    """L over the MEDS rows and the 3,417 TT1 gate rows (R_cam, R_ffhq, M_ffhq). No MEDS identifier is written."""
    c = ctx_meds()
    MD, TR = c["MD"], c["TR"]
    if not _finite(L, c["ids"]):
        return dict(not_computed=f"{_missing(L, c['ids'])} MEDS or gate rows missing or non-finite")
    prim, sec, cam, ffq, mfq, Wm, Wc, Wf = (c[k] for k in ("prim", "sec", "cam", "ffq", "mfq", "Wm", "Wc", "Wf"))
    NB = MD.NB
    # --- tt1_read_meds.main, per network (lines 82-102 at the pin)
    xm = np.array([L[r["id"]] for r in prim]); xc = np.array([L[r["id"]] for r in cam]); xf = np.array([L[r["id"]] for r in ffq])
    xmf = np.array([L[r["id"]] for r in mfq])
    f = (xm > 0).astype(float)
    bf = (Wm @ f) / Wm.sum(1)
    lo, hi = np.percentile(bf, [2.5, 97.5])
    au_c = TR.wauc(xm, xc); au_f = TR.wauc(xm, xf)
    dc = [TR.wauc(xm, xc, Wm[b], Wc[b]) for b in range(NB)]
    df = [TR.wauc(xm, xf, Wm[b], Wf[b]) for b in range(NB)]
    u = float(np.median(xmf) - np.median(xc))
    lap = np.log(np.array([float(r["lap_var"]) for r in prim])); enl = np.log(np.array([float(r["enlarge"]) for r in prim]))
    part = {p: float(np.mean([L[r["id"]] > 0 for r in prim if r["part"] == p])) for p in ("MEDS-I", "MEDS-II")}
    small = [r for r in prim if r["width"] == "240" and r["height"] == "240"]
    return dict(n_primary=len(prim), persons=len({r["person"] for r in prim}), flag=float(f.mean()), flag_boot=[max(0.0, float(lo)), float(hi)],
                flag_cp=MD.cp(int(f.sum()), len(f)), flag_secondary=float(np.mean([L[r["id"]] > 0 for r in sec])) if sec else None,
                flag_R_cam=float((xc > 0).mean()), flag_R_ffhq=float((xf > 0).mean()),
                auc_vs_R_cam=au_c, auc_vs_R_cam_ci=[float(np.percentile(dc, 2.5)), float(np.percentile(dc, 97.5))],
                auc_vs_R_ffhq=au_f, auc_vs_R_ffhq_ci=[float(np.percentile(df, 2.5)), float(np.percentile(df, 97.5))],
                median_logit=float(np.median(xm)), shift_from_R_cam=float(np.median(xm) - np.median(xc)), u=u,
                shift_in_u=float((np.median(xm) - np.median(xc)) / u) if u else None,
                rho_logit_loglap=MD.spear(xm, lap), rho_logit_logenlarge=MD.spear(xm, enl),
                flag_by_part=part, flag_240px=float(np.mean([L[r["id"]] > 0 for r in small])) if small else None, n_240px=len(small))


# --------------------------------------------------------------------------- GD (PR1/gd_read.py)
def ctx_gd():
    if "gd" in _CTX:
        return _CTX["gd"]
    legacy.get("pr1_read")
    GD = legacy.get("gd_read")
    assert GD.sha(GD.GDMAN) == GD.GDMAN_SHA
    man = list(csv.DictReader(open(GD.GDMAN)))
    by = {r["id"]: r for r in man}
    M, names, chk = GD.baseline_models()
    ids = lambda **kw: [r["id"] for r in man if all(r[k] == v for k, v in kw.items())]   # noqa: E731
    G0 = ("stylegan_wplus", "stylegan_w", "diffae")
    base = {}
    if GD.CUE_GD0.exists():                       # --- gd_read.main cue baselines (lines 175-188 at the pin)
        cg, ng = GD.cues(GD.CUE_GD0)
        assert ng == names
        for f in G0:
            pi, ni = ids(fam="gd0", rung=f"{f}_orig"), ids(fam="gd0", rung=f"{f}_resmatch")
            assert all(i in cg for i in pi + ni), "missing GD0 cues"
            Pm, Nm = np.array([cg[i] for i in pi]), np.array([cg[i] for i in ni])
            row = {k: GD.auc(m.decision_function(Pm), m.decision_function(Nm)) for k, (m, _, _) in M.items()}
            single = [max(GD.auc(Pm[:, j], Nm[:, j]), 1 - GD.auc(Pm[:, j], Nm[:, j])) for j in range(Pm.shape[1])]
            row["best_single"] = float(max(single))
            row["best_single_name"] = names[int(np.argmax(single))]
            base[f] = row
    fsman = list(csv.DictReader(open(legacy.get("pr1_read").MAN)))
    c = dict(GD=GD, man=man, by=by, ids=ids, G0=G0, base=base, baseline_check=chk, fsman=fsman)
    _CTX["gd"] = c
    return c


def block_gd(sc, dev):
    """sc over the GD rows (pr1_gd.csv); dev over the FS1 evaluation rows (native FFHQ and test R0, printed beside)."""
    c = ctx_gd()
    GD, man, by, ids, G0, base = c["GD"], c["man"], c["by"], c["ids"], c["G0"], c["base"]
    need = [r["id"] for r in man]
    if not _finite(sc, need):
        return dict(not_computed=f"{_missing(sc, need)} GD rows missing or non-finite")
    fs = c["fsman"]
    bn = np.array([dev[r["id"]] for r in fs if r["rung"] == "ffhq_bona_orig"]) if dev else None
    xr0 = [dev[r["id"]] for r in fs if r["fam"] == "ladder" and r["role"] == "test" and r["rung"] == "R0" and r["strength"] == ""] if dev else None
    if xr0 is not None:
        assert len(xr0) == 191
    share, auc = GD.share, GD.auc
    # --- gd_read.main, per network (lines 197-234 at the pin)
    v = lambda L: np.array([sc[i] for i in L])   # noqa: E731
    R = {}
    gd0 = {}
    for f in G0:
        pi, ni = ids(fam="gd0", rung=f"{f}_orig"), ids(fam="gd0", rung=f"{f}_resmatch")
        p, q = v(pi), v(ni)
        gd0[f] = dict(auc=auc(p, q), ci=GD.boot_img(p, q, 20261143), miss_own=share(p, gt=False), gen_flag_own=share(q),
                      auc_vs_bona_native=(auc(p, bn) if bn is not None else None),
                      minus_s_lad=(auc(p, q) - base[f]["s_lad"]) if f in base else None)
    R["gd0"] = gd0
    rung = lambda fam, rg: [i for i in ids(fam=fam, rung=rg)]   # noqa: E731
    h = lambda L: [by[i]["host"] for i in L]                    # noqa: E731
    gd1 = {}
    for x_, y_ in (("X", "REC"), ("REC", "G"), ("SAME", "REC"), ("X", "SAME"), ("MIR", "REC")):
        P_, N_ = rung("gd1", x_), rung("gd1", y_)
        gd1[f"{x_}_vs_{y_}"] = dict(auc=auc(v(P_), v(N_)), ci=GD.boot_unit(v(P_), v(N_), h(P_), h(N_), 20261144))
    gd1["flags_own_frame_confounded"] = {rg: share(v(rung("gd1", rg))) for rg in ("G", "REC", "MIR", "SAME", "X")}
    gd1["test_R0_native_flag_own_stored"] = share(xr0) if xr0 is not None else None
    R["gd1"] = gd1
    gd2 = {}
    for x_, y_ in (("R4", "R2"), ("R4", "R3"), ("R2", "R0"), ("R2s", "R0"), ("R4", "R2s"), ("R3", "R0"), ("R3m", "R0"), ("R4", "R0")):
        P_, N_ = rung("gd2", x_), rung("gd2", y_)
        gd2[f"{x_}_vs_{y_}"] = dict(auc=auc(v(P_), v(N_)), ci=GD.boot_unit(v(P_), v(N_), h(P_), h(N_), 20261145))
    gd2["flags_own"] = {rg: share(v(rung("gd2", rg))) for rg in ("R0", "R2", "R2s", "R3", "R3m", "R4")}
    gd2["n"] = {rg: len(rung("gd2", rg)) for rg in ("R0", "R2", "R2s", "R3", "R3m", "R4")}
    R["gd2"] = gd2
    return R


# --------------------------------------------------------------------------- BD1 (BD1/bd1_read.py)
def ctx_bd1():
    if "bd1" in _CTX:
        return _CTX["bd1"]
    BD = legacy.get("bd1_read")
    dfile = str(BD.DFILE)
    assert BD.sha(dfile) == pathlib.Path(dfile + ".sha256").read_text().split()[0]
    D = {r["id"]: r for r in csv.DictReader(open(dfile))}
    RG = ("S4", "S3", "S0")
    test = {rg: sorted([i for i, r in D.items() if r["role"] == "test" and r["rung"] == rg], key=lambda i: D[i]["host"]) for rg in RG}
    dev = {rg: sorted([i for i, r in D.items() if r["role"] == "dev" and r["rung"] == rg], key=lambda i: D[i]["host"]) for rg in RG}
    dv = lambda L, k="D": np.array([float(D[i][k]) for i in L])   # noqa: E731
    ref_q = BD.strat_auc(dv(test["S4"]), dv(test["S3"]), dv(test["S4"]), dv(test["S3"]))
    ref_w = BD.window_auc(dv(test["S4"]), dv(test["S3"]), dv(test["S4"]), dv(test["S3"]))
    c = dict(BD=BD, D=D, test=test, dev=dev, dv=dv, ref_q=ref_q, ref_w=ref_w, dfile_sha256=BD.sha(dfile),
             ids=[i for v in list(test.values()) + list(dev.values()) for i in v])
    _CTX["bd1"] = c
    return c


def block_bd1(L):
    c = ctx_bd1()
    BD, D, test, dev, dv, ref_q, ref_w = (c[k] for k in ("BD", "D", "test", "dev", "dv", "ref_q", "ref_w"))
    if not _finite(L, c["ids"]):
        return dict(not_computed=f"{_missing(L, c['ids'])} BD1 rows missing or non-finite")
    auc, strat_auc, window_auc, spearmanr, B = BD.auc, BD.strat_auc, BD.window_auc, BD.spearmanr, BD.B
    # --- bd1_read.main, per network (lines 116-147 at the pin)
    v = lambda ids: np.array([L[i] for i in ids])   # noqa: E731
    p, n = v(test["S4"]), v(test["S3"])
    sa, cover, strata = strat_auc(p, n, dv(test["S4"]), dv(test["S3"]))
    wa, npairs = window_auc(p, n, dv(test["S4"]), dv(test["S3"]))
    readable_q, readable_w = cover >= 0.5, npairs >= 1000
    primary = sa if readable_q else (wa if readable_w else None)
    rng = np.random.default_rng(20261151)
    hs = len(test["S4"])
    assert [D[i]["host"] for i in test["S4"]] == [D[i]["host"] for i in test["S3"]], "host order"
    bs, low = [], 0
    for _ in range(B):
        ix = rng.integers(0, hs, hs)
        if readable_q:
            x, cv_, _ = strat_auc(p[ix], n[ix], dv(test["S4"])[ix], dv(test["S3"])[ix])
            low += int(cv_ < 0.5)
        else:
            x = window_auc(p[ix], n[ix], dv(test["S4"])[ix], dv(test["S3"])[ix])[0]
        if x is not None:
            bs.append(x)
    pd_, nd_ = v(dev["S4"]), v(dev["S3"])
    ref = ref_q[0] if readable_q else (ref_w[0] if readable_w else None)
    extra = {}
    for kk in ("D_int", "D_band", "D_Y"):
        extra[f"strat_auc_{kk}"] = strat_auc(p, n, dv(test["S4"], kk), dv(test["S3"], kk))[0]
        extra[f"rho_logit_{kk}_S3"] = float(spearmanr(n, dv(test["S3"], kk)).correlation)
    s0 = v(test["S0"])
    return dict(
        auc_test=auc(p, n), strat_auc_test=sa, cover=cover, strata=strata, window_auc_test=wa, window_pairs=npairs,
        primary=primary, primary_kind=("quintile" if readable_q else ("window" if readable_w else "not readable")),
        primary_ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else None,
        rho_logit_D_S3=float(spearmanr(n, dv(test["S3"])).correlation),
        rho_logit_D_S4=float(spearmanr(p, dv(test["S4"])).correlation),
        auc_dev=auc(pd_, nd_), strat_auc_dev=strat_auc(pd_, nd_, dv(dev["S4"]), dv(dev["S3"]))[0],
        S3_flag_test=float((n > 0).mean()), reference=ref,
        primary_minus_ref=(primary - ref) if (primary is not None and ref is not None) else None,
        boot_low_cover_draws=low, rho_logit_D_S0=float(spearmanr(s0, dv(test["S0"])).correlation),
        S0_flag_test=float((s0 > 0).mean()), rho_logit_G_S3=float(spearmanr(n, dv(test["S3"], "G")).correlation), **extra)


# --------------------------------------------------------------------------- all blocks
def all_blocks(dev, train=None, train_kinds=None, tt1=None, meds=None, gd=None, netdir=None, scores_eval_dir=None, info=None):
    """every block computable from the given logits; a block without its rows records why it was not computed."""
    out = {}
    nc = lambda why: dict(not_computed=why)   # noqa: E731
    out["FS1"] = block_fs1(dev) if dev else nc("no FS1 evaluation logits")
    out["PR1"] = block_pr1(dev, train, info) if dev else nc("no FS1 evaluation logits")
    out["AB1"] = block_ab1(dev, train_kinds) if dev else nc("no AB1 evaluation logits")
    out["C2P"] = block_c2p(dev) if dev else nc("no MS1 hold-out logits")
    out["BD1"] = block_bd1(dev) if dev else nc("no FS1 evaluation logits")
    out["TT1"] = block_tt1(tt1, netdir, scores_eval_dir) if (tt1 and netdir and scores_eval_dir) else nc("no TT1 logits")
    out["MEDS"] = block_meds(meds) if meds else nc("no MEDS logits")
    out["GD"] = block_gd(gd, dev) if gd else nc("no GD logits")
    return out
