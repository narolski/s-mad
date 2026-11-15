#!/bin/bash
# PN1 CPU chain 3 (amendment 4): after chain 1, tier 0 recomputed (CLIP), certificate cues for AF0's softened list,
# the ladder copies and the JPEG copies, then the certificates and the matched-subsample test.
set -u
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
cd /home/narolski/smad-next/src/PN1
while kill -0 2353342 2>/dev/null; do sleep 20; done
$P tier0.py --backbones clip224; echo "tier0 v2 clip rc $? $(date +%T)"
$P report.py tier0 > /dev/null; echo "report rc $?"
$P cert_cues.py soft=/mnt/t7/smad_next/AF0/lists/soft.csv ladsoft=/mnt/t7/smad_next/PN1/lists/ladsoft.csv jpegc=/mnt/t7/smad_next/PN1/lists/jpegc.csv
echo "cert cues 3 rc $? $(date +%T)"
$P cert.py tier0; echo "cert tier0 rc $? $(date +%T)"
$P cert.py tier1; echo "cert tier1 rc $? $(date +%T)"
