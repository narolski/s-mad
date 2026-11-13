# Input resolution and resize method (RZ1): registration

Written 13 Nov 2026 evening (machine clock, from about 18:40 CET) by the RZ1 owner (Claude agent for the lead). It was
written before any RZ1 network exists and before any score of any RZ1 network has been read. Development data only. No row of FRLL, MAD22,
MorDIFF, DiM, H1, FEI, CASIA-WebFace or any sealed set is in any RZ1 pack. `manifests/valx.csv`, FST and A12SP are
never opened. `prep_eval.py` and `prep_gtest.py` are not touched. `~/dmenv` is used as it is.

## 0. Authority, status and what was known

- **Author's ruling, verbatim:** "For native resolution crops, yes, plan experiments on that with input size 512, and see
  if any particular resize method (or a mix of resizes in training) has an impact on shortcut learning alleviation".
  - NOTEBOOK entry headed "19:20". Dated note: it was given at about 18:32-18:46 by the machine clock. The lead's
    times after 17:00 were about 45 minutes ahead (NOTEBOOK "18:46 machine clock: CORRECTION OF TIMES").
  - For RZ1 only, this lifts two restrictions: the input may be 512 px, and code that varies the resize method from a
    stored frame to the network input may be written.
  - Nothing else changes. The stored images are read as they are: the approved alignment, the unchanged morphers, the
    existing shrink-and-enlarge storage copies and the JPEG branch.
- **Status of the arms.** The author's ruling of about 18:36 by the machine clock (the lead's message said 19:25):
  "Go with A READ NOW, improve later for MAD22".
  - The frozen CLIP candidate (Sb, seeds 403-407) is read on MAD22. The freeze is not lifted.
  - **No RZ1 arm can enter that read.** RZ1 arms are development rows for a possible next method version (section 8).
  - The freeze ruling was at about 18:27 by the machine clock.
- **Known at writing** (reviewed results, disclosed):
  - AB1's per-seed numbers for A and Sb at 408-412 on WCSS H100 (`AB1/result.md`): landmark_combined, the C2P
    quantities, S0, S3 and camera flags.
  - TT1's verdicts for seeds 401-407: Sb fails on CFP-FF and AgeDB on two seeds; transfers on 4 of 5 fresh seeds.
  - The border follow-up: Sb flags 2.9-16.3% of border-blanked camera photos.
  - The best single statistic 0.886 (noise_std_face at full resolution) and the 27-statistic baseline 0.814.
  - No RZ1 number of any kind existed.
  - The rules below were fixed with AB1's A and Sb numbers in view. That is why every RZ1 comparison is paired within
    seed against RZ1's own refits A0 and Sb0, and not against AB1's networks.

## 1. Questions, and why

The stored frame is 512 x 512 with the eyes at (190, 210) and (322, 210): 132 px apart (`prep_eval.py` docstring). The
network sees it resized to 224, where the eyes are 57.75 px apart. The storage-test copies were stored at 61.2 px (fm61,
trained size) and 112.7 px (amsl112, untrained size) between the eyes and enlarged back by the aligner's warp. In the
512 frame that is the content of a 237-px and a 437-px frame. At 224 an ideal resize would therefore keep almost
nothing that fm61 removed. Yet plain training raises its flag rate on stored genuine photos by +27 to +39 points (AB1).
The working assumption tested here: the reaction comes from how the kernels treat content near and above the 224 limit
(the current loader is PIL BILINEAR, a triangle filter). Resize mixing tests that directly. At 512 the same storage
removes everything above 46% of the frame's band, so a 512 network should both see more evidence and react more.

1. (Wave 2b) Does a 512-px input raise detection of landmark morphs from an unseen tool? What does it do to the
   storage reaction, the unseen-source false alarms and the border reaction?
2. (Wave 1) Does the fixed resize kernel matter for the shortcuts? Answered mainly by the test-time cross table under
   nine kernels on every network, and by one training arm with the extreme kernel (nearest, no antialiasing).
3. (Wave 1; the author's main question) Does a per-image mix of resize kernels in training, with or without a random
   intermediate size, reduce the storage reaction and the unseen-source false alarms? Tested for plain training and
   for the candidate recipe, without losing detection. Does it replace or add to the protocol negatives?
4. (Wave 2a) Is a native-resolution crop (224 window cut by integer slicing) better than the whole frame at the same
   token count (196 patches)?

## 2. Arms (CLIP ViT-B/16 MADation + LoRA, the FS1 recipe and flags unchanged; WCSS H100; seeds 408-412)

| Arm | Wave | Training rows | Input transform in training (rz1_kernels.py) | Res / batch | Primary test transform | Cross table |
|---|---|---|---|---|---|---|
| A0 plain, current kernel | 1 | train_A.csv af070a60… | fixed:pil_bilinear (= the current loader, bit for bit) | 224 / 256 | same | 9 + 4 held-out |
| Sb0 candidate recipe, current kernel | 1 | train_Sb.csv 2cf3fda3… | fixed:pil_bilinear | 224 / 256 | same | 9 + 4 held-out |
| AN plain, nearest kernel | 1 | train_A.csv | fixed:pil_nearest (no antialiasing) | 224 / 256 | fixed:pil_nearest | 9 + 4 held-out |
| AM plain, kernel mix | 1 | train_A.csv | mix | 224 / 256 | fixed:pil_bilinear | 9 + 4 held-out |
| SbM candidate, kernel mix | 1 | train_Sb.csv | mix | 224 / 256 | fixed:pil_bilinear | 9 + 4 held-out |
| AMR plain, kernel mix + intermediate size | 1 | train_A.csv | mixR | 224 / 256 | fixed:pil_bilinear | 9 + 4 held-out |
| SbMR candidate, kernel mix + intermediate size | 1 | train_Sb.csv | mixR | 224 / 256 | fixed:pil_bilinear | 9 + 4 held-out |
| Ac plain, native centre crop | 2a | train_A.csv | crop:144:160 (x 144-367, y 160-383) | 224 / 256 | same crop | none |
| Sbc candidate, native centre crop | 2a | train_Sb.csv | crop:144:160 | 224 / 256 | same crop | none |
| A512 plain, 512 input | 2b | train_A.csv | none (the frame itself) | 512 / 64 x 4 | same | none |
| Sb512 candidate, 512 input | 2b | train_Sb.csv | none | 512 / 64 x 4 | same | none |
| SbMR512 candidate, 512 input + intermediate size | 2b | train_Sb.csv | mixR at 512 | 512 / 64 x 4 | none (the frame) | none |

**The nine kernels:**
- PIL: BILINEAR, NEAREST, BICUBIC, LANCZOS, BOX. PIL antialiases its filters when shrinking.
- OpenCV: INTER_AREA, INTER_LINEAR, INTER_CUBIC, INTER_LANCZOS4. The last three do not antialias.

**The mixes:**
- **mix:** one kernel drawn uniformly per image and per step.
- **mixR:** with p = 0.5, a two-step resize 512 → s → output, where s = round(exp(U(ln 256, ln 400))) and each step
  draws its own kernel; otherwise one step as in mix.
- The band 256-400 is chosen to exclude both storage-test sizes (237 and 437 px equivalents), so the storage test
  stays a test at both sizes.
- At 224 the two-step branch only shrinks (s > 224). It varies the resampling history without removing passband
  content.
- At 512 (SbMR512) the two-step branch is a shrink-and-enlarge that removes content above s/512 of the band. There it
  is the augmentation analogue of the stored-small copies. It is not the storage operation itself: it acts on the
  aligned frame, not before alignment.

**Draws:**
- Draws come from a per-worker numpy stream seeded with (torch.initial_seed() + 7919) mod 2^63. This is separate from
  the loader's flip stream.
- So A0 and Sb0 see the same flips as the FS1 path. A local CPU check confirmed that fixed:pil_bilinear equals the
  current loader bit for bit (max difference 0).

**Choices stated:**
- **Refitting A0 and Sb0.** A0 and Sb0 repeat AB1's A and Sb exactly (same manifests, flags, seeds, GPU model and
  software build). They are refit so that every network is scored inside its own fit job on the same rows. AB1's
  in-fit numbers for A and Sb are printed beside A0 and Sb0 as a reproduction check, labelled "AB1, other fits". They
  enter no rule.
- **The crop window.** The window is fixed before any fit. It is centred on x = 256 and starts 50 px above the eye
  line, so it covers eyes to mouth.
  - It excludes the black border of small faces, the face outline and most of the hair.
  - It also excludes part of the splice hull at the jaw, so Sbc's splice reads are not like for like (printed).
- **Single-crop scoring only.** Every crop arm is scored on that one window. No multi-crop averaging is done: that
  would be an ensemble, which the author has ruled out.
- **512 input, CLIP ViT-B/16.** CLIP was pretrained at 224, so the tower is built at img_size 512, and timm's
  checkpoint filter resamples the 14 x 14 position embedding to 32 x 32 (`resample_abs_pos_embed`, bicubic). This
  interpolation is a design choice of the arm.
  - The pack's archs_a12.py refuses any resolution other than 224 for a pretrained CLIP tower. The RZ1 patch sets
    `archs_a12.CLIP_RES = 512` for the 512 arms only; no pack file is edited.
  - The job's first-step guard asserts:
    - 1,025 tokens;
    - an embedding equal to the bicubic resample of the 224 one within 1e-5;
    - items of 3 x 512 x 512;
    - after training: meta.json res 512, bs 64, accum 4, steps 6,250.
  - Batch 256 is reached as 64 x 4 accumulated micro-batches. The memory measured on the DGX is 4.2 times that of 224.
- **Not DINOv3 at 512.** DINOv3 ViT-L/16 handles 512 natively (RoPE), but its fit would take about 11 H100-h, and the
  BB2 owner's training-fit gate (E3) for its learning rate is unread. The BB2 owner agreed: DINOv3 stays at 224 in
  their programme, and no base arm is duplicated. The RZ1 loader may be offered for one DINOv3 arm once E3's gate is
  read.

## 3. Data and code

- **Inputs, all sha256-pinned in `src/RZ1/run_rz1.sh`:**
  - the FS1 pack (96c31ae2…);
  - the AB1 overlay v2 (171fdb21…);
  - the AB1 border overlay (e5886e72…), which gives `ab1x_eval.csv` 5257fb63…: AB1's 21,277 evaluation rows plus
    3,582 border rows;
  - the TT1 pack (2109f742…; 30,994 rows from eight unseen low-resolution sources in seven families, the border
    references R_cam_border and R_ffhq_border, the geometry references g224 and g112, and the gate rows R_cam,
    R_ffhq, M_ffhq);
  - the TT1-M MEDS pack (3fb917b2…; 1,018 rows, 865 primary);
  - the RZ1 overlay (sha256 in `pins.sha256`; code, the cross-table manifest, RZ1SUMS).
- **Unchanged:** the morphs, the storage copies and every image file. NIST MEDS may be used on all machines by the
  author's ruling. No MEDS image or identifier appears in any RZ1 artifact; only aggregate flag shares do.
- **Cross-table rows** (`rz1_cross.csv` 2f41e6d4…, 13,771 rows, `src/RZ1/mk_rz1.py`):
  - landmark_combined 1,000 morphs and 2,000 resmatch genuine photos;
  - development splices S0, S3 and S4, 100 each;
  - development camera photos 226 and their 452 stored-small copies;
  - the MS1 FFHQ hold-out, 1,480;
  - development border-blanked camera photos, 1,582;
  - TT1 R_cam, 417, and every fourth row of each unseen source.
- **Code (`src/RZ1/`):**
  - `rz1_kernels.py`: the transforms.
  - `rz1_patch.py`: replaces `common.ImageItems.load` at import time and, for 512 only, sets `CLIP_RES`.
  - `rz1_train.py`: runs the unchanged pack `train.py`.
  - `rz1_score.py`: pn1_score.py's core with the transform.
  - `rz1_guard.py`, `run_rz1.sh` (a copy of AB1's run.sh v2 with marked changes), `mk_rz1.py`, and
    `wcss/rz1-{smoke,w1,crop,512}.sbatch`.
- **Scoring, inside each fit job** (same H100 and build; TF32 on as pn1_score.py; logit without flip as the read value):
  - ab1x_eval, the unique training rows, TT1 and MEDS under the primary transform;
  - the cross table under the nine training kernels and four held-out test transforms (resize arms only; section 12).

## 4. Reads (every network; own rule logit > 0; development data only)

- **C2P quantities.** Exactly as AB1, with the functions of `src/PN1/c2p_read.py` on the ms1ffhq rows:
  - Δf(n, z), Δm(n, z), Δm_att(n, z) and the upper 95% bound of Δf, for z ∈ {fm61, amsl112};
  - the C2P.3 pass of X against a control arm at the same seed, with the control's own C2P requirement.
  - The control is A0 for 224 arms and A512 for 512 arms; against A0 is printed for 512 arms.
- **Detection.** landmark_combined AUC with a 95% within-class bootstrap (default_rng(20261118)).
- **Floors.** The best of the 27 statistics and their baseline, recomputed on the arm's primary input:
  - 224 arms: on the 224 image made by the arm's primary kernel;
  - crop arms: on the crop;
  - 512 arms: the existing full-resolution values 0.886 / 0.814.
  - Computed on the DGX CPU before the read, with the existing cue code applied to the transformed array.
  - "Exceeds the floor" uses the R2 floor rule of AB1 (2.5% bound of AUC minus floor, re-taken in the same draw, above
    0 on every read seed).
- **Same-person and splice flags.** Development S3, S0 and S4 flag shares; S3-vs-S4 AUC; same-person morph flags
  (ladder R3 and R3m, development); warp-only flags.
- **Unseen genuine sources (TT1 statistics):**
  - per-family own-rule share with person-bootstrap bounds, using the TT1 reader's functions, pools and draws (seed
    20261122) unchanged;
  - **F̄** = mean over the seven families; **TT-H1** failing families (lower bound above 5%);
  - **border reaction Bd** = mean over families of the R_cam_border flag share minus the R_cam flag share;
  - **geometry references** g224 and g112 flag shares (printed);
  - **MEDS:** the TT-M1 per-network verdict ("transfers" if the person-bootstrap upper bound ≤ 10%).
- **Camera photos and storage.** Development camera-photo flags (226); the development storage rise Δsoft (AB1's
  definition).
- **Kernel sensitivity κ** (cross table, resize arms):
  - For each of the eight non-primary kernels, the absolute change in own-rule flag share from the primary kernel:
    - on the genuine cross rows (camera 226, FFHQ hold-out natives 300, R_cam 417, TT1 sample genuine);
    - on the morph cross rows (landmark_combined morphs 1,000).
  - κ = the largest of these 16 changes.
  - Printed beside it: the landmark_combined AUC and the C2P Δf at fm61 under every kernel.
- **Training-row flags** per row kind (printed).

## 5. Hypotheses, pass and fail rules (fixed now)

**Seed counting** is AB1's (section 5 there). With n read seeds, "on ≥ 4 of 5" means 4 of 5 when n = 5 and 4 of 4 when
n = 4. With n ≤ 3 the result is "not read (too few seeds)". A seed is read for a hypothesis only if every network it
needs at that seed passed provenance: sha256, an H100 in gpu.txt, steps, every input pin, the arm in task.env, the
manifest hashes, finite loss, guard lines present, and complete finite scores. Margins are inclusive. Any other outcome
is "inconclusive, no claim". Rules marked primary are the RZ1 answers; the rest are secondary, with no multiplicity
correction.

### Wave 1: question 3, resize mixing (primary)

- **H-mix1, mixing reduces plain training's storage reaction** (separately for X = AM and X = AMR).
  - ρ(s, z) = Δf(X_s, z) / Δf(A0_s, z), on seeds where A0's C2P control is met at z.
  - Supported: ρ ≤ 1/2 on ≥ 4 of 5 at both sizes.
  - Falsified: ρ ≥ 0.8 on ≥ 4 of 5 at both sizes.
  - "Uninformative" if A0's control is met on ≤ 3 seeds at either size.
- **H-mix2, mixing alone meets the storage bars** (whether it replaces the protocol negatives for storage). X ∈ {AM,
  AMR} is read as an X of C2P.3 against A0, as AB1's H-ab1s.
  - Supported: X passes on ≥ 4 of 5 at both sizes.
  - Falsified: X passes on ≤ 1 at either size, with A0's control met on ≥ 4 there.
- **H-mix3, mixing lowers plain training's unseen-source false alarms.**
  - Per seed, ΔF̄ = F̄(X) − F̄(A0), with the person-bootstrap 95% interval of the difference (TT1's draws).
  - Supported: ΔF̄ ≤ −0.01 with the upper bound below 0, on ≥ 4 of 5.
  - Falsified: ΔF̄ > −0.005 on ≥ 4 of 5.
- **H-mix4, mixing adds to the candidate.** For X ∈ {SbM, SbMR} against Sb0 at the same seed, four parts:
  - (a) ΔF̄ = F̄(X) − F̄(Sb0), with the H-mix3 rule;
  - (b) ΔBd = Bd(X) − Bd(Sb0): lower if ≤ −0.02 on ≥ 4 of 5; falsified if > −0.005 on ≥ 4 of 5;
  - (c) storage: X passes C2P.3 against A0 at fm61 on ≥ 4 of 5, and Δf(X, amsl112) ≤ Δf(Sb0, amsl112) + 0.01 on
    ≥ 4 of 5;
  - (d) detection guard: landmark_combined X − Sb0 ≥ −0.02 on ≥ 4 of 5.
  - **"Adds" (supported):** (a) or (b) supported, with (c) and (d) met.
  - **"Does not add" (falsified):** (a) and (b) both falsified.
  - Otherwise "inconclusive, no claim".
  - If (d) fails, the reading is "trades detection for …".
- **Detection guard for plain mixing (H-mix5).**
  - "Held": AM or AMR minus A0 ≥ −0.02 on ≥ 4 of 5.
  - "Lost": < −0.02 on ≥ 4 of 5.
  - Printed with every H-mix1 to H-mix3 verdict.
- **How the author's question is answered.**
  - "Resize mixing is a cheap remedy for the resampling shortcut of plain training": H-mix1 supported and H-mix5 held.
  - "It replaces the protocol negatives for storage": H-mix2 supported. It is never said to replace them for splices,
    which mixing does not address.
  - "It adds to the candidate": H-mix4 supported.

### Wave 1: question 2, kernel dependence

- **H-ker1, the plain network has learned the current kernel** (A0).
  - Supported: κ(A0) > 0.10 on ≥ 4 of 5.
  - Falsified: κ(A0) ≤ 0.05 on ≥ 4 of 5.
  - Printed for Sb0 the same way.
- **H-ker2, mixing removes the kernel dependence** (primary for Q2). For X ∈ {AM, AMR} against A0 and X ∈ {SbM, SbMR}
  against Sb0.
  - Supported: κ(X) ≤ κ(base)/2 and κ(X) ≤ 0.05 on ≥ 4 of 5.
  - Falsified: κ(X) ≥ 0.8 κ(base) on ≥ 4 of 5.
  - "Uninformative" if κ(base) ≤ 0.05 on ≥ 4 of 5 (nothing to remove).
- **H-ker3, the training kernel changes the storage reaction** (AN against A0).
  - Supported: |Δf(AN, fm61) − Δf(A0, fm61)| ≥ 0.10 on ≥ 4 of 5, all in one direction (the sign is reported).
  - Falsified: the absolute difference < 0.03 on ≥ 4 of 5.
  - Printed: AN's landmark_combined, F̄ and κ.

### Wave 2b: question 1, 512 input (the trade is made explicit)

- **H-512a, detection.**
  - Supported: Sb512 − Sb0 landmark_combined ≥ +0.03 on ≥ 4 of 5.
  - Falsified: < +0.01 on ≥ 4 of 5.
  - Printed the same way: A512 − A0. Floor: Sb512 against 0.886 by the floor rule.
- **H-512b, the storage reaction rises at 512.**
  - Plain: Δf(A512, fm61) − Δf(A0, fm61) ≥ +0.10 on ≥ 4 of 5 is supported; < +0.03 on ≥ 4 of 5 is falsified.
  - Candidate: Δf(Sb512, z) − Δf(Sb0, z) ≥ +0.05 at either size on ≥ 4 of 5 is "rises"; < +0.02 at both sizes on
    ≥ 4 of 5 is "does not rise".
  - Printed: Sb512's C2P.3 pass against A512 and against A0.
- **H-512c, unseen-source false alarms and the border reaction rise at 512.**
  - F̄(Sb512) − F̄(Sb0) ≥ +0.01 with the lower bound above 0, on ≥ 4 of 5, is "rises"; < +0.005 on ≥ 4 of 5 is "does
    not rise".
  - The same for Bd with +0.02 / +0.005. MEDS: TT-M1 on ≥ 4 of 5.
- **Trade verdict (primary for Q1):**
  - "better at no measured cost": H-512a supported, and none of storage, F̄ and Bd "rises" for Sb512;
  - "a trade": H-512a supported and at least one "rises";
  - "no gain": H-512a falsified;
  - otherwise "inconclusive, no claim".
- **H-512d, mixing at 512 (SbMR512 against Sb512).**
  - Supported: SbMR512 passes C2P.3 against A512 at both sizes on ≥ 4 of 5, AND SbMR512 − Sb512 landmark_combined
    ≥ −0.02 on ≥ 4 of 5, AND F̄(SbMR512) ≤ F̄(Sb512) on ≥ 4 of 5.
  - Falsified: SbMR512 fails C2P.3 against A512 at fm61 on ≥ 4 of 5.
  - "Uninformative" if A512's control is met on ≤ 3 seeds at either size.

### Wave 2a: question 4, native crop against the whole frame

- **H-crop1, detection.**
  - Supported: Sbc − Sb0 landmark_combined ≥ +0.03 on ≥ 4 of 5.
  - Falsified: < +0.01 on ≥ 4 of 5.
  - Printed: Ac − A0, and the floors on the crop.
- **H-crop2, storage.** Ac and Sbc read as X of C2P.3 against A0, as printed reads.
  - Supported for "the crop alone meets the storage bars" if Ac passes on ≥ 4 of 5 at both sizes.
  - Falsified if Ac passes on ≤ 1 at either size.
- **Border, splices, MEDS and F̄** are printed only. The border is outside the window by construction for most images,
  so a low Bd is not a learned property.

## 6. Must not be claimed

- That any RZ1 arm is a method, a candidate or "shortcut-free". Anything about benchmarks. "Removes" for any shortcut:
  the reads say "reduced at the decision rule on development data".
- Generalisation beyond the OpenCV-style training engine and the FRGC and colorFERET training hosts.
- That 512 is better "at no cost" unless the trade verdict says so.
- That mixing replaces the protocol negatives beyond the storage reads.

## 7. Failures, platform, read once

- **Platform.** WCSS H100 only (lem-gpu-short, `gpu:hopper:1`, 8 CPUs, 64 GB, 80 GB local disk, `~/dmenv` torch 2.11
  cu128, timm 1.0.30, Pillow 12.3.0, OpenCV 5.0.0). Every fit and every score of RZ1 is on H100s with that build, and
  every network is scored inside its own fit job. A network whose gpu.txt does not name an H100 is not read.
- **Failures.** An infrastructure failure is re-run once, unchanged, on H100. A non-finite run is never re-run. A run
  that is out of memory or over the limit is re-run once with twice the limit, unchanged otherwise, and labelled. A
  lost arm-seed counts against the denominator.
- **Smoke.** A WCSS smoke job is required, because the run path differs from AB1's (TT1 and MEDS packs, OpenCV
  kernels, the RZ1 scripts, 512 input):
  - arm SbMR, 100 steps, full scoring;
  - arm Sb512, 20 steps at 64 x 4, 64 scoring rows.
  - It measures step rates, memory and scoring time, and decides nothing.
  - The fit arrays age alongside it (the lead's rule). Their outputs count only if the smoke passes: exit 0, all
    guard lines, all scores finite. If it fails, the dispatcher cancels the arrays.
- **Read once, per wave**, by `src/RZ1/rz1_read.py`.
  - The reader is committed with its sha256 before the first RZ1 tar is fetched. It is tested on mock tars (full, and
    with one seed dropped) and implements the rules of section 5 exactly. It imports AB1's reader functions,
    c2p_read.py and the TT1 reader functions unchanged.
  - Each wave is read when all its fits have ended, or at 15 Nov 2026 18:00 CET with the fits present then, whichever
    comes first. Rows that arrive after that read are reported as late rows (the author's ruling on cluster waits),
    read once by the same reader, and labelled late.
  - No RZ1 number is looked at before its wave's read. The smoke's outputs are checked only for finiteness and timing.
- **Copies.** Two verified copies of every tar before the read: WCSS `results/RZ1` and `/mnt/t7/smad_next/RZ1/results/`.
  Trained weights are kept.

## 8. Proposed selection rule for the next method version (a proposal; not in force)

The author has kept the freeze (about 18:36 by the machine clock). This rule is proposed now, before any RZ1 fit, for
the freeze of a next version of the method. It applies only if the author adopts it before the RZ1 reads.

At most one RZ1 arm replaces Sb, and they are considered in the fixed order SbMR, SbM, Sb512, SbMR512, Sbc. The first
arm that meets all of the following, on its own five seeds against Sb0 at the same seed, is chosen:
1. It passes C2P.3 against its plain control at both sizes on ≥ 4 of 5, with that control met, and storage evasion
   (H-new-1) is falsified.
2. landmark_combined is at least Sb0 + 0.03, paired, on ≥ 4 of 5.
3. F̄ ≤ F̄(Sb0) + 0.01 on ≥ 4 of 5, and MEDS "transfers" on ≥ 4 of 5.
4. Bd ≤ Bd(Sb0) on ≥ 4 of 5, and the development S3 flag share ≤ Sb0's + 0.05 on ≥ 4 of 5.
5. For the resize arms, κ ≤ 0.05 on ≥ 4 of 5.

Then:
- The chosen arm's sealed read runs on WCSS H100, the platform it was trained on, with the byte-identity gate on
  development rows first. It never runs on a rented A100: H100-trained networks scored on another GPU model are the
  C2P failure mode.
- MAD22 counts as a benchmark seen during development (it is read with the frozen candidate first).
- Every arm is reported.

## 9. Budget and timing

| Wave | Fits | Per fit (estimate) | H100-h | Limit | Readable by 15 Nov 18:00? |
|---|---|---|---|---|---|
| Smoke | 1 job | about 25 min | 0.4 | 1:30 | yes |
| 1 (resize) | 35 | 45-60 min training plus about 10 min of input copy and scoring | about 38 | 2:00 | yes, if it starts by about 15 Nov 12:00 |
| 2a (crops) | 10 | as wave 1 | about 11 | 2:00 | likely |
| 2b (512) | 15 | about 4.5-5.5 h (6.4 times the 224 step time measured on the DGX) | about 80 | 9:00 | only if it starts by about 15 Nov 06:00; uncertain |

Order within RZ1 for the dispatcher: smoke and wave 1, then crops, then 512. The dispatcher may hold the 512 array near
our 32-GPU cap.

## 10. Commands

```
python3 -I src/RZ1/mk_rz1.py                                   # cross manifest + overlay (done; DGX CPU)
# local code-path smoke (DGX; SbMR 20 steps full path, Sb512 3 steps): see README
cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/RZ1 && /opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR rz1-smoke.sbatch
cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/RZ1 && /opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR rz1-w1.sbatch
cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/RZ1 && /opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR rz1-crop.sbatch
cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/RZ1 && /opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR rz1-512.sbatch
```

## 11. Pins at the registration commit

In `pins.sha256` beside this file: every file of `src/RZ1/`, the overlay tar and rz1_cross.csv. Where an earlier line of
this file names an overlay hash, `pins.sha256` and section 12 take precedence.

## 12. Pre-run review fixes (`PRERUN_RZ1_20261113.md`, GO WITH FIXES), applied before any fit; they take precedence over sections 1-9

- **B1.** Code frozen, overlay rebuilt once after the fixes, all pins in `pins.sha256`, committed before any sbatch.
- **M1 (F̄ floor).** H-mix3 and H-mix4(a) per seed: "lower" if (ΔF̄ ≤ −0.01 OR F̄(X) ≤ F̄(base)/2) with the upper
  bound of ΔF̄ below 0. Supported: "lower" on ≥ 4 of 5. Falsified unchanged: ΔF̄ > −0.005 on ≥ 4 of 5. Printed beside
  it: F̄ at the cut-off −1 (TT1's `extra_reads`). The RZ1 F̄ (TF32 on, scored in the fit job) is never compared with the
  TT1 tables (TF32 off) as a measured difference (m4).
- **M2 (held-out kernels).**
  - The cross table adds four test-only transforms, never used in training: PIL HAMMING, cv2 INTER_NEAREST,
    cv2 INTER_LINEAR_EXACT, and the two-step 512 → 300 (HAMMING) → 224 (INTER_LINEAR_EXACT).
  - κ_ho is the same statistic as κ over these four only. **κ_ho is the binding quantity of H-ker2**, with the
    margins unchanged; κ over the nine training kernels is printed.
  - H-ker1 is renamed **"kernel sensitivity of the plain network"** (m7). Kernels that do not antialias add aliasing,
    so a large κ reads "the verdict depends on the resize kernel", never "learned the kernel".
- **M3 (floor).** The binding floor for every arm is 0.886 (the best single statistic at full resolution, as AB1). The
  floors recomputed on each arm's input are printed beside it. Their code and values are pinned before the read.
- **M4 (deciding size).** H-mix1 and H-mix2 decide at fm61 only (ratio rule, and C2P.3 pass at fm61, with A0's control
  met at fm61). amsl112 is printed, with the paired difference Δf(X) − Δf(A0) and its bootstrap interval (C2P's
  draws). The same applies to H-crop2 and H-512d (fm61 decides, amsl112 printed).
- **M5 (512 confound and resolution shortcut).**
  - Added to section 6: the CLIP tower, including the resampled position embedding, stays frozen. Only LoRA r2 on
    q and v and the head train, at learning rates set for 224. "No gain at 512" therefore reads "no gain at 512 with
    this frozen-tower recipe", never "512 does not help".
  - The trade verdict's list of costs adds "geo112 rises": the g112 flag share minus Sb0's ≥ +0.05 on ≥ 4 of 5.
    The same is printed for the crop arms.
- **M6 (512 timing).**
  - The WCSS smoke runs Sb512 for 30 steps at 64 x 4. The projected fit time is the smoke's seconds per step ×
    6,250 + 0.5 h.
  - The 512 array is queued only after the smoke, with `--time` = min(12 h, 1.3 × the projection), rounded up to
    the hour.
  - If the projection exceeds 7 h, SbMR512 is dropped (not submitted; reported "not run: cost") and only A512 and
    Sb512 run. If it exceeds 10 h, the lead is asked before anything at 512 is submitted.
- **M7 (scope; for the author).** "Native resolution" here means the stored aligned 512 frame's own pixels with no
  resampling after storage. Crops of the original capture would need new crop code on originals, which is not
  allowed. The lead approved the 224 interior crops (wave 2a). The author's reading of his ruling is asked through
  the lead. If he rules that 224 crops are not meant, wave 2a is cancelled before it starts, or is not read.
- **m1.** Arms Ac and Sbc are named "interior crop". The share of each splice hull inside the window is computed on
  the DGX CPU before the read and printed.
- **m2.** A 3-step local smoke of Ac and AN ran on the DGX before submission (README).
- **m3.** cv2 runs single-threaded in the workers.
- **m5.** rz1_read.py gets its own loader (RZ1 task_info keys) and a TT1 wrapper. It is mock-tested before the first
  fetch.
- **m6.** Section 8 adds a confirmation on five fresh seeds (413-417) of the chosen arm, read once with the same rules,
  before any freeze. Section 8 stays a proposal.
- **m8.** SbMR512's mixR band lies within 7-9% of both storage sizes. A C2P pass for it means it handles a perturbation
  close to one it trained on; it is never called generalisation.
- **Not taken up now:** rescoring AB1's kept A and Sb with rz1_score.py (about 2 H100-h: the refit-versus-original
  yardstick), and an arm mixing only antialiasing kernels (5 fits). Both are offered to the lead.

## Amendment 1: rescoring AB1's kept A and Sb as the refit yardstick

Written 13 Nov 2026 at about 19:20 by the machine clock, before any RZ1 network exists or any RZ1 or rescored score is
read. The lead accepted the reviewer's improvement 3 and asked for this amendment.

**What.** One WCSS H100 job (`src/RZ1/wcss/rz1-rescore.sbatch`, `src/RZ1/run_rz1r.sh`, `src/RZ1/rz1_rescore.py`) rescores
AB1's kept networks A and Sb at seeds 408-412: ten networks, tars in `results/AB1`, each sha256-pinned in run_rz1r.sh.
- It uses the RZ1 inputs and data root unchanged, with `~/dmenv` read-only (torch 2.11.0+cu128).
- Each network is rebuilt from its meta.json and last_trainable.pt. The frozen tower comes from the pack weights. The
  loaded keys must be exactly the trainable ones, and the missing keys exactly the frozen ones.

**Gate (bit identity).** Before any RZ1 row of a network is used, its 21,277 ab1_eval.csv logits are recomputed exactly
as pn1_score.py did in AB1's fit job: same loader, batch 64 in manifest order, TF32 on, logit without flip.
- They are compared with the tar's stored scores_eval.npz. **"Passed" means every float32 logit is equal.**
- A network whose gate fails is not used in any read of this amendment. It is reported as "gate failed", with the
  number of differing rows, max |Δ| and own-rule agreement.
- If more than 2 of the 5 networks of an arm fail, the yardstick for that arm is "not available".

**Then** the unchanged rz1_score.py runs on the rebuilt network. It gives the outputs of an RZ1 A0 or Sb0 fit job:
primary fixed:pil_bilinear on ab1x_eval, training rows, TT1, MEDS, and the 13-spec cross table.

**Reads (descriptive; they enter no hypothesis of section 5).**
- For every per-network read of section 4 and each seed: the refit difference δ(r, s) = r(A0_s) − r(AB1 A_s), and the
  same for Sb0 against AB1 Sb.
- Printed per read: each δ, the median of |δ| over seeds and the maximum of |δ| over seeds.
- Plain-words use: a paired RZ1 difference smaller than the maximum same-arm, same-seed refit |δ| of that read is
  written "within refit noise", whatever its verdict.

**Change to the section 8 proposal.**
- Criterion 2 also requires the median paired landmark_combined gain over Sb0 to exceed the maximum over seeds of the
  Sb refit |δ| on landmark_combined.
- If the yardstick is not available, criterion 2 is unchanged and the gap is stated.

**Order and cost.** About 1-1.5 H100-h. Queued behind wave 1 and valid only if the RZ1 smoke passed. Read once with the
wave 1 read, by rz1_read.py, which loads the RZ1R tars with their gate.json.

**Pre-run check.** Requested from the lead. A local code-path test is in the README; on the DGX GPU the gate is
expected to fail, because it is another GPU model.

**Amendment 1, fixes from its pre-run check** (`experiments/reviews/PRERUN_RZ1_A1_20261113.md`, GO WITH FIXES; applied
at about 19:35 by the machine clock, before the job was submitted).
- Then, for a network whose gate passed, the unchanged rz1_score.py runs. A network whose gate fails is not scored
  further.
- The gate also fails ("RZ1R FAIL") unless the stored id list equals the current ids in order, and the stored
  manifest_sha256 equals the sha256 of manifests/ab1_eval.csv.
- gate.json records the driver version. Two AB1 Sb fits (s409, s410) ran on driver 595.91.07 and the other eight on
  595.112.07. Bit identity across drivers is likely, not guaranteed.
- Yardstick wording: "the maximum of |δ| over the seeds whose gate passed and whose RZ1 refit exists (n printed beside
  it)".
- The job is submitted with --dependency=afterok:6316283 (the RZ1 smoke) and placed behind wave 1 by --nice.
- rz1_read.py excludes every network whose gate.json does not say "passed". It is pinned before the wave 1 read.
