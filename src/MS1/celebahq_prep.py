"""MS1 candidate fourth source (author 13 Nov 09:10: "Use CeleA-HQ as a source, it is valid"): CelebA-HQ preparation only
(no training without a registered amendment and a pre-run check).

align : stream every PNG from the zip (no unpacked copy of the 37 GB archive; the zip's sha256 is checked first), the
        unchanged aligner scripts/73_delin_align.align (the call of src/AR1/frll_prep.py) -> 512 frame + 106-point .tem
        under OUT/celebahq/frames/; glintr100 embedding of the frame (src/AR1/fr.py, unchanged);
        OUT/celebahq/align_log.csv (index, outcome, frame sha256), OUT/celebahq/emb.npz.
  python3 -I celebahq_prep.py align [--limit 8] [--start 0 --stop 30000]
"""
import argparse
import csv
import json
import pathlib
import sys
import time
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ms1common as C  # noqa: E402

ZIP = pathlib.Path("/mnt/t7/Datasety/downloads/CelebA-HQ/CelebA-HQ-1024.zip")
ZIP_SHA = "bda2d6f0df08f6362057224e1007d3eacfd603f5f5cb67475451c7284e11eb2d"
O = C.OUT / "celebahq"


def align(a):
    import cv2
    if not a.limit and not (O / "zip_sha_ok").exists():
        assert C.sha(ZIP) == ZIP_SHA, "zip sha256 differs"
        (O / "zip_sha_ok").parent.mkdir(parents=True, exist_ok=True)
        (O / "zip_sha_ok").write_text(ZIP_SHA + "\n")
    da = C.load(C.MC / "scripts/73_delin_align.py", "delin_align")
    C.add_paths(C.SRC / "AR1")
    import fr as FR
    z = zipfile.ZipFile(ZIP)
    names = sorted(n for n in z.namelist() if n.endswith(".png"))
    names = names[a.start:a.stop][: a.limit or None]
    fr_dir = O / ("frames" if not a.limit else "frames_smoke")
    fr_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{a.start}_{a.stop}" if not a.limit else "smoke"
    rows, embs, keys = [], [], []
    t0 = time.time()
    for k, n in enumerate(names):
        idx = pathlib.Path(n).stem
        img = cv2.imdecode(np.frombuffer(z.read(n), np.uint8), cv2.IMREAD_COLOR)
        r = da.align(img)
        if r is None:
            rows.append(dict(index=idx, outcome="no_face_or_frontal_filter", frame_sha256=""))
            continue
        al, lm = r
        dst = fr_dir / f"{idx}.png"
        assert cv2.imwrite(str(dst), al)
        da.write_tem(str(dst)[:-4] + ".tem", lm)
        e, f = FR.embed_images([al])
        rows.append(dict(index=idx, outcome="aligned" if f[0] else "aligned_no_fr_face", frame_sha256=C.sha(dst)))
        if f[0]:
            embs.append(e[0])
            keys.append(idx)
        if (k + 1) % 500 == 0:
            print(f"{k + 1}/{len(names)} {time.time() - t0:.0f}s", flush=True)
    C.write_csv(O / f"align_log_{tag}.csv", rows)
    np.savez(O / f"emb_{tag}.npz", key=np.array(keys), emb=np.array(embs, np.float32).reshape(-1, 512))
    from collections import Counter
    print(json.dumps(dict(n=len(rows), outcomes=dict(Counter(r["outcome"] for r in rows)), seconds=round(time.time() - t0),
                          aligner_sha256=C.sha(C.MC / "scripts/73_delin_align.py"))), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("align",))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--stop", type=int, default=30000)
    a = ap.parse_args()
    align(a)
