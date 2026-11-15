"""SM1 Part 1: document the SMDD release's pair structure and file sizes (no score is read).

For each split on disk (train: m15k_t / os25k_bf_t / os25k_m_t; evaluation: m15k_e / os25k_bf_e / os25k_m_e):
  - parse morphed_<A>_<B>.png -> first / second contributor counts
  - is every contributor a file of the morph-source folder (os25k_m_*)? of the genuine folder (os25k_bf_*)?
  - name overlap between os25k_bf_* and os25k_m_* (same file names would be different renders or the same?)
  - image size of every morph and genuine file (PNG header only), share not 256 x 256
  - cross-split: overlap of contributors / genuine names between train and evaluation
Writes experiments/SM1_.../p1_structure.json.

  python3 -I p1_document.py
"""
import collections
import hashlib
import json
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path("/mnt/t7/Datasety/downloads/SMDD")
RES = pathlib.Path("/home/narolski/smad-next/experiments/SM1_smdd-partner-audit-and-rebuild")
SPLITS = {"train": dict(m=ROOT / "SMDD_release_train/m15k_t", bf=ROOT / "SMDD_release_train/os25k_bf_t",
                        src=ROOT / "os25k_m_t"),
          "evaluation": dict(m=ROOT / "SMDD_release_evaluation/m15k_e", bf=ROOT / "SMDD_release_evaluation/os25k_bf_e",
                             src=ROOT / "os25k_m_e")}
PAT = re.compile(r"^morphed_(img\d+)_(img\d+)\.png$")


def png_size(p):
    with open(p, "rb") as f:
        h = f.read(24)
    assert h[:8] == b"\x89PNG\r\n\x1a\n", p
    return struct.unpack(">II", h[16:24])


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    out = {}
    names = {}
    for sp, d in SPLITS.items():
        mf = sorted(x.name for x in d["m"].iterdir() if x.suffix == ".png")
        bad = [x for x in mf if not PAT.match(x)]
        pairs = [PAT.match(x).groups() for x in mf if PAT.match(x)]
        first = collections.Counter(a for a, _ in pairs)
        second = collections.Counter(b for _, b in pairs)
        bf = {x.name[:-4] for x in d["bf"].iterdir() if x.suffix == ".png"}
        src = {x.name[:-4] for x in d["src"].iterdir() if x.suffix == ".png"}
        contrib = set(first) | set(second)
        msz = collections.Counter(png_size(d["m"] / x) for x in mf)
        bsz = collections.Counter(png_size(d["bf"] / (x + ".png")) for x in sorted(bf))
        ssz = collections.Counter(png_size(d["src"] / (x + ".png")) for x in sorted(src))
        both_bf_src = sorted(bf & src)
        same_bytes = None
        if both_bf_src:
            k = both_bf_src[:200]
            same_bytes = sum(md5(d["bf"] / (x + ".png")) == md5(d["src"] / (x + ".png")) for x in k)
        per_first = collections.Counter(first.values())
        pairs_set = collections.Counter(pairs)
        out[sp] = dict(
            morph_dir=str(d["m"]), genuine_dir=str(d["bf"]), source_dir=str(d["src"]),
            n_morph_files=len(mf), n_unparsed=len(bad), unparsed_examples=bad[:5],
            n_first_contributors=len(first), n_second_contributors=len(second),
            second_contributor_counts=dict(second.most_common()),
            first_also_second=len(set(first) & set(second)),
            morphs_per_first_contributor_hist={str(k): v for k, v in sorted(per_first.items())},
            duplicate_pairs=sum(v > 1 for v in pairs_set.values()),
            n_contributors=len(contrib),
            contributors_in_source_dir=len(contrib & src), contributors_not_in_source_dir=sorted(contrib - src)[:10],
            contributors_in_genuine_dir=len(contrib & bf),
            n_genuine=len(bf), n_source=len(src), genuine_names_also_in_source_dir=len(both_bf_src),
            same_bytes_of_first200_shared_names=same_bytes,
            morph_sizes={f"{w}x{h}": v for (w, h), v in msz.most_common()},
            morph_share_not_256=round(1 - msz.get((256, 256), 0) / len(mf), 5),
            genuine_sizes={f"{w}x{h}": v for (w, h), v in bsz.most_common()},
            source_sizes={f"{w}x{h}": v for (w, h), v in ssz.most_common()},
        )
        names[sp] = dict(first=set(first), second=set(second), bf=bf, src=src)
        print(sp, json.dumps({k: v for k, v in out[sp].items() if k not in ("second_contributor_counts",)}, indent=0)[:3000])
    t, e = names["train"], names["evaluation"]
    out["cross_split"] = dict(
        second_contributors_shared=sorted(t["second"] & e["second"]),
        first_contributors_shared=len(t["first"] & e["first"]),
        genuine_names_shared=len(t["bf"] & e["bf"]),
        train_contributors_in_eval_genuine=len((t["first"] | t["second"]) & e["bf"]),
        eval_contributors_in_train_genuine=len((e["first"] | e["second"]) & t["bf"]),
        source_names_shared=len(t["src"] & e["src"]))
    print(json.dumps(out["cross_split"], indent=1))
    json.dump(out, open(RES / "p1_structure.json", "w"), indent=1)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
