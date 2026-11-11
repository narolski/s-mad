#!/bin/bash
# SM1 rented: check one uploaded tar against its pinned .sha256, unpack it to its place, delete the tar (the .sha256
# stays as the record). Idempotent: done/<name> marks a finished pack.
#   bash unpack_one.sh NAME      (NAME = ad4_pack | sm1gpu_img_<set> | sm1lora_manifests_<v2|b|audit>)
set -euo pipefail
N=${1:?name}
B=/workspace/sm1r; IN=$B/in; mkdir -p "$B/done" "$B/data/x" "$B/manifests" "$B/logs"
[ -f "$B/done/$N" ] && { echo "already unpacked $N"; exit 0; }
cd "$IN"
sha256sum -c "$N.tar.sha256"
case "$N" in
  ad4_pack)
    tar -C "$B" -xf "$N.tar"
    (cd "$B/ad4" && sha256sum -c --quiet SHA256SUMS)
    rm -rf "$B/ad4/data/train" ;;                        # not used by SM1 (as lora_run.sh)
  sm1gpu_img_*) tar -C "$B/data/x" -xf "$N.tar" ;;
  sm1lora_manifests_*) mkdir -p "$B/manifests/${N#sm1lora_manifests_}"; tar -C "$B/manifests/${N#sm1lora_manifests_}" -xf "$N.tar" ;;
  *) echo "unknown pack $N"; exit 1 ;;
esac
rm -f "$N.tar"
touch "$B/done/$N"
echo "UNPACKED $N $(df -h /workspace | tail -1 | awk '{print $4}') free"
