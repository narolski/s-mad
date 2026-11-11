"""PN1: stored-small (softened) copies of the DEVELOPMENT genuine camera photos, for the development threshold pools.
The image operation is the existing registered shrink-and-enlarge path, run unchanged: the functions load_pe() and
e7_branch() of the alpha-field probe's verified script /home/narolski/smad-next/src/AF0/soften.py (imported, not
copied, not edited; its sha256 is pinned below), which run smadcvpr/prep_eval.py (sha256 374408ab..., pinned there).
Only the output folder differs: /mnt/t7/smad_next/PN1/img/soft/<strength>/<id>_<strength>.png.

Sources (camera photos only, development persons only, prereg.md "Persons"):
  - development ladder hosts D: their R0 photo (AF0 list ar1.csv, cell frgcferet, rung R0)
  - AF0 validation-split photos of persons not in V (AF0 lists af0_w1 / af0_w2, cell val, rung photo)
Strengths: fm61 (61.2 px) and amsl112 (112.7 px), both for every source.
  python3 -I soften_dev.py list      # writes /mnt/t7/smad_next/PN1/lists/devsoft_src.csv
  python3 -I soften_dev.py build [--limit 8]
"""
import argparse
import csv
import hashlib
import importlib.util
import pathlib
import sys

AF0SRC = pathlib.Path("/home/narolski/smad-next/src/AF0/soften.py")
AF0SRC_SHA = None       # filled at first run into the log; checked against prereg-recorded value below
OUT = pathlib.Path("/mnt/t7/smad_next/PN1")
SPLIT = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split")
LISTS_AF0 = pathlib.Path("/mnt/t7/smad_next/AF0/lists")
FIELDS = ["id", "path", "set", "cell", "rung", "tool", "p1", "p2", "geom", "g1", "g2", "w1"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_soften():
    spec = importlib.util.spec_from_file_location("af0_soften", AF0SRC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def make_list():
    lad = {r["pid"]: r for r in csv.DictReader(open(SPLIT / "ladder_split.csv"))}
    af = {r["pid"]: r for r in csv.DictReader(open(SPLIT / "af0_split.csv"))}
    rows = []
    for r in csv.DictReader(open(LISTS_AF0 / "ar1.csv")):
        if r["cell"] == "frgcferet" and r["rung"] == "R0" and lad[r["p1"]]["role"] == "dev":
            rows.append(r)
    for n in ("af0_w1", "af0_w2"):
        for r in csv.DictReader(open(LISTS_AF0 / f"{n}.csv")):
            if r["cell"] == "val" and r["rung"] == "photo" and af[r["p1"]]["pn1_use"] == "dev":
                rows.append(r)
    (OUT / "lists").mkdir(parents=True, exist_ok=True)
    with open(OUT / "lists" / "devsoft_src.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print("devsoft_src rows", len(rows), "sha256", sha(OUT / "lists" / "devsoft_src.csv"))


def build(a):
    import cv2
    S = load_soften()
    print("AF0 soften.py sha256", sha(AF0SRC), "prep_eval pin", S.PE_SHA, flush=True)
    P = S.load_pe()
    rows = list(csv.DictReader(open(OUT / "lists" / "devsoft_src.csv")))[: a.limit or None]
    log = []
    for k, r in enumerate(rows):
        for st in ("fm61", "amsl112"):
            out = OUT / "img" / "soft" / st / f"{r['id']}_{st}.png"
            if out.exists():
                log.append((r["id"], st, str(out), "", "", ""))
                continue
            img, flag, nied, sc = S.e7_branch(P, cv2.imread(r["path"]), S.STRENGTHS[st])
            if img is None:
                log.append((r["id"], st, "", False, nied, sc))
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            assert cv2.imwrite(str(out), img)
            log.append((r["id"], st, str(out), flag, nied, sc))
        if (k + 1) % 50 == 0:
            print(k + 1, len(rows), flush=True)
    tag = f"_limit{a.limit}" if a.limit else ""
    with open(OUT / f"soft_devsoft_src{tag}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["src_id", "strength", "path", "aligned", "native_ied", "scale"])
        w.writerows(log)
    print("done", len(log), "failed", sum(1 for x in log if not x[2]), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("list", "build"))
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    make_list() if a.cmd == "list" else build(a)
