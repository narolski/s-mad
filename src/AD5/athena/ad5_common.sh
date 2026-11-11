# Retrains of released methods (AD5): shared shell functions for the Athena jobs. Sourced by every AD5 sbatch file.
# Rules (ATHENA.md): build environments inside jobs, all work in $SCRATCH_LOCAL, one tar in / one tar out per task.
ROOT=/net/pr2/projects/plgrid/plggrestoration
G=$ROOT/smad-next
PK=$G/packs/AD5
RS=$G/results/AD5
EN=$G/envs/AD5
LG=$G/logs
# Work area: the RAM disk $MEMFS (-C memfs). ATHENA.md, 11 Nov: -C localfs gives only 4.0 GB (our first smoke job,
# 3544190, died there with "No space left on device"); memfs counts toward --mem (at most 120G per GPU).
: "${MEMFS:?RAM disk required (-C memfs)}"
SCRATCH_LOCAL=$MEMFS
export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
export PIP_NO_CACHE_DIR=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1

untar_checked() {  # untar_checked TAR DEST [MEMBER...]: verify TAR against TAR.sha256, then extract (members) into DEST
  local t=$1 d=$2; shift 2
  ( cd "$(dirname "$t")" && sha256sum -c "$(basename "$t").sha256" ) || { echo "HASH MISMATCH $t"; return 1; }
  mkdir -p "$d"; tar -xf "$t" -C "$d" "$@"
}

build_env() {  # build_env NAME REQUIREMENTS WHEEL_TAR: venv under $EN/NAME from local wheels only (no index)
  local name=$1 req=$2 wt=$3 e=$EN/$1 w=$SCRATCH_LOCAL/wheels_$1
  if [ -f "$e/AD5_ENV_OK" ]; then echo "env $name exists"; return 0; fi
  untar_checked "$wt" "$w"
  rm -rf "$e"; python3 -m venv "$e"
  "$e/bin/python" -m pip install -q --no-index --find-links "$w" setuptools==69.5.1 wheel==0.43.0 2>/dev/null \
    || "$e/bin/python" -m pip install -q --no-index --find-links "$w" setuptools wheel
  "$e/bin/python" -m pip install -q --no-index --find-links "$w" --no-build-isolation -r "$req"
  "$e/bin/python" -m pip freeze > "$e/pip_freeze.txt"
  touch "$e/AD5_ENV_OK"
  echo "env $name built"; cat "$e/pip_freeze.txt"
}

gpu_monitor() {  # gpu_monitor FILE: sample GPU memory every 5 s in the background; prints the PID
  ( while :; do nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits >> "$1"; sleep 5; done ) \
    > /dev/null 2>&1 &
  echo $!
}

keep_log() {  # keep_log FILE...: copy logs out of the RAM disk (lost when the job ends) to logs/AD5_keep/<job>/
  local k=$LG/AD5_keep/${SLURM_JOB_ID:-nojob}_${SLURM_ARRAY_TASK_ID:-0}; mkdir -p "$k"; cp "$@" "$k/" 2>/dev/null || true
  echo "logs kept in $k"
}

peak_mib() { awk -F", " '{if ($2+0>m) m=$2+0} END {print m+0}' "$1"; }
