"""Fixed-threshold re-read (EV1), Part C: identity dose inside the morph class. Spearman between a morph's score and
the dissimilarity of its two contributors (1 - glintr100 cosine of their photos), per family and expression stratum,
two-way person bootstrap. The oracle power check (1 - lower cosine of the morph to its contributors) runs and is
written first, before any detector score is loaded. Run: python3 -I src/EV1/ev1_partC.py [--smoke]
"""
import csv, json, sys, time, pathlib
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ev1_common as K  # noqa: E402

SMOKE = "--smoke" in sys.argv
B = 50 if SMOKE else K.B_FULL
T0 = time.time()
A46 = pathlib.Path("/mnt/t7/smad_heldout/a46/feat/a46_feat.npz")
A41G = pathlib.Path("/mnt/t7/smad_heldout/a41_diffae/work/glint_embeddings.npz")
AR1E = pathlib.Path("/mnt/t7/smad_next/AR1/frll_src_emb.npz")
MORPH_GROUP = {"mordiff": "pub_mordiff", "dim_c": "pub_dim_c", "greedy_dim": "pub_greedy_dim", "greedy_dim_s": "pub_greedy_dim_s"}


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def emb_map(path, keykey="keys"):
    z = np.load(path, allow_pickle=False)
    keys = z[keykey] if keykey in z.files else z["stem"]
    E = z["emb"].astype(np.float64)
    E /= np.linalg.norm(E, axis=1, keepdims=True)
    ok = z["found"]
    return {str(k): e for k, e, f in zip(keys, E, ok) if f}


def main():
    rows = [r for r in K.eval_rows() if r["set"] != "mad22" and r["variant"] != "chip"]
    I = K.Index(rows)
    ids = [r["id"] for r in rows]
    A = emb_map(A46)
    raw = {k.split("|", 1)[1]: v for k, v in A.items() if k.startswith("raw|")}
    assert len(raw) == 204
    ar1 = emb_map(AR1E, "stem")
    G41 = emb_map(A41G)
    raw41 = {k.split("|", 1)[1]: v for k, v in G41.items() if k.startswith("raw|")}
    allp = sorted({p for r in rows if r["pers"] for p in r["pers"]})
    D = K.Draw(allp, B, K.SEED)
    fam_items, ORC = {}, []
    # ------------------------------------------------------------------ dose and oracle (no detector score yet)
    for f in K.FAMS:
        mi = [i for i in I.morph(f) if rows[i]["pers"][0] != rows[i]["pers"][1]]
        n_self = len(I.morph(f)) - len(mi)
        for st, ee in (("neutral-neutral", "0303"), ("smiling-smiling", "0808")):
            ix = [i for i in mi if rows[i]["expr"] == ee]
            if SMOKE:
                ix = ix[:40]
            if not ix:
                continue
            e = ee[:2]
            pa = [(rows[i]["pers"][0] + "_" + e, rows[i]["pers"][1] + "_" + e) for i in ix]
            delta = np.array([1 - raw[a] @ raw[b] for a, b in pa])
            d_ar1 = np.array([1 - ar1[a] @ ar1[b] for a, b in pa])
            W = D.w([rows[i]["pers"] for i in ix])
            rec = {"family": f, "stratum": st, "n": len(ix), "n_self_pairs_excluded": n_self,
                   "delta_median": float(np.median(delta)), "delta_iqr": [float(np.percentile(delta, 25)), float(np.percentile(delta, 75))],
                   "delta_vs_AR1_pearson": float(np.corrcoef(delta, d_ar1)[0, 1])}
            orc, src = None, None
            stems = [rows[i]["stem"] for i in ix]
            if f in MORPH_GROUP:
                g = MORPH_GROUP[f]
                me = [A.get(f"{g}|{s}") for s in stems]
                if all(x is not None for x in me):
                    orc = np.array([1 - min(m @ raw[a], m @ raw[b]) for m, (a, b) in zip(me, pa)])
                    src = f"a46 {g}"
            elif f == "dim_a":
                have = [j for j, s in enumerate(stems) if f"dim_a_pub|{s}" in G41]
                if have:
                    jj = np.array(have)
                    me = [G41[f"dim_a_pub|{stems[j]}"] for j in have]
                    o = np.array([1 - min(m @ raw41[pa[j][0]], m @ raw41[pa[j][1]]) for m, j in zip(me, have)])
                    r_ = spearmanr(o, delta[jj]).statistic
                    rep = K.wspearman(o, delta[jj], W[:, jj])
                    rec["secondary_oracle_a41_dim_a_subset"] = {"n": len(have), "rho": float(r_), "ci95": K.ci(rep),
                                                                 "power_at_0.3": bool(abs(r_) >= 0.3)}
            if orc is not None:
                r_ = spearmanr(orc, delta).statistic
                rec.update({"oracle_source": src, "rho_oracle": float(r_), "rho_oracle_ci95": K.ci(K.wspearman(orc, delta, W)),
                            "power": "power" if abs(r_) >= 0.3 else "no power"})
            else:
                rec.update({"oracle_source": None, "rho_oracle": None, "rho_oracle_ci95": [None, None],
                            "power": "no power (no oracle embeddings)"})
            fam_items[(f, st)] = (np.array(ix), delta, K.RankCache(delta, W))
            ORC.append(rec)
            log("oracle", f, st, rec["n"], rec["power"], None if rec["rho_oracle"] is None else round(rec["rho_oracle"], 3),
                "AR1 r", round(rec["delta_vs_AR1_pearson"], 4))
    if not SMOKE:
        json.dump(ORC, open(K.OUT / "C_oracle.json", "w"), indent=1)
        with open(K.OUT / "C_oracle.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["family", "stratum", "n", "self_pairs_excluded", "delta_median", "rho_oracle", "lo95", "hi95", "power",
                        "oracle_source", "delta_vs_AR1_pearson", "secondary_dim_a_a41"])
            for r in ORC:
                w.writerow([r["family"], r["stratum"], r["n"], r["n_self_pairs_excluded"], r["delta_median"], r["rho_oracle"],
                            *r["rho_oracle_ci95"], r["power"], r["oracle_source"], r["delta_vs_AR1_pearson"],
                            json.dumps(r.get("secondary_oracle_a41_dim_a_subset", ""))])
    log("oracle check written; loading detector scores")
    power = {(r["family"], r["stratum"]): r["power"] for r in ORC}
    # ------------------------------------------------------------------ detector slopes
    dets = K.detectors()
    if SMOKE:
        dets = [d for d in dets if d["name"] in ("MADation ViT-L/14 release", "SelfMAD release, own preprocessing")] + \
               [d for d in dets if d.get("method") == "M3L"][:1]
    DOSE = []
    for det in dets:
        s, _ = K.load_scores(det, "eval", ids)
        boot = det["block"] != "other recipe"
        for (f, st), (ix, delta, RC) in fam_items.items():
            x = s[ix]
            if not np.isfinite(x).all():
                continue
            r_ = spearmanr(x, delta).statistic
            lo, hi = K.ci(RC.spearman(x)) if boot else ("", "")
            DOSE.append([det["name"], det["block"], f, st, len(ix), float(r_), lo, hi, power[(f, st)]])
        log(det["name"], [(r[2][:6], round(r[5], 2)) for r in DOSE if r[0] == det["name"]][:6])
    # ------------------------------------------------------------------ falsifiers
    fz = {}
    lm_power = {f: power.get((f, "neutral-neutral")) for f in K.LANDMARK}
    targets = ["MADation ViT-L/14 release"] + [d["name"] for d in dets if d.get("method") == "M3L"]
    inv = {}
    for n in targets:
        cond = []
        for f in K.LANDMARK:
            r = [x for x in DOSE if x[0] == n and x[2] == f and x[3] == "neutral-neutral"]
            if r:
                cond.append(r[0][5] <= 0.10 and r[0][7] != "" and r[0][7] < 0.20)
        inv[n] = {"all_four_flat": bool(cond) and all(cond), "n_families_flat": int(sum(cond))}
    fz["invariance_audit"] = {"power_in_landmark_families": lm_power,
                              "applicable": all(v == "power" for v in lm_power.values()),
                              "per_network": inv}
    fz["invariance_audit"]["reading"] = ("not applicable: power not shown in the FRLL landmark families"
                                         if not fz["invariance_audit"]["applicable"] else
                                         "applied")
    idr = {}
    for det in dets:
        if det["block"] == "other recipe":
            continue
        per = {}
        for f in K.GEN_FAMS:
            for st in ("neutral-neutral", "smiling-smiling"):
                r = [x for x in DOSE if x[0] == det["name"] and x[2] == f and x[3] == st]
                if not r:
                    continue
                r = r[0]
                per[f"{f} {st}"] = {"rho": r[5], "ub": r[7], "power": r[8], "ub_le_0.10": (r[7] != "" and r[7] <= 0.10)}
        pw = {k: v for k, v in per.items() if v["power"] == "power"}
        idr[det["name"]] = {"families_with_power": list(pw), "no_identity_reading_in": [k for k, v in pw.items() if v["ub_le_0.10"]],
                            "statement_holds_in_every_powered_generator_family": bool(pw) and all(v["ub_le_0.10"] for v in pw.values())}
    fz["identity_audit"] = idr
    log(json.dumps(fz["invariance_audit"])[:600])
    if SMOKE:
        print("smoke ok")
        return
    with open(K.OUT / "C_dose.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["detector", "block", "family", "stratum", "n", "spearman", "lo95", "hi95", "power"])
        w.writerows(DOSE)
    json.dump({"B": B, "seed": K.SEED, "falsifiers": fz}, open(K.OUT / "C_partC.json", "w"), indent=1)
    log("written")


if __name__ == "__main__":
    main()
