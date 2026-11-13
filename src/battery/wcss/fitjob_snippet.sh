# Shared test battery (BATTERY) v1: the lines a NEW arm's WCSS H100 fit job adds after pn1_score.py (fail-soft: a battery
# failure never stops the fit job from returning its own result tar). Pre-run review F8 template.
# Assumes the fit job's own variables: W (local work dir in $TMPDIR), RUN (train.py run dir: last.pt + meta.json),
# R (the result dir being tarred), D (data root of the FS1 pack + AB1 overlay), SEED, ARM, MAN (training manifest name),
# PY=$HOME/dmenv/bin/python. Needs on Lustre: packs/BATTERY/battery_code_<version>.tar (pinned below), the TT1, MEDS and
# GD packs (packs/TT1/tt1_pack.tar, packs/BB2/tt1m_meds.tar, packs/BB2/pr1_gd.tar) and the H100 reference
# results/AB1/AB1_Sb_s408.tar. Copy, verify and unpack them into $W exactly as battery_smoke.sbatch does.
#   BATTERY_CODE_SHA=<sha256 of the released code tar>
(
  set -e
  cp "$L/packs/BATTERY/battery_code_v1rc2.tar" "$W/bcode.tar"
  [ "$(sha256sum "$W/bcode.tar" | cut -c1-64)" = "$BATTERY_CODE_SHA" ]
  mkdir -p "$W/bcode" && tar -C "$W/bcode" -xf "$W/bcode.tar" && rm -f "$W/bcode.tar"
  cd "$W/bcode/src" && $PY -m battery.run --ckpt "$RUN" --arm "$ARM" --seed "$SEED" --out "$R/battery" \
      --code "$W/pn1/code" --hf-home "$W/pn1/hf" --ref "$W/AB1_Sb_s408.tar" \
      --data dev="$D" tt1="$W/tt1/data" meds="$W/tt1m/data" gd="$W/pr1g/data" \
      --train-manifest "$D/manifests/$MAN" --expect-eval "$R/scores_eval.npz" --workers 7 --stats no
) > "$R/battery.log" 2>&1 || echo "BATTERY rc $?" >> "$R/battery.log"
# --out is a fresh directory inside the fit's result dir (outputs are never overwritten). Statistics are completed on the
# DGX after fetch:  cd src && python -m battery.run --stats-only <unpacked result>/battery
