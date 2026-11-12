"""Competitor baselines on the corrected MAD22 and FRLL-Morphs (CB1): image list for scoring our CNN retrains.

Reads only existing, already-aligned 512-px frames (no image operation here). Writes one CSV:
  id, path (absolute), bench, family, label (1 = morph), pool, person_a, person_b
bench / pool:
  mad22c  native  corrected MAD22, canonical512 CPU-backend frames (204 genuine + 4,483 morphs)
  mad22c  e7      corrected MAD22 history-matched genuine pools (E7; 204 per morph family)
  frllm   native  FRLL-Morphs from eval.csv (old aligner): frll_bona orig (204) + 5 morph families orig
  frllm   e7      FRLL-Morphs history-matched genuine pools (eval.csv variant resmatch, 204 per family)
  gate    native  OLD MAD22 subset rows of eval.csv (185 + 4,069; orig) - only for the reproduction gate against the
  gate    e7      stored A12-BR / A45 numbers (resmatch rows); never a result row
Usage: python3 -I build_manifest.py OUT.csv
"""
import csv
import hashlib
import pathlib
import re
import sys

EVAL = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv")
EVAL_SHA = "86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9"
DATA = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")
MAD = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z")
FAM = ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")
COUNTS = {"BonaFide": 204, "FaceMorpher": 1000, "MIPGAN_I": 1000, "MIPGAN_II": 999, "OpenCV": 984, "Webmorph": 500}
PID = re.compile(r"(\d{3})_\d{2}")


def persons(name):
    p = PID.findall(name)
    return (p[0], p[1] if len(p) > 1 else p[0]) if p else ("", "")


def main(out):
    assert hashlib.sha256(EVAL.read_bytes()).hexdigest() == EVAL_SHA, "eval.csv changed"
    rows = []
    for fam, n in COUNTS.items():
        files = sorted((MAD / "native" / fam).glob("*.png"))
        assert len(files) == n, (fam, len(files))
        for f in files:
            a, b = persons(f.stem)
            rows.append(dict(id=f"mad22c/native/{fam}/{f.stem}", path=str(f), bench="mad22c",
                             family="bona" if fam == "BonaFide" else fam, label=int(fam != "BonaFide"),
                             pool="native", person_a=a, person_b=b))
    for fam in FAM:
        files = sorted((MAD / "e7" / fam).glob("*.png"))
        assert len(files) == 204, (fam, len(files))
        for f in files:
            a, b = persons(f.stem)
            rows.append(dict(id=f"mad22c/e7/{fam}/{f.stem}", path=str(f), bench="mad22c", family=fam, label=0,
                             pool="e7", person_a=a, person_b=b))
    for r in csv.DictReader(open(EVAL)):
        s, fam, var = r["set"], r["family"], r["variant"]
        if s not in ("frllm", "mad22"):
            continue
        bench = "frllm" if s == "frllm" else "gate"
        if var == "orig":
            pool = "native"
            family = "bona" if fam in ("frll_bona", "mad22_bona") else fam
        elif var == "resmatch":
            pool, family = "e7", fam
        else:
            continue
        a, b = persons(pathlib.Path(r["path"]).stem)
        rows.append(dict(id=f"{bench}/{pool}/{r['id']}", path=str(DATA / r["path"]), bench=bench, family=family,
                         label=int(r["label"]), pool=pool, person_a=a, person_b=b))
    for r in rows:
        assert pathlib.Path(r["path"]).is_file(), r["path"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    for k, v in sorted(Counter((r["bench"], r["pool"], r["family"], r["label"]) for r in rows).items()):
        print(*k, v)
    print("rows", len(rows), "sha256", hashlib.sha256(pathlib.Path(out).read_bytes()).hexdigest())


if __name__ == "__main__":
    main(sys.argv[1])
