"""PN1 amendment 10: rescore a finished network from its result tar (meta.json + last_trainable.pt, i.e. LoRA and head)
on extra rows of the evaluation manifest. Model = common.build_run_model(meta) (base CLIP weights from HF_HOME/a12, as
train.py builds it) + the trained tensors (strict for every trained tensor). Logit without flip, as pn1_score.py.
  python rescore.py --resdir RESULT_DIR --code CODE --manifest NAME --fam splice --out OUT.npz"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resdir", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--manifest", default="pn1_eval.csv")
    ap.add_argument("--fam", default="splice")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=7)
    a = ap.parse_args()
    sys.path.insert(0, str(pathlib.Path(a.code) / "smadcvpr"))
    import torch
    from torch.utils.data import DataLoader
    import common as C
    d = pathlib.Path(a.resdir)
    meta = json.load(open(d / "meta.json"))
    model, _ = C.build_run_model(meta)
    tr = torch.load(d / "last_trainable.pt", map_location="cpu", weights_only=True)
    names = {n for n, p in model.named_parameters() if p.requires_grad}
    assert set(tr) == names, (len(tr), len(names))
    missing, unexpected = model.load_state_dict(tr, strict=False)
    assert not unexpected
    model.to("cuda").eval()
    rows = [r for r in C.read_manifest(a.manifest) if r["fam"] == a.fam]
    dl = DataLoader(C.ImageItems([(r["path"], int(r["label"])) for r in rows], meta["res"]), batch_size=64, num_workers=a.workers)
    lg = []
    with torch.no_grad():
        for x, _ in dl:
            lg += C.forward_logit(model, x.to("cuda"))[0].float().cpu().tolist()
    np.savez(a.out, id=np.array([r["id"] for r in rows]), logit=np.array(lg, np.float32), seed=meta["seed"])
    print("RESCORE_DONE", len(rows))


if __name__ == "__main__":
    main()
