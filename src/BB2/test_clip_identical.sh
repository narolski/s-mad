#!/bin/bash
# BB2 CPU test: the CLIP path is unchanged by the BB2 archs_a12.py.
# Runs the pinned train.py (cbb2cbd1...) with the FS1 CLIP flags (run.sh), short (STEPS steps, batch BS, CPU), once from the
# pinned FS1 code tree and once from the BB2 tree (identical except archs_a12.py), on the same pack data and pinned CLIP
# weights; then scores LIMIT evaluation rows of each with the unchanged pn1_score.py. Compares: every tensor of last.pt
# (torch.equal), meta.json without wall-clock keys, the train.py stdout without timing fields, and the logits (bit-equal).
# Also checks that the DINOv3 name builds only with the BB2 tree. Usage: test_clip_identical.sh OUTDIR [ARM] [STEPS] [BS]
set -euo pipefail
OUT=${1:?outdir}; ARM=${2:-B}; STEPS=${3:-3}; BS=${4:-8}; LIMIT=${LIMIT:-16}
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
PIN=/mnt/t7/smad_next/BB2/pinned/pn1          # real-file copy of the FS1 tree code (checked against the pack SHA256SUMS)
NEW=/mnt/t7/smad_next/BB2/tree/pn1            # same, with src/BB2/archs_a12.py
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES="" \
  HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
mkdir -p "$OUT"
for side in pin new; do
  [ "${COMPARE_ONLY:-0}" = 1 ] && break
  T=$PIN; [ $side = new ] && T=$NEW
  D=$OUT/data_$side; rm -rf "$D" "$OUT/run_$side" "$OUT/score_$side"; mkdir -p "$D/manifests"
  ln -s "$T/data/train" "$D/train"; ln -s "$T/data/eval" "$D/eval"
  for f in "$T"/data/manifests/*.csv; do ln -s "$f" "$D/manifests/$(basename "$f")"; done
  ln -sfn "$T/data/manifests/train_$ARM.csv" "$D/manifests/train.csv"
  RUN=$OUT/run_$side/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s403_pn1$ARM
  SMAD_DATA=$D HF_HOME=$T/hf nice -n 10 "$PY" -I "$T/code/smadcvpr/train.py" --arch a12_clip_vitb16_madation \
    --regime d0 --split train90 --lofo none --lr 3.33e-06 --seed 403 --res 224 --workers 2 --out "$RUN" \
    --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps="$STEPS" --ft=lora \
    --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw \
    --wd=0.05 --head-lr=3.33e-05 --bs="$BS" --aug=flip --sched=const --clip-grad=5 --pos-weight=1 > "$OUT/train_$side.log" 2>&1
  SMAD_DATA=$D HF_HOME=$T/hf nice -n 10 "$PY" -I "$T/src/pn1_score.py" --run "$RUN" --code "$T/code" \
    --eval-manifest pn1_eval.csv --train-manifest train.csv --out "$OUT/score_$side" --workers 2 --limit "$LIMIT" \
    > "$OUT/score_$side.log" 2>&1
done
"$PY" -I - "$OUT" "$ARM" <<'EOF'
import json, pathlib, re, sys
import numpy as np, torch
out, arm = pathlib.Path(sys.argv[1]), sys.argv[2]
r = {}
rd = lambda s: out / f"run_{s}" / f"a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s403_pn1{arm}"
a = torch.load(rd("pin") / "last.pt", map_location="cpu", weights_only=True)
b = torch.load(rd("new") / "last.pt", map_location="cpu", weights_only=True)
r["last_pt_same_keys"] = sorted(a) == sorted(b)
r["last_pt_all_tensors_equal"] = r["last_pt_same_keys"] and all(torch.equal(a[k], b[k]) for k in a)
r["n_tensors"] = len(a)
TIME = {"train_hours", "wall_s", "train_s", "started", "finished", "time", "hours", "s_per_step", "out", "host", "date",
        "elapsed_s", "it_s"}
def clean(d):
    if isinstance(d, dict):
        return {k: clean(v) for k, v in d.items() if k not in TIME and "time" not in k and "hour" not in k}
    if isinstance(d, list):
        return [clean(v) for v in d]
    if isinstance(d, str):   # the two trees' own paths are the only expected difference in strings
        return d.replace("/mnt/t7/smad_next/BB2/pinned/pn1", "TREE").replace("/mnt/t7/smad_next/BB2/tree/pn1", "TREE")
    return d
ma, mb = (json.load(open(rd(s) / "meta.json")) for s in ("pin", "new"))
diff = sorted(k for k in set(ma) | set(mb)
              if k not in TIME and "time" not in k and "hour" not in k and clean(ma.get(k)) != clean(mb.get(k)))
r["meta_keys_differing_after_dropping_wallclock"] = diff
r["meta_differing_values"] = {k: [ma.get(k), mb.get(k)] for k in diff}
def strip(p):
    t = open(p).read().replace(str(out / "run_pin"), "RUN").replace(str(out / "run_new"), "RUN")
    t = t.replace(str(out / "data_pin"), "DATA").replace(str(out / "data_new"), "DATA")
    t = t.replace("/mnt/t7/smad_next/BB2/pinned/pn1", "TREE").replace("/mnt/t7/smad_next/BB2/tree/pn1", "TREE")
    t = re.sub(r"\d+(\.\d+)?\s*(s|it/s|s/it|min|h)\b", "T", t)
    t = re.sub(r"\d\d:\d\d:\d\d", "HH:MM:SS", t)
    t = re.sub(r'"train_hours": [0-9.e-]+', '"train_hours": T', t)
    return [l for l in t.splitlines() if "Warning" not in l]
la, lb = strip(out / "train_pin.log"), strip(out / "train_new.log")
r["train_stdout_lines"] = [len(la), len(lb)]
r["train_stdout_differing_lines"] = [[x, y] for x, y in zip(la, lb) if x != y][:20] + ([["<len>", ""]] if len(la) != len(lb) else [])
za, zb = (np.load(out / f"score_{s}" / "scores_eval.npz") for s in ("pin", "new"))
r["n_scored_eval"] = int(len(za["logit"]))
r["eval_ids_equal"] = bool((za["id"] == zb["id"]).all())
r["eval_logits_bit_equal"] = bool(np.array_equal(za["logit"].view(np.uint32), zb["logit"].view(np.uint32)))
ta, tb = (np.load(out / f"score_{s}" / "scores_train.npz") for s in ("pin", "new"))
r["train_logits_bit_equal"] = bool(np.array_equal(ta["logit"].view(np.uint32), tb["logit"].view(np.uint32)))
r["eval_logits_first4"] = za["logit"][:4].tolist()
sys.path.insert(0, "/mnt/t7/smad_next/BB2/pinned/pn1/code/smadcvpr")
import archs_a12 as P
r["dinov3_name_absent_from_pinned_registry"] = "a12_dinov3_vitl16_madation" not in P.ARCHS_A12
r["PASS"] = bool(r["last_pt_all_tensors_equal"] and not diff and not r["train_stdout_differing_lines"]
                 and r["eval_ids_equal"] and r["eval_logits_bit_equal"] and r["train_logits_bit_equal"]
                 and r["dinov3_name_absent_from_pinned_registry"])
json.dump(r, open(out / "clip_identical.json", "w"), indent=1)
print(json.dumps(r, indent=1))
EOF
