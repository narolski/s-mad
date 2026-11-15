# DINOv3 evaluated like CLIP: programme plan (BB2 owner, 13 Nov 2026; version 2 after the pre-run check; DRAFT for the lead and the author)

Times (note added after the lead's 18:46 correction): the author-ruling times quoted below from the lead's messages were
about 45 minutes ahead of the machine clock. By the machine clock: cut-off ruling ("17:15") about 17:11; freeze
("18:28") about 18:27; "read now" ("19:25") about 18:36; the lead's "19:00", "19:20" and "18:50" between 18:32 and 18:46.
The rulings themselves are unchanged. Pre-run check: `experiments/reviews/PRERUN_BB2_PLAN_20261113.md` (GO WITH FIXES; F1-F9 applied below).

Author's instruction (13 Nov, relayed 19:00), verbatim: "Please plan extensive experiments for Dinov3, ok? So that we
evaluate it like we did with CLIP." Meaning (lead): every reviewed read the CLIP candidate has had since 12 Nov, repeated
on a properly trained DINOv3, on development data only, each registered before it runs with the same rules where they
make sense. Nothing new is submitted until the lead says so; already queued: E3 (6313860), E2 (6313858 smoke, 6313861),
BB2 C2P job (6313488). Draft registrations: `prereg_programme_draft.md` (this folder).

## 0. Status that binds this plan

- **CLIP candidate frozen by the author** (18:28: "Ok, freeze the candidate and let's test it"): arm Sb, CLIP ViT-B/16 +
  LoRA, seeds 403-407. **Author, 19:25: "Go with A READ NOW, improve later for MAD22, we need to know where we stand on
  this eval set."** The frozen candidate is read on corrected MAD22 now; FRLL-Morphs, FEI, MorDIFF, the DiM families, H1
  and the benign variants stay sealed for the improved method. The arms ordered this evening (second engine, GAN with
  render-matched negatives, the DINOv3 programme, input resolution and resize study RZ1, look-alike search) are
  **development of the next method version**. So this plan's target is: whether a DINOv3 arm should be the next method
  version, to be read once on the remaining sealed sets. MAD22 numbers of the frozen CLIP candidate are "seen during
  development" for the next version and are never a selection input (section 7).
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
- **Is one learning rate enough?** Only if E3's gate passes. If it fails on more than one seed of the read set, a small
  registered sweep is justified, chosen **on training rows only**: LoRA learning rates {3.33e-5, 1e-4} (about 2.8x and
  8.5x of 1.17e-5), arm Sb only, seed 403 only, 6,250 steps; the value used for the fresh seeds is the lowest one at which Sb's
  training AUC S4 vs S3 ≥ 0.80 and training-row own-rule accuracy ≥ 0.95 with finite loss; nothing else is looked at
  (no development read of the sweep fits is computed before the choice is committed). Then A, B, Sb at 403-407 at that
  value (15 fits; the sweep fit of Sb 403 at the chosen value is not reused). Blindness is enforced, not only by
  discipline: the sweep reader extracts only `scores_train.npz` from each sweep tar, logs the tar sha256, and the
  choice is committed before any `scores_eval` member is read. Cost: 2 + 15 fits ≈ 27 H100-h. If no value passes: "DINOv3 ViT-L/16 does not fit the splice task
  with LoRA r2 in this recipe" (a result), and the programme stops at wave 2's descriptive reads.
- **Capacity (pretraining mixed with size).** DINOv3 ViT-L/16 (303 M) against CLIP ViT-B/16 (86 M). On disk: DINOv3
  ViT-L/16 (timm and HF), DINOv2 ViT-L/14 and ViT-S/14, CLIP ViT-L/14 (timm `vit_large_patch14_clip_224.openai`, already
  an entry in `archs_a12.py` as `a12_clip_vitl14_madation`, MADation's own ViT-L recipe). Not on disk: DINOv3 ViT-B/16
  (gated HF repository; access existed for A49; a download needs the author's approval; weights would go into the HF
  cache, not into `~/dmenv`).
  - **Control available now: CLIP ViT-L/14** (A, B, Sb x 403-407). It holds the pretraining fixed and changes size:
    if CLIP-L/14 repeats CLIP-B/16's pattern, size alone does not explain DINOv3's result. It is informative mainly if
    E3 reads "backbone-dependent", so it is **conditional on that outcome**. Not zero cost: the arch entry exists, but
    a run script (run_lr.sh hardcodes the DINOv3 arch) and the CLIP-L weights in an overlay are needed; MADation's
    ViT-L/14 ran at batch 32 x 8 accumulation (src/AD4/run.sh), 257 tokens per image against DINOv3's 201, so batch
    256 in one pass probably does not fit in 80 GB (memory rule of section 4 applies, from its own smoke); the fit
    time is unmeasured (estimate 1.6-2.5 h). At CLIP-B's learning rate it may under-fit the same way, so it carries
    E3's splice-fit gate and a printed relative LoRA update. Patch 14 against 16 remains a confound.
  - **DINOv3 ViT-B/16** holds the size fixed and changes pretraining: the better control for "is it the backbone".
    Weights: the official Meta release is on disk since 18:50 (author's login; `/mnt/t7/smad_next/weights/
    dinov3_vitb16_official/`, Hugging Face transformers format: separate q/k/v projections, q and v biases present but
    all zero, 4 register tokens, layer-scale, RoPE theta 100). **How it loads (rule, fixed before any fit):** the same
    model code path as ViT-L/16 (timm `Eva`, `vit_base_patch16_dinov3`, CLS after the final norm, fused `attn.qkv` so
    the same LoRAQKV q/v wiring applies, qkv bias off because the official q/v biases are zero), through a small
    key-for-key conversion of the official state dict into timm's names (q, k, v concatenated into qkv; o_proj -> proj;
    up/down -> fc1/fc2; layer_scale -> gamma; embeddings and register tokens; no value changed). Loading the official
    weights through transformers' own `DINOv3ViTModel` instead would change the attention module (separate q/v
    projections), so the LoRA placement would not be the recipe's. **Verification:** (i) the converter is first run on
    the official ViT-L/16 release already on disk (`facebook/dinov3-vitl16-pretrain-lvd1689m`, A49) and must reproduce
    the timm ViT-L/16 file that E3 uses tensor for tensor (if not, the conversion is wrong and nothing is trained); (ii)
    the converted ViT-B/16 in timm, and the official ViT-B/16 in transformers 5.12 (DGX), give the CLS feature of the 8
    featcheck images with max |difference| ≤ 1e-3 after truncating timm's RoPE periods to bfloat16 as the timm model
    card describes (the official model keeps them as a bfloat16 buffer); (iii) the WCSS featcheck against a DGX CPU
    reference, as for ViT-L/16. **Would the timm conversion be more consistent?** Its provenance equals the ViT-L/16
    file's (timm's own conversion), which is the most consistent; check (i) makes our conversion of the official file
    equivalent to it by construction, so the official weights are used and the timm file is not needed. Needs an
    `archs_a12.py` entry (same class, new name, dim 768) and its own registration; later wave.

## 2. The existing-network battery (PR1) on DINOv3 (item 2)

- **Z reads from stored scores (zero GPU):** warp-only (R2w), same-person morphs (R3, R3m), same-person and seam-only
  splices (S3, S0), training-row fit, operating point (τ5 in-source, own rule), engine transfer (OpenCV trained,
  FaceMorpher held out), softness (TT-H4 style), the 27-statistic floors. All rows are in the FS1 pack that every BB2
  and E3 fit already scores in-fit (`scores_eval.npz`, `scores_train.npz`). Code: `src/PR1/pr1_read.py` adapted to
  BB2/BB2L tar names (a copy with the names and folders changed, as for bb2_read.py). Ready within an hour of E3's
  fetch. Exceptions: Z2b and Z5 also need the TT1 and C2P rescoring outputs (wave 2's merged job).
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
- **NIST MEDS (TT-M1):** allowed on all machines by the author; it ran only through the rented-machine driver
  (`src/TT1/meds/remote_tt1_m.sh`), so WCSS needs a new sbatch and a pre-run check; pack built by `src/TT1/meds/build_meds_pack.py`, scored
  by the same rescoring pattern; reader `tt1_read_meds.py` copy. **No MEDS image or identifier in any artifact** (only
  aggregate flag shares, the stratum sizes and pack sha256). About 0.3 H100-h.

## 5. Component ablations and the new arms (item 5), on DINOv3 at the E3 learning rate

Each arm = 5 seeds x 1.6 h ≈ 8 H100-h, trained and scored in one fit job on the AB1 evaluation pack (which already holds
the C2P hold-out, landmark_combined, S0/S3/S4 and the warp-only rows), so C2P and the AB1 reads come out of the fit
itself with no rescoring. Code: AB1's `run.sh` with the BB2 overlay and BB2_LR (a copy, as run_lr.sh); manifests are
AB1's, unchanged (sha256 in AB1's pins). Compared within seed with E3's DINOv3 Sb (seeds 403-407, the E3 block; AB1
used 408-412 on CLIP).
- **Scoring paths (review F7):** DINOv3 Sp and SbS get C2P from in-fit AB1-pack scores, E3's A and Sb from the gated
  rescoring job; AB1 forbids mixing scoring paths in one statistic, so within-seed C2P comparisons with E3 networks
  are printed with that label, and SbS (whose only purpose is the storage component) waits for W2c's control result:
  if E3's plain arm shows no storage reaction, SbS is not run. Sp does not depend on storage.
- **AB1 leave-one-out arms:** SbZ (no warp-only), SbH (no native halves), SbS (no stored-small copies), AS (plain + stored
  copies), Sp (no matched splice negatives); B2 arms SbR, SbH61, SbSp, SbnS0, SbnS3. Ten arms = 80 H100-h. Value order:
  Sp (the matched-negative claim), SbS (storage component), SbnS3, then the rest.
- **SE1 same-person blend arm (SE):** manifest from `src/SE1/mk_se.py` (existing images); 8 H100-h.
- **Border-crossed arm Sbx:** AB1's overlay `ab1x_overlay.tar` (e5886e72…) plus its border evaluation rows; 8 H100-h.
- **Second morphing engine arm (author 18:50, AB1 owner):** its manifest when the AB1 owner registers it on CLIP; the
  DINOv3 copy uses the same manifest; 8 H100-h.
- **GX1: GAN morphs with one-person renders as genuine (author 18:50, AG1 owner): blocked.** Only 36 usable two-person
  MIPGAN-I morphs exist (NOTEBOOK 19:20); the lead will not run an arm that small and asked for the cost of building
  300-500. The DINOv3 copy follows the CLIP arm's manifest once it exists.
- **CLIP ViT-L/14 size control** (section 1): about 24 H100-h (unmeasured); conditional (section 1).

## 5b. Resolution and resize method (RZ1)

RZ1 (other owner) runs on CLIP ViT-B/16 only (224 px resize-kernel arms; 512 px pending the lead). This plan proposes
nothing on resolution or resampling for DINOv3: a ViT-L/16 fit at 512 px is about 11 H100-h (RZ1's measurement scaled).
RZ1's loader patch (per-sample resize kernel, an overlay of the loader) can be dropped into run_lr.sh for one DINOv3 arm
later, only if E3's gate passes and the lead asks; not planned here.

## 6. Blend-difference attribution (BD1) on DINOv3 Sb (item 6)

`bd1b_read.py`, `bd1c_read.py` (copies with E3's names) on E3's Sb networks (the same 191 test hosts): **zero GPU**. The
blend-difference features are image statistics already computed (`/mnt/t7/smad_next/BD1/d_feats.csv`), and the
network scores are the S3/S4 rows of each E3 fit's `scores_eval.npz`. Read within an hour of E3's fetch. Meaning: whether DINOv3 Sb's response
grows with the blend difference inside the face the way CLIP Sb's does (the "reads blending, not identity" question).

## 7. Selection rule for the next method version (proposal; must be committed before E3 is read)

Target: whether a DINOv3 arm becomes the next method version, read once on the remaining sealed sets (FRLL-Morphs, FEI,
MorDIFF, DiM, H1). The rule must be committed **before E3's read** (that is, before E3's seed mode is frozen), because
items 1-2 are E3 reads. Other candidates for the next version are being built tonight (second engine SbFM, GX1, RZ1);
choosing among several of them by development numbers is uncontrolled multiplicity, so **one programme-level rule over
all candidates must be fixed by the lead or the author** before any of their reads; the items below are the DINOv3 part
of it. Never an input: any MAD22 number. Five read seeds (the FS1 seeds 403-407; not fresh for DINOv3, since BB2 part 1
used them), development data only, margins inclusive:
1. Splice-fit gate met on ≥ 4 of 5 seeds and E3 outcome "did not transfer because under-fitted" (contrast 1 repeated).
2. FFHQ landmark_combined AUC: median ≥ CLIP Sb's median + 0.03 (CLIP Sb 403-407: 0.814, 0.874, 0.845, 0.884, 0.885;
   median 0.874, so ≥ 0.904), and exact one-sided Mann-Whitney 5 against 5 p ≤ 0.05 (U ≤ 4; p = 12/252 = 0.048).
3. Storage, as an absolute non-inferiority bar (CLIP Sb never passed contrast 2-prime with a met control: 403-407
   "uninformative", 408-412 "inconclusive"; and DINOv3's plain arm may show no reaction at all): DINOv3 Sb's own-rule
   flag rise Δf at fm61 and at amsl112 on the MS1 FFHQ hold-out, median over seeds, and the median of its upper 95%
   bounds, each no worse than CLIP Sb's AB1 H100 values (408-412) plus 0.02; and H-new-1 "falsified".
4. Unseen sources: TT1 F̄ (mean own-rule flag share over the seven TT1 families; LFW and CALFW merged) median ≤ CLIP Sb's
   median + 0.02 (CLIP Sb's seed SD is 0.012, so a +0.01 margin would be inside seed noise), and MEDS "transfers" on
   ≥ 4 of 5 seeds.
5. Same-person splices: development S3 flag share median ≤ CLIP Sb's median + 0.05; GAN one-photo-render flags median ≤
   CLIP Sb's median.
6. Guards: development R4 vs R2w AUC within 0.02 of CLIP Sb's median; own-rule miss on development S4 within 5 points.
If any item is unread by 15 Nov 18:00, no DINOv3 arm is chosen. One DINOv3 arm at most (E3's Sb, or the sweep's).

## 8. Waves (value per GPU-hour, real constraints)

| Wave | What | Fits / jobs | H100-h | Inputs ready | Can be read by 15 Nov 18:00? |
|---|---|---|---|---|---|
| 1 (queued) | E3 (15 fits, gate), E2 (ablation + probe), BB2 C2P job | 15 fits + 3 jobs | ≈ 27 | yes, queued | likely, if E3 starts by about 14 Nov 18:00 (1.8 h per fit; how many of the 15 run at once depends on the shared cap: other owners' arrays, AB1 B2 25 fits and MS1 part 4 20 fits, share it) |
| 2 | PR1 Z reads and BD1 (0 GPU, within an hour of E3's fetch); one merged H100 rescoring job for C2P, GD, TT1 and MEDS on E3's networks (about 4.5 h, one queue wait), pre-submitted with `--dependency=afterany:6313860` (it carries its whole workload; the E3 tars are its only later inputs) on the lead's go | 1 job | ≈ 4.5 | GD pack to stage on WCSS; TT1 pack already on WCSS (`packs/TT1`); both need the BB2 overlay over their archs_a12.py; MEDS has no WCSS job yet (a new sbatch and pre-run check) | only if E3 ends by about 15 Nov 06:00 and the merged job waits ≤ 6 h; tight |
| 2b (only if E3's gate fails) | LR sweep (2 fits, training rows only), then A, B, Sb at the chosen value | 2 + 15 fits | ≈ 27 | yes | no (two queue waits plus fits); after the deadline |
| 3a | Sp and SE on DINOv3 (SbS only if W2c shows a plain-arm storage reaction); CLIP ViT-L/14 only if E3 reads "backbone-dependent" | 10 (+5) (+15) fits | ≈ 16-48 | manifests exist (AB1, SE1); code is a copy of run_lr.sh with AB1's pack | unlikely by 15 Nov 18:00 (queue wait plus the shared cap) |
| 3b | the other AB1 arms (8), Sbx, second engine, GX1 | 55 fits | ≈ 88 | second engine and GX1 manifests not yet registered on CLIP | no: after the deadline |
| 4 | DINOv3 ViT-B/16 (A, B, Sb x 5; download), repeat blocks | 15 fits | ≈ 15 | needs the author's download approval | no: after the deadline |

The 32-GPU cap is shared with the other owners' arrays (AB1 B2, MS1 part 4, SE1, ...); waves 1 and 3a do not fit in it
at once, and the lead checks the queue before any submission. Queue wait (3-20 h per submission) binds as much as GPUs. Wave 2 is registered and staged tonight so that it
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

## 10. Decisions for the author (and the lead)

1. One programme-level selection rule for the next method version across DINOv3, SbFM, GX1 and RZ1: who fixes it, and
   before which read (it must precede E3's read for the DINOv3 part; section 7 is the DINOv3 proposal).
2. Approve wave 2 now: the merged rescoring job pre-submitted with a dependency on E3 (≈ 4.5 H100-h), staging the GD
   pack and a MEDS sbatch on WCSS tonight (each with a pre-run check).
3. Wave 3a: run Sp and SE on DINOv3 before E3's gate is known (≈ 16 H100-h), or wait for the gate (then after the
   deadline).
4. CLIP ViT-L/14 size control: only if E3 reads "backbone-dependent" (recommended), or now.
5. DINOv3 ViT-B/16 download (gated HF; capacity control) yes or no.
6. Whether the learning-rate sweep (2b) may run if E3's gate fails.
