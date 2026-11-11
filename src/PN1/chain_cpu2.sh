#!/bin/bash
# PN1 CPU chain 2 (one process at a time, nice 10), after the JPEG copy build (PID given as $1):
# ladder-copy CLIP means (AF0 cache), tier-0 CLIP rerun with them, final manifests, full pack, DINOv3 tar for Athena.
set -u
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
cd /home/narolski/smad-next/src/PN1
while kill -0 "$1" 2>/dev/null; do sleep 15; done
echo "== jpeg build finished $(date +%T)"; tail -1 /mnt/t7/smad_next/PN1/jpeg_build.log
until [ "$(cat /mnt/t7/smad_next/AF0/feat/clip224/ladsoft.done 2>/dev/null)" = "2544" ]; do sleep 15; done
$P featpool.py clip224:ladsoft
$P tier0.py --backbones clip224; echo "tier0 clip rc $? $(date +%T)"
$P mkmanifests.py final > /mnt/t7/smad_next/PN1/manifests/final.log 2>&1; echo "manifests rc $? $(date +%T)"
$P build_pack.py; echo "pack rc $? $(date +%T)"
$P build_featx.py r2w4_td=/mnt/t7/smad_next/PN1/lists/r2w4_td.csv frll_e5s=/mnt/t7/smad_next/PN1/lists/frll_e5s.csv \
  devsoft=/mnt/t7/smad_next/PN1/lists/devsoft.csv soft=/mnt/t7/smad_next/AF0/lists/soft.csv \
  ladsoft=/mnt/t7/smad_next/PN1/lists/ladsoft.csv; echo "featx rc $? $(date +%T)"
