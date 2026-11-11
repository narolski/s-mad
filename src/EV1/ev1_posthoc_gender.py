"""Fixed-threshold re-read (EV1), POST HOC (not pre-registered; added after the gender strata of amendment 1 were read):
identity-dose slope within gender. Person gender is taken from the MorDIFF release's folder names (both contributors of a
morph in `*_female_aligned` are female, etc.); every family is split into female-female, male-male and mixed pairs; the
oracle power check and the primary detectors' slopes are read within each stratum. Same dose, statistic and bootstrap as
ev1_partC.py. Run: python3 -I src/EV1/ev1_posthoc_gender.py
"""
import csv, json, sys, time, pathlib
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ev1_common as K  # noqa: E402

T0 = time.time()
SMOKE = "--smoke" in sys.argv
A46 = pathlib.Path("/mnt/t7/smad_heldout/a46/feat/a46_feat.npz")
MDR = pathlib.Path("/mnt/t7/Datasety/downloads/MorDIFF/MorDIFF_crop")
MORPH_GROUP = {"mordiff": "pub_mordiff", "dim_c": "pub_dim_c", "greedy_dim": "pub_greedy_dim", "greedy_dim_s": "pub_greedy_dim_s"}


def main():
    rows = [r for r in K.eval_rows() if r["set"] != "mad22" and r["variant"] != "chip"]
    I = K.Index(rows)
    ids = [r["id"] for r in rows]
    z = np.load(A46, allow_pickle=False)
    E = z["emb"].astype(np.float64)
    E /= np.linalg.norm(E, axis=1, keepdims=True)
    A = {str(k): e for k, e, f in zip(z["keys"], E, z["found"]) if f}
    raw = {k.split("|", 1)[1]: v for k, v in A.items() if k.startswith("raw|")}
    gp, conflict = {}, set()
    for d in MDR.glob("*_front_*_aligned"):
        g = "F" if "_female_" in d.name else "M"
        for p in (d / "morphed").glob("*.png"):
            m = K.RXM_MD.match(p.name)
            for q in (m.group(1), m.group(3)):
                if gp.get(q, g) != g:
                    conflict.add(q)
                gp[q] = g
    D = K.Draw(sorted({p for r in rows if r["pers"] for p in r["pers"]}), 50 if SMOKE else K.B_FULL, K.SEED)
    dets = [d for d in K.detectors() if d["block"] != "other recipe"][: 1 if SMOKE else None]
    S = {d["name"]: K.load_scores(d, "eval", ids)[0] for d in dets}
    OR, SL = [], []
    for f in (K.FAMS[:1] + ("mordiff",)) if SMOKE else K.FAMS:
        mi = [i for i in I.morph(f) if rows[i]["pers"][0] != rows[i]["pers"][1]]
        for st, ee in (("neutral-neutral", "0303"), ("smiling-smiling", "0808")):
            for gpair in ("FF", "MM", "mixed"):
                ix = [i for i in mi if rows[i]["expr"] == ee and (
                    (gp.get(rows[i]["pers"][0]), gp.get(rows[i]["pers"][1])) == tuple(gpair) if gpair != "mixed"
                    else {gp.get(rows[i]["pers"][0]), gp.get(rows[i]["pers"][1])} == {"F", "M"})]
                if len(ix) < 30:
                    if ix or gpair != "mixed":
                        OR.append([f, st, gpair, len(ix), "", "", "", "fewer than 30 morphs"])
                    continue
                e = ee[:2]
                pa = [(rows[i]["pers"][0] + "_" + e, rows[i]["pers"][1] + "_" + e) for i in ix]
                delta = np.array([1 - raw[a] @ raw[b] for a, b in pa])
                RC = K.RankCache(delta, D.w([rows[i]["pers"] for i in ix]))
                if f in MORPH_GROUP:
                    me = [A.get(f"{MORPH_GROUP[f]}|{rows[i]['stem']}") for i in ix]
                    orc = np.array([1 - min(m @ raw[a], m @ raw[b]) for m, (a, b) in zip(me, pa)])
                    r_ = spearmanr(orc, delta).statistic
                    OR.append([f, st, gpair, len(ix), float(r_), *K.ci(RC.spearman(orc)), "power" if abs(r_) >= 0.3 else "no power"])
                else:
                    OR.append([f, st, gpair, len(ix), "", "", "", "no power (no oracle embeddings)"])
                for d in dets:
                    x = S[d["name"]][ix]
                    if not np.isfinite(x).all():
                        continue
                    SL.append([d["name"], d["block"], f, st, gpair, len(ix), float(spearmanr(x, delta).statistic), *K.ci(RC.spearman(x))])
        print(f"[{time.time() - T0:6.1f}s]", f, [(r[2], r[3], r[7]) for r in OR if r[0] == f], flush=True)
    if SMOKE:
        print("smoke ok", len(OR), len(SL), len(gp), "persons", len(conflict), "conflicts")
        return
    W_ = lambda fn_, hdr, R: (lambda fh: (csv.writer(fh).writerow(hdr), csv.writer(fh).writerows(R)))(open(K.OUT / fn_, "w", newline=""))  # noqa: E731
    W_("PH_gender_oracle.csv", ["family", "stratum", "gender_pair", "n", "rho_oracle", "lo95", "hi95", "power"], OR)
    W_("PH_gender_slopes.csv", ["detector", "block", "family", "stratum", "gender_pair", "n", "spearman", "lo95", "hi95"], SL)
    json.dump({"post_hoc": True, "persons_with_gender": len(gp), "gender_counts": {g: sum(v == g for v in gp.values()) for g in "FM"},
               "conflicting_persons": sorted(conflict)}, open(K.OUT / "PH_gender.json", "w"), indent=1)
    print("written", len(gp), "persons with gender;", len(conflict), "conflicts", flush=True)


if __name__ == "__main__":
    main()
