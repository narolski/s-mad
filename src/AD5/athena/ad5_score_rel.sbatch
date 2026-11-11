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
# Retrains of released methods (AD5): score retrains of MADation (L, B, F) and MixFaceNet-MAD (X) through the own-crop
# re-score (RS1) release path, on RS1's images (packs/RS1/rs1a_pack.tar [+ rs1a_pack_amend.tar], read only).
#  1. env envs/AD5/score (the RS1 versions, from shipped wheels);
#  2. crops: reuse results/AD5/rs1_crops.tar if it exists, else run RS1's athena_run.py crop exactly as
#     src/RS1/athena_rs1.sbatch (3 shards) and keep the crop PNGs in results/AD5/rs1_crops.tar for later jobs;
#  3. per retrain in $ITEMS (e.g. "madation_L_s401 madation_L_s402 mixfacenet_X_s401"): hash-checked untar of
#     results/AD5/<item>.tar, MADation converted by the A46 a36_madation.py convert (as the releases), then scored with
#     score/ad5_score_athena.py (RS1's byte-identical score.py, release spec of the arm);
#  4. per release in $RELEASES (default: the releases of the arms in $ITEMS): the same wrapper on the release file
#     (platform reference for RS1's release scores).
# Output: results/AD5/scores_<TAG>.tar (+ .sha256). Submit: sbatch --export=ALL,ITEMS="...",TAG=name ad5_score_rel.sbatch
set -eo pipefail
module load Python/3.10.4
set -u
source /net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD5/code/src/AD5/athena/ad5_common.sh
ITEMS=${ITEMS-}; TAG=${TAG:?tag}; LIMIT=${LIMIT:-0}   # ITEMS may be empty when RELEASES is given
[ -f $RS/scores_$TAG.tar.sha256 ] && { echo "scores_$TAG done already"; exit 0; }
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; date
C=$PK/code
build_env score $C/src/AD5/env/score_requirements.txt $PK/wheels_score.tar
PY=$EN/score/bin/python
W=$SCRATCH_LOCAL/ad5score; mkdir -p $W/out/logs $W/scores $W/conv $W/ret; SITE=$W/nosite; mkdir -p $SITE
R=$W/pack; mkdir -p $R
untar_checked $G/packs/RS1/rs1a_pack.tar $R
[ -f $G/packs/RS1/rs1a_pack_amend.tar ] && untar_checked $G/packs/RS1/rs1a_pack_amend.tar $R
sha256sum $G/packs/RS1/rs1a_pack*.tar.sha256 > $W/out/logs/rs1_pack_sha.txt; cat $W/out/logs/rs1_pack_sha.txt
"$PY" -I - "$R" "$LIMIT" <<'EOF'
import csv, sys, pathlib
R, lim = pathlib.Path(sys.argv[1]), int(sys.argv[2])
rows = list(csv.DictReader(open(R / "manifests/athena_manifest.csv")))
for name, origin in (("tocrop", "crop"), ("a46", "a46")):
    sel = [r for r in rows if r["origin"] == origin]
    if lim:
        seen, keep = {}, []
        for r in sel:
            k = r["set"].split("_")[0]
            if seen.get(k, 0) < lim:
                seen[k] = seen.get(k, 0) + 1; keep.append(r)
        sel = keep
    with open(R / f"manifests/{name}_abs.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "path"]); [w.writerow([r["id"], str(R / r["relpath"])]) for r in sel]
    print(name, len(sel))
EOF
CT=$RS/rs1_crops$([ "$LIMIT" = 0 ] || echo _limit$LIMIT).tar
if [ -f $CT.sha256 ]; then
  untar_checked $CT $W/crops
else
  for i in 0 1 2; do
    "$PY" -I "$R/code/rs1/athena_run.py" "$R" "$SITE" crop --manifest "$R/manifests/tocrop_abs.csv" --out "$W/crops/main" --shard $i/3 > "$W/out/logs/crop_shard$i.log" 2>&1 &
  done
  FAIL=0; for j in $(jobs -p); do wait $j || FAIL=1; done
  [ $FAIL = 0 ] || { tail -20 "$W"/out/logs/crop_shard*.log; exit 4; }
  tar -cf $SCRATCH_LOCAL/crops.tar -C $W/crops . && ( cd $SCRATCH_LOCAL && sha256sum crops.tar | sed "s/crops.tar/$(basename $CT)/" > crops.sha )
  cp $SCRATCH_LOCAL/crops.tar $CT; cp $SCRATCH_LOCAL/crops.sha $CT.sha256
fi
# the score list, exactly as RS1's merge step (retained or flagged crops + the A46 crops)
"$PY" -I - "$R" "$W" <<'EOF'
import csv, sys, pathlib, glob, collections
R, W = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out, st = [], collections.Counter()
for f in sorted(glob.glob(str(W / "crops/main/crops_*of3.csv"))):
    for r in csv.DictReader(open(f)):
        st[r["status"].split(":")[0]] += 1
        if r["status"] == "retained" or r["status"].startswith("flag:"):
            p = r["path"]
            if not pathlib.Path(p).exists():          # crops reused from an earlier job: same names, new scratch root
                p = str(W / "crops/main" / f"{r['id']}.png")     # crop_rgb.py writes DIR/<id>.png
            out.append((r["id"], p))
out += [(r["id"], r["path"]) for r in csv.DictReader(open(R / "manifests/a46_abs.csv"))]
missing = [p for _, p in out if not pathlib.Path(p).exists()]
assert not missing, (len(missing), missing[:3])
with open(W / "score_all.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["id", "path"]); w.writerows(out)
print("score list", len(out), dict(st))
EOF
declare -A AS=( [L]=madation_vitl14 [B]=madation_vitb16 [F]=madation_fe_vitl14 [X]=mixfacenet_mad_smdd )
declare -A KIND=( [L]=madation [B]=madation [F]=fe ) ; declare -A ARCH=( [L]=vitl14 [B]=vitb16 [F]=vitl14 )
declare -A RELW=( [madation_vitl14]=bb452ded624ffce2dc85168f8dde9293fc3709ec8cce755d8ecf1d5f5370e980.safetensors \
  [madation_vitb16]=ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f.safetensors \
  [madation_fe_vitl14]=74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9.safetensors \
  [mixfacenet_mad_smdd]=3d507c8bbd5dbd06bd735ae809fa0095e589c17c0c94cd2ed530cf34a014ab1c.pth )
LIM=$([ "$LIMIT" = 0 ] || echo "--limit $((LIMIT*4))")
score_one() {  # score_one RELEASE_SPEC NAME WEIGHTS
  local t0=$(date +%s)
  "$PY" -I $C/src/AD5/score/ad5_score_athena.py "$R" "$SITE" --as $1 --name $2 --weights $3 -- --mode rel \
    --manifest $W/score_all.csv --out-dir $W/scores --tag rel_$2__ad5 --workers 6 --bs 32 $LIM > $W/out/logs/score_$2.log 2>&1
  echo "$2 as $1 $(( $(date +%s) - t0 )) s" | tee -a $W/out/logs/score_times.txt
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
cp $W/scores/scores_*.npz $W/out/; cp $W/score_all.csv $W/out/; "$PY" -m pip freeze > $W/out/logs/pip_freeze.txt
printf '{"tag":"%s","items":"%s","job":"%s","host":"%s","limit":%s}\n' "$TAG" "$ITEMS" $SLURM_JOB_ID $(hostname) $LIMIT > $W/out/job.json
tar -cf $SCRATCH_LOCAL/scores_$TAG.tar -C $W/out .
( cd $SCRATCH_LOCAL && sha256sum scores_$TAG.tar > scores_$TAG.tar.sha256 )
cp $SCRATCH_LOCAL/scores_$TAG.tar $RS/; cp $SCRATCH_LOCAL/scores_$TAG.tar.sha256 $RS/
cat $RS/scores_$TAG.tar.sha256; echo SCORE_DONE $TAG; date
