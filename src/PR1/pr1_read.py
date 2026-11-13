"""Registered reads of the existing fresh-seed protocol networks (PR1), parts Z0, Z1, Z2 (Z2a, Z2c, Z2-rho), Z3, Z4
and Z6 (experiments/PR1_protocol-reads-existing-networks/prereg.md). Zero GPU: stored scores of the 15 FS1 networks
(A, B, Sb x seeds 403-407), read from the tar members after a sha256 check. Development data only.
  python -I pr1_read.py --out OUT.json            (the registered read, once)
  python -I pr1_read.py --mock --out MOCK.json    (random logits over the true row ids; code test only)"""
import argparse
import csv
import hashlib
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

RES = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
MAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
MAN_SHA = "f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045"
AR1_LIST = pathlib.Path("/mnt/t7/smad_next/AF0/lists/ar1.csv")
CUE_LAD = pathlib.Path("/mnt/t7/smad_next/AF0/cues/ar1.npz")
CUE_SPL = pathlib.Path("/mnt/t7/smad_next/PN1/cues/splice_nat.npz")
TRAIN_SB = pathlib.Path("/mnt/t7/smad_next/PN1/manifests2/train_Sb.csv")
ARMS, SEEDS = ("A", "B", "Sb"), (403, 404, 405, 406, 407)
FAMS = {"af0", "ladder", "splice", "ffhq", "ffhq_lcomb"}
FORBID = ("fst", "valx", "a12sp", "a12-sp", "frll", "mad22", "mordiff", "dim_", "/dim", "h1", "fei", "casia")
B = 2000


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def auc(p, n):
    p, n = np.asarray(p, float), np.asarray(n, float)
    if len(p) == 0 or len(n) == 0:
        return None
    from scipy.stats import rankdata
    r = rankdata(np.r_[p, n])[: len(p)]
    return float((r.sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n)))


def share(x, gt=True, t=0.0):
    x = np.asarray(x, float)
    if len(x) == 0:
        return None
    return float((x > t).mean()) if gt else float((x <= t).mean())


def boot_auc(p, n, seed):
    rng = np.random.default_rng(seed)
    p, n = np.asarray(p, float), np.asarray(n, float)
    v = [auc(p[rng.integers(0, len(p), len(p))], n[rng.integers(0, len(n), len(n))]) for _ in range(B)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def count(vals, cond):
    """seeds meeting cond; missing (None) never meets it; denominator 5"""
    return int(sum(1 for v in vals if v is not None and cond(v)))


# ----------------------------------------------------------------- data
def manifest():
    assert sha(MAN) == MAN_SHA, "manifest off its pin"
    rows = list(csv.DictReader(open(MAN)))
    for r in rows:
        assert r["fam"] in FAMS, r["fam"]
        assert r["path"].startswith(("eval/pn1/", "eval/hn2/", "eval/a14/")), r["path"]
        assert not any(f in r["path"].lower() for f in FORBID), r["path"]
    return rows


def load_net(arm, seed, mock, ids_eval, train_ids):
    t = RES / f"PN1_{arm}_s{seed}.tar"
    want = (RES / f"PN1_{arm}_s{seed}.tar.sha256").read_text().split()[0]
    got = sha(t)
    assert got == want, f"{t} sha256 {got} != {want}"
    n = f"PN1_{arm}_s{seed}"
    with tarfile.open(t) as tf:
        ev = np.load(io.BytesIO(tf.extractfile(f"{n}/scores_eval.npz").read()))
        trn = np.load(io.BytesIO(tf.extractfile(f"{n}/scores_train.npz").read()))
        info = json.loads(tf.extractfile(f"{n}/info.json").read())
        ev = {k: ev[k] for k in ev.files}
        trn = {k: trn[k] for k in trn.files}
    if mock:
        rng = np.random.default_rng(seed * 10 + ARMS.index(arm))
        ev["logit"] = rng.normal(-1, 2, len(ev["id"])).astype(np.float32)
        trn["logit"] = rng.normal(-1, 2, len(trn["path"])).astype(np.float32)
    e = dict(zip(ev["id"].tolist(), ev["logit"].astype(float).tolist()))
    assert set(e) == ids_eval, "eval ids differ from the manifest"
    tr = [dict(path=p, kind=k, label=int(lb), logit=float(lg))
          for p, k, lb, lg in zip(trn["path"].tolist(), trn["kind"].tolist(), trn["label"].tolist(), trn["logit"].tolist())]
    return dict(eval=e, train=tr, tar_sha256=got, info=info)


# ----------------------------------------------------------------- selectors
class Sel:
    def __init__(self, rows):
        self.rows = rows

    def ids(self, **kw):
        out = []
        for r in self.rows:
            if all((r[k] in v) if isinstance(v, (tuple, set, list)) else r[k] == v for k, v in kw.items()):
                out.append(r["id"])
        return out


def half(key):
    return hashlib.sha256(key.encode()).digest()[0] % 2 == 0     # True = calibration half


def pools(rows):
    S = Sel(rows)
    by = {r["id"]: r for r in rows}
    P = {}
    # genuine, native
    P["c1_af0_photo_dev"] = S.ids(fam="af0", role="dev", rung="photo", strength="")
    P["c1_lad_R0_dev"] = S.ids(fam="ladder", role="dev", rung="R0", strength="")
    bona = S.ids(fam="ffhq", rung="ffhq_bona_orig")
    P["ffhq_bona_all"] = bona
    P["c2_ffhq_bona_cal"] = [i for i in bona if half(by[i]["host"])]
    P["ffhq_bona_eval"] = [i for i in bona if not half(by[i]["host"])]
    lcr = S.ids(fam="ffhq", rung="landmark_complete_resmatch")
    lbr = S.ids(fam="ffhq_lcomb", rung="landmark_combined_resmatch")
    P["ffhq_lcomplete_resmatch_eval"] = [i for i in lcr if not half(by[i]["host"])]
    P["ffhq_lcombined_resmatch_eval"] = [i for i in lbr if not half(by[i]["host"])]
    P["ffhq_lcomplete_resmatch_all"] = lcr
    P["ffhq_lcombined_resmatch_all"] = lbr
    for role in ("dev", "test"):
        for st in ("", "61", "112"):
            P[f"lad_R0_{role}_{st or 'nat'}"] = S.ids(fam="ladder", role=role, rung="R0", strength=st)
    for st in ("61", "112"):
        P[f"af0_photo_dev_{st}"] = S.ids(fam="af0", role="dev", rung="photo", strength=st)
    # one-person (protocol genuine) and attack pools
    for role in ("dev", "test"):
        for rg in ("R2w", "R3", "R3m", "R4"):
            for tool in ("opencv", "facemorpher"):
                for st in ("", "61", "112"):
                    k = f"lad_{rg}_{tool}_{role}_{st or 'nat'}"
                    v = S.ids(fam="ladder", role=role, rung=rg, tool=tool, strength=st)
                    if v:
                        P[k] = v
        for rg in ("S0", "S3", "S4"):
            P[f"spl_{rg}_{role}"] = S.ids(fam="splice", role=role, rung=rg)
    for rg in ("halfA", "halfB", "zero", "u50"):
        P[f"af0_{rg}_dev"] = S.ids(fam="af0", role="dev", rung=rg, strength="")
    P["lcomb_orig"] = S.ids(fam="ffhq_lcomb", rung="landmark_combined_orig")
    P["lcomplete_orig"] = S.ids(fam="ffhq", rung="landmark_complete_orig")
    # H-new-4 pools (TT1 prereg section 8): ladder R4 native both roles/engines (582), af0 u50 (180), splice S4 (291)
    P["hn4_lad_R4"] = S.ids(fam="ladder", rung="R4", strength="")
    P["hn4_af0_u50"] = S.ids(fam="af0", rung="u50")
    P["hn4_spl_S4"] = S.ids(fam="splice", rung="S4")
    assert len(P["hn4_lad_R4"]) == 582 and len(P["hn4_af0_u50"]) == 180 and len(P["hn4_spl_S4"]) == 291, \
        (len(P["hn4_lad_R4"]), len(P["hn4_af0_u50"]), len(P["hn4_spl_S4"]))
    for k, v in P.items():
        assert v, f"empty pool {k}"
    return P


def tau5(e, P):
    """smallest cut-off t with flag share (logit > t) <= 0.05 in each calibration source"""
    c1 = np.array([e[i] for i in P["c1_af0_photo_dev"] + P["c1_lad_R0_dev"]])
    c2 = np.array([e[i] for i in P["c2_ffhq_bona_cal"]])
    cand = np.unique(np.r_[c1, c2])
    for t in cand:                     # ascending: first t that protects both sources
        if (c1 > t).mean() <= 0.05 and (c2 > t).mean() <= 0.05:
            return float(t), float((c1 > t).mean()), float((c2 > t).mean())
    raise RuntimeError("no tau5")


# ----------------------------------------------------------------- parts
def z_eval_tables(e, P, t5):
    g = {}
    for k, v in P.items():
        x = np.array([e[i] for i in v])
        g[k] = dict(n=len(v), above_own=share(x), above_t5=share(x, t=t5), median=float(np.median(x)))
    return g


def stratified_auc(pos, neg, cpos, cneg, q=5):
    lp, ln_ = np.log(np.asarray(cpos) + 1e-12), np.log(np.asarray(cneg) + 1e-12)
    edges = np.quantile(np.r_[lp, ln_], np.linspace(0, 1, q + 1))
    bp = np.clip(np.searchsorted(edges, lp, side="right") - 1, 0, q - 1)
    bn = np.clip(np.searchsorted(edges, ln_, side="right") - 1, 0, q - 1)
    num = den = 0.0
    per = []
    for b in range(q):
        p, n = np.asarray(pos)[bp == b], np.asarray(neg)[bn == b]
        if len(p) and len(n):
            a = auc(p, n)
            w = len(p) * len(n)
            num += a * w
            den += w
            per.append(dict(stratum=b, n_pos=int(len(p)), n_neg=int(len(n)), auc=a))
    return (num / den if den else None), per


def spearman(x, y):
    from scipy.stats import spearmanr
    if len(x) < 3:
        return None
    return float(spearmanr(x, y).correlation)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    rows = manifest()
    by = {r["id"]: r for r in rows}
    P = pools(rows)
    ids_eval = set(by)
    nets = {(arm, s): load_net(arm, s, a.mock, ids_eval, None) for arm in ARMS for s in SEEDS}
    out = dict(mock=a.mock, manifest_sha256=MAN_SHA, pools_n={k: len(v) for k, v in P.items()},
               tars={f"{k[0]}_s{k[1]}": v["tar_sha256"] for k, v in nets.items()}, per_net={})
    # engine check of training rows (fact check, no score)
    ar1 = {r["id"]: r for r in csv.DictReader(open(AR1_LIST))}
    eng = {}
    for r in csv.DictReader(open(TRAIN_SB)):
        if r["kind"] in ("lad_R4", "lad_R2w", "lad_R0", "lad_half"):
            i = pathlib.Path(r["path"]).stem
            eng.setdefault(r["kind"], {}).setdefault(ar1[i]["tool"] if i in ar1 else "not_in_ar1", 0)
            eng[r["kind"]][ar1[i]["tool"] if i in ar1 else "not_in_ar1"] += 1
        elif r["kind"] in ("lad_S0", "lad_S3", "lad_S4"):
            t = "opencv" if "_opencv_" in r["path"] else "other"
            eng.setdefault(r["kind"], {}).setdefault(t, 0)
            eng[r["kind"]][t] += 1
    out["z3_train_engine_Sb_list"] = eng
    zl, zs = np.load(CUE_LAD), np.load(CUE_SPL)
    li = list(zl["names"]).index("lapvar_face")
    lap = {str(i): float(c[li]) for i, c in zip(zl["ids"], zl["cues"])}
    lap.update({str(i): float(c[li]) for i, c in zip(zs["ids"], zs["cues"])})
    rng_seed = 20261141
    for (arm, s), N in nets.items():
        e = N["eval"]
        t5, c1r, c2r = tau5(e, P)
        G = z_eval_tables(e, P, t5)
        v = lambda k: np.array([e[i] for i in P[k]])          # noqa: E731
        R = dict(tau5=t5, tau5_cal_flags=dict(c1=c1r, c2=c2r), pools=G)
        # Z0 / Z4 AUCs
        A_ = {}
        for role in ("dev", "test"):
            A_[f"S3_vs_S0_{role}"] = auc(v(f"spl_S3_{role}"), v(f"spl_S0_{role}"))
            A_[f"S4_vs_S3_{role}"] = auc(v(f"spl_S4_{role}"), v(f"spl_S3_{role}"))
            A_[f"S4_vs_S0_{role}"] = auc(v(f"spl_S4_{role}"), v(f"spl_S0_{role}"))
            for tool in ("opencv", "facemorpher"):
                r4 = v(f"lad_R4_{tool}_{role}_nat")
                for neg in ("R2w", "R3", "R3m"):
                    A_[f"R4_vs_{neg}_{tool}_{role}"] = auc(r4, v(f"lad_{neg}_{tool}_{role}_nat"))
                A_[f"R4_vs_R0_{tool}_{role}"] = auc(r4, v(f"lad_R0_{role}_nat"))
                A_[f"R2w_vs_R0_{tool}_{role}"] = auc(v(f"lad_R2w_{tool}_{role}_nat"), v(f"lad_R0_{role}_nat"))
                A_[f"R3_vs_R0_{tool}_{role}"] = auc(v(f"lad_R3_{tool}_{role}_nat"), v(f"lad_R0_{role}_nat"))
        A_["lcomb_vs_resmatch"] = auc(v("lcomb_orig"), v("ffhq_lcombined_resmatch_all"))
        A_["lcomplete_vs_resmatch"] = auc(v("lcomplete_orig"), v("ffhq_lcomplete_resmatch_all"))
        A_["lcomb_vs_devS3"] = auc(v("lcomb_orig"), v("spl_S3_dev"))
        R["auc"] = A_
        # Z2c printed: lcomb miss at cut-offs flagging 10% / 20% of dev S3
        s3 = v("spl_S3_dev")
        R["z2c_lcomb_miss_at_S3_flag"] = {str(q): share(v("lcomb_orig"), gt=False, t=float(np.quantile(s3, 1 - q)))
                                          for q in (0.10, 0.20)}
        # Z2a
        gk = ("ffhq_bona_eval", "ffhq_lcomplete_resmatch_eval", "ffhq_lcombined_resmatch_eval", "lad_R0_test_nat",
              "lad_R0_test_61", "lad_R0_test_112")
        gmax = max(G[k]["above_t5"] for k in gk)
        R["z2a"] = dict(G_max=gmax, G_max_pool=max(gk, key=lambda k: G[k]["above_t5"]),
                        lcomb_miss_t5=share(v("lcomb_orig"), gt=False, t=t5),
                        usable=bool(gmax <= 0.10 and share(v("lcomb_orig"), gt=False, t=t5) <= 0.30))
        # Z2-rho inputs
        y_own = float(np.mean([share(v(k), gt=False) for k in ("hn4_lad_R4", "hn4_af0_u50", "hn4_spl_S4")]))
        y_t5 = float(np.mean([share(v(k), gt=False, t=t5) for k in ("hn4_lad_R4", "hn4_af0_u50", "hn4_spl_S4")]))
        R["z2rho"] = dict(x_own=share(v("ffhq_bona_all")), y_own=y_own, x_t5=gmax, y_t5=y_t5)
        # Z3 (test natives, paired by host)
        z3 = {}
        for role in ("test", "dev"):
            hp = {}
            for tool in ("opencv", "facemorpher"):
                for rg in ("R4", "R2w"):
                    hp[(tool, rg)] = {by[i]["host"]: e[i] for i in P[f"lad_{rg}_{tool}_{role}_nat"]}
            hosts = sorted(set.intersection(*[set(d) for d in hp.values()]))
            M = {k: np.array([d[h] for h in hosts]) for k, d in hp.items()}
            acv = auc(M[("opencv", "R4")], M[("opencv", "R2w")])
            afm = auc(M[("facemorpher", "R4")], M[("facemorpher", "R2w")])
            rng = np.random.default_rng(rng_seed)
            bs = []
            for _ in range(B):
                ix = rng.integers(0, len(hosts), len(hosts))
                bs.append(auc(M[("opencv", "R4")][ix], M[("opencv", "R2w")][ix])
                          - auc(M[("facemorpher", "R4")][ix], M[("facemorpher", "R2w")][ix]))
            z3[role] = dict(n_hosts=len(hosts), auc_cv=acv, auc_fm=afm, delta=acv - afm,
                            delta_ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                            r4_vs_r0_cv=A_[f"R4_vs_R0_opencv_{role}"], r4_vs_r0_fm=A_[f"R4_vs_R0_facemorpher_{role}"],
                            miss_own_cv=share(M[("opencv", "R4")], gt=False), miss_own_fm=share(M[("facemorpher", "R4")], gt=False),
                            miss_t5_cv=share(M[("opencv", "R4")], gt=False, t=t5),
                            miss_t5_fm=share(M[("facemorpher", "R4")], gt=False, t=t5))
        R["z3"] = z3
        # Z1 (training rows)
        tk = {}
        for row in N["train"]:
            tk.setdefault(row["kind"], []).append(row["logit"])
        z1 = {k: dict(n=len(x), above_own=share(x), median=float(np.median(x))) for k, x in tk.items()}
        R["z1"] = dict(kinds=z1)
        if "lad_S3" in tk:
            R["z1"].update(f_tr_S3=share(tk["lad_S3"]), m_tr_S4=share(tk["lad_S4"], gt=False),
                           auc_tr_S3_vs_S0=auc(tk["lad_S3"], tk["lad_S0"]), auc_tr_S4_vs_S3=auc(tk["lad_S4"], tk["lad_S3"]))
        R["train_acc_rule0_info"] = N["info"].get("train_acc_rule0")
        # Z6
        def lv(k):
            ids = [i for i in P[k] if i in lap]
            return np.array([e[i] for i in ids]), np.array([lap[i] for i in ids]), len(P[k]) - len(ids)
        p4, c4, m4 = lv("lad_R4_opencv_test_nat")
        p2, c2, m2 = lv("lad_R2w_opencv_test_nat")
        sa, per = stratified_auc(p4, p2, c4, c2)
        s4, cs4, ms4 = lv("spl_S4_test")
        s3_, cs3, ms3 = lv("spl_S3_test")
        sa2, per2 = stratified_auc(s4, s3_, cs4, cs3)
        rho = {}
        for k in ("lad_R0_test_nat", "lad_R2w_opencv_test_nat", "lad_R3_opencv_test_nat", "lad_R4_opencv_test_nat",
                  "spl_S0_test", "spl_S3_test", "spl_S4_test"):
            x, c, _ = lv(k)
            rho[k] = spearman(x, np.log(c + 1e-12))
        R["z6"] = dict(strat_auc_R4_vs_R2w=sa, strata=per, auc_R4_vs_R2w=auc(p4, p2),
                       strat_auc_S4_vs_S3=sa2, strata_S=per2, auc_S4_vs_S3=auc(s4, s3_), rho_logit_loglap=rho,
                       missing_cues=dict(R4=m4, R2w=m2, S4=ms4, S3=ms3))
        out["per_net"][f"{arm}_s{s}"] = R
    # cue-only numbers (direction-free), once
    zz = lambda k: np.array([lap[i] for i in P[k] if i in lap])   # noqa: E731
    a1 = auc(zz("lad_R4_opencv_test_nat"), zz("lad_R2w_opencv_test_nat"))
    out["z6_lapvar_face_alone_R4_vs_R2w"] = max(a1, 1 - a1)
    a2 = auc(zz("spl_S4_test"), zz("spl_S3_test"))
    out["z6_lapvar_face_alone_S4_vs_S3"] = max(a2, 1 - a2)
    # ---------------------------------------------------------- verdicts
    V = {}
    pn = out["per_net"]
    get = lambda arm, f: [f(pn[f"{arm}_s{s}"]) for s in SEEDS]   # noqa: E731
    # Z1 (Sb)
    f3, m4_ = get("Sb", lambda r: r["z1"].get("f_tr_S3")), get("Sb", lambda r: r["z1"].get("m_tr_S4"))
    under = sum(1 for x, y in zip(f3, m4_) if (x is not None and x >= 0.20) or (y is not None and y >= 0.15))
    fitg = sum(1 for x, y in zip(f3, m4_) if x is not None and y is not None and x <= 0.05 and y <= 0.05)
    V["Z1_Sb"] = dict(f_tr_S3=f3, m_tr_S4=m4_, n_underfit=under, n_fit=fitg,
                      verdict="underfit" if under >= 4 else ("fit, does not generalise" if fitg >= 4 else "mixed, no claim"))
    # Z2a
    for arm in ARMS:
        u = get(arm, lambda r: r["z2a"]["usable"])
        n = sum(u)
        V[f"Z2a_{arm}"] = dict(usable=u, n=n, verdict="usable operating point" if n >= 4 else
                               ("no usable operating point" if n <= 1 else "inconclusive, no claim"))
    # Z2c (Sb)
    c = get("Sb", lambda r: r["auc"]["lcomb_vs_devS3"])
    V["Z2c_Sb"] = dict(auc=c, verdict="same band (supported)" if count(c, lambda x: x <= 0.65) >= 4 else
                       ("separate bands (falsified)" if count(c, lambda x: x >= 0.80) >= 4 else "inconclusive"))
    # Z2-rho
    from scipy.stats import spearmanr
    keys = [(arm, s) for arm in ARMS for s in SEEDS]
    for tag, xk, yk in (("own", "x_own", "y_own"), ("t5", "x_t5", "y_t5")):
        x = np.array([pn[f"{a_}_s{s}"]["z2rho"][xk] for a_, s in keys])
        y = np.array([pn[f"{a_}_s{s}"]["z2rho"][yk] for a_, s in keys])
        rho = float(spearmanr(x, y).correlation)
        rng = np.random.default_rng(20261142)
        perm = np.array([spearmanr(x, rng.permutation(y)).correlation for _ in range(200000 if not a.mock else 2000)])
        p = float((np.abs(perm) >= abs(rho) - 1e-12).mean())
        within = {arm: spearman(x[i * 5:(i + 1) * 5], y[i * 5:(i + 1) * 5]) for i, arm in enumerate(ARMS)}
        V[f"Z2rho_{tag}"] = dict(rho=rho, p_perm_two_sided=p, within_arm=within, x=x.tolist(), y=y.tolist(),
                                 verdict=(("falsified" if rho >= 0 else ("supported" if rho <= -0.6 else "weak (not decided)"))
                                          if tag == "own" else "printed only"))
    # Z3
    for arm in ARMS:
        d = get(arm, lambda r: r["z3"]["test"]["delta"])
        V[f"Z3_{arm}"] = dict(delta=d, verdict="engine gap" if count(d, lambda x: x >= 0.03) >= 4 else
                              ("no engine gap" if count(d, lambda x: x <= 0.01) >= 4 else "inconclusive, no claim"))
    # Z4
    for arm in ARMS:
        fr2 = get(arm, lambda r: r["pools"]["lad_R2w_opencv_test_nat"]["above_own"])
        a42 = get(arm, lambda r: r["auc"]["R4_vs_R2w_opencv_test"])
        n_ok = sum(1 for f, x in zip(fr2, a42) if f <= 0.05 and x >= 0.90)
        V[f"Z4_row6_R2w_{arm}"] = dict(f=fr2, auc_R4_vs_R2w=a42, verdict="warp-only not flagged" if n_ok >= 4 else
                                       ("warp-only flagged" if count(fr2, lambda x: x >= 0.20) >= 4 else "inconclusive, no claim"))
        for rg, key in (("R3", "lad_R3_opencv_test_nat"), ("R3m", "lad_R3m_opencv_test_nat"), ("S3", "spl_S3_test")):
            f = get(arm, lambda r, key=key: r["pools"][key]["above_own"])
            V[f"Z4_{rg}_{arm}"] = dict(f=f, verdict="flagged like a morph" if count(f, lambda x: x >= 0.50) >= 4 else
                                       ("not flagged" if count(f, lambda x: x <= 0.10) >= 4 else "inconclusive"))
        f0 = get(arm, lambda r: r["pools"]["spl_S0_test"]["above_own"])
        a40 = get(arm, lambda r: r["auc"]["S4_vs_S0_test"])
        n0 = sum(1 for f, x in zip(f0, a40) if f <= 0.05 and x >= 0.90)
        V[f"Z4_row9_S0_{arm}"] = dict(f=f0, auc_S4_vs_S0=a40, verdict="seam-only not flagged" if n0 >= 4 else
                                      ("seam-only flagged" if count(f0, lambda x: x >= 0.20) >= 4 else "inconclusive"))
    # Z6
    for arm in ARMS:
        sa = get(arm, lambda r: r["z6"]["strat_auc_R4_vs_R2w"])
        V[f"Z6_{arm}"] = dict(strat_auc=sa, verdict="softness explains" if count(sa, lambda x: x <= 0.70) >= 4 else
                              ("not softness alone" if count(sa, lambda x: x >= 0.85) >= 4 else "inconclusive, no claim"))
    # Z0 fact check (printed)
    def rng_(arm, f):
        xs = [x for x in get(arm, f) if x is not None]
        return [min(xs), max(xs)]
    V["Z0"] = dict(
        Sb_dev_S0_flags_per_seed=get("Sb", lambda r: r["pools"]["spl_S0_dev"]["above_own"]),
        Sb_dev_S3_flags=rng_("Sb", lambda r: r["pools"]["spl_S3_dev"]["above_own"]), cited_S3=[0.31, 0.41],
        Sb_S3_vs_S0_dev=rng_("Sb", lambda r: r["auc"]["S3_vs_S0_dev"]),
        Sb_S3_vs_S0_test=rng_("Sb", lambda r: r["auc"]["S3_vs_S0_test"]), cited_S3_vs_S0=[0.86, 0.93],
        Sb_S4_vs_S3_dev=rng_("Sb", lambda r: r["auc"]["S4_vs_S3_dev"]),
        Sb_S4_vs_S3_test=rng_("Sb", lambda r: r["auc"]["S4_vs_S3_test"]), cited_S4_vs_S3=[0.78, 0.82],
        Sb_lcomb_miss_own=rng_("Sb", lambda r: 1 - r["pools"]["lcomb_orig"]["above_own"]),
        cited_lcomb_miss=[0.26, 0.47],
        AB_dev_S3_flags={arm: rng_(arm, lambda r: r["pools"]["spl_S3_dev"]["above_own"]) for arm in ("A", "B")},
        Sb_dev_S4_miss=rng_("Sb", lambda r: 1 - r["pools"]["spl_S4_dev"]["above_own"]), cited_S4_miss=[0.15, 0.29])
    out["verdicts"] = V
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    for k, x in V.items():
        print(k, x.get("verdict", ""), {kk: vv for kk, vv in x.items() if kk not in ("verdict", "x", "y")})


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()
