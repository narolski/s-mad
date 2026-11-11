# AR1 (with AR2, AR3, AR4, first round) Landmark-morph ladder with composition-matched self-morph twins

Written 11 Nov 2026, about 14:45 CET. At this point no AR1 detector score exists: the images are being built and no
detector has run on them. Scores read before this page: the A46 RGB-only descriptive tables
(`mambamorph-code/experiments/A46_diffusion-register-raw-files/RGB_ONLY_RESULTS_20261108.md`, read for gate G-a)
and the A46 published anchors (`smadcvpr/plans/A46/A46_published.json`). Nothing from the r8 sets has been scored.

- **Hypothesis (plain words):** when released detectors separate landmark morphs (OpenCV, FaceMorpher) from camera
  photos, the separation comes from morphing two people (R2 -> R4 carries most of it), not from tool processing of a
  genuine photo (R0 -> R2). Side question: is a same-person morph (twin) flagged like a morph (R2 -> R3) or does the
  detector need the second identity (R3 -> R4)?

- **Data (built on the DGX CPU, unchanged tools, PNG at tool size 512 x 512):**
  - Primary pool: FRGC 2.0 + colorFERET, 536 host persons (FRGC 427, FERET 109); `experiments/AR1/pool.csv`,
    `src/AR1/pool.py`. Source frames are the record's existing 73_delin_align frames with 106-point `.tem`
    (train/bona_frgc, arms/r6_frgc, train/bona_feret), copied byte-identically to `/mnt/t7/smad_next/AR1/src`.
    Per person: host H (neutral, session s1), second S (neutral, session s2 != s1), independent reference R (another
    photo, for the FR oracle only; 534 of 536). B = S of another person of the same database, by a permutation
    without fixed points that maximises glintr100 cos(H_p, S_q) (every person is host once and second contributor once).
    Session = capture date; FRGC neutral = BlankStare in the bbaselite dump; FERET neutral = fa.
  - Rungs per host: R0 = H; R1 = not built (see below); R2 = tool(H, H); R3 = tool(H, S); R4 = tool(H, B);
    NC (negative control) = tool(S, H). Tools: OpenCV (`scripts/78_tool_morph.py`, first tool) and FaceMorpher
    (`scripts/96_facemorpher_tool.py`), both unchanged. The A27 / h1_build warp path is not built in round 1.
  - AR2 graded set: 300 seeded hosts, FaceMorpher library (`baselines/face_morpher`, unchanged functions, the
    library's own frame loop with background 'average'), mixing m = 0, 0.1, 0.2, 0.3, 0.4, 0.5 on (H, B).
    OpenCV graded is not built: `78` / `68_hires_morph.morph` hard-code 0.5, so a graded OpenCV would need a code change.
  - Secondary pool: FRLL, 102 persons. Raw front photos aligned with the unchanged `scripts/73_delin_align.align`
    (same aligner as every train / R6 / R8 frame). H = p_03 (neutral), S = p_08 (smiling), B = q_08 by the same
    assignment. Bridge sets: tool(a_03, b_03) for every published FRLL-Morphs pair of that tool (opencv 1,221;
    facemorpher 1,222; published pairs assumed neutral-neutral, as the AMSL file names in the dataset state).
    FRLL benchmark side: raw photos and published morphs (the A46 RGB crops), and in prep_eval frames
    frll_bona orig (R0f), the existing E7 frames `*_resmatch_{opencv,facemorpher}` (R1f) and published morph frames.
  - R1 on the primary pool: our morphs are made from the same aligned 512 frames as R0, so morphs and photos have the
    same face size and the same resampling history; the E7 rule (photos shrunk to the morphs' median face size) is the
    identity here and no E7 output exists for these frames. The R0 -> R1 step is therefore 0 by construction on our
    builds and is measured only on the FRLL benchmark side (R0f -> R1f, existing E7 outputs).
  - Known before scoring (smoke test, 8 hosts): OpenCV R2 is bit-identical to H (mean |diff| 0); FaceMorpher R2
    differs from H by at most 1 grey level in about 14% of pixels. The R0 -> R2 step on our builds is therefore
    expected to be near zero for every detector; this is a property of the tools at tool size, recorded here so that a
    near-zero R0 -> R2 share is not read as a detector finding. The benchmark processing (resize to the published size,
    JPEG) is not part of "tool run on one photo" and is not reproduced by R2.
  - Identity overlap (printed with every table): FRGC / FERET persons are unseen for the released detectors (SMDD
    training; SelfMAD's training set not verified). The M3 / M3L retrains used here are R x d0 (SMDD only), so FRGC /
    FERET are unseen for them too; the r8 sets (training identities of our d1 / A8-W1F networks) are not used in the
    primary table. FRLL persons are the benchmark's bona fide and never enter any training or refit.

- **Detectors (scored as released, each on its own preprocessing):**
  - SelfMAD release HRNet-W18 (sha 0ad8db6f, fetched from WCSS A12REL by one rsync): own preprocessing
    (`rsx_selfmad_own`, dlib 81 points, 384, softmax[:,1]).
  - MADation ViT-B/16 (ddb1455b) and ViT-L/14 (bb452ded), MixFaceNet-MAD (3d507c8b): the A46 RGB-only path (RGB MTCNN
    crop of `a46_corrective_crop.py`, then `a12_released` adapters via the same functions as `a41g_score.run_rel`).
  - Our retrain block (separate, labelled "our retrain"): M3 (MADation recipe ViT-B/16, R x d0, seeds 1-8) and M3L
    (ViT-L/14, seeds 1-5), last.pt, our 512-frame pipeline (`a41g_score.run_nets` functions). Every seed is reported;
    no seed is picked and no scores are averaged into a decision; the verdict line for the block is the count of seeds
    per verdict.
  - Decision key: `score_noTTA` (morph = higher). AUC is rank-based; d' = sqrt(2) * Phi^-1(AUC), AUC clipped to
    [0.005, 0.995] (a41_read.dprime).

- **Primary metric:** for every detector x tool x pool, the AUC of each step (higher rung positive): R1->R2 = R2 vs R0
  (R1 = R0 on our builds), R2->R3 = R3 vs R2, R3->R4 = R4 vs R3; main R2 vs R4; R0 vs R4. Share of a step = its d'
  divided by d'(R0 vs R4). 95% intervals from the two-way (pigeonhole, dyadic) person bootstrap of `a41_read.Draw`
  (B = 2,000, seed [20261111, 1]): a single-person image weighs its host's count, an R4 image the product of its two
  contributors' counts; the same draw for all detectors, tools and rungs of a pool (paired).

- **Gates, computed before any score file is opened:**
  - G-a (reproduction): from the A46 RGB-only result, FRLL OpenCV / FaceMorpher EER within 3 points of the published
    cell. ViT-B/16 1.47 / 0.86 vs 2.97 / 1.35 and MixFaceNet 4.42 / 2.98 vs 4.39 / 3.87: reproduced (ViT-B/16 with the
    A46 AI-10 caveat on which variant the published FRLL numbers belong to). ViT-L/14 and SelfMAD: no published
    landmark-cell anchor in the record -> "not reproduced, descriptive". Our retrains: separate block.
  - G-b (twin validity), glintr100 through the registered X3 route (prep_eval.kps, norm_crop, a2f_common 'glint'):
    oracle score = 1 - cos(image, R_host) (R = independent reference photo); AUC R4 vs R3 >= 0.90. Verification
    threshold tau at FMR 1/1,000 from the impostor scores cos(H_p, R_q), p != q, same database. Morphs verify against
    both contributors (cos(R4, R_host) >= tau and cos(R4, R_B) >= tau) in >= 70%; twins verify against the host
    (rate printed). Negative control: oracle AUC of NC vs R3 within [0.40, 0.60]. Computed per tool and pool
    (FRLL: no independent reference; the oracle uses the other expression of the host is not possible, so FRLL
    G-b uses H as reference and is labelled "source-photo reference").
  - G-c (readability): L2 logistic regression (sklearn, standardised, C = 1) on each detector's frozen features
    (input of its last linear layer, no-TTA pass), R4 vs R3, 5-fold GroupKFold by host person, pooled out-of-fold
    AUC; below 0.65 -> wording "neither the released detectors nor a probe trained for it read identity blending".
    Negative control probe: NC vs R3, expected 0.5.

- **Verdict rules (fixed in 11_AUDIT_PLAN.md, copied):**
  - Main, R2 vs R4: Reads morphing = AUC >= 0.75, lower bound > 0.65, R0 -> R2 share <= 0.2. Reads the benchmark =
    R0 -> R2 share lower bound >= 0.5, or folded AUC < 0.60 with upper bound < 0.65. Mixed otherwise.
  - Side, R3 vs R4 and R2 vs R3: No identity reading = folded AUC < 0.60, upper bound < 0.65; Twin artefact, cell
    invalid = AUC < 0.40 with upper bound < 0.5; Identity reading = AUC >= 0.75, lower bound > 0.65; Mixed otherwise.
  - Twin rejection rate at the benchmark threshold (the detector's EER threshold on the FRLL benchmark cell of the same
    tool, raw files for releases, prep_eval frames for retrains) with Clopper-Pearson interval; no rule.
  - Multiplicity: the four landmark primary cells (4 releases x OpenCV x primary pool) are 4 of the plan's 12; I print
    the one-sided bootstrap p of "AUC(R2 vs R4) <= 0.65" and the Bonferroni-at-12 interval (99.58%) as a conservative
    stand-in for Holm (the other 8 p-values do not exist yet). Everything else is descriptive.

- **AR2 (dose):** per detector, mean logit per mixing level; Page trend test (scipy `page_trend_test`, blocks = the 300
  hosts, predicted order m = 0 < 0.1 < ... < 0.5); "monotone" = Page p < 0.05. AUC(m vs m = 0) per level with person
  bootstrap intervals.

- **AR3 (baselines), out-of-fold by host person where learned, same contrasts as the detectors:**
  non-content: (a) file attributes (PNG bytes; width / height are constant 512 on our builds; on the FRLL benchmark
  side file bytes, width, height of the raw files); (b) border mask only (exact-zero pixels: fraction + 32 x 32 block
  means of the mask, logistic); (c) background only (face hull blanked to constant grey, 32 x 32 block-mean thumbnail,
  logistic). Content: (d) 32-pixel thumbnail of the whole image; (e) face only (background blanked) thumbnail.
  The 32 x 32 block means are a numpy feature (16 x 16 block average), never written as an image or shown to a
  detector. Reading: detector AUC minus best non-content baseline AUC, paired bootstrap, lower bound > 0.

- **AR4 (blanking):** constant colour (128, 128, 128); face mask = convex hull of the 106 `.tem` landmarks of the
  image's geometry (host `.tem` for R0 / R2; mean of the two contributors' `.tem` for R3 / R4 / NC, as both tools
  place the face). Background-blanked = outside the hull; face-blanked = inside. Crop boxes (MTCNN) and SelfMAD
  landmarks are taken from the unblanked image. Scored for the four releases on the primary pool; AUC R2 vs R4 and
  R0 vs R4 with intervals. "Works with the face blanked" = R2 vs R4 AUC >= 0.75 with lower bound > 0.65.

- **Falsifier (fixed before the run):** "reads the benchmark" on the main contrast for a release on both pools
  refutes the hypothesis for that release; "reads morphing" on both pools with G-b and G-c passed supports it.

- **Guards:** negative control (FR oracle, probe, and detector AUC of NC vs R3); thumbnail and non-content baselines;
  identity overlap printed; G-a; no image operation other than the unchanged tools, the unchanged aligner (FRLL only,
  disclosed), constant-colour blanking, lossless PNG.
- **Stop rule and budget:** DGX only; GPU shared with other jobs (modest batch sizes); about 1 GPU-hour.
- **Commands:** `src/AR1/{pool,build,graded_fm,frll_prep,crop_rgb,score,gates,analyse}.py`; each tested on 8 images
  (smoke outputs under `/mnt/t7/smad_next/AR1/img/smoke`) before the full run.
- **Pre-run review:** not run (owner brief does not require it for this round; flagged to the lead).
- **Result:** `experiments/AR1/result.md`.

## Amendments (all registered before the detector scores they concern were opened)

1. 11 Nov about 15:00 CET (lead): new one-photo rungs. R2w, warp-only: host photo H warped by the tool's own warp
   routine to the mean shape of H and its same-person photo S, texture from H only, no blending. R3m, mirror
   self-morph: the unchanged tool on H and its lossless left-right mirror, with mirrored and re-indexed landmarks
   (measured 106-point permutation). Verdict rules applied with R2w in place of R2; R2 kept and labelled
   "identical to R0" for OpenCV. Validity: R2w differs from H; R3m cosine to H >= R3 (both checked, passed).
2. 11 Nov about 16:45 CET (lead): FRLL smiling files differ in capture detail (larger files, noisier backdrop).
   Every FRLL rung that uses a smiling file (R2w, R3, R4 with a smiling partner, NC) is labelled "confounded by capture
   detail and expression" and gets no verdict. Clean FRLL controls: R2wm (H warped toward its own mirrored shape,
   neutral file only) and R3m; FRLL clean ladder R0 -> R2wm -> R3m -> R4nn (our neutral+neutral two-person morphs of
   the published pairs). FRLL genuine class neutral-only wherever FRLL photos enter a contrast, all-photo number beside.
3. 11 Nov about 19:00 CET (lead, ID0): 8 primary hosts are validation-reserved persons (prep_train.is_val); results
   carry a sensitivity line without them. No rebuild.
4. 11 Nov about 19:45 CET (lead, ideation round 3): new rung R2w4, warp-only toward the two-person mean shape: H warped
   with the same warp routine to the SAME mean shape its R4 uses (mean of H's and B's landmarks), texture from H only,
   no blending; all primary hosts, both tools. Contrasts: R4 vs R2w4 (geometry held equal; only the blending of the
   second texture differs) and R2w4 vs R2w (what warp size alone does). Verification against the unchanged tool:
   averaging the A-side warp (R2w4) with the matching B-side warp must reproduce the tool's R4 inside the face
   (OpenCV: within rounding everywhere; FaceMorpher: inside the face mask), checked on 8 hosts and then on all.
5. Same date, reading rule: the mirror self-blend R3m is not a matched twin (a symmetry score isolates it, and a
   32-pixel thumbnail separates it from a two-person morph at about 0.93 in our AR3 baselines). R3m is read for
   trace contrasts only (processing / blending traces) and never supports a statement about a second person.
6. Same date, presentation rule: every detector row is printed beside the best simple baseline on the same contrast
   (32-pixel thumbnail, background-only thumbnail, band power, Laplacian variance, and the non-content baselines), as
   the excess AUC over that baseline with a paired person-bootstrap interval. Band power = the a41_read
   power_profile / band_shares luminance band shares (logistic, out-of-fold by host); Laplacian variance = variance of
   the 3x3 Laplacian of the luminance (one scalar, orientation folded). Both are measurements; no image is written.
