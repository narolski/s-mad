"""AB1 note 2 (post hoc, zero GPU): share of the net storage flag increase from the sharpest quartile of native FFHQ
hold-out photos (lapvar_face, C2P H-new-2 edge), for A, AS and SbS at seeds 408-412, both sizes.
  python3 -I ab1_sharp.py OUT.json"""
import csv
import importlib.util
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("c2p_read", HERE.parent / "PN1" / "c2p_read.py")
C2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C2)
M = list(csv.DictReader(open("/mnt/t7/smad_next/AB1/manifests/ab1_eval.csv")))
natp, natm, pairs, mpairs = C2.holdout(M)
cz = np.load(C2.CUES)
names = list(cz["names"])
lap = dict(zip([str(i) for i in cz["ids"]], cz["cues"][:, names.index("lapvar_face")]))
edge = np.quantile([lap[i] for i in natp], 0.75)
top = {i for i in natp if lap[i] >= edge}
out = {"edge": float(edge), "n_top": len(top), "arms": {}}
for arm in ("A", "AS", "SbS"):
    res = {}
    for z in C2.SIZES:
        per = {}
        for s in (408, 409, 410, 411, 412):
            T = f"AB1_{arm}_s{s}"
            with tarfile.open(f"/mnt/t7/smad_next/AB1/results/{T}.tar") as t:
                zz = np.load(io.BytesIO(t.extractfile(f"{T}/scores_eval.npz").read()))
            L = dict(zip([str(i) for i in zz["id"]], zz["logit"].astype(float)))
            ids = pairs[z]
            up = sum(1 for i in ids if L[i] <= 0 < L[f"{i}_{z}"])
            dn = sum(1 for i in ids if L[i] > 0 >= L[f"{i}_{z}"])
            ut = sum(1 for i in ids if i in top and L[i] <= 0 < L[f"{i}_{z}"])
            dt = sum(1 for i in ids if i in top and L[i] > 0 >= L[f"{i}_{z}"])
            net = up - dn
            per[s] = dict(net=net, up=up, down=dn, top_share=(ut - dt) / net if net > 0 else None)
        res[z] = per
    en = all(sum(1 for v in res[z].values() if v["top_share"] is not None and v["top_share"] >= 0.50) >= 4 for z in C2.SIZES)
    ne = all(sum(1 for v in res[z].values() if v["top_share"] is not None and v["top_share"] <= 0.35) >= 4 for z in C2.SIZES)
    res["verdict"] = "enriched" if en else ("not enriched" if ne else "inconclusive")
    out["arms"][arm] = res
json.dump(out, open(sys.argv[1], "w"), indent=1)
for arm, r in out["arms"].items():
    print(arm, r["verdict"], {z: {s: (v["net"], None if v["top_share"] is None else round(v["top_share"], 2)) for s, v in r[z].items()} for z in C2.SIZES})
