# Frozen read of the new diffusion ladder (FZ2): full record

Owner: the frozen-features owner (also owner of FZ1). `prereg.md` = registration, `result.md` = short verdict (not yet
written), this file = full record. Code `/home/narolski/smad-next/src/FZ2/`, large outputs `/mnt/t7/smad_next/FZ2/`,
Athena folders `/net/pr2/projects/plgrid/plggrestoration/smad-next/{packs,results}/FZ2/`, logs `.../smad-next/logs/FZ2-<job>.out`.

## 1. Question and current answer

12 Nov 2026, 03:30 CET. Status: **finished.** H-new-1 not decided, H-new-2 not decided, H-new-3 falsified, H-new-4
falsified (registered readings on the DG1 add-on).
Question: on the new diffusion-autoencoder ladder (DG1) with fresh persons (FRGC, colorFERET), do frozen CLIP ViT-L/14
and DINOv2 features, and the frozen SMDD heads of FZ1, read mixing, or only "not rendered from its own noise map"
(H-new-1, H-new-2); does the frozen heads' weak ordering of two-person over same-person mixes replicate with an excess
over simple statistics (H-new-3); and does the two-person-against-same-person probe read input disagreement (H-new-4)?
No answer yet.

## 2. Timeline

- 20:20 Lead's order (after the FZ1 review): new experiment FZ2, registration before any feature of new images.
- 20:28–20:32 Read the DG1 README, prereg (amendment 1 reading rules, amendment 2 add-on), result, `ATHENA.md`,
  `src/AR1/folds.py`, `src/AR1/baselines.py`, `src/AR1/blank.py`, `src/DG1/dg1_validity.py`,
  `src/DG1/dg1_manifest_extra.py`, the DG1 job lists (production `/mnt/t7/smad_next/DG1/jobs/`, add-on
  `/mnt/t7/smad_next/DG1/addon_jobs/`). No DG1 image opened.
- 20:32 `prereg.md` written.
- 20:33 `src/FZ2/fz2_feats.py` written. **8-image check on the DGX** (real command line, both backbones) on the first 8
  PNGs of production shard 1 (`/mnt/t7/smad_next/DG1/gen/setB_s1`): ok, outputs
  `/mnt/t7/smad_next/FZ2/dgx_check8/{clip_mad,dinov2}_setB_s1_smoke.npz`.
- 20:34 64 A43 check frames (8 per arm A, B, B20, C, C20, D, D20, E; byte copies, sha checked) →
  `/mnt/t7/smad_next/FZ2/pack/fz2pack/a43check/` + `a43check.csv`. `fz2_feats.py` on them on the DGX and
  `src/FZ2/fz2_envcheck.py` against FZ1's DGX features: identical (cosine 1.0, max |Δ logit| 0.0;
  `envcheck_dgx_vs_fz1.json`). So the FZ2 script reproduces FZ1's features; the Athena check compares the container
  with this.
- 20:35 Pack build failed: **/mnt/t7 full** (20 KB free). Removed my partial copies, told the lead. Rebuilt the pack as a
  symlink staging folder and **streamed** the tar to Athena (no local tar): `fz2_pack.tar`, 2,444,308,480 bytes, sha256
  26c12258b4e1183efa446b0ab59658a6fd0b1fb34b9b2a0847918dac09994d18 (contents and per-file hashes in
  `/mnt/t7/smad_next/FZ2/pack/fz2pack/MANIFEST.sha256`). Checked on Athena with `sha256sum -c` (a 2.4 GB read on the
  login node; the jobs re-check it, later checks stay inside jobs).
- 20:39 **Athena job 1 submitted: 3545969** (`sbatch --dependency=afterok:3545877 packs/FZ2/fz2_job.sbatch prod setB_s0
  setB_s1 setB_s2 setB_s3`; account `plgmultivision-gpu-a100`, `-C memfs`, `--exclude=t0010`, 1 A100, 1 h limit). It
  starts after the DG1 production array 3545877 (shards 0 and 2) finishes.
- 20:40 `src/FZ2/fz2_read.py` (registered analysis) written; smoke on **random features** for the production shards 1
  and 3 (120 hosts, B = 300): code paths run end to end. Its printout showed one real number: the best simple baseline
  for X20 vs SAME20 on those 120 hosts is about 0.70 (baselines use the real images). Smoke outputs deleted.
- 20:44–21:29 Job 1 pending (DG1 shards 0 and 2 finished about 21:10; then "Priority"); `squeue --start` gave 12 Nov
  04:27 (most Athena nodes unavailable). DG1 add-on shards 0 and 1 were generated and fetched to the DGX meanwhile.
- 21:31 Deviation (recorded in `prereg.md`): features computed on the DGX with `fz2_feats.py` in FZ1's environment
  (exact match to FZ1, so no cross-environment check needed). `src/FZ2/fz2_dgx_feats.sh setB_s0 setB_s1 setB_s2
  setB_s3` started (log `/mnt/t7/smad_next/FZ2/dgx_feats_prod.log`, per-try logs `/mnt/t7/smad_next/FZ2/logs/`); about
  16 img/s; one CUDA out-of-memory at model load (retried after 90 s). Athena job 3545969 cancelled before it started
  (0 GPU-hours). My `pkill -f "fz2_wait_fetch.sh prod"` also killed its own shell (the pattern was in its command line;
  the same mistake as FZ1 dead end 4); the scancel had already run (sacct: CANCELLED, 0 s).
- 21:33 `src/FZ2/fz2_dgx_addon_watch.sh` started (log `/mnt/t7/smad_next/FZ2/dgx_addon_watch.log`): after the production
  extraction, every 5 minutes it extracts each add-on shard whose DGX copy is complete (PNG count = job count).
- 21:31–21:41 Production features done (8 files in `/mnt/t7/smad_next/FZ2/results/dgx/out/`, about 1 min per file).
- 21:41 Registered production read: `OMP_NUM_THREADS=1 python -I src/FZ2/fz2_read.py --run prod --feats-dir
  /mnt/t7/smad_next/FZ2/results/dgx/out --workers 1` (log `/mnt/t7/smad_next/FZ2/logs/read_prod.log`; serial baselines
  so that at most 6 CPU processes of mine run beside the extraction) → `read_prod.json`, items
  `/mnt/t7/smad_next/FZ2/read_prod_items.csv`. Results in `result.md` and section 5.
- 21:41–21:46 Add-on shards 0 and 1 extracted by the watcher.
- 21:50 `result.md` (production, secondary) written; interim status sent to the lead.
- 21:55–00:00 Waiting for DG1 add-on shards 2–7: Athena array 3545907 pending (`ReqNodeNotAvail`; `sinfo`: 13 nodes
  reserved, 11–12 mixed; start estimate N/A). Both FZ2 watchers alive.
- 00:09–00:14 Add-on shard 2 arrived (DG1 owner's copy, 1,258 PNG) and was extracted by the watcher. Shards 3–7 still
  pending on Athena at 00:43 (`ReqNodeNotAvail`).
- 00:50 Lead: shards 2–7 come from a rented RTX 3090 (generation owner's driver, passed the registered equivalence
  check), unpacked into the same `/mnt/t7/smad_next/DG1/gen/addon_s<k>/` with a `PLATFORM.txt` (shard 2 is rented; 0, 1
  Athena); last shard about 03:15. Each shard is self-contained, so no contrast mixes platforms within a host.
  `fz2_read.py` patched before any add-on read: column `platform` (rented if `PLATFORM.txt` exists, else athena) and
  per-platform sensitivity rows beside unflagged / FRGC / colorFERET. Watchers unchanged (they already found shard 2).
- 00:51–03:10 Shards 3–7 extracted by the watcher as each arrived (rented, about 37 min apart).
- 03:19 The automatic read had not started: its `pgrep -f "fz2_feats.py --backbone"` matched the still-open launching
  shell (PID 2632680, whose command line held the script text). Killed both (my own), ran the read by hand:
  `OMP_NUM_THREADS=2 python -I src/FZ2/fz2_read.py --run addon --feats-dir /mnt/t7/smad_next/FZ2/results/dgx/out
  --workers 3` (log `/mnt/t7/smad_next/FZ2/logs/read_addon.log`) → `read_addon.json`, items
  `/mnt/t7/smad_next/FZ2/read_addon_items.csv`. Readings: H-new-1 not decided, H-new-2 not decided, H-new-3 falsified,
  H-new-4 falsified (numbers in `result.md`).
- 03:30 `result.md` completed; report sent.
- 12 Nov: independent review (`experiments/reviews/REVIEW_FZ2_AR1A10_20261112.md`, commit a91e120) applied (F1–F7) in commit
  8be8361; DG1 platform-equivalence record `experiments/DG1_diffusion-generation-athena/platform_reproducibility_fz2.json`.
- 12 Nov: amendment 1 registered (commit dbc151d) before computing; smoke (120 hosts, B = 300; output deleted), full run
  `OMP_NUM_THREADS=2 nice -n 10 python -I src/FZ2/fz2_amend1.py` (log `/mnt/t7/smad_next/FZ2/logs/amend1.log`) →
  `amend1.json`: H-A transfer supported, H-B falsified, H-C supported (numbers in `result.md`).
- 12 Nov: draft DG1 amendment for SAME_orth / X_corr rungs written for pre-run review:
  `experiments/DG1_diffusion-generation-athena/drafts/AMENDMENT_SAMEorth_Xcorr_DRAFT.md` (not run).

## 3. Data

- DG1 images (read-only): production set B tars on Athena `.../results/DG1/DG1_setB_s{0..3}.tar` (+ `.sha256`), DGX
  copies `/mnt/t7/smad_next/DG1/gen/setB_s{k}/` (shards 1 and 3 fetched by the DG1 owner); add-on tars
  `DG1_addon_s{0..7}.tar` (not yet generated). Metadata: DG1 job lists (`set,pool,rung,name,src_a,src_b,alpha,steps,
  host,partner[,mode,fresh_k]`), pool `/home/narolski/smad-next/experiments/AR1/pool.csv` (sha256 86101978…; partner
  cycles), DiffAE-aligned inputs `/mnt/t7/smad_next/DG1/pool_a256/` (pair disagreement, input flags).
- Pack contents (`fz2pack/`): `code/fz2_feats.py` (sha e855f29d…), `code/common.py` (unchanged
  `mambamorph-code/smadcvpr/common.py`, ee71517a…), `weights/madation_fe_vitl14_model.safetensors` (74dd7fbc…, the
  released MADation FE ViT-L/14 file; its `net.*` tensors are OpenAI CLIP ViT-L/14), `weights/dinov2_vitl14_lvd142m.safetensors`
  (0424a5d1…, local timm cache), `a43check/` (64 frames), `a43check.csv` (13466276…).
- Heads (no refit): `/mnt/t7/smad_next/FZ1/heads/head_s40{1..5}.pt`, release head in the FE file.
- Produced so far: `/mnt/t7/smad_next/FZ2/dgx_check8/` (8-image and 64-frame DGX features).

## 4. Code (`/home/narolski/smad-next/src/FZ2/`)

- `fz2_feats.py`: frozen features (clip_mad, dinov2) of every PNG under a folder or of a list; DGX or container.
- `fz2_envcheck.py`: registered cross-environment check on the 64 A43 frames against FZ1's DGX features.
- `fz2_pack.sh`: first pack builder (copies; failed on the full disk; the streamed variant is in the timeline).
- `fz2_job.sbatch TAG DG1_LIST...`: Athena job (pack and DG1 tar sha checks, unpack into `$MEMFS`, container
  `smad_torch221_cu121_v1.sif`, both backbones on the A43 check frames and each DG1 tar, one result tar
  `results/FZ2/FZ2_<TAG>.tar` + `.sha256`).
- `fz2_fetch.sh TAG...`: copy back, sha check, unpack into `/mnt/t7/smad_next/FZ2/results/<TAG>/`.
- `fz2_read.py --run prod|addon --feats-dir DIR`: the registered analysis (heads, out-of-fold probes with partner-cycle
  folds from `src/AR1/folds.py`, five baselines, person bootstrap, readings, sensitivity).
- Environments: DGX `/home/narolski/mambamorph-code/.venv-spark` (torch 2.12.1, timm 1.0.27); Athena container
  (torch 2.2.1, timm 1.0.27, sha256 fedeff10…).

## 5. Results

Production set B: the same 536 hosts and pairs re-rendered with the same deterministic sampler; its agreement with the
add-on is a cross-platform reproducibility check (Athena A100 vs RTX 3090), not an independent replication (review F1).
Full table in `result.md`, all numbers in `read_prod.json`:
- Heads s401 / release, X20 vs SAME20: 0.662 [0.622, 0.699] / 0.665 [0.625, 0.703]; best baseline thumb32 0.700
  [0.656, 0.741]; excess −0.038 [−0.094, +0.019] / −0.035 [−0.089, +0.023]. Heads s402–s405 0.660–0.661.
  SAME20 vs REC20 0.378 / 0.396; X20 vs REC20 0.537 / 0.561; MIR20 vs REC20 0.702 / 0.722.
- Baselines X20 vs SAME20: PNG 0.603, Laplacian 0.695, asymmetry 0.631 (X lower each), thumb32 0.700, surround 0.669.
- clip_mad probes: D_SR (SAME vs REC) 0.999; along it X vs REC 0.987, MIR vs REC 0.994, X vs SAME 0.162. P_XS (X vs
  SAME) 0.941 [0.923, 0.957]; stratified by d 0.933, Δ +0.008 [+0.001, +0.017]; A_hi 0.912. P_XS mean scores: SAME
  −2.81, MIR −0.64, REC +2.21, X +2.17, dose α 0.1–0.4 +2.37 to +2.52. dinov2: P_XS 0.953, Δ +0.007.
Add-on (primary): see `result.md` (all registered numbers, sensitivity per platform) and `read_addon.json`.

## 6. Checks

- 8-image DGX check of `fz2_feats.py` (both backbones): ran.
- `fz2_feats.py` on the DGX reproduces FZ1's features exactly on 64 A43 frames.
- `fz2_read.py` smoke on random features: runs end to end.
- The registered cross-environment check of the Athena container was never run: job 3545969 was cancelled before it
  started and every feature (production and add-on) was computed on the DGX (dated deviations in `prereg.md`).
- Independent review 12 Nov (`experiments/reviews/REVIEW_FZ2_AR1A10_20261112.md`): every registered number reproduced
  from `read_addon_items.csv`; verdict needs qualification (F1–F7 applied to `result.md` 12 Nov).

## 7. Dead ends and failures

- 20:35 `/mnt/t7` full while copying the 2.4 GB weights into the pack folder ("No space left on device"); partial copies
  removed; streamed the tar instead. Disk later back to 54 GB free (someone freed space).

## 8. Observations and ideas

- The production set B fold map puts the largest partner cycle (163 persons) alone into fold 0; folds 1–4 hold 92–94.

## 9. Open items and next steps

1. Post hoc amendment 1 (zero GPU, `prereg.md`): P_XS and D_SR on the noise-only / semantic-only rungs with H-A's
   transfer predictions, θ- and Laplacian-stratified readings; residual + simple floor for every contrast (H-B); H-C on
   FZ1's A43 frames; P_XS applied to the A43 frames.
2. Draft DG1 amendment for SAME_orth / X_corr rungs (H-A causal test), for pre-run review.

## 10. Handover state (03:30, 12 Nov)

Nothing of FZ2 is running. Compute: Athena 0 GPU-hours (3545969 cancelled before start); DGX GB10 about 40 min of
shared GPU time (features) plus CPU reads.

## 11. Reproduce from scratch

```
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
# pack (streamed): see timeline 20:35; job: sbatch packs/FZ2/fz2_job.sbatch <TAG> <DG1 lists...>
bash src/FZ2/fz2_fetch.sh <TAG>
$PY -I src/FZ2/fz2_envcheck.py --clip .../<TAG>/out/clip_mad_a43check.npz --dino .../<TAG>/out/dinov2_a43check.npz --out <json>
OMP_NUM_THREADS=2 $PY -I src/FZ2/fz2_read.py --run prod --feats-dir /mnt/t7/smad_next/FZ2/results/prod/out
OMP_NUM_THREADS=2 $PY -I src/FZ2/fz2_read.py --run addon --feats-dir /mnt/t7/smad_next/FZ2/results/addon/out
```
