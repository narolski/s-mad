"""Gates of Amendment 1 of the morph-free networks experiment (AD4). CPU only except `equiv` scoring (done before by
ad4_score.py). Code tree, data root and weights: the DGX test extraction of the AD4 pack.

  python gates.py order --arch a12_clip_vitb16_madation --seed 401 --manifest train_i3.csv [--meta META.json]
      CPU prediction of the first 200 batch compositions train.py records (generalises the reviewer's
      order_check2.py: same seeding, model build, LoRA, DataLoader base-seed draw, RandomSampler seed draw, randperm);
      with --meta: compares with that network's recorded composition.per_batch (exact equality of all 200 rows)
  python gates.py equiv --ours OUT/scores_eval.npz --ref REGISTERED/scores_eval_last.npz
      per shared cell: AUC both ways, |difference| <= 0.005, Kendall tau >= 0.99
"""
import argparse
import csv
import json
import os
import pathlib
import random
import sys

import numpy as np

W = pathlib.Path("/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401")
CODE = W / "ad4/code/smadcvpr"
sys.path.insert(0, str(CODE))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


def order(a):
    os.environ["SMAD_DATA"] = str(W / "data")
    os.environ["HF_HOME"] = str(W / "ad4/hf")
    os.environ["HF_HUB_OFFLINE"] = "1"
    import torch
    import common as C
    rows = list(csv.DictReader(open(W / "ad4/data/manifests" / a.manifest)))
    rows = [r for r in rows if r["source"] == "smdd"]          # C.train_rows d0 train90: every SMDD row, in order
    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed); torch.cuda.manual_seed_all(a.seed)
    model, _ = C.build_model(a.arch, 224, 0.0)
    C.apply_lora(model, 2, targets="qv", alpha=4.0, dropout=0.4, rs=True, train_norms=False)
    lab = np.array([int(r["label"]) for r in rows])
    bs = 256 if "vitb16" in a.arch else 32

    def draw():
        return int(torch.empty((), dtype=torch.int64).random_().item())

    draw()                                                       # _BaseDataLoaderIter base seed
    comp, n = [], len(rows)
    while len(comp) < 200:
        g = torch.Generator()
        g.manual_seed(draw())
        perm = torch.randperm(n, generator=g).numpy()
        for k in range(n // bs):
            ii = perm[k * bs:(k + 1) * bs]
            comp.append([int((lab[ii] == 0).sum()), int((lab[ii] == 1).sum()), 0])
            if len(comp) == 200:
                break
    out = {"arch": a.arch, "seed": a.seed, "manifest": a.manifest, "torch": torch.__version__,
           "first3": comp[:3], "per_batch": comp}
    if a.meta:
        rec = json.load(open(a.meta))["composition"]["per_batch"]
        eq = [list(x) == list(y) for x, y in zip(comp, rec)]
        out.update(recorded_n=len(rec), equal_rows=int(sum(eq)), gate_pass=bool(len(rec) == 200 and all(eq)),
                   recorded_first3=rec[:3])
    print(json.dumps({k: v for k, v in out.items() if k != "per_batch"}))
    if a.out:
        json.dump(out, open(a.out, "w"))


def equiv(a):
    from scipy.stats import kendalltau
    import analyze as A
    import ad4_score as S
    rows = list(csv.DictReader(open(W / "ad4/data/manifests/ad4_eval.csv")))
    o = np.load(a.ours)
    r = np.load(a.ref)
    so = dict(zip(o["id"].tolist(), o["score"].tolist()))
    sr = dict(zip(r["id"].tolist(), r["score"].tolist()))
    res, ok = {}, True
    for name, (m, b) in S.cells(rows).items():
        ids = [rows[i]["id"] for i in m + b]
        if not all(i in sr for i in ids):
            continue
        x, y = np.array([so[i] for i in ids]), np.array([sr[i] for i in ids])
        nm = len(m)
        ao, ar = A.auc(x[:nm], x[nm:]), A.auc(y[:nm], y[nm:])
        tau = float(kendalltau(x, y).statistic)
        p = abs(ao - ar) <= 0.005 and tau >= 0.99
        ok &= p
        res[name] = {"auc_ours": round(ao, 5), "auc_registered": round(ar, 5), "abs_diff": round(abs(ao - ar), 5),
                     "kendall_tau": round(tau, 5), "eer_ours": round(100 * A.eer(x[nm:], x[:nm]), 3),
                     "eer_registered": round(100 * A.eer(y[nm:], y[:nm]), 3), "pass": p}
    out = {"cells": res, "n_cells": len(res), "gate_pass": bool(ok and res)}
    print(json.dumps(out, indent=1))
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("order")
    p.add_argument("--arch", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--meta")
    p.add_argument("--out")
    q = sp.add_parser("equiv")
    q.add_argument("--ours", required=True)
    q.add_argument("--ref", required=True)
    q.add_argument("--out")
    a = ap.parse_args()
    order(a) if a.cmd == "order" else equiv(a)


if __name__ == "__main__":
    main()
