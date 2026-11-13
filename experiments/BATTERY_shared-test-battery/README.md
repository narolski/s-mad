# Shared test battery (BATTERY): record

Owner: BATTERY role (Claude agent for the lead). Design: `DESIGN.md`. Audit rows without data: `MISSING_DATA.md`.
Status: release candidate `1.0.0-rc1` (commit 761a3c7 and later), **not released**: it needs the pre-run check
(experiment-reviewer, launched by the lead), the H100 smoke and the lead's word. Arms registered before the release keep
their own readers. The audit table itself stays with SA1 (row definitions, review status); existing reviewed cells are not
recomputed or replaced by battery output.

## Timeline (machine clock, CET, 13 Nov 2026)

- 18:55 started; read OWNER_BRIEF, SA1 result.md, TT1 platform pins, the PN1/PR1/TT1/AB1/BD1/SE1 readers.
- 19:11-19:28 full regression (`regression_v1.json`): 189 comparisons, 189 exact, 28,527 leaves compared, 0 differ.
- 19:15-19:16 CPU test of the real command line on 8 rows per set (`/mnt/t7/smad_next/BATTERY/test8_cpu`, TEST, never
  read): all four sets load and pass the deny-list (21,277 / 34,411 / 1,018 / 11,042 rows, every image present); loader and
  scorer run; CPU logits of FS1 Sb s403 within about 1e-4 of its stored A100 logits (loader check only).
- 19:17 CPU gate test started (`--test-gate-key` with the A100 reference on the DGX CPU; must fail): section 3.
- 19:40 commit 761a3c7 (code, design, regression); code tar `battery_code_v1rc1.tar` 8a86676d...; uploaded with
  `battery_smoke.sbatch` (c75f2cb0...) to WCSS `packs/BATTERY/`; every input pin checked on WCSS.
- 19:41 smoke command written to `/mnt/t7/smad_next/dispatch/submit_queue/wcss_battery_smoke.cmd`; the dispatcher
  submitted it as WCSS job **6316361** (battery-smoke, limit 1:30; queued behind BB2's E2 jobs). Owner: BATTERY.
  Expected run 25-40 min after start. Check at its end with `python -m battery.smoke_check <tar> <out.json>`.
- 19:4x-19:50 stored-logit records (38, `/mnt/t7/smad_next/BATTERY/stored/`), cell-level check (`cells_check_v1.json`),
  reader print (`read_stored_v1.txt`).

## 1. Regression test: the battery reproduces the reviewed numbers exactly

Every leaf of the reviewed per-network records, compared by exact equality with the battery's value (floats ==):

| Block | Reference record | Networks | Leaves | Differ |
|---|---|---|---|---|
| FS1 | fs.json seeds/<s>/<arm> (incl. the storage-share interval, replayed in fs_read's order) | A, B, Sb 403-407 | 270 | 0 |
| FS1 | fs.json printed_R1_R6 (per arm; R3_base, R5) | A, B, Sb 403-407 | 345 | 0 |
| PR1 | z_read.json per_net | A, B, Sb 403-407 | 6,965 | 0 |
| BD1 | bd1_read.json FS1 / AB1 / SE1 blocks | FS1 15; AB1 Sb 408-412; SE1 Sb 408-411 | 1,104 | 0 |
| GD | gd_read.json per_net (GD0, GD1, GD2) | A, B, Sb 403-407 | 1,170 | 0 |
| TT1 | tt1_read_fs.json nets; tt1_read_x_sp.json nets | A, B, Sb 403-407; Sp 403-405 | 15,603 | 0 |
| MEDS | tt1_read_meds.json nets | A, B, Sb 403-407; Sp 403-405 | 468 | 0 |
| C2P | c2p_read.json per_network (L40S rescoring) | B_s405, Sb 403, 405, 406, 407 | 160 | 0 |
| AB1 | ab1_read.json networks | A, B, Sb, Sp, SbZ, SbH, SbS, AS 408-412 | 2,370 | 0 |
| FS1/PR1 | sp.json Sp prints (R1-R6, lcomb, storage share, dev S0/S3 flags, S0-vs-S4 AUC) | Sp 403-405 | 72 | 0 |
| **all** | | | **28,527** | **0** |

Run under the deny-list audit hook; no denied path was opened (the battery never calls `pn1lib.catalog()`).

Cell-level check against the audit table text (`cells_check_v1.json`): 82 headline ranges of reviewed cells of our arms
(rows 1, 2, 4-10, 12-14, 17-20; FS1 block 403-407 and AB1 block 408-412), recomputed from the stored-logit records and
rounded as printed: **80 of 82 match**. The two that differ are rounding in the table text; the battery's values equal the
reviewed JSON exactly:
- 1-A "FFHQ own-rule flags native 6.4-10.7%": the largest value is 0.1075 (A_s404, fs.json), which rounds to 10.8%
  (half up); the table prints 10.7.
- 7-B "R4 vs R3 0.75-0.79": the smallest value is 0.7446 (B_s403, z_read.json), which rounds to 0.74; the table (from
  `experiments/PR1_protocol-reads-existing-networks/result.md:117`) prints 0.75.
For SA1 and RECORDS; the battery changes nothing in the table.

## 2. What the regression does not cover, and why

- Rows 3 (JPEG) and 16 (expression): no development data (`MISSING_DATA.md`).
- Row 11 (data volume) and row 15 (partner trace): not per-network statistics (between-arm controls; SA1's manifest audit).
- The 80 released-detector cells: released networks are not battery arms (RS1/CB1/AR1 machinery, own crops).
- The three-source arm (SbM3 column, MS1): its fits were scored on MS1's own evaluation manifest, not on the battery's dev
  set, and read by MS1's reader; not regressed in v1.
- Seeds 401/402 and the controls Bn, Bv, C (row 11 and earlier leads): read by the tier-1 readers, which the battery does
  not import; not regressed.
- Registered verdicts (TT-H1 to H6, PR1 Z-rules, C2P contrast, H-new-1, AB1 rules): the battery reproduces the
  per-network statistics they are computed from, but prints no verdict, so arm-level verdict lines are not part of v1.
- Reads outside the per-network records of the eight readers: PR1 Z1b/Z3b (`z1b_read.py`), Z2b-tau5 (`z2b_read.py`),
  BD1 amendments 2 and 4 (FR similarity, colour, session gap), MEDS strata S1/S2, TT1-X part 2, the AB1 border-crossed
  and second-engine arms (AB1X, AB1FM). Not in v1.
- 2-A and 2-B on 403-407: not read in the table either (C2P platform gate failed).
- Not yet measured on hardware: the gate on a GPU (H100 smoke 6316361 pending; A100 PCIe not smoke-tested).

## 3. Gate test on the DGX CPU (TEST, never read)

`--test-gate-key "NVIDIA A100-PCIE-40GB|torch 2.2.1|tf32 1/1"` runs the A100 gate on the DGX CPU, where it must fail (a
different platform). Output `/mnt/t7/smad_next/BATTERY/test_gate_cpu/` (19:17-19:55, 38 min on 2 CPU threads).
Result, as designed: exit code 2, "BATTERY PLATFORM GATE FAILED", 2,496 of 2,496 reference logits differ (max |dlogit|
0.0563, median 0.00038, own-rule flips 0; stored reference range -3.59 to +3.46, 369 rows between -2 and +2); no row
scored; the temporary reference copy was removed. Same weights and images, other arithmetic: the byte-identity gate
detects it although no decision flips.

## Commands

```
cd /home/narolski/smad-next/src
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
nice -n 10 $PY -W ignore -m battery.regress --out ../experiments/BATTERY_shared-test-battery/regression_v1.json
nice -n 10 $PY -W ignore -m battery.stored --out /mnt/t7/smad_next/BATTERY/stored
$PY -m battery.cells --stored /mnt/t7/smad_next/BATTERY/stored --out ../experiments/BATTERY_shared-test-battery/cells_check_v1.json
$PY -m battery.read --include-stored /mnt/t7/smad_next/BATTERY/stored/* --json /mnt/t7/smad_next/BATTERY/read_stored_v1.json
CUDA_VISIBLE_DEVICES= HF_HOME=/mnt/t7/smad_next/PN1/fs_tree/pn1/hf HF_HUB_OFFLINE=1 nice -n 10 $PY -W ignore -m battery.run \
    --ckpt /mnt/t7/smad_next/PN1/results_fs/unpacked/PN1_Sb_s403 --arm Sb --seed 403 --out /mnt/t7/smad_next/BATTERY/test8_cpu \
    --device cpu --test-limit 8 --workers 2 --train-manifest /mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv
# after the smoke: fetch results/BATTERY/BATTERY_smoke_6316361.tar (+.sha256), then
$PY -m battery.smoke_check BATTERY_smoke_6316361.tar ../experiments/BATTERY_shared-test-battery/smoke_6316361.json
$PY -m battery.run --stats-only <unpacked>/AB1_Sb_s408      # zero-GPU completion of the statistics
```

## What is kept where

- Code `src/battery/` (committed). Small results: this folder (`regression_v1.json`, `cells_check_v1.json`,
  `read_stored_v1.txt`). Large: `/mnt/t7/smad_next/BATTERY/` (test outputs, 38 stored-logit records, stdout files,
  `battery_code_v1rc1.tar` + sha256). Nothing only in /tmp.
- WCSS: `packs/BATTERY/battery_code_v1rc1.tar`, `.sha256`, `battery_smoke.sbatch`; results will land in `results/BATTERY/`.
- The stored-logit records and the reader print contain no MEDS identifier (statistics only).
