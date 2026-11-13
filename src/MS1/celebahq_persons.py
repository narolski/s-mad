"""MS1 candidate fourth source, CelebA-HQ: persons and overlap (preparation only; no training without a registered
amendment and a pre-run check).

casia  : glintr100 embeddings (a2f_common.embed_crops('glint'), the route of src/AR1/fr.py, unchanged) of up to 3 images
         per CASIA-WebFace identity, read from the packed 112x112 aligned crops (train.rec; used ONLY to exclude persons,
         nothing is scored on it) -> OUT/celebahq/ref_casia.npz
calib  : threshold error on labelled CelebA (data-celeb-aligned, split.csv person_id): 1,000 identities x 2 images
         (seed 20261113), genuine and impostor cosine -> FNMR / FMR at the threshold -> experiments/.../celebahq_calib.json
refs   : embeddings of our other sources' persons: FFHQ (MS1 900 kept + ffhqm references, existing npz), CFD, KDEF,
         TT1 aligned (one frame per TT1 person), FRGC / colorFERET training frames (AF0 + AR1 src) -> ref_<name>.npz
group  : CelebA-HQ persons = connected components of the graph cos >= THR over the aligned frames; components with any
         member at cos >= THR to any reference set are dropped -> OUT/celebahq/persons.csv, summary json
  python3 -I celebahq_persons.py casia|calib|refs|group
"""
import csv
import glob
import json
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ms1common as C  # noqa: E402

O = C.OUT / "celebahq"
THR = 0.40
CASIA = pathlib.Path("/mnt/t7/Datasety/downloads/CASIA-Webface/train.rec")
CELEBA = pathlib.Path("/mnt/t7/Datasety/datasets_processed/data-celeb-aligned")


def fr():
    C.add_paths(C.SRC / "AR1")
    import fr as FR
    return FR


def casia():
    import cv2
    FR = fr()
    PE, A2F = FR._mods()
    per, crops, labels = {}, [], []
    with open(CASIA, "rb") as f:
        while True:
            h = f.read(8)
            if len(h) < 8:
                break
            m, ln = struct.unpack("II", h)
            assert m == 0xced7230a
            n = ln & ((1 << 29) - 1)
            d = f.read(n)
            f.read((4 - n % 4) % 4)
            flag, label, _, _ = struct.unpack("IfQQ", d[:24])
            lab = int(label)
            if per.get(lab, 0) >= 3:
                continue
            img = cv2.imdecode(np.frombuffer(d[24 + 4 * flag:], np.uint8), cv2.IMREAD_COLOR)
            if img is None or img.shape[:2] != (112, 112):
                continue
            per[lab] = per.get(lab, 0) + 1
            crops.append(img)
            labels.append(lab)
    E = np.concatenate([np.asarray(A2F.embed_crops("glint", crops[i:i + 2048]), np.float32)
                        for i in range(0, len(crops), 2048)])
    np.savez(O / "ref_casia.npz", label=np.array(labels), emb=E)
    print(json.dumps(dict(identities=len(per), images=len(labels))), flush=True)


def calib():
    import random
    FR = fr()
    rows = list(csv.DictReader(open(CELEBA / "split.csv")))
    by = {}
    for r in rows:
        by.setdefault(r["person_id"], []).append(r["image_id"])
    ids = sorted(p for p, v in by.items() if len(v) >= 2)
    rng = random.Random(20261113)
    pick = rng.sample(ids, 1000)
    paths, who = [], []
    for p in pick:
        for im in rng.sample(by[p], 2):
            paths.append(str(CELEBA / "images" / im))
            who.append(p)
    E, found = FR.embed_paths(paths)
    who = np.array(who)
    keep = found
    E, who = E[keep], who[keep]
    S = E @ E.T
    iu = np.triu_indices(len(who), 1)
    same = who[iu[0]] == who[iu[1]]
    g, i = S[iu][same], S[iu][~same]
    res = dict(threshold=THR, n_images=int(keep.sum()), genuine_pairs=int(same.sum()), impostor_pairs=int((~same).sum()),
               FNMR=float((g < THR).mean()), FMR=float((i >= THR).mean()),
               genuine_median=float(np.median(g)), impostor_p999=float(np.percentile(i, 99.9)),
               note="CelebA aligned 178x218 JPEG (lower resolution than CelebA-HQ frames); error is indicative")
    json.dump(res, open(C.RES / "celebahq_calib.json", "w"), indent=1)
    print(json.dumps(res), flush=True)


def refs():
    FR = fr()
    out = {}
    z = np.load(C.OUT / "ffhq/emb_kept.npz")
    zr = np.load(C.OUT / "ffhq/emb_ref.npz")
    out["ffhq"] = np.concatenate([z["emb"], zr["emb"][zr["found"]]])
    for name, pool in (("cfd", C.OUT / "cfd/pool.csv"), ("kdef", C.OUT / "kdef/pool.csv")):
        ps = [r["frame"] for r in csv.DictReader(open(pool)) if r["aligned"] == "1"]
        e, f = FR.embed_paths(ps)
        out[name] = e[f]
    import gzip
    tt = {}
    for r in csv.DictReader(gzip.open("/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/"
                                      "aligned_manifest.csv.gz", "rt")):
        if r["aligned"] == "1" and r["person"] not in tt:
            tt[r["person"]] = r["aligned_path"]
    e, f = FR.embed_paths(list(tt.values()))
    out["tt1"] = e[f]
    ff = sorted(glob.glob("/mnt/t7/smad_next/AF0/src/*/*/*.png")) + sorted(glob.glob("/mnt/t7/smad_next/AR1/src/*/*/*.png"))
    e, f = FR.embed_paths(ff)
    out["frgcferet"] = e[f]
    for k, v in out.items():
        np.savez(O / f"ref_{k}.npz", emb=v)
    print(json.dumps({k: len(v) for k, v in out.items()}), flush=True)


def group():
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components
    keys, embs = [], []
    for f in sorted(O.glob("emb_*_*.npz")):
        z = np.load(f)
        keys += list(z["key"])
        embs.append(z["emb"])
    E = np.concatenate(embs)
    rows, cols = [], []
    for i in range(0, len(E), 2048):
        S = E[i:i + 2048] @ E.T
        r, c = np.nonzero(S >= THR)
        rows += list(r + i)
        cols += list(c)
    G = csr_matrix((np.ones(len(rows), np.int8), (rows, cols)), shape=(len(E), len(E)))
    ncomp, lab = connected_components(G, directed=False)
    hit = {}
    for f in sorted(O.glob("ref_*.npz")):
        R = np.load(f)["emb"]
        mx = np.concatenate([(E[i:i + 2048] @ R.T).max(1) for i in range(0, len(E), 2048)])
        hit[f.stem[4:]] = mx >= THR
    any_hit = np.zeros(len(E), bool)
    for v in hit.values():
        any_hit |= v
    bad = set(lab[any_hit])
    sizes = np.bincount(lab)
    out = [dict(index=k, person=f"celebahq:{lab[i]:05d}", component_size=int(sizes[lab[i]]),
                dropped=int(lab[i] in bad), **{f"hit_{n}": int(v[i]) for n, v in hit.items()}) for i, k in enumerate(keys)]
    C.write_csv(O / "persons.csv", out)
    kept = [r for r in out if not r["dropped"]]
    kp = {}
    for r in kept:
        kp.setdefault(r["person"], 0)
        kp[r["person"]] += 1
    summ = dict(threshold=THR, aligned_with_embedding=len(E), components=int(ncomp), largest_component=int(sizes.max()),
                dropped_images=len(out) - len(kept), dropped_persons=len(bad),
                hits_by_reference={n: int(v.sum()) for n, v in hit.items()},
                kept_images=len(kept), kept_persons=len(kp), kept_persons_with_2plus=sum(1 for v in kp.values() if v >= 2),
                kept_component_size_hist={str(s): int(sum(1 for v in kp.values() if v == s)) for s in range(1, 11)})
    json.dump(summ, open(C.RES / "celebahq_persons_summary.json", "w"), indent=1)
    print(json.dumps(summ), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    {"casia": casia, "calib": calib, "refs": refs, "group": group}[sys.argv[1]]()
