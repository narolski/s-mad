# Morph-free networks (AD4): result

Status 13 Nov 2026, 08:45 CET: **both recipes read as registered.** Every statement is **in our preprocessing** (our alignment
of every benchmark, "our frames"). Platforms are facts of each number: ViT-B/16 registered arm on WCSS H100 (cluster stack, Amendment 5);
ViT-L/14 registered arm on Athena A100 40 GB (morph-free 401, 402, label-permuted 401 to 405) and WCSS H100 (morph-free 403 to 405).
Tables: `ad4_reading_m3.md`, `ad4_reading_m3l.md`, post hoc readings `posthoc_m3.md`, `posthoc_m3l.md`; record `README.md`. Wording
follows `experiments/reviews/REVIEW_AD4_VITB_20261111.md`.

## What the networks are

CLIP with LoRA, five seeds (401 to 405), last checkpoint, **trained only to flag shrink-and-enlarge copies of synthetic SMDD faces (no
morph, no blending)**: label 0 = SMDD renders, label 1 = their copies shrunk to 31% and enlarged again. Training saturates: ViT-B/16
natives at a logit of about -3.65 and copies at about +3.62; ViT-L/14 -4.07 and +4.02 (5th to 95th percentile within 0.03).
References per recipe: five networks trained on the same images with shuffled labels and the untrained network. The label-permuted
networks partly learned the true task (true-label accuracy 0.40 to 0.69 for ViT-B/16, 0.36 to 0.68 for ViT-L/14), so they are
conservative references.

**Bounded head (affects every threshold read in this experiment).** The head is a linear layer on L2-normalised CLIP features
(`archs_a12.py` line 277), so a logit cannot exceed the head's weight norm plus its bias. Measured on the trained tensors (ViT-B/16 rented arm, ViT-L/14 Athena arm): ViT-B/16
morph-free ||w|| 3.72 to 3.76, bias -0.035 to 0.013 (logits bounded at about ±3.8); ViT-L/14 morph-free ||w|| 4.16 (bound about
±4.17); label-permuted ViT-B/16 ||w|| 0.61 to 0.65 (bound about ±0.65, hence their logits near 0). Every genuine photo of a
training-like source therefore sits on a floor about 0.03 logits wide, and the FRLL-5% threshold lies a few hundredths of a logit
above it: flag rates at FRLL-5% read a cosine band about 0.03 wide, not a large score difference. The same mechanism is documented
for the protocol network's fits in `experiments/reviews/REVIEW_PN1_TIER1_20261112.md` (finding 1: ||w|| 3.84 to 3.86, logits
within about ±3.87).

## Gates

- Scorer equivalence on the H100 stack (Amendment 5 (c)): the A47 I-3 seed-1 network re-scored with `ad4_score.py` in the WCSS
  container (job 6308825) equals its registered scores in all 24 shared cells (|AUC difference| 0.0, Kendall tau 1.0). This is a
  same-stack, bitwise self-consistency check (the registered file was itself scored on a WCSS H100): score files sha256 `97eae24c…`
  (H100 re-score) and `2c3fba3e…` (registered). `gate_scorer_equivalence_h100.json`. The DGX scorer gate (11 Nov) also passed.
- Sample-order gate: 10 of 10 WCSS ViT-B/16 networks, 10 of 10 registered ViT-L/14 networks, 10 of 10 WCSS ViT-L/14 repeats, 10 of
  10 rented ViT-B/16 networks: all pass (200 of 200 batches). No network refused.
- **Reproduction gate, ViT-B/16 cluster rerun: pass, "reproduced on the cluster stack"** (11 of 11 cells; morph-free seed means
  MorDIFF 0.00, DiM-A 0.97, DiM-C 0.00, Fast-DiM 1.92, Fast-DiM-ODE 2.69, Greedy-DiM 0.22, Greedy-DiM-S 0.79, FRLL FaceMorpher 2.45,
  Webmorph 0.70, AMSL 0.58, OpenCV 17.72 against the bounds 3.0 / 5.6 / 8.8 to 26.0). The same five seeds gave 4.01 on Fast-DiM-ODE on
  the rented stack, so the pass is within platform-to-platform variation: "reproduced" is specific to the cluster stack. The rented arm's miss (Fast-DiM-ODE 4.01) stays
  on the rented arm, which is now a cross-platform repeat.

## ViT-B/16 recipe, registered (WCSS H100, jobs 6308830_0 to _9, 13 Nov 03:44 to 06:46), in our preprocessing

- **Registered cells.** MorDIFF native (primary): EER 0.0% in all five seeds [95% CI 0.0, 0.0]; references 37.3 to 60.8% (untrained
  53.9%). Six DiM natives (secondary): DiM-A 1.0, DiM-C 0.0, Fast-DiM 1.9, Fast-DiM-ODE 2.7, Greedy-DiM 0.2, Greedy-DiM-S 0.8%;
  references 37.3 to 63.8%. Each of the seven is "passable without morphs" (5 of 5 seeds meet the 10-point margin; margins -34.6 to
  -42.5 points) and A1 is not falsified on any. A network that never sees a morph or a blended image, trained only to detect
  resampling of synthetic faces, reaches these numbers; low error on these cells therefore cannot by itself be read as evidence of
  morph detection.
- **Descriptive cells.** FRLL AMSL 0.6, FaceMorpher 2.5, Webmorph 0.7% (each at least 10 points below every label-free reference; the
  untrained network reaches AUC up to 0.72 there, so not "above chance"); FRLL OpenCV 17.7% (per seed 6.3 to 34.2; not passable);
  FRLL StyleGAN 33.1%. Corrected MAD22 FaceMorpher 0.0% native and 0.0% history-matched; OpenCV 37.0; Webmorph 26.7 (borderline:
  margin met in 3 of 5 seeds, above 15% in 5 of 5); MIPGAN-I and MIPGAN-II reversed in all five seeds (no seed mean).
- **Resolution-history matching (E7)** removes or overshoots the cue on DiM-A (59.7%), Fast-DiM (56.4%) and Fast-DiM-ODE (reversed in
  all seeds). It reduces but does not remove it on DiM-C (19.4%, AUC 0.72 to 0.93), and does not remove it on MorDIFF (2.4%, per seed 0.1 to 5.5), corrected MAD22 FaceMorpher (0.0%) or the
  FRLL landmark cells (AMSL 4.8, FaceMorpher 7.0, Webmorph 4.5%). Greedy-DiM and Greedy-DiM-S history-matched cells split by seed
  (EER 3.0 to 84.4 and 17.2 to 72.0; no seed mean).
- **Fixed thresholds, flag and miss rates together.** At the 0.5 rule: 0.0% of unprocessed genuine photos flagged; 71.1% of MorDIFF
  morphs missed (per seed 5.0 to 98.7), 90.3 to 100% of DiM morphs (DiM-C per seed 51.4 to 100) and 100% of FRLL morphs missed, 7.2% of corrected MAD22
  FaceMorpher morphs missed. At FRLL-5% (on the floor, see above): 0.0% of MorDIFF and DiM-C morphs missed while 60.9% of MorDIFF's
  own genuine photos are flagged (per seed 30.4 to 92.6) and 4.9% of DiM genuine photos.
- **Cross-platform repeat (the rented arm, same tasks and seeds, A100 / RTX 6000 Ada, torch 2.2.1).** 340 network-cell pairs: median
  |EER difference| 0.34 points; largest 21.1 points (morph-free seed 403), largest |AUC difference| 0.27. Label-permuted networks
  agree within 0.9 points; morph-free seeds 401, 402, 403 differ by up to 14.9, 8.3, 21.1 points in some cells. The registered
  verdicts are the same on both stacks for all seven registered cells. On registered cells the largest same-seed difference is 10.7
  points (Greedy-DiM native, seed 401: 11.2% rented, 0.5% WCSS). The differences are shifts of whole networks (rented seed 401 is worse
  by 5.7 points on average over 34 cells, 27 of 34 in the same direction), about as large as the differences between seeds (median ratio
  0.94), so a per-seed number describes one run, not a seed. `xplat_m3_wcss_vs_rented.md`.

## ViT-L/14 recipe, registered (Athena A100 and WCSS H100, Amendment 5), in our preprocessing

- MorDIFF native (primary): 0.0% in all five seeds; references 41.2 to 52.0%; passable; A1 not falsified. The morph-trained ViT-L/14
  recipe (A12BR R × d0: the benchmark-recipe ViT-L/14 retrains on SMDD morphs, five seeds, last checkpoint, same files) reaches 48.7%
  (34.8 to 56.9) on this cell.
- DiM natives (secondary): DiM-A 3.6, DiM-C 1.6, Fast-DiM 9.1, Greedy-DiM-S 4.4%: passable, A1 not falsified; Greedy-DiM 9.5%:
  passable but borderline (margin met in 3 of 5 seeds, 2 of 5 above 15%). The morph-trained recipe reaches 10.2 to 29.7% on these
  cells.
- **Fast-DiM-ODE native 11.8% (per seed 0.4, 5.9, 18.6, 17.6, 16.2). By the registered rule A1 is falsified: 3 of 5 seeds are above
  15%, by 1.2 to 3.6 points, and these three seeds were each trained once, on WCSS. The cell is not passable because one
  label-permuted network (seed 403, which did not learn its training task: true-label training AUC 0.47) reaches 18.2%; every other
  reference is at 32.4% or above. The morph-trained recipe reaches 13.7% (1 of 5 seeds above 15%).** Label-permuted seed 403 is the
  lowest reference in 15 of the 17 native ViT-L/14 cells (signed AUC above 0.5 in all 17).
- Bounded head on ViT-L/14: the DiM morphs sit 0.04 to 0.38 logits above the genuine floor (span about 8.1), and all are missed at 0.5.
  "Passable" and "falsified" on these cells are both read inside the floor band.
- Seed 403 (WCSS) has the highest EER in 5 of the 6 DiM natives (for example Fast-DiM 24.6%, DiM-A 11.8%); seed 402 (Athena) is the
  highest in most FRLL cells. The WCSS repeats of seeds 401 and 402 match Athena (largest |EER difference| 1.3 and 6.3 points), so the
  platform mix does not explain the weakness of seeds 403 to 405.
- Resolution-history matching: five DiM history-matched cells are reversed (AUC below 0.5 in every seed); DiM-C is split. It does not
  remove the cue on MorDIFF (4.0%), FRLL AMSL (15.6%, per seed 1.5 to 36.3) or Webmorph (11.1%). FRLL FaceMorpher native 20.6% (per seed
  5.0 to 35.8) and OpenCV 34.3% (the morph-trained recipe reaches 0.1 and
  0.5%); StyleGAN and both MIPGAN cells reversed; corrected MAD22 FaceMorpher 0.0% native, 37.7% history-matched (per seed 2.0 to 55.4; no twin on MAD22). The reader's
  tables print seed means also for reversed and split cells (for example DiM-A history-matched 83.7%); for those, only the per-seed
  values in `posthoc_m3l.md` (D) apply.
- 0.5 rule: 0.0% of genuine photos flagged; 63.1% of MorDIFF morphs missed (per seed 8.4 to 100), 100% of DiM-A morphs. FRLL-5%: 0.0%
  of MorDIFF morphs missed while 21.0% of MorDIFF's own genuine photos are flagged.
- **Cross-platform repeat** (the ten WCSS H100 results; Amendment 1c): for the seven tasks that also ran on Athena (238 network-cell
  pairs), median |EER difference| 0.1 and largest 6.3 points (morph-free seed 402), largest |AUC difference| 0.072. The all-WCSS arm gives the same
  registered verdicts (Fast-DiM-ODE 11.5%, A1 falsified; the other six passable). `xplat_m3l_wcss_vs_athena.md`,
  `ad4_reading_m3l_wcssrepeat.md`.

## Post hoc follow-ups (Amendment 4; on the rented ViT-B/16 networks, before the cluster rerun)

These follow-ups describe the rented networks, now a cross-platform repeat. The registered WCSS networks of the same seeds differ by
up to 21.1 points, so the follow-ups do not describe the registered arm.


- Face-only softness: a statistic of high-frequency power in a fixed face box separates morphs from genuine photos at AUC 1.000 in all
  8 native cells the rented networks pass at AUC ≥ 0.99; the networks' scores follow it with Spearman ≥ 0.7 in 4 of the 8 (H-new-1:
  mixed). Across the 7 diffusion history-matched cells the networks' AUC follows how much softer the morphs are than the
  history-matched photos (Spearman 0.86; H-new-2: consistent with overshoot). `fu_sharpness_m3.md`.
- Border-blanked re-score (H-new-3), ladder morphs (H-new-5), held-out generator renders (H-new-4): scored on the DGX (Amendment 4b).
  The DGX re-score of the unblanked images misses the registered agreement gate for 3 of 5 morph-free networks (Kendall tau 0.987 to
  0.989 against 0.99; |AUC difference| at most 0.0012; probably ties at the saturation floor, not rescued), so these rows are
  "incomplete (2 of 5)", seeds 402 and 403 only. Blanking everything outside the face: MorDIFF history-matched 2.9 and 13.2% EER,
  corrected MAD22 FaceMorpher 0.0 native; the cue is not removed on those cells in these two networks. Landmark ladder (its own
  frames): same-person blends are scored like two-person morphs (gap OpenCV 0.009, FaceMorpher -0.006; R4 vs R3 AUC 0.47 to 0.52).
  Held-out SMDD renders and FRLL genuine photos are indistinguishable: both at the trained floor (differences of -0.03 and -0.05
  logits inside a floor whose 5th to 95th percentile spans about 0.03; no interval). `fu_blank_m3.md`, `fu_pools_m3.md`. An H100
  re-score of these follow-ups on the registered WCSS networks was registered (Amendment 6) and is on hold (lead's ruling pending).

## Withdrawn

- WITHDRAWN (13 Nov; the 11 to 12 Nov status lines "ViT-B/16 recipe: read; flagged 'not reproduced on this stack'" and "ViT-L/14:
  incomplete (2 of 5)"): superseded by the registered cluster-stack readings above (Amendment 5). The rented ViT-B/16 numbers stay
  valid as a cross-platform repeat with their flag; the 23:59 ViT-L/14 interim is kept on T7 (`read/incomplete2_*`).

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
- Whether one stack is deterministic run to run (a repeat of one seed on the same stack was not run).
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
