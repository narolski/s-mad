"""PN1 amendment 8: inside-against-outside sharpness ratio = var(Laplacian of luma) inside the R4 hull / outside it, on
the native image; hull = pixels not equal to the constant grey 128 of the background-blanked copy. At 224 px through the
AD4 pack loader (as the certificate cues). -> /mnt/t7/smad_next/PN1/cues/ratio_splice.npz (ids, ratio)."""
import csv
import os
import pathlib
import sys

os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np  # noqa: E402

AR1 = pathlib.Path("/mnt/t7/smad_next/AR1")
PACK_CODE = pathlib.Path("/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401/ad4/code/smadcvpr")


def main():
    import cv2
    sys.path.insert(0, str(PACK_CODE))
    import common as C
    ld = C.ImageItems([], 224, root="/")
    sp = list(csv.DictReader(open(AR1 / "manifest_splice2.csv")))
    bgp = {r["id"].replace("__bg", ""): r["path"] for r in sp if r["variant"] == "bg_R4hull"}
    jobs = []                                    # (id used in PN1 catalogues, native path, bg path)
    for r in sp:
        if r["variant"] == "native":
            jobs.append((r["id"], r["path"], bgp[r["id"]]))
    # ladder natives R2w / R2w4 (R4 hull from splice2), R4 (own hull, AR1 blank/)
    stem = lambda p: pathlib.Path(p).stem  # noqa: E731
    bm = {r["id"]: r for r in csv.DictReader(open(AR1 / "blank" / "blank_manifest.csv"))}
    for r in csv.DictReader(open(AR1 / "manifest.csv")):
        if r["pool"] != "frgcferet":
            continue
        if r["rung"] in ("R2w", "R2w4"):
            k = f"sp2_{r['rung']}_{r['tool']}_{stem(r['path'])}"
            if k in bgp:
                jobs.append(("ar1_" + r["id"], r["path"], bgp[k]))
        elif r["rung"] == "R4" and r["id"] in bm:
            jobs.append(("ar1_" + r["id"], r["path"], bm[r["id"]]["bg_path"]))
    ids, rat = [], []
    for k, (i, p, b) in enumerate(jobs):
        img = np.asarray(ld.load(p)[0]).astype(np.float32)
        bg = np.asarray(ld.load(b)[0]).astype(np.int16)
        inside = np.abs(bg - 128).max(-1) > 2
        Y = 0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]
        L = cv2.Laplacian(Y, cv2.CV_32F, ksize=1)
        ids.append(i)
        rat.append(float(L[inside].var() / (L[~inside].var() + 1e-6)) if inside.any() and (~inside).any() else np.nan)
        if (k + 1) % 1000 == 0:
            print(k + 1, len(jobs), flush=True)
    np.savez("/mnt/t7/smad_next/PN1/cues/ratio_splice.npz", ids=np.array(ids), ratio=np.array(rat))
    print("DONE", len(ids))


if __name__ == "__main__":
    main()
