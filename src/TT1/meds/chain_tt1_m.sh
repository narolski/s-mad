#!/bin/bash
# TT1-M chain: wait for SE1_DONE_411 (SE1 owner's seed 411 fetched and verified), then start (the driver refuses if the
# GPU is busy or a job already runs) and pull until TT1M_DONE. If start refuses, retry every 5 min for at most 2 h.
set -u
L0=/mnt/t7/smad_next/vast/se1d; D=/home/narolski/smad-next/src/TT1/meds/drive_tt1_m.sh
until [ -f "$L0/SE1_DONE_411" ]; do sleep 60; done
for k in $(seq 1 24); do bash "$D" start && break; sleep 300; done
bash "$D" loop
