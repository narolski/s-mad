"""SM1 amendment A12 items 11 and 13: feature lists for the Athena pass (no image is read or written).

  train_armd5.csv   the 14,734 morphs of armd5 (item 11), as train_armd50.csv
  test_af0soft.csv  the protocol-network softened copies of AR1 frames (item 13; AF0 lists ar1soft.csv: R0 / R2w at
                    112.7 and 61.2 px, 200 hosts; ladsoft.csv: R4 / R3 (536 hosts) and R3m (200) at both strengths),
                    id "s:<AF0 id>", cell "af0soft:<rung>:<tool>:<strength>", base = the SM1 test_ar1 id of the
                    unsoftened image of the same host and rung ("ar1:<6 digits>"), label as AR1 (R4 = 1, else 0)
-> OUT/flists/{train_armd5,test_af0soft}.csv and OUT/gpupack/sm1gpu_lists_a12.tar (lists/<name>.csv, id + rel)
  python3 -I a12_flists.py
"""
import csv
import hashlib
import io
import pathlib
import sys
import tarfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

FL = K.OUT / "flists"
AF = pathlib.Path("/mnt/t7/smad_next/AF0/lists")


def write(name, rows):
    with open(FL / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(name, len(rows))


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    d5 = [dict(id=r["id"], path=r["out"], pair=r["id"], person=r["na"])
          for r in csv.DictReader(open(K.OUT / "lists/armd5.csv"))]
    assert all(pathlib.Path(r["path"]).exists() for r in d5)
    write("train_armd5.csv", d5)
    ar1 = {r["id"]: r for r in csv.DictReader(open(FL / "test_ar1.csv"))}
    rows = []
    for f in ("ar1soft.csv", "ladsoft.csv"):
        for r in csv.DictReader(open(AF / f)):
            rung, strength = r["rung"].split("_soft_")
            base = "ar1:" + r["id"].split("_")[1]
            b = ar1.get(base)
            assert b is not None and b["cell"] == f"ar1:frgcferet:{r['tool']}:{rung}", (r["id"], b and b["cell"])
            assert pathlib.Path(r["path"]).exists(), r["path"]
            rows.append(dict(id=f"s:{r['id']}", path=r["path"], cell=f"af0soft:{rung}:{r['tool']}:{strength}",
                             label=b["label"], hist=strength, p1=b["p1"], p2=b["p2"], expr="", base=base))
    write("test_af0soft.csv", rows)
    tp = K.OUT / "gpupack/sm1gpu_lists_a12.tar"
    with tarfile.open(tp, "w") as t:
        for name, rs in (("train_armd5", d5), ("test_af0soft", rows)):
            buf = io.StringIO()
            w = csv.DictWriter(buf, fieldnames=["id", "rel"], lineterminator="\r\n")
            w.writeheader()
            w.writerows([dict(id=r["id"], rel=r["path"].lstrip("/")) for r in rs])
            data = buf.getvalue().encode()
            ti = tarfile.TarInfo(f"./lists/{name}.csv")
            ti.size = len(data)
            t.addfile(ti, io.BytesIO(data))
    sha = hashlib.sha256(open(tp, "rb").read()).hexdigest()
    (tp.parent / (tp.name + ".sha256")).write_text(f"{sha}  {tp.name}\n")
    fl = K.OUT / "gpupack/filelist_a12.txt"
    fl.write_text("\n".join(sorted({r["path"] for r in d5 + rows})) + "\n")
    print(tp, sha, "files", len(d5) + len(rows))


if __name__ == "__main__":
    main()
