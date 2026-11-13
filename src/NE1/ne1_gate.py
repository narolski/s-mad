"""NE1 gate (prereg.md section 8): per network, H0 logits on the 3,417 G rows (ne1_gate.csv, tt1_score.csv fam-gate
order) against TT1-FS pn1fs <net>__gate.npz: same ids in the same order and float32 bytes identical. Also checks
logit == feat . w + b (|diff| < 1e-4) so the stored features are the head's input.
  python ne1_gate.py --feats DIR --ref DIR --nets DIR --out gate.json"""
import argparse, json, os, pathlib
import numpy as np
import torch

ap = argparse.ArgumentParser()
ap.add_argument("--feats", required=True); ap.add_argument("--ref", required=True); ap.add_argument("--nets", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
res = {}
for n in sorted(os.listdir(a.nets)):
    z = np.load(pathlib.Path(a.feats) / f"{n}__ne1_gate.npz"); r = np.load(pathlib.Path(a.ref) / f"{n}.npz")
    t = torch.load(pathlib.Path(a.nets) / n / "last_trainable.pt", map_location="cpu", weights_only=True)
    w = t["head.cls.weight"].float().numpy()[0]; b = float(t["head.cls.bias"].float().numpy()[0])
    same_ids = bool(z["id"].shape == r["id"].shape and (z["id"] == r["id"]).all())
    ident = bool(same_ids and z["logit"].astype(np.float32).tobytes() == r["logit"].astype(np.float32).tobytes())
    lin = {}
    for m in ("ne1_gate", "ne1_train", "ne1_read"):
        q = np.load(pathlib.Path(a.feats) / f"{n}__{m}.npz")
        lin[m] = float(np.abs(q["feat"].astype(np.float64) @ w + b - q["logit"]).max())
    res[n] = dict(n=int(z["id"].shape[0]), same_ids=same_ids, byte_identical=ident,
                  max_abs_diff=float(np.abs(z["logit"] - r["logit"]).max()) if same_ids else None,
                  linear_check_max=lin, linear_ok=all(v < 1e-4 for v in lin.values()))
out = dict(nets=res, passed=[n for n, v in res.items() if v["byte_identical"] and v["linear_ok"]])
json.dump(out, open(a.out, "w"), indent=1)
print(json.dumps({n: (v["byte_identical"], v["max_abs_diff"], v["linear_ok"]) for n, v in res.items()}))
