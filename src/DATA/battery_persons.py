"""Battery data requests (experiments/BATTERY_shared-test-battery/MISSING_DATA.md), lists only, CPU, no image opened.

(1) Person and source table per battery set (dev, tt1, meds, gd; manifests pinned in src/battery/sets.py, checked here
    against the same sha256): per set, family and rung, the row count, distinct persons and the person sources.
    Person lists per set: /mnt/t7/smad_next/DATA/battery/persons_<set>.csv (MEDS ids stay on /mnt/t7); counts in git.
(2) GD host overlap: the persons in every row of the GD set (host, plus the partner of a two-person row) against the
    training persons of every arm's training manifest. Training persons are resolved from row ids through the
    builders' own lists (AR1 manifest p1/p2, AF0 manifest pid_A/pid_B, MS1 FFHQ lists, PN1 ladder split partners);
    halves carry only their own side's person. GX1's selected training persons (select.json, no manifest yet) are
    checked as a planned arm. Unresolved row ids are counted and printed.

  python3 -I battery_persons.py
"""
import collections
import csv
import glob
import hashlib
import json
import pathlib
import re

T7 = pathlib.Path("/mnt/t7/smad_next")
R = pathlib.Path("/home/narolski/smad-next")
OUT = T7 / "DATA/battery"
SETS = {
    "dev": ("/mnt/t7/smad_next/AB1/overlay_tree/pn1/data/manifests/ab1_eval.csv", "93a5ba234f91e57951829c5536fabbe0f792ee4ad0a293f074aaca72f7465bd5"),
    "tt1": ("/mnt/t7/smad_next/TT1/pack_tree/tt1/data/manifests/tt1_score.csv", "c0055b51467cf8d001d56cbc4689706d68f0bf35c64066b1ba49fada5cb45761"),
    "meds": ("/mnt/t7/smad_next/TT1/meds/pack_tree/tt1m/data/manifests/meds_score.csv", "9093d5d5425e1d031f5f940e15321a6371cb0fe6a5d2014aabc404ba4543415a"),
    "gd": ("/mnt/t7/smad_next/PR1/pr1_gd_tree/pr1g/data/manifests/pr1_gd.csv", "3577a91351131b104457424054c29ca3c6f3fc59666e9204598e45e608e15157"),
}
DENY = re.compile(r"valx|fst|a12sp|a12-sp", re.I)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def norm(h):
    """person ids as db:subject; FFHQ-Morphs keys 'AAAAA_BBBBB' -> two FFHQ persons."""
    if ":" in h:
        return [h]
    if re.fullmatch(r"\d{5}_\d{5}", h):
        a, b = h.split("_")
        return [f"ffhq:{a}", f"ffhq:{b}"]
    if re.fullmatch(r"\d{5}", h):
        return [f"ffhq:{h}"]
    m = re.fullmatch(r"(feret|frgc)_(\d+)", h)
    if m:
        return [f"{m.group(1)}:{m.group(2)}"]
    return [h]


# ---------------- (1) person and source table
OUT.mkdir(parents=True, exist_ok=True)
sets = {}
table = []
for name, (p, pin) in SETS.items():
    assert not DENY.search(p)
    assert sha(p) == pin, (name, "manifest off its pin")
    rows = list(csv.DictReader(open(p)))
    sets[name] = rows
    g = collections.defaultdict(lambda: dict(rows=0, persons=set(), sources=collections.Counter()))
    for r in rows:
        k = (r.get("fam", ""), r.get("rung", ""), r.get("cell", ""), r.get("label", ""))
        g[k]["rows"] += 1
        for q in norm(r.get("host", "")):
            g[k]["persons"].add(q)
            g[k]["sources"][q.split(":")[0] if ":" in q else "unlabelled"] += 1
    allp = collections.defaultdict(set)
    for (fam, rung, cellv, lab), v in sorted(g.items()):
        table.append(dict(set=name, fam=fam, rung=rung, cell=cellv, label=lab, rows=v["rows"], persons=len(v["persons"]),
                          person_sources=";".join(f"{s}:{n}" for s, n in sorted(v["sources"].items()))))
        for q in v["persons"]:
            allp[q].add(f"{fam}/{rung}")
    with open(OUT / f"persons_{name}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["person", "source", "cells"])
        for q in sorted(allp):
            w.writerow([q, q.split(":")[0] if ":" in q else "unlabelled", ";".join(sorted(allp[q]))])
with open(R / "experiments/DATA_builds/battery_person_source.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(table[0].keys()))
    w.writeheader()
    w.writerows(table)

# ---------------- (2) training persons per arm
ar1 = {}
for f in sorted(glob.glob(str(T7 / "AR1/manifest*.csv"))):
    if "soft" in f or "swap" in f:
        continue
    for r in csv.DictReader(open(f)):
        if "p1" in r and r["p1"]:
            ar1[r["id"]] = {r["p1"], r["p2"]}
af0 = {r["id"]: (r["pid_A"], r["pid_B"]) for r in csv.DictReader(open(T7 / "AF0/manifest.csv"))}
for r in csv.DictReader(open(T7 / "MS1/ffhq/lists/af0_pairs.csv")):
    af0[r["id"]] = (r["pid_A"], r["pid_B"])
for r in csv.DictReader(open(T7 / "MS1/ffhq/lists/soft.csv")):
    af0.setdefault(r["src_id"], (r["pid"], r["pid"]))
ms1lad = {r["pid"]: r["B_pid"] for r in csv.DictReader(open(T7 / "MS1/ffhq/lists/ladder.csv"))}
partner = {r["pid"]: r["partner_B"] for r in
           csv.DictReader(open(R / "experiments/PN1_protocol-network-first-tests/split/ladder_split.csv"))}


def persons_of(i):
    b = re.sub(r"(__bd|_jpeg\d+|_fm\d+|_amsl\d+|_selfm)+$", "", i)
    m = re.fullmatch(r"ar1_(\d+)", b)
    if m:
        return ar1.get(m.group(1))
    m = re.fullmatch(r"sm1h_(feret|frgc)_(\d+)_h([AB])", b)
    if m:
        h = f"{m.group(1)}:{m.group(2)}"
        return {h} if m.group(3) == "A" else ({partner[h]} if h in partner else None)
    m = re.fullmatch(r"sp2_S(\d)_opencv_(feret|frgc)_(\d+)", b)
    if m:
        h = f"{m.group(2)}:{m.group(3)}"
        if m.group(1) == "4":
            return {h, partner[h]} if h in partner else None
        return {h}
    m = re.fullmatch(r"lad_ffhq_(\d+)_(R\d+w?\d*|hA|hB)", b)
    if m:
        h = f"ffhq:{m.group(1)}"
        t = m.group(2)
        if t == "hA" or t == "R0":
            return {h}
        return {ms1lad[h]} if t == "hB" else {h, ms1lad[h]}
    m = re.fullmatch(r"(train_\w+?_\d+)_half([AB])", b)
    if m and m.group(1) in af0:
        return {af0[m.group(1)][0 if m.group(2) == "A" else 1]}
    if b in af0:
        return set(af0[b])
    return None


arms = {}
unres = {}
for f in sorted(glob.glob(str(T7 / "PN1/manifests/train_*.csv")) + glob.glob(str(T7 / "AB1/manifests/train_*.csv")) +
                glob.glob(str(T7 / "AB1/*/manifests/train_*.csv")) + glob.glob(str(T7 / "MS1/manifests/train_*.csv")) +
                glob.glob(str(T7 / "SE1/manifests/train_*.csv"))):
    if DENY.search(f):
        continue
    arm = pathlib.Path(f).stem.replace("train_", "")
    ps, bad = set(), collections.Counter()
    for r in csv.DictReader(open(f)):
        q = persons_of(r["id"])
        if q is None:
            bad[re.sub(r"\d+", "N", r["id"])] += 1
        else:
            ps |= q
    arms[f"{arm} ({pathlib.Path(f).relative_to(T7)})"] = ps
    unres[arm] = dict(bad)
gx = json.load(open(T7 / "GX1/inputs/select.json"))
arms["GX1 planned (GX1/inputs/select.json, group train)"] = {norm(x["person"])[0] for x in gx if x.get("group") == "train"}

ag1 = {}
for r in csv.DictReader(open(T7 / "AG1/data/manifests/ag1.csv")):
    ag1[(r["db"], r["rung"], r["pa"])] = r["pb"]
dg = {}
for r in csv.DictReader(open(R / "experiments/DG1_diffusion-generation-athena/validity/setB_manifest.csv")):
    dg[(r["rung"], r["host"])] = r["partner"]
gdrows = []
for r in sets["gd"]:
    host = set(norm(r["host"]))
    full = set(host)
    if r["fam"] == "gd1" and r["rung"] in ("X",):
        pt = dg.get(("X", r["host"]), "")
        if pt:
            full.add(pt)
    if r["fam"] == "gd2" and r["rung"] == "R4":
        db, s = r["host"].split(":")
        pb = ag1.get((db, "R4", f"{db}_{s}"), "")
        if pb:
            full |= set(norm(pb))
    gdrows.append((r["fam"], r["rung"], host, full))
ov = []
for arm, ps in arms.items():
    for fam in sorted({x[0] for x in gdrows}):
        rr = [x for x in gdrows if x[0] == fam]
        ov.append(dict(arm=arm, training_persons=len(ps), gd_family=fam, gd_rows=len(rr),
                       rows_host_in_training=sum(bool(x[2] & ps) for x in rr),
                       rows_any_person_in_training=sum(bool(x[3] & ps) for x in rr),
                       gd_persons_in_training=len(set().union(*[x[3] for x in rr]) & ps)))
with open(R / "experiments/DATA_builds/gd_overlap.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(ov[0].keys()))
    w.writeheader()
    w.writerows(ov)
summ = dict(manifests={k: v[1] for k, v in SETS.items()}, unresolved_ids_per_arm=unres,
            table_sha256=sha(R / "experiments/DATA_builds/battery_person_source.csv"),
            overlap_sha256=sha(R / "experiments/DATA_builds/gd_overlap.csv"))
json.dump(summ, open(R / "experiments/DATA_builds/battery_persons_summary.json", "w"), indent=1)
print(json.dumps(summ, indent=1))
for o in ov:
    if o["rows_any_person_in_training"]:
        print("OVERLAP", o)
