#!/bin/bash
# PN1 amendment 14 (rented, one lease): pip pins as remote_setup.sh, then score from pn1_a14.tar:
#   gate   A_s401 and B_s402 on the HN2 list (fam ffhq), compared on the DGX with their pn1a / pn1b scores
#   HN7    A, Bn, C x 401, 402 on the splice rows (fam splice)
#   HN8    all 12 networks on FFHQ landmark_combined orig + resmatch (fam ffhq_lcomb)
#   HN2b   Sb, Bv x 401, 402 on the HN2 list (fam ffhq)
# One tar PN1_A14.tar + .sha256 in results. Arg: the registered pack sha256.
set -u
PIN=${1:?pack pin}
B=/workspace/pn1; T=PN1_A14
mkdir -p "$B/root/results/PN1" "$B/logs" "$B/rc"
fail() { echo "FAIL $1" > "$B/rc/$T"; exit 1; }
[ "$(sha256sum < "$B/root/packs/PN1/pn1_a14.tar" | cut -d' ' -f1)" = "$PIN" ] || fail pin
python -c "import torch, torchvision; print('torch==' + torch.__version__.split('+')[0]); print('torchvision==' + torchvision.__version__.split('+')[0])" > "$B/constraints.txt"
python -m pip install --no-cache-dir -c "$B/constraints.txt" timm==1.0.27 huggingface_hub==0.36.2 safetensors==0.8.0 \
  numpy==1.26.4 pyyaml==6.0.3 pillow==10.2.0 > "$B/logs/pip.log" 2>&1 || fail pip
python -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0' and torch.cuda.device_count() >= 1" || fail versions
W=$B/work/a14; rm -rf "$W"; mkdir -p "$W/res/$T"
tar -C "$W" -xf "$B/root/packs/PN1/pn1_a14.tar" && (cd "$W/pn14" && sha256sum -c --quiet SHA256SUMS) || fail sums
D=$W/data; mkdir -p "$D/manifests"; ln -s "$W/pn14/data/eval" "$D/eval"; ln -s "$W/pn14/data/manifests/pn1_a14.csv" "$D/manifests/pn1_a14.csv"
sc() {  # net fam
  SMAD_DATA=$D HF_HOME=$W/pn14/hf HF_HUB_OFFLINE=1 python "$B/bin/rescore.py" --resdir "$W/pn14/nets/$1" --code "$W/pn14/code" \
    --manifest pn1_a14.csv --fam "$2" --out "$W/res/$T/${1}__$2.npz" >> "$B/logs/$T.log" 2>&1 || fail "$1_$2"
}
sc PN1_A_s401 ffhq; sc PN1_B_s402 ffhq                                   # gate
for s in 401 402; do for a in A Bn C; do sc PN1_${a}_s$s splice; done; done   # HN7
for s in 401 402; do for a in A B Bn C Sb Bv; do sc PN1_${a}_s$s ffhq_lcomb; done; done   # HN8
for s in 401 402; do for a in Sb Bv; do sc PN1_${a}_s$s ffhq; done; done      # HN2 for Sb, Bv
echo 0 > "$B/rc/$T"
cp "$B/logs/$T.log" "$B/logs/pip.log" "$W/res/$T/"
nvidia-smi --query-gpu=uuid,name,driver_version --format=csv,noheader > "$W/res/$T/gpu.txt"
python -c "import sys, torch, timm, numpy, PIL; print(sys.version.split()[0], torch.__version__, torch.version.cuda, timm.__version__, numpy.__version__, PIL.__version__)" > "$W/res/$T/versions.txt"
tar -C "$W/res" -cf "$B/root/results/PN1/$T.tar" "$T"; (cd "$B/root/results/PN1" && sha256sum "$T.tar" > "$T.tar.sha256")
rm -rf "$W"; date > "$B/A14_DONE"
