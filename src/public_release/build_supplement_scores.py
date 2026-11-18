"""PRIVATE helper (not for the public release): collects the score files behind the supplement benchmark tables
(FRLL-Morphs grid, authors'-recipe retrains, our-recipe retrains, SelfMAD retrains) into one compact file.
Stored per row: method, seed, variant, pool, logit, and for FRLL rows the contributor index (position of the FRLL
person in the sorted person list of the frozen roster, 0..101; no FRLL identifier is stored).
Run:  python3 -I build_supplement_scores.py <release-repo>/results/supplement/scores_supplement.npz"""
import csv, sys, collections
import numpy as np

T7 = "/mnt/t7/smad_next"
ROSTER = f"{T7}/FRLL_READ_V1/FRLL_READ_MANIFEST_V1.csv"
ATHENA = f"{T7}/RS1/regen_pack/manifests/athena_manifest.csv"
RS1MAN = f"{T7}/RS1/manifest.csv"
PROD = f"{T7}/RS1/results_rented"
AD5 = f"{T7}/AD5/scores_retrains"
AD6 = "/home/narolski/ad6_stage/scores_h_sbr"
SM22 = "/home/narolski/ad6_stage/scores_selfmad_m22_final"
FRL = ["amsl", "facemorpher", "opencv", "stylegan", "webmorph"]
M22 = ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"]

roster = list(csv.DictReader(open(ROSTER)))
plist = sorted({p for r in roster for p in r["persons"].split("|")})
assert len(plist) == 102
pidx = {p: i for i, p in enumerate(plist)}


def pool_of(st, lab):
    if st == "G_raw" and lab == "0": return "frll_genuine_raw"
    if st.startswith("M_") and st[2:] in FRL and lab == "1": return "frll_morph_" + st[2:]
    if st == "G22_raw": return "genuine_raw"
    if st == "G22_aln": return "genuine_aligned"
    if st.startswith("E7aln22_"): return "genuine_history_" + st[8:]
    if st.startswith("M22_") and lab == "1": return "morph_" + st[4:]
    return None


def tagmap(path):
    return {r["id"]: (pool_of(r["set"], r["label"]), r["persons"]) for r in csv.DictReader(open(path)) if r["id"] and r["label"] != ""}


ATH, RS1 = tagmap(ATHENA), tagmap(RS1MAN)
ROS = {r["id"]: (pool_of(r["set"], r["label"]), r["persons"]) for r in roster}
rows = []  # method, seed, variant, pool, logit, p1, p2


def add(method, seed, variant, path, tags, key="logit_noTTA", idfix=lambda i: i):
    z = np.load(path, allow_pickle=True)
    n = 0
    for i, v in zip(map(str, z["id"]), np.asarray(z[key], np.float64)):
        t = tags.get(idfix(i))
        if t is None or t[0] is None: continue
        pp = [pidx[p] for p in t[1].split("|")] if t[0].startswith("frll") else []
        pp += [-1] * (2 - len(pp))
        rows.append((method, seed, variant, t[0], v, pp[0], pp[1])); n += 1
    print(f"{method:24s} {seed} {variant} {n}")


# FRLL read v1: Sb (own frames) and SelfMAD release (own preprocessing) on the frozen roster
for s in range(403, 408):
    add("Sb", s, "own", f"{T7}/FRLL_READ_V1/sb_scores_s{s}.npz", ROS, key="logit")
add("SelfMAD-RW", 0, "own", f"{T7}/FRLL_READ_V1/selfmad_own/scores_frll_read_v1.npz", ROS)
# released weights on release crops (prod scoring): FRLL + MAD22
for v in ("v1", "v2"):
    for det, name in (("madation_vitb16", "MADation-B16-RW"), ("madation_vitl14", "MADation-L14-RW"), ("mixfacenet_mad_smdd", "MixFaceNet-MAD-RW")):
        add(name, 0, v, f"{PROD}/prod_{v}_rented/scores/scores_rel_{det}__{v}.npz", ATH)
    # SelfMAD release through the common protocol on the same crops (MAD22 only in the supplement)
    add("SelfMAD-RW", 0, v + "common", f"{SM22}/scores_rel_selfmad_hrnet_w18__m22{v}.npz", ATH)
# authors'-recipe retrains (seeds 401-405)
for s in range(401, 406):
    for v in ("v1", "v2"):
        for pat, name in (("madation_B", "MADation-B16-authors"), ("madation_L", "MADation-L14-authors"), ("mixfacenet_X", "MixFaceNet-MAD-authors")):
            add(name, s, v, f"{AD5}/scores_rel_{pat}_s{s}__ad5{v}.npz", ATH)
        add("SelfMAD-authors", s, v + "common", f"{SM22}/scores_rel_selfmad_S_s{s}__m22{v}.npz", ATH)
    add("SelfMAD-authors", s, "own", f"{T7}/AD5/scores_selfmad/scores_own_selfmad_S_s{s}__ad5.npz", RS1)
# our-recipe retrains (seeds 401-405)
for s in range(401, 406):
    for v in ("v1", "v2"):
        for arm, name in (("madation_B_sbr", "MADation-B16-ours"), ("madation_L_sbr", "MADation-L14-ours"), ("mixfacenet_X_sbr", "MixFaceNet-MAD-ours")):
            add(name, s, v, f"{AD6}/scores_h_{arm}_s{s}__ad6{v}.npz", ATH)

m, sd, var, pool, lg, p1, p2 = zip(*rows)
cat = lambda a: (lambda u: (u, np.searchsorted(u, np.array(a)).astype(np.int16)))(np.array(sorted(set(a))))
out = {}
for k, a in (("method", m), ("variant", var), ("pool", pool)):
    u, c = cat(a); out[k + "_names"] = u; out[k] = c
out.update(seed=np.array(sd, np.int16), logit=np.array(lg, np.float32), person1=np.array(p1, np.int8), person2=np.array(p2, np.int8))
np.savez_compressed(sys.argv[1], **out)
print(len(rows), collections.Counter(pool))
