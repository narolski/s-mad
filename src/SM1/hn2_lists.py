"""SM1 H-n2 (DRAFT A18): lists for training the A11 m3 recipe on our own diffusion ladder (development data only).

DG1 add-on, 536 FRGC / colorFERET hosts in 8 shards of 67 hosts (`/mnt/t7/smad_next/FZ2/read_addon_items.csv`).
Train = shards addon_s0..s5, test = addon_s6, s7. Host sets are disjoint by shard; an X20 row is used only if its host
and its partner are on the same side (2 crossing X20 rows are dropped), so test hosts, test partners and their partner
cycles never occur in training.
  arm R  : attack X20 (two-person mix), genuine REC20 (one-person reconstruction)
  arm RS : attack X20, genuine REC20 + SAME20 (one-person mix; the only difference from X20 is the second person)
Training manifests: train.py columns (path,label,source,tool,arm,val,mixed; source smdd so regime d0 keeps every row).
Test manifest (ad4_eval columns id,path,set,family,label,variant,src_id): X20, SAME20, REC20 of the test shards.
Paths are "x/" + the absolute DGX path (unpacked under data/x on the machine).

  python3 -I hn2_lists.py -> OUT/hn2/{train_hn2R.csv, train_hn2RS.csv, sm1_hn2_test.csv, filelist_hn2.txt,
                             hn2_files.sha256, lists.json} and OUT/hn2/sm1_hn2_manifests.tar (+ .sha256)
"""
import csv
import hashlib
import json
import pathlib
import sys
import tarfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

G = pathlib.Path("/mnt/t7/smad_next/DG1/gen")
TRAIN, TEST = {f"addon_s{k}" for k in range(6)}, {"addon_s6", "addon_s7"}
COLS = ["path", "label", "source", "tool", "arm", "val", "mixed"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    od = K.OUT / "hn2"
    od.mkdir(parents=True, exist_ok=True)
    items = [r for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv"))
             if r["key"] in ("X20", "REC20", "SAME20")]
    side = {r["host"]: r["list"] for r in items}
    keep, dropped = [], []
    for r in items:
        h = "train" if side[r["host"]] in TRAIN else "test"
        if r["key"] == "X20":
            ps = "train" if side.get(r["partner"], "") in TRAIN else "test"
            if ps != h:
                dropped.append(r["id"])
                continue
        r["_side"] = h
        r["_path"] = str(G / r["list"] / r["id"])
        assert pathlib.Path(r["_path"]).exists(), r["_path"]
        keep.append(r)
    tr = [r for r in keep if r["_side"] == "train"]
    te = [r for r in keep if r["_side"] == "test"]
    assert not {r["host"] for r in tr} & {r["host"] for r in te}
    assert not {r["partner"] for r in tr if r["key"] == "X20"} & {r["host"] for r in te}
    info = dict(dropped_crossing_X20=dropped)
    for arm, gen in (("R", ("REC20",)), ("RS", ("REC20", "SAME20"))):
        rows = [dict(path="x" + r["_path"], label=1 if r["key"] == "X20" else 0, source="smdd", tool="dg1",
                     arm=f"hn2{arm}", val=0, mixed=0) for r in tr if r["key"] == "X20" or r["key"] in gen]
        f = od / f"train_hn2{arm}.csv"
        with open(f, "w", newline="") as fo:
            w = csv.DictWriter(fo, fieldnames=COLS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        info[f.name] = dict(n=len(rows), n_attack=sum(r["label"] == 1 for r in rows), sha256=sha(f))
    ev = [dict(id=f"hn2:{r['key']}:{r['host']}", path="x" + r["_path"], set="hn2test", family=r["key"],
               label=1 if r["key"] == "X20" else 0, variant="orig", src_id=r["host"]) for r in te]
    f = od / "sm1_hn2_test.csv"
    with open(f, "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(ev[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(ev)
    info[f.name] = dict(n=len(ev), per_family={k: sum(e["family"] == k for e in ev) for k in ("X20", "SAME20", "REC20")},
                        sha256=sha(f))
    files = sorted({r["_path"] for r in keep})
    (od / "filelist_hn2.txt").write_text("\n".join(files) + "\n")
    with open(od / "hn2_files.sha256", "w") as fo:
        for p in files:
            fo.write(f"{sha(p)}  {p.lstrip('/')}\n")
    info["files"] = len(files)
    json.dump(info, open(od / "lists.json", "w"), indent=1)
    tp = od / "sm1_hn2_manifests.tar"
    with tarfile.open(tp, "w") as t:
        for n in ("train_hn2R.csv", "train_hn2RS.csv", "sm1_hn2_test.csv", "hn2_files.sha256"):
            t.add(od / n, arcname=n)
    (od / (tp.name + ".sha256")).write_text(f"{sha(tp)}  {tp.name}\n")
    print(json.dumps({k: v for k, v in info.items() if k != "dropped_crossing_X20"}, indent=1), len(dropped))


if __name__ == "__main__":
    main()
