#!/bin/bash
set -u
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"; L=/mnt/t7/smad_next/PN1/lists
cd /home/narolski/smad-next/src/PN1
$P cues27.py splice_nat=$L/splice_nat.csv splice_blank=$L/splice_blank.csv; echo "cues27 rc $?"
$P cert_cues.py splice_nat=$L/splice_nat.csv splice_blank=$L/splice_blank.csv; echo "cert rc $?"
$P splice_ratio.py; echo "ratio rc $?"
