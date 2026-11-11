# Morph-free networks (AD4): result

Status 11 Nov 2026, 23:50 CET. ViT-B/16 recipe: read; flagged "not reproduced on this stack"; descriptive until the WCSS
cluster rerun decides. ViT-L/14 recipe: running on Athena (3 of 10 networks back); not read. Every statement below is
**in our preprocessing** (our alignment of every benchmark, "our frames"). Full tables: `ad4_reading_m3.md`, post hoc
addendum `posthoc_m3.md` (prereg Amendment 3); record: `README.md`. Wording follows the independent review
`experiments/reviews/REVIEW_AD4_VITB_20261111.md`.

## What the networks are

CLIP ViT-B/16 with LoRA, five seeds (401 to 405), last checkpoint, **trained only to flag shrink-and-enlarge copies of
synthetic SMDD faces (no morph, no blending)**: label 0 = SMDD renders, label 1 = their copies shrunk to 31% and enlarged
again. Training saturates: natives at a logit of about -3.65, copies at about +3.62 (5th to 95th percentile within 0.03;
posthoc_m3 A). References: five networks trained on the same images with shuffled labels and the untrained network.
The label-permuted networks partly learned the true task (true-label accuracy 0.399 to 0.686), so they are conservative
references; they show the effect needs the true labels, not which feature carries it.

## ViT-B/16 recipe, in our preprocessing (flag: not reproduced on this stack)

- **Flag.** Reproduction gate missed on 1 of 11 cells: Fast-DiM-ODE native, morph-free seed mean 4.01% against a bound of
  3.0 (per seed 8.72, 1.88, 3.96, 0.10, 5.40). The other ten cells are inside their bounds. The original morph-free run
  (A47 I-3, three other seeds, WCSS H100) gave MorDIFF 0.00 and DiM 0.00 to 1.17%. So: seen on two stacks; the
  registered cluster rerun is pending (queued on WCSS, which refuses connections tonight).
- **Registered cells.** MorDIFF native (primary): EER 0.0% in all five seeds [95% CI 0.0, 0.0]; references 37.3 to 60.8%
  (untrained 53.9%). Six DiM natives (secondary): 0.0 to 4.0% (DiM-A 0.8, DiM-C 0.0, Fast-DiM 1.7, Fast-DiM-ODE 4.0,
  Greedy-DiM 2.4, Greedy-DiM-S 1.0); references 37.2 to 63.3%. By the registered rule each of the seven is "passable
  without morphs" (5 of 5 seeds meet the 10-point margin; native margins -33 to -41 points) and A1 is not falsified on
  any. A network that never sees a morph or a blended image, trained only to detect resampling of synthetic faces,
  reaches these numbers; low error on these cells therefore cannot by itself be read as evidence of morph detection.
- **Descriptive cells.** FRLL AMSL 1.1%, FaceMorpher 4.1%, Webmorph 1.0% (each at least 10 points below every label-free
  reference, lowest 24.0 to 27.4%; not "above chance": the untrained network reaches AUC up to 0.72 there); FRLL OpenCV
  19.7% (per seed 7.9 to 40.2; not passable); FRLL StyleGAN 32.9%. Corrected MAD22 FaceMorpher 0.0%; OpenCV 34.3%;
  Webmorph 27.2% (meets the margin in 3 of 5 seeds, above 15% in 5 of 5; borderline, not a headline). Corrected MAD22
  MIPGAN-I and MIPGAN-II reversed in all five seeds (AUC 0.017 to 0.438; no seed mean).
- **Resolution-history matching (E7)** removes or overshoots the cue on DiM-A, Fast-DiM and Fast-DiM-ODE (AUC 0.02 to 0.52;
  DiM-A and Fast-DiM-ODE reversed in all five seeds). The history-matched genuine photos there are softer than the morphs
  (file-size null AUC 0.10 to 0.44). It does **not** remove the cue on MorDIFF (2.9%, per seed 0.4 to 5.4, AUC 0.990 to
  1.000), DiM-C (21.7%, AUC 0.72 to 0.93), corrected MAD22 FaceMorpher (0.1%) or the FRLL landmark cells (AMSL 8.2,
  Webmorph 7.8, FaceMorpher 11.1%; OpenCV split). Greedy-DiM and Greedy-DiM-S split by seed (AUC 0.014 to 0.987 and
  0.185 to 0.877; no seed mean). What carries the remaining cue on MorDIFF, MAD22 FaceMorpher and the FRLL landmark cells
  is not identified here; candidates are the surround, border, watermark and blending softness (untested).
- **Fixed thresholds, flag and miss rates together.** Every genuine photo sits near the trained floor. At the 0.5 rule the
  morph-free networks flag 0.0% of unprocessed genuine photos and miss 64.5% of MorDIFF morphs (per seed 4.1 to 98.4),
  86 to 100% of DiM morphs and 100% of every FRLL family; they miss 4.3% of corrected MAD22 FaceMorpher morphs while
  flagging 0.0% of its unprocessed genuine photos. The FRLL-5% threshold lies at p = 0.027 to 0.036, just above the floor:
  there MorDIFF morphs are missed 0.0% while **50.7% of MorDIFF's own unprocessed genuine photos are flagged** (per seed
  1.0, 70.1, 54.9, 87.7, 39.7%); DiM morphs are missed 0.0 to 4.1% with 4.9% of DiM genuine photos flagged. That 100% of
  history-matched genuine photos are flagged at FRLL-5% in the MorDIFF, DiM and MAD22 FaceMorpher E7 cells follows from the
  training task (E7 is the same kind of operation as the training positives) and adds nothing about the benchmarks.
- **File size alone** (smaller PNG = morph) separates the native cells of our frames at AUC 0.72 to 1.00 for the diffusion,
  FRLL landmark and MAD22 FaceMorpher cells (Greedy-DiM 0.72, Fast-DiM-ODE 0.86, the others 0.95 to 1.00; MorDIFF 0.999,
  MAD22 FaceMorpher 1.000), and inside each cell the network score
  rises with smaller file size (Spearman 0.14 to 0.89 in native cells). Our aligner's border around smaller morph files
  lowers file size, so softness and border are confounded in our frames (posthoc_m3 C).

## Withdrawn

- WITHDRAWN (my reading section of 23:36, "E7 cells: MorDIFF 2.9; DiM 21.7 to 75.9 (AUC 0.18 to 0.85)"): as a summary of
  the history-matched control it hid that the control does not remove the cue on MorDIFF, DiM-C and the landmark cells and
  overshoots elsewhere; replaced by the E7 paragraph above.
- WITHDRAWN ("Fixed thresholds: ... at FRLL-5%, diffusion misses 0 to 4.1% with 100% of history-matched genuine photos
  flagged"): the 100% follows from the training task, and the sentence left out the 50.7% flag rate of MorDIFF's own
  genuine photos; replaced by the fixed-threshold paragraph above.
- WITHDRAWN (wording "never saw a morph" alone, and "storage history"): replaced by "trained only to flag shrink-and-enlarge
  copies of synthetic faces (no morph, no blending)" and "resolution history" (E7 imitates shrink-and-enlarge, not file
  format or compression).
- WITHDRAWN ("Rebuilding a network from `last_trainable.pt` + the pack weights: not tested"): tested by the pre-run reviewer,
  203 tensors, 0 differ (README 6.1).
- WITHDRAWN (seed means of reversed or split cells, e.g. Greedy-DiM E7 "49.9%", MIPGAN-I "76.4%"): averages of networks that
  separate strongly in opposite directions; per-seed values only (posthoc_m3 D).

## Not verified

- Anything outside our preprocessing (own-crop re-score RS1 not run; no border control yet).
- The cluster rerun of the ten ViT-B/16 networks (queued on WCSS).
- Which image feature carries the cue (follow-ups H-new-1 to H-new-5 of the review, to be registered).

## Run record (preparation, leases, gates; earlier text kept, superseded items marked)


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
- ~~Rebuilding a network from `last_trainable.pt` + the pack weights (not checked bitwise).~~ Corrected 11 Nov 22:50:
  this was tested by the pre-run reviewer on the DGX smoke network: `build_run_model(meta)` + pack weights +
  `last_trainable.pt` reproduce `last.pt`, 203 tensors, 0 differ (README section 6.1).
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

## Gates of the trained networks (11 Nov 22:41 to 22:43; reader `src/AD4/summarise.py --stage gates`)

Our frames throughout. Files: `ad4_gates_m3.json`, `ad4_gates_m3l.json`.
- ViT-B/16 (rented: morph-free on A100-SXM4-40GB, label-permuted on RTX 6000 Ada; torch 2.2.1), 9 of 10 tars at gate time:
  no refusal; sample-order gate 9 of 9 pass (200/200).
- **Reproduction gate: MISS, "not reproduced on this stack"**, 1 of 11 cells: Fast-DiM-ODE native, morph-free seed mean 4.01%
  against a bound of 3.0 (seeds 401 to 405: 8.72, 1.88, 3.96, 0.10, 5.40). The 10 other cells are inside their bounds
  (README, "Gates"). Lead's ruling: the flag stands on every ViT-B/16 number; the registered remedy (the ten ViT-B/16
  tasks on WCSS, still in its ready queue) decides when WCSS reopens; until then the rented arm is read descriptively.
- Scorer-equivalence gate: pass (16:46).
- ViT-L/14 (Athena array 3544219, A100 40 GB): 1 of 10 tars at gate time (`AD4_m3lmf_s402`, hash OK); sample-order gate pass.

### Superseded reading text of 23:36 (kept for the record; see "Withdrawn")

> ## Reading, ViT-B/16 recipe (11 Nov 23:36; flagged "not reproduced on this stack", read descriptively)
>
> Our frames. Tables: `ad4_reading_m3.md`; rows `ad4_cells_m3.csv`. Ten networks plus the untrained one; no refusal; order gate 10/10.
> EER %, morph-free seed mean [95% person-bootstrap interval]:
> - MorDIFF native (primary) 0.0 [0.0, 0.0]; references 37.3 to 60.8; "passable without morphs" yes (5/5 seeds); A1 not falsified.
> - DiM natives (secondary) 0.0 to 4.0; all passable (5/5 seeds); A1 not falsified on any.
> - E7 cells: MorDIFF 2.9; DiM 21.7 to 75.9 (AUC 0.18 to 0.85).
> - FRLL AMSL 1.1, FaceMorpher 4.1, Webmorph 1.0, OpenCV 19.7, StyleGAN 32.9. Corrected MAD22 FaceMorpher 0.0, OpenCV 34.3, Webmorph 27.2,
>   MIPGAN-I 76.4, MIPGAN-II 75.1.
> - Fixed thresholds: at the 0.5 rule, 0% genuine flagged, MorDIFF miss 64.5%, DiM miss 86 to 100%; at FRLL-5%, diffusion misses 0 to 4.1%
>   with 100% of history-matched genuine photos flagged in the MorDIFF and DiM E7 cells.
