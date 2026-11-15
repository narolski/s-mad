"""PN1 amendment 8: lists of the spliced images (AF0 list format) and of the blanked copies used by the reads.
  python3 -I splice_lists.py   -> /mnt/t7/smad_next/PN1/lists/{splice_nat,splice_blank}.csv
splice_nat: S0, S3, S4 natives, both tools, all 536 hosts. splice_blank: test hosts only, OpenCV-style engine: S0, S3,
S4, R2w, R2w4 face-blanked / face-only copies (R4 hull) and R4 face-blanked / face-only copies (AR1 blank/, own hull)."""
import csv
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lists as LS  # noqa: E402

AR1 = pathlib.Path("/mnt/t7/smad_next/AR1")
SPLIT = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split/ladder_split.csv")


def main():
    lad = {r["pid"]: r for r in csv.DictReader(open(SPLIT))}
    test = {p for p, r in lad.items() if r["test_read"] == "1"}
    nat, bl = [], []
    for r in csv.DictReader(open(AR1 / "manifest_splice2.csv")):
        v = r["variant"]
        row = dict(id=r["id"], path=r["path"], set="splice", cell="frgcferet",
                   rung=r["rung"] + ("" if v == "native" else "_" + v.split("_")[0]), tool=r["tool"], p1=r["p1"],
                   p2=r["p2"], geom="")
        if v == "native" and r["rung"] in ("S0", "S3", "S4"):
            nat.append(row)
        elif v != "native" and r["p1"] in test and r["tool"] == "opencv":
            bl.append(row)
    bm = {r["id"]: r for r in csv.DictReader(open(AR1 / "blank" / "blank_manifest.csv"))}
    for r in csv.DictReader(open(AR1 / "manifest.csv")):
        if r["pool"] == "frgcferet" and r["rung"] == "R4" and r["tool"] == "opencv" and r["p1"] in test and r["id"] in bm:
            for v, k in (("bg", "bg_path"), ("face", "face_path")):
                bl.append(dict(id=f"ar1_{r['id']}__{v}", path=bm[r["id"]][k], set="splice", cell="frgcferet",
                               rung=f"R4_{v}", tool="opencv", p1=r["p1"], p2=r["p2"], geom=""))
    LS.write("splice_nat", nat)
    LS.write("splice_blank", bl)


if __name__ == "__main__":
    main()
