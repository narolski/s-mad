"""Shared test battery (BATTERY): the development image sets scored for the audit rows. Development data only.

Each set is one manifest (pinned by sha256) read from <data root>/manifests/, with image paths relative to that data
root, exactly as the pack that carries it lays them out. The scorer keeps each manifest's row order (batch composition =
the stored runs'), so logits made by the battery on a gated platform are directly comparable with fit-job logits made on
that platform with pn1_score.py.

  set   manifest         rows    pack (WCSS: packs/<dir>/<tar>, sha256 of the tar)               audit rows
  dev   ab1_eval.csv     21,277  BB2/pn1_pack_fs.tar 96c31ae2 + AB1/ab1_overlay_v2.tar 171fdb21  1,2,6-9,12,17-20
  tt1   tt1_score.csv    34,411  TT1/tt1_pack.tar 2109f742                                       4,5,10,17,(19)
  meds  meds_score.csv    1,018  BB2/tt1m_meds.tar 3fb917b2 (also RZ1/)                          4
  gd    pr1_gd.csv       see pin BB2/pr1_gd.tar 40aa95d2                                         13,14
dev = the FS1 evaluation rows (pn1_eval.csv, 19,797, its first rows in the same order) + the 1,480 MS1 FFHQ hold-out rows.
The gate rows are inside the first 19,797 dev rows."""
import csv
import os
import pathlib

from . import guard

SETS = {
    "dev": dict(manifest="ab1_eval.csv", sha256="93a5ba234f91e57951829c5536fabbe0f792ee4ad0a293f074aaca72f7465bd5", n=21277,
                default_roots=["/mnt/t7/smad_next/PN1/fs_tree/pn1/data", "/mnt/t7/smad_next/AB1/overlay_tree/pn1/data"],
                pack="BB2/pn1_pack_fs.tar 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 + "
                     "AB1/ab1_overlay_v2.tar 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149"),
    "tt1": dict(manifest="tt1_score.csv", sha256="c0055b51467cf8d001d56cbc4689706d68f0bf35c64066b1ba49fada5cb45761", n=34411,
                default_roots=["/mnt/t7/smad_next/TT1/pack_tree/tt1/data"],
                pack="TT1/tt1_pack.tar 2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554"),
    "meds": dict(manifest="meds_score.csv", sha256="9093d5d5425e1d031f5f940e15321a6371cb0fe6a5d2014aabc404ba4543415a", n=1018,
                 default_roots=["/mnt/t7/smad_next/TT1/meds/pack_tree/tt1m/data"],
                 pack="BB2/tt1m_meds.tar 3fb917b226c6d31fab176a4d8fdd5d6e6b22b8274cc091591f444e623a87ab61"),
    "gd": dict(manifest="pr1_gd.csv", sha256="3577a91351131b104457424054c29ca3c6f3fc59666e9204598e45e608e15157", n=None,
               default_roots=["/mnt/t7/smad_next/PR1/pr1_gd_tree/pr1g/data"],
               pack="BB2/pr1_gd.tar 40aa95d2b48719025bc3b80ebf9fa997bb1adf6c69da894120716a6e962b7329"),
}
ORDER = ("dev", "tt1", "meds", "gd")


def sha(p):
    from .legacy import sha as _s
    return _s(p)


def load(name, roots):
    """-> (rows with an absolute 'abspath', manifest path, sha256). Refuses a manifest off its pin, any denied path, any
    missing image."""
    spec = SETS[name]
    roots = [pathlib.Path(r) for r in roots]
    man = None
    for r in roots:
        p = r / "manifests" / spec["manifest"]
        if p.exists():
            man = p
            break
    if man is None:
        raise FileNotFoundError(f"BATTERY: manifest {spec['manifest']} of set {name} not under {[str(r) for r in roots]}")
    guard.check_path(man, "manifest")
    got = sha(man)
    if got != spec["sha256"]:
        raise RuntimeError(f"BATTERY: {man} off its pin ({got[:16]} != {spec['sha256'][:16]})")
    rows = list(csv.DictReader(open(man)))
    if spec["n"] is not None:
        assert len(rows) == spec["n"], (name, len(rows))
    guard.check_rows(rows)
    missing = []
    for r in rows:
        for root in roots:
            q = root / r["path"]
            if os.path.exists(q):
                r["abspath"] = str(q)
                break
        else:
            missing.append(r["path"])
    if missing:
        raise FileNotFoundError(f"BATTERY: {len(missing)} images of set {name} missing (first {missing[:3]})")
    return rows, str(man), got
