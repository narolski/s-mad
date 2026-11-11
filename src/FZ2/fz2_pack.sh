#!/bin/bash
# FZ2 pack: code (fz2_feats.py + the unchanged smadcvpr/common.py), weights (released MADation FE ViT-L/14 file, whose
# net.* tensors are OpenAI CLIP ViT-L/14; DINOv2 ViT-L/14 safetensors from the local timm cache), the 64 A43 check frames.
set -euo pipefail
P=/mnt/t7/smad_next/FZ2/pack
D=$P/fz2pack
mkdir -p $D/code $D/weights
cp /home/narolski/smad-next/src/FZ2/fz2_feats.py $D/code/
cp /home/narolski/mambamorph-code/smadcvpr/common.py $D/code/
cp /mnt/t7/smad_next/FZ1/release/madation_fe_vitl14_model.safetensors $D/weights/
cp -L $(ls ~/.cache/huggingface/hub/models--timm--vit_large_patch14_dinov2.lvd142m/snapshots/*/model.safetensors) $D/weights/dinov2_vitl14_lvd142m.safetensors
( cd $D && find . -type f ! -name MANIFEST.sha256 | sort | xargs sha256sum > MANIFEST.sha256 )
tar -cf $P/fz2_pack.tar -C $P fz2pack
( cd $P && sha256sum fz2_pack.tar > fz2_pack.tar.sha256 )
cat $P/fz2_pack.tar.sha256; ls -la $P/fz2_pack.tar
