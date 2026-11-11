"""AR1 FRLL secondary pool: the 204 FRLL front photos (102 persons, neutral _03 + smiling _08) aligned with the
UNCHANGED existing aligner scripts/73_delin_align.align (the aligner behind every train.csv / R6 / R8 frame: insightface
detection + 106 landmarks, frontal filter, 2-point eye similarity to the 512^2 frame) -> PNG + .tem; then the pool:
H = p_03, S = p_08 (twin = tool(neutral, smiling) of one person), B = q_08 by a Hungarian assignment on glintr100
cos(H_p, S_q) without fixed points; plus the bridge pair lists: every published FRLL-Morphs opencv / facemorpher pair
(a, b) -> tool(a_03, b_03) (published pairs assumed neutral-neutral, as the AMSL file names state).

  python3 -I frll_prep.py [--limit 8]
"""
import argparse
import csv
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402

RAW = pathlib.Path("/mnt/t7/Datasety/downloads/frll_base/extracted")
PUB = pathlib.Path("/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    import cv2
    K.add_paths(K.MC / "scripts")
    da = K.load_module(K.MC / "scripts/73_delin_align.py", "delin_align", pin=None)
    out = K.OUT / ("frll_src" if not a.limit else "frll_src_smoke")
    out.mkdir(parents=True, exist_ok=True)
    photos = sorted(RAW.glob("neutral_front/*_03.jpg")) + sorted(RAW.glob("smiling_front/*_08.jpg"))
    photos = photos[: a.limit or None]
    t0 = time.time()
    ok, fail = [], []
    for p in photos:
        dst = out / (p.stem + ".png")
        if not dst.exists():
            r = da.align(cv2.imread(str(p)))
            if r is None:
                fail.append(p.name)
                continue
            al, lm = r
            cv2.imwrite(str(dst), al)
            da.write_tem(str(dst)[:-4] + ".tem", lm)
        ok.append(dst)
    dt = time.time() - t0
    log = dict(aligner=str(K.MC / "scripts/73_delin_align.py"), aligner_sha256=K.sha(K.MC / "scripts/73_delin_align.py"),
               attempted=len(photos), aligned=len(ok), failed=fail, seconds=round(dt, 1))
    print(json.dumps(log), flush=True)
    if a.limit:
        return
    import fr
    emb, found = fr.embed_paths([str(p) for p in ok])
    E = {p.stem: (e, f) for p, e, f in zip(ok, emb, found)}
    np.savez(K.OUT / "frll_src_emb.npz", stem=np.array([p.stem for p in ok]), emb=emb, found=found)
    persons = sorted({s[:3] for s in E if f"{s[:3]}_03" in E and f"{s[:3]}_08" in E
                      and E[f"{s[:3]}_03"][1] and E[f"{s[:3]}_08"][1]})
    from scipy.optimize import linear_sum_assignment
    Hm = np.stack([E[f"{p}_03"][0] for p in persons])
    Sm = np.stack([E[f"{p}_08"][0] for p in persons])
    cos = Hm @ Sm.T
    cost = -cos.copy()
    np.fill_diagonal(cost, 1e6)
    r, c = linear_sum_assignment(cost)
    rows = [dict(pid=f"frll:{persons[i]}", db="frll", subject=persons[i], H=str(out / f"{persons[i]}_03.png"),
                 H_session="", H_raw=f"{persons[i]}_03.jpg", S=str(out / f"{persons[i]}_08.png"), S_session="",
                 S_raw=f"{persons[i]}_08.jpg", R="", R_neutral="", B_pid=f"frll:{persons[j]}",
                 B=str(out / f"{persons[j]}_08.png"), cos_HS=round(float(cos[i, i]), 4),
                 cos_HB=round(float(cos[i, j]), 4)) for i, j in zip(r, c)]
    with open(K.OUT / "pool_frll.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for tool, d in (("opencv", "morph_opencv"), ("facemorpher", "morph_facemorpher")):
        br = []
        for p in sorted((PUB / d).glob("*.jpg")):
            x, y = p.stem.split("_")
            ax, by = out / f"{x}_03.png", out / f"{y}_03.png"
            if ax.exists() and by.exists():
                br.append(dict(pid=f"frll:{x}|frll:{y}", a=str(ax), b=str(by), out_stem=p.stem, published=str(p)))
        with open(K.OUT / f"bridge_frll_{tool}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(br[0]))
            w.writeheader()
            w.writerows(br)
        log[f"bridge_{tool}"] = len(br)
    log["persons"] = len(persons)
    log["cos_HS_median"] = float(np.median(np.diag(cos)))
    json.dump(log, open(K.RES / "frll_prep_log.json", "w"), indent=1)
    print(json.dumps(log), flush=True)


if __name__ == "__main__":
    main()
