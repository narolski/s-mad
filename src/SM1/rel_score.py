"""SM1 Part 2 scorer: the released SMDD-trained detectors through the AR1 / A46 release path, unchanged.

Copied from src/AR1/score.py (--mode rel), with the FE and FS weight paths added (staged payload, sha256 from the
A12REL convert.json files). Path: a12_released.RELEASES spec + build_release / load_release / extract_state(strict)
/ adapt_input / head_logit, common.ImageItems at the release's res (PIL bilinear), as a41g_score.run_rel. Input =
the own MTCNN crops written by src/AR1/crop_rgb.py (run unchanged) or, for the reproduction check, whole eval.csv
frames (--root smadcvpr_data). Writes scores only (logit_noTTA = morph logit, score_noTTA = sigmoid; flip TTA as
AR1); nothing is read back here.

  python3 -I rel_score.py --det NAME --manifest M.csv --out-dir D --tag T [--root R] [--limit 8]
"""
import argparse
import csv
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import sm1_common as K  # noqa: E402

PAY = pathlib.Path("/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models")
WEIGHT_SHA = {
    "madation_vitb16": "ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f",
    "madation_vitl14": "bb452ded624ffce2dc85168f8dde9293fc3709ec8cce755d8ecf1d5f5370e980",
    "madation_fe_vitb16": "6a4d93ba80f3c48ecb0a9d8a6ae07e0c64e8c4f49f2cc62b2588dafbffb84d92",
    "madation_fe_vitl14": "74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9",
    "madation_fs_vitb16": "a7cacd4773ed3ef959e78202c7f0e0426e5fff04367418130da78e9e85e64885",
    "madation_fs_vitl14": "6071ec7b7dcb0b3f28f4c8b71c79692a322404c33893a62f5a89964fb79a9421",
    "mixfacenet_mad_smdd": "3d507c8bbd5dbd06bd735ae809fa0095e589c17c0c94cd2ed530cf34a014ab1c",
}
WEIGHTS = {k: (PAY / f"{v}.safetensors" if k != "mixfacenet_mad_smdd"
               else pathlib.Path("/mnt/t7/mixfacenet_mad_official/mixfacenet_SMDD.pth")) for k, v in WEIGHT_SHA.items()}
A12_PINS = {K.W46 / "smadcvpr/a12_released.py": "839f0cd4498577cad5410a63e1da63feeff53e05a3bed2c511ff67cac01e41da",
            K.W46 / "smadcvpr/a41g_score.py": "f53612cb146e72ca5598d9b01962dcf3fb2f9d4aa8c9d616d80bd99e273c6113"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--det", required=True, choices=sorted(WEIGHTS))
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--col", default="path")
    ap.add_argument("--root", default="/")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-tta", action="store_true", help="skip the flip pass (decision key logit_noTTA unchanged)")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    for p, s in A12_PINS.items():
        assert K.sha(p) == s, p
    for p in (K.MC, K.W46 / "smadcvpr"):
        sys.path.insert(0, str(p))
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
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    spec = R.RELEASES[a.det]
    ck = WEIGHTS[a.det]
    assert K.sha(ck) == WEIGHT_SHA[a.det], ck
    model = R.build_release(spec)
    model.load_state_dict(R.extract_state(R.load_release(ck), spec), strict=True)
    model.to(dev).eval()
    fwd = lambda x: R.head_logit(model(R.adapt_input(x, spec)), spec["classes"], spec["morph_index"])  # noqa: E731
    dl = torch.utils.data.DataLoader(C.ImageItems([(r[a.col], 0) for r in rows], spec["res"], root=a.root),
                                     batch_size=a.bs, num_workers=a.workers)
    t0 = time.time()
    s_tta, s_one, z_one = [], [], []
    with torch.no_grad():
        for x, _ in dl:
            x = x.to(dev, non_blocking=True)
            l0 = fwd(x)
            l1 = l0 if a.no_tta else fwd(torch.flip(x, dims=[3]))
            p0, p1 = torch.sigmoid(l0), torch.sigmoid(l1)
            z_one += l0.cpu().tolist()
            s_one += p0.cpu().tolist()
            s_tta += ((p0 + p1) / 2).cpu().tolist()
    sfx = "" if not a.limit else f"_limit{a.limit}"
    np.savez(od / f"scores_{a.tag}{sfx}.npz", id=ids, det=a.det, score=np.array(s_tta, np.float32),
             score_noTTA=np.array(s_one, np.float32), logit_noTTA=np.array(z_one, np.float32),
             manifest_sha256=K.sha(a.manifest), script_sha256=K.sha(__file__), weight_sha256=WEIGHT_SHA[a.det])
    dt = time.time() - t0
    mem = torch.cuda.max_memory_allocated() / 2 ** 30 if dev == "cuda" else 0
    print(f"{a.tag}: {len(ids)} images, {dt:.1f}s ({len(ids) / dt:.1f} img/s), max GPU mem {mem:.1f} GB; "
          f"scores written, not opened", flush=True)


if __name__ == "__main__":
    main()
