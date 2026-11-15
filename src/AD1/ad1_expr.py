"""AD1 descriptive add-on: expression-split contrasts (neutral 03 / smiling 08), same draw as ad1_read.py."""
import sys, json, csv, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/AD1")
import ad1_read as R
rows = list(csv.DictReader(open(R.MAN)))
allp = sorted({p for r in rows for p in R.pers_a43(r)})
D = R.Draw(allp, R.B, R.SEED)
out = {}
for lab, a43f, k43, *_ in R.DETS[:4]:
    s = np.load(R.A43 / "a43_out/a43" / a43f / "scores_a43.npz")[k43].astype(float)
    def g(arm, ex=None):
        ii = [i for i, r in enumerate(rows) if r["source"] == "a43" and r["arm"] == arm and (ex is None or r["expr"] == ex)]
        return s[ii], D.w([R.pers_a43(rows[i]) for i in ii])
    def c(a, b):
        (sa, wa), (sb, wb) = a, b
        pt = float(R.wauc(sa, sb, np.ones((1, len(sa))), np.ones((1, len(sb))))[0]); rep = R.wauc(sa, sb, wa, wb)
        return [round(pt, 3), round(float(np.percentile(rep, 2.5)), 3), round(float(np.percentile(rep, 97.5)), 3)]
    o = {}
    for ex, nm in (("03", "neutral"), ("08", "smiling")):
        o[f"main B20 vs D20, {nm} only (expression-matched)"] = c(g("B20", ex), g("D20", ex))
        o[f"R3->R4 B20 {nm} vs C20 (all)"] = c(g("B20", ex), g("C20"))
        o[f"R2->R3 C20 vs D20 {nm}"] = c(g("C20"), g("D20", ex))
    out[lab] = o
    print(lab, o)
json.dump(out, open("/home/narolski/smad-next/experiments/AD1/ad1_expr_split.json", "w"), indent=1)
