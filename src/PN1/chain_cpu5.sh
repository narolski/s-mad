#!/bin/bash
# PN1 CPU chain 5: tier 0 on DINOv3 (DGX means + Athena means), the 64-image platform check, tables.
set -u
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
cd /home/narolski/smad-next/src/PN1
$P tier0.py --backbones dinov3_512; echo "tier0 dinov3 rc $? $(date +%T)"
$P postfeatx.py check; echo "platform check rc $? $(date +%T)"
$P report.py tier0 > /dev/null; echo "report rc $? $(date +%T)"
