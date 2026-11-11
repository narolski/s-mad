"""FZ1: merge contiguous SMDD feature parts (fz1_feats.py --part k/n) into smdd.npz / smdd_flip.npz, checking that
the ids equal items_for('smdd') in order. Run: python -I src/FZ1/merge_parts.py clip_mad smdd 2"""
import json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fz1_common as K
import csv
bb, set_name, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
rows = [r["path"] for r in csv.DictReader(open(K.TRAIN)) if r["source"] == "smdd"]
d = K.BIG / "feats" / bb
for suf in ("", "_flip"):
    parts = [np.load(d / f"{set_name}{suf}_part{k}of{n}.npz", allow_pickle=False) for k in range(1, n + 1)]
    ids = np.concatenate([p["id"] for p in parts])
    assert ids.tolist() == rows, "id order mismatch"
    feat = np.concatenate([p["feat"] for p in parts])
    metas = [json.loads(str(p["meta"])) for p in parts]
    meta = dict(metas[0], n=len(ids), seconds=max(m["seconds"] for m in metas), parts=n)
    assert all(m["tf32"] == meta["tf32"] for m in metas)
    out = d / f"{set_name}{suf}.npz"
    assert not out.exists()
    np.savez(out, id=ids, feat=feat, meta=json.dumps(meta))
    print("wrote", out, feat.shape)
