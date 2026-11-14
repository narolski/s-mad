"""AB1 pre-flight (infrastructure check, no image read): before any training starts, assert that every image path named
by the job's evaluation manifest and training manifest exists inside the pack tar or the overlay tar the job unpacks.
Exit 0 if all present, 1 otherwise (printing up to 10 missing paths). Uses tar listings only.
  python3 preflight.py --pack PACK.tar --overlay OVERLAY.tar --eval ab1_eval.csv --train train_SbFM.csv"""
import argparse
import csv
import io
import sys
import tarfile


def listing(path):
    with tarfile.open(path) as t:
        names = set()
        for m in t:
            names.add(m.name)
    return names


def read_member(paths, name):
    for p in paths:
        with tarfile.open(p) as t:
            for m in t:
                if m.name == name:
                    return t.extractfile(m).read().decode()
    raise SystemExit(f"PREFLIGHT FAIL: {name} not found in pack or overlay")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--overlay", required=True)
    ap.add_argument("--eval", required=True)
    ap.add_argument("--train", required=True)
    a = ap.parse_args()
    names = listing(a.pack) | listing(a.overlay)
    missing, n = [], 0
    for man in (a.eval, a.train):
        txt = read_member([a.overlay, a.pack], f"pn1/data/manifests/{man}")
        for r in csv.DictReader(io.StringIO(txt)):
            n += 1
            if f"pn1/data/{r['path']}" not in names:
                missing.append(r["path"])
    if missing:
        print(f"PREFLIGHT FAIL: {len(missing)} of {n} manifest paths missing, e.g. {missing[:10]}")
        sys.exit(1)
    print(f"PREFLIGHT OK: all {n} manifest paths present ({a.eval}, {a.train})")


if __name__ == "__main__":
    main()
