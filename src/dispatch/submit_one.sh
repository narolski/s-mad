#!/usr/bin/env bash
# Dispatcher helper: submit one queue file and move it to done/ with the job ID.
# Usage: submit_one.sh /mnt/t7/smad_next/dispatch/submit_queue/<cluster>_<owner>_<name>.cmd
# Prints "SUBMITTED <jobid> <file>" or "REFUSED <file>: <output>". Never retries by itself.
set -uo pipefail
f="$1"; q=$(dirname "$f"); base=$(basename "$f")
cmd=$(grep -v '^#' "$f" | sed '/^[[:space:]]*$/d')
[ "$(printf '%s\n' "$cmd" | wc -l)" -eq 1 ] || { echo "REFUSED $base: not exactly one command line"; exit 2; }
n=$(printf '%s' "$cmd" | grep -o '/sbatch \|^sbatch \| sbatch ' | wc -l)
[ "$n" -eq 1 ] || { echo "REFUSED $base: $n sbatch calls"; exit 2; }
if printf '%s' "$cmd" | grep -qE '(^|[ ;&|])(scancel|rm|mv)( |$)|[<>]'; then echo "REFUSED $base: forbidden token"; exit 2; fi
grep -q '^#.*regist' "$f" || { echo "REFUSED $base: no registration line"; exit 2; }
case "$base" in
  wcss_*)
    printf '%s' "$cmd" | grep -q -- '--extra=FORCE_RM_TMPDIR' || { echo "REFUSED $base: no FORCE_RM_TMPDIR"; exit 2; }
    out=$(flock -w 600 /tmp/opencode/wcss-client.lock timeout 90 ssh -o BatchMode=yes -o ConnectTimeout=20 narolski@ui.wcss.pl "$cmd" 2>&1) ;;
  athena_*)
    out=$(timeout 90 ssh -o BatchMode=yes -o ConnectTimeout=20 plgpnarolski@athena.cyfronet.pl "$cmd" 2>&1) ;;
  *) echo "REFUSED $base: unknown cluster prefix"; exit 2 ;;
esac
id=$(printf '%s' "$out" | sed -n 's/.*Submitted batch job \([0-9]*\).*/\1/p' | head -1)
if [ -n "$id" ]; then
  mv "$f" "$q/done/${base%.cmd}.$id.cmd"; echo "SUBMITTED $id $base"
else
  echo "REFUSED $base: $(printf '%s' "$out" | tr '\n' ' ' | cut -c1-300)"; exit 1
fi
