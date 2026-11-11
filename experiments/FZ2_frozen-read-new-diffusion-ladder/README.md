# Frozen read of the new diffusion ladder (FZ2): full record

Owner: the frozen-features owner (also owner of FZ1). `prereg.md` = registration, `result.md` = short verdict (not yet
written), this file = full record. Code `/home/narolski/smad-next/src/FZ2/`, large outputs `/mnt/t7/smad_next/FZ2/`,
Athena folders `/net/pr2/projects/plgrid/plggrestoration/smad-next/{packs,results}/FZ2/`, logs `.../smad-next/logs/FZ2-<job>.out`.

## 1. Question and current answer

11 Nov 2026, 20:45 CET. Status: **registered; Athena job 1 submitted (waits for the last two DG1 production shards);
the primary images (DG1 add-on) are not generated yet** (array 3545907 pending, start estimate 12 Nov morning).
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

None yet (no DG1 feature read).

## 6. Checks

- 8-image DGX check of `fz2_feats.py` (both backbones): ran.
- `fz2_feats.py` on the DGX reproduces FZ1's features exactly on 64 A43 frames.
- `fz2_read.py` smoke on random features: runs end to end.
- Pending: the registered cross-environment check of the Athena container (inside job 1).

## 7. Dead ends and failures

- 20:35 `/mnt/t7` full while copying the 2.4 GB weights into the pack folder ("No space left on device"); partial copies
  removed; streamed the tar instead. Disk later back to 54 GB free (someone freed space).

## 8. Observations and ideas

- The production set B fold map puts the largest partner cycle (163 persons) alone into fold 0; folds 1–4 hold 92–94.

## 9. Open items and next steps

1. Job 1 (3545969) runs after 3545877; fetch `bash src/FZ2/fz2_fetch.sh prod`; run `fz2_envcheck.py` on
   `results/prod/out/{clip_mad,dinov2}_a43check.npz`; if it passes, `fz2_read.py --run prod`.
2. When the add-on tars exist: `sbatch packs/FZ2/fz2_job.sbatch addon addon_s0 … addon_s7`, fetch, check, `fz2_read.py
   --run addon` (the primary read), then `result.md`.

## 10. Handover state (20:45)

- Athena 3545969 (FZ2 job 1), pending on dependency `afterok:3545877`. If 3545877 fails, 3545969 never starts
  (DependencyNeverSatisfied): cancel it (`scancel 3545969`, my own job) and resubmit without the failed shard.
- Compute: Athena 0 so far; DGX: 8 + 64 + 64 image features (seconds).

## 11. Reproduce from scratch

```
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
# pack (streamed): see timeline 20:35; job: sbatch packs/FZ2/fz2_job.sbatch <TAG> <DG1 lists...>
bash src/FZ2/fz2_fetch.sh <TAG>
$PY -I src/FZ2/fz2_envcheck.py --clip .../<TAG>/out/clip_mad_a43check.npz --dino .../<TAG>/out/dinov2_a43check.npz --out <json>
OMP_NUM_THREADS=2 $PY -I src/FZ2/fz2_read.py --run prod --feats-dir /mnt/t7/smad_next/FZ2/results/prod/out
OMP_NUM_THREADS=2 $PY -I src/FZ2/fz2_read.py --run addon --feats-dir /mnt/t7/smad_next/FZ2/results/addon/out
```
