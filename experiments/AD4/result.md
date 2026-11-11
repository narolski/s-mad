# AD4 result (preparation stage; no trained AD4 network exists yet)

## What is staged

- Pack (one tar): `/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/AD4/ad4_pack.tar`, 11,193,948,160 bytes,
  sha256 `1ad170be30af949c55536f5dd6fff8c8c62b60f39b3faaa8bc134cb68967bfde` (checked on WCSS after upload). Local
  copy `/mnt/t7/smad_next/AD4/ad4_pack.tar`. Built by `src/AD4/build_pack.py`; contents and hashes in the pack's
  `ad4/build_info.json` and `ad4/SHA256SUMS` (69,941 files).
- 20 task directories: `/lustre/pd03/hpc-narolski-1790461090/smad-next/staging/AD4/AD4_{m3mf,m3perm,m3lmf,m3lperm}_s{401..405}`
  (run.sh = `src/AD4/run.sh`, task.env, est_minutes 75 for M3, 180 for M3L). Built by `src/AD4/make_tasks.sh`.
  Not in `ready/`; nothing submitted.
- Each task also copies `pylib.tar` and `pylib_a12.tar` from `smadcvpr/packs` (sha256 checked against their
  `.sha256`) and runs in `/lustre/software-data/container-images/pytorch_latest.sif`, as A47 did.
- Output per task: `/lustre/.../smad-next/results/AD4/<TASK>.tar` + `.tar.sha256` (meta.json, train.log,
  metrics.json, scores_eval.npz, scores_train.npz, last_trainable.pt = LoRA + head only, last_pt.sha256).

## Time estimate basis

A47 I-3 M3 `train_hours` 0.52 h (H100, `/mnt/t7/smad_heldout/a47/runs/A47I3/*vitb16*s1_i3/meta.json`); A12BR M3L
1.94 h (WCSS `~/jobs/smadcvpr_a12/logs/a12-br-t2-m3l-6207420_[0-4].out`). Plus pack staging (190 s on the DGX USB
disk) and scoring of 19,827 eval + 50,000 training images. Total about 21 H100-h. The fewer loader workers (7, slot
has 8 CPUs) are not expected to bind: M3 needs about 850 images/s.

## Tested on the DGX (same run.sh, same pack, AD4_LOCAL=1, host python .venv-spark, torch 2.12.1+cu130, timm 1.0.27)

| Task | Setting | Outcome |
|---|---|---|
| AD4_m3mf_s401 | AD4_STEPS=3, AD4_LIMIT=8, 4 workers | rc 0; pack sha + SHA256SUMS ok; train.py 3 steps; 8 eval + 8 train images scored; result tar copied and sha-checked (wall 452 s) |
| AD4_m3mf_s401 again | same result dir | "already done", rc 0 (idempotent) |
| AD4_m3lperm_s402 | AD4_STEPS=2, AD4_LIMIT=8 | rc 0; train.csv = train_perm_s402.csv; ViT-L/14 bs 32 x 8 accumulation; wall 360 s |

Logs: `/mnt/t7/smad_next/AD4/test/*.stdout.log`, results `/mnt/t7/smad_next/AD4/test/root/smad-next/results/AD4/`.

## Not tested

- The container path on WCSS (apptainer + SIF torch + pylib timm, x86 H100). Same SIF and library packs as A47,
  which trained these recipes there.
- A full-length run (6,250 steps) and full-manifest scoring of a trained network; peak GPU memory of M3 bs 256 on
  H100 (A47 ran the same batch).
- Rebuilding a network from `last_trainable.pt` + the pack weights (not checked bitwise).
- That the zero-step network equals train.py's step-0 state: by construction (same seeding, build_model, apply_lora
  order), not checked bitwise.

## Zero-step networks (DGX, full manifests)

See `zero_step/` (metrics_m3.json; metrics_m3l.json is written by a detached job, scorer started 15:38 CET, expected about 17:30, log `/mnt/t7/smad_next/AD4/zero_step_m3l.log`). Raw scores in `/mnt/t7/smad_next/AD4/zero_step/<recipe>/`
(m3: scores_eval.npz a846fbdf…, scores_train.npz c92b0065…). Point values only; person bootstrap at read time.

M3 zero-step (seed 401), EER % / signed AUC, native cells: MorDIFF 53.9 / 0.436; DiM 48.0–55.8 (AUC 0.41–0.52);
FRLL AMSL 37.3 / 0.656, FaceMorpher 33.4 / 0.708, OpenCV 34.8 / 0.680, Webmorph 32.8 / 0.722, StyleGAN 46.6 / 0.553;
corrected MAD22 FaceMorpher 44.6 / 0.579, OpenCV 49.9 / 0.492, Webmorph 41.2 / 0.620, MIPGAN-I 56.4 / 0.400,
MIPGAN-II 54.4 / 0.442. Training set (true labels): accuracy 0.295, AUC 0.227 (the random head ranks copies below
natives). So an untrained network is not at 0.5 on the FRLL landmark cells (AUC up to 0.72).

Note on E7 cells: FRLL StyleGAN and corrected MAD22 MIPGAN-I / MIPGAN-II E7 photos are byte-identical to the native
bona fide (checked with cmp on one file each; those families' IED is not below the photos', so no resampling is
applied). Their E7 cells therefore equal the native cells and carry no extra information.
