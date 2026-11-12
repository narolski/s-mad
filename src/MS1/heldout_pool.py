"""MS1 held-out sharp evaluation sources (prereg part 2, P1-S and the KDEF secondary): never used in training.

cfd  : every neutral image (*-N.jpg) of the Chicago Face Database 3.0.1 (CFD, CFD-INDIA, CFD-MR), one per person.
kdef : KDEF neutral straight images (??##NES.JPG), sessions A and B (70 persons x 2), if present.
Each through the unchanged aligner scripts/73_delin_align.align (the call of src/AR1/frll_prep.py) -> 512 frame + .tem.
  python3 -I heldout_pool.py cfd|kdef [--limit 8]
-> OUT/<src>/frames/*.png, OUT/<src>/pool.csv (id, person, raw, raw_sha256, aligned, frame, frame_sha256),
   experiments/MS1.../<src>_pool_summary.json
"""
import argparse
import collections
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ms1common as C  # noqa: E402

CFD = pathlib.Path("/mnt/t7/Datasety/downloads/ChicagoFaceDatabase/cfd/CFD Version 3.0.1/Images")
KDEF = pathlib.Path("/mnt/t7/Datasety/downloads/KDEF_and_AKDEF/KDEF_and_AKDEF/KDEF")


def items(src):
    if src == "cfd":
        out = []
        for p in sorted(CFD.rglob("*-N.jpg")):
            parts = p.stem.split("-")              # CFD-AF-200-228-N -> person CFD-AF-200
            out.append((f"cfd:{'-'.join(parts[:3])}", p))
        return out
    out = []
    for p in sorted(KDEF.glob("*/*NES.JPG")):
        out.append((f"kdef:{p.stem[1:4]}", p))      # AF01NES (session A) / BF01NES (session B): person F01
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", choices=("cfd", "kdef"))
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    import cv2
    da = C.load(C.MC / "scripts/73_delin_align.py", "delin_align")
    it = items(a.src)[: a.limit or None]
    O = C.OUT / a.src
    fr = O / ("frames" if not a.limit else "frames_smoke")
    fr.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    for k, (person, p) in enumerate(it):
        iid = f"{a.src}_{k:04d}"
        dst = fr / f"{iid}.png"
        r = da.align(cv2.imread(str(p)))
        row = dict(id=iid, person=person, raw=str(p), raw_sha256=C.sha(p), aligned=0, frame="", frame_sha256="")
        if r is not None:
            al, lm = r
            assert cv2.imwrite(str(dst), al)
            da.write_tem(str(dst)[:-4] + ".tem", lm)
            row.update(aligned=1, frame=str(dst), frame_sha256=C.sha(dst))
        rows.append(row)
    tag = "" if not a.limit else "_smoke"
    C.write_csv(O / f"pool{tag}.csv", rows)
    ok = [r for r in rows if r["aligned"]]
    summ = dict(source=a.src, images=len(rows), aligned=len(ok), failed=[r["raw"] for r in rows if not r["aligned"]],
                persons_aligned=len({r["person"] for r in ok}), persons_total=len({r["person"] for r in rows}),
                by_subset=dict(collections.Counter(pathlib.Path(r["raw"]).relative_to(CFD).parts[0] for r in ok))
                if a.src == "cfd" else None,
                pool_csv_sha256=C.sha(O / f"pool{tag}.csv"), aligner_sha256=C.sha(C.MC / "scripts/73_delin_align.py"),
                seconds=round(time.time() - t0))
    if not a.limit:
        json.dump(summ, open(C.RES / f"{a.src}_pool_summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "failed"}), "failed", len(summ["failed"]))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
