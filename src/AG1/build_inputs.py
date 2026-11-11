"""AG1 / AG2 / AG3 generator inputs, pair lists and shard plans (CPU, DGX; nothing is scored here).

Pools
  frll  the 102 FRLL persons of the corrected MAD22 bona fide (BonaFide/NNN_03.jpg neutral, NNN_08.jpg smiling,
        byte-identical to frll_base). s1 = _03, s2 = _08.
  feret colorFERET subjects with a frontal 'fa*' capture on >= 2 distinct dates; s1, s2 = one fa capture of each of
        two distinct dates (seeded). Gender from the subject ground truth.
  frgc  FRGC 2.0 subjects with controlled stills (env nd1E00004 / nd1E00005) of emotion 'BlankStare' on >= 2 distinct
        capture dates; s1, s2 = one still of each of two dates (seeded). Gender from the bbaselite subject table.
  val10 subjects (smadcvpr/prep_train.is_val) are excluded from feret / frgc (sealed VAL-X persons stay unexposed).
Per photo, the registered H4 / A33 input path (h4_prep.py l.69-74; the same calls re-typed here, not imported as a
function): prep_eval.kps (buffalo_l det, CPU) -> gancommon.ffhq_align 1024 (imported unchanged: LANCZOS shrink,
reflect padding with Gaussian blur and median blend of the padded border, bilinear quad warp) -> cv2.resize INTER_AREA
512 -> prep_eval.kps on the crop -> kps256. These resampling / blur steps are NOT on OWNER_BRIEF's allowed list; they
are the generator's input alignment of the approved A33 set, flagged for the author's acknowledgement.
Pairing (R4 partner sigma): frll = a cycle cover restricted to the published MAD22 MIPGAN pairs (edge present in
MIPGAN_I 03-03 and 08-08 lists), max total w600k cosine of s1(p) vs s1(q) (same expression, as the bridge pair); feret / frgc = a cycle cover within (db, gender), max total
w600k cosine of s1(p) vs s2(q) (linear_sum_assignment, diagonal forbidden).
Rungs per person p (MIPGAN-I = mip1; frll also MIPGAN-II-style = mip2):
  R2   mipgan(x, x) for x in {s1(p), s2(p)}          (A = B, the pipeline-only image)
  R2i  G(w_inv(x)) render of the inversion (mip1 only; descriptive)
  R3   mipgan(s1(p), s2(p))                         (twin)
  R4   mipgan(s1(p), s2(sigma p))                   (morph; same host photo, B from the other session/expression)
  R3m  mipgan(s1(p), mirror(s1(p)))                 (mirror self-morph: one photograph, one person; amendment 2)
  BR   frll only: mipgan(p_e, sigma(p)_e), e in {03, 08}, the published pair (bridge), unordered pairs deduplicated
  RT   every FRLL person + 25 FERET + 25 FRGC: mipgan(s2(p), s1(p)) (order-reversed twin; determinism / noise floor)
  AG3  feret / frgc subset of 80 R4 edges: alpha in {0, 0.1, 0.2, 0.3, 0.4} through mipgan_alpha (0.5 = R4 of the core)
  AG3T the same 80 hosts' twin pairs (s1(p), s2(p)) at alpha 0.1 ... 0.4 (second photo without second identity)
Usage: build_inputs.py select | prep | pair | mirror | shards   (each stage reads the previous stage's outputs)
"""
import csv
import glob
import hashlib
import json
import pathlib
import random
import re
import sys
from collections import defaultdict

import numpy as np

OUT = pathlib.Path("/mnt/t7/smad_next/AG1/inputs")
CODE = pathlib.Path("/home/narolski/mambamorph-code")
GAN1 = pathlib.Path("/home/narolski/mambamorph-code-gan1/smadcvpr/gan")
MAD = pathlib.Path("/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted")
FERET = pathlib.Path("/mnt/t7/Datasety/colorferet")
FRGC = pathlib.Path("/mnt/t7/Datasety/FRGC-2.0/FRGC-2.0-dist")
SQL = FRGC / "bbaselite_FRGC_2.0/bbaselite_data_frgc2.1.sql"
CONTROLLED = {"nd1E00004", "nd1E00005"}
SEED = 20261111
N_POOL = {"feret": 100, "frgc": 100}
N_CAND = {"feret": 125, "frgc": 125}          # candidates in seeded order; the first N_POOL that prep keeps are used
N_AG3 = {"feret": 40, "frgc": 40}
N_RT = {"frll": 102, "feret": 25, "frgc": 25}   # pre-run review: RT on every FRLL person + 50 primary (noise floor)
# H100 seconds (measured: H4 job 6237081 log.jsonl: inversion 500 steps median 23.3 s, a morph incl. 2 inversions
# 53.6 s -> MIPGAN-I 150 steps 6.9 s; A28 job mipgan2 FERET 0-124: 9.3 s per morph incl. 2 e4e encodes)
T_INV, T_MIP1, T_MIP2 = 23.3, 7.0, 9.3
SAFETY, FIXED_MIN = 1.3, 12                  # est_minutes = SAFETY * GPU time + fixed (2.6 GB pack copy, load, tar)
SHARD_MAX_MIN = 150


def is_val(subject):                          # = smadcvpr/prep_train.is_val (checked in main)
    return int(hashlib.sha1(f"smadcvpr:{subject}".encode()).hexdigest(), 16) % 10 == 0


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ------------------------------------------------------------------------------------------------------ select
def feret_candidates():
    rows = defaultdict(lambda: defaultdict(list))
    for p in sorted(glob.glob(str(FERET / "dvd*/data/images/*/*_fa*.ppm.bz2"))):
        m = re.match(r"(\d{5})_(\d{6})_(fa[^.]*)\.ppm\.bz2$", pathlib.Path(p).name)
        if m:
            rows[m.group(1)][m.group(2)].append(p)
    gender = {}
    for t in glob.glob(str(FERET / "dvd*/data/ground_truths/name_value/*/[0-9][0-9][0-9][0-9][0-9].txt")):
        kv = dict(l.strip().split("=", 1) for l in open(t) if "=" in l)
        gender[pathlib.Path(t).stem] = kv.get("gender", "?")
    out = []
    for s, dates in rows.items():
        if len(dates) >= 2 and not is_val(s) and gender.get(s) in ("Male", "Female"):
            out.append({"db": "feret", "subject": s, "gender": gender[s][0],
                        "dates": {d: sorted(v) for d, v in dates.items()}})
    return out


def frgc_candidates():
    rec, uri, emo, subj, gender = {}, {}, {}, {}, {}
    sec = None
    for line in open(SQL, errors="replace"):
        if line.startswith("COPY "):
            sec = line.split()[1]
            continue
        if line.startswith("\\."):
            sec = None
            continue
        f = line.rstrip("\n").split("\t")
        if sec == "recording":
            rec[f[0]] = (f[8], f[4][:10])                  # env_id, capture date (as build_arms.frgc_meta)
        elif sec == "rec_frame":
            uri[f[0]] = f[2]
        elif sec == "rec_subject":
            subj[f[0]], emo[f[0]] = f[1], f[14]
        elif sec == "subject":
            gender[f[0]] = f[6].strip()
    per = defaultdict(lambda: defaultdict(list))
    for r, (env, date) in rec.items():
        if env in CONTROLLED and emo.get(r) == "BlankStare" and r in uri and r in subj:
            p = FRGC / "nd1" / uri[r]
            if p.suffix.lower() == ".jpg" and p.exists():
                per[subj[r]][date].append(str(p))
    out = []
    for s, dates in per.items():
        sid = s.replace("nd1S", "")
        if len(dates) >= 2 and not is_val(sid) and gender.get(s) in ("M", "F"):
            out.append({"db": "frgc", "subject": sid, "gender": gender[s],
                        "dates": {d: sorted(v) for d, v in dates.items()}})
    return out


def stage_select():
    sys.path.insert(0, str(CODE / "smadcvpr"))
    import prep_train                                         # noqa: E402  (only its is_val)
    for s in ("00001", "02463", "00423", "04201"):
        assert prep_train.is_val(s) == is_val(s)
    rng = random.Random(SEED)
    sel = []
    for db, cands in (("feret", feret_candidates()), ("frgc", frgc_candidates())):
        cands.sort(key=lambda r: r["subject"])
        rng.shuffle(cands)
        for r in cands[:N_CAND[db]]:
            d1, d2 = sorted(rng.sample(sorted(r["dates"]), 2))
            sel.append({"db": db, "person": f"{db}_{r['subject']}", "subject": r["subject"], "gender": r["gender"],
                        "s1": rng.choice(r["dates"][d1]), "s2": rng.choice(r["dates"][d2]), "d1": d1, "d2": d2,
                        "n_eligible": len(cands)})
    for f in sorted(MAD.glob("BonaFide/*_03.jpg")):
        n = f.name[:3]
        sel.append({"db": "frll", "person": f"frll_{n}", "subject": n, "gender": "?", "s1": str(f),
                    "s2": str(MAD / "BonaFide" / f"{n}_08.jpg"), "d1": "03", "d2": "08"})
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(sel, open(OUT / "select.json", "w"), indent=0)
    c = defaultdict(int)
    for r in sel:
        c[(r["db"], r["gender"])] += 1
    print("SELECT", dict(c), {db: next(r["n_eligible"] for r in sel if r["db"] == db) for db in ("feret", "frgc")})


# ------------------------------------------------------------------------------------------------------ prep
def read_bgr(p):
    import bz2
    import cv2
    if p.endswith(".bz2"):
        buf = np.frombuffer(bz2.decompress(open(p, "rb").read()), np.uint8)
        return cv2.imdecode(buf, cv2.IMREAD_COLOR)
    return cv2.imread(p, cv2.IMREAD_COLOR)


def stage_prep():
    import cv2
    sys.path.insert(0, str(CODE / "smadcvpr"))
    import prep_eval                                          # noqa: E402  (unchanged)
    sys.path.insert(0, str(GAN1))
    import gancommon as G                                     # noqa: E402  (unchanged)
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"],
                       providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(512, 512))
    det = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"], providers=["CPUExecutionProvider"])
    det.prepare(ctx_id=-1, det_size=(512, 512))
    prep_eval._APP = det                                       # as h4_prep.cpu_app
    sel = json.load(open(OUT / "select.json"))
    (OUT / "pack/crops").mkdir(parents=True, exist_ok=True)
    photos, emb, drop = {}, {}, {}
    kept = defaultdict(int)
    for r in sel:
        if r["db"] != "frll" and kept[r["db"]] >= N_POOL[r["db"]]:
            continue
        ok = True
        rec = {}
        for slot in ("s1", "s2"):
            pid = f"{r['person']}__{slot}"
            im = read_bgr(r[slot])
            k = prep_eval.kps(im) if im is not None else None
            if k is None:
                ok = False
                drop[pid] = "no_face_src"
                break
            crop, padded = G.ffhq_align(cv2.cvtColor(im, cv2.COLOR_BGR2RGB), np.asarray(k, np.float64), 1024)
            c512 = cv2.resize(cv2.cvtColor(crop, cv2.COLOR_RGB2BGR), (512, 512), interpolation=cv2.INTER_AREA)
            kc = prep_eval.kps(c512)
            fc = app.get(c512)
            if kc is None or not fc:
                ok = False
                drop[pid] = "no_face_crop"
                break
            f = max(fc, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
            rec[pid] = ({"photo": pid, "person": r["person"], "db": r["db"], "slot": slot, "gender": r["gender"],
                         "src": r[slot], "src_sha256": sha(r[slot]), "date": r["d1" if slot == "s1" else "d2"],
                         "crop": f"crops/{pid}.png", "kps256": (np.asarray(kc) / 2).tolist(),
                         "reflect_padded": bool(padded)}, c512, f.normed_embedding)
        if not ok:
            if r["db"] == "frll":
                sys.exit(f"FRLL photo of {r['person']} failed prep: {drop}")
            continue
        for pid, (meta, c512, e) in rec.items():
            cv2.imwrite(str(OUT / "pack" / meta["crop"]), c512)
            meta["crop_sha256"] = sha(OUT / "pack" / meta["crop"])
            photos[pid] = meta
            emb[pid] = e
        kept[r["db"]] += 1
    json.dump(photos, open(OUT / "pack/photos.json", "w"), indent=0)
    np.savez(OUT / "emb_w600k.npz", ids=np.array(sorted(emb)), emb=np.stack([emb[k] for k in sorted(emb)]))
    json.dump(drop, open(OUT / "prep_drop.json", "w"), indent=1)
    print("PREP kept persons", dict(kept), "dropped photos", len(drop))


# ------------------------------------------------------------------------------------------------------ pair
def cycle_cover(names, score, allowed=None):
    """max-total-score permutation without fixed points (linear_sum_assignment on -score, diagonal forbidden)."""
    from scipy.optimize import linear_sum_assignment
    n = len(names)
    C = -np.asarray(score, float).copy()
    C[np.arange(n), np.arange(n)] = 1e6
    if allowed is not None:
        C[~allowed] = 1e6
    r, c = linear_sum_assignment(C)
    if (C[r, c] >= 1e6).any():
        sys.exit("cycle cover infeasible")
    return {names[i]: names[j] for i, j in zip(r, c)}


def cycles(sigma):
    seen, out = set(), []
    for p in sorted(sigma):
        if p in seen:
            continue
        cyc, q = [], p
        while q not in seen:
            seen.add(q)
            cyc.append(q)
            q = sigma[q]
        out.append(cyc)
    return out


def stage_pair():
    photos = json.load(open(OUT / "pack/photos.json"))
    z = np.load(OUT / "emb_w600k.npz")
    E = {k: v for k, v in zip(z["ids"], z["emb"])}
    persons = defaultdict(list)
    for pid, m in photos.items():
        persons[(m["db"], m["gender"])].append(m["person"])
    sigma = {}
    for key, ps in persons.items():
        ps = sorted(set(ps))
        S = np.array([[float(E[f"{p}__s1"] @ E[f"{q}__s2"]) for q in ps] for p in ps])
        allowed = None
        if key[0] == "frll":
            names = {f.name for f in (MAD / "MIPGAN_I").glob("*.png")}

            def published(a, b):                          # the bridge needs the pair in both expressions
                return all(f"{a}_{e}-vs-{b}_{e}.png" in names or f"{b}_{e}-vs-{a}_{e}.png" in names
                           for e in ("03", "08"))
            num = [p.split("_")[1] for p in ps]
            allowed = np.array([[published(a, b) for b in num] for a in num])
            S = np.array([[float(E[f"{p}__s1"] @ E[f"{q}__s1"]) for q in ps] for p in ps])
        sigma.update(cycle_cover(ps, S, allowed))
    rows = []
    for p, q in sorted(sigma.items()):
        db = p.split("_")[0]
        rows.append({"person": p, "partner": q, "db": db, "gender": photos[f"{p}__s1"]["gender"],
                     "cos_s1p_s2q": float(E[f"{p}__s1"] @ E[f"{q}__s2"]),
                     "cos_s1p_s1q": float(E[f"{p}__s1"] @ E[f"{q}__s1"]),
                     "cos_s1p_s2p": float(E[f"{p}__s1"] @ E[f"{p}__s2"])})
    with open(OUT / "pairs.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    json.dump(sigma, open(OUT / "sigma.json", "w"), indent=0)
    for db in ("frll", "feret", "frgc"):
        r = [x for x in rows if x["db"] == db]
        print(f"PAIR {db}: {len(r)} persons, {len(cycles({x['person']: x['partner'] for x in r}))} cycles, "
              f"morph-contrib cos mean {np.mean([x['cos_s1p_s2q'] for x in r]):.3f}, "
              f"twin-contrib cos mean {np.mean([x['cos_s1p_s2p'] for x in r]):.3f}")


# ------------------------------------------------------------------------------------------------------ mirror
def stage_mirror():
    """R3m inputs: the host photo s1 of every person mirrored left-right (lossless np.fliplr of the stored 512 crop,
    allowed by the lead / author on 11 Nov), 5 points re-detected on the mirrored crop (prep_eval.kps, CPU)."""
    import cv2
    sys.path.insert(0, str(CODE / "smadcvpr"))
    import prep_eval                                          # noqa: E402  (unchanged)
    from insightface.app import FaceAnalysis
    det = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"], providers=["CPUExecutionProvider"])
    det.prepare(ctx_id=-1, det_size=(512, 512))
    prep_eval._APP = det
    photos = json.load(open(OUT / "pack/photos.json"))
    n = 0
    for pid in sorted(k for k in photos if k.endswith("__s1")):
        m = photos[pid]
        mid = pid + "m"
        img = cv2.imread(str(OUT / "pack" / m["crop"]), cv2.IMREAD_COLOR)
        fl = np.ascontiguousarray(img[:, ::-1])
        k = prep_eval.kps(fl)
        if k is None:
            sys.exit(f"{mid}: no face on the mirrored crop")
        crop = f"crops/{mid}.png"
        cv2.imwrite(str(OUT / "pack" / crop), fl)
        back = cv2.imread(str(OUT / "pack" / crop), cv2.IMREAD_COLOR)
        assert np.array_equal(back[:, ::-1], img), "mirror not lossless"
        photos[mid] = {**m, "photo": mid, "slot": "s1m", "crop": crop, "crop_sha256": sha(OUT / "pack" / crop),
                       "kps256": (np.asarray(k) / 2).tolist(), "mirror_of": pid}
        n += 1
    json.dump(photos, open(OUT / "pack/photos.json", "w"), indent=0)
    print(f"MIRROR {n} mirrored host crops")


# ------------------------------------------------------------------------------------------------------ shards
def job(stem, rung, a, b, alpha=0.5, gen="mip1"):
    return {"stem": stem, "rung": rung, "a": a, "b": b, "alpha": alpha, "gen": gen}


def person_jobs(p, q, gen, db):
    s1, s2, q1, q2 = f"{p}__s1", f"{p}__s2", f"{q}__s1", f"{q}__s2"
    g = gen
    J = [job(f"{g}_R2_{s1}", "R2", s1, s1, gen=g), job(f"{g}_R2_{s2}", "R2", s2, s2, gen=g),
         job(f"{g}_R3_{p}", "R3", s1, s2, gen=g), job(f"{g}_R4_{p}", "R4", s1, q2, gen=g),
         job(f"{g}_R3m_{p}", "R3m", s1, f"{p}__s1m", gen=g)]
    if g == "mip1":
        J += [job(f"{g}_R2i_{s1}", "R2i", s1, s1, gen=g), job(f"{g}_R2i_{s2}", "R2i", s2, s2, gen=g)]
    return J


def est_min(n_inv, n_mip, gen):
    t = n_inv * T_INV + n_mip * (T_MIP1 if gen == "mip1" else T_MIP2)
    return int(np.ceil(SAFETY * t / 60 + FIXED_MIN))


def stage_shards():
    photos = json.load(open(OUT / "pack/photos.json"))
    sigma = json.load(open(OUT / "sigma.json"))
    rng_rt, rng_ag3 = random.Random(SEED + 1), random.Random(SEED + 2)
    shards = []

    def pack_cycles(db, gen, extra):
        cyc = cycles({p: q for p, q in sigma.items() if p.startswith(db + "_")})
        cur, out = [], []

        def cost(ps):
            n_mip = 5 * len(ps)                                   # R2 x 2, R3, R4, R3m (R2i: no optimisation)
            return est_min(0 if gen == "mip2" else 3 * len(ps), n_mip + extra(ps), gen)
        for c in cyc:
            if cur and cost(cur + c) > SHARD_MAX_MIN:
                out.append(cur)
                cur = []
            cur = cur + c
        if cur:
            out.append(cur)
        return out

    def bridge_and_rt(ps, rt, db):
        J = []
        seen = set()
        for p in ps:
            q = sigma[p]
            for e, slot in ((("03", "s1"), ("08", "s2")) if db == "frll" else ()):
                u = frozenset((p, q, e))
                if u in seen:
                    continue
                seen.add(u)
                J.append(job(f"{{g}}_BR{e}_{p}_{q}", "BR", f"{p}__{slot}", f"{q}__{slot}"))
            if p in rt:
                J.append(job(f"{{g}}_RT_{p}", "RT", f"{p}__s2", f"{p}__s1"))
        return J

    frll = sorted(p for p in sigma if p.startswith("frll_"))
    rt = set()
    for db in ("frll", "feret", "frgc"):
        rt |= set(rng_rt.sample(sorted(p for p in sigma if p.startswith(db + "_")), N_RT[db]))
    for gen in ("mip1", "mip2"):
        for db in ("frll", "feret", "frgc"):
            if gen == "mip2" and db != "frll":
                continue
            groups = pack_cycles(db, gen, lambda ps: len(bridge_and_rt(ps, rt, db)))
            for i, ps in enumerate(groups):
                J = []
                for p in ps:
                    J += person_jobs(p, sigma[p], gen, db)
                for j in bridge_and_rt(ps, rt, db):
                    j["stem"] = j["stem"].replace("{g}", gen)
                    j["gen"] = gen
                    J.append(j)
                inv = sorted({f"{p}__{s}" for p in ps for s in ("s1", "s2", "s1m")} |
                             {j["b"] for j in J})
                n_mip = sum(1 for j in J if j["rung"] != "R2i")
                shards.append({"shard": f"AG1_{gen}_{db}_{i:02d}", "gen": gen, "db": db, "persons": ps,
                               "invert": inv, "jobs": J, "needs": [],
                               "est_minutes": est_min(len(inv) if gen == "mip1" else 0, n_mip, gen)})
    # AG3: graded mixing on a seeded subset of R4 edges (alpha 0 through mipgan_alpha too, pre-run review 9), and the
    # twin-dose arm AG3T (the same hosts' R3 pairs at the same alphas: second photo without second identity);
    # latents from the core mip1 shards
    owner = {}
    for s in shards:
        if s["gen"] == "mip1":
            for ph in s["invert"]:
                owner[ph] = s["shard"]
    for db in ("feret", "frgc"):
        ps = sorted(p for p in sigma if p.startswith(db + "_"))
        sub = sorted(rng_ag3.sample(ps, N_AG3[db]))
        J = [job(f"mip1_AG3a{int(round(a * 10))}_{p}", "AG3", f"{p}__s1", f"{sigma[p]}__s2", alpha=a)
             for p in sub for a in (0.0, 0.1, 0.2, 0.3, 0.4)]
        J += [job(f"mip1_AG3Ta{int(round(a * 10))}_{p}", "AG3T", f"{p}__s1", f"{p}__s2", alpha=a)
              for p in sub for a in (0.1, 0.2, 0.3, 0.4)]
        need = sorted({owner[j["a"]] for j in J} | {owner[j["b"]] for j in J})
        half = len(J) // 2
        for i, JJ in enumerate((J[:half], J[half:])):
            shards.append({"shard": f"AG1_mip1_{db}_ag3_{i:02d}", "gen": "mip1", "db": db, "persons": [],
                           "invert": [], "jobs": JJ, "needs": need,
                           "est_minutes": est_min(0, len(JJ), "mip1")})
    # smoke shards (first in the queue; their images never enter the data: ag1_manifest skips *smoke*): 2 FRLL
    # persons p1, p2 = sigma(p1), real iteration counts, every code path (R2, R2i, R3, R4, RT, AG3 alpha, mip2)
    p1 = frll[0]
    p2 = sigma[p1]
    sm = [job("smoke_mip1_R2_" + p1, "R2", f"{p1}__s1", f"{p1}__s1"),
          job("smoke_mip1_R2i_" + p1, "R2i", f"{p1}__s1", f"{p1}__s1"),
          job("smoke_mip1_R3_" + p1, "R3", f"{p1}__s1", f"{p1}__s2"),
          job("smoke_mip1_R4_" + p1, "R4", f"{p1}__s1", f"{p2}__s2"),
          job("smoke_mip1_R3_" + p2, "R3", f"{p2}__s1", f"{p2}__s2"),
          job("smoke_mip1_RT_" + p1, "RT", f"{p1}__s2", f"{p1}__s1"),
          job("smoke_mip1_AG3a3_" + p1, "AG3", f"{p1}__s1", f"{p2}__s2", alpha=0.3),
          job("smoke_mip1_R2_" + p2, "R2", f"{p2}__s1", f"{p2}__s1"),
          job("smoke_mip1_R3m_" + p1, "R3m", f"{p1}__s1", f"{p1}__s1m"),
          job("smoke_mip1_R3m_" + p2, "R3m", f"{p2}__s1", f"{p2}__s1m"),
          job("smoke_mip1_R4_" + p2, "R4", f"{p2}__s1", f"{sigma[p2]}__s2")]
    sm2 = [dict(j, stem=j["stem"].replace("mip1", "mip2"), gen="mip2") for j in sm
           if j["rung"] in ("R2", "R3", "R4", "R3m")]
    for name, gen, J in (("AG1_smoke_mip1", "mip1", sm), ("AG1_smoke_mip2", "mip2", sm2)):
        inv = sorted({j["a"] for j in J} | {j["b"] for j in J})
        shards.append({"shard": name, "gen": gen, "db": "frll", "persons": [p1, p2], "invert": inv, "jobs": J,
                       "needs": [], "smoke": True,
                       "est_minutes": est_min(len(inv) if gen == "mip1" else 0, len(J), gen) + 5})
    order = {"frll": 0, "feret": 1, "frgc": 1}
    shards.sort(key=lambda s: (not s.get("smoke", False), s["shard"].find("ag3") >= 0, s["gen"] == "mip2",
                               order[s["db"]], s["shard"]))
    for k, s in enumerate(shards):
        s["order"] = k
    (OUT / "shards").mkdir(exist_ok=True)
    for s in shards:
        json.dump(s, open(OUT / "shards" / f"{s['shard']}.json", "w"), indent=0)
    tot = sum(s["est_minutes"] for s in shards)
    for s in shards:
        print(f"{s['order']:2d} {s['shard']:26s} inv {len(s['invert']):3d} jobs {len(s['jobs']):4d} "
              f"est {s['est_minutes']:4d} min needs {len(s['needs'])}")
    print(f"SHARDS {len(shards)}, est total {tot} min = {tot / 60:.1f} slot-h")


if __name__ == "__main__":
    {"select": stage_select, "prep": stage_prep, "pair": stage_pair, "mirror": stage_mirror,
     "shards": stage_shards}[sys.argv[1]]()
