#!/bin/bash
# Diffusion-autoencoder generation on Athena (DG1): align the FRGC / colorFERET pool photos with DiffAE's align.py run
# UNCHANGED through the X3 runner (run_align_unchanged.py: only the Pillow ANTIALIAS alias restored), on the DGX CPU.
# The inputs not yet aligned are split into N parts (symlinks to the byte-identical copies in pool_in/) and aligned by
# N processes into one output folder (output names are unique; align.py skips files that exist). Used because one
# process ran at about 3 s per photo on the loaded DGX (load average above 100).
set -euo pipefail
N=${1:-4}
D=/mnt/t7/smad_next/DG1
RUNNER=/mnt/t7/smad_heldout/a41_diffae/data/scripts/run_align_unchanged.py
ALIGN=/mnt/t7/thirdparty/diffae_00c57d3f626f28bf9ed8aff58d90baab25de3af4/repo/align.py
ALIGN_SHA=7d7cf0d0222d25800d5205a91122859b4077401b53ee33a014e4a650c8f5d27b
PY=/mnt/t7/thirdparty/diffae_venv/bin/python
rm -rf "$D/pool_in_parts"   # only symlinks this script made
python3 -I - "$D" "$N" <<'EOF'
import os, pathlib, sys
D, N = pathlib.Path(sys.argv[1]), int(sys.argv[2])
done = {p.stem for p in (D / "pool_a256").glob("*.png")}
files = sorted(f for f in os.listdir(D / "pool_in") if pathlib.Path(f).stem not in done)
for k in range(N):
    d = D / "pool_in_parts" / f"p{k}"
    d.mkdir(parents=True)
    for f in files[k::N]:
        os.symlink(D / "pool_in" / f, d / f)
print("to align", len(files))
EOF
for k in $(seq 0 $((N - 1))); do
  ( cd "$D/align_run" && nohup "$PY" -I "$RUNNER" "$ALIGN" "$ALIGN_SHA" -i "$D/pool_in_parts/p$k" -o "$D/pool_a256" \
      > "$D/pool_align_p$k.log" 2>&1 & )
done
echo "started $N aligner processes"
