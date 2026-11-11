"""PN1 amendment 11 post hoc: seam tone of the spliced natives (OpenCV-style): mean luma and mean (R-G) of a 3-px ring
inside the R4 hull minus the same of a 3-px ring outside it (hull = non-grey pixels of the background-blanked copy;
cv2.erode / cv2.dilate on the mask: measurement only, no image written). -> cues/tone_splice.npz (ids, tone (N, 2))."""
import csv
import numpy as np


def main():
    import cv2
    sp = list(csv.DictReader(open("/mnt/t7/smad_next/AR1/manifest_splice2.csv")))
    bgp = {r["id"].replace("__bg", ""): r["path"] for r in sp if r["variant"] == "bg_R4hull"}
    k = np.ones((7, 7), np.uint8)
    ids, out = [], []
    for r in sp:
        if r["variant"] != "native" or r["tool"] != "opencv" or r["rung"] not in ("S0", "S3", "S4"):
            continue
        img = cv2.imread(r["path"]).astype(np.float32)
        bg = cv2.imread(bgp[r["id"]]).astype(np.int16)
        m = (np.abs(bg - 128).max(-1) > 2).astype(np.uint8)
        inner = m & (1 - cv2.erode(m, k))
        outer = cv2.dilate(m, k) & (1 - m)
        Y = 0.114 * img[..., 0] + 0.587 * img[..., 1] + 0.299 * img[..., 2]
        RG = img[..., 2] - img[..., 1]
        ids.append(r["id"])
        out.append([Y[inner == 1].mean() - Y[outer == 1].mean(), RG[inner == 1].mean() - RG[outer == 1].mean()])
    np.savez("/mnt/t7/smad_next/PN1/cues/tone_splice.npz", ids=np.array(ids), tone=np.array(out))
    print("DONE", len(ids))


if __name__ == "__main__":
    main()
