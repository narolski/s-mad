#!/bin/bash
# Source-pinned new full40-epoch late-cohort fit. Root release required; never a retry.
set -euo pipefail
L=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5
SRC=$L/ad5_full_math_v2
SEED=${1:?seed}
KEEP=$L/logs/keep/ad5_full_math_v2_20261114/s$SEED
: "${TMPDIR:?}" "${SLURM_JOB_ID:?}"
case "$TMPDIR" in /mnt/lscratch/*) ;; *) echo not-local-TMPDIR;exit 2;; esac
python3 -I -c "import sys;sys.path.insert(0,'/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_full_math_v2');import verify;verify.release(int(sys.argv[1]))" "$SEED"
[ -d "$KEEP/technical" ] || exit 90
S=$TMPDIR/ad5_full_math_v2_s$SEED
mkdir -p "$S/code" "$S/wheels" "$S/crop"
ln -s "$KEEP/technical" "$S/out"
export PYTHONUNBUFFERED=1
export ARM=B AD5_SEED=$SEED AD5_NO_TEST=1 CUDA_LAUNCH_BLOCKING=1 TORCH_SHOW_CPP_STACKTRACES=1 PYTHONFAULTHANDLER=1
for spec in 'ad5w_code:94964c3689aa866ad7700f4b86496590c1b353e8e8be59173158e7b46c35d6ee' 'ad5w_wheels39:3bd18def4da9cbec2766896fa160c34c0364de464ca3abd02d675c72620cf13c' 'smdd_train_cropped:3189e52af12e2853b06c86993b1b8b5cfef891fda749395778492e3445924900'; do
 name=${spec%%:*};expected=${spec#*:}
 [ "$(sha256sum "$L/packs/$name.tar"|cut -c1-64)" = "$expected" ] || exit 3
done
# Actual weight/data access starts only here, inside separately released native allocation.
tar -xf "$L/packs/ad5w_code.tar" -C "$S/code"
tar -xf "$L/packs/ad5w_wheels39.tar" -C "$S/wheels"
tar -xf "$L/packs/smdd_train_cropped.tar" -C "$S/crop"
python3 -I "$SRC/patch.py" "$S/code" > "$S/out/PATCH_PROOF.json"
python3 -m venv "$S/env"
PY=$S/env/bin/python
"$PY" -m pip install -q --no-index --find-links "$S/wheels" setuptools==69.5.1 wheel==0.43.0
"$PY" -m pip install -q --no-index --find-links "$S/wheels" --no-build-isolation -r "$S/code/src/AD5/env/madation_requirements.txt"
"$PY" -m pip freeze > "$S/out/pip_freeze.txt"
"$PY" -I -c "import sys,torch;assert sys.version_info[:2]==(3,9);assert torch.__version__=='2.0.1+cu118';assert torch.version.cuda=='11.8';assert torch.cuda.device_count()==1;assert 'H100' in torch.cuda.get_device_name(0);print(sys.version,torch.__version__,torch.version.cuda,torch.cuda.get_device_name(0))" > "$S/out/environment.txt"
# Exact full original CSV, prefix-only rewrite, no subsampling.
[ "$(sha256sum "$S/crop/smdd_train_cropped_rel.csv" | cut -c1-64)" = 83c01705e140843afa6cb4c89765d0528ff21e2f444aee23aa50de49eaf894a3 ] || exit 5
sed "s#^CROP_ROOT#$S/crop#" "$S/crop/smdd_train_cropped_rel.csv" > "$S/train.csv"
[ "$(( $(wc -l < "$S/train.csv") - 1 ))" = 39723 ] || exit 4
sha256sum "$S/crop/smdd_train_cropped_rel.csv" > "$S/out/canonical_full_csv_sha256.txt"
sha256sum "$S/train.csv" > "$S/out/runtime_train_csv_sha256.txt" 
sha256sum "$S/code/weights/clip_vitb16_openai.bin" > "$S/out/runtime_weight_sha256.txt"
[ "$(cut -c1-64 "$S/out/runtime_weight_sha256.txt")" = 53b401837e5baa82115d3b6db60c6fff43cfd1a6412e48ed0193d54a69d2f993 ] || exit 6
export AD5_TRAIN_CSV=$S/train.csv AD5_OUT=$S/run AD5_CLIP_SD=$S/code/weights/clip_vitb16_openai.bin AD5_FULL_OUT=$S/out AD5_CROP_ROOT=$S/crop
rc=0
(cd "$S/code/build/madation_src/src" && OMP_NUM_THREADS=4 "$PY" -I -m torch.distributed.launch --nproc_per_node=1 --nnodes=1 --node_rank=0 --master_addr=localhost --master_port=$((12000 + SEED)) config.py --debug=True --dataset_name=MADTrain --training_type=MAD_training --lr_model=1e-5 --lr_header=1e-4 --backbone_size=ViT-B/16 --lora_dropout=0.4 --lora_r=2 --lora_a=4 --batch_size=256 --num_epoch=40 --save_every=40 --log_every=50) || rc=$?
printf '%s\n' "$rc" > "$S/out/child_exit.txt"
[ "$rc" = 0 ] || exit "$rc"
"$PY" -I -c "import json;d=json.load(open('$S/out/MULTI_RESULT.json'));assert d['status']=='FULL_B_6200_UPDATES_AND_CHECKPOINT_ROUNDTRIP_COMPLETE';assert d['optimizer_model_updates']==d['optimizer_header_updates']==d['effective_batches']==6200"
# Only this producer's original epoch40 checkpoint pair is preserved; no scorer/evaluation.
exit 0
