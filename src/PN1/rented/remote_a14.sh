#!/bin/bash
# PN1 amendment 14 (rented, one lease). Args: PIN VARIANT   (VARIANT full | reduced; reduced = no ffhq_lcomb rows,
# pack pn1_a14r.tar). pip pins as remote_setup.sh, then score from the pack:
#   gate   A_s401 and B_s402 on the HN2 list (fam ffhq), compared on the DGX with their pn1a / pn1b scores
#   HN7    A, Bn, C x 401, 402 on the splice rows (fam splice)
#   HN8    (full only) all 12 networks on FFHQ landmark_combined orig + resmatch (fam ffhq_lcomb)
#   HN2b   Sb, Bv x 401, 402 on the HN2 list (fam ffhq)
# Every call continues on error and is logged; on exit (success, failure or error) whatever exists is tarred with an
# rc file into PN1_A14.tar + .sha256 (rc file content "0" = every call succeeded).
set -u
PIN=${1:?pack pin}; VAR=${2:?variant}
B=/workspace/pn1; T=PN1_A14
PK=pn1_a14.tar; [ "$VAR" = reduced ] && PK=pn1_a14r.tar
W=$B/work/a14; OUT=$W/res/$T
rm -rf "$W"; mkdir -p "$OUT" "$B/root/results/PN1" "$B/logs" "$B/rc"
FAILS=()
note() { echo "$(date +%T) $*" | tee -a "$OUT/calls.log"; }
finish() {
  if [ ${#FAILS[@]} -eq 0 ]; then echo 0 > "$OUT/rc"; else printf '%s\n' "${FAILS[@]}" > "$OUT/rc"; fi
  cp "$OUT/rc" "$B/rc/$T"
  cp "$B/logs/$T.log" "$B/logs/pip.log" "$OUT/" 2>/dev/null
  { echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"; nvidia-smi -i "${CUDA_VISIBLE_DEVICES:-0}" --query-gpu=index,uuid,name,driver_version --format=csv,noheader; } > "$OUT/gpu.txt" 2>&1
  python -c "import sys, torch, timm, numpy, PIL; print(sys.version.split()[0], torch.__version__, torch.version.cuda, timm.__version__, numpy.__version__, PIL.__version__)" > "$OUT/versions.txt" 2>&1
  echo "$VAR" > "$OUT/variant.txt"
  tar -C "$W/res" -cf "$B/root/results/PN1/$T.tar" "$T"; (cd "$B/root/results/PN1" && sha256sum "$T.tar" > "$T.tar.sha256")
  date > "$B/A14_DONE"
}
trap finish EXIT
abort() { FAILS+=("FATAL $1"); note "FATAL $1"; exit 1; }
avail=$(df --output=avail -B1G /workspace | tail -1 | tr -d ' ')
[ "$avail" -ge 15 ] || abort "workspace_${avail}G_free"
[ "$(sha256sum < "$B/root/packs/PN1/$PK" | cut -d' ' -f1)" = "$PIN" ] || abort pin
python -c "import torch, torchvision; print('torch==' + torch.__version__.split('+')[0]); print('torchvision==' + torchvision.__version__.split('+')[0])" > "$B/constraints.txt" || abort torch
python -m pip install --no-cache-dir -c "$B/constraints.txt" timm==1.0.27 huggingface_hub==0.36.2 safetensors==0.8.0 \
  numpy==1.26.4 pyyaml==6.0.3 pillow==10.2.0 > "$B/logs/pip.log" 2>&1 || abort pip
python -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0' and torch.cuda.device_count() >= 1" || abort versions
tar -C "$W" -xf "$B/root/packs/PN1/$PK" && (cd "$W/pn14" && sha256sum -c --quiet SHA256SUMS) || abort sums
D=$W/data; mkdir -p "$D/manifests"; ln -s "$W/pn14/data/eval" "$D/eval"; ln -s "$W/pn14/data/manifests/pn1_a14.csv" "$D/manifests/pn1_a14.csv"
sc() {  # net fam: continue on error, logged
  if SMAD_DATA=$D HF_HOME=$W/pn14/hf HF_HUB_OFFLINE=1 python "$B/bin/rescore.py" --resdir "$W/pn14/nets/$1" --code "$W/pn14/code" \
       --manifest pn1_a14.csv --fam "$2" --out "$OUT/${1}__$2.npz" >> "$B/logs/$T.log" 2>&1; then note "ok $1 $2"
  else FAILS+=("$1 $2"); note "FAILED $1 $2"; fi
}
sc PN1_A_s401 ffhq; sc PN1_B_s402 ffhq                                          # gate
for s in 401 402; do for a in A Bn C; do sc PN1_${a}_s$s splice; done; done     # HN7
if [ "$VAR" = full ]; then
  for s in 401 402; do for a in A B Bn C Sb Bv; do sc PN1_${a}_s$s ffhq_lcomb; done; done   # HN8
fi
for s in 401 402; do for a in Sb Bv; do sc PN1_${a}_s$s ffhq; done; done        # HN2b
