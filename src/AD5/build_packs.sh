#!/bin/bash
# Retrains of released methods (AD5): build the Athena packs on the DGX (T7 drive).
#   code/  : patched authors' code (build/madation_src, build/smdd_src, build/selfmad_src), the patches, src/AD5,
#            the two OpenAI-format CLIP files (weights/), the Hugging Face cache for SelfMAD (hf_cache/)
#   wheels_madation.tar, wheels_selfmad.tar : x86_64 / cp310 wheels + the sdists that have no wheel
#   smdd_train_raw.tar : SMDD_release_train/{train.csv, os25k_bf_t/, m15k_t/} byte-for-byte
# Every tar gets a .sha256 beside it. Re-running rebuilds code/ and skips tars that exist.
set -euo pipefail
A=/mnt/t7/smad_next/AD5; P=$A/packs; B=$A/build; mkdir -p $P
HF=/home/narolski/.cache/huggingface/hub
rm -rf $P/code; mkdir -p $P/code/build $P/code/src $P/code/weights
cp -a $B/madation_src $B/smdd_src $B/selfmad_src $P/code/build/
cp -a /home/narolski/smad-next/src/AD5 $P/code/src/; find $P/code -name "__pycache__" -type d -prune -exec rm -rf {} +
cp -L $HF/models--timm--vit_base_patch16_clip_224.openai/snapshots/977e3dd0ec55ab8da155f2fbeb6b5f54948b6e3d/pytorch_model.bin $P/code/weights/clip_vitb16_openai.bin
cp -L $HF/models--timm--vit_large_patch14_clip_224.openai/snapshots/18d0535469bb561bf468d76c1d73aa35156c922b/pytorch_model.bin $P/code/weights/clip_vitl14_openai.bin
cp -a $A/hf_cache $P/code/hf_cache
(cd $P/code && find . -type f ! -name CODE_SHA256SUMS | sort | xargs sha256sum > CODE_SHA256SUMS)
mk() {  # mk NAME.tar DIR...: tar of the given -C DIR . pairs, with sha256
  local t=$1; shift
  [ -f $P/$t.sha256 ] && { echo "$t exists"; return 0; }
  tar -cf $P/$t "$@"; (cd $P && sha256sum $t > $t.sha256); cat $P/$t.sha256
}
mk wheels_madation.tar -C $A/wheels/madation . -C $A/wheels/madation_sdist .
mk wheels_selfmad.tar -C $A/wheels/selfmad . -C $A/wheels/selfmad_sdist .
mk wheels_score.tar -C $A/wheels/score .
mk smdd_train_raw.tar -C /mnt/t7/Datasety/downloads/SMDD SMDD_release_train/train.csv SMDD_release_train/os25k_bf_t SMDD_release_train/m15k_t
du -sh $P/*; echo PACKS_DONE
