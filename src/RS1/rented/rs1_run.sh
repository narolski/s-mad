#!/bin/bash
# Own-crop re-score of the audit rows (RS1), amendment 5: the same pipeline as src/RS1/athena_rs1.sbatch on one rented
# Docker machine (image pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime, root, one GPU).
#   bash rs1_run.sh setup                 -> pinned packages into the image's Python, versions to $G/setup_versions.txt
#   RS1_VARIANT=v1|v2 RS1_LIMIT=8|0 bash rs1_run.sh run
# Layout on the machine: G=/root/rs1 with packs/ (three tars + .sha256), image_preprocess.py, results/, work/.
set -eo pipefail
G=/root/rs1
if [ "${1:-}" = setup ]; then
  python3 -m pip install --no-cache-dir -q "timm==1.0.27" "huggingface_hub==0.36.2" "safetensors==0.8.0" "numpy==1.26.4" \
    "pyyaml==6.0.3" "pillow==10.2.0" "opencv-python-headless==4.11.0.86" "requests==2.32.3" "tqdm==4.67.1"
  # the image's conda Pillow 10.2.0 links a different libjpeg than the PyPI wheel used on Athena: replace it
  python3 -m pip install --no-cache-dir -q --force-reinstall --no-deps "pillow==10.2.0"
  python3 -c "import PIL.features as F; print('libjpeg_turbo', F.version('libjpeg_turbo'), 'jpg', F.version('jpg'))" | tee $G/setup_libjpeg.txt
  WH=$G/pack/wheels/facenet_pytorch-2.6.0-py3-none-any.whl
  [ -f $WH ] || { mkdir -p $G/whl && tar -xf $G/packs/rs1a_pack.tar -C $G/whl wheels/facenet_pytorch-2.6.0-py3-none-any.whl; WH=$G/whl/wheels/facenet_pytorch-2.6.0-py3-none-any.whl; }
  python3 -m pip install --no-cache-dir -q --no-deps $WH
  python3 -m pip freeze > $G/setup_pip_freeze.txt
  python3 -c "import torch, torchvision, timm, cv2, numpy, PIL, tqdm, facenet_pytorch; print('torch', torch.__version__, 'cuda', torch.version.cuda, 'tv', torchvision.__version__, 'timm', timm.__version__, 'cv2', cv2.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'tqdm', tqdm.__version__, 'gpu', torch.cuda.get_device_name(0))" | tee $G/setup_versions.txt
  exit 0
fi
[ "${1:-}" = run ] || { echo "usage: rs1_run.sh setup | run"; exit 2; }
set -u
LIMIT=${RS1_LIMIT:-0}
VAR=${RS1_VARIANT:-both}
VARS=$([ "$VAR" = both ] && echo "v1 v2" || echo "$VAR")
TAG=$([ "$LIMIT" = 0 ] && echo prod || echo smoke)_${VAR}_rented
W=$G/work/$TAG; rm -rf "$W"; mkdir -p "$W/out/logs"; cd "$W"
export TMPDIR=$W/tmp; mkdir -p "$TMPDIR"
PY=python3
SITE=$W/nosite
SMDD=$G/image_preprocess.py
hostname | tee "$W/out/logs/host.txt"; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | tee -a "$W/out/logs/host.txt"
[ "$(sha256sum "$SMDD" | cut -d' ' -f1)" = bcaecd2970cd8d95e37b005f793035f2d0222219bf99215edc1168519fe5ee2c ] || { echo "SMDD script not at its pin"; exit 3; }
echo "unpack $(date +%T)"; df -h /root | tail -1
if [ ! -f "$G/pack/.unpacked" ]; then                      # unpack the three packs once (hash-checked)
  mkdir -p "$G/pack"
  for p in rs1a_pack rs1a_pack_amend rs1a_pack_raw; do
    H=$(sha256sum "$G/packs/$p.tar" | cut -d' ' -f1); [ "$H" = "$(cut -d' ' -f1 "$G/packs/$p.tar.sha256")" ] || { echo "$p sha mismatch"; exit 3; }
    tar -xf "$G/packs/$p.tar" -C "$G/pack" && rm -f "$G/packs/$p.tar"   # 80 GB disk: originals stay on DGX/Athena
  done
  touch "$G/pack/.unpacked"
fi
R=$G/pack
# environment: built by "rs1_run.sh setup" (see top)
"$PY" -m pip freeze > "$W/out/logs/pip_freeze.txt"
"$PY" -I -c "import sys, cv2, facenet_pytorch, torch, timm, numpy, PIL, tqdm; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'cv2', cv2.__version__, 'tqdm', tqdm.__version__, 'gpu', torch.cuda.get_device_name(0)); assert torch.cuda.is_available() and torch.__version__.startswith('2.2.1') and numpy.__version__ == '1.26.4'" | tee "$W/out/logs/versions.txt"
# input list (every image that needs a crop; the reused A46 crops are not used) and the 3 shard folders for variant 1
N=3
"$PY" -I - "$R" "$W" "$LIMIT" "$N" <<'EOF'
import csv, sys, pathlib, os
R, W, lim, n = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
rows = [r for r in csv.DictReader(open(R / "manifests/athena_manifest.csv")) if r["origin"] == "crop"]
if lim:
    seen, keep = {}, []
    for r in rows:
        if seen.get(r["set"], 0) < lim:
            seen[r["set"]] = seen.get(r["set"], 0) + 1; keep.append(r)
    rows = keep
with open(W / "inputs_abs.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["id", "path"]); [w.writerow([r["id"], str(R / r["relpath"])]) for r in rows]
for i in range(n):
    (W / f"v1in/s{i}").mkdir(parents=True, exist_ok=True)
for k, r in enumerate(rows):
    src = R / r["relpath"]
    os.symlink(src, W / f"v1in/s{k % n}" / src.name)          # name = <id><ext>, as stored in the pack
print("inputs", len(rows))
EOF
mkdir -p "$W/crops/v1" "$W/crops/v2"
if [[ " $VARS " == *" v1 "* ]]; then
echo "variant 1: SMDD image_preprocess.py unchanged $(date +%T)"
for i in $(seq 0 $((N-1))); do
  ( cd "$W" && "$PY" -I "$SMDD" --in_folder "$W/v1in/s$i" --out_folder "$W/crops/v1" > "$W/out/logs/v1_shard$i.log" 2>&1 ) &
done
FAIL=0; for j in $(jobs -p); do wait $j || FAIL=1; done
[ $FAIL = 0 ] || { tail -20 "$W"/out/logs/v1_shard*.log; exit 4; }
fi
if [[ " $VARS " == *" v2 "* ]]; then
echo "variant 2: corrected crop, PNG (AR1 crop_rgb.py unchanged) $(date +%T)"
for i in $(seq 0 $((N-1))); do
  "$PY" -I "$R/code/rs1/athena_run.py" "$R" "$SITE" crop --manifest "$W/inputs_abs.csv" --out "$W/crops/v2" --shard $i/$N > "$W/out/logs/v2_shard$i.log" 2>&1 &
done
FAIL=0; for j in $(jobs -p); do wait $j || FAIL=1; done
[ $FAIL = 0 ] || { tail -20 "$W"/out/logs/v2_shard*.log; exit 4; }
fi
echo "lists $(date +%T)"
"$PY" -I - "$W" <<'EOF'
import csv, sys, pathlib, glob, collections, json
W = pathlib.Path(sys.argv[1])
inp = list(csv.DictReader(open(W / "inputs_abs.csv")))
v1, miss1 = [], []
for r in inp:
    p = W / "crops/v1" / pathlib.Path(r["path"]).name
    (v1.append((r["id"], str(p))) if p.exists() else miss1.append(r["id"]))
v2, st = [], collections.Counter()
for f in sorted(glob.glob(str(W / "crops/v2/crops_*of3.csv"))):
    for r in csv.DictReader(open(f)):
        st[r["status"].split(":")[0]] += 1
        if r["status"] == "retained" or r["status"].startswith("flag:"):
            v2.append((r["id"], r["path"]))
for name, rows in (("score_v1.csv", v1), ("score_v2.csv", v2)):
    with open(W / name, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "path"]); w.writerows(rows)
json.dump(dict(n_inputs=len(inp), v1_written=len(v1), v1_missing=miss1, v2_status=dict(st)),
          open(W / "out/crop_summary.json", "w"), indent=1)
print("v1", len(v1), "missing", len(miss1), "| v2", len(v2), dict(st))
EOF
echo "score $(date +%T)"
mkdir -p "$W/scores"
for v in $VARS; do
  for d in madation_vitb16 madation_vitl14 madation_fe_vitl14 madation_fe_vitb16 madation_fs_vitb16 madation_fs_vitl14 mixfacenet_mad_smdd; do
    t0=$(date +%s)
    "$PY" -I "$R/code/rs1/athena_run.py" "$R" "$SITE" score --det $d --mode rel --manifest "$W/score_$v.csv" --out-dir "$W/scores" --tag rel_${d}__$v --workers 6 --bs 32 > "$W/out/logs/score_${d}__$v.log" 2>&1
    echo "$d $v $(( $(date +%s) - t0 )) s" | tee -a "$W/out/logs/score_times.txt"
  done
done
echo "border check $(date +%T)"
# amendment 2 (d): fraction of black pixels (all three channels 0) in every crop, per crop file (summarised on the DGX)
"$PY" -I - "$W" "$VARS" <<'EOF'
import csv, sys, pathlib, cv2
W, vars_ = pathlib.Path(sys.argv[1]), sys.argv[2].split()
with open(W / "out/border_fraction.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["variant", "id", "black_frac"])
    for v in vars_:
        for r in csv.DictReader(open(W / f"score_{v}.csv")):
            im = cv2.imread(r["path"], cv2.IMREAD_COLOR)
            w.writerow([v, r["id"], "" if im is None else round(float((im.max(axis=2) == 0).mean()), 6)])
EOF
echo "pack results $(date +%T)"
mkdir -p "$W/out/scores" "$W/out/v2meta"
cp "$W"/scores/scores_*.npz "$W/out/scores/"; cp "$W"/score_v1.csv "$W"/score_v2.csv "$W"/inputs_abs.csv "$W/out/"
cp "$W"/crops/v2/crops_*.csv "$W"/crops/v2/boxes_*.jsonl "$W/out/v2meta/" 2>/dev/null || true
( cd "$W/crops" && find v1 v2 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) -print0 | sort -z | xargs -0 sha256sum > "$W/out/crops_sha256.txt" )
mkdir -p "$G/results"
# small result tar (scores, lists, logs, crop sha256 list; copied back) and the crop tar (stays on Athena: disk rule)
tar -cf "$G/results/rs1a_$TAG.tar" -C "$W/out" .
tar -cf "$G/results/rs1a_${TAG}_crops.tar" -C "$W" $(for v in $VARS; do echo crops/$v; done)
( cd "$G/results" && sha256sum "rs1a_$TAG.tar" > "rs1a_$TAG.tar.sha256" && sha256sum "rs1a_${TAG}_crops.tar" > "rs1a_${TAG}_crops.tar.sha256" )
echo "RS1_DONE $TAG $(date +%T)"
