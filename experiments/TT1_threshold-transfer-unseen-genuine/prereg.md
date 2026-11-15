# Threshold transfer on unseen genuine sources (TT1)

Owner: TT1 owner agent (started by the lead, 12 Nov 2026). Folder created `date`: Thu Nov 12 10:54:00 PM CET 2026, at
git `dac4d99b2d8d42f24fc8c32c5dba0ab7c07671a8` (branch sprint-plan-v2).

## 0. Author's approval

- The author asked on the evening of 12 Nov which genuine data we have, and approved running the aligner on new unseen
  genuine sources, his words: "Run the aligner, of course!" (relayed by the lead in the owner's task message; the time
  of the author's message is not known to the owner; recorded here at `date` Thu Nov 12 10:54:00 PM CET 2026).
- The 12 Nov ruling holds: no set used to benchmark methods (FRLL, MAD22, MorDIFF, DiM, H1, FEI, sealed sets; also
  CASIA-WebFace, the source of H1) is used in development. The sources below are not benchmarks of this sprint, and
  none of them was used to train any network of the sprint.

## 1. Question (plain words)

Our candidate detectors (CLIP ViT-B/16 + LoRA, the protocol network first tests (PN1)) put morphs above genuine photos
well, but a fixed threshold does not carry over to genuine photos from a source they never saw: photos of the training
databases (FRGC, colorFERET) sit on the floor of a bounded score range, other sources sit higher. TT1 asks, on genuine
photos only, how often each network flags photos of unseen sources, whether that false-alarm rate follows the image's
enlargement (how much a small source face is blown up to the canonical 132 px eye distance) and sharpness or the source
itself, and which training arm gives the lowest and most uniform false-alarm rates. There are no morphs of these
sources, so TT1 is a false-alarm test only.

## 2. Step 2 (pool building; no score is computed in this step)

- Sources and rules: `src/TT1/extract.py` (docstring is the specification). Genuine anti-spoofing frames ("Bona fide"
  in each set's `metadata.json`, asserted equal to the documented file-name convention on every row) and distinct images
  of four face-verification validation packs (lfw, calfw, cfp_ff, agedb_30), loaded only with a restricted unpickler.
  Not used: CASIA-WebFace `train.rec`, `cplfw.bin`, `cfp_fp.bin`.
- Alignment: `src/TT1/align.py` calls `align()` of `/home/narolski/mambamorph-code/smadcvpr/prep_eval.py` unchanged
  (sha256 `374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628`), the function every genuine pool of PN1,
  AR1, AF0 and FFHQ-Morphs went through.
- The scoring experiment is registered separately (draft `prereg_scoring_draft.md`, for independent pre-run review);
  nothing is scored before that registration is committed.

## 3. Registration TT1-S (scoring), registered at the git commit that adds this section

- Text: `prereg_scoring.md` (applies the pre-run review `experiments/reviews/PRERUN_TT1_SCORING_20261112.md`, commit
  7c0ecb6, majors M1-M7, platform list, minors; and the lead's rulings R1-R5). `date` at writing: Thu Nov 12 11:25:24 PM CET 2026.
- At this commit no TT1 image, border-matched or crop-geometry-matched reference has been scored, and the
  crop-geometry-matched reference has not been built. Pins of the list, pack, network tar, job script and reader
  follow in a pins section, committed before any score.

## 4. Pins of registration TT1-S (committed before any score; `date`: Thu Nov 12 11:32:53 PM CET 2026)

Built after the registration commit 01557ce; no TT1, border or geo reference row has been scored by any network.
- Crop-geometry reference (section 2.4): `src/TT1/build_geo_ref.py` `4475ca8798790254c45e9842057ec22f35b1beaf7ffbf3bb707fb76f478d50ca`
  (imports soften.py `aa90f271…` and prep_eval.py `374408ab…` unchanged, pins asserted); 834 of 834 aligned;
  `/mnt/t7/smad_next/TT1/geo_ref.csv` `40d211f454274bbfb71d32bfd1ae872e94a70fb044411eeb7877d23113955310` (copy here).
  8-image test viewed before the full build (one g112 frame inspected: face crop with border, as intended).
- Border reference (section 2.3, edge-connected mask): `src/TT1/build_border_ref.py`
  `366058805349dc322088cf98debd78598eaa9900294e2c7f7ec37d5f1293113c`; 4,919 images; `border_ref.csv`
  `9d866232914ee6c1e3e363f31cf4109d6ec817d0e220abb45cbac217c475b07a` (gz copy here). Median masked share 0.422. The first
  build with the every-black-pixel mask (never scored) was deleted.
- Shared definitions `src/TT1/tt1common.py` `1053022792e99ade577abc11490d169e0bec15c6a6dd761fc5aac3b92c52a1a3`;
  `src/TT1/geometry.py` `85c52d3e54c73afef9ccdb2ae532b4d9ed08b24d684b69d7fe62447f57b5a606` (crop_geometry.json at 01557ce).
- Scoring list `tt1_score.csv` `c0055b51467cf8d001d56cbc4689706d68f0bf35c64066b1ba49fada5cb45761`: 34,411 rows (gate 3,417;
  tt1 30,994 = U_all 25,241 + border 4,919 + geo 834); builder `src/TT1/build_pack.py`
  `34322f3685e1872d426af13caea8b017bbd1debafadc8e2f29eff61fe26337fa` (asserts the forbidden pack files were never read
  and that every image path is under TT1 outputs or the PN1 fs_tree eval/pn1, eval/hn2).
- Pack `/mnt/t7/smad_next/TT1/tt1_pack.tar` `2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554`
  (8,103,157,760 bytes; 34,519 files under SHA256SUMS; bin/rescore.py `6f6eede7…`, bin/gate_check.py
  `36cfaa63347241d72a535ec898ca012737deb3e32f418c74004dfc1c6be7b657`). Reusable for the FS1 block.
- Networks `/mnt/t7/smad_next/TT1/tt1_nets_s401402.tar` `92bd1841bd9307659c4666bfc344974592613e310f2ee4187dc3fc6884205303`
  (12 networks, each tar checked against its .sha256; gate_ref/<net>.npz = stored A100 logits of the 3,417 gate rows;
  sources in nets.json).
- Job body `src/TT1/tt1_job.sh` `2a280c5f267a6cefb2314455a2676bc6e78f51b2127c3c9ad9d90aa76e2a21fd`; WCSS file
  `src/TT1/wcss/tt1.sbatch` `c3ad44cbebfd549db316af7e0f65af307e31d5b9b08aad713767a7350c1d3685`.
- Local DGX test of the job (TT1_MODE=test, 8 gate rows x 12 networks, torch 2.12.1 on GB10): runs end to end; largest
  |Δlogit| against the stored A100 logits 0.00067. gate_check.py self-test on identical scores passes.
- Reader `src/TT1/tt1_read.py`: pinned in the next commit, before the full job is submitted.
- Reader pin (`date`: Thu Nov 12 11:45:15 PM CET 2026; before any TT1 score): `src/TT1/tt1_read.py`
  `2b7b0898db9451792ab3dd2f8b02fc232da43d4d8943e3cae109030d2f503940`, tested on random mock scores only
  (`tt1_read_mock.json`, 4.5 min for 12 networks). Implementation choices stated now: flag-share and AUC intervals use
  the 2,000 registered draws; the ρ, leave-one-family-out and R5 paired intervals use every 4th of those draws (500) for
  cost; family-level own-rule intervals (TT-H1) pool the sources of a family (lfw_calfw: LFW and CALFW persons
  resampled within each source); TT-H3 family AUCs for lfw_calfw are the mean of the two source AUCs; τ_cam for Sb and
  Bv is computed with the tier-1 rule from their scores_eval.npz; floor = −‖head.cls.weight‖ + head.cls.bias.
- WCSS: pack, network tar, tt1_job.sh (+ .sha256) and tt1.sbatch uploaded to
  /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/TT1/ (rsync rc 0, 23:37-23:42).

## 5. Deviation TT1-D1 (`date`: Fri Nov 13 12:13:30 AM CET 2026; registered at the git commit that adds this section, before any TT1 row is scored on any platform): rented A100 instead of the DGX

- Fact: the DGX fallback gate (G-DGX tolerances) FAILED for all 12 networks (commit 3fb51f6, `gate_dgx_run2.json`):
  max |Δlogit| 0.032-0.116 against 0.02; the large differences lie only on the 2,000 FFHQ genuine rows (A_s401: R_cam
  max 0.0048, M_ffhq 0.0006, R_ffhq 0.088); one own-rule flip in A_s401, A_s402, C_s401; |ΔAUC| ≤ 0.00006; Kendall on R_cam
  0.995-0.998. Stacks: DGX torch 2.12.1 / Pillow 12.2 / GB10 against the stored scores' torch 2.2.1 / Pillow 10.2 / A100.
  No TT1 row was scored on the DGX, and no row of the DGX run is read (its gate scores are kept only as the record).
  No tolerance is amended.
- Platform (lead's decision): one rented A100-SXM4 80 GB (lease tt1a, `/mnt/t7/smad_next/vast/tt1a`, image
  pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime, the pn1b type), pip pins exactly as the PN1 hosts
  (`src/PN1/rented/remote_setup.sh`: timm 1.0.27, huggingface_hub 0.36.2, safetensors 0.8.0, numpy 1.26.4, pyyaml 6.0.3,
  pillow 10.2.0; torch held at 2.2.1), cap 3 USD, deadline 2.5 h. Same pack (`2109f742…`), network tar (`92bd1841…`),
  list, rescore.py and reader as pinned; everything else of TT1-S unchanged.
- Gate (byte-identity gate, applied to all 12 networks, gate rows scored first, gate.json, stop on failure):
  `src/TT1/gate_check_a100.py` `69f341014c43c5f988aa6ee9906efc93b3331ec5c4e4df31fbbcf961a169e578`:
  - the 3,000 FFHQ rows (R_ffhq 2,000 + M_ffhq 1,000), whose stored logits were produced by the same script
    (rescore.py) on A100s: byte identity, max |Δlogit| = 0 (float32);
  - the 417 R_cam rows: their stored logits come from pn1_score.py, which sets TF32 on (allow_tf32 = True; rescore.py
    leaves PyTorch's defaults) and scored the whole evaluation manifest in other batches, so bit identity is not
    expected there (stated now, before any A100 number): max |Δlogit| ≤ 0.02, zero own-rule changes, Kendall τ-b ≥ 0.99;
  - |ΔAUC(R_ffhq vs R_cam)| ≤ 0.002.
  On failure: result tar with rc GATE_FAILED, no TT1 row scored, RELEASE + FAILED after verification, lead told.
- Scripts: remote `src/TT1/rented/remote_tt1.sh` `dedc9f5c33976d5f6d29cd3190b9f9ee14a4ad1689d77bf35cf8696cb5b5467d` (pins, pip, extract, diagnostic, gate, TT1 rows, result tar);
  driver `src/TT1/rented/drive_tt1.sh` `b797cafe19d88a151da685c6fa6f1e0d23e0ddc228c8e0d1d5f9ea40bfd255c7` (rsync --partial upload, start, pull, sha256 of the result tar and of every
  log, second local copy in /mnt/t7/smad_next/TT1/results/, RELEASE only after both copies verify; RELEASE + FAILED
  on a verified failed gate; no decision on unreadable remote state; no RELEASE in test mode).
- Zero-GPU-budget diagnostic (lead's request; NOT a registered read, decides nothing): `src/TT1/diag_stack.py`
  `71e503bf372af6aeb09d1f4cf9a1487cbec77f15efc34dda80dca9f695660105` saves, for the 5 FFHQ genuine rows with the largest DGX-A100 gate differences for A_s401 (fq016604, fq010376,
  fq008900, fq008528, fq011276; chosen from the failed DGX gate), the decoded array, the resized array, the input
  tensor and the A_s401 logit on each stack (DGX output `/mnt/t7/smad_next/TT1/diag/diag_dgx.npz`, already computed;
  the A100 output comes back in the result tar). It answers which stage differs: decode, resize or network.
- Local test of remote_tt1.sh on the DGX (test mode, pip skipped) started before this commit; result in the README.

## 6. Deviation TT1-D2 (`date`: Fri Nov 13 12:35:01 AM CET 2026; registered at the git commit that adds this section, before any TT1 row is scored on any platform): batching of the gate rows

- Facts (commit 7a781f7, `gate_a100.json`): on lease tt1a (A100-SXM4 80 GB, torch 2.2.1, Pillow 10.2.0) the TT1-D1
  gate failed only on FFHQ byte identity, in all 12 networks: 16-25 of 3,000 FFHQ rows per network differ, by at most
  2.2e-5 logit; R_cam passed (max |Δ| 0.0014-0.035, 0 flips, Kendall 0.996-0.998); |ΔAUC| ≤ 2.6e-5. No TT1 row was
  scored. Probable cause: batch composition (the gate list put the 417 R_cam rows first, so the FFHQ rows fell into
  other batches of 64 than in the runs that produced the stored scores). tt1a was released by the lead's guard
  (0.56 USD).
- Fix (lead's decision, option b). The registered criterion stays (byte identity on the 3,000 FFHQ rows). The FFHQ
  rows are scored as in the runs that produced their stored scores: the HN2 list alone (`pn1_hn2.csv` sha256
  `4c0caa89ab25406854b6865c17943ef5e9532b0e5cc8bed58ad8e73d53b15871`, 5,000 rows, fam ffhq, original order,
  rescore.py batch 64; the amendment-14 list's ffhq rows are in the same order, checked), from
  `/mnt/t7/smad_next/TT1/tt1_hn2.tar`, rebuilt from the HN2 tree and byte-identical to the registered HN2 pack
  (sha256 `7648b15ac67798e7601e24b790e62ef86687949f9af0ac440065c2fcb6ac42a7`). The R_cam rows keep their
  tolerance criterion: their original run (pn1_score.py over whole evaluation manifests that contain benchmark rows)
  cannot be repeated under the 12 Nov ruling, and TF32 differs; they are scored in their own family (fam gate of the
  TT1 list). Order on the host: HN2 list for all 12 networks, gate family for all 12, gate decision, then the TT1 rows.
- Stated now: the TT1 rows themselves are scored in fixed batches whose composition is pinned by the list order
  (`tt1_score.csv` `c0055b51…`, fam tt1, batch 64). Last-bit differences between batchings (about 1e-5 logit, as
  measured on tt1a) are far below anything a registered read depends on. No tolerance is amended.
- If the gate fails again with matched batching: stop with RELEASE + FAILED and report; the lead decides.
- Scripts: `src/TT1/rented/remote_tt1.sh` `c1e11eef13ec550c8ace5d2d13080f6af5f2fd5f0abfb7c4756dc60003ebdc30`; `src/TT1/rented/drive_tt1.sh` `17ebdce5ebeb108ec2690bd95af08bffecb2923b7ca7cf67a2ad4d1c3a402909` (uploads tt1_hn2.tar too);
  `src/TT1/gate_check_a100.py` `a636ff6c474b250b92e026bf2f745b787162fb4f3430f74b48303f4c04ab0666` (`--require-hn2`: FFHQ logits from <net>__hn2.npz).
- Platform fact for the final read (zero-GPU-budget diagnostic, `diag_stack_compare.json`, not a registered read): on
  five FFHQ genuine images the decoded image, the resized image and the input tensor are bit-identical between the
  DGX stack (torch 2.12.1, Pillow 12.2.0, GB10) and the A100 stack (torch 2.2.1, Pillow 10.2.0); the A_s401 logits
  differ by 0.061-0.088. The DGX gate failure lies in the network computation on GB10 / torch 2.12, not in decode or
  resize.
- Lease tt1b: /mnt/t7/smad_next/vast/tt1b, A100-SXM4 80 GB, host 104.202.122.106 port 30463, cap 2.5 USD, 2 h.

## 7. Deviation TT1-D3 (`date`: Fri Nov 13 01:06:07 AM CET 2026; registered at the git commit that adds this section, before any TT1 row is scored; WRITTEN AFTER SEEING THE tt1b GATE NUMBERS): per-network gate, Bn_s401 excluded

- Written after the tt1b gate numbers were seen (commit e73ae50, `gate_a100_tt1b.json`). Lead's decision (option 1).
- The gate is applied per network. A network that fails any criterion is not scored on TT1 rows, and every read that
  needs it is printed "not available (failed platform gate)".
- Bn_s401 failed on tt1b (one camera row, ar1_000377, |Δ| 0.035 against 0.02; the stored camera logits were produced
  with TF32 on) and is excluded: it is gated and printed again on tt1c but never scored on TT1 rows. Bn is a
  printed-only arm, so no decision rule loses an input. Bn_s402 is printed alone and labelled "one seed".
- The eleven other networks passed every criterion on tt1b, with the FFHQ rows byte-identical.
- No tolerance, threshold or hypothesis text changes.
- The gate runs again in the same job on lease tt1c (same batching as tt1b: HN2 list alone, then the gate family). If
  any of the eleven fails this time: stop with RELEASE + FAILED and report (run-to-run instability; the lead then
  treats the camera criterion itself as unsound).
- Each lease's result tar has its own name (TT1_A100_<lease>_full.tar).
- Scripts: `src/TT1/rented/remote_tt1.sh` `528f81d37c95de2dbb927deca4ff7f52688eeced29cada1867152539e12b9058` (EXCL=PN1_Bn_s401; lease-named tar); `src/TT1/rented/drive_tt1.sh`
  `c37c68d19802c6679cf441f1ca4314e7caaa18d66500af70f658f9b02323dd26`; `src/TT1/gate_check_a100.py` `e0c268e6cd894ab9ef319c7395c7ab2ff4d965bde7ab6b2a42dc9c503fa794ef` (`--exclude`: excluded networks printed, outside the pass decision).
  Reader `src/TT1/tt1_read.py` gains `--exclude` (missing networks -> "not available (failed platform gate)" in
  TT-H1, TT-H4, TT-H5; the other seed printed alone); re-pinned, after its mock test, before any score is read.
- Lease tt1c: /mnt/t7/smad_next/vast/tt1c, A100-SXM4 80 GB, host 104.202.122.106 port 30099, cap 2.5 USD, 2 h.
- Reader re-pin under TT1-D3 (`date`: Fri Nov 13 01:06:37 AM CET 2026; before any TT1 score exists locally or is read): `src/TT1/tt1_read.py`
  `4546f520f63b48c33e6d313673314b6c0f778ddc81da02b22d356f8c6a87fb8f` (only change: `--exclude` handling; tested on mock scores with `--exclude PN1_Bn_s401`); table script
  `src/TT1/summarize_read.py` `61409b534b6fd7ccc0429deba145df7caf57aa778b108244edeffd9b21a50d5d` (formats the reader's JSON; no statistic). Run:
  `python -I tt1_read.py --scores <result>/scores --nets /mnt/t7/smad_next/TT1/nets_tree_s401402/tt1nets/nets --exclude PN1_Bn_s401 --out tt1_read.json`.

## 8. Amendments H-new-1, H-new-2, H-new-4 (`date`: Fri Nov 13 02:05:34 AM CET 2026; registered at the git commit that adds this section, BEFORE any of them is computed; zero GPU; development data only; from review REVIEW_TT1_20261113.md)

Post-result amendments: the TT1 scores and the review's numbers are known; each test is labelled post hoc in result.md.
Code: `src/TT1/hnew.py` (committed with the results).

### H-new-2: onset of A's storage cue (existing PN1 scores, no new score)
- Statement: A's storage cue switches on with enlargement; protocol B removes it.
- Data: each network's stored `scores_eval.npz` (12 networks of seeds 401/402, Bn_s401 included: these are stored
  PN1 scores, not TT1 scores). Pools (FS1 `pn1_eval.csv` rows, development only): development ladder R0 native (100)
  with its stored copies at 61.2 px and 112.7 px inter-eye distance (rows R0 strength 61 / 112, same hosts), and AF0
  development photos native (126) with their 61 / 112 copies. Enlargement to 132 px: 61.2 px = 2.16x, 112.7 px =
  1.17x (TT1: 1.7x and 3.5x).
- Read: paired median shift (copy minus native, same image) per network, pools pooled (226 pairs per strength); own-rule
  flag share of the copies.
- Disclosure: PN1 tier 1 already printed A's raw R0 -> R0_61 shift on the TEST ladder (+1.73 / +2.64); this
  amendment reads the development ladder and AF0 development photos, values not seen.
- Rule: falsified if, on either seed, A's paired median shift at 61 px ≤ B's + 0.1 logit. Printed: the 112 px shifts.

### H-new-1: missing high frequency (measurement only)
- Statement: A's 112 px response is a "missing high-frequency" cue; JPEG and capture noise in the packs partly mask
  it, which is why the packs score below the geometry-matched camera photos.
- Measurement (no image operation): variance of cv2.Laplacian (CV_64F) of the greyscale aligned 512 frame inside the
  fixed canonical face box rows 170:400, columns 170:342 (eyes at (190,210), (322,210)), for the 417 R_cam^geo112
  frames and the U_p frames of the four packs (19,631).
- Reads: median face-box Laplacian variance of geo112 and of the packs; per A seed, median A logit of geo112 minus
  median A logit of the packs (TT1 tt1c scores); OLS slope of A's logit on log face-box variance over packs + geo112
  pooled (printed).
- Rule: falsified if the geo112 median face-box variance ≥ the pack median AND geo112 scores more than 2 logits
  higher than the packs (median difference) on both A seeds. Otherwise "not falsified".

### H-new-4: trade between genuine flags and misses on development attack pools
- Statement: B's low TT1 flag rate trades against misses.
- Networks: the 10 networks with both seeds scored on TT1 (A, B, Sb, C, Bv x 401, 402).
- x = TT1 F̄ (registered R5, `tt1_read.json`).
- y = mean over three development attack pools of the own-rule miss share (logit ≤ 0), equal pool weights:
  (1) our landmark ladder R4 native morphs, development and test hosts, OpenCV-style and FaceMorpher (582 rows, fam
  ladder, rung R4, strength empty); (2) AF0 development u50 morphs (180 rows, fam af0, rung u50); (3) the OpenCV-style
  face splices S4 of the development splice rungs, development and test hosts (291 rows, fam splice, rung S4).
- Proof none is a benchmark: all three are our own builds from FRGC / colorFERET ladder hosts (`/mnt/t7/smad_next/AR1`,
  `/mnt/t7/smad_next/AF0`, PN1 splice builds), paths `eval/pn1/*` of the FS1 development pack (`pn1_eval.csv`
  `f0f29f22…`, whose builder asserts no benchmark row); the code asserts fam ∈ {ladder, af0, splice} and path prefix
  `eval/pn1/`. No FRLL, MAD22, MorDIFF, DiM, H1, FEI or sealed row.
- Score sources (stored, development): ladder and AF0 rows from each network's `scores_eval.npz`; splice rows from
  `scores_eval.npz` (Sb, Bv), `PN1_Brescore_s<seed>/scores_splice.npz` (B), amendment-14 `PN1_<arm>_s<seed>__splice.npz`
  (A, C).
- Read: Spearman ρ(x, y) over the 10 networks, with the exact permutation p-value printed.
- Rule: falsified if ρ ≥ 0; "supported" if ρ ≤ −0.6; otherwise "weak (not decided)". Two seeds per arm; no arm claim.

## 9. Amendment H-new-5 (`date`: Fri Nov 13 02:08:06 AM CET 2026; registered at the git commit that adds this section, before computing; a few minutes of DGX GPU; development rows only)

- Statement: the GB10 discrepancy comes from attention or reduced-precision kernels, not from decode or resize.
- Test (`src/TT1/diag_kernels.py`): A_s401 on the five diagnostic FFHQ genuine rows (fq016604, fq010376, fq008900,
  fq008528, fq011276), using the A100 input tensors from `diag_a100.npz` (bit-identical to the DGX ones), under six
  settings on the DGX stack: default; TF32 off (matmul and cuDNN); TF32 on; math-only SDPA attention; math-only + TF32
  off; math-only + TF32 on. Compared with the A100 logits.
- Rule: falsified if no setting brings max |Δ| over the five rows below 1e-3. Decides whether the DGX can ever be a
  scoring fallback (if falsified: no).

## 10. Registration TT1-FS (`date`: Fri Nov 13 07:18:42 AM CET 2026; registered at the git commit that adds this section; before any FS1 network is scored on a TT1 row)

- Text: `prereg_fs1_block.md` (15 FS1 networks A, B, Sb x 403-407 on the TT1 pools; per-network byte-identity gate on
  the 19,797 FS1 development evaluation rows with TF32 on; TT1 rows with rescore.py unchanged; 4-of-5-seed rules; F4
  limits; platform pins; no scoring beside the Sp fits: the job waits for the host's fit lock). Reader
  `src/TT1/tt1_read_fs.py` fe9f97401f3633c2947b23af685be5587e741ed97163d64810e971469f5b4a62 (mock-tested with one network missing: `tt1_read_fs_mock.json`).
- Pre-run check by the experiment-reviewer follows; fixes are registered as amendment lines before the job starts.

## 11. Registration TT1-X (`date`: Fri Nov 13 08:56:40 AM CET 2026; registered at the git commit that adds this section; nothing of it scored or read)

- Text: `prereg_x_block.md` (Sp seeds 403-405 on pn1fs after the main block, same per-network gate, printed only;
  SbM3 seeds 403-407: a read of MS1's existing L40S scores after the MS1 registered read, no new scoring). Pre-run check
  by the experiment-reviewer follows; fixes as amendment lines before any start.

## 12. Post-result items Z1-Z4 on the fresh seeds (`date`: Fri Nov 13 11:26:20 AM CET 2026; registered at the git commit that adds this section, before computing; zero GPU; development data only; review REVIEW_TT1_FS_20261113.md items 1-4)

All are written after the TT1-FS scores were read; labels: Z1 post hoc, Z2-Z4 descriptive. Code `src/TT1/zfs.py`
(committed with the results). Inputs: `tt1_read_fs.json` (TT1-FS), `tt1_read.json` (TT1 401/402),
`posthoc_review.json`, the stored FS1 `scores_eval.npz` in `/mnt/t7/smad_next/TT1/nets_fs/`.
- **Z1 (post hoc): flags against development misses on the 15 fresh-seed networks** (H-new-4 repeated). x = TT1 F̄;
  y = mean of own-rule miss shares (logit ≤ 0) over the three development attack pools of H-new-4 (FS1 `pn1_eval.csv`
  rows: ladder R4 native, OpenCV and FaceMorpher, dev and test hosts, 582; AF0 u50, 180; splice S4, dev and test
  hosts, 291; asserted fam in {ladder, af0, splice}, path prefix eval/pn1/), from each fit's stored scores_eval.npz.
  Printed: Spearman ρ(x, y) over 15 networks with a permutation p (200,000 permutations, default_rng(20261124)); per
  seed the B − A and Sb − B difference of y and of each pool's miss. Prediction: the trade is driven by Sb's lower
  splice misses, with no B-against-A trade. Rule: "B pays in misses" if B's y exceeds A's by more than 0.02 on at least
  4 of 5 seeds; otherwise "no B-against-A miss cost shown".
- **Z2 (descriptive): A's false-alarm rate against its storage sensitivity.** Within A at seeds 403-407: Spearman of
  F̄ with the geometry-112 flag share and with |ρ_LFW| (TT-H4 LFW ρ). Prediction ≥ 0.7; "not related" if < 0.3;
  otherwise "weak". Seeds 401/402 printed separately (other hosts; not pooled).
- **Z3 (descriptive): Sb's excess and CFP-sized borders.** Per seed, Sb minus B on the CFP-FF border-reference flag
  share (R_cam^border(cfp_ff) own-rule flags) and on R3(c) for CFP-FF. Prediction: Sb's border-reference flag share
  above B's on at least 4 of 5 seeds. "Not a border cue on CFP" if Sb − B ≤ 0.005 on at least 4 of 5 seeds; otherwise
  as observed. Also printed for the other six families.
- **Z4 (descriptive): B's FFHQ genuine flags against its TT1 flags.** Over B's seven seeds (401, 402 from tt1_read.json;
  403-407 from tt1_read_fs.json; two hosts, labelled): Spearman of R_ffhq own-rule flag share with F̄. "One seed-level
  instability consistent" if ρ ≥ 0.7; "not consistent" if ρ < 0.3; otherwise "weak".

## 13. Registration TT1-M (`date`: Fri Nov 13 01:47:43 PM CET 2026; registered at the git commit that adds this section; no MEDS score on the scoring platform)

- Text: `prereg_meds_block.md` (NIST SD32 MEDS frontal pool, 865 aligned images of 400 persons; 15 FS1 networks + 3 Sp
  printed; per-network byte-identity gate on the 3,417 TT1 fam-gate rows against pn1fs, on se1d after SE1_DONE_411; reads
  TT-M1 to TT-M4). Pre-run check by the experiment-reviewer follows.
