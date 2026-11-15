"""CB1: C1-F for the FD-MAD re-score (amendment 1): row-wise against the stored A45 scores on the eval.csv rows of the
list (gate = old MAD22 subset, FRLL-Morphs): median |d| <= 1e-3, max |d| <= 1e-2, EER within 0.5 in >= 9 of 10 cells.
Writes OUT/c1f_gate.json, OUT/c1_pass.txt (net ids that pass) and analysis-compatible score files
OUT/compat/FDMAD_<branch-res>_s<seed>_model.npz (logit_noTTA = score_noTTA = score = morph score 1 - s).
  python3 -I fdmad_gate.py --images IMAGES.csv --scores DIR --out OUT"""
import argparse, csv, json, pathlib, re, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from analyse_cnn import w_eer, GATEFAM, FAM

ap = argparse.ArgumentParser(); ap.add_argument("--images"); ap.add_argument("--scores"); ap.add_argument("--out")
a = ap.parse_args(); out = pathlib.Path(a.out); (out / "compat").mkdir(parents=True, exist_ok=True)
rows = list(csv.DictReader(open(a.images))); ids = np.array([r["id"] for r in rows])
res, passed = {}, []
for f in sorted(pathlib.Path(a.scores).glob("fdmad_*_r*_s*.npz"), key=lambda p: ("fused" in p.name, p.name)):
    br, r_, s_ = re.match(r"fdmad_(\w+)_r(\d+)_s(\d)", f.stem).groups()
    z = np.load(f); assert np.array_equal(z["id"], ids)
    net = f"FDMAD_{'g' if br == 'global' else 'f'}{r_}_s{s_}_model"
    np.savez(out / "compat" / f"{net}.npz", id=ids, score=z["score"], score_noTTA=z["score"], logit_noTTA=z["score"])
    st = pathlib.Path(f"/mnt/t7/smad_heldout/a45/fdmad/fdmad_{br}_r{r_}_s{s_}/scores_eval.npz")
    if not st.exists():   # fused: never ran in A45; its global part must equal our gated global run (same res, seed)
        gfile = pathlib.Path(a.scores) / f"fdmad_global_r{r_}_s{s_}.npz"
        gp = res.get(f"FDMAD_g{r_}_s{s_}_model", {}).get("passed")
        if gfile.exists() and gp:
            dg = float(np.abs(np.load(gfile)["s_global"] - z["s_global"]).max())
            p = dg <= 1e-6
            res[net] = dict(global_part_max_abs_vs_gated_global=dg, passed=p, has_face_rows=int(z["has_face"].sum()),
                            note="local branch has no stored reference (never run in A45)")
            if p: passed.append(net)
        else:
            res[net] = dict(passed=None, note="global run of the same res/seed not yet gated")
        continue
    sz = np.load(st); pos = {e: i for i, e in enumerate(sz["id"])}
    cells, meds, mx = [], [], 0.0
    for bench, fams in (("gate", GATEFAM), ("frllm", FAM["frllm"])):
        for fam in fams:
            g = [i for i, r in enumerate(rows) if r["bench"] == bench and r["pool"] == "native" and r["family"] == "bona"]
            m = [i for i, r in enumerate(rows) if r["bench"] == bench and r["pool"] == "native" and r["family"] == fam]
            sel = g + m; y = np.r_[np.zeros(len(g)), np.ones(len(m))]
            mine = z["score"][sel]; stored = sz["score"][[pos[ids[i].split("/", 2)[2]] for i in sel]]
            d = np.abs(mine - stored); meds.append(float(np.median(d))); mx = max(mx, float(d.max()))
            cells.append(dict(bench=bench, family=fam, eer_mine=100 * w_eer(mine, y), eer_stored=100 * w_eer(stored, y)))
    ok = sum(abs(c["eer_mine"] - c["eer_stored"]) <= 0.5 for c in cells)
    p = bool(np.median(meds) <= 1e-3 and mx <= 1e-2 and ok >= 9)
    res[net] = dict(median_cell_medabs=float(np.median(meds)), max_abs=mx, eer_cells_within_0p5=ok, passed=p, cells=cells)
    if p: passed.append(net)
json.dump(res, open(out / "c1f_gate.json", "w"), indent=1)
open(out / "c1_pass.txt", "w").write("\n".join(passed) + "\n")
for k, v in res.items(): print(k, {x: v[x] for x in v if x != "cells"})
