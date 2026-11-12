"""MS1 step 1 (prereg part 1, section 3.1-3.2): FFHQ persons.

refs   : glintr100 embeddings (src/AR1/fr.py, unchanged) of the 2,000 ffhqm genuine frames (orig) and of the raw files of
         the 2,000 contributors of ffhqm's 1,000 sampled morph pairs -> OUT/ffhq/emb_ref.npz
select : candidates = FFHQ keys outside the FFHQ-Morphs universe, order random.Random(20261112).shuffle(sorted);
         unchanged aligner scripts/73_delin_align.align (the call of src/AR1/frll_prep.py) -> 512 frame + 106-pt .tem;
         glintr100 of the frame; dropped if cos >= 0.40 to any reference or earlier kept frame; stop at --n kept.
         Parts in kept order: 450 af0 (training), 150 ladder (training), 300 holdout.
  python3 -I ffhq_select.py refs | select [--n 900] [--limit 8]
"""
import argparse
import csv
import json
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ms1common as C  # noqa: E402

THR = 0.40
PARTS = (("af0", 450), ("ladder", 150), ("holdout", 300))
O = C.OUT / "ffhq"


def fr():
    C.add_paths(C.SRC / "AR1")
    import fr as FR
    return FR


def refs(a):
    FR = fr()
    bona = [C.FFHQM / r["path"] for r in csv.DictReader(open(C.FFHQM / "manifests/ffhqm.csv"))
            if r["family"] == "ffhq_bona" and r["variant"] == "orig"]
    contrib = []
    for ln in open(C.FFHQM / "protocol/morph_pair_keys.txt"):
        if ln.strip():
            contrib += ln.strip().split("_")
    contrib = sorted(set(contrib))
    paths = [str(p) for p in bona] + [str(C.raw_ffhq(k)) for k in contrib]
    names = [f"bona:{pathlib.Path(p).name.split('_')[0]}" for p in bona] + [f"contrib:{k}" for k in contrib]
    if a.limit:
        paths, names = paths[:a.limit], names[:a.limit]
    t0 = time.time()
    emb, found = FR.embed_paths(paths, chunk=256, log=lambda s: print(s, f"{time.time() - t0:.0f}s", flush=True))
    O.mkdir(parents=True, exist_ok=True)
    np.savez(O / ("emb_ref.npz" if not a.limit else "emb_ref_smoke.npz"), name=np.array(names), emb=emb, found=found)
    print(json.dumps(dict(n=len(paths), bona=len(bona), contrib=len(contrib), found=int(found.sum()),
                          seconds=round(time.time() - t0))), flush=True)


def select(a):
    import cv2
    FR = fr()
    da = C.load(C.MC / "scripts/73_delin_align.py", "delin_align")
    ex, named = C.excluded_keys()
    assert named <= ex, sorted(named - ex)[:5]
    allk = sorted(f"{int(p.stem):05d}" for d in sorted(C.FFHQ.glob("Part*")) for p in d.glob("*.png"))
    assert len(allk) == 70000, len(allk)
    cand = [k for k in allk if k not in ex]
    random.Random(20261112).shuffle(cand)
    z = np.load(O / ("emb_ref.npz" if not a.limit else "emb_ref_smoke.npz"))
    ref = z["emb"][z["found"]]
    kept_e, kept, log = [], [], []
    src = O / ("src" if not a.limit else "src_smoke")
    src.mkdir(parents=True, exist_ok=True)
    nwant = a.limit or a.n
    t0 = time.time()
    for i, k in enumerate(cand):
        if len(kept) >= nwant:
            break
        raw = C.raw_ffhq(k)
        dst = src / f"{k}.png"
        r = da.align(cv2.imread(str(raw)))
        if r is None:
            log.append(dict(order=i, key=k, outcome="no_face_or_frontal_filter", maxcos_ref="", maxcos_kept="",
                            raw_sha256="", frame_sha256=""))
            continue
        al, lm = r
        e, f = FR.embed_images([al])
        if not f[0]:
            log.append(dict(order=i, key=k, outcome="no_face_in_frame", maxcos_ref="", maxcos_kept="", raw_sha256="",
                            frame_sha256=""))
            continue
        cr = float((ref @ e[0]).max())
        ck = float((np.stack(kept_e) @ e[0]).max()) if kept_e else -1.0
        if cr >= THR or ck >= THR:
            log.append(dict(order=i, key=k, outcome="identity_duplicate", maxcos_ref=round(cr, 4),
                            maxcos_kept=round(ck, 4), raw_sha256="", frame_sha256=""))
            continue
        assert cv2.imwrite(str(dst), al)
        da.write_tem(str(dst)[:-4] + ".tem", lm)
        kept_e.append(e[0])
        kept.append(k)
        log.append(dict(order=i, key=k, outcome="kept", maxcos_ref=round(cr, 4), maxcos_kept=round(ck, 4),
                        raw_sha256=C.sha(raw), frame_sha256=C.sha(dst)))
        if len(kept) % 50 == 0:
            print(f"kept {len(kept)} of {i + 1} attempted, {time.time() - t0:.0f}s", flush=True)
    tag = "" if not a.limit else "_smoke"
    C.write_csv(O / f"select_log{tag}.csv", log)
    np.savez(O / f"emb_kept{tag}.npz", key=np.array(kept), emb=np.stack(kept_e))
    persons, j = [], 0
    for part, n in PARTS:
        for k in kept[j:j + n]:
            persons.append(dict(pid=f"ffhq:{k}", key=k, part=part, frame=str(src / f"{k}.png"),
                                tem=str(src / f"{k}.tem")))
        j += n
    C.write_csv(O / f"persons{tag}.csv", persons)
    from collections import Counter
    summ = dict(candidates=len(cand), excluded_keys=len(ex), attempted=len(log), kept=len(kept),
                outcomes=dict(Counter(r["outcome"] for r in log)), threshold=THR, seconds=round(time.time() - t0),
                parts=dict(Counter(p["part"] for p in persons)),
                aligner_sha256=C.sha(C.MC / "scripts/73_delin_align.py"), fr_sha256=C.sha(C.SRC / "AR1/fr.py"))
    json.dump(summ, open(O / f"select_summary{tag}.json", "w"), indent=1)
    print(json.dumps(summ), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("refs", "select"))
    ap.add_argument("--n", type=int, default=900)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    refs(a) if a.cmd == "refs" else select(a)
