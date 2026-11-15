#!/bin/bash
# SM1 A12: stream an image tar to Athena packs/SM1 without writing it on the T7 (disk near the 50 GB floor).
# tar of the file list -> sha256 + byte count computed in the stream -> ssh cat into <name>.part; then the .sha256
# file is written next to it and the .part renamed, all under the transfer lock (one connection per step).
#   bash athena_stream.sh FILELIST NAME      e.g. filelist_a12.txt sm1gpu_img_a12.tar
set -euo pipefail
FL=${1:?}; NAME=${2:?}
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
L=/mnt/t7/smad_next/SM1/gpupack
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=20 plgpnarolski@athena.cyfronet.pl)
INFO=$L/stream_${NAME}.json
T0=$(date +%s)
flock -w 1800 /tmp/smadnext-athena.lock bash -c "tar -cf - -T '$FL' | /usr/bin/python3 -I -c '
import hashlib, json, sys
h = hashlib.sha256(); n = 0
for b in iter(lambda: sys.stdin.buffer.read(1 << 20), b\"\"):
    h.update(b); n += len(b); sys.stdout.buffer.write(b)
sys.stdout.buffer.flush()
json.dump(dict(sha256=h.hexdigest(), bytes=n), open(\"$INFO\", \"w\"))
' | ${SSH[*]} 'cat > $G/packs/SM1/$NAME.part'"
SHA=$(/usr/bin/python3 -I -c "import json; print(json.load(open('$INFO'))['sha256'])")
BYTES=$(/usr/bin/python3 -I -c "import json; print(json.load(open('$INFO'))['bytes'])")
echo "$SHA  $NAME" > "$L/$NAME.sha256"
flock -w 1800 /tmp/smadnext-athena.lock "${SSH[@]}" "cd $G/packs/SM1 && [ \$(stat -c %s $NAME.part) = $BYTES ] && echo '$SHA  $NAME' > $NAME.sha256 && mv $NAME.part $NAME && ls -la $NAME $NAME.sha256"
echo "$(date -Is) streamed $NAME ($BYTES bytes, sha256 $SHA) in $(( $(date +%s) - T0 )) s" | tee -a $L/athena_upload.log
