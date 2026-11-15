#!/bin/bash
# TT1-X Part 1 chain (prereg_x_block.md amendment): wait for tt1/TT1_DONE (main job verified, two copies) and for the
# three verified local Sp tars, check free disk on pn1fs, then run the pinned start call and the pull loop.
set -u
L0=/mnt/t7/smad_next/vast/pn1fs; D=/mnt/t7/smad_next/PN1/results_fs
KEY=/home/narolski/.config/smad-next/vast_ssh_key
log() { echo "$(date +%T) [chain_sp] $*" | tee -a "$L0/tt1/tt1_x_drive.log"; }
until [ -f "$L0/tt1/TT1_DONE" ]; do sleep 60; done
log "TT1_DONE seen"
until for s in 403 404 405; do [ -f "$D/PN1_Sp_s$s.tar" ] && (cd "$D" && sha256sum -c --quiet "PN1_Sp_s$s.tar.sha256") || exit 1; done; do sleep 60; done
log "three Sp tars verified locally"
ssh -o BatchMode=yes -o ConnectTimeout=15 -o UserKnownHostsFile=$L0/known_hosts -i $KEY -p 30078 root@149.248.21.7 'df -h /workspace | tail -1' 2>/dev/null | grep -v -i "welcome\|fun" | tee -a "$L0/tt1/tt1_x_drive.log"
export TAG=sp TASKS="PN1_Sp_s403 PN1_Sp_s404 PN1_Sp_s405" LOCAL_TARS=$D GPU_UUID=GPU-5bd20020-715e-e9fd-b9d3-f89ca57849ad \
  DEADLINE_EPOCH=1794581505 GATE_PACK=/workspace/pn1/root/packs/PN1/pn1_pack_fs.tar \
  GATE_PACK_SHA=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
bash /home/narolski/smad-next/src/TT1/rented/drive_tt1_x.sh 149.248.21.7 30078 $L0 start || { log "start failed"; exit 1; }
bash /home/narolski/smad-next/src/TT1/rented/drive_tt1_x.sh 149.248.21.7 30078 $L0 loop
