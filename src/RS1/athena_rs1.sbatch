#!/bin/bash -l
#SBATCH -J smadnext-RS1
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=110G
#SBATCH --gres=gpu:1
#SBATCH --time=04:00:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/RS1-%j.out
# Own-crop re-score of the audit rows (RS1) on Athena: build envs/RS1 (facenet-pytorch 2.6.0 wheel from the pack,
# opencv-python-headless 4.11.0.86, requests) on top of the shared venv, unpack the pack in node-local scratch, crop
# with the byte-identical AR1 crop_rgb.py (3 shards); all work in the RAM disk $MEMFS (-C memfs: about 30 GB used), score seven releases with the byte-identical AR1 score.py,
# re-detect the 32 crop-check files, and write one result tar (+ .sha256). RS1_LIMIT=8 -> smoke (8 images per stage).
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable; using system python"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs; localfs is only 4 GB on Athena)}"
LIMIT=${RS1_LIMIT:-0}
TAG=$([ "$LIMIT" = 0 ] && echo prod || echo smoke)_$SLURM_JOB_ID
export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
W=$MEMFS/rs1; mkdir -p "$W/out/logs"; cd "$W"
PY=$G/envs/RS1/venv/bin/python
SITE=$W/nosite
hostname | tee "$W/out/logs/host.txt"; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | tee -a "$W/out/logs/host.txt"
echo "unpack $(date +%T)"
H=$(sha256sum "$G/packs/RS1/rs1a_pack.tar" | cut -d' ' -f1); [ "$H" = "$(cut -d' ' -f1 "$G/packs/RS1/rs1a_pack.tar.sha256")" ] || { echo "pack sha mismatch"; exit 3; }
mkdir -p "$W/pack"; tar -xf "$G/packs/RS1/rs1a_pack.tar" -C "$W/pack"
if [ -f "$G/packs/RS1/rs1a_pack_amend.tar" ]; then       # amendment 2 images and the full manifest
  H=$(sha256sum "$G/packs/RS1/rs1a_pack_amend.tar" | cut -d' ' -f1); [ "$H" = "$(cut -d' ' -f1 "$G/packs/RS1/rs1a_pack_amend.tar.sha256")" ] || { echo "pack2 sha mismatch"; exit 3; }
  tar -xf "$G/packs/RS1/rs1a_pack_amend.tar" -C "$W/pack"
fi
R=$W/pack
# own environment (the shared venv does not exist yet): the WCSS-container versions plus the crop packages
if ! "$PY" -I -c "import torch, timm, cv2, facenet_pytorch, requests, safetensors" 2>/dev/null; then
  python3 -m venv --clear "$G/envs/RS1/venv"
  P="$PY -m pip --require-virtualenv --no-cache-dir"
  $P install -q -U "pip==24.3.1"
  $P install -q torch==2.2.1 torchvision==0.17.1 --index-url https://download.pytorch.org/whl/cu121
  $P install -q "timm==1.0.27" "huggingface_hub==0.36.2" "safetensors==0.8.0" "numpy==1.26.4" "pyyaml==6.0.3" \
    "pillow==10.2.0" "opencv-python-headless==4.11.0.86" "requests==2.32.3"
  $P install -q --no-deps "$R/wheels/facenet_pytorch-2.6.0-py3-none-any.whl"
fi
"$PY" -m pip freeze > "$W/out/logs/pip_freeze.txt"
"$PY" -I -c "import sys, cv2, facenet_pytorch, torch, timm, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'cv2', cv2.__version__, 'gpu', torch.cuda.get_device_name(0)); assert torch.cuda.is_available() and torch.__version__.startswith('2.2.1') and numpy.__version__ == '1.26.4'" | tee "$W/out/logs/versions.txt"
# absolute-path lists
"$PY" -I - "$R" "$LIMIT" <<'EOF'
import csv, sys, pathlib
R, lim = pathlib.Path(sys.argv[1]), int(sys.argv[2])
rows = list(csv.DictReader(open(R / "manifests/athena_manifest.csv")))
for name, origin in (("tocrop", "crop"), ("check", "check"), ("a46", "a46")):
    sel = [r for r in rows if r["origin"] == origin]
    if lim:
        # smoke: 8 images of every set (new crops and reused A46 crops), for the DGX equivalence check
        seen, keep = {}, []
        for r in sel:
            k = r["set"]
            if seen.get(k, 0) < lim:
                seen[k] = seen.get(k, 0) + 1; keep.append(r)
        sel = keep
    with open(R / f"manifests/{name}_abs.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "path"]); [w.writerow([r["id"], str(R / r["relpath"])]) for r in sel]
    print(name, len(sel))
EOF
echo "crop $(date +%T)"
N=3
for i in $(seq 0 $((N-1))); do
  "$PY" -I "$R/code/rs1/athena_run.py" "$R" "$SITE" crop --manifest "$R/manifests/tocrop_abs.csv" --out "$W/crops/main" --shard $i/$N > "$W/out/logs/crop_shard$i.log" 2>&1 &
done
FAIL=0; for j in $(jobs -p); do wait $j || FAIL=1; done
[ $FAIL = 0 ] || { tail -20 "$W"/out/logs/crop_shard*.log; exit 4; }
"$PY" -I "$R/code/rs1/athena_run.py" "$R" "$SITE" crop --manifest "$R/manifests/check_abs.csv" --out "$W/crops/check" > "$W/out/logs/crop_check.log" 2>&1
echo "merge $(date +%T)"
"$PY" -I - "$R" "$W" <<'EOF'
import csv, sys, pathlib, glob, collections
R, W = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out, st = [], collections.Counter()
for f in sorted(glob.glob(str(W / "crops/main/crops_*of3.csv"))):
    for r in csv.DictReader(open(f)):
        st[r["status"].split(":")[0]] += 1
        if r["status"] == "retained" or r["status"].startswith("flag:"):
            out.append((r["id"], r["path"]))
out += [(r["id"], r["path"]) for r in csv.DictReader(open(R / "manifests/a46_abs.csv"))]
with open(W / "score_all.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["id", "path"]); w.writerows(out)
print("score list", len(out), dict(st))
EOF
echo "score $(date +%T)"
mkdir -p "$W/scores"
for d in madation_vitb16 madation_vitl14 madation_fe_vitl14 madation_fe_vitb16 madation_fs_vitb16 madation_fs_vitl14 mixfacenet_mad_smdd; do
  t0=$(date +%s)
  "$PY" -I "$R/code/rs1/athena_run.py" "$R" "$SITE" score --det $d --mode rel --manifest "$W/score_all.csv" --out-dir "$W/scores" --tag rel_${d}__athena --workers 6 --bs 32 > "$W/out/logs/score_$d.log" 2>&1
  echo "$d $(( $(date +%s) - t0 )) s" | tee -a "$W/out/logs/score_times.txt"
done
echo "pack results $(date +%T)"
mkdir -p "$W/out/crops" "$W/out/scores"
cp "$W"/crops/main/crops_*.csv "$W"/crops/main/boxes_*.jsonl "$W/out/crops/"
cp "$W/crops/check/crops.csv" "$W/out/crops/check_crops.csv"; cp "$W/crops/check/boxes.jsonl" "$W/out/crops/check_boxes.jsonl"
cp "$W"/scores/scores_*.npz "$W/out/scores/"; cp "$W/score_all.csv" "$W/out/"
mkdir -p "$G/results/RS1"
tar -cf "$G/results/RS1/rs1a_$TAG.tar" -C "$W/out" .
( cd "$G/results/RS1" && sha256sum "rs1a_$TAG.tar" > "rs1a_$TAG.tar.sha256" )
echo "RS1_DONE $TAG $(date +%T)"
