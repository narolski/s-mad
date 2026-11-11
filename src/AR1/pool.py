"""AR1 stage 1: the FRGC + colorFERET host pool (composition rule, 11_AUDIT_PLAN.md).

Candidates = already-aligned 512^2 frames with 106-point .tem that exist in the record (73_delin_align output):
  FRGC  : arms/r6_frgc (raw still known from r6_provenance.csv) + train/bona_frgc whose raw still is known
          (r6_train_sources.csv); session = capture date, expression = rec_subject.emotiontype (BlankStare = neutral),
          both from the FRGC bbaselite dump.
  FERET : train/bona_feret, raw name from dmad/data/maps/feret_map.csv (<subj>_<yymmdd>_<fa|fb>...); session = date,
          neutral = fa.
Within a subject, pixel duplicates (mean |diff| < 2 on the build_arms fingerprint) are dropped (r8 rule).
Per person with neutral photos from >= 2 sessions: host H (neutral, session s1), second S (neutral, session s2 != s1),
optional reference R (another photo of the person, not H or S, for the FR oracle), all drawn with a fixed seed.
B assignment: within each database a permutation without fixed points that maximises the glintr100 cosine
cos(H_p, S_q) (Hungarian), so every person is host once and second contributor once (morph(H_p, S_q)).
Copies the used source frames byte-identically to OUT/src (the /dev/shm arms are volatile).
"""
import collections
import csv
import json
import pathlib
import random
import shutil
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402

SEED = 20261111
SAME_MAD = 2.0
SQL = pathlib.Path("/home/narolski/mambamorph/Datasety/FRGC-2.0/FRGC-2.0-dist/bbaselite_FRGC_2.0/bbaselite_data_frgc2.1.sql")


def frgc_meta():
    rec, uri, emo, sec = {}, {}, {}, None
    for line in open(SQL, errors="replace"):
        if line.startswith("COPY "):
            sec = line.split()[1]
            continue
        if line.startswith("\\."):
            sec = None
            continue
        f = line.rstrip("\n").split("\t")
        if sec == "recording":
            rec[f[0]] = (f[8], f[4][:10])
        elif sec == "rec_frame":
            uri[pathlib.Path(f[2]).stem.lower()] = f[0]
        elif sec == "rec_subject":
            emo[f[0]] = f[14]
    return {k: (rec[r][0], rec[r][1], emo.get(r)) for k, r in uri.items() if r in rec}


def candidates():
    out = []
    meta = frgc_meta()
    for r in csv.DictReader(open(K.DATA / "arms/r6_provenance.csv")):
        if r["db"] != "frgc":
            continue
        env, date, e = meta[pathlib.Path(r["raw"]).stem.lower()]
        out.append(dict(db="frgc", subject=r["subject"], path=r["path"], raw=r["raw"], session=date, env=env,
                        neutral=int(e == "BlankStare")))
    for r in csv.DictReader(open(K.DATA / "arms/r6_train_sources.csv")):
        if r["db"] != "frgc" or r["subject"] != r["train_subject"]:
            continue
        env, date, e = meta[pathlib.Path(r["raw"]).stem.lower()]
        out.append(dict(db="frgc", subject=r["subject"], path=r["train_path"], raw=r["raw"], session=date, env=env,
                        neutral=int(e == "BlankStare")))
    fmap = {r["aligned"]: r for r in csv.DictReader(open(K.MC / "dmad/data/maps/feret_map.csv"))}
    for r in csv.DictReader(open(K.DATA / "manifests/train.csv")):
        if r["arm"] != "bona_feret":
            continue
        m = fmap[pathlib.Path(r["path"]).name]
        parts = m["src"].split("_")
        out.append(dict(db="feret", subject=m["subject"], path=r["path"], raw=m["src"], session=parts[1], env="",
                        neutral=int(parts[2].startswith("fa"))))
    return out


def fp(p):
    import cv2
    img = cv2.imread(str(K.DATA / p))
    return img.reshape(-1, 3)[np.random.RandomState(20261028).choice(512 * 512, 2048, replace=False)].astype(np.int16)


def main():
    t0 = time.time()
    rng = random.Random(SEED)
    cand = candidates()
    for c in cand:
        assert not K.forbidden(c["path"])
    by = collections.defaultdict(list)
    seen = set()
    for c in sorted(cand, key=lambda c: c["path"]):
        if c["path"] in seen:
            continue
        seen.add(c["path"])
        by[(c["db"], c["subject"])].append(c)
    ndup = 0
    for k, lst in by.items():
        kept = []
        for c in lst:
            f = fp(c["path"])
            if any(np.abs(f - g).mean() < SAME_MAD for _, g in kept):
                ndup += 1
                continue
            kept.append((c, f))
        by[k] = [c for c, _ in kept]
    hosts = []
    for k in sorted(by):
        lst = by[k]
        neu = collections.defaultdict(list)
        for c in lst:
            if c["neutral"]:
                neu[c["session"]].append(c)
        if len(neu) < 2:
            continue
        s1, s2 = rng.sample(sorted(neu), 2)
        H, S = rng.choice(neu[s1]), rng.choice(neu[s2])
        rest = [c for c in lst if c["path"] not in (H["path"], S["path"])]
        restn = [c for c in rest if c["neutral"]]
        R = rng.choice(restn or rest) if rest else None
        hosts.append(dict(db=k[0], subject=k[1], H=H, S=S, R=R))
    print(f"candidates {len(cand)}, pixel duplicates dropped {ndup}, subjects {len(by)}, hosts {len(hosts)} "
          f"({collections.Counter(h['db'] for h in hosts)})", flush=True)
    # copy used frames (+ .tem) out of volatile storage
    src = K.OUT / "src"
    used = {}
    for h in hosts:
        for role in ("H", "S", "R"):
            c = h[role]
            if c is None:
                continue
            dst = src / h["db"] / h["subject"] / pathlib.Path(c["path"]).name
            dst.parent.mkdir(parents=True, exist_ok=True)
            for ext in (".png", ".tem"):
                a = (K.DATA / c["path"]).with_suffix(ext)
                b = dst.with_suffix(ext)
                if not b.exists():
                    shutil.copyfile(a, b)
                assert K.sha(a) == K.sha(b)
            c["local"] = str(dst)
            used[str(dst)] = c
    import fr
    paths = sorted(used)
    emb, found = fr.embed_paths(paths, log=lambda s: print(s, flush=True))
    E = {p: (e, f) for p, e, f in zip(paths, emb, found)}
    np.savez(K.OUT / "pool_src_emb.npz", path=np.array(paths), emb=emb, found=found)
    hosts = [h for h in hosts if E[h["H"]["local"]][1] and E[h["S"]["local"]][1]]
    from scipy.optimize import linear_sum_assignment
    rows = []
    for db in ("frgc", "feret"):
        hs = [h for h in hosts if h["db"] == db]
        Hm = np.stack([E[h["H"]["local"]][0] for h in hs])
        Sm = np.stack([E[h["S"]["local"]][0] for h in hs])
        cos = Hm @ Sm.T
        cost = -cos.copy()
        np.fill_diagonal(cost, 1e6)
        r, c = linear_sum_assignment(cost)
        assert (r != c).all()
        for i, j in zip(r, c):
            h, b = hs[i], hs[j]
            R = h["R"]
            rows.append(dict(pid=f"{db}:{h['subject']}", db=db, subject=h["subject"],
                             H=h["H"]["local"], H_session=h["H"]["session"], H_raw=h["H"]["raw"],
                             S=h["S"]["local"], S_session=h["S"]["session"], S_raw=h["S"]["raw"],
                             R=R["local"] if R and E[R["local"]][1] else "", R_neutral=R["neutral"] if R else "",
                             B_pid=f"{db}:{b['subject']}", B=b["S"]["local"], cos_HS=round(float(cos[i, i]), 4),
                             cos_HB=round(float(cos[i, j]), 4)))
    rows.sort(key=lambda r: r["pid"])
    with open(K.OUT / "pool.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    shutil.copyfile(K.OUT / "pool.csv", K.RES / "pool.csv")
    summ = dict(seed=SEED, candidates=len(cand), pixel_duplicates_dropped=ndup, subjects=len(by),
                hosts=dict(collections.Counter(r["db"] for r in rows)), with_reference=sum(bool(r["R"]) for r in rows),
                cos_HS_median=float(np.median([r["cos_HS"] for r in rows])),
                cos_HB_median=float(np.median([r["cos_HB"] for r in rows])), seconds=round(time.time() - t0, 1))
    json.dump(summ, open(K.RES / "pool_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
