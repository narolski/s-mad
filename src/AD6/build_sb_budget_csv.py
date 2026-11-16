"""AD6 matched-recipe comparator retrains: materialise the full-Sb training list into a fixed
update budget (6,250 optimizer updates x global batch 256 = 1,600,000 presentations).

Input: the registered FS1 manifest `/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv`
(sha256 2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a, 8,386 rows, already
count-balanced 4,193 genuine / 4,193 attack; rows are FS1 training rows of FRGC and colorFERET only).

Construction (deterministic, seed 400, shared by every AD6 arm and seed):
  1. shuffle one interleaved cycle: rows sorted (label-major alternating) then permuted with
     random.Random(400).shuffle over BLOCKS of 256 equal-label runs, so every consecutive 256-row
     block is exactly 128 bonafide / 128 attack (per-batch count balance);
  2. tile whole BLOCKS until 1,600,000 rows (6,250 x 256; 1,600,000 / 8,386 = 190.84 cycles, so the
     last cycle's blocks are dropped, never truncated mid-block -> per-batch balance holds everywhere);
  3. write header `image_path,label` with label strings bonafide|attack (bonafide = genuine photo,
     attack = morph), paths rooted at CROP_ROOT (placeholder; jobs sed it to the staged root).

Run: python3 -I build_sb_budget_csv.py OUT_CSV OUT_JSON
"""
import csv, hashlib, json, pathlib, sys

SRC = "/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv"
SRC_SHA = "2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a"
STEPS, GBS = 6250, 256
SEED = 400


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    out_csv, out_json = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    assert sha(SRC) == SRC_SHA, "train_Sb.csv sha mismatch"
    rows = list(csv.DictReader(open(SRC)))  # columns: path,label,source,tool,arm,val,mixed,id,kind,db,hist
    assert len(rows) == 8386
    gens = [r for r in rows if r["label"] == "0"]
    morphs = [r for r in rows if r["label"] == "1"]
    assert len(gens) == len(morphs) == 4193
    for kind in ("FRLL", "MAD22"):
        assert all(kind.lower() not in r["path"].lower() for r in rows), "eval corpus row in training list"

    # interleaved base: alternate genuine/attack (4193 pairs -> 8386 rows)
    base = [x for pair in zip(gens, morphs) for x in pair]
    assert len(base) == 8386 and base[0]["label"] == "0" and base[1]["label"] == "1"

    n_blocks_per_cycle = len(base) // GBS  # 32 full blocks of 256; 8386 - 32*256 = 194 = 97+97 remainder rows
    base_blocks = [base[i * GBS:(i + 1) * GBS] for i in range(n_blocks_per_cycle)]
    tail = base[n_blocks_per_cycle * GBS:]  # 194 rows: 97+97 if perfectly alternating
    assert len(tail) % 2 == 0 and all(r["label"] == "0" for r in tail[::2]) and all(r["label"] == "1" for r in tail[1::2]), \
        "tail block not label-alternating"

    rng_blocks = base_blocks[:]
    import random
    random.Random(SEED).shuffle(rng_blocks)
    # block-internal label shuffle of row order inside each block only among same-label rows
    for blk in rng_blocks:
        g = [r for r in blk if r["label"] == "0"]; m = [r for r in blk if r["label"] == "1"]
        random.Random(SEED + 1).shuffle(g); random.Random(SEED + 2).shuffle(m)
        inter = [x for p in zip(g, m) for x in p]
        assert len(inter) == GBS and sum(r["label"] == "0" for r in inter) == GBS // 2
        blk[:] = inter

    total = STEPS * GBS
    full_cycles = total // (n_blocks_per_cycle * GBS)
    leftover = total - full_cycles * n_blocks_per_cycle * GBS
    used = rng_blocks * full_cycles + rng_blocks[: leftover // GBS]
    out_rows, ngen = [], 0
    for blk in used:
        for r in blk:
            out_rows.append((r["path"], "bonafide" if r["label"] == "0" else "attack"))
            ngen += 1 if r["label"] == "0" else 0
    assert len(out_rows) == total, (len(out_rows), total)
    assert ngen == total // 2, (ngen, total // 2)

    off = 0
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["image_path", "label"])
        for p, lab in out_rows:
            w.writerow([f"CROP_ROOT/{p}", lab]); off += 1

    rep = dict(source=SRC, source_sha256=SRC_SHA, seed=SEED, steps=STEPS, global_batch=GBS,
               presentations=total, cycles=full_cycles, n_blocks_cycle=n_blocks_per_cycle,
               unique=8386, output=str(out_csv), output_sha256_pending=False,
               bonafide=ngen, attack=total - ngen, header="image_path,label",
               label_map="bonafide=genuine photo(FS1 label 0), attack=face-spliced/protocol morph etc.(FS1 label 1)",
               rows_written=off, csv_sha256=sha(out_csv))
    json.dump(rep, open(out_json, "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if "sha" in k or k in ("presentations", "bonafide", "attack", "cycles")}))


if __name__ == "__main__":
    main()
