import sys, csv, numpy as np, pathlib, collections, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
R = rows_eval(); ids = [r["id"] for r in R]
a43 = list(csv.DictReader(open(A43/"data/manifests/a43.csv"))); a43ids = [r["id"] for r in a43]
Eix = [i for i, r in enumerate(a43) if r["source"]=="a43" and r["arm"]=="E"]
G = {"FRLL orig": sel(R,"frllm","frll_bona","orig","0"), "MorDIFF align": sel(R,"mordiff","mordiff_bona","orig","0")}
for v in ("jpeg90","jpeg70","jpeg50","blur1","resample50"): G[v] = sel(R,"frllm","frll_bona",v,"0")
for f in FAMS: G["E7 "+f] = sel(R, SETOF[f], f, "resmatch", "0")
G["devbona"] = sel(R, "devbona","devbona","orig","0")
M = {f: sel(R, SETOF[f], f, "orig", "1") for f in FAMS}
print("Share with P(morph) > 0.5 (each release's own argmax / 0.5 rule; no threshold pool). %")
hdr = ["stored-small"] + list(G) 
for nm, d in (("ViT-L/14","madation_vitl14"),("ViT-B/16","madation_vitb16"),("FE ViT-L/14","madation_fe_vitl14"),("FE ViT-B/16","madation_fe_vitb16"),("SelfMAD ours","selfmad_hrnet_w18"),("SelfMAD own",None)):
    if d:
        s = rel(d, ids); sE = load(A43/f"a43_out/a43/{d}/rel/scores_a43.npz", a43ids, "logit_noTTA")[Eix]; c = 0.0
    else:
        s = load(OWN, ids, "score"); sE = load(A43/"a43_out/a43/selfmad_hrnet_w18/own/scores_a43.npz", a43ids, "score")[Eix]; c = 0.5
    print(f"\n{nm}")
    print("  genuine: stored-small %5.1f | " % (100*(sE>c).mean()) + " | ".join(f"{k} {100*(s[v]>c).mean():.1f}" for k, v in G.items() if np.isfinite(s[v]).all()))
    print("  morphs detected (P>0.5): " + " | ".join(f"{f} {100*(s[v]>c).mean():.1f}" for f, v in M.items()) + f" | family mean miss {100-np.mean([100*(s[v]>c).mean() for v in M.values()]):.1f}")
