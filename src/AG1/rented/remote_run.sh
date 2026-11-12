#!/bin/bash
# AG1 on a rented Docker machine (image pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime, root, one GPU). No credentials.
#   remote_run.sh setup              check the uploaded packs, pin numpy / pillow, record versions, unpack once
#   remote_run.sh shard NAME         one generation shard (ag1_gen.py) -> results/NAME.tar + .sha256 + .log.csv
#   remote_run.sh spread GEN POOL    spread-matched renders (ag1_spread.py) -> results/AG1_spread_GEN_POOL.tar
# Inversion latents of shards made elsewhere (Athena) come from the uploaded needs_lat.tar; latents of shards made here
# are added to the same folder after each shard. AG1_ROOT / AG1_PY / AG1_MAXJOBS: DGX rehearsal only.
set -euo pipefail
B=${AG1_ROOT:-/root/ag1}
PY=${AG1_PY:-python}
cd "$B"
mkdir -p logs results lat
case "${1:?setup|shard|spread}" in
setup)
  (cd upload && sha256sum -c ag1_pack.tar.sha256 needs_lat.tar.sha256 ag1_spread.py.sha256) > logs/setup_hashes.txt
  if [ -z "${AG1_PY:-}" ]; then
    python -c "import torch, torchvision; print('torch==' + torch.__version__.split('+')[0]); print('torchvision==' + torchvision.__version__.split('+')[0])" > constraints.txt
    python -m pip install --no-cache-dir -c constraints.txt numpy==1.26.4 pillow==10.2.0 > logs/pip.log 2>&1 || { tail -20 logs/pip.log; exit 1; }
    python -c "import torch, torchvision, numpy, PIL; assert torch.__version__.startswith('2.2.1') and torchvision.__version__.startswith('0.17.1') and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0' and torch.cuda.is_available()"
  fi
  "$PY" -c "import sys, torch, torchvision, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'torchvision', torchvision.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'gpu', torch.cuda.get_device_name(0))" | tee logs/versions.txt
  "$PY" -m pip freeze > logs/pip_freeze.txt 2>/dev/null || true
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | tee logs/gpu.txt
  rm -rf work && mkdir work && cd work
  tar -xf ../upload/ag1_pack.tar
  sha256sum -c SHA256SUMS
  for f in gan_weights.tar gan_sg1.tar ag1_code.tar ag1_inputs.tar; do tar -xf "$f" && rm -f "$f"; done
  cp ../upload/ag1_spread.py ag1_code/
  cd .. && mkdir -p lat/mip1 lat/mip2 && tar -xf upload/needs_lat.tar -C lat     # needs_lat.tar holds mip1/... only
  df -h "$B" | tail -1 | tee logs/disk.txt
  echo SETUP_OK ;;
shard)
  S=${2:?shard}; W=$B/work; OUT=$B/out/$S
  rm -rf "$OUT"; mkdir -p "$OUT"
  set +e
  ( while :; do nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits >> "$OUT/gpumem.csv"; sleep 10; done ) & MON=$!
  read -r GEN NEEDS < <("$PY" -I -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['gen'], len(d['needs']))" "$W/ag1_inputs/shards/$S.json")
  LAT=(); [ "$NEEDS" -gt 0 ] && LAT=(--latents "$B/lat/$GEN")   # only dependent shards read stored latents
  mkdir -p "$B/lat/$GEN"
  "$PY" -I "$W/ag1_code/ag1_gen.py" --shard "$W/ag1_inputs/shards/$S.json" --inputs "$W/ag1_inputs" \
    --weights "$W/gan_weights" --sg1 "$W/gan_sg1/stylegan1_ffhq1024.pt" --out "$OUT" "${LAT[@]}" \
    ${AG1_MAXJOBS:+--max-jobs $AG1_MAXJOBS} > "logs/$S.log" 2>&1
  RC=$?; kill $MON 2>/dev/null; set -e
  tail -3 "logs/$S.log"
  [ "$RC" = 0 ] || { echo "SHARD_FAILED $S rc=$RC"; exit "$RC"; }
  if [[ "$S" != *smoke* ]]; then                                      # the check shard never feeds later shards
    cp "$OUT"/lat/inv_*.npz "$B/lat/$GEN/" 2>/dev/null || true        # per generator: names collide across them
    cp "$OUT"/lat/*_R2_*__s1.npz "$B/lat/$GEN/" 2>/dev/null || true
  fi
  tar -C "$B/out" -cf "results/$S.tar" "$S"
  (cd results && sha256sum "$S.tar" > "$S.tar.sha256"); cp "$OUT/log.csv" "results/$S.log.csv"
  echo "SHARD_DONE $S $(cut -c1-64 results/$S.tar.sha256)" ;;
spread)
  G=${2:?gen}; P=${3:?pool}; S=AG1_spread_${G}_${P}; W=$B/work; OUT=$B/out/$S
  rm -rf "$OUT"; mkdir -p "$OUT"
  "$PY" -I "$W/ag1_code/ag1_spread.py" --gen "$G" --pool "$P" --lat "$B/lat/$G" --inputs "$W/ag1_inputs" \
    --weights "$W/gan_weights" --sg1 "$W/gan_sg1/stylegan1_ffhq1024.pt" --out "$OUT" > "logs/$S.log" 2>&1 \
    || { tail -5 "logs/$S.log"; echo "SHARD_FAILED $S"; exit 1; }
  tar -C "$B/out" -cf "results/$S.tar" "$S"
  (cd results && sha256sum "$S.tar" > "$S.tar.sha256"); cp "$OUT/log.csv" "results/$S.log.csv"
  echo "SHARD_DONE $S $(cut -c1-64 results/$S.tar.sha256)" ;;
esac
