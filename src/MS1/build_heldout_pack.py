"""MS1 held-out scoring pack (prereg part 2, 2.2): code and base weights from the FS1 tree, the unchanged rescorer
src/PN1/rescore.py, the CFD and KDEF frames (pools pinned in part 2.9), TT1's registered references (fam tt1ref) and
manifest ms1_heldout.csv (fam cfd / kdef / tt1ref).
  python3 -I build_heldout_pack.py -> OUT/ms1_heldout_pack.tar (+ .sha256)"""
import csv
import os
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ms1common as C  # noqa: E402

FS = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1")
POOLS = {"cfd": "d6ef6793b588fa981ccb27a575ead4b91ffad0f3fe2b2345973c8ec9866b75a9",
         "kdef": "e54be768a2b1ab8cb6fc9e9812d6baf1e2009ca06ef35268bbbecd497589d8c3"}
RESCORE = (C.SRC / "PN1/rescore.py", "6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e")


def main():
    fs_sums = dict(reversed(line.rstrip("\n").split("  ", 1)) for line in open(FS / "SHA256SUMS"))
    tree = C.OUT / "heldout_tree"
    if tree.exists():
        shutil.rmtree(tree)
    root = tree / "pn1"
    sums = []

    def link(pp, src, expect=None):
        dst = root / pp
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(os.path.realpath(src), dst)
        h = C.sha(src)
        assert expect is None or h == expect, src
        sums.append((h, pp))

    for p, h in sorted(fs_sums.items()):
        if p.startswith(("code/", "hf/")):
            link(p, FS / p, h)
    link("src/rescore.py", RESCORE[0], RESCORE[1])
    rows = []
    for fam, ph in POOLS.items():
        pool = C.OUT / fam / "pool.csv"
        assert C.sha(pool) == ph, pool
        for r in csv.DictReader(open(pool)):
            if r["aligned"] != "1":
                continue
            pp = f"eval/{fam}/{r['id']}.png"
            link("data/" + pp, r["frame"], r["frame_sha256"])
            rows.append(dict(id=r["id"], path=pp, label="0", klass="genuine", role="dev", fam=fam, rung="photo",
                             strength="", tool="", cell=fam, host=r["person"], neutral="1"))
    # TT1's registered references (TT1-S, 01557ce; list pinned at ccd6319): R_cam, its border-blanked and
    # crop-geometry-matched copies, and R_ffhq_border; fam "tt1ref" (rung and cell as TT1's list)
    import gzip, io, json
    TL = pathlib.Path("/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/tt1_score.csv.gz")
    raw = gzip.open(TL).read()
    assert __import__("hashlib").sha256(raw).hexdigest() == "c0055b51467cf8d001d56cbc4689706d68f0bf35c64066b1ba49fada5cb45761"
    srcmap = json.load(open("/mnt/t7/smad_next/TT1/tt1_score_sources.json"))
    for r in csv.DictReader(io.StringIO(raw.decode())):
        if r["rung"] not in ("R_cam", "R_cam_border", "R_cam_geo224", "R_cam_geo112", "R_ffhq_border"):
            continue
        pp = r["path"]
        link("data/" + pp, srcmap[pp])
        rows.append(dict(id=r["id"] if r["rung"] != "R_cam" else "rcam_" + r["id"], path=pp, label="0", klass="genuine",
                         role="dev", fam="tt1ref", rung=r["rung"], strength=r["strength"], tool=r["tool"], cell=r["cell"],
                         host=r["host"], neutral=r["neutral"]))
    mf = root / "data/manifests/ms1_heldout.csv"
    C.write_csv(mf, rows)
    sums.append((C.sha(mf), "data/manifests/ms1_heldout.csv"))
    with open(root / "SHA256SUMS", "w") as f:
        for h, p in sums:
            f.write(f"{h}  {p}\n")
    tar = C.OUT / "ms1_heldout_pack.tar"
    subprocess.run(["tar", "-C", str(tree), "-chf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-13 00:00:00", "pn1"], check=True)
    th = C.sha(tar)
    (C.OUT / "ms1_heldout_pack.tar.sha256").write_text(f"{th}  ms1_heldout_pack.tar\n")
    print("rows", len(rows), "manifest", C.sha(mf), "pack", th, tar.stat().st_size)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
