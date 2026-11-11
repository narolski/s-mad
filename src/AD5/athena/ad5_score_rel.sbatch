#!/bin/bash -l
#SBATCH -J ad5-score
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=100G
#SBATCH --gres=gpu:1
#SBATCH --time=06:00:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-score-%j.out
# Retrains of released methods (AD5), scoring v2 (pre-run review finding 4): MADation (L, B, F) and MixFaceNet-MAD (X)
# retrains scored on the own-crop re-score's (RS1) crop files, reused by hash, so that every row (release and retrains,
# native and history-matched photos) is cropped on one machine by one run (RS1 amendments 3 and 4):
#   variant 1 (primary) = the authors' SMDD image_preprocess.py run unchanged by RS1; variant 2 = RS1's corrected crop.
# Inputs: results/RS1/$RS1_TAR (RS1's result tar with crops/v1, crops/v2, crops_sha256.txt, score_v*.csv) and the code
# and weights of packs/RS1/rs1a_pack.tar (RS1's frozen A46 runtime, score.py; release weights for the reference rows).
# Per retrain in $ITEMS: hash-checked untar of results/AD5/<item>.tar; MADation converted by a36_madation.py convert
# (as the releases); scored by score/ad5_score_athena.py (RS1's byte-identical score.py with the release spec).
# Per release in $RELEASES (default: those of the arms in $ITEMS): the same path on the release file.
# Output: results/AD5/scores_<TAG>.tar (+ .sha256), files scores_rel_<name>__ad5<variant>.npz.
# Submit: sbatch --export=ALL,RS1_TAR=rs1a_prod_<job>.tar,ITEMS="madation_L_s401 ...",TAG=name[,LIMIT=8] ad5_score_rel.sbatch
set -eo pipefail
module load Python/3.10.4
set -u
source /net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD5/code_v4/src/AD5/athena/ad5_common.sh
ITEMS=${ITEMS-}; TAG=${TAG:?tag}; LIMIT=${LIMIT:-0}; RS1_TAR=${RS1_TAR:?RS1 result tar name}
[ -f $RS/scores_$TAG.tar.sha256 ] && { echo "scores_$TAG done already"; exit 0; }
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; date
C=$PK/code_v4
W=$SCRATCH_LOCAL/ad5score; mkdir -p $W/out/logs $W/scores $W/conv $W/ret $W/rs1; SITE=$W/nosite; mkdir -p $SITE
trap 'echo "TERM received $(date +%T)"; keep_log $W/out/logs/*; exit 1' TERM
build_env_local score $C/src/AD5/env/score_requirements.txt $PK/wheels_score.tar
PY=$SCRATCH_LOCAL/env_score/bin/python
cp $SCRATCH_LOCAL/env_score/pip_freeze.txt $W/out/logs/
R=$W/pack; mkdir -p $R
echo "unpack RS1 $(date +%T)"; untar_checked $G/packs/RS1/rs1a_pack.tar $R --wildcards 'code/*' 'weights/*' 'manifests/*'
untar_checked $G/results/RS1/$RS1_TAR $W/rs1
sha256sum $G/packs/RS1/rs1a_pack.tar $G/results/RS1/$RS1_TAR > $W/out/logs/rs1_inputs_sha.txt
( cd $W/rs1/crops && sha256sum -c --quiet ../crops_sha256.txt ) || { echo "RS1 crop files do not match crops_sha256.txt"; exit 3; }
cp $W/rs1/crops_sha256.txt $W/out/logs/rs1_crops_sha256.txt
echo "RS1 crops verified: $(wc -l < $W/rs1/crops_sha256.txt) files"
# score lists with this job's paths (RS1 names: crops/v1/<id><ext>, crops/v2/<id>.png); LIMIT keeps the first rows per set
"$PY" -I - "$W" "$R" "$LIMIT" <<'EOF'
import csv, sys, pathlib
W, R, lim = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), int(sys.argv[3])
sets = {r["id"]: r["set"] for r in csv.DictReader(open(R / "manifests/athena_manifest.csv"))}
for v in ("v1", "v2"):
    rows = [(r["id"], str(W / "rs1/crops" / v / pathlib.Path(r["path"]).name))
            for r in csv.DictReader(open(W / f"rs1/score_{v}.csv"))]
    if lim:
        seen, keep = {}, []
        for i, p in rows:
            s = sets.get(i, "?")
            if seen.get(s, 0) < lim:
                seen[s] = seen.get(s, 0) + 1; keep.append((i, p))
        rows = keep
    miss = [p for _, p in rows if not pathlib.Path(p).exists()]
    assert not miss, (v, len(miss), miss[:3])
    with open(W / f"score_{v}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "path"]); w.writerows(rows)
    print(v, len(rows))
EOF
declare -A AS=( [L]=madation_vitl14 [B]=madation_vitb16 [F]=madation_fe_vitl14 [X]=mixfacenet_mad_smdd )
declare -A KIND=( [L]=madation [B]=madation [F]=fe ) ; declare -A ARCH=( [L]=vitl14 [B]=vitb16 [F]=vitl14 )
declare -A RELW=( [madation_vitl14]=bb452ded624ffce2dc85168f8dde9293fc3709ec8cce755d8ecf1d5f5370e980.safetensors \
  [madation_vitb16]=ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f.safetensors \
  [madation_fe_vitl14]=74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9.safetensors \
  [mixfacenet_mad_smdd]=3d507c8bbd5dbd06bd735ae809fa0095e589c17c0c94cd2ed530cf34a014ab1c.pth )
score_one() {  # score_one RELEASE_SPEC NAME WEIGHTS: both crop variants
  local v t0
  for v in v1 v2; do
    t0=$(date +%s)
    "$PY" -I $C/src/AD5/score/ad5_score_athena.py "$R" "$SITE" --as $1 --name $2 --weights $3 -- --mode rel \
      --manifest $W/score_$v.csv --out-dir $W/scores --tag rel_$2__ad5$v --workers 6 --bs 32 > $W/out/logs/score_$2_$v.log 2>&1 \
      || { tail -20 $W/out/logs/score_$2_$v.log; keep_log $W/out/logs/score_$2_$v.log; return 1; }
    echo "$2 as $1 $v $(( $(date +%s) - t0 )) s $(date +%T)" | tee -a $W/out/logs/score_times.txt
    tail -1 $W/out/logs/score_$2_$v.log
  done
}
RELS=""
for it in $ITEMS; do
  arm=$(echo $it | cut -d_ -f2); rel=${AS[$arm]}; RELS="$RELS $rel"
  untar_checked $RS/$it.tar $W/ret/$it
  if [ $arm = X ]; then wf=$W/ret/$it/mixfacenet_SMDD.pth
  else
    "$PY" -I $R/code/smadcvpr/a36_madation.py convert --release $it --kind ${KIND[$arm]} --arch ${ARCH[$arm]} \
      --backbone $W/ret/$it/40_backbone.pth --header $W/ret/$it/40_header.pth --log $W/ret/$it/training.log \
      --out $W/conv/$it > $W/out/logs/convert_$it.log 2>&1 || { cat $W/out/logs/convert_$it.log; exit 5; }
    cp $W/conv/$it/convert.json $W/out/logs/convert_$it.json; wf=$W/conv/$it/model.safetensors
  fi
  score_one $rel $it $wf
  rm -rf $W/ret/$it $W/conv/$it/model.safetensors
done
for rel in $(echo ${RELEASES:-$RELS} | tr ' ' '\n' | sort -u); do score_one $rel $rel $R/weights/${RELW[$rel]}; done
cp $W/scores/scores_*.npz $W/out/; cp $W/score_v1.csv $W/score_v2.csv $W/out/
printf '{"tag":"%s","items":"%s","releases":"%s","rs1_tar":"%s","job":"%s","host":"%s","limit":%s}\n' "$TAG" "$ITEMS" \
  "${RELEASES:-$RELS}" "$RS1_TAR" $SLURM_JOB_ID $(hostname) $LIMIT > $W/out/job.json
tar -cf $SCRATCH_LOCAL/scores_$TAG.tar -C $W/out .
( cd $SCRATCH_LOCAL && sha256sum scores_$TAG.tar > scores_$TAG.tar.sha256 )
cp $SCRATCH_LOCAL/scores_$TAG.tar $RS/; cp $SCRATCH_LOCAL/scores_$TAG.tar.sha256 $RS/
cat $RS/scores_$TAG.tar.sha256; echo SCORE_DONE $TAG; date
