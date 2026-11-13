"""D5: border- and resolution-balanced genuine selection lists (selection only; no image opened or changed).

Sources with per-frame border fraction and source eye distance already recorded by their owners:
  TT1 unseen genuine   /mnt/t7/smad_next/TT1/aligned_manifest.csv   (aligned = 1 rows only)
  TT1-M NIST MEDS      /mnt/t7/smad_next/TT1/meds/meds_manifest.csv (aligned = 1 rows only; restricted terms)
Cells: border  none (border_frac == 0) / any (> 0)  x  source eye distance  < 61.2 / 61.2-112.7 / >= 112.7 px
(the two storage sizes of the protocol). Balanced list: in every non-empty cell the same number of images, at most
one image per person per cell, seeded draw (seed 20261113). The cap is the smallest non-empty cell.
Two lists: all sources, and without MEDS (so a reader can use it without the NIST terms).
Version 2 (13 Nov, lead's go): adds the MS1 FFHQ, CelebA-HQ and AR1 / AF0 genuine frames measured by
d5_measure_border.py (border only: their source eye distance is in no existing record). Design "bied" = border x eye
distance (rows with a recorded eye distance only); design "border" = border none / any over every source.
Version 3 (13 Nov, lead's go): source eye distance measured for those frames (d5_measure_ied.py, detection only);
the pooled border x eye-distance lists now include them, and "biedstrat" lists balance cells within each source.
Lists stay on /mnt/t7 (MEDS ids); the repository gets the cell table only.

  python3 -I d5_balanced_genuine.py
"""
import collections
import csv
import hashlib
import json
import pathlib
import random

OUT = pathlib.Path("/mnt/t7/smad_next/DATA/D5")
REPO = pathlib.Path("/home/narolski/smad-next/experiments/DATA_builds/D5_cells.json")
SRC = {"tt1": pathlib.Path("/mnt/t7/smad_next/TT1/aligned_manifest.csv"),
       "meds": pathlib.Path("/mnt/t7/smad_next/TT1/meds/meds_manifest.csv")}


def cell(r, design="bied"):
    b = "none" if float(r["border_frac"]) == 0 else "any"
    if design == "border":
        return f"border_{b}"
    e = float(r["ied_src"])
    q = "lt61" if e < 61.2 else ("61to113" if e < 112.7 else "ge113")
    return f"border_{b}|ied_{q}"


items = []
for name, p in SRC.items():
    for r in csv.DictReader(open(p)):
        if r["aligned"] != "1" or r["border_frac"] in ("", "nan") or r["ied_src"] in ("", "nan"):
            continue
        fam = r.get("family") or "meds"
        person = r["person"] if name == "tt1" else "meds:" + r["person"]
        items.append(dict(id=r["id"], source=name, family=fam, person=person, role="development",
                          border_frac=r["border_frac"], ied_src=r["ied_src"], path=r["aligned_path"],
                          sha256=r["aligned_sha256"]))
MEAS = OUT / "frames_ied.csv"   # version 3: frames_measured.csv + source eye distance (d5_measure_ied.py)
for r in csv.DictReader(open(MEAS)):
    if r["border_frac"] == "":
        continue
    items.append(dict(id=pathlib.Path(r["path"]).stem, source=r["source"], family=r["source"], person=r["person"],
                      role=r["role"], border_frac=r["border_frac"], ied_src=r["ied_src"], path=r["path"], sha256=""))
MIN_STRAT = 20


def one_per_person(v, rng):
    v = sorted(v, key=lambda x: (x["source"], x["id"]))
    rng.shuffle(v)
    seen, keep = set(), []
    for it in v:
        if it["person"] not in seen:
            seen.add(it["person"])
            keep.append(it)
    return keep


def stratified(pool, tag):
    """Within each source: equal counts over the cells in which that source has >= MIN_STRAT persons."""
    pool = [dict(it, cell=cell(it, "bied")) for it in pool if it["ied_src"] != ""]
    tag = f"biedstrat_{tag}"
    rng = random.Random(20261113)
    by = collections.defaultdict(list)
    for it in pool:
        by[(it["source"], it["cell"])].append(it)
    avail = {k: one_per_person(v, rng) for k, v in sorted(by.items())}
    out, caps = [], {}
    for src in sorted({k[0] for k in avail}):
        cells = {c: v for (s_, c), v in avail.items() if s_ == src and len(v) >= MIN_STRAT}
        if len(cells) < 2:
            caps[src] = dict(cap=0, cells=sorted(cells), note="fewer than 2 cells with >= 20 persons: not used")
            continue
        cap = min(len(v) for v in cells.values())
        caps[src] = dict(cap=cap, cells=sorted(cells))
        for c in sorted(cells):
            out += [dict(it, list=tag) for it in cells[c][:cap]]
    p = OUT / f"genuine_balanced_{tag}.csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    (OUT / f"genuine_balanced_{tag}.csv.sha256").write_text(f"{h}  {p.name}\n")
    table = collections.defaultdict(dict)
    for (s_, c), v in avail.items():
        table[s_][c] = len(v)
    sel = collections.defaultdict(lambda: collections.Counter())
    for it in out:
        sel[it["source"]][it["cell"]] += 1
    return dict(min_persons_per_cell=MIN_STRAT, persons_available_by_source_cell=dict(table), caps=caps,
                selected_by_source_cell={k: dict(v) for k, v in sel.items()}, rows=len(out), list_sha256=h)


def balanced(pool, tag, design):
    pool = [dict(it, cell=cell(it, design)) for it in pool if design == "border" or it["ied_src"] != ""]
    tag = f"{design}_{tag}"
    rng = random.Random(20261113)
    by = collections.defaultdict(list)
    for it in pool:
        by[it["cell"]].append(it)
    picked = {}
    for c, v in sorted(by.items()):
        v = sorted(v, key=lambda x: x["id"])
        rng.shuffle(v)
        seen, keep = set(), []
        for it in v:
            if it["person"] not in seen:
                seen.add(it["person"])
                keep.append(it)
        picked[c] = keep
    cap = min(len(v) for v in picked.values())
    out = [dict(it, list=tag) for c in sorted(picked) for it in picked[c][:cap]]
    p = OUT / f"genuine_balanced_{tag}.csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    (OUT / f"genuine_balanced_{tag}.csv.sha256").write_text(f"{h}  {p.name}\n")
    bys = collections.defaultdict(lambda: collections.Counter())
    for it in out:
        bys[it["source"]][it["cell"]] += 1
    return dict(available_images=dict(collections.Counter(it["cell"] for it in pool)),
                selected_by_source_cell={k: dict(v) for k, v in bys.items()},
                one_per_person=dict((c, len(v)) for c, v in picked.items()), per_cell=cap, rows=len(out),
                by_source=dict(collections.Counter(it["source"] for it in out)), list_sha256=h)


OUT.mkdir(parents=True, exist_ok=True)
SRC["measured"] = MEAS
nomeds = [i for i in items if i["source"] != "meds"]
res = dict(version=3, seed=20261113, sources={k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in SRC.items()},
           bied_all_sources=balanced(items, "all", "bied"), bied_without_meds=balanced(nomeds, "nomeds", "bied"),
           border_all_sources=balanced(items, "all", "border"), border_without_meds=balanced(nomeds, "nomeds", "border"),
           bied_stratified_all_sources=stratified(items, "all"), bied_stratified_without_meds=stratified(nomeds, "nomeds"))
json.dump(res, open(OUT / "cells.json", "w"), indent=1)
json.dump(res, open(REPO, "w"), indent=1)
print(json.dumps(res, indent=1))
