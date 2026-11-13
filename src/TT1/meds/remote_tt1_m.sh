#!/bin/bash
# TT1 MEDS extension (prereg_meds_block.md), run on se1d (A100 PCIe). Own folder /workspace/tt1m, own venv (system site
# packages + the PN1 pip pins), so the SE1 environment is untouched. Started by the driver only after SE1_DONE_411.
# Steps: pins; venv + versions asserted; extract tt1_pack + MEDS pack + nets; per network: TT1 fam-gate rows (rescore.py
# unchanged) -> gate_check_m.py (byte identity vs pn1fs); passing networks: MEDS rows (fam meds); one result tar; DONE.
# Args: TT1_PACK_SHA MEDS_PACK_SHA NETS_SHA
set -u
PSHA=${1:?}; MSHA=${2:?}; NSHA=${3:?}
B=${TT1M_B:-/workspace/tt1m}; T=TT1M_se1d; W=$B/work; R=$W/res/$T
mkdir -p "$B/results" "$B/logs" "$R/scores"
log() { echo "$(date +%FT%T) $*" | tee -a "$R/calls.log"; }
finish() {
  echo "$1" > "$R/rc"
  nvidia-smi --query-gpu=index,uuid,name,driver_version --format=csv,noheader > "$R/gpu.txt" 2>&1 || true
  tar -C "$W/res" -cf "$B/results/$T.tar" "$T" && (cd "$B/results" && sha256sum "$T.tar" > "$T.tar.sha256")
  (cd "$B/logs" && sha256sum * > "$B/results/logs_m.sha256") 2>/dev/null || true
  date > "$B/DONE_M"
}
abort() { log "FATAL $1"; finish "FATAL $1"; exit 1; }
log "start"
(cd "$B/bin" && sha256sum -c --quiet SHA256SUMS) || abort "bin pins"
[ "$(sha256sum < "$B/packs/tt1_pack.tar" | cut -c1-64)" = "$PSHA" ] || abort "tt1 pack pin"
[ "$(sha256sum < "$B/packs/tt1m_meds.tar" | cut -c1-64)" = "$MSHA" ] || abort "meds pack pin"
[ "$(sha256sum < "$B/packs/tt1m_nets.tar" | cut -c1-64)" = "$NSHA" ] || abort "nets pin"
[ "$(df --output=avail -B1G "$B" | tail -1 | tr -d ' ')" -ge 20 ] || abort "disk"
[ "${TT1M_TEST:-0}" = 1 ] || nvidia-smi --query-gpu=name --format=csv,noheader | grep -q "A100-PCIE" || abort "GPU model"
if [ "${TT1M_SKIP_VENV:-0}" != 1 ]; then
  [ -x "$B/venv/bin/python" ] || python -m venv --system-site-packages "$B/venv" || abort venv
  PY=$B/venv/bin/python
  $PY -c "import torch, torchvision; print('torch==' + torch.__version__.split('+')[0]); print('torchvision==' + torchvision.__version__.split('+')[0])" > "$B/constraints.txt" || abort torch
  $PY -m pip install --no-cache-dir -c "$B/constraints.txt" timm==1.0.27 huggingface_hub==0.36.2 safetensors==0.8.0 \
    numpy==1.26.4 pyyaml==6.0.3 pillow==10.2.0 > "$B/logs/pip.log" 2>&1 || abort pip
  $PY -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0'" || abort versions
else
  PY=${TT1M_PY:?}
fi
$PY -c "import sys, torch, timm, numpy, PIL; print(sys.version.split()[0], torch.__version__, torch.version.cuda, torch.backends.cudnn.version(), timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0)); print('cudnn.benchmark', torch.backends.cudnn.benchmark, 'matmul.allow_tf32', torch.backends.cuda.matmul.allow_tf32, 'cudnn.allow_tf32', torch.backends.cudnn.allow_tf32)" > "$R/versions.txt" || abort env
rm -rf "$W/tt1" "$W/tt1m" "$W/tt1mnets"
tar -C "$W" -xf "$B/packs/tt1_pack.tar" 2>/dev/null && (cd "$W/tt1" && sha256sum -c --quiet SHA256SUMS) || abort "tt1 sums"
tar -C "$W" -xf "$B/packs/tt1m_meds.tar" 2>/dev/null && (cd "$W/tt1m" && sha256sum -c --quiet SHA256SUMS) || abort "meds sums"
tar -C "$W" -xf "$B/packs/tt1m_nets.tar" 2>/dev/null && (cd "$W/tt1mnets" && sha256sum -c --quiet SHA256SUMS) || abort "nets sums"
log "packs ok"
export HF_HOME=$W/tt1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
NL=$(ls "$W/tt1mnets/nets"); [ "${TT1M_TEST:-0}" = 1 ] && NL=$(echo "$NL" | head -1)
for n in $NL; do
  SMAD_DATA=$W/tt1/data $PY "$W/tt1/bin/rescore.py" --resdir "$W/tt1mnets/nets/$n" --code "$W/tt1/code" --manifest tt1_score.csv \
    --fam gate --out "$R/scores/${n}__gate.npz" --workers 7 >> "$B/logs/m_score.log" 2>&1 || abort "gate score $n"
  log "gate scored $n"
done
$PY "$B/bin/gate_check_m.py" --scores "$R/scores" --ref "$W/tt1mnets/gate_ref" --out "$R/gate_m.json" > "$R/gate_m.txt" 2>&1 || abort "gate check"
log "$(cat "$R/gate_m.txt")"
PASSED=$($PY -c "import json; print(' '.join(json.load(open('$R/gate_m.json'))['passed']))")
[ "${TT1M_TEST:-0}" = 1 ] && PASSED=$NL      # test only: exercise the MEDS path whatever the gate says
for n in $PASSED; do
  SMAD_DATA=$W/tt1m/data $PY "$W/tt1/bin/rescore.py" --resdir "$W/tt1mnets/nets/$n" --code "$W/tt1/code" --manifest meds_score.csv \
    --fam meds --out "$R/scores/${n}__meds.npz" --workers 7 >> "$B/logs/m_score.log" 2>&1 || abort "meds score $n"
  log "meds scored $n"
done
finish 0
