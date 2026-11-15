#!/bin/bash -l
#SBATCH -J ad5-oracle
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-oracle-%j.out
# Retrains of released methods (AD5): SelfMAD oracle-epoch diagnostic (prereg amendment 2). Scores every saved epoch
# (results/AD5/selfmad_S_s<seed>_epochs/epoch_<eee>_model.tar, every 5 epochs) of the finished SelfMAD retrains and
# the SelfMAD release (packs/AD5/selfmad_release.safetensors) on the cached FRLL-cell preprocessing, one platform.
# Output: results/AD5/oracle_<TAG>.tar (+ .sha256) with oracle_<name>_e<epoch>.npz. Submit with SEEDS="401 402 ..." TAG=..
set -eo pipefail
module load Python/3.10.4
set -u
source /net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD5/code_v5/src/AD5/athena/ad5_common.sh
SEEDS=${SEEDS:?seeds}; TAG=${TAG:?tag}
[ -f $RS/oracle_$TAG.tar.sha256 ] && { echo "oracle_$TAG done already"; exit 0; }
C=$PK/code_v5; W=$SCRATCH_LOCAL/oracle; mkdir -p $W/out $W/pack
trap 'echo "TERM $(date +%T)"; keep_log $W/out/*.log; exit 1' TERM
build_env_local score $C/src/AD5/env/score_requirements.txt $PK/wheels_score.tar
PY=$SCRATCH_LOCAL/env_score/bin/python
untar_checked $G/packs/RS1/rs1a_pack.tar $W/pack --wildcards 'code/*'
untar_checked $PK/selfmad_oracle_cache.tar $W/cache
( cd $PK && sha256sum -c selfmad_release.safetensors.sha256 )
J=("selfmad_hrnet_w18_erelease=$PK/selfmad_release.safetensors")
for s in $SEEDS; do
  for f in $RS/selfmad_S_s${s}_epochs/epoch_*_model.tar; do
    e=$(basename $f | cut -d_ -f2); J+=("selfmad_S_s${s}_e$((10#$e))=$f")
  done
done
echo "networks ${#J[@]}"
$PY -I $C/src/AD5/score/selfmad_oracle_athena.py $W/pack $W/cache $W/out "${J[@]}" > $W/out/oracle.log 2>&1 || { tail -20 $W/out/oracle.log; exit 1; }
tail -3 $W/out/oracle.log
tar -cf $SCRATCH_LOCAL/oracle_$TAG.tar -C $W/out .
( cd $SCRATCH_LOCAL && sha256sum oracle_$TAG.tar > oracle_$TAG.tar.sha256 )
cp $SCRATCH_LOCAL/oracle_$TAG.tar $SCRATCH_LOCAL/oracle_$TAG.tar.sha256 $RS/
cat $RS/oracle_$TAG.tar.sha256; echo ORACLE_DONE $TAG
