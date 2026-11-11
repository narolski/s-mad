#!/bin/bash
# PN1 CPU chain 3: after chain 1, certificate cues for AF0's softened list, the ladder copies and the JPEG copies;
# then the certificates and the matched-subsample test (cert.py tier0, tier1).
set -u
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
cd /home/narolski/smad-next/src/PN1
while kill -0 2353342 2>/dev/null; do sleep 20; done
$P cert_cues.py soft=/mnt/t7/smad_next/AF0/lists/soft.csv ladsoft=/mnt/t7/smad_next/PN1/lists/ladsoft.csv jpegc=/mnt/t7/smad_next/PN1/lists/jpegc.csv
echo "cert cues 3 rc $? $(date +%T)"
$P cert.py tier0; echo "cert tier0 rc $? $(date +%T)"
$P cert.py tier1; echo "cert tier1 rc $? $(date +%T)"
