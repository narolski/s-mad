"""CB1 review F2 bridge for cell 10-SelfMAD: same score field (logit_noTTA) for both genuine pools. Aligned genuine =
the 204 frll_bona rows (eval/frllm/frll_bona/*_orig.png) of the A43 SelfMAD own-preprocessing scores
(/mnt/t7/smad_heldout/a43/a43_out/a43/selfmad_hrnet_w18/own/scores_a43.npz); raw genuine and raw morphs = A41 x7
(logit_noTTA) via RS1 analyse.selfmad_pools. FRLL five-family EER.
  python3 -I sa1_selfmad_bridge.py OUT.json"""
import csv, json, sys
import numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/RS1"); sys.path.insert(0, "/home/narolski/smad-next/src/CB1")
import analyse as A
from analyse_cnn import w_eer
P = A.selfmad_pools(A.manifest())
z = np.load("/mnt/t7/smad_heldout/a43/a43_out/a43/selfmad_hrnet_w18/own/scores_a43.npz")
man = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_heldout/a43/data/manifests/a43.csv"))}
aln = np.array([l for i, l in zip(z["id"].tolist(), z["logit_noTTA"]) if "eval/frllm/frll_bona/" in man[i]["path"] and man[i]["path"].endswith("_orig.png")], float)
out = {"n_aligned_genuine": int(len(aln))}
for name, g in (("raw genuine (A41 x7 logit)", P["G_raw"].s.astype(float)), ("aligned genuine (A43 own logit)", aln)):
    e = {}
    for f in ("amsl", "facemorpher", "opencv", "stylegan", "webmorph"):
        m = P[f"M_{f}"].s.astype(float)
        e[f] = round(100 * w_eer(np.r_[g, m], np.r_[np.zeros(len(g)), np.ones(len(m))]), 2)
    out[name] = dict(per_family=e, mean5=round(float(np.mean(list(e.values()))), 2))
json.dump(out, open(sys.argv[1], "w"), indent=1); print(json.dumps(out, indent=1))
