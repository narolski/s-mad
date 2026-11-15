"""C2P-R pack (draft amendment C2P-R): the MS1 FFHQ hold-out images (fam ms1ffhq, 1,480, from the MS1 pack tree, each
checked against the MS1 pack SHA256SUMS of pn1_pack_ms1.tar c11b16bc...) and the MS1 evaluation manifest (d1fab6ad...),
under pn1c/data/; SHA256SUMS. The FS1 rows' images and the code/weights come from pn1fs's own pn1_pack_fs.tar.
  python3 -I build_c2pr_pack.py -> /mnt/t7/smad_next/PN1/c2pr/c2pr_pack.tar (+ .sha256)"""
import csv, hashlib, os, pathlib, shutil, subprocess, sys
MS = pathlib.Path("/mnt/t7/smad_next/MS1/pack_tree/pn1")
OUT = pathlib.Path("/mnt/t7/smad_next/PN1/c2pr")
MAN_SHA = "d1fab6ad4b20f0ec9dd426374ccd56e96368bf7b658b48e3ef31867e1fe470c5"
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
sums = dict(reversed(l.rstrip("\n").split("  ", 1)) for l in open(MS / "SHA256SUMS"))
man = MS / "data/manifests/pn1_eval.csv"
assert sha(man) == MAN_SHA
tree = OUT / "tree"
if tree.exists(): shutil.rmtree(tree)
root = tree / "pn1c"
out = []
for r in csv.DictReader(open(man)):
    if r["fam"] != "ms1ffhq": continue
    pp = "data/" + r["path"]; src = MS / pp
    h = sha(src); assert h == sums[pp], pp
    d = root / pp; d.parent.mkdir(parents=True, exist_ok=True); os.symlink(os.path.realpath(src), d); out.append((h, pp))
(root / "data/manifests").mkdir(parents=True, exist_ok=True)
os.symlink(os.path.realpath(man), root / "data/manifests/ms1_eval.csv"); out.append((MAN_SHA, "data/manifests/ms1_eval.csv"))
with open(root / "SHA256SUMS", "w") as f:
    for h, p in out: f.write(f"{h}  {p}\n")
tar = OUT / "c2pr_pack.tar"
subprocess.run(["tar", "-C", str(tree), "-chf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                "--mtime=2026-11-13 00:00:00", "pn1c"], check=True)
th = sha(tar); (OUT / "c2pr_pack.tar.sha256").write_text(f"{th}  c2pr_pack.tar\n")
print("files", len(out), "pack", th, tar.stat().st_size)
