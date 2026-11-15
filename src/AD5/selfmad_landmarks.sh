#!/bin/bash
# Retrains of released methods (AD5): SelfMAD landmarks for the 25,000 SMDD genuine training renders, on the DGX CPU,
# with the authors' preprocessing/dlib_lm.py UNCHANGED (dlib frontal detector, upsample 1, 81-point predictor, faces
# sorted by landmark-box area). The script is run once per shard directory (4 shards of symlinks, so 4 processes);
# per-image output does not depend on the shard. Outputs are merged into
#   /mnt/t7/smad_next/AD5/data/selfmad/SMDD_landmarks/os25k_bf_t/<name>.npy
# (the layout utils/selfMAD.py expects: <SMDD_path>_landmarks/os25k_bf_t/).
set -euo pipefail
SM=/mnt/t7/Datasety/downloads/SMDD/SMDD_release_train/os25k_bf_t
D=/mnt/t7/smad_next/AD5/data/selfmad
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
SITE=/mnt/t7/smad_next/AD5/build/dgx_site
SCRIPT=/mnt/t7/smad_next/AD5/build/selfmad_src/preprocessing/dlib_lm.py
PRED=/mnt/t7/thirdparty/dlib81_wcss_20261107/shape_predictor_81_face_landmarks.dat
NS=${NS:-4}
mkdir -p $D/SMDD/os25k_bf_t
ls $SM | sort > $D/bf_names.txt
[ "$(wc -l < $D/bf_names.txt)" = 25000 ] || { echo "expected 25000 files"; exit 1; }
while read -r f; do ln -sfn $SM/$f $D/SMDD/os25k_bf_t/$f; done < $D/bf_names.txt
for k in $(seq 0 $((NS-1))); do
  S=$D/shards/s$k; mkdir -p $S/SMDD/os25k_bf_t $S/work; ln -sfn $PRED $S/work/
  awk -v k=$k -v n=$NS 'NR % n == k' $D/bf_names.txt | while read -r f; do ln -sfn $SM/$f $S/SMDD/os25k_bf_t/$f; done
  ( cd $S/work && nice -n 10 $PY -I /home/narolski/smad-next/src/AD5/checks/run_with_site.py $SITE $SCRIPT \
      -i $S/SMDD -o landmarks > $S/dlib_lm.log 2>&1; echo "shard $k exit $?" >> $D/shards/done.txt ) &
done
wait
cat $D/shards/done.txt
mkdir -p $D/SMDD_landmarks/os25k_bf_t
for k in $(seq 0 $((NS-1))); do
  find $D/shards/s$k/SMDD_landmarks/os25k_bf_t -name "*.npy" -exec mv -t $D/SMDD_landmarks/os25k_bf_t/ {} +
done
n=$(ls $D/SMDD_landmarks/os25k_bf_t | wc -l); echo "landmark files: $n of 25000"
grep -h "No faces in" $D/shards/s*/dlib_lm.log | sed 's/.*No faces in //' | xargs -r -n1 basename | sort > $D/no_face.txt || true
echo "no face: $(wc -l < $D/no_face.txt)"
(cd $D/SMDD_landmarks/os25k_bf_t && ls | sort | xargs sha256sum) > $D/landmarks_SHA256SUMS
echo LANDMARKS_DONE
