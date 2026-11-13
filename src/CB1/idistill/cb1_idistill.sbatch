#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --no-requeue
#SBATCH --job-name=cb1ids
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/logs/CB1/cb1ids-%x-%j.out
# Competitor baselines (CB1): IDistill retrain from the authors' code (commit 0473bb43, paths/seed/last-save patch
# idistill_cb1.patch). Submit with --gres=gpu:hopper:1,storage:local:150G --time=... and
#   --export=ALL,STAGE=ae        crop (SMDD release crop script, unchanged) + autoencoder (300 epochs) + latents
#   --export=ALL,STAGE=cls,SEED=401|402|403   classifier (needs results/CB1/idistill_ae.tar; exits within a minute if absent)
#   add SMOKE=1 for the smoke (both stages on small subsets, 2 AE epochs, 1 classifier epoch).
# Everything in $TMPDIR (local NVMe): packs untarred there, venv built there from wheels, one tar back to Lustre.
set -euo pipefail
L=${CB1_L:-/lustre/pd03/hpc-narolski-1790461090/smad-next}; P=$L/packs/CB1; R=$L/results/CB1; mkdir -p $R   # CB1_L: rented variant root
STAGE=${STAGE:?ae|cls}; SM=${SMOKE:-}
case $STAGE in ae) T=idistill_ae ;; cls) T=idistill_cls_s${SEED:?} ;; *) exit 2 ;; esac
[ -n "$SM" ] && T=${T}_smoke
[ -f $R/$T.tar.sha256 ] && { echo "$T done already"; exit 0; }
AE=$R/idistill_ae${SM:+_smoke}.tar
if [ $STAGE = cls ]; then
  [ -f $AE.sha256 ] || { echo "no autoencoder result $AE: nothing to do"; exit 1; }
  ( cd $R && sha256sum -c $(basename $AE).sha256 ) || { echo "HASH MISMATCH $AE"; exit 3; }
fi
: "${TMPDIR:?local scratch required}"; W=$TMPDIR/ids; mkdir -p $W/out
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; python3 --version; date
PK="idistill_code idistill_data smdd_train_cropped"; case "${CB1_PIP:-}" in online|dgx) ;; *) PK="$PK ad5w_wheels39" ;; esac
for p in $PK; do ( cd $P && sha256sum -c $p.tar.sha256 ) || { echo "HASH MISMATCH $p"; exit 3; }; done
tar -xf $P/idistill_code.tar -C $W; mkdir -p $W/wheels $W/smdd $W/data
case "${CB1_PIP:-}" in online|dgx) ;; *) tar -xf $P/ad5w_wheels39.tar -C $W/wheels ;; esac
tar -xf $P/smdd_train_cropped.tar -C $W/smdd; mv $W/smdd/os25k_bf_t $W/smdd/os25k_bf_t_cropped; mv $W/smdd/m15k_t $W/smdd/m15k_t_cropped
t0=$(date +%s)
if [ "${CB1_PIP:-}" = dgx ]; then   # DGX variant (amendment 3): program venv (torch 2.12, ARM/GB10) + extra packages dir
  PY=/home/narolski/mambamorph-code/.venv-spark/bin/python; export CB1_EXTRA_SITE=/mnt/t7/smad_next/CB1/site_idistill_dgx
  export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
elif [ "${CB1_PIP:-}" = online ]; then
  python3 -m venv $W/env; PY=$W/env/bin/python   # rented variant: the same versions as the WCSS wheel house, from PyPI
  $PY -m pip install -q torch==2.0.1 torchvision==0.15.2 numpy==1.22.4 pandas==1.5.0 scikit-learn==1.1.1 \
      opencv-python-headless==4.5.5.64 tqdm==4.64.0 Pillow==9.1.1 facenet-pytorch==2.5.2 tensorboard==2.17.1
else
  python3 -m venv $W/env; PY=$W/env/bin/python
  WH=$(find $W/wheels -name 'torch-2.0.1*.whl' -printf '%h' -quit)
  $PY -m pip install -q --no-index --find-links $WH torch==2.0.1 torchvision==0.15.2 numpy pandas scikit-learn opencv-python-headless tqdm Pillow facenet-pytorch tensorboard
fi
$PY -m pip freeze > $W/out/pip_freeze.txt; [ -n "${CB1_EXTRA_SITE:-}" ] && ls $CB1_EXTRA_SITE >> $W/out/pip_freeze.txt; echo "env built in $(( $(date +%s) - t0 )) s"
C=$W/cb1/code; ST=$W/cb1/stubs; RUN="$PY -I $W/cb1/run_code.py $C $ST"
$PY -I -c "import os,sys; sys.path[:0]=[p for p in os.environ.get('CB1_EXTRA_SITE','').split(':') if p]; import torch, torchvision, cv2, sklearn, facenet_pytorch, tensorboard; print(torch.__version__, torch.cuda.get_device_name(0))"
( n=0; while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> $W/out/gpu.csv; sleep 30; n=$((n+1))
    if [ $((n % 60)) = 0 ]; then mkdir -p $R/${T}_partial   # review F4: checkpoints and logs leave TMPDIR every 30 min
      find $W/out -maxdepth 4 \( -name '*_best.pt' -o -name '*.pt' -o -name '*.pt.valbest' -o -name '*.log' \) -exec cp {} $R/${T}_partial/ \; ; fi
  done ) >/dev/null 2>&1 &
MP=$!
crop() {  # SMDD release crop script, unchanged: image_preprocess.py --in_folder --out_folder
  ( cd $W/cb1/smdd && $PY -I $W/cb1/run_code.py $W/cb1/smdd $ST image_preprocess.py --in_folder "$1" --out_folder "$2" ) > "$3" 2>&1
  echo "crop $(basename $1): $(ls $1 | wc -l) in, $(ls $2 | wc -l) out"
}
if [ $STAGE = ae ]; then
  tar -xf $P/idistill_data.tar -C $W/data
  if [ -n "$SM" ]; then  # smoke subsets
    for d in $W/data/eval_raw/*; do ls $d | tail -n +17 | sed "s#^#$d/#" | xargs rm -f; done
    ls $W/smdd/os25k_bf_t_cropped | tail -n +257 | sed "s#^#$W/smdd/os25k_bf_t_cropped/#" | xargs rm -f
    ls $W/smdd/m15k_t_cropped | tail -n +129 | sed "s#^#$W/smdd/m15k_t_cropped/#" | xargs rm -f
    keep=$(ls $W/smdd/m15k_t_cropped | sed -E 's/morphed_(img[0-9]+)_(img[0-9]+)\.png/\1.png\n\2.png/' | sort -u)
    mkdir $W/data/m_keep; for k in $keep; do mv $W/data/os25k_m_t/$k $W/data/m_keep/; done; rm -rf $W/data/os25k_m_t; mv $W/data/m_keep $W/data/os25k_m_t
  fi
  mkdir -p $W/out/croplogs
  crop $W/data/os25k_m_t $W/smdd/os25k_m_t_cropped $W/out/croplogs/os25k_m_t.log
  for d in $W/data/eval_raw/*; do crop $d $W/eval_crop/$(basename $d) $W/out/croplogs/$(basename $d).log; done
  EP=300; [ -n "$SM" ] && EP=2
  t1=$(date +%s)
  ( cd $C && $RUN train_autoencoder.py --data_dir $W/smdd/os25k_bf_t_cropped --dataset BonaFideImages --model UNetAutoencoder \
      --emb_size 128 --batchsize 32 --imgsize 224 --epochs $EP --lr 1e-4 --results_dir $W/out/ae --num_workers 8 ${AE_RESUME:+--resume --checkpoint $AE_RESUME} )   # AE_RESUME: authors' resume from a copied *_best.pt > $W/out/ae_train.log 2>&1
  echo "autoencoder: $(( $(date +%s) - t1 )) s"; { grep -E "^Train Loss" $W/out/ae_train.log || true; } | tail -3
  CK=$(find $W/out/ae -name '*_best.pt' | head -1); echo "AE checkpoint $CK"
  ( cd $C && $RUN inference_autoencoder.py --data_dir $W/smdd/os25k_bf_t_cropped --data_dir $W/smdd/os25k_m_t_cropped \
      --new_data_dir $W/lat --dataset BonaFideImages --model UNetAutoencoder --emb_size 128 --imgsize 224 --checkpoint $CK ) > $W/out/ae_infer.log 2>&1
  echo "latents: $(ls $W/lat/os25k_bf_t_cropped | wc -l) bona fide, $(ls $W/lat/os25k_m_t_cropped | wc -l) contributors"
  tar -cf $W/out/lat.tar -C $W lat; tar -cf $W/out/crops.tar -C $W eval_crop -C $W/smdd os25k_m_t_cropped
  ( cd $W/out && find . -type f ! -name '*.tar' | LC_ALL=C sort | xargs sha256sum > OUT_SHA256SUMS )
fi
if [ $STAGE = cls ] || [ -n "$SM" ]; then
  if [ $STAGE = cls ]; then
    tar -xf $AE -C $W/out; tar -xf $W/out/lat.tar -C $W; tar -xf $W/out/crops.tar -C $W
    mv $W/os25k_m_t_cropped $W/smdd/ 2>/dev/null || true
    [ -n "$SM" ] && { ls $W/smdd/os25k_bf_t_cropped | tail -n +257 | sed "s#^#$W/smdd/os25k_bf_t_cropped/#" | xargs rm -f; ls $W/smdd/m15k_t_cropped | tail -n +129 | sed "s#^#$W/smdd/m15k_t_cropped/#" | xargs rm -f; }
  fi
  S=${SEED:-401}; EPC=250; [ -n "$SM" ] && EPC=6
  $PY -I $W/cb1/make_csvs.py train $W/smdd $W/lat | tee $W/out/train_csv_s$S.log
  mkdir -p $W/frll; $PY -I $W/cb1/make_csvs.py frll $W/eval_crop $W | tee -a $W/out/train_csv_s$S.log
  t1=$(date +%s)
  ( cd $C && IDS_LAT=$W/lat IDS_FRLL=$W IDS_SEED=$S $RUN train.py --train_csv_path $W/smdd/train.csv --test_csv_path $W/eval_all.csv \
      --model_name resnet18_mult --output_dir $W/out/cls_s$S --model_path $W/out/cls_s$S/idistill_s$S.pt --is_train True --is_test False \
      --max_epoch $EPC --batch_size 16 --latent_size 128 --lr 1e-4 --weight_loss 1 --loss_measure prefusion ) > $W/out/cls_s$S.log 2>&1
  echo "classifier seed $S: $(( $(date +%s) - t1 )) s"; { grep -E "Lowest EER|Train process Stopped|^epoch" $W/out/cls_s$S.log || true; } | tail -3
  for v in best valbest last; do
    ck=$W/out/cls_s$S/idistill_s$S.pt; [ $v != best ] && ck=$ck.$v
    ( cd $C && $RUN $W/cb1/score_idistill.py $W $ck $W/out/scores_s${S}_$v.csv 128 ) >> $W/out/score_s$S.log 2>&1
  done
  cp $W/eval_all.csv $W/eval_all_meta.csv $W/smdd/train.csv $W/out/ 2>/dev/null || true
  [ $STAGE = cls ] && rm -f $W/out/lat.tar $W/out/crops.tar $W/out/OUT_SHA256SUMS && rm -rf $W/out/ae
  ( cd $W/out && find . -type f ! -name '*.tar' | LC_ALL=C sort | xargs sha256sum > OUT_SHA256SUMS_cls_s$S )
fi
kill $MP 2>/dev/null || true
tar -cf $TMPDIR/$T.tar -C $W/out .
cp $TMPDIR/$T.tar $R/$T.tar.part && mv $R/$T.tar.part $R/$T.tar && ( cd $R && sha256sum $T.tar > $T.tar.sha256 )
echo "DONE $T $(cat $R/$T.tar.sha256) $(date)"
