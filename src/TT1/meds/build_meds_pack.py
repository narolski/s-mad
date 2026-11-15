"""TT1 MEDS extension: scoring list, small MEDS image pack and the network tar with gate references.
  meds pack : /mnt/t7/smad_next/TT1/meds/tt1m_meds.tar: tt1m/data/eval/meds/<id>.png (all 1,018 aligned frames incl.
              aligned=0), tt1m/data/manifests/meds_score.csv (PN1 manifest format, fam "meds", rung = MEDS-I/MEDS-II,
              cell = primary|secondary, host = person, strength = encounter), tt1m/SHA256SUMS.
  nets tar  : /mnt/t7/smad_next/TT1/meds/tt1m_nets.tar: nets/<net>/{meta.json,last_trainable.pt} for the 15 FS1 networks
              and the 3 Sp networks (from the verified local result tars), gate_ref/<net>.npz = the network's pn1fs
              scores of the 3,417 TT1 fam-gate rows (__gate.npz of TT1_A100_pn1fs_fs / TT1_pn1fs_sp), SHA256SUMS.
  python3 -I build_meds_pack.py"""
import csv
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import tarfile

M = pathlib.Path("/mnt/t7/smad_next/TT1/meds")
R = pathlib.Path("/mnt/t7/smad_next/TT1/results")
FSR = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
NETS = [f"PN1_{a}_s{s}" for a in ("A", "B", "Sb") for s in (403, 404, 405, 406, 407)] + [f"PN1_Sp_s{s}" for s in (403, 404, 405)]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def tar_tree(tree, top, out):
    subprocess.run(["tar", "-C", str(tree), "-chf", str(out), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-13 00:00:00", top], check=True)
    pathlib.Path(str(out) + ".sha256").write_text(f"{sha(out)}  {out.name}\n")
    return sha(out)


def main():
    rows = list(csv.DictReader(open(M / "meds_manifest.csv")))
    tree = M / "pack_tree"
    if tree.exists():
        shutil.rmtree(tree)
    root = tree / "tt1m"
    (root / "data" / "eval" / "meds").mkdir(parents=True)
    (root / "data" / "manifests").mkdir(parents=True)
    out = []
    for r in rows:
        p = f"eval/meds/{r['id']}.png"
        os.symlink(r["aligned_path"], root / "data" / p)
        out.append(dict(id=r["id"], path=p, label="0", klass="genuine", role="meds", fam="meds", rung=r["part"],
                        strength=r["encounter"], tool="", cell="primary" if r["aligned"] == "1" else "secondary",
                        host=r["person"], neutral=""))
    mf = root / "data" / "manifests" / "meds_score.csv"
    with open(mf, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    shutil.copyfile(mf, M / "meds_score.csv")
    ss = subprocess.run(f"cd {root} && find -L . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum", shell=True,
                        check=True, capture_output=True, text=True).stdout
    (root / "SHA256SUMS").write_text(ss)
    hp = tar_tree(tree, "tt1m", M / "tt1m_meds.tar")
    # nets
    nt = M / "nets_tree"
    if nt.exists():
        shutil.rmtree(nt)
    nr = nt / "tt1mnets"
    (nr / "gate_ref").mkdir(parents=True)
    info = {}
    for n in NETS:
        t = FSR / f"{n}.tar"
        want = (FSR / f"{n}.tar.sha256").read_text().split()[0]
        assert sha(t) == want, n
        (nr / "nets" / n).mkdir(parents=True)
        with tarfile.open(t) as tf:
            for f in ("meta.json", "last_trainable.pt"):
                (nr / "nets" / n / f).write_bytes(tf.extractfile(f"{n}/{f}").read())
        src = R / ("unpacked_sp/TT1_pn1fs_sp" if "_Sp_" in n else "unpacked_fs/TT1_A100_pn1fs_fs") / "scores" / f"{n}__gate.npz"
        shutil.copyfile(src, nr / "gate_ref" / f"{n}.npz")
        info[n] = dict(tar_sha256=want, gate_ref=str(src), gate_ref_sha256=sha(src))
    (nr / "nets.json").write_text(json.dumps(info, indent=1))
    ss = subprocess.run(f"cd {nr} && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum", shell=True,
                        check=True, capture_output=True, text=True).stdout
    (nr / "SHA256SUMS").write_text(ss)
    hn = tar_tree(nt, "tt1mnets", M / "tt1m_nets.tar")
    print("meds pack", hp, len(out), "list", sha(mf), "nets", hn, len(NETS))


if __name__ == "__main__":
    main()
