# DINOv3 evaluated like CLIP: programme plan (BB2 owner, 13 Nov 2026, 19:10 CET; DRAFT for the lead and the author)

Author's instruction (13 Nov, relayed 19:00), verbatim: "Please plan extensive experiments for Dinov3, ok? So that we
evaluate it like we did with CLIP." Meaning (lead): every reviewed read the CLIP candidate has had since 12 Nov, repeated
on a properly trained DINOv3, on development data only, each registered before it runs with the same rules where they
make sense. Nothing new is submitted until the lead says so; already queued: E3 (6313860), E2 (6313858 smoke, 6313861),
BB2 C2P job (6313488). Draft registrations: `prereg_programme_draft.md` (this folder).

## 0. Status that binds this plan

- **CLIP candidate frozen by the author** (18:28: "Ok, freeze the candidate and let's test it"): arm Sb, CLIP ViT-B/16 +
  LoRA, seeds 403-407. The author has been asked whether to hold the sealed read and lift the freeze while better arms
  are tried. **Until he answers, no DINOv3 arm can enter the sealed read.** Section 7 proposes the selection rule that
  would apply if he lifts the freeze.
- **What BB2 part 1 showed** (reviewed, `result.md`): at CLIP's learning rates DINOv3 Sb did not fit its own splice
  training rows (training AUC S4 vs S3 0.58-0.59 against CLIP 0.85-0.88; relative LoRA update about 3.5x smaller);
  landmark_combined gain not repeated; face-only gain repeated at a low level; no storage reaction of the plain arm on
  FFHQ development photos. BB2 so far neither confirms nor refutes backbone independence.
- **Reads accepted until 15 Nov 2026 18:00 CET** (author ruling 17:15); paper due 16 Nov. WCSS queue waits 3-20 h; cap
  32 GPUs for our account. Measured cost: one DINOv3 ViT-L/16 fit 1.5-1.8 h on one H100 (BB2: B, Sb 1:29-1:31; A up
  to 1:49), batch 256 in one pass (69 GB peak).
- **Platform rule (lead):** every DINOv3 network is scored on the GPU model and software build it was trained on (WCSS
  H100, `~/dmenv` torch 2.11 / timm 1.0.30), inside its fit job or in a same-stack rescoring job with the precision
  probe (`src/BB2/precision_probe.py`) and the C2P.2 gate against its in-fit scores. CLIP-side packs and scripts that ran
  on A100 leases are re-staged for WCSS before use. `~/dmenv` is frozen: nothing is installed.

## 1. Base arms A, B, Sb on five fresh seeds (item 1)

- **E3 (queued, 6313860):** A, B, Sb x 403-407 at the rule-fixed LoRA learning rate 1.17e-5 (3.5 x CLIP's, from the
  training-fit diagnosis), head unchanged, splice-fit gate (Sb training AUC S4 vs S3 ≥ 0.80), seed mode frozen before
  any tar is opened. 15 fits, about 24 H100-h. This is wave 1: it decides whether DINOv3 deserves the rest.
- **Is one learning rate enough?** Only if E3's gate passes. If it fails on most seeds, a small registered sweep is
  justified, chosen **on training rows only**: LoRA learning rates {3.33e-5, 1e-4} (the next two half-decades above
  1.17e-5), arm Sb only, seed 403 only, 6,250 steps; the value used for the fresh seeds is the lowest one at which Sb's
  training AUC S4 vs S3 ≥ 0.80 and training-row own-rule accuracy ≥ 0.95 with finite loss; nothing else is looked at
  (no development read of the sweep fits is computed before the choice is committed). Then A, B, Sb at 403-407 at that
  value (15 fits). Cost: 2 + 15 fits ≈ 27 H100-h. If no value passes: "DINOv3 ViT-L/16 does not fit the splice task
  with LoRA r2 in this recipe" (a result), and the programme stops at wave 2's descriptive reads.
- **Capacity (pretraining mixed with size).** DINOv3 ViT-L/16 (303 M) against CLIP ViT-B/16 (86 M). On disk: DINOv3
  ViT-L/16 (timm and HF), DINOv2 ViT-L/14 and ViT-S/14, CLIP ViT-L/14 (timm `vit_large_patch14_clip_224.openai`, already
  an entry in `archs_a12.py` as `a12_clip_vitl14_madation`, MADation's own ViT-L recipe). Not on disk: DINOv3 ViT-B/16
  (gated HF repository; access existed for A49; a download needs the author's approval; weights would go into the HF
  cache, not into `~/dmenv`).
  - **Cleaner control now: CLIP ViT-L/14** (A, B, Sb x 403-407, CLIP learning rates unchanged as for ViT-B/16; zero
    code change; about 15 x 1.6 h ≈ 24 H100-h). It holds the pretraining fixed and changes size: if CLIP-L/14 repeats
    CLIP-B/16's pattern, size alone does not explain DINOv3's result. Patch 14 at 224 px gives a 16 x 16 grid (no
    resampling: the CLIP weights are built at 224).
  - **DINOv3 ViT-B/16** holds the size fixed and changes pretraining: the better control for "is it the backbone",
    but it needs a download (author) and an `archs_a12.py` entry (same class, new name). After the deadline unless
    approved tonight.

## 2. The existing-network battery (PR1) on DINOv3 (item 2)

- **Z reads from stored scores (zero GPU):** warp-only (R2w), same-person morphs (R3, R3m), same-person and seam-only
  splices (S3, S0), training-row fit, operating point (τ5 in-source, own rule), engine transfer (OpenCV trained,
  FaceMorpher held out), softness (TT-H4 style), the 27-statistic floors. All rows are in the FS1 pack that every BB2
  and E3 fit already scores in-fit (`scores_eval.npz`, `scores_train.npz`). Code: `src/PR1/pr1_read.py` adapted to
  BB2/BB2L tar names (a copy with the names and folders changed, as for bb2_read.py). Ready within an hour of E3's
  fetch.
- **GAN and diffusion development families with their one-photo render controls (PR1 GD0/GD1/GD2):** need scoring.
  Pack `/mnt/t7/smad_next/PR1/pr1_gd.tar` (3.9 GB; FFHQ StyleGAN / diffusion families, DG1 diffusion ladder, AG1 MIPGAN
  controls; scored for CLIP on the rented A100) is uploaded to WCSS and rescored for the DINOv3 networks with the
  unchanged `src/PN1/rescore.py` through `src/TT1/rescore_tf32.py` in one H100 job with the precision probe and the
  C2P.2 gate (same pattern as `bb2_c2p.sbatch`). 15 networks, about 1.5 H100-h. Reader: `src/PR1/gd_read.py` copy.
- **27-statistic floors:** existing cue files (cues27, `/mnt/t7/smad_next/PR1/cues`, `PN1/cues`), zero GPU.

## 3. Storage test with a working plain control, and storage evasion (item 3)

- **C2P on its own platform (as AB1 did):** for E3's networks a rescoring job on the MS1 FFHQ hold-out (the BB2 C2P job
  with `BB2_TASKS` = the 15 BB2L tasks and `BB2_C2P_RESULTS=results/BB2L`; reader `bb2_c2p_read.py` with BB2L names).
  About 0.5 H100-h. Contrast 2-prime with A's positive control; H-new-1 storage evasion; five-seed rules (C2P's own).
- **Caveat that may decide it:** the plain DINOv3 arm showed no storage reaction on FFHQ development photos at CLIP's
  learning rates (A's control would fail: "uninformative"). If E3's plain arm also shows none, the paper's storage
  claim cannot be tested on DINOv3, and the sentence is "on DINOv3 the plain recipe shows no storage reaction, so there
  is nothing for the protocol to remove" (descriptive). The BB2 C2P job (6313488, CLIP-rate networks) answers the same
  question for part 1 (prediction logged: control fails).

## 4. Unseen genuine sources (item 4)

- **TT1 pools:** the eight low-resolution sources (LFW, CFP, AgeDB, OULU-NPU, Replay-Attack, CASIA-FASD, MSU-MFSD, ...;
  about 21,000 aligned genuine photos), the border references R_cam_border and the geometry references, FFHQ (in the
  fit pack already). TT1 pack `/mnt/t7/smad_next/TT1/tt1_pack.tar` (8.1 GB; on WCSS `packs/TT1`, to be checked) rescored
  for the 15 E3 networks in one H100 job (same pattern, precision probe, gate). About 2 H100-h. Reader: `src/TT1/
  tt1_read_fs.py` copy (TT-H1 transfer, TT-H3 border, TT-H4 softness, F̄).
- **NIST MEDS (TT-M1):** allowed on all machines by the author; pack built by `src/TT1/meds/build_meds_pack.py`, scored
  by the same rescoring pattern; reader `tt1_read_meds.py` copy. **No MEDS image or identifier in any artifact** (only
  aggregate flag shares, the stratum sizes and pack sha256). About 0.3 H100-h.

## 5. Component ablations and the new arms (item 5), on DINOv3 at the E3 learning rate

Each arm = 5 seeds x 1.6 h ≈ 8 H100-h, trained and scored in one fit job on the AB1 evaluation pack (which already holds
the C2P hold-out, landmark_combined, S0/S3/S4 and the warp-only rows), so C2P and the AB1 reads come out of the fit
itself with no rescoring. Code: AB1's `run.sh` with the BB2 overlay and BB2_LR (a copy, as run_lr.sh); manifests are
AB1's, unchanged (sha256 in AB1's pins). Compared within seed with E3's DINOv3 Sb (seeds 403-407, the E3 block; AB1
used 408-412 on CLIP).
- **AB1 leave-one-out arms:** SbZ (no warp-only), SbH (no native halves), SbS (no stored-small copies), AS (plain + stored
  copies), Sp (no matched splice negatives); B2 arms SbR, SbH61, SbSp, SbnS0, SbnS3. Ten arms = 80 H100-h. Value order:
  Sp (the matched-negative claim), SbS (storage component), SbnS3, then the rest.
- **SE1 same-person blend arm (SE):** manifest from `src/SE1/mk_se.py` (existing images); 8 H100-h.
- **Border-crossed arm Sbx:** AB1's overlay `ab1x_overlay.tar` (e5886e72…) plus its border evaluation rows; 8 H100-h.
- **Second morphing engine arm (author 18:50, AB1 owner):** its manifest when the AB1 owner registers it on CLIP; the
  DINOv3 copy uses the same manifest; 8 H100-h.
- **GX1: GAN morphs with one-person renders as genuine (author 18:50, AG1 owner):** existing AG1 images only; the DINOv3
  copy uses the same manifest once registered; 8 H100-h; its GAN render reads need the GD pack rescoring (section 2).
- **CLIP ViT-L/14 size control** (section 1): 24 H100-h.

## 6. Blend-difference attribution (BD1) on DINOv3 Sb (item 6)

`src/BD1/bd1b_feat.py` and `bd1b_read.py`, `bd1c_read.py` on E3's Sb networks (the same 191 test hosts); features need
one H100 job (about 0.5 H100-h) on WCSS with the probe; reads on the DGX CPU. Meaning: whether DINOv3 Sb's response
grows with the blend difference inside the face the way CLIP Sb's does (the "reads blending, not identity" question).

## 7. Selection rule if the author lifts the freeze (proposal; must be committed before any wave-2 or wave-3 read)

A DINOv3 arm replaces the frozen CLIP Sb for the sealed read only if, on five fresh seeds, development data only, all
of the following hold (each with its registered rule; margins inclusive):
1. Splice-fit gate met on ≥ 4 of 5 seeds, and E3 outcome "did not transfer because under-fitted" (contrast 1 repeated).
2. FFHQ landmark_combined AUC: median over seeds ≥ CLIP Sb's median + 0.03 (CLIP Sb 403-407: 0.814, 0.874, 0.845, 0.884,
   0.885; median 0.874, so ≥ 0.904), and exact one-sided Mann-Whitney 5 against 5 p ≤ 0.05 (U ≤ 4).
3. Storage: contrast 2-prime "passes" with A's control met, and H-new-1 "falsified" (the frozen candidate's own bar).
4. Unseen sources: TT1 F̄ (mean own-rule flag share over the eight sources) median ≤ CLIP Sb's median + 0.01, and MEDS
   "transfers" on ≥ 4 of 5 seeds.
5. Same-person splices: development S3 flag share median ≤ CLIP Sb's median + 0.05; and GAN one-photo-render flags
   median ≤ CLIP Sb's median.
6. No guard worse than CLIP Sb by more than the AB1 guard margins (development R4 vs R2w AUC within 0.02; own-rule miss on
   development S4 within 5 points).
If any item is unread by 15 Nov 18:00, the CLIP Sb freeze stands. One arm at most (the DINOv3 Sb of E3 or of the sweep);
no arm is chosen among several by its development numbers beyond this rule.

## 8. Waves (value per GPU-hour, real constraints)

| Wave | What | Fits / jobs | H100-h | Inputs ready | Can be read by 15 Nov 18:00? |
|---|---|---|---|---|---|
| 1 (queued) | E3 (15 fits, gate), E2 (ablation + probe), BB2 C2P job | 15 fits + 3 jobs | ≈ 27 | yes, queued | yes, if E3 starts by about 14 Nov 18:00 (1.8 h per fit, 15 GPUs in parallel); likely |
| 2 (zero / low GPU; registered now, submitted the hour E3's tars exist) | PR1 Z reads (0 GPU); C2P for E3 (0.5); GD rescoring (1.5); TT1 + MEDS rescoring (2.3); BD1 features (0.5) | 4 jobs | ≈ 5 | packs exist; GD and TT1 packs to stage on WCSS now | yes if E3 ends by about 15 Nov 06:00 and each job waits ≤ 6 h; tight |
| 2b (only if E3's gate fails) | LR sweep (2 fits, training rows only), then A, B, Sb at the chosen value | 2 + 15 fits | ≈ 27 | yes | no (two queue waits plus fits); after the deadline |
| 3a (if E3's gate passes) | Sp, SbS, SE, CLIP ViT-L/14 size control | 5 + 5 + 5 + 15 fits | ≈ 48 | manifests exist (AB1, SE1); code is a copy of run_lr.sh with AB1's pack | only if submitted by about 14 Nov 12:00 and started within 6 h; partly |
| 3b | the other AB1 arms (8), Sbx, second engine, GX1 | 55 fits | ≈ 88 | second engine and GX1 manifests not yet registered on CLIP | no: after the deadline |
| 4 | DINOv3 ViT-B/16 (A, B, Sb x 5; download), repeat blocks | 15 fits | ≈ 15 | needs the author's download approval | no: after the deadline |

With the 32-GPU cap, waves 1-3a fit inside the cap at once (15 + 30 at most when E3 ends, staggered). The binding
constraint is queue wait, not GPUs: each new submission waits 3-20 h. Wave 2 is registered and staged tonight so that it
starts the moment E3's tars exist; wave 3a can be submitted tonight only if the lead and the author accept it before
E3's gate is known (then its DINOv3 learning rate is E3's 1.17e-5, fixed now; if the gate fails, wave 3a is read as
"under-fitted" too).

## 9. What each outcome means for the paper

- E3 gate met, contrast 1 repeated: "the spliced-positive gain is not CLIP-specific: with the splice rows fitted, it
  repeats on DINOv3 ViT-L/16 (development data)". Waves 2-3 then tell whether the rest of the CLIP audit transfers.
- E3 gate met, contrast 1 not repeated (Sb − B < +0.02): "backbone-dependent for DINOv3 ViT-L/16 with a CLS read-out";
  the CLIP ViT-L/14 row then says whether size or pretraining is responsible.
- E3 gate failed: "DINOv3 under this recipe does not learn the splice task"; the paper keeps CLIP and reports BB2 as
  an attempted transfer; wave 2b after the deadline.
- Storage: if DINOv3's plain arm never reacts to storage, the storage claim is CLIP-specific in the sense that the
  shortcut itself is backbone-dependent (descriptive).

## 10. Decisions for the author

1. Hold the sealed read and lift the freeze while DINOv3 is tried, or keep the CLIP Sb freeze (then every DINOv3 result
   is a robustness row only).
2. If lifted: adopt the selection rule of section 7 (or amend it) before any wave-2/3 read.
3. Approve wave 2 now (≈ 5 H100-h; staging the GD and TT1 packs on WCSS tonight).
4. Approve wave 3a now, before E3's gate is known (≈ 48 H100-h), or wait for the gate (then 3a is after the deadline).
5. DINOv3 ViT-B/16 download (gated HF; capacity control) yes or no.
6. Whether the LR sweep (2b) may run if E3's gate fails.
