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

## Vast lease for the ViT-B/16 arm of the morph-free networks experiment (AD4): not opened

11 Nov, about 16:00 CET. The lead authorised one lease (cap 10 USD) for the ten ViT-B/16 tasks. Preparation done:
- Live Vast credit read: 111.85 USD. No instance of ours existed before or after.
- Container torch found in the WCSS logs: 2.2.1 / CUDA 12.1 / Python 3.10. Planned rented environment:
  `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime` + timm 1.0.27, huggingface_hub 0.36.2, safetensors 0.8.0,
  numpy 1.26.4.
- Chosen offer: 58777466, 2x RTX 4090 (China), 0.73 USD/h, reliability 0.997. It had the lowest price per unit
  of work among the 4090/5090 offers. Fallbacks: Quebec 58852161 (0.94 USD/h) and Slovakia 50305477 (1.07 USD/h).
- Scripts written but never run against a rented machine: `src/AD4/vast_api.py`, `src/AD4/vast/remote_setup.sh`,
  `src/AD4/vast/remote_queue.sh` and `src/AD4/vast/watchdog.py`. The watchdog stops at the cost cap, after 8 h,
  or when the queue is done and every result is copied back to the DGX and to WCSS.
- The instance-creation call was refused by this session's permission system (category "real-world
  transactions"). Nothing was rented and nothing was spent.
- The ten task directories were moved from WCSS `queue/ready` to `staging/AD4` before the attempt and then moved
  back to `queue/ready`. All 20 AD4 tasks are now in `ready/`.

## Vast lease for the ViT-B/16 arm of the morph-free networks experiment (AD4): opened by the main session

- **Exception to "no training on rented machines":** confirmed by the author for this one experiment (approved
  run on Vast, 11 Nov), because the WCSS scheduler forecasts no slot before 13 Nov 23:20. The rental commands
  (create and destroy) are run by the main session, not by the owner.
- **Instance:** 60223497, 2x RTX 4090, Sweden, reliability 0.992. Price 0.962 USD/h in total. Image
  `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, which matches the torch version of the WCSS container.
  Created 11 Nov about 16:08 CET; credit before creation 111.85 USD. Lease config
  `/mnt/t7/smad_next/AD4/vast/lease.json`: cap 9.6 USD, 8-hour deadline.
- **Watchdog:** `src/AD4/vast/watchdog.py` (PID 1952064), run from the DGX.
- **Tasks:** the ten ViT-B/16 task directories were moved out of the WCSS ready queue into `staging/AD4`
  before the queue started, so no cluster slot runs them twice.
- **Deviations from the WCSS path:**
  - Host Python from the image, not the SIF container. torch 2.2.1 matches the container; timm 1.0.27,
    huggingface_hub 0.36.2 and safetensors 0.8.0 are pinned to the WCSS library packs. numpy is pinned to
    1.26.4, and Pillow is the image's own.
  - No apptainer. `AD4_LOCAL=1` with the same `run.sh` and the same pack.
  - Cards are RTX 4090 instead of H100; 7 loader workers, as on WCSS.

## Rented path as run, and the gates of Amendment 1 of the morph-free networks experiment (AD4)

**Leases**
- Two aborted leases, nothing ran on either, 0.27 USD in total: lease 1 (2x RTX 4090, too small for batch 256)
  and lease 2 (2x RTX PRO 5000, never reachable over SSH).
- Machine A, the morph-free arm: instance 60226054, A100-SXM4-40GB, 0.433 USD/h.
- Machine B, the permuted arm: instance 60227348, RTX 6000 Ada (48 GB), 0.738 USD/h. It replaced instance
  60226099, which stayed unreachable.
- Both machines use image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime` with Python 3.10.13, torch 2.2.1 and
  timm 1.0.27.

**Smoke test, machine A** (200 steps, 8 scored images, `vast/leaseA/smoke.txt`)
- rc 0.
- Speed 1.83 it/s at step 100 and 1.90 it/s at step 200.
- Peak GPU memory 30,839 MiB (nvidia-smi).
- Projection: 6,250 steps / 1.9 it/s = 0.91 h of training, plus about 10 min of staging and scoring, so about
  1.1 h per network. Five networks run one after another: about 5.5 h and 2.4 USD on machine A.

**Gate 3, scorer equivalence: pass.** One ViT-B/16 network of the original morph-free run (A47 I-3) was
re-scored with `ad4_score.py` on the DGX: seed 1, last checkpoint, sha256 f9e391c4…, which equals its
registered list line. It was compared with its registered `scores_eval_last.npz` on the 24 shared cells
(diffusion and FRLL, native and E7).
- Largest |AUC difference|: 0.0011. Smallest Kendall tau: 0.9962. EERs are equal to 0.1 point.
- File: `gate_scorer_equivalence.json`.

**Gate 1 predictor, sample order:** `src/AD4/gates.py order` reproduces the recorded order of that original run
exactly (200 of 200 batches, seed 1). For seed 401 it gives [[139,117,0],[125,131,0],[124,132,0]], which
matches the reviewer's expectation and the DGX smoke test. Applied to each network when its result arrives.

**Gate 2, reproduction:** computed when the five morph-free ViT-B/16 networks are in.
