"""AF0 persons, split and pair manifest.

Persons: FRGC + colorFERET candidates exactly as AR1 builds them (`src/AR1/pool.py: candidates()`, imported unchanged:
the record's existing 73_delin_align 512^2 frames with 106-point .tem; FRGC neutral = BlankStare, FERET neutral = fa),
minus every person that appears in experiments/AR1/pool.csv as host (pid) or partner (B_pid) (the reference R is a
photo of the host, so it is covered). No FRLL person (not in the candidate set). Neutral photos only; within a person,
pixel duplicates are dropped with AR1's rule (pool.fp, mean |diff| < 2). Used frames + .tem are copied
byte-identically to OUT/src (the arms frames live in /dev/shm).
Split: per database, persons shuffled with SEED, first 80% train, rest validation (person-disjoint; partners are drawn
from the same split and database).
Images: per split x database x field type a fixed count; host persons cycle through the split's persons (balanced),
host photo and partner (different person, same database and split) and partner photo drawn with SEED; each image has
its own seed for the field. Wave 1 = the first-pass subset (balanced over split, database, field type).
Unprocessed photos: every used neutral photo, kind = photo, map = the shared all-zero map.

  python3 -I pairs.py [--train-per 400 --val-per 100 --w1-train 60 --w1-val 20]   (per database per field type)
"""
import argparse
import collections
import csv
import hashlib
import importlib.util
import json
import pathlib
import random
import shutil
import sys

import numpy as np

AR1_SRC = pathlib.Path("/home/narolski/smad-next/src/AR1")
AR1_POOL = pathlib.Path("/home/narolski/smad-next/experiments/AR1/pool.csv")
OUT = pathlib.Path("/mnt/t7/smad_next/AF0")
RES = pathlib.Path("/home/narolski/smad-next/experiments/AF0")
SEED = 20261111 + 401
FIELDS = ("zero", "u25", "u50", "grad", "bump")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-per", type=int, default=400)
    ap.add_argument("--val-per", type=int, default=100)
    ap.add_argument("--w1-train", type=int, default=60)
    ap.add_argument("--w1-val", type=int, default=20)
    a = ap.parse_args()
    sys.path.insert(0, str(AR1_SRC))
    spec = importlib.util.spec_from_file_location("ar1pool", AR1_SRC / "pool.py")
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)
    K = P.K
    cand = P.candidates()
    ar1 = list(csv.DictReader(open(AR1_POOL)))
    used = {r["pid"] for r in ar1} | {r["B_pid"] for r in ar1}
    by = collections.defaultdict(list)
    seen = set()
    for c in sorted(cand, key=lambda c: c["path"]):
        if c["path"] in seen or not c["neutral"]:
            continue
        seen.add(c["path"])
        pid = f"{c['db']}:{c['subject']}"
        if pid in used or c["db"] not in ("frgc", "feret"):
            continue
        assert not K.forbidden(c["path"])
        by[pid].append(c)
    ndup = 0
    for pid, lst in by.items():
        kept = []
        for c in lst:
            f = P.fp(c["path"])
            if any(np.abs(f - g).mean() < P.SAME_MAD for _, g in kept):
                ndup += 1
                continue
            kept.append((c, f))
        by[pid] = [c for c, _ in kept]
    # copy frames out of volatile storage
    photos = {}
    for pid, lst in sorted(by.items()):
        for c in lst:
            dst = OUT / "src" / c["db"] / c["subject"] / pathlib.Path(c["path"]).name
            dst.parent.mkdir(parents=True, exist_ok=True)
            for ext in (".png", ".tem"):
                s, d = (K.DATA / c["path"]).with_suffix(ext), dst.with_suffix(ext)
                if not d.exists():
                    shutil.copyfile(s, d)
                assert sha(s) == sha(d)
            photos.setdefault(pid, []).append(dict(path=str(dst), raw=c["raw"], session=c["session"], src=c["path"]))
    assert not (set(photos) & used)
    rng = random.Random(SEED)
    split = {}
    for db in ("frgc", "feret"):
        ps = sorted(p for p in photos if p.startswith(db + ":"))
        rng.shuffle(ps)
        ntr = int(round(0.8 * len(ps)))
        for i, p in enumerate(ps):
            split[p] = "train" if i < ntr else "val"
    rows = []
    zero_map = OUT / "maps" / "zero_512.npy"
    zero_map.parent.mkdir(parents=True, exist_ok=True)
    if not zero_map.exists():
        np.save(zero_map, np.zeros((512, 512), np.float16))
    for sp, per, w1 in (("train", a.train_per, a.w1_train), ("val", a.val_per, a.w1_val)):
        for db in ("frgc", "feret"):
            ps = sorted(p for p in photos if split[p] == sp and p.startswith(db + ":"))
            for field in FIELDS:
                order = ps[:]
                rng.shuffle(order)
                combos = set()
                k = 0
                while k < per:
                    host = order[k % len(order)]
                    pa = rng.choice(photos[host])
                    partner = rng.choice([p for p in ps if p != host])
                    pb = rng.choice(photos[partner])
                    key = (pa["path"], pb["path"])
                    if key in combos and len(combos) < len(ps) * (len(ps) - 1):
                        continue
                    combos.add(key)
                    seed = rng.randrange(2 ** 31)
                    iid = f"{sp}_{db}_{field}_{k:04d}"
                    rows.append(dict(id=iid, kind="morph", split=sp, db=db, field=field, seed=seed,
                                     pid_A=host, pid_B=partner, A=pa["path"], B=pb["path"],
                                     image=str(OUT / "img" / sp / field / f"{iid}.png"),
                                     map=str(OUT / "maps" / sp / field / f"{iid}.npy"),
                                     wave=1 if k < w1 else 2))
                    k += 1
            allp = [(p, ph) for p in ps for ph in photos[p]]
            rng.shuffle(allp)
            nw1 = w1  # photos in wave 1: as many as one field type
            for k, (p, ph) in enumerate(allp):
                iid = f"{sp}_{db}_photo_{k:04d}"
                rows.append(dict(id=iid, kind="photo", split=sp, db=db, field="photo", seed="", pid_A=p, pid_B=p,
                                 A=ph["path"], B=ph["path"], image=ph["path"], map=str(zero_map),
                                 wave=1 if k < nw1 else 2))
    cols = list(rows[0])
    with open(OUT / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    shutil.copyfile(OUT / "manifest.csv", RES / "manifest.csv")
    cnt = collections.Counter((r["split"], r["db"], r["field"]) for r in rows)
    cnt1 = collections.Counter((r["split"], r["field"]) for r in rows if r["wave"] == 1)
    persons = collections.Counter((split[p], p.split(":")[0]) for p in photos)
    summ = dict(seed=SEED, candidates=len(cand), ar1_persons_excluded=len(used), pixel_duplicates_dropped=ndup,
                persons={f"{k[0]}/{k[1]}": v for k, v in sorted(persons.items())},
                neutral_photos=sum(len(v) for v in photos.values()),
                images={"/".join(k): v for k, v in sorted(cnt.items())},
                wave1={"/".join(k): v for k, v in sorted(cnt1.items())},
                overlap_with_ar1=len(set(photos) & used),
                train_val_person_overlap=len({r["pid_A"] for r in rows if r["split"] == "train"} &
                                             {r["pid_A"] for r in rows if r["split"] == "val"}))
    json.dump(summ, open(RES / "pairs_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
