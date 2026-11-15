"""XF1 gate (prereg.md section 4): one network's logits on the 3,417 registered gate rows (fam gate of xf1_eval.csv, NE1
ne1_gate.csv order, scored by the unchanged rescore.py) against its TT1-FS pn1fs reference: same ids in the same order
and float32 bytes identical. Exit 0 if byte-identical, 3 otherwise (the job then scores nothing of that network).
  python xf1_gate.py --scores NET__gate.npz --ref REF.npz --out NET__gate.json"""
import argparse, json, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--scores", required=True); ap.add_argument("--ref", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
z, r = np.load(a.scores), np.load(a.ref)
same = bool(z["id"].shape == r["id"].shape and (z["id"] == r["id"]).all())
ident = bool(same and z["logit"].astype(np.float32).tobytes() == r["logit"].astype(np.float32).tobytes())
res = dict(n=int(z["id"].shape[0]), same_ids=same, byte_identical=ident,
           max_abs_diff=float(np.abs(z["logit"].astype(np.float64) - r["logit"].astype(np.float64)).max()) if same else None)
json.dump(res, open(a.out, "w"), indent=1)
print("GATE", a.scores, json.dumps(res))
sys.exit(0 if ident else 3)
