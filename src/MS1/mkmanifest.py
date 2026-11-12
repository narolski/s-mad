"""MS1: multi-source training manifest (prereg part 1, section 5).

Unique rows of train_Sb (FS1 pack, sha256 2cf3fda3...) + the FFHQ training images (and later any further source added
with --sources), class balance per stratum database x storage history with src/PN1/mkmanifests.py `balanced`
(imported unchanged). Sb's four strata keep their original seeds (20261111 + index in Sb's sorted strata), new strata
j (sorted) get 20261111 + 100 + j, so the FRGC / colorFERET rows equal train_Sb's rows (checked as a multiset).
  python3 -I mkmanifest.py [--name SbM3] [--sources ffhq]
-> OUT/manifests/train_<name>.csv, OUT/manifests/<name>_files.csv (pack path -> source file), <name>_summary.json
"""
import argparse
import collections
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ms1common as C  # noqa: E402

SB = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv")
SB_SHA = "2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a"
TRCOLS = ["path", "label", "source", "tool", "arm", "val", "mixed", "id", "kind", "db", "hist"]


def ffhq_rows():
    O = C.OUT / "ffhq"
    out = []

    def add(iid, src, kind, label, hist):
        assert pathlib.Path(src).exists(), src
        out.append(dict(id=iid, src=src, kind=kind, label=label, db="ffhq", hist=hist))

    persons = list(csv.DictReader(open(O / "persons.csv")))
    for i, p in enumerate([p for p in persons if p["part"] == "af0"]):
        add(f"train_ffhq_photo_{i:04d}", p["frame"], "af0_photo", "0", "native")
    for r in csv.DictReader(open(O / "lists/af0_pairs.csv")):
        if r["split"] == "train":
            add(r["id"], r["image"], "af0_" + r["field"], "1" if r["field"] == "u50" else "0", "native")
    for h in csv.DictReader(open(O / "lists/halves.csv")):
        if h["split"] == "train":
            add(h["id"], h["path"], "af0_half", "0", "native")
    soft = {(r["src_id"], r["strength"]): r for r in csv.DictReader(open(O / "soft_log.csv"))}
    for r in csv.DictReader(open(O / "lists/soft.csv")):
        if r["split"] != "train" or r["strength"] != "fm61":
            continue
        s = soft.get((r["src_id"], "fm61"))
        if s is None or s["aligned"] == "False" or not pathlib.Path(r["out"]).exists():
            continue                                    # re-alignment failed: dropped and counted in the summary
        kind = {"photo": "af0_photo61", "u50": "af0_u5061", "half": "af0_half61"}[r["kind"]]
        add(f"{r['src_id']}_fm61", r["out"], kind, "1" if r["kind"] == "u50" else "0", "s61")
    for r in csv.DictReader(open(O / "lists/ladder.csv")):
        s = r["pid"].replace(":", "_")
        add(f"lad_{s}_R0", r["H"], "lad_R0", "0", "native")
        add(f"lad_{s}_R4", r["R4"], "lad_R4", "1", "native")
        add(f"lad_{s}_hA", r["hA"], "lad_half", "0", "native")
        add(f"lad_{s}_hB", r["hB"], "lad_half", "0", "native")
    return out


SOURCES = {"ffhq": ffhq_rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="SbM3")
    ap.add_argument("--sources", default="ffhq")
    a = ap.parse_args()
    MM = C.load(C.SRC / "PN1/mkmanifests.py", "pn1mk")
    assert C.sha(SB) == SB_SHA
    sb = list(csv.DictReader(open(SB)))
    uniq = {}
    for r in sb:
        uniq.setdefault(r["id"], r)
    old = sorted({(r["db"], r["hist"]) for r in uniq.values()})
    assert old == [("feret", "native"), ("feret", "s61"), ("frgc", "native"), ("frgc", "s61")], old
    rows = list(uniq.values())
    files = {}
    new = []
    for s in a.sources.split(","):
        for r in SOURCES[s]():
            pp = f"train/{r['kind']}/{r['id']}.png"
            assert pp not in files and r["id"] not in uniq, pp
            assert not C.forbidden(r["src"])
            files[pp] = r["src"]
            new.append(dict(path=pp, label=r["label"], source="smdd", tool="smdd", arm="smdd", val="0", mixed="0",
                            id=r["id"], kind=r["kind"], db=r["db"], hist=r["hist"]))
    out, rep = [], {}
    for i, st in enumerate(old):
        rs = [r for r in rows if (r["db"], r["hist"]) == st]
        b, _, _ = MM.balanced(rs, seed=20261111 + i)
        out += b
        rep["|".join(st)] = dict(unique_neg=sum(r["label"] == "0" for r in rs), unique_att=sum(r["label"] == "1" for r in rs),
                                 rows=len(b), seed=20261111 + i)
    nst = sorted({(r["db"], r["hist"]) for r in new})
    for j, st in enumerate(nst):
        rs = [r for r in new if (r["db"], r["hist"]) == st]
        n0, n1 = sum(r["label"] == "0" for r in rs), sum(r["label"] == "1" for r in rs)
        if n0 == 0 or n1 == 0:
            raise SystemExit(f"stratum {st} has one class only ({n0}, {n1})")
        b, _, _ = MM.balanced(rs, seed=20261111 + 100 + j)
        out += b
        rep["|".join(st)] = dict(unique_neg=n0, unique_att=n1, rows=len(b), seed=20261111 + 100 + j)
    key = lambda r: tuple(r[c] for c in TRCOLS)          # noqa: E731
    sb_part = collections.Counter(key(r) for r in out if r["db"] in ("frgc", "feret"))
    assert sb_part == collections.Counter(key(r) for r in sb), "FRGC / colorFERET rows differ from train_Sb"
    M = C.OUT / "manifests"
    M.mkdir(parents=True, exist_ok=True)
    mf = M / f"train_{a.name}.csv"
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=TRCOLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    C.write_csv(M / f"{a.name}_files.csv", [dict(pack_path=k, source=v, sha256=C.sha(v)) for k, v in sorted(files.items())])
    summ = dict(name=a.name, rows=len(out), unique=len(rows) + len(new), sb_rows_equal=True, strata=rep,
                by_db_kind={f"{d}/{k}": n for (d, k), n in sorted(collections.Counter((r["db"], r["kind"]) for r in
                                                                                     rows + new).items())},
                sha256=C.sha(mf), files_sha256=C.sha(M / f"{a.name}_files.csv"), mkmanifests_sha256=C.sha(C.SRC / "PN1/mkmanifests.py"))
    json.dump(summ, open(C.RES / f"manifest_{a.name}_summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "by_db_kind"}, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
