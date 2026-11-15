#!/bin/bash
# CB1 IDistill: data pack (symlink staging, tar -h dereferences; no image is changed). Writes
# /mnt/t7/smad_next/CB1/packs/idistill_data.tar (+ .sha256) and the staging list STAGE_LIST.txt (folder, source).
set -euo pipefail
P=/mnt/t7/smad_next/CB1/packs; S=$P/stage_idistill; rm -rf $S; mkdir -p $S/eval_raw
FR=/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london; FB=/mnt/t7/Datasety/downloads/frll_base/extracted
MR=/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted
MA=/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z
EV=/home/narolski/mambamorph-code/smadcvpr_data/eval/frllm/frll_bona
ln -s /mnt/t7/Datasety/downloads/SMDD/os25k_m_t $S/os25k_m_t
mk() { local d=$1 x; shift; mkdir -p $S/eval_raw/$d; for x in "$@"; do ln -s "$x" $S/eval_raw/$d/; done; }
mk frll_bona $FB/neutral_front/*.jpg $FB/smiling_front/*.jpg
for f in amsl facemorpher opencv stylegan webmorph; do mk frll_$f $FR/morph_$f/*; done
mk frll_alnnative_bona $EV/*_orig.png
for f in amsl facemorpher opencv stylegan webmorph; do mk frll_e7_$f $EV/*_resmatch_$f.png; done
mk mad22_bona $MR/BonaFide/*
for f in FaceMorpher MIPGAN_I MIPGAN_II OpenCV Webmorph; do mk mad22_$f $MR/$f/*; mk mad22_e7_$f $MA/e7/$f/*; done
mk mad22_alnnative_bona $MA/native/BonaFide/*
( cd $S/eval_raw && for d in *; do echo "$d $(ls $d | wc -l)"; done ) | tee $P/idistill_stage_counts.txt
( cd $S && find -L . -type f | LC_ALL=C sort ) > $P/idistill_stage_files.txt
wc -l < $P/idistill_stage_files.txt
tar -chf $P/idistill_data.tar -C $S .
( cd $P && sha256sum idistill_data.tar > idistill_data.tar.sha256 && cat idistill_data.tar.sha256 )
