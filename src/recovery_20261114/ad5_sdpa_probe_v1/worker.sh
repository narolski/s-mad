#!/bin/bash
# New synthetic operator diagnostic; NOT a migration or replay of6321768.
set -euo pipefail
: "${SLURM_JOB_ID:?allocated GPU job required}"
: "${TMPDIR:?local scratch required}"
[ "${SLURM_JOB_PARTITION:-}" = lem-gpu-interactive ] || exit 2
[ -t 0 ] && [ -t 1 ] || { echo 'real interactive PTY required'; exit 2; }
L=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5
SRC=$L/ad5_sdpa_probe_v1
DEST=$L/logs/keep/ad5_sdpa_probe_v1_20261114
mkdir "$DEST" # create-only; neither prior failure nor partial result is overwritten
W=$TMPDIR/ad5_sdpa_probe_v1
mkdir "$W"
finish() {
 rc=$?
 trap - EXIT
 printf 'worker_exit=%s\njob=%s\n' "$rc" "$SLURM_JOB_ID" > "$W/worker_exit.txt"
 for f in "$W"/*.txt "$W"/*.log; do
  [ -f "$f" ] || continue
  cp "$f" "$DEST/" || rc=91
  cmp "$f" "$DEST/$(basename "$f")" || rc=92
 done
 ( cd "$DEST" && find . -maxdepth 1 -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS ) || rc=93
 exit "$rc"
}
trap finish EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
printf 'job=%s\npartition=%s\nstarted=%s\n' "$SLURM_JOB_ID" "$SLURM_JOB_PARTITION" "$(date -Is)" > "$W/job.txt"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader > "$W/device.txt"
echo "98d13a375bc9d171307fba2596aa81cba4a9089a82643c7f38ccbe93d9eb7c8f  $SRC/probe.py" | sha256sum -c -
echo "5b370b16905aba7465e5dffc79c42061e29298d1a55c996d62ec56e86dffe05d  $SRC/requirements.txt" | sha256sum -c -
echo "3bd18def4da9cbec2766896fa160c34c0364de464ca3abd02d675c72620cf13c  $L/packs/ad5w_wheels39.tar" | sha256sum -c -
mkdir "$W/wheels"
tar -xf "$L/packs/ad5w_wheels39.tar" -C "$W/wheels"
python3 -m venv "$W/env"
PY=$W/env/bin/python
"$PY" -m pip install -q --no-index --find-links "$W/wheels" setuptools==69.5.1 wheel==0.43.0 > "$W/build.log" 2>&1
"$PY" -m pip install -q --no-index --find-links "$W/wheels" --no-build-isolation -r "$SRC/requirements.txt" >> "$W/build.log" 2>&1
"$PY" -m pip freeze > "$W/pip_freeze.txt"
export CUDA_LAUNCH_BLOCKING=1 TORCH_SHOW_CPP_STACKTRACES=1 PYTHONFAULTHANDLER=1
for mode in default math; do
 rc=0
 "$PY" -I "$SRC/probe.py" --mode "$mode" > "$W/$mode.log" 2>&1 || rc=$?
 printf '%s\n' "$rc" > "$W/${mode}_exit.txt"
 # Preserve each result before entering a fresh process for next mode.
 cp "$W/$mode.log" "$W/${mode}_exit.txt" "$DEST/"
 cmp "$W/$mode.log" "$DEST/$mode.log"
 cmp "$W/${mode}_exit.txt" "$DEST/${mode}_exit.txt"
done
printf 'Both fresh processes attempted; inspect individual exit statuses, never infer PASS from worker exit0.\n' > "$W/interpretation.txt"
