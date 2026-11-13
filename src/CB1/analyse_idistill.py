"""CB1: IDistill readings (amendments 3-4). Input: a classifier result tar (idistill_cls_s<seed>.tar, or the smoke tar)
with scores_s<seed>_{best,valbest,last}.csv (folder, file, y_bona, id1, id2, morph_score_id1xid2).
Morph score = id1 x id2. Genuine pools: native = raw FRLL / MAD22 photos (crops); E7 effect read as E7 minus
aligned-native (both aligned frames through the same crop; amendment 1 F7). Binding gate (amendment 3 / 4): test-selected
checkpoint ("best"), FRLL-Morphs native, written crops only: five-family mean within 1.5 of 2.90. Worst case (a morph
without a crop counts as accepted) printed beside. Two-way person bootstrap (B 2000, seed 0).
  python3 -I analyse_idistill.py RESULT.tar OUT_DIR [--seed 401] [--counts STAGE_COUNTS.txt]"""
import argparse, csv, io, json, math, pathlib, re, sys, tarfile
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from analyse_cnn import w_eer, eer_matrix, bpcer_at

PUB = {"amsl": 4.00, "facemorpher": 2.05, "opencv": 2.46, "stylegan": 1.96, "webmorph": 4.01}
PUB_B1 = {"amsl": 21.10, "facemorpher": 4.26, "opencv": 6.14, "stylegan": 8.51, "webmorph": 14.41}
PUB_B20 = {"amsl": 2.85, "facemorpher": 0.16, "opencv": 0.16, "stylegan": 0.08, "webmorph": 0.33}
FR = ["amsl", "facemorpher", "opencv", "stylegan", "webmorph"]
M22 = ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"]
CK = {"best": "test-selected as in the authors' code", "valbest": "selected on the SMDD validation split",
      "last": "stopping epoch set by test-set early stopping"}
RAW_COUNTS = {"frll_amsl": 2175, "frll_facemorpher": 1222, "frll_opencv": 1221, "frll_stylegan": 1222, "frll_webmorph": 1221,
              "mad22_FaceMorpher": 1000, "mad22_OpenCV": 984, "mad22_Webmorph": 500, "mad22_MIPGAN_I": 1000, "mad22_MIPGAN_II": 999}
PID = re.compile(r"(\d{3})")


def persons(folder, f):
    p = PID.findall(f)
    return (p[0], p[1] if len(p) > 1 and folder.startswith(("frll_amsl", "frll_face", "frll_open", "frll_style", "frll_web", "mad22_F", "mad22_O", "mad22_W", "mad22_M")) and "_e7_" not in folder else p[0])


ap = argparse.ArgumentParser(); ap.add_argument("tar"); ap.add_argument("out"); ap.add_argument("--seed", default="401")
a = ap.parse_args(); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
T = tarfile.open(a.tar)
rng = np.random.default_rng(0)
rows_out, gate = [], {}
for ck in CK:
    name = f"./scores_s{a.seed}_{ck}.csv"
    try:
        D = list(csv.DictReader(io.TextIOWrapper(T.extractfile(name))))
    except KeyError:
        print("missing", name); continue
    by = {}
    for r in D:
        by.setdefault(r["folder"], []).append((float(r["morph_score_id1xid2"]), persons(r["folder"], r["file"])))
    allp = sorted({p for v in by.values() for _, pp in v for p in pp})
    pi = {p: i for i, p in enumerate(allp)}
    C = rng.multinomial(len(allp), [1 / len(allp)] * len(allp), size=2000).astype(float)
    def cell(gfold, mfold, worst=False):
        g, m = by.get(gfold, []), by.get(mfold, [])
        s = np.array([x for x, _ in g] + [x for x, _ in m], float)
        y = np.r_[np.zeros(len(g)), np.ones(len(m))]
        pa = np.array([pi[pp[0]] for _, pp in g + m]); pb = np.array([pi[pp[1]] for _, pp in g + m])
        if worst and mfold in RAW_COUNTS:                 # uncropped morphs count as accepted (score below everything)
            k = RAW_COUNTS[mfold] - len(m)
            if k > 0:
                s = np.r_[s, np.full(k, s.min() - 1)]; y = np.r_[y, np.ones(k)]
                return 100 * w_eer(s, y), None, len(g), len(m) + k
        W = np.where(y[None, :] == 1, C[:, pa] * C[:, pb], C[:, pa])
        be = 100 * eer_matrix(s, y, W)
        rec = dict(eer=100 * w_eer(s, y), lo=float(np.percentile(be, 2.5)), hi=float(np.percentile(be, 97.5)))
        for q in (0.01, 0.05, 0.10, 0.20):
            rec[f"bpcer{int(q * 100)}"] = 100 * bpcer_at(s, y, q)
        return rec, be, len(g), len(m)
    for bench, fams, gnat, galn, pref in (("frllm", FR, "frll_bona", "frll_alnnative_bona", "frll_"),
                                          ("mad22c", M22, "mad22_bona", "mad22_alnnative_bona", "mad22_")):
        means = {}
        for pool, gf in (("native", None), ("aligned_native", galn), ("e7", None)):
            vals, boots = [], []
            for fam in fams:
                g = gnat if pool == "native" else galn if pool == "aligned_native" else f"{pref}e7_{fam}"
                rec, be, ng, nm = cell(g, f"{pref}{fam}")
                wc = cell(g, f"{pref}{fam}", worst=True)[0] if pool == "native" else None
                r = dict(ckpt=ck, label=CK[ck], bench=bench, pool=pool, family=fam, n_gen=ng, n_morph=nm, **rec,
                         eer_worstcase_uncropped=wc, published=PUB.get(fam) if bench == "frllm" else None,
                         pub_bpcer1=PUB_B1.get(fam) if bench == "frllm" else None, pub_bpcer20=PUB_B20.get(fam) if bench == "frllm" else None)
                if r["published"] is not None:
                    r["family_window"] = "within" if abs(r["eer"] - r["published"]) <= max(1.5, 0.25 * r["published"]) else "outside"
                rows_out.append(r); vals.append(rec["eer"]); boots.append(be)
            mb = np.mean(boots, 0)
            means[pool] = dict(mean=float(np.mean(vals)), lo=float(np.percentile(mb, 2.5)), hi=float(np.percentile(mb, 97.5)))
            rows_out.append(dict(ckpt=ck, label=CK[ck], bench=bench, pool=pool, family="MEAN5", eer=means[pool]["mean"],
                                 lo=means[pool]["lo"], hi=means[pool]["hi"]))
        if bench == "frllm" and ck == "best":
            m = means["native"]["mean"]
            wc = float(np.mean([r["eer_worstcase_uncropped"] for r in rows_out if r["ckpt"] == "best" and r["bench"] == "frllm"
                                and r["pool"] == "native" and r["family"] in FR]))
            ok = abs(m - 2.90) <= 1.5
            gate = dict(checkpoint=CK["best"], frll_mean_written_crops=m, ci=[means["native"]["lo"], means["native"]["hi"]],
                        published=2.90, margin=1.5, frll_mean_worstcase_uncropped=wc,
                        label=("our retrain on a different stack, one seed: reproduces within tolerance" if ok else
                               "our retrain on a different stack, one seed: does not reproduce"))
keys = []
for r in rows_out:
    for k in r:
        if k not in keys: keys.append(k)
with open(out / f"idistill_s{a.seed}_readings.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows_out)
json.dump(gate, open(out / f"idistill_s{a.seed}_gate.json", "w"), indent=1)
print(json.dumps(gate, indent=1))
for r in rows_out:
    if r["family"] == "MEAN5":
        print(r["ckpt"], r["bench"], r["pool"], f"{r['eer']:.2f} [{r['lo']:.2f}, {r['hi']:.2f}]")
