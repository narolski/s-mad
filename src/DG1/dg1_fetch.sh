#!/bin/bash
# Diffusion-autoencoder generation on Athena (DG1): copy result tars back from Athena with the lock, check each tar's
# sha256 against the .sha256 written on the compute node, and unpack into /mnt/t7/smad_next/DG1/gen/<TAG>/.
# usage: bash dg1_fetch.sh TAG [TAG...]     (TAG as in DG1_<TAG>.tar, e.g. smoke_12345, setA, setB_s0)
set -euo pipefail
D=/mnt/t7/smad_next/DG1
R=/net/pr2/projects/plgrid/plggrestoration/smad-next/results/DG1
mkdir -p "$D/athena_results" "$D/gen"
SRC=()
for t in "$@"; do SRC+=("plgpnarolski@athena.cyfronet.pl:$R/DG1_$t.tar" "plgpnarolski@athena.cyfronet.pl:$R/DG1_$t.tar.sha256"); done
flock -w 600 /tmp/smadnext-athena.lock rsync -a --partial --info=stats1 -e "ssh -o BatchMode=yes -o ConnectTimeout=20" \
  "${SRC[@]}" "$D/athena_results/"
for t in "$@"; do
  ( cd "$D/athena_results" && sha256sum -c "DG1_$t.tar.sha256" )
  [ ! -e "$D/gen/$t" ] || { echo "refused: $D/gen/$t exists"; exit 1; }
  mkdir -p "$D/gen/$t"
  tar -C "$D/gen/$t" -xf "$D/athena_results/DG1_$t.tar"
  echo "unpacked $t: $(find "$D/gen/$t" -name '*.png' | wc -l) png"
done
