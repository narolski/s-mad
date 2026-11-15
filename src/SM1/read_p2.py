"""SM1 Part 2 reader: partner audit of released detectors (and of the Part 3 heads, difference-in-differences).

Per score set (logit_noTTA of a release on own crops; or a Part 3 head's logit on whole-image features):
  paired gap = mean over keys of [mean of its 5 key x P logits - mean of its 5 key x U logits]; 95% percentile
  interval, 10,000 key-bootstrap draws (seed 20261111); AUC key x P vs key x U (2,000 key draws); per-slot gaps; exact
  sign-flip p over the 5 matched slots; two-way (keys x slots) bootstrap; placebo test (A1.1): first 100 keys, per
  partner mean over the keys for 5 P + 5 U + 20 X, Mann-Whitney U of P above the 25 unused, exact p over all
  C(30, 5) labelings; responsiveness (A1.4): AUC all audit morphs vs the 500 key renders; render logits of P and U as
  percentiles of the key renders; P x P and U x U means.
Keys whose crop failed on any of their KP/KU images are dropped (count printed).

  python3 -I read_p2.py [--smoke] [--dets ...]
-> RES/p2_<tag>.json
"""
import argparse
import csv
import itertools
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402

PRIMARY = ("madation_vitb16", "madation_vitl14", "madation_fe_vitb16", "madation_fe_vitl14", "mixfacenet_mad_smdd")
DESCR = ("madation_fs_vitb16", "madation_fs_vitl14")
ARMS = ("a", "b", "bp", "c", "cr", "d", "e", "d50", "d500", "a256", "dplus")
COMBS = np.array(list(itertools.combinations(range(30), 5)))


def audit_meta():
    return list(csv.DictReader(open(K.OUT / "flists/audit.csv")))


def analyse(meta, z, B=10000):
    """z: {id: logit} (missing = crop failed)."""
    keys = sorted({r["key"] for r in meta if r["kind"] in ("KP", "KU")})
    kp = {(r["key"], int(r["slot"])): r["id"] for r in meta if r["kind"] == "KP"}
    ku = {(r["key"], int(r["slot"])): r["id"] for r in meta if r["kind"] == "KU"}
    full = [k for k in keys if all(kp[(k, j)] in z and ku[(k, j)] in z for j in range(5))]
    if not full:
        return None
    P = np.array([[z[kp[(k, j)]] for j in range(5)] for k in full])
    U = np.array([[z[ku[(k, j)]] for j in range(5)] for k in full])
    D = P - U
    gk = D.mean(1)
    rng = np.random.default_rng(K.SEED)
    n = len(full)
    idx = rng.integers(0, n, (B, n))
    boot = gk[idx].mean(1)
    out = dict(n_keys=n, n_keys_dropped=len(keys) - n, gap=float(gk.mean()), gap_ci=S.ci(boot),
               gap_prob_scale=None)
    # AUC KP vs KU, key bootstrap weights
    Cw = np.stack([np.bincount(row, minlength=n) for row in idx[:2000]]).astype(float)
    wP = np.repeat(Cw, 5, axis=1)
    auc_pt = S.wauc(P.ravel(), U.ravel(), np.ones((1, P.size)), np.ones((1, U.size)))[0]
    out["auc_KP_vs_KU"] = float(auc_pt)
    out["auc_ci"] = S.ci(S.wauc(P.ravel(), U.ravel(), wP, wP))
    # per slot
    sl = D.mean(0)
    out["slot_gaps"] = [dict(slot=j, gap=float(sl[j]), ci=S.ci(D[idx[:2000], j].mean(1))) for j in range(5)]
    # sign flip over the 5 matched slots
    T = sl.mean()
    flips = np.array(list(itertools.product((1, -1), repeat=5)))
    out["signflip_p_one_sided"] = float(((flips * sl).mean(1) >= T - 1e-12).mean())
    # two-way bootstrap keys x slots
    js = rng.integers(0, 5, (B, 5))
    out["gap_ci_two_way"] = S.ci(np.array([D[idx[b]][:, js[b]].mean() for b in range(2000)]))
    # placebo (first 100 keys, every partner present)
    kx = {(r["key"], int(r["slot"])): r["id"] for r in meta if r["kind"] == "KX"}
    pk = sorted({k for k, _ in kx})
    pk = [k for k in pk if k in full and all(kx[(k, j)] in z for j in range(20))]
    if pk:
        fi = [full.index(k) for k in pk]
        mP = P[fi].mean(0)
        mU = np.concatenate([U[fi].mean(0), np.array([[z[kx[(k, j)]] for j in range(20)] for k in pk]).mean(0)])
        allm = np.concatenate([mP, mU])
        from scipy.stats import rankdata
        rk_ = rankdata(allm)                                     # average ranks; U = rank sum of trained - 15
        u0 = float(rk_[:5].sum() - 15)
        rs = rk_[COMBS].sum(1) - 15
        out["placebo"] = dict(n_keys=len(pk), trained_means=np.round(mP, 4).tolist(),
                              unused_means=np.round(mU, 4).tolist(), U=u0, U_max=125.0,
                              p_exact=float((rs >= u0 - 1e-9).mean()),
                              trained_rank_among_30=[int((allm > v).sum()) + 1 for v in mP])
    # responsiveness, renders, partner-partner
    rk = [z[r["id"]] for r in meta if r["kind"] == "Rkey" and r["id"] in z]
    mor = np.concatenate([P.ravel(), U.ravel()])
    if rk:
        rk = np.array(rk)
        out["responsive_auc_morphs_vs_key_renders"] = float(S.wauc(mor, rk, np.ones((1, len(mor))),
                                                                   np.ones((1, len(rk))))[0])
        out["responsive"] = bool(out["responsive_auc_morphs_vs_key_renders"] >= 0.70)
        for kind in ("RP", "RU"):
            v = [(r["partner"], z[r["id"]]) for r in meta if r["kind"] == kind and r["id"] in z]
            out[f"render_{kind}"] = [dict(name=n, logit=round(float(x), 4), pct_of_keys=round(float((rk < x).mean()), 4))
                                     for n, x in v]
        out["key_render_logit_mean"] = float(rk.mean())
    for kind in ("PP", "UU"):
        v = [z[r["id"]] for r in meta if r["kind"] == kind and r["id"] in z]
        if v:
            out[f"{kind}_mean"] = float(np.mean(v))
            out[f"{kind}_n"] = len(v)
    out["KP_mean"], out["KU_mean"] = float(P.mean()), float(U.mean())
    out["_gk"], out["_idx_seed"] = gk, K.SEED
    return out


def verdict(o):
    if o is None:
        return "no data"
    lo, hi = o["gap_ci"]
    plac = o.get("placebo", {}).get("p_exact", 1.0)
    if not o.get("responsive", True):
        tag = "descriptive (not responsive)"
    elif lo > 0 and plac < 0.05:
        tag = "partner memorisation"
    elif lo > 0:
        tag = "gap above 0, placebo test not passed"
    elif hi < 0:
        tag = "reversed partner effect"
    else:
        tag = "no gap"
    return tag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seeds", default="401,402,403,404,405")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    meta = audit_meta()
    sd = K.OUT / ("p2scores/smoke" if a.smoke else "p2scores")
    res, gks = {}, {}
    for det in PRIMARY + DESCR:
        f = sd / f"scores_rel_{det}.npz"
        if not f.exists():
            continue
        zf = np.load(f, allow_pickle=False)
        z = {str(i): float(v) for i, v in zip(zf["id"], zf["logit_noTTA"])}
        o = analyse(meta, z)
        if o is None:
            continue
        gks[det] = o.pop("_gk")
        o.pop("_idx_seed")
        o["verdict"] = verdict(o)
        o["role"] = "primary" if det in PRIMARY else "descriptive"
        res[det] = o
    whole = {}
    for det in PRIMARY:
        f = K.OUT / "p2scores/whole" / f"scores_rel_{det}.npz"
        if f.exists():
            zf = np.load(f, allow_pickle=False)
            o = analyse(meta, {str(i): float(v) for i, v in zip(zf["id"], zf["logit_noTTA"])})
            if o is not None:
                o.pop("_gk")
                o.pop("_idx_seed")
                o["verdict"] = verdict(o)
                whole[det] = o
    # Part 3 heads on whole-image features (A1.1 difference-in-differences)
    hd = K.OUT / ("heads/smoke" if a.smoke else "heads")
    heads = {}
    for arm in ARMS + ("feref",):
        per = []
        for s in (a.seeds.split(",") if arm != "feref" else [None]):
            f = hd / f"{arm}_s{s}.npz" if arm != "feref" else K.OUT / "heads/feref.npz"
            if not f.exists():
                continue
            zf = np.load(f, allow_pickle=False)
            z = {str(i): float(v) for i, v in zip(zf["id"], zf["logit"])}
            o = analyse(meta, z, B=2000)
            if o is not None:
                per.append(o)
        if per:
            gk = np.mean([o.pop("_gk") for o in per], 0)
            heads[arm] = dict(gap_seeds=[round(o["gap"], 4) for o in per], gap=float(gk.mean()),
                              placebo_p=[o.get("placebo", {}).get("p_exact") for o in per],
                              responsive=[o.get("responsive_auc_morphs_vs_key_renders") for o in per], _gk=gk)
    did = {}
    rng = np.random.default_rng(K.SEED)
    for x in ("a", "b", "feref"):
        for ref in ("cr", "c"):
            if x in heads and ref in heads and len(heads[x]["_gk"]) == len(heads[ref]["_gk"]):
                d = heads[x]["_gk"] - heads[ref]["_gk"]
                idx = rng.integers(0, len(d), (10000, len(d)))
                did[f"{x}-{ref}"] = dict(did=float(d.mean()), ci=S.ci(d[idx].mean(1)))
    for v in heads.values():
        v.pop("_gk")
    # bridge to the original tool (A3): whole-file audit scores (KP, KE) beside the whole-file T-A scores of the
    # release's own morphs with the same partner (training split: the five trained partners; evaluation split: KE)
    bridge = {}
    tl = K.OUT / "flists/tab_sub.csv"
    if tl.exists():
        tmeta = list(csv.DictReader(open(tl)))
        for det in PRIMARY:
            fw, ft = K.OUT / "p2scores/whole" / f"scores_rel_{det}.npz", K.OUT / "p2scores/tab_sub" / f"scores_rel_{det}.npz"
            if not (fw.exists() and ft.exists()):
                continue
            zw = {str(i): float(v) for i, v in zip(np.load(fw)["id"], np.load(fw)["logit_noTTA"])}
            zt = {str(i): float(v) for i, v in zip(np.load(ft)["id"], np.load(ft)["logit_noTTA"])}
            b = {}
            for kind, split, parts in (("KP", "train", K.PARTNERS), ("KE", "eval", K.EVAL_PARTNERS)):
                for p_ in parts:
                    ours = [zw[r["id"]] for r in meta if r["kind"] == kind and r["partner"] == p_ and r["id"] in zw]
                    orig = [zt[r["id"]] for r in tmeta if r["split"] == split and r["kind"] == "morph"
                            and r["partner"] == p_ and r["id"] in zt]
                    b[f"{split}:{p_}"] = dict(ours_engine_mean=float(np.mean(ours)) if ours else None, n_ours=len(ours),
                                              original_tool_mean=float(np.mean(orig)) if orig else None,
                                              n_original=len(orig))
            bridge[det] = b
    prim = [res[d] for d in PRIMARY if d in res]
    lead = dict(text="no partner memorisation if the paired gap interval includes 0 for every detector",
                n_detectors=len(prim),
                holds=bool(all(o["gap_ci"][0] <= 0 <= o["gap_ci"][1] for o in prim)) if prim else None)
    smddT = dict(text="releases' gap interval includes 0 (A1.2: no primary detector shows partner memorisation)",
                 holds=bool(all(o["verdict"] != "partner memorisation" for o in prim)) if prim else None,
                 strict_holds=lead["holds"])
    tag = "smoke" if a.smoke else "full"
    json.dump(dict(detectors=res, heads=heads, did=did, lead_falsifier=lead, smddT_gap_condition=smddT, bridge=bridge,
                   whole_file_secondary=whole),
              open(K.RES / f"p2_{tag}.json", "w"), indent=1)
    print(json.dumps(dict(lead=lead, smddT=smddT, verdicts={d: o["verdict"] for d, o in res.items()}), indent=1))


if __name__ == "__main__":
    main()
