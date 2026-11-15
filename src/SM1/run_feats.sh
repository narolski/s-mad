#!/bin/bash
# SM1: frozen-feature pass over the named flists, one after another (main + W loader workers). Usage: run_feats.sh W name...
set -euo pipefail
W=$1; shift
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
cd /tmp
for n in "$@"; do
  $P /home/narolski/smad-next/src/SM1/feats.py run --list /mnt/t7/smad_next/SM1/flists/$n.csv --name $n --workers $W --bs 64
done
echo FEATS_DONE "$@"
