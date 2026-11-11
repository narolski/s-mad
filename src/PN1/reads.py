"""PN1 reads shared by tier 0 (frozen heads) and tier 1 (LoRA networks): given one score per catalogue/eval id (logit or
any monotone score; `prob` tells whether 0.5 or 0 is the own rule), compute thresholds and reads (a) to (h) of
prereg.md sections 5 to 7. Pools are defined on the catalogue rows (pn1lib.catalog or the tier-1 pn1_eval.csv).
"""
import numpy as np

import pn1lib as K

TOOLS = ("opencv", "facemorpher")


def pools(rows):
    """name -> list of rows. Test ladder (T_), development ladder (D_), AF0 validation (V_), benchmarks, H1."""
    P = {}

    def add(name, r):
        P.setdefault(name, []).append(r)

    for r in rows:
        st = ("_" + r["strength"]) if r["strength"] else ""
        if r["fam"] == "ladder" and r["role"] in ("test", "dev"):
            pre = "T_" if r["role"] == "test" else "D_"
            tool = "" if r["rung"] == "R0" else "_" + r["tool"]
            add(f"{pre}{r['rung']}{tool}{st}", r)
        elif r["fam"] == "af0" and r["role"] == "dev":
            rung = "half" if r["rung"] in ("halfA", "halfB") else r["rung"]
            if rung == "half" and r.get("field", "u50") not in ("u50", ""):
                continue
            add(f"V_{rung}{st}", r)
        elif r["fam"] == "bench":
            cell, rung = r["cell"], r["rung"]
            if cell in ("frllm_frll_bona",) or cell.endswith("_bona") or cell == "mad22_BonaFide":
                src = "FRLL" if cell.startswith("frllm") else "MAD22"
                add(f"{src}_bona_{'native' if rung in ('native', 'orig') else rung}", r)
                if src == "FRLL" and r.get("neutral") in (True, "True"):
                    add(f"FRLL_bona_{'native' if rung in ('native', 'orig') else rung}_neutral", r)
            else:
                src = "FRLL" if cell.startswith("frllm") else "MAD22"
                fam = cell.split("_", 1)[1]
                if r["klass"] == "attack":
                    add(f"{src}_{fam}_morph", r)
                else:
                    add(f"{src}_{fam}_e7", r)
        elif r["fam"] == "h1":
            add(f"H1_{'morph' if r['klass'] == 'attack' else 'bona'}", r)
    return P


PROTECTED = ["D_R0", "D_R0_61", "D_R0_112", "V_photo", "V_photo_61", "V_photo_112"]
NATIVE_DEV = ["D_R0", "V_photo"]


def thresholds(S, P, own=0.0):
    """S: dict id -> score. own: the own-rule threshold on this score scale (0 for logits, 0.5 for probabilities)."""
    per = {p: K.thr_at([S[r["id"]] for r in P[p]]) for p in PROTECTED if P.get(p)}
    nat = {p: per[p] for p in NATIVE_DEV if p in per}
    bind = max(per, key=per.get)
    cam = [S[r["id"]] for p in NATIVE_DEV for r in P.get(p, [])]
    return dict(own=own, dev=per[bind], dev_binding=bind, dev_per_pool=per, dev_native=max(nat.values()),
                dev_pools_missing=[p for p in PROTECTED if not P.get(p)], cam5=K.thr_at(cam))


def scores_of(S, rows):
    return np.array([S[r["id"]] for r in rows], float)


def by_host(S, rows):
    return {r["host"]: S[r["id"]] for r in rows}


def paired(S, P, pos, neg, extra_cues=None):
    """AUC pos vs neg (test or dev ladder, host bootstrap); extra_cues: (ids -> 27-vector dict, names) for the excess."""
    if not P.get(pos) or not P.get(neg):
        return dict(missing=[x for x in (pos, neg) if not P.get(x)])
    rp, rn = P[pos], P[neg]
    sp, sn = scores_of(S, rp), scores_of(S, rn)
    extra = None
    if extra_cues is not None:
        cue, names = extra_cues
        if all(r["id"] in cue for r in rp + rn):
            extra = {n: (np.array([cue[r["id"]][j] for r in rp]), np.array([cue[r["id"]][j] for r in rn]))
                     for j, n in enumerate(names)}
    out = K.paired_auc_ci(sp, sn, [r["host"] for r in rp], [r["host"] for r in rn], extra=extra)
    out.update(pos=pos, neg=neg)
    if extra_cues is not None and extra is None:
        out["excess"] = "cues missing"
    return out


def shift(S, P, a, b):
    """mean paired shift a -> b over hosts present in both, in units of the SD of a's scores."""
    if not P.get(a) or not P.get(b):
        return dict(missing=[x for x in (a, b) if not P.get(x)])
    ha, hb = by_host(S, P[a]), by_host(S, P[b])
    hs = sorted(set(ha) & set(hb))
    d = np.array([hb[h] - ha[h] for h in hs])
    sd = float(np.std([ha[h] for h in hs], ddof=1))
    rng = np.random.default_rng(20261111)
    bs = [d[rng.integers(0, len(d), len(d))].mean() / sd for _ in range(2000)]
    return dict(a=a, b=b, n=len(hs), mean_shift=float(d.mean()), median_shift=float(np.median(d)), sd_a=sd,
                shift_sd=float(d.mean() / sd), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)),
                share_rising=float((d > 0).mean()))


def unpaired(S, P, pos, neg, with_eer=True):
    if not P.get(pos) or not P.get(neg):
        return dict(missing=[x for x in (pos, neg) if not P.get(x)])
    sp, sn = scores_of(S, P[pos]), scores_of(S, P[neg])
    out = K.unpaired_auc_ci(sp, sn)
    if with_eer:
        out.update({"eer_" + k: v for k, v in K.eer_ci(sp, sn).items()})
    out.update(pos=pos, neg=neg)
    return out


GENUINE_TABLE = ["T_R0", "T_R0_61", "T_R0_112", "D_R0", "D_R0_61", "D_R0_112", "V_photo", "V_photo_61", "V_photo_112",
                 "FRLL_bona_native", "FRLL_bona_native_neutral", "FRLL_amsl_e7", "FRLL_facemorpher_e7",
                 "FRLL_opencv_e7", "FRLL_webmorph_e7", "FRLL_bona_blur1", "FRLL_bona_resample50", "FRLL_bona_jpeg90",
                 "FRLL_bona_jpeg70", "FRLL_bona_jpeg50", "MAD22_bona_native", "MAD22_FaceMorpher_e7",
                 "MAD22_OpenCV_e7", "MAD22_Webmorph_e7", "MAD22_MIPGAN_I_e7", "MAD22_MIPGAN_II_e7", "H1_bona"]
SINGLE_TABLE = [f"{p}_{r}_{t}{s}" for p in ("T", "D") for r in ("R2w", "R2w4", "R3", "R3m") for t in TOOLS
                for s in ("", "_61", "_112")] + ["V_zero", "V_half"]
ATTACK_TABLE = [f"T_R4_{t}{s}" for t in TOOLS for s in ("", "_61", "_112")] + [f"D_R4_{t}" for t in TOOLS] + \
    ["V_u50", "MAD22_OpenCV_morph", "MAD22_Webmorph_morph", "MAD22_FaceMorpher_morph", "MAD22_MIPGAN_I_morph",
     "MAD22_MIPGAN_II_morph", "FRLL_amsl_morph", "FRLL_facemorpher_morph", "FRLL_opencv_morph", "FRLL_webmorph_morph",
     "FRLL_stylegan_morph", "H1_morph"]
GATING_ATTACK = ["T_R4_opencv", "MAD22_OpenCV_morph", "MAD22_Webmorph_morph", "H1_morph"]
LEFT_OUT_GENUINE = ["T_R0_112", "FRLL_bona_native", "FRLL_amsl_e7", "FRLL_facemorpher_e7", "FRLL_opencv_e7",
                    "FRLL_webmorph_e7", "FRLL_bona_blur1", "FRLL_bona_resample50", "MAD22_bona_native",
                    "MAD22_FaceMorpher_e7", "MAD22_OpenCV_e7", "MAD22_Webmorph_e7", "H1_bona"]


def fixed_table(S, P, t):
    out = {}
    for kind, names in (("genuine_flag", GENUINE_TABLE), ("single_placement", SINGLE_TABLE),
                        ("attack_miss", ATTACK_TABLE)):
        for n in names:
            if not P.get(n):
                continue
            s = scores_of(S, P[n])
            out[n] = dict(kind=kind, **K.rate(s <= t if kind == "attack_miss" else s > t))
    return out


def all_reads(S, P, own, cues27=None):
    T = thresholds(S, P, own)
    R = dict(thresholds=T)
    R["a"] = {f"{w}_vs_R4_{t}": paired(S, P, f"T_R4_{t}", f"T_{w}_{t}", cues27) for w in ("R2w", "R2w4") for t in TOOLS}
    R["b"] = {"R0_61_vs_R4_opencv": paired(S, P, "T_R4_opencv", "T_R0_61"),
              "R2w_61_vs_R4_opencv": paired(S, P, "T_R4_opencv", "T_R2w_opencv_61"),
              "R0_61_vs_R4_facemorpher": paired(S, P, "T_R4_facemorpher", "T_R0_61"),
              "R2w_61_vs_R4_facemorpher": paired(S, P, "T_R4_facemorpher", "T_R2w_facemorpher_61")}
    R["c"] = {"R0_to_R0_61": shift(S, P, "T_R0", "T_R0_61"), "R0_to_R0_112": shift(S, P, "T_R0", "T_R0_112"),
              "R2w_to_R2w_61_opencv": shift(S, P, "T_R2w_opencv", "T_R2w_opencv_61"),
              "R2w_to_R2w_112_opencv": shift(S, P, "T_R2w_opencv", "T_R2w_opencv_112"),
              "R4_to_R4_61_opencv": shift(S, P, "T_R4_opencv", "T_R4_opencv_61")}
    R["d"] = unpaired(S, P, "H1_morph", "H1_bona", with_eer=True)
    R["e"] = {f"{fam}_{g}": unpaired(S, P, f"MAD22_{fam}_morph", f"MAD22_bona_native" if g == "native" else
                                     f"MAD22_{fam}_e7") for fam in ("OpenCV", "Webmorph", "FaceMorpher", "MIPGAN_I",
                                                                     "MIPGAN_II") for g in ("native", "e7")}
    R["e_frll_printed_never_gating"] = {f"{fam}_{g}": unpaired(S, P, f"FRLL_{fam}_morph", "FRLL_bona_native" if
                                                               g == "native" else f"FRLL_{fam}_e7")
                                        for fam in ("amsl", "facemorpher", "opencv", "webmorph") for g in ("native", "e7")}
    R["g"] = {"g1_R2w_vs_R4": paired(S, P, "T_R4_opencv", "T_R2w_opencv"),
              "g2_R2w61_vs_R4": paired(S, P, "T_R4_opencv", "T_R2w_opencv_61"),
              "g3_R2w_vs_R4_61": paired(S, P, "T_R4_opencv_61", "T_R2w_opencv"),
              "g4_R2w112_vs_R4_112": paired(S, P, "T_R4_opencv_112", "T_R2w_opencv_112"),
              "g4b_R2w61_vs_R4_61": paired(S, P, "T_R4_opencv_61", "T_R2w_opencv_61")}
    R["h_R4_vs_R3"] = {t: paired(S, P, f"T_R4_{t}", f"T_R3_{t}") for t in TOOLS}
    R["dev_ladder"] = {"a_R2w_vs_R4_opencv": paired(S, P, "D_R4_opencv", "D_R2w_opencv"),
                       "a_R2w4_vs_R4_opencv": paired(S, P, "D_R4_opencv", "D_R2w4_opencv"),
                       "b_R0_61_vs_R4_opencv": paired(S, P, "D_R4_opencv", "D_R0_61"),
                       "c_R0_to_R0_61": shift(S, P, "D_R0", "D_R0_61")}
    R["fixed"] = {name: fixed_table(S, P, T[key]) for name, key in (("own_rule", "own"), ("dev", "dev"),
                                                                    ("dev_native", "dev_native"))}
    for name, key in (("own_rule", "own"), ("dev", "dev")):
        ms = [R["fixed"][name][c]["rate"] for c in GATING_ATTACK if c in R["fixed"][name]]
        R["fixed"][name]["_family_mean_miss_gating"] = dict(cells=[c for c in GATING_ATTACK if c in R["fixed"][name]],
                                                            mean=float(np.mean(ms)) if ms else None)
    return R


def marks_tier0(R):
    """K0, the 2x2 marks and NU1r marks of prereg section 7 (tier 0)."""
    g = R["g"]
    out = {}
    b2 = R["b"]["R2w_61_vs_R4_opencv"].get("auc")
    out["K0_b_R2w61_lt_0.60"] = None if b2 is None else bool(b2 < 0.60)
    gs = [g[k].get("auc") for k in ("g1_R2w_vs_R4", "g2_R2w61_vs_R4", "g3_R2w_vs_R4_61")]
    los = [g[k].get("lo") for k in ("g1_R2w_vs_R4", "g2_R2w61_vs_R4", "g3_R2w_vs_R4_61")]
    if all(x is not None for x in gs):
        out["2x2_min_g1_g3"] = min(gs)
        out["2x2_pass"] = bool(min(gs) >= 0.85 and min(los) > 0.75 and (g["g4_R2w112_vs_R4_112"].get("auc") or 0) >= 0.70)
        out["2x2_kill_this_feature_set"] = bool(min(gs) < 0.75)
    else:
        out["2x2"] = "not read: " + ", ".join(k for k in g if "missing" in g[k])
    viol = []
    for th in ("own_rule", "dev"):
        for p in LEFT_OUT_GENUINE:
            x = R["fixed"][th].get(p)
            if x and x["rate"] > 0.10:
                viol.append((th, p, round(x["rate"], 4)))
    out["NU_a_violations_gt10pct"] = viol
    nub = []
    for th in ("own_rule", "dev"):
        for p in LEFT_OUT_GENUINE:
            x = R["fixed"][th].get(p)
            if x and x["n"] >= 150 and (x["rate"] > 0.05 or x["hi"] > 0.10):
                nub.append((th, p, round(x["rate"], 4), round(x["hi"], 4)))
    out["NU_b_fails"] = nub
    r61 = [R["fixed"][th].get("T_R4_opencv_61") for th in ("own_rule", "dev")]
    out["NU_d_miss_R4_61"] = None if not all(r61) else [round(x["rate"], 4) for x in r61]
    return out
