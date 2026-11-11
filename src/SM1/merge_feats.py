"""SM1: merge the Athena feature shards (feats_gpu.py output, extracted from the result tar) into one file per list,
checked against the feature list order, and run the DGX equivalence check (amendment A7).

  python3 -I merge_feats.py merge DIR [--suffix _limit400]   -> OUT/feat_athena[<suffix>]/<list>.npz (id, feat)
  python3 -I merge_feats.py equiv DIR_OR_MERGED             -> RES/feat_equivalence.json
Equivalence: rows of test_eval present in both the Athena set and the DGX set (`feat/test_eval.npz`, made by
feats.py): maximum absolute feature difference, and the AUC difference of one fixed head (the FE ViT-L/14 release
header) on FRLL-Morphs OpenCV native morphs vs genuine among those rows.
"""
import csv
import glob
import json
import pathlib
import re
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402


def merge(d, suffix=""):
    d = pathlib.Path(d)
    od = K.OUT / f"feat_athena{suffix}"
    od.mkdir(parents=True, exist_ok=True)
    groups = {}
    for f in sorted(glob.glob(str(d / "*.npz"))):
        m = re.match(r"(.+)__(\d{3})(_limit\d+)?\.npz$", pathlib.Path(f).name)
        if m and (m.group(3) or "") == suffix:
            groups.setdefault(m.group(1), []).append((int(m.group(2)), f))
    out = {}
    for name, parts in groups.items():
        parts.sort()
        ids, F = [], []
        for _, f in parts:
            z = np.load(f, allow_pickle=False)
            ids += [str(i) for i in z["id"]]
            F.append(z["feat"])
        F = np.concatenate(F)
        want = [r["id"] for r in csv.DictReader(open(K.OUT / "flists" / f"{name}.csv"))]
        assert ids == want[:len(ids)], name
        np.savez(od / f"{name}.npz", id=np.array(ids), feat=F.astype(np.float32))
        out[name] = dict(n=len(ids), complete=len(ids) == len(want), shards=len(parts))
    json.dump(out, open(od / "merge_log.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


def equiv(d):
    d = pathlib.Path(d)
    a = np.load(d / "test_eval.npz", allow_pickle=False)
    b = np.load(K.OUT / "feat/test_eval.npz", allow_pickle=False)
    pos = {str(i): j for j, i in enumerate(b["id"])}
    ida = [str(i) for i in a["id"]]
    common = [i for i in ida if i in pos]
    fa = a["feat"][[ida.index(i) for i in common]]
    fb = b["feat"][[pos[i] for i in common]]
    from safetensors.numpy import load_file
    sd = load_file("/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models/"
                   "74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9.safetensors")
    W, bb = sd["head.weight"].astype(np.float64), sd["head.bias"].astype(np.float64)
    za, zb = fa @ W.T + bb, fb @ W.T + bb
    la, lb = za[:, 0] - za[:, 1], zb[:, 0] - zb[:, 1]
    meta = {r["id"]: r for r in csv.DictReader(open(K.OUT / "flists/test_eval.csv"))}
    lab = np.array([meta[i]["label"] == "1" for i in common])
    res = dict(n_common=len(common), max_abs_feature_diff=float(np.abs(fa - fb).max()),
               max_abs_logit_diff=float(np.abs(la - lb).max()), n_morph=int(lab.sum()), n_genuine=int((~lab).sum()))
    if lab.any() and (~lab).any():
        one = lambda x: float(S.wauc(x[lab], x[~lab], np.ones((1, lab.sum())), np.ones((1, (~lab).sum())))[0])  # noqa
        res.update(auc_athena=one(la), auc_dgx=one(lb), auc_diff=one(la) - one(lb))
    json.dump(res, open(K.RES / "feat_equivalence.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    if sys.argv[1] == "merge":
        merge(sys.argv[2], sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--suffix" else "")
    else:
        equiv(sys.argv[2])
