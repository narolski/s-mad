"""Fixed-threshold re-read (EV1), Amendment 2 B4: zero-border fraction of the aligned genuine frames of the E5 variant
pools and the 12 E7 (resmatch) pools, plus FRLL orig, the DiM copy and the MorDIFF alignment for reference. Same
definition as c_checks.stats_job (zero_frac = 1 - share of pixels with R+G+B > 0), computed directly and checked
equal to stats_job on the first 20 frames. Frames are decoded and
read only; nothing is written except the result file. Single process (the machine is shared).
Run: nice -n 10 python3 -I src/EV1/ev1_border.py [--smoke]
"""
import sys, time, pathlib
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "C_cue_checks"))
import ev1_common as K  # noqa: E402
import c_checks as CC  # noqa: E402

SMOKE = "--smoke" in sys.argv


def main():
    T0 = time.time()
    rows = [r for r in K.eval_rows() if r["set"] != "mad22" and r["variant"] != "chip"]
    I = K.Index(rows)
    ix = []
    for v in K.GVARS:
        ix += list(I.bona("frll_bona", v))
    ix += list(I.bona("dim_bona")) + list(I.bona("mordiff_bona"))
    for f in K.FAMS:
        ix += list(I.resmatch(f))
    if SMOKE:
        ix = ix[:8]
    ids, paths, zero = [], [], []
    for n, i in enumerate(ix):
        p = K.MC / "smadcvpr_data" / rows[i]["path"]
        assert not K.forbidden(p)
        with Image.open(p) as im:
            a = np.asarray(im.convert("RGB"))
        z = float(1 - (a.astype(np.uint16).sum(2) > 0).mean())          # same definition as c_checks.stats_job
        if n < 20:                                                        # equivalence check on the first 20 frames
            o = CC.stats_job((str(p), "al"))
            assert abs(o["zero_frac"] - z) < 1e-12, (p, o["zero_frac"], z)
        ids.append(rows[i]["id"]); paths.append(str(p)); zero.append(z)
        if n % 500 == 0:
            print(f"[{time.time() - T0:6.1f}s] {n}/{len(ix)}", flush=True)
    out = K.BIG / ("border_e5e7_smoke.npz" if SMOKE else "border_e5e7.npz")
    np.savez_compressed(out, id=np.array(ids), path=np.array(paths), zero_frac=np.array(zero))
    print("written", out, len(ids), f"{time.time() - T0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
