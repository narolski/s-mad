#!/bin/bash
# PN1 CPU chain 1 (one process at a time, nice 10): waits for the dev softening build, then JPEG-call verification,
# 27-statistic floors for new lists (8-image test first), certificate cues (8-image test first).
set -u
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
L=/mnt/t7/smad_next/PN1/lists; A=/mnt/t7/smad_next/AF0/lists
cd /home/narolski/smad-next/src/PN1
while kill -0 2335741 2>/dev/null; do sleep 20; done
echo "== soften_dev finished $(date +%T)"; tail -1 /mnt/t7/smad_next/PN1/soften_dev.log
$P lists.py devsoft
$P jpeg_c.py verify; echo "jpeg verify rc $?"
PN1_LIMIT=8 $P cues27.py r2w4=$L/r2w4.csv && $P cues27.py r2w4=$L/r2w4.csv ar1soft=$A/ar1soft.csv devsoft=$L/devsoft.csv frll_e5=$L/frll_e5.csv
echo "cues27 rc $? $(date +%T)"
PN1_LIMIT=8 $P cert_cues.py cert_a=$L/cert_a.csv && $P cert_cues.py cert_a=$L/cert_a.csv cert_b=$L/cert_b.csv devsoft=$L/devsoft.csv
echo "cert rc $? $(date +%T)"
