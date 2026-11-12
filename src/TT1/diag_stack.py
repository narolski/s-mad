"""Threshold transfer on unseen genuine sources (TT1): ZERO-GPU-BUDGET DIAGNOSTIC (not a registered read; lead's request
13 Nov). Which stage differs between two software stacks on FFHQ genuine rows: image decode, resize, or the network?
For a fixed list of FFHQ genuine ids (gate rows, stored scores already known): saves per image
  dec   the decoded RGB array (PIL Image.open(...).convert("RGB")), uint8, and its sha256;
  rsz   the resized RGB array (PIL resize to the network res, BILINEAR, as common.ImageItems.load), uint8, sha256;
  x     the tensor common.ImageItems returns (float32), sha256 of its bytes;
  logit the network's logit for A_s401 (rescore.py's model build: build_run_model + last_trainable.pt; eval mode;
        batch of these 5 images only).
Versions are saved too. Compare two outputs with --compare A.npz B.npz.
  python diag_stack.py --data DATA_ROOT --code CODE --net NETDIR --ids id1,id2,... --out OUT.npz
  python diag_stack.py --compare A.npz B.npz"""
import argparse
import hashlib
import json
import pathlib
import sys

import numpy as np


def h(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def run(a):
    sys.path.insert(0, str(pathlib.Path(a.code) / "smadcvpr"))
    import PIL
    import torch
    from PIL import Image
    import common as C
    meta = json.load(open(pathlib.Path(a.net) / "meta.json"))
    ids = a.ids.split(",")
    rows = {r["id"]: r for r in C.read_manifest(a.manifest)}
    paths = [rows[i]["path"] for i in ids]
    dec, rsz = [], []
    for p in paths:
        im = Image.open(pathlib.Path(a.data) / p).convert("RGB")
        dec.append(np.asarray(im))
        rsz.append(np.asarray(im.resize((meta["res"], meta["res"]), Image.BILINEAR)))
    ds = C.ImageItems([(p, 0) for p in paths], meta["res"])
    x = torch.stack([ds[i][0] for i in range(len(paths))])
    model, _ = C.build_run_model(meta)
    tr = torch.load(pathlib.Path(a.net) / "last_trainable.pt", map_location="cpu", weights_only=True)
    model.load_state_dict(tr, strict=False)
    model.to("cuda").eval()
    with torch.no_grad():
        lg = C.forward_logit(model, x.to("cuda"))[0].float().cpu().numpy()
    np.savez(a.out, ids=np.array(ids), dec=np.stack(dec), rsz=np.stack(rsz), x=x.numpy(), logit=lg,
             versions=np.array([sys.version.split()[0], torch.__version__, PIL.__version__, np.__version__,
                                torch.cuda.get_device_name(0)]))
    print(json.dumps(dict(ids=ids, dec=[h(d) for d in dec], rsz=[h(r) for r in rsz], x=h(x.numpy()),
                          logit=lg.tolist()), indent=1))


def compare(fa, fb):
    A, B = np.load(fa), np.load(fb)
    assert (A["ids"] == B["ids"]).all()
    out = dict(versions_a=A["versions"].tolist(), versions_b=B["versions"].tolist(), per_image=[])
    for k, i in enumerate(A["ids"].tolist()):
        dd = np.abs(A["dec"][k].astype(int) - B["dec"][k].astype(int))
        dr = np.abs(A["rsz"][k].astype(int) - B["rsz"][k].astype(int))
        dx = np.abs(A["x"][k] - B["x"][k])
        out["per_image"].append(dict(id=i, decode_identical=bool(dd.max() == 0), decode_max=int(dd.max()),
                                     resize_identical=bool(dr.max() == 0), resize_max=int(dr.max()),
                                     resize_share_px_differ=float((dr > 0).mean()),
                                     tensor_max_abs=float(dx.max()),
                                     logit_a=float(A["logit"][k]), logit_b=float(B["logit"][k]),
                                     logit_diff=float(A["logit"][k] - B["logit"][k])))
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data")
    ap.add_argument("--code")
    ap.add_argument("--net")
    ap.add_argument("--ids")
    ap.add_argument("--manifest", default="tt1_score.csv")
    ap.add_argument("--out")
    ap.add_argument("--compare", nargs=2)
    a = ap.parse_args()
    if a.compare:
        compare(*a.compare)
    else:
        run(a)
