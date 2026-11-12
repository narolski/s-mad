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
