"""PN1 amendment 5: tar of the eight SMDD ViT-B/16 recipe retrains (meta.json + last.pt), read only, hash-checked
against experiments/PN1_.../ref_smdd_m3_last_sha256.txt. -> /mnt/t7/smad_next/PN1/refnets.tar (+ .sha256)."""
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

PN1 = pathlib.Path("/mnt/t7/smad_next/PN1")
RUNS = pathlib.Path("/mnt/t7/wcss_backups/smadcvpr/runs/A12BR")
META = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12BR")
PIN = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/ref_smdd_m3_last_sha256.txt")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    tree = PN1 / "refnets_tree"
    if tree.exists():
        shutil.rmtree(tree)
    root = tree / "refnets"
    sums = []
    for line in open(PIN):
        run, h, _, _ = line.split()
        d = root / run
        d.mkdir(parents=True)
        os.symlink(RUNS / run / "last.pt", d / "last.pt")
        os.symlink(META / run / "meta.json", d / "meta.json")
        assert sha(d / "last.pt") == h, run
        sums += [f"{h}  {run}/last.pt", f"{sha(d / 'meta.json')}  {run}/meta.json"]
    (root / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    out = PN1 / "refnets.tar"
    subprocess.run(["tar", "-chf", str(out), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-11 00:00:00", "-C", str(tree), "refnets"], check=True)
    (PN1 / "refnets.tar.sha256").write_text(f"{sha(out)}  refnets.tar\n")
    print("REFNETS", out, os.path.getsize(out))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
