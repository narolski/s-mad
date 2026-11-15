"""SM1 amendment A12 item 8 (review F11): release file names against image content, before the SMDD authors' email.

Per split, 100 seeded release morphs (numpy default_rng([20261111, 8, split])) out of `m15k_t` / `m15k_e`; buffalo_l
(insightface, CPU, det 512, largest face; the unchanged detector of landmarks.py) ArcFace normed embeddings of each
morph, its named first contributor, the split's five partner renders and 20 seeded other source renders of the split.
Readings: share of morphs whose named second contributor is the most similar of the split's five partners (chance
0.2); cosine to the named partner vs the mean of the other four; share whose named first contributor is more similar
than all 20 random renders; cosine to the named first contributor vs the 20. No pixel is changed or written.
Single process, one ONNX thread.

  python3 -I a12_names.py -> RES/a12_names.json
"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import landmarks as LM  # noqa: E402


def emb(p):
    import cv2
    img = cv2.imread(str(p))
    fs = LM._IF["app"].get(img)
    if not fs:
        return None
    f = max(fs, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
    return f.normed_embedding.astype(np.float64)


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    LM._init()
    res = {}
    for si, (sp, mdir, sdir, parts) in enumerate((("train", K.M_T, K.SRC_T, K.PARTNERS),
                                                  ("eval", K.M_E, K.SRC_E, K.EVAL_PARTNERS))):
        rng = np.random.default_rng([K.SEED, 8, si])
        names = sorted(x.name for x in mdir.iterdir() if K.PAT.match(x.name))
        pick = [names[i] for i in rng.choice(len(names), 100, replace=False)]
        firsts = {K.PAT.match(n).group(1) for n in names}
        others = sorted(x.name[:-4] for x in sdir.iterdir() if x.suffix == ".png" and x.name[:-4] not in firsts
                        and x.name[:-4] not in parts)
        rnd = [others[i] for i in rng.choice(len(others), 20, replace=False)]
        E = {p: emb(sdir / f"{p}.png") for p in list(parts) + rnd}
        rows, nodet = [], []
        for n in pick:
            a, b = K.PAT.match(n).groups()
            em, ea = emb(mdir / n), emb(sdir / f"{a}.png")
            if em is None or ea is None or any(E[p] is None for p in parts):
                nodet.append(n)
                continue
            cp = {p: float(em @ E[p]) for p in parts}
            cr = [float(em @ E[r]) for r in rnd if E[r] is not None]
            ca = float(em @ ea)
            rows.append(dict(name=n, named_partner=b, top_partner=max(cp, key=cp.get), cos_named=cp[b],
                             cos_other4=float(np.mean([v for k, v in cp.items() if k != b])), cos_first=ca,
                             cos_rand20_mean=float(np.mean(cr)), first_above_all20=bool(ca > max(cr))))
        res[sp] = dict(n=len(rows), no_face=nodet,
                       share_named_partner_top=round(float(np.mean([r["top_partner"] == r["named_partner"]
                                                                    for r in rows])), 3),
                       cos_named_partner_mean=round(float(np.mean([r["cos_named"] for r in rows])), 4),
                       cos_other_four_mean=round(float(np.mean([r["cos_other4"] for r in rows])), 4),
                       share_first_above_all20=round(float(np.mean([r["first_above_all20"] for r in rows])), 3),
                       cos_first_mean=round(float(np.mean([r["cos_first"] for r in rows])), 4),
                       cos_rand20_mean=round(float(np.mean([r["cos_rand20_mean"] for r in rows])), 4),
                       mismatches=[r for r in rows if r["top_partner"] != r["named_partner"]][:20])
        print(sp, json.dumps({k: v for k, v in res[sp].items() if k != "mismatches"}), flush=True)
    json.dump(res, open(K.RES / "a12_names.json", "w"), indent=1)


if __name__ == "__main__":
    main()
