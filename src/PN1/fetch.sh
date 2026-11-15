#!/bin/bash
# PN1: copy Athena results back (transfer lock) and check every tar against its .sha256 before anything reads it.
set -u
A=plgpnarolski@athena.cyfronet.pl; G=/net/pr2/projects/plgrid/plggrestoration/smad-next
mkdir -p /mnt/t7/smad_next/PN1/results
flock -w 1800 /tmp/smadnext-athena.lock rsync -a --exclude 'unpacked' $A:$G/results/PN1/ /mnt/t7/smad_next/PN1/results/ || { echo "FETCH FAILED"; exit 1; }
cd /mnt/t7/smad_next/PN1/results
for f in *.tar.sha256 smoke/*.tar.sha256; do [ -f "$f" ] || continue; (cd "$(dirname "$f")" && sha256sum -c "$(basename "$f")"); done
[ -f featx_out.tar ] && cp -n featx_out.tar featx_out.tar.sha256 /mnt/t7/smad_next/PN1/ 2>/dev/null
ls -la /mnt/t7/smad_next/PN1/results /mnt/t7/smad_next/PN1/results/logs | tail -30
