#!/bin/bash
# PN1 CPU chain 4 (amendment 4): full pack of the fixed manifests, then the DINOv3 tar for the Athena smoke job.
set -u
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
cd /home/narolski/smad-next/src/PN1
$P build_pack.py; echo "pack rc $? $(date +%T)"
$P build_featx.py r2w4_td=/mnt/t7/smad_next/PN1/lists/r2w4_td.csv frll_e5s=/mnt/t7/smad_next/PN1/lists/frll_e5s.csv \
  devsoft=/mnt/t7/smad_next/PN1/lists/devsoft.csv soft=/mnt/t7/smad_next/AF0/lists/soft.csv \
  ladsoft=/mnt/t7/smad_next/PN1/lists/ladsoft.csv; echo "featx rc $? $(date +%T)"
