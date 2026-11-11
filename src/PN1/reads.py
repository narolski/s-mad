"""PN1 reads shared by tier 0 (frozen heads) and tier 1 (LoRA networks): given one score per id (logits; own rule at 0),
compute thresholds and reads (a) to (h) of prereg.md sections 5 to 7 as changed by amendment 4. Pools are defined on
catalogue rows (pn1lib.catalog, or tier-1 pn1_eval.csv rows in the same format). Ladder bootstrap units: partner
cycles (amendment 4, item 6).
"""
import numpy as np

import pn1lib as K

TOOLS = ("opencv", "facemorpher")
_CYC = None


def cyc(host):
    global _CYC
    if _CYC is None:
        _CYC = K.cycle_map()
    return _CYC.get(host, host)


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
            src = "FRLL" if cell.startswith("frllm") else "MAD22"
            if cell == "frllm_frll_bona" or cell.endswith("_bona") or cell == "mad22_BonaFide":
                v = "native" if rung in ("native", "orig") else rung
                add(f"{src}_bona_{v}", r)
                if src == "FRLL" and r.get("neutral") in (True, "True"):
                    add(f"FRLL_bona_{v}_neutral", r)
            else:
                fam = cell.split("_", 1)[1]
                add(f"{src}_{fam}_{'morph' if r['klass'] == 'attack' else 'e7'}", r)
        elif r["fam"] == "h1":
            add(f"H1_{'morph' if r['klass'] == 'attack' else 'bona'}", r)
    return P


PROTECTED = ["D_R0", "D_R0_61", "D_R0_112", "V_photo", "V_photo_61", "V_photo_112"]
CAMERA = ["D_R0", "V_photo"]


def thresholds(S, P, own=0.0):
    per = {p: K.thr_at([S[r["id"]] for r in P[p]]) for p in PROTECTED if P.get(p)}
    bind = max(per, key=per.get)
    cam = {p: per[p] for p in CAMERA if p in per}
    return dict(own=own, cam=max(cam.values()), cam_binding=max(cam, key=cam.get), V=per.get("V_photo"),
                dev=per[bind], dev_binding=bind, per_pool=per,
                dev_pools_missing=[p for p in PROTECTED if not P.get(p)])


def scores_of(S, rows):
    return np.array([S[r["id"]] for r in rows], float)


def unit(r):
    return cyc(r["host"]) if r["fam"] == "ladder" else r["host"]


def paired(S, P, pos, neg, extra_cues=None):
    """AUC pos vs neg, bootstrap over partner cycles (ladder); extra_cues: (id -> vector, names) for the excess."""
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
    out = K.paired_auc_ci(sp, sn, [unit(r) for r in rp], [unit(r) for r in rn], extra=extra)
    out.update(pos=pos, neg=neg)
    if extra_cues is not None and extra is None:
        out["excess"] = "cues missing for %d images" % sum(1 for r in rp + rn if r["id"] not in extra_cues[0])
    return out


def shift(S, P, a, b, B=2000):
    """mean paired shift a -> b over hosts in both, in SD of a's scores; bootstrap over partner cycles."""
    if not P.get(a) or not P.get(b):
        return dict(missing=[x for x in (a, b) if not P.get(x)])
    ha = {r["host"]: S[r["id"]] for r in P[a]}
    hb = {r["host"]: S[r["id"]] for r in P[b]}
    hs = sorted(set(ha) & set(hb))
    d = np.array([hb[h] - ha[h] for h in hs])
    sd = float(np.std([ha[h] for h in hs], ddof=1))
    units = [cyc(h) for h in hs]
    w, u = K.boot_weights(units, B, 20261111)
    ui = {x: i for i, x in enumerate(u)}
    W = w[:, [ui[x] for x in units]]
    bs = (W * d[None, :]).sum(1) / np.maximum(W.sum(1), 1e-9) / sd
    return dict(a=a, b=b, n=len(hs), n_units=len(u), mean_shift=float(d.mean()), median_shift=float(np.median(d)),
                sd_a=sd, shift_sd=float(d.mean() / sd), lo=float(np.percentile(bs, 2.5)),
                hi=float(np.percentile(bs, 97.5)), share_rising=float((d > 0).mean()))


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
ATTACK_TABLE = [f"{p}_R4_{t}{s}" for p in ("T", "D") for t in TOOLS for s in ("", "_61", "_112")] + \
    ["V_u50", "MAD22_OpenCV_morph", "MAD22_Webmorph_morph", "MAD22_FaceMorpher_morph", "MAD22_MIPGAN_I_morph",
     "MAD22_MIPGAN_II_morph", "FRLL_amsl_morph", "FRLL_facemorpher_morph", "FRLL_opencv_morph", "FRLL_webmorph_morph",
     "FRLL_stylegan_morph", "H1_morph"]
GATING_ATTACK = ["T_R4_opencv", "MAD22_OpenCV_morph", "MAD22_Webmorph_morph", "H1_morph"]
UNSEEN_KERNELS = ["FRLL_bona_blur1", "FRLL_bona_resample50", "FRLL_amsl_e7", "FRLL_facemorpher_e7", "FRLL_opencv_e7",
                  "FRLL_webmorph_e7", "MAD22_OpenCV_e7", "MAD22_Webmorph_e7"]
LEFT_OUT_GENUINE = ["T_R0_112", "FRLL_bona_native"] + UNSEEN_KERNELS + ["MAD22_bona_native", "H1_bona"]
THR_NAMES = ("own", "cam", "dev", "V")


def fixed_table(S, P, t):
    out = {}
    for kind, names in (("genuine_flag", GENUINE_TABLE), ("single_placement", SINGLE_TABLE),
                        ("attack_miss", ATTACK_TABLE)):
        for n in names:
            if not P.get(n):
                continue
            s = scores_of(S, P[n])
            out[n] = dict(kind=kind, **K.rate(s <= t if kind == "attack_miss" else s > t))
    ms = [out[c]["rate"] for c in GATING_ATTACK if c in out]
    out["_family_mean_miss_gating"] = dict(cells=[c for c in GATING_ATTACK if c in out],
                                           mean=float(np.mean(ms)) if ms else None)
    return out


def all_reads(S, P, own, cues=None):
    T = thresholds(S, P, own)
    R = dict(thresholds=T)
    R["a"] = {f"{w}_vs_R4_{t}": paired(S, P, f"T_R4_{t}", f"T_{w}_{t}", cues) for w in ("R2w", "R2w4") for t in TOOLS}
    R["b"] = {"R0_61_vs_R4_opencv": paired(S, P, "T_R4_opencv", "T_R0_61"),
              "R2w_61_vs_R4_opencv": paired(S, P, "T_R4_opencv", "T_R2w_opencv_61"),
              "R0_61_vs_R4_facemorpher": paired(S, P, "T_R4_facemorpher", "T_R0_61"),
              "R2w_61_vs_R4_facemorpher": paired(S, P, "T_R4_facemorpher", "T_R2w_facemorpher_61")}
    R["c"] = {"R0_to_R0_61": shift(S, P, "T_R0", "T_R0_61"), "R0_to_R0_112": shift(S, P, "T_R0", "T_R0_112"),
              "R2w_to_R2w_61_opencv": shift(S, P, "T_R2w_opencv", "T_R2w_opencv_61"),
              "R2w_to_R2w_112_opencv": shift(S, P, "T_R2w_opencv", "T_R2w_opencv_112"),
              "R4_to_R4_61_opencv": shift(S, P, "T_R4_opencv", "T_R4_opencv_61"),
              "R4_to_R4_112_opencv": shift(S, P, "T_R4_opencv", "T_R4_opencv_112")}
    R["d"] = unpaired(S, P, "H1_morph", "H1_bona", with_eer=True)
    R["e"] = {f"{fam}_{g}": unpaired(S, P, f"MAD22_{fam}_morph", "MAD22_bona_native" if g == "native" else
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
                       "g3_R2w_vs_R4_61_opencv": paired(S, P, "D_R4_opencv_61", "D_R2w_opencv"),
                       "c_R0_to_R0_61": shift(S, P, "D_R0", "D_R0_61"), "c_R0_to_R0_112": shift(S, P, "D_R0", "D_R0_112"),
                       "V_u50_vs_V_zero": unpaired(S, P, "V_u50", "V_zero", with_eer=False),
                       "V_u50_vs_V_photo": unpaired(S, P, "V_u50", "V_photo", with_eer=False)}
    R["fixed"] = {k: fixed_table(S, P, T[k]) for k in THR_NAMES if T.get(k) is not None}
    return R


def storage_marks(R):
    """P-c (61.2 px) and P-c2 (sizes and kernels never trained), amendment 4 item 2, at own rule and τ_cam."""
    out = {}
    for name, key, pool in (("P-c", "R0_to_R0_61", "T_R0_61"), ("P-c2", "R0_to_R0_112", "T_R0_112")):
        c = R["c"][key]
        fl = {th: R["fixed"][th].get(pool, {}).get("rate") for th in ("own", "cam")}
        ok = c.get("shift_sd") is not None and c["shift_sd"] <= 0.3 and all(v is not None and v <= 0.10 for v in fl.values())
        out[name] = dict(shift_sd=c.get("shift_sd"), flag=fl, pass_=bool(ok))
    ker = {p: {th: R["fixed"][th][p]["rate"] for th in ("own", "cam")} for p in UNSEEN_KERNELS
           if p in R["fixed"]["own"]}
    out["P-c2_kernels"] = dict(flags=ker, pass_=bool(all(v <= 0.10 for d in ker.values() for v in d.values())))
    j = {p: {th: R["fixed"][th].get(p, {}).get("rate") for th in ("own", "cam")}
         for p in ("FRLL_bona_jpeg90", "FRLL_bona_jpeg70", "FRLL_bona_jpeg50")}
    out["jpeg_flags"] = j
    out["jpeg50_gt10"] = bool(any(v is not None and v > 0.10 for v in j["FRLL_bona_jpeg50"].values()))
    out["jpeg50_le10_both"] = bool(all(v is not None and v <= 0.10 for v in j["FRLL_bona_jpeg50"].values()))
    out["A_violation_parts"] = dict(R0_61_or_left_out_gt10_own=bool(
        (R["fixed"]["own"].get("T_R0_61", {}).get("rate", 0) > 0.10) or
        any(R["fixed"]["own"][p]["rate"] > 0.10 for p in LEFT_OUT_GENUINE if p in R["fixed"]["own"])),
        R0_61_or_left_out_gt10_cam=bool((R["fixed"]["cam"].get("T_R0_61", {}).get("rate", 0) > 0.10) or
                                         any(R["fixed"]["cam"][p]["rate"] > 0.10 for p in LEFT_OUT_GENUINE
                                             if p in R["fixed"]["cam"])))
    return out


def marks_tier0(R):
    """K0, the 2 x 2 marks and NU1r marks (now at own rule and τ_cam; τ_dev printed), plus the storage marks."""
    g = R["g"]
    out = {}
    b2 = R["b"]["R2w_61_vs_R4_opencv"].get("auc")
    out["K0_b_R2w61_lt_0.60"] = None if b2 is None else bool(b2 < 0.60)
    keys = ("g1_R2w_vs_R4", "g2_R2w61_vs_R4", "g3_R2w_vs_R4_61")
    gs, los = [g[k].get("auc") for k in keys], [g[k].get("lo") for k in keys]
    if all(x is not None for x in gs):
        out["2x2_min_g1_g3"] = min(gs)
        out["2x2_pass"] = bool(min(gs) >= 0.85 and min(los) > 0.75 and (g["g4_R2w112_vs_R4_112"].get("auc") or 0) >= 0.70)
        out["2x2_kill_this_feature_set"] = bool(min(gs) < 0.75)
    else:
        out["2x2"] = "not read: " + ", ".join(k for k in g if "missing" in g[k])
    for th in ("own", "cam", "dev"):
        out[f"NU_a_violations_gt10pct_{th}"] = [(p, round(R["fixed"][th][p]["rate"], 4)) for p in LEFT_OUT_GENUINE
                                                if p in R["fixed"][th] and R["fixed"][th][p]["rate"] > 0.10]
        out[f"NU_b_fails_{th}"] = [(p, round(R["fixed"][th][p]["rate"], 4), round(R["fixed"][th][p]["hi"], 4))
                                   for p in LEFT_OUT_GENUINE if p in R["fixed"][th] and R["fixed"][th][p]["n"] >= 150
                                   and (R["fixed"][th][p]["rate"] > 0.05 or R["fixed"][th][p]["hi"] > 0.10)]
        x = R["fixed"][th].get("T_R4_opencv_61")
        out[f"NU_d_miss_R4_61_{th}"] = None if x is None else round(x["rate"], 4)
    out["storage"] = storage_marks(R)
    return out
