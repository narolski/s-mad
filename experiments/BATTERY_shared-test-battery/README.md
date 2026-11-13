# Shared test battery (BATTERY): record

Owner: BATTERY role (Claude agent for the lead). Design: `DESIGN.md`. Missing data: `MISSING_DATA.md`.
Status: release candidate `1.0.0-rc1`, **not released** (needs the pre-run check, the H100 smoke and the lead's word).

## Timeline (machine clock, CET)

- 13 Nov 18:55 started; read OWNER_BRIEF, SA1 result.md, TT1 platform pins, the PN1/PR1/TT1/AB1/BD1/SE1 readers.
- 19:0x first block test (A_s403): every leaf exact.
- 19:15-19:16 CPU test of the real command line on 8 rows per set (`/mnt/t7/smad_next/BATTERY/test8_cpu`, TEST, never read):
  all four sets load (21,277 / 34,411 / 1,018 / 11,042 rows pass the deny-list and exist), loader and scorer run; CPU
  logits of FS1 Sb s403 within about 1e-4 of its stored A100 logits (loader check only).
- 19:0x-19:5x full regression (`regression_v1.json`): 189 comparisons, 189 exact, 28,527 leaves, 0 differ.
- CPU gate test (`--test-gate-key` A100 reference on the DGX CPU, expected to fail): see section "Gate test".
- Stored-logit records (`/mnt/t7/smad_next/BATTERY/stored/`, 38 records) and cell-level check (`cells_check_v1.json`).

## Commands

```
cd /home/narolski/smad-next/src
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 $PY -W ignore -m battery.regress \
    --out ../experiments/BATTERY_shared-test-battery/regression_v1.json
nice -n 10 $PY -W ignore -m battery.stored --out /mnt/t7/smad_next/BATTERY/stored
$PY -m battery.cells --stored /mnt/t7/smad_next/BATTERY/stored --out ../experiments/BATTERY_shared-test-battery/cells_check_v1.json
$PY -m battery.read --include-stored /mnt/t7/smad_next/BATTERY/stored/* --json /mnt/t7/smad_next/BATTERY/read_stored_v1.json
CUDA_VISIBLE_DEVICES= HF_HOME=/mnt/t7/smad_next/PN1/fs_tree/pn1/hf HF_HUB_OFFLINE=1 $PY -W ignore -m battery.run \
    --ckpt /mnt/t7/smad_next/PN1/results_fs/unpacked/PN1_Sb_s403 --arm Sb --seed 403 --out /mnt/t7/smad_next/BATTERY/test8_cpu \
    --device cpu --test-limit 8 --workers 2 --train-manifest /mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv
```

## What is kept where

- Code `src/battery/` (committed). Results small: this folder. Large: `/mnt/t7/smad_next/BATTERY/` (test outputs, stored
  records, stdout files). Nothing only in /tmp.
- Smoke command for the dispatcher: `/mnt/t7/smad_next/dispatch/submit_queue/wcss_battery_smoke.cmd`; code tar
  `/mnt/t7/smad_next/BATTERY/battery_code_v1rc1.tar` (copy on WCSS `packs/BATTERY/`).
