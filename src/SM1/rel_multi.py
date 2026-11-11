"""SM1: several released detectors on one image list in one pass (each image decoded once; CPU-starved DGX).

Same path as rel_score.py (copied from src/AR1/score.py rel mode): a12_released spec + build_release / load_release /
extract_state(strict) / adapt_input / head_logit, common.ImageItems at 224 (PIL bilinear), no TTA; every release here
has res 224. Input = whole images (A6: the A39 path, SMDD 256-px files resized to 224 by the loader) or own MTCNN crops.

  python3 -I rel_multi.py --manifest M.csv --out-dir D [--dets a,b,...] [--root R] [--limit 8] [--bs 64] [--workers 0]
-> D/scores_rel_<det>.npz (id, logit_noTTA, score_noTTA) per detector
"""
import argparse
import csv
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import rel_score as RS  # noqa: E402
import sm1_common as K  # noqa: E402

DEFAULT = ("madation_vitb16", "madation_vitl14", "madation_fe_vitb16", "madation_fe_vitl14", "mixfacenet_mad_smdd",
           "madation_fs_vitb16", "madation_fs_vitl14")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--dets", default=",".join(DEFAULT))
    ap.add_argument("--root", default="/")
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    for p, s in RS.A12_PINS.items():
        assert K.sha(p) == s, p
    for p in (K.MC, K.W46 / "smadcvpr"):
        sys.path.insert(0, str(p))
    import torch
    import common as C
    import a12_released as R
    R.np, R.torch, R.C = np, torch, C
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    rows = list(csv.DictReader(open(a.manifest)))[: a.limit or None]
    for r in rows:
        assert not K.forbidden(r["path"])
    ids = np.array([r["id"] for r in rows])
    assert len(set(ids.tolist())) == len(ids)
    od = pathlib.Path(a.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    dets = [d for d in a.dets.split(",") if not (od / f"scores_rel_{d}{'_limit%d' % a.limit if a.limit else ''}.npz").exists()]
    models = {}
    for d in dets:
        spec = R.RELEASES[d]
        assert spec["res"] == 224
        ck = RS.WEIGHTS[d]
        assert K.sha(ck) == RS.WEIGHT_SHA[d], ck
        m = R.build_release(spec)
        m.load_state_dict(R.extract_state(R.load_release(ck), spec), strict=True)
        models[d] = (m.to("cuda").eval(), spec)
    dl = torch.utils.data.DataLoader(C.ImageItems([(r["path"], 0) for r in rows], 224, root=a.root),
                                     batch_size=a.bs, num_workers=a.workers)
    z = {d: [] for d in dets}
    t0, n = time.time(), 0
    with torch.no_grad():
        for x, _ in dl:
            x = x.to("cuda", non_blocking=True)
            for d, (m, spec) in models.items():
                z[d] += R.head_logit(m(R.adapt_input(x, spec)), spec["classes"], spec["morph_index"]).float().cpu().tolist()
            n += len(x)
            if (n // a.bs) % 25 == 0:
                print(f"PROGRESS {n}/{len(rows)} {time.time() - t0:.0f}s", flush=True)
    sfx = "" if not a.limit else f"_limit{a.limit}"
    for d in dets:
        zz = np.array(z[d], np.float32)
        np.savez(od / f"scores_rel_{d}{sfx}.npz", id=ids, det=d, logit_noTTA=zz, score_noTTA=1 / (1 + np.exp(-zz)),
                 manifest_sha256=K.sha(a.manifest), script_sha256=K.sha(__file__), weight_sha256=RS.WEIGHT_SHA[d],
                 root=a.root)
    mem = torch.cuda.max_memory_allocated() / 2 ** 30
    print(f"{len(ids)} images x {len(dets)} detectors, {time.time() - t0:.0f}s, max GPU mem {mem:.1f} GB; "
          f"scores written, not opened", flush=True)


if __name__ == "__main__":
    main()
