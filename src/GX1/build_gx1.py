"""GAN morphs in training (GX1): persons, inputs, pairs and generation shard plans. Reuses the AG1 builder
(src/AG1/build_inputs.py) unchanged for photo selection rules, input prep (the H4 / A33 path) and the cycle cover.
Persons: protocol-network (PN1) training persons (ladder training hosts, train_genuine = 1; AF0 pn1_use = train) and
development persons (ladder role dev; AF0 pn1_use = dev), from the PN1 split files only (never valx.csv), with two
neutral photos of two capture dates under the AG1 rule (FERET fa* frontals; FRGC controlled BlankStare stills; val10
excluded by the AG1 rule and by PN1's V).
Pairs: within (split group, database, gender): training hosts get two disjoint cycle covers (two partners each, 2 R4
per host), development hosts one cover; max total w600k cosine of s1(p) vs s2(q) (the AG1 look-alike rule).
Stages: select | prep | pair | shards.  Out: /mnt/t7/smad_next/GX1/inputs/
"""
import csv
import json
import pathlib
import random
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/AG1")
import build_inputs as BI  # noqa: E402

OUT = pathlib.Path("/mnt/t7/smad_next/GX1/inputs")
SPLIT = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split")
SEED = 20261113


def groups():
    a = {r["pid"]: r for r in csv.DictReader(open(SPLIT / "af0_split.csv"))}
    l = {r["pid"]: r for r in csv.DictReader(open(SPLIT / "ladder_split.csv"))}
    train = {p for p, r in l.items() if r["train_genuine"] == "1"} | {p for p, r in a.items() if r["pn1_use"] == "train"}
    dev = {p for p, r in l.items() if r["role"] == "dev"} | {p for p, r in a.items() if r["pn1_use"] == "dev"}
    assert not train & dev
    return train, dev


def stage_select():
    train, dev = groups()
    rng = random.Random(SEED)
    sel = []
    for c in sorted(BI.feret_candidates() + BI.frgc_candidates(), key=lambda c: (c["db"], c["subject"])):
        pid = f"{c['db']}:{c['subject']}"
        g = "train" if pid in train else "dev" if pid in dev else None
        if g is None:
            continue
        d1, d2 = sorted(rng.sample(sorted(c["dates"]), 2))
        sel.append({"db": c["db"], "person": f"{c['db']}_{c['subject']}", "subject": c["subject"],
                    "gender": c["gender"], "group": g, "s1": rng.choice(c["dates"][d1]),
                    "s2": rng.choice(c["dates"][d2]), "d1": d1, "d2": d2})
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(sel, open(OUT / "select.json", "w"), indent=0)
    from collections import Counter
    print("SELECT", Counter((r["group"], r["db"], r["gender"]) for r in sel))


def stage_prep():
    import insightface.app as IA                   # DGX courtesy: onnxruntime sessions capped at 2 threads after prepare
    sys.path.insert(0, "/home/narolski/smad-next/src/AG1")
    import ag1_manifest as AM
    _prep = IA.FaceAnalysis.prepare

    def prepare(self, *a, **k):
        _prep(self, *a, **k)
        AM.cap_threads(self)
    IA.FaceAnalysis.prepare = prepare
    BI.OUT = OUT                                   # AG1's stage_prep, unchanged, pointed at the GX1 folder
    BI.N_POOL = {"feret": 10 ** 6, "frgc": 10 ** 6}
    BI.stage_prep()


def stage_pair():
    photos = json.load(open(OUT / "pack/photos.json"))
    sel = {r["person"]: r for r in json.load(open(OUT / "select.json"))}
    z = np.load(OUT / "emb_w600k.npz")
    E = {k: v for k, v in zip(z["ids"], z["emb"])}
    by = defaultdict(list)
    for m in photos.values():
        by[(sel[m["person"]]["group"], m["db"], m["gender"])].append(m["person"])
    rows = []
    for (g, db, gen), ps in sorted(by.items()):
        ps = sorted(set(ps))
        if len(ps) < 3:
            print("SKIP group too small", g, db, gen, ps)
            continue
        S = np.array([[float(E[f"{p}__s1"] @ E[f"{q}__s2"]) for q in ps] for p in ps])
        allowed = np.ones_like(S, bool)
        covers = 2 if g == "train" else 1
        for k in range(covers):
            sig = BI.cycle_cover(ps, S, allowed)
            for p, q in sig.items():
                rows.append({"group": g, "db": db, "gender": gen, "cover": k, "person": p, "partner": q,
                             "cos_s1p_s2q": float(E[f"{p}__s1"] @ E[f"{q}__s2"]),
                             "cos_s1p_s2p": float(E[f"{p}__s1"] @ E[f"{p}__s2"])})
                i, j = ps.index(p), ps.index(q)
                allowed[i, j] = allowed[j, i] = False      # the second cover uses new pairs only
    with open(OUT / "pairs.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print("PAIRS", Counter((r["group"], r["cover"]) for r in rows))
    for g in ("train", "dev"):
        c = [r["cos_s1p_s2q"] for r in rows if r["group"] == g]
        print(g, "contributor cosine quartiles", np.round(np.quantile(c, [0, .25, .5, .75, 1]), 3))


def job(stem, rung, a, b, gen):
    return {"stem": stem, "rung": rung, "a": a, "b": b, "alpha": 0.5, "gen": gen}


def stage_shards():
    pairs = list(csv.DictReader(open(OUT / "pairs.csv")))
    hosts = defaultdict(list)
    for r in pairs:
        hosts[(r["group"], r["db"])].append(r)
    shards = []
    for gen in ("mip1", "mip2"):
        for (g, db), rs in sorted(hosts.items()):
            ps = sorted({r["person"] for r in rs})
            J = []
            for p in ps:
                s1, s2 = f"{p}__s1", f"{p}__s2"
                J += [job(f"gx1_{gen}_R2_{s1}", "R2", s1, s1, gen), job(f"gx1_{gen}_R2_{s2}", "R2", s2, s2, gen),
                      job(f"gx1_{gen}_R3_{p}", "R3", s1, s2, gen)]
            for r in rs:
                J.append(job(f"gx1_{gen}_R4c{r['cover']}_{r['person']}", "R4", f"{r['person']}__s1",
                             f"{r['partner']}__s2", gen))
            per = 160 if gen == "mip1" else 260                       # images per shard (about 1.0-1.5 H100-h)
            for i in range(0, len(J), per):
                JJ = J[i:i + per]
                inv = sorted({j["a"] for j in JJ} | {j["b"] for j in JJ})
                t = (len(inv) * BI.T_INV if gen == "mip1" else 0) + len(JJ) * (BI.T_MIP1 if gen == "mip1" else BI.T_MIP2)
                shards.append({"shard": f"GX1_{gen}_{g}_{db}_{i // per:02d}", "gen": gen, "db": db, "group": g,
                               "persons": ps, "invert": inv, "jobs": JJ, "needs": [],
                               "est_minutes": int(np.ceil(1.3 * t / 60 + 12))})
    # smoke shards (2 training persons and one of their R4; never data): every job type for both generators
    r0 = next(r for r in pairs if r["group"] == "train" and r["cover"] == "0")
    p1, q1 = r0["person"], r0["partner"]
    for gen in ("mip1", "mip2"):
        J = [job(f"gx1smoke_{gen}_R2_{p1}__s1", "R2", f"{p1}__s1", f"{p1}__s1", gen),
             job(f"gx1smoke_{gen}_R3_{p1}", "R3", f"{p1}__s1", f"{p1}__s2", gen),
             job(f"gx1smoke_{gen}_R4c0_{p1}", "R4", f"{p1}__s1", f"{q1}__s2", gen)]
        inv = sorted({j["a"] for j in J} | {j["b"] for j in J})
        shards.insert(0, {"shard": f"GX1_smoke_{gen}", "gen": gen, "db": r0["db"], "group": "train", "persons": [p1, q1],
                          "invert": inv, "jobs": J, "needs": [], "smoke": True, "est_minutes": 15})
    (OUT / "shards").mkdir(exist_ok=True)
    for s in shards:
        json.dump(s, open(OUT / "shards" / f"{s['shard']}.json", "w"), indent=0)
    tot = 0
    for s in shards:
        tot += s["est_minutes"]
        print(f"{s['shard']:28s} inv {len(s['invert']):3d} jobs {len(s['jobs']):4d} est {s['est_minutes']} min")
    print("SHARDS", len(shards), "est total", tot, "min")


if __name__ == "__main__":
    {"select": stage_select, "prep": stage_prep, "pair": stage_pair, "shards": stage_shards}[sys.argv[1]]()
