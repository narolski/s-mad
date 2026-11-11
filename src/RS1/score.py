"""AR1 detector pass: frozen features (for gate G-c) and scores, written to SEPARATE files so the gates can be computed
before any score file is opened. Scoring paths are the record's, imported unchanged from the frozen A46 runtime:
  rel  : a12_released.RELEASES spec + build_release / load_release / extract_state(strict) / adapt_input / head_logit,
         common.ImageItems at the release's res, flip TTA as a41g_score.run_rel (decision key score_noTTA, as A46 RGB-only)
         -- MADation ViT-B/16, ViT-L/14, MixFaceNet-MAD on their own RGB MTCNN crops (crop_rgb.py).
  own  : the SelfMAD release with its own preprocessing (rsx_selfmad_own._init / _prep / crop_face, dlib 81 points;
         as a41g_score.run_own), softmax[:, 1], no TTA. --lm-from: landmarks detected on the ORIGINAL image are applied
         to a blanked copy (AR4).
  nets : our A12-BR retrains (M3 / M3L, R x d0) as a41g_score.run_nets: common.build_run_model(meta.json), last.pt,
         ImageItems at meta res on the 512^2 frames (their own pipeline), flip TTA.
Features = the input of the network's last nn.Linear (forward pre-hook), no-TTA pass.

  python3 -I score.py --det NAME --mode rel|own|nets --manifest M.csv --col path --out-dir D [--run RUN] [--limit 8]
Writes D/feat_<tag>.npz (id, feat) and D/scores_<tag>.npz (id, score, score_noTTA, logit_noTTA).
"""
import argparse
import csv
import json
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402


_RO = _LMCOL = _COL = None


def _own_prep(r):
    """rsx_selfmad_own._prep (unchanged) or, for a blanked copy, the same steps with the landmarks detected on the
    original image (crop_face, cv2.resize 384, /255)."""
    import cv2
    RO = _RO
    if not _LMCOL:
        return RO._prep(r[_COL])
    src = cv2.cvtColor(cv2.imread(r[_LMCOL]), cv2.COLOR_BGR2RGB)
    img = cv2.cvtColor(cv2.imread(r[_COL]), cv2.COLOR_BGR2RGB)
    best, area = None, 0
    for f in RO._DP["det"](src, 1):
        sh = RO._DP["pred"](src, f)
        lm = np.array([(sh.part(j).x, sh.part(j).y) for j in range(sh.num_parts)], dtype=int)
        s_ = (lm[:, 0].max() - lm[:, 0].min()) * (lm[:, 1].max() - lm[:, 1].min())
        if s_ > area:
            best, area = lm, s_
    if best is not None:
        img = RO.crop_face(img, best)
    return cv2.resize(img, (384, 384)).transpose(2, 0, 1).astype("float32") / 255, best is not None


def last_linear(model):
    import torch.nn as nn
    lin = [m for m in model.modules() if isinstance(m, nn.Linear)]
    return lin[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--det", required=True)
    ap.add_argument("--mode", required=True, choices=("rel", "own", "nets"))
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--col", default="path")
    ap.add_argument("--lm-from", default=None, help="own mode: column with the original image for landmarks")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--run", default=None)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    K.add_paths(K.MC, K.W46 / "smadcvpr")
    for p in K.PINS:
        if p.parent == K.W46 / "smadcvpr":
            assert K.sha(p) == K.PINS[p], p
    import torch
    import common as C
    import a12_released as R
    R.np, R.torch, R.C = np, torch, C
    rows = [r for r in csv.DictReader(open(a.manifest)) if r[a.col]][: a.limit or None]
    for r in rows:
        assert not K.forbidden(r[a.col])
    ids = np.array([r["id"] for r in rows])
    assert len(set(ids.tolist())) == len(ids)
    od = pathlib.Path(a.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    feats = []
    t0 = time.time()
    if a.mode in ("rel", "nets"):
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        if a.mode == "rel":
            spec = R.RELEASES[a.det]
            ck = K.WEIGHTS[a.det]
            assert K.sha(ck) == K.WEIGHT_SHA[a.det], ck
            model = R.build_release(spec)
            model.load_state_dict(R.extract_state(R.load_release(ck), spec), strict=True)
            res = spec["res"]
            fwd = lambda x: R.head_logit(model(R.adapt_input(x, spec)), spec["classes"], spec["morph_index"])  # noqa
        else:
            meta = json.load(open(K.A12BR_META / a.run / "meta.json"))
            model, _ = C.build_run_model(meta)
            model.load_state_dict(torch.load(K.A12BR_RUNS / a.run / "last.pt", map_location="cpu", weights_only=True),
                                  strict=True)
            res = meta["res"]
            fwd = lambda x: C.forward_logit(model, x)[0].float().reshape(-1)  # noqa
        model.to(dev).eval()
        grab = {}
        h = last_linear(model).register_forward_pre_hook(lambda m, inp: grab.__setitem__("f", inp[0].detach()))
        dl = torch.utils.data.DataLoader(C.ImageItems([(r[a.col], 0) for r in rows], res, root="/"),
                                         batch_size=a.bs, num_workers=a.workers)
        s_tta, s_one, z_one = [], [], []
        with torch.no_grad():
            for x, _ in dl:
                x = x.to(dev, non_blocking=True)
                l0 = fwd(x)
                feats.append(grab["f"].float().reshape(len(x), -1).cpu().numpy())
                l1 = fwd(torch.flip(x, dims=[3]))
                p0, p1 = torch.sigmoid(l0), torch.sigmoid(l1)
                z_one += l0.cpu().tolist()
                s_one += p0.cpu().tolist()
                s_tta += ((p0 + p1) / 2).cpu().tolist()
        h.remove()
        sc = dict(score=np.array(s_tta, np.float32), score_noTTA=np.array(s_one, np.float32),
                  logit_noTTA=np.array(z_one, np.float32))
    else:
        import cv2
        import a41g_score as S
        import rsx_selfmad_own as RO
        ck = K.WEIGHTS[a.det]
        assert K.sha(ck) == K.WEIGHT_SHA[a.det], ck
        model = S.selfmad_net(R, str(ck), torch).eval()
        grab = {}
        h = last_linear(model).register_forward_pre_hook(lambda m, inp: grab.__setitem__("f", inp[0].detach()))
        global _RO, _LMCOL, _COL
        _RO, _LMCOL, _COL = RO, a.lm_from, a.col
        scores, logits, cropped, batch = [], [], [], []

        def flush():
            x = torch.from_numpy(np.stack(batch)).to(dev)
            with torch.no_grad():
                out = model(x).float()
            feats.append(grab["f"].float().reshape(len(x), -1).cpu().numpy())
            scores.extend(out.softmax(1)[:, 1].cpu().tolist())
            logits.extend((out[:, 1] - out[:, 0]).cpu().tolist())
            batch.clear()

        import multiprocessing as mp
        # as a41g_score.run_own: a fork Pool with rsx_selfmad_own._init; the workers never touch CUDA
        with mp.get_context("fork").Pool(a.workers, initializer=RO._init, initargs=(str(K.PREDICTOR81),)) as pool:
            model.to(dev)                                 # after the fork, as a41g_score.run_own
            for img, okc in pool.imap(_own_prep, rows, chunksize=8):
                batch.append(img)
                cropped.append(okc)
                if len(batch) == 32:
                    flush()
        if batch:
            flush()
        h.remove()
        sc = dict(score=np.array(scores, np.float32), score_noTTA=np.array(scores, np.float32),
                  logit_noTTA=np.array(logits, np.float32), cropped=np.array(cropped))
    F = np.concatenate(feats).astype(np.float32)
    assert len(F) == len(ids) and all(len(v) == len(ids) for v in sc.values())
    sfx = "" if not a.limit else f"_limit{a.limit}"
    np.savez(od / f"feat_{a.tag}{sfx}.npz", id=ids, feat=F)
    np.savez(od / f"scores_{a.tag}{sfx}.npz", id=ids, det=a.det, mode=a.mode, run=a.run or "",
             manifest_sha256=K.sha(a.manifest), script_sha256=K.sha(__file__), **sc)
    print(f"{a.tag}: {len(ids)} images, feat dim {F.shape[1]}, {time.time() - t0:.1f}s "
          f"({len(ids) / (time.time() - t0):.1f} img/s); scores written, not opened", flush=True)


if __name__ == "__main__":
    main()
