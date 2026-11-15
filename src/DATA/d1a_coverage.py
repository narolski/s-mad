"""D1a: paired-control coverage table (lists only; no image is opened).

For each positive family (two-person morph tool(A, B)) count the hosts A that also have, from the same pipeline:
  same  = same-person morph tool(A, A')
  warp  = warp-only image (A's texture warped toward a mean shape)
  one   = one-photo render tool(A, A) or reconstruction of A alone
Host-matched for the AR1 ladder, AG1 MIPGAN and DG1 DiffAE. For the AF0 fields, splices and MS1 FFHQ the training
manifests carry no common host key across kinds, so counts are per kind (marked host_matched = no).
Closed-benchmark rows (FRLL persons) are left out. Person roles from the PN1 split files (never valx).

  python3 -I d1a_coverage.py   -> /mnt/t7/smad_next/DATA/D1a/coverage.csv and experiments/DATA_builds/D1a_coverage.csv
"""
import collections
import csv
import pathlib

R = pathlib.Path("/home/narolski/smad-next")
T7 = pathlib.Path("/mnt/t7/smad_next")
OUT = T7 / "DATA/D1a"
role = {r["pid"]: r["role"] for r in csv.DictReader(open(R / "experiments/PN1_protocol-network-first-tests/split/ladder_split.csv"))}
rows = []


def matched(fam, engine, db_of, hosts_by_rung, two, same, warp, one, note=""):
    by = collections.defaultdict(lambda: collections.Counter())
    for h in hosts_by_rung.get(two, set()):
        k = (db_of(h), role.get(h.replace("_", ":", 1), "not_in_ladder_split"))
        by[k]["two"] += 1
        for name, rg in (("same", same), ("warp", warp), ("one", one)):
            if rg and h in hosts_by_rung.get(rg, set()):
                by[k][name] += 1
    for (db, rl), c in sorted(by.items()):
        rows.append(dict(family=fam, engine=engine, db=db, role=rl, host_matched="yes", two_person=c["two"],
                         same_person=c["same"] if same else "n/a", warp_only=c["warp"] if warp else "n/a",
                         one_photo=c["one"] if one else "n/a", rungs=f"{two} / {same} / {warp} / {one}", note=note))


# AR1 landmark ladder (frgcferet pool only; frll pools are closed)
ar = collections.defaultdict(lambda: collections.defaultdict(set))
for r in csv.DictReader(open(T7 / "AR1/manifest.csv")):
    if r["pool"] == "frgcferet":
        ar[r["tool"]][r["rung"]].add(r["p1"])
for tool in ("opencv", "facemorpher"):
    matched("landmark ladder (AR1)", tool, lambda h: h.split(":")[0], ar[tool], "R4", "R3", "R2w4", "R2",
            note="R2 equals R0 for OpenCV; R2w (warp toward own second photo) also exists for every host")

# AG1 MIPGAN (FERET / FRGC only)
ag = collections.defaultdict(lambda: collections.defaultdict(set))
for r in csv.DictReader(open(T7 / "AG1/data/manifests/ag1.csv")):
    if r["db"] in ("feret", "frgc") and r["gen"] in ("mip1", "mip2"):
        ag[r["gen"]][r["rung"]].add(r["pa"].replace("_", ":", 1))
for g in sorted(ag):
    matched("MIPGAN (AG1)", g, lambda h: h.split(":")[0], ag[g], "R4", "R3", None, "R2",
            note="no warp-only rung exists for a GAN pipeline; R2i and R3m also exist")

# DG1 DiffAE set B
dg = collections.defaultdict(set)
for r in csv.DictReader(open(R / "experiments/DG1_diffusion-generation-athena/validity/setB_manifest.csv")):
    dg[r["rung"]].add(r["host"])
matched("DiffAE (DG1 set B)", "diffae", lambda h: h.split(":")[0], dg, "X", "SAME", None, "REC",
        note="MIR (mirror self-morph) also exists")

# per-kind counts from the Sb-family training manifest (AB1 train_SbZ = Sb rows) and MS1 FFHQ
kinds = collections.Counter()
for r in csv.DictReader(open(T7 / "AB1/manifests/train_SbZ.csv")):
    kinds[r["kind"]] += 1
rows.append(dict(family="AF0 morph fields", engine="af0", db="frgc+feret", role="train", host_matched="no",
                 two_person=f"af0_u50 rows {kinds['af0_u50']}", same_person="SE1 self-morphs (mirror partner) 644 images, outside Sb",
                 warp_only="af0_zero (not in Sb rows); halves af0_half rows " + str(kinds["af0_half"]),
                 one_photo="none built", rungs="u50 / selfm / zero, half / -", note="rows of train_SbZ (repetitions included)"))
rows.append(dict(family="face splices", engine="opencv hull (amendment 7b)", db="frgc+feret", role="train", host_matched="no",
                 two_person=f"lad_S4 rows {kinds['lad_S4']}", same_person=f"lad_S3 rows {kinds['lad_S3']}",
                 warp_only="n/a", one_photo=f"lad_S0 rows {kinds['lad_S0']}", rungs="S4 / S3 / - / S0",
                 note="no FaceMorpher splices (D1c, author)"))
d1d = sum(1 for _ in open(T7 / "DATA/D1d/SHA256SUMS"))
rows.append(dict(family="MS1 FFHQ ladder", engine="opencv", db="ffhq", role="train+hold", host_matched="no",
                 two_person="lad_R4 150 (training)", same_person="none (one photo per person)",
                 warp_only="R2w4 (built with R4)", one_photo="OpenCV R2 = R0 (identity)",
                 rungs="R4 / - / R2w4 / R0", note=f"D1d FaceMorpher one-photo renders {d1d} exist, but no FaceMorpher FFHQ two-person morphs exist yet"))

OUT.mkdir(parents=True, exist_ok=True)
keys = list(rows[0].keys())
for p in (OUT / "coverage.csv", R / "experiments/DATA_builds/D1a_coverage.csv"):
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
for r in rows:
    print(r["family"], r["engine"], r["db"], r["role"], r["two_person"], r["same_person"], r["warp_only"], r["one_photo"], sep=" | ")
