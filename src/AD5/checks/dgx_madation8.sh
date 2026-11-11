#!/bin/bash
# Retrains of released methods (AD5): 8-image check of the patched MADation code on the DGX (world size 1, batch 4,
# 3 epochs so that the epoch-3 checkpoint is written), ARM=B (ViT-B/16) or L (ViT-L/14). Retries on CUDA out of memory
# at start (the DGX GPU is shared), up to 6 times, 3 min apart.
set -uo pipefail
ARM=${1:-B}; C=/mnt/t7/smad_next/AD5/checks; HF=/home/narolski/.cache/huggingface/hub
if [ $ARM = B ]; then BB="ViT-B/16"; X="--lora_dropout=0.4 --lora_r=2 --lora_a=4"; CS=$HF/models--timm--vit_base_patch16_clip_224.openai/snapshots/977e3dd0ec55ab8da155f2fbeb6b5f54948b6e3d/pytorch_model.bin
else BB="ViT-L/14"; X="--lora_dropout=0.2 --lora_r=2 --lora_a=8"; CS=$HF/models--timm--vit_large_patch14_clip_224.openai/snapshots/18d0535469bb561bf468d76c1d73aa35156c922b/pytorch_model.bin; fi
for k in 1 2 3 4 5 6; do
  rm -rf $C/madation8/out_$ARM
  ( cd /mnt/t7/smad_next/AD5/build/madation_src/src && AD5_SEED=401 AD5_TRAIN_CSV=$C/madation8/train8.csv AD5_OUT=$C/madation8/out_$ARM \
    AD5_NO_TEST=1 AD5_CLIP_SD=$CS PYTHONPATH=/mnt/t7/smad_next/AD5/build/dgx_site OMP_NUM_THREADS=4 timeout 2400 nice -n 10 \
    /home/narolski/mambamorph-code/.venv-spark/bin/python -I -m torch.distributed.launch --nproc_per_node=1 --nnodes=1 \
    --node_rank=0 --master_addr=localhost --master_port=12399 config.py --debug=True --backbone_size="$BB" \
    --dataset_name="MADTrain" --training_type="MAD_training" --lr_model=1e-5 --lr_header=1e-4 $X --batch_size=4 \
    --num_epoch=3 --save_every=3 --log_every=1 ) > $C/madation8/run_$ARM.log 2>&1
  rc=$?; echo "try $k rc $rc $(date +%H:%M)"
  ls $C/madation8/out_$ARM/last_trainings/*/*/*/*/3_backbone.pth 2>/dev/null && { echo CHECK_OK; exit 0; }
  grep -q "out of memory" $C/madation8/run_$ARM.log || { echo "failed, not OOM"; exit 1; }
  sleep 180
done
exit 1
