"""D2: NIST MEDS cross-encounter genuine pairs (ids only; lead's go 13 Nov 2026).

Every pair of aligned MEDS images of one person from different encounters, from the TT1-M manifest
(/mnt/t7/smad_next/TT1/meds/meds_manifest.csv). No image is opened or changed. The list stays on /mnt/t7
(NIST terms: no file name or identifier in the repository); only counts are printed and committed.

  python3 -I d2_meds_pairs.py  -> /mnt/t7/smad_next/DATA/D2/meds_cross_encounter_pairs.csv (+ .sha256), counts JSON
"""
import collections
import csv
import hashlib
import itertools
import json
import pathlib

SRC = pathlib.Path("/mnt/t7/smad_next/TT1/meds/meds_manifest.csv")
OUT = pathlib.Path("/mnt/t7/smad_next/DATA/D2")
REPO = pathlib.Path("/home/narolski/smad-next/experiments/DATA_builds/D2_counts.json")

rows = [r for r in csv.DictReader(open(SRC)) if r["aligned"] == "1"]
by = collections.defaultdict(list)
for r in rows:
    by[r["person"]].append(r)
pairs = []
for person, v in sorted(by.items()):
    for a, b in itertools.combinations(sorted(v, key=lambda x: x["id"]), 2):
        if a["encounter"] != b["encounter"]:
            pairs.append(dict(id_a=a["id"], id_b=b["id"], person=person, part_a=a["part"], part_b=b["part"],
                              encounter_a=a["encounter"], encounter_b=b["encounter"],
                              ied_src_a=a["ied_src"], ied_src_b=b["ied_src"],
                              border_frac_a=a["border_frac"], border_frac_b=b["border_frac"],
                              aligned_sha256_a=a["aligned_sha256"], aligned_sha256_b=b["aligned_sha256"]))
OUT.mkdir(parents=True, exist_ok=True)
p = OUT / "meds_cross_encounter_pairs.csv"
with open(p, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(pairs[0].keys()))
    w.writeheader()
    w.writerows(pairs)
h = hashlib.sha256(p.read_bytes()).hexdigest()
(OUT / "meds_cross_encounter_pairs.csv.sha256").write_text(f"{h}  {p.name}\n")
per = collections.Counter(x["person"] for x in pairs)
imgs = {x["id_a"] for x in pairs} | {x["id_b"] for x in pairs}
counts = dict(source_manifest_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(), aligned_images=len(rows),
              aligned_persons=len(by), persons_with_pairs=len(per), images_in_pairs=len(imgs), pairs=len(pairs),
              pairs_per_person_max=max(per.values()), pairs_per_person_median=sorted(per.values())[len(per) // 2],
              cross_part_pairs=sum(x["part_a"] != x["part_b"] for x in pairs), list_sha256=h)
json.dump(counts, open(OUT / "counts.json", "w"), indent=1)
json.dump(counts, open(REPO, "w"), indent=1)
print(json.dumps(counts))
