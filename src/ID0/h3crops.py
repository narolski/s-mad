"""ID0: glintr100 embeddings of the existing H3 CASIA contributor crops (h3_sg3/work/h3_inputs.npz, 112x112, already
aligned crops) via a2f_common.embed_crops('glint') (pinned, through AR1's fr._mods()). Nothing is written as an image.
  python3 -I h3crops.py [--limit 8]
"""
import argparse
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import id0_common as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    sys.path.insert(0, str(C.AR1_SRC))
    import fr
    _, A2F = fr._mods()
    z = np.load(C.H3_INPUTS)
    folder, crops = z["folder"], z["crop"]
    if a.limit:
        folder, crops = folder[: a.limit], crops[: a.limit]
    # h3_prepare.py stores the crops as RGB; h3_finalise.py flips them to BGR before use; the glint route takes BGR
    emb = np.asarray(A2F.embed_crops("glint", [c[:, :, ::-1].copy() for c in crops]), np.float32)
    out = C.OUT / "feat" / ("h3crops_glint_test.npz" if a.limit else "h3crops_glint.npz")
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, folder=folder, emb=emb)
    t = z["tmpl"][: len(emb)]
    t = t / np.linalg.norm(t, axis=1, keepdims=True)
    print(out, emb.shape, "cos(glint, stored a2f template) is not comparable (different models); norms",
          np.linalg.norm(emb, axis=1)[:4])


if __name__ == "__main__":
    main()
