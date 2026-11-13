# Regional identity disagreement (RI1): registration

Owner: PR1/BD1 owner agent (Opus), on the lead's assignment of 13 Nov 2026. It is built from the IDEAS test draft
`experiments/IDEAS_mechanism-ledger/TEST_regional-identity.md` at commit c17ac7d (sha256 `f61b71a9…`; ledger entry
M1). Registered at the git commit that adds this file. Before that commit, the only computations were:
- an 8-image code test of `src/RI1/ri1_embed.py` (`emb_rows_0of1_limit8.npz`, not looked at);
- a mock run of the reader with random embeddings. The mock printed the cue-only 27-statistic floors on real cues:
  R4 vs R3, S4 vs S3 and R4 vs R0, with R4 vs R0 at about 0.93.

No real embedding of the full sets exists. Development data only. Nothing enters the frozen method (Sb, seeds 403-407).

**Lead's ruling (13 Nov, verbatim in substance).** "Blanking regions of the already-aligned 112 px face-recognition
crop with a constant colour, in memory, is the allowed constant-colour blanking. No blanked image is stored as data or
fed to training."

## 1. Question and hypothesis

- **H-RI1.** A two-person morph carries identity evidence that differs between face regions. Frozen face-recognition
  embeddings of occluded versions of one image therefore disagree more, and lean towards different contributors, than
  for a genuine photo, a same-person morph or splice, a stored-small photo, a warp-only image or a seam-only image.
- This is the first direct single-image test of a second-identity mechanism (M1). No training is involved.

## 2. Rows (development only)

- **Ladder and splice rows.** The 291 hosts of BD1 (191 test, 100 development) from the FS1 evaluation list
  (`pn1_eval.csv` `f0f29f22…`, the frames the networks see): R0 (camera photo), R0_61 (stored small), R2w4
  (warp-only, two-person geometry), R3 (same-person morph), R4 (two-person morph), each OpenCV-style; FaceMorpher R2w4,
  R3 and R4 printed; splices S0, S3, S4. That is 3,201 images.
- **Sources** from `AR1/pool.csv`: H (host photo), S (host's second photo), B (partner photo), R (independent host
  photo). 948 unique photos.
- **FFHQ development genuine photos:** the first 1,000 `ffhq_bona_orig` rows of the FS1 list by id, used as the
  reference distribution only. The draft's 2,000 is reduced to 1,000 for CPU time.
- **Border control: dropped.** No clean border-blanked camera set exists among these rows; the ladder frames share
  the aligner's border. Stated as not tested.
- **Closed:** everything in OWNER_BRIEF. No valx, FST or A12SP file.

## 3. Measurement (`src/RI1/ri1_embed.py`; platform: DGX CPU, one platform for every RI1 embedding)

- **Route.** `prep_eval.kps` unchanged (its detector object is a CPU insightface FaceAnalysis, buffalo_l detection,
  det_size 512: the same model and size). Then insightface norm_crop to the 112 × 112 ArcFace crop. Then glintr100.onnx
  via insightface ArcFaceONNX.get_feat on onnxruntime CPU.
  - The CUDA session swap of `a2f_common` is not used, because the DGX GPU is busy. Embeddings therefore differ in the
    last digits from the GPU-made AR1 embeddings, which are never mixed in.
  - Keypoints come from the unoccluded image.
- **Occlusion patterns.** 8 patterns, grey 128, as integer slices of the crop around the template points:
  - left-eye, right-eye, nose and mouth boxes;
  - upper and lower halves, left and right halves;
  - the boxes are fixed in the code (`BOXES`).
- **Per image:** e_0 (unoccluded) and e_1..e_8, L2-normalised. No image is written.

## 4. Gate G0 (before any contrast)

- Verification AUC per pattern k: cos(e_k(R0_h), e_0(R_h)) for the same host, against cos(e_k(R0_h), e_0(R_g)) for
  other hosts g of the same database.
- A pattern with AUC < 0.90 is dropped. Fewer than 5 patterns left: RI1 stops with "face-recognition regions too weak
  to test".

## 5. P1 oracle premise (uses the known sources; not a detector)

- **Leaning.** For R4: L_k = cos(e_k, emb(H_src)) − cos(e_k, emb(B_src)). For R3: L_k = cos(e_k, emb(H_src)) −
  cos(e_k, emb(S_src)).
- **Spread.** V = SD over the kept patterns of (L_k − L_0), divided by the mean of (1 − cos(e_0, src)) over the two
  sources.
- **Read.** AUC(V_R4 > V_R3), paired by host, 2,000 host-bootstrap draws (`default_rng(20261161)`).
- **Pass:** AUC ≥ 0.70 with a lower bound > 0.62. **Kill:** AUC ≤ 0.60. Otherwise inconclusive.
- **Printed:** V without the divisor; V with the independent photo R in place of H_src (the draft's bias check).

## 6. S1 single-image statistic

- **Dispersion.** Δ = mean over pairs of kept patterns of (1 − cos(e_j, e_k)), z-scored on the FFHQ reference.
- **Signal contrasts** (AUC, paired by host, bootstrap): R4 vs R3; S4 vs S3, also within the five BD1 D quintiles with
  BD1's pure-D reference printed; R4 vs R0.
- **Controls that must stay ≤ 0.60:** R0_61 vs R0 (storage), R2w4 vs R0 (warp to two-person geometry), S0 vs R0
  (seam). R3 vs R0 is printed with no bar. FaceMorpher R4 vs R3 and R2w4 vs R0 are printed.
- **Floor.** The best single statistic of the 27-statistic set on the same rows, direction-free, chosen on one host
  half and scored on the other (mean of both halves); for R4 vs R3, S4 vs S3 and R4 vs R0. The ADVERSARY floor (lead to
  coordinate) is added beside it when published. The read waits if ADVERSARY announces it as pending.
- **Increment.** S4 vs S3 over all 291 hosts, per Sb seed 403-407 (stored development scores). Cross-fitted logistic
  regression in 5 host folds (`default_rng(20261163)`), [Sb logit, Δ] against [Sb logit].

## 7. Outcome table (fixed now; from the draft, unchanged)

| P1 | S1 signal | S1 controls | Reading | Next |
|---|---|---|---|---|
| ≥ 0.70 | R4/R3 and S4/S3-within-D ≥ 0.65 | all ≤ 0.60 | regional identity disagreement exists and is readable in one image | if the increment is ≥ +0.03 on ≥ 4 of 5 seeds: an identity-consistency arm may be registered (post-freeze ablation) |
| ≥ 0.70 | < 0.65 | — | the premise holds but glintr100 occlusions are too coarse to read it | a trained region encoder only if the paper needs it |
| ≤ 0.60 | S4/S3 ≥ 0.65, R4/R3 < 0.60 | all ≤ 0.60 | splice-only mechanism | an arm limited to spliced attacks |
| ≤ 0.60 | < 0.60 | — | no regional identity disagreement measurable | M1 closed |
| any | any | a control > 0.60 | the statistic reads the nuisance | closed unless stratifiable |

Any other combination is "inconclusive (no row of the outcome table)".

## 8. Code, cost, run

- `src/RI1/ri1_embed.py`, `src/RI1/ri1_read.py`; pins in `src/RI1/SHA256SUMS`. The reader was tested on mock
  embeddings only.
- Cost: about 46,000 crops on the CPU at about 6.6 crops/s per 2-thread process, run as 2 processes. About 1 hour; 0 GPU.
- Commands (run once, after the pre-run check fixes):
  - `OMP_NUM_THREADS=2 nice -n 10 .venv-spark/bin/python -I src/RI1/ri1_embed.py rows --shard 0/2`, then `--shard 1/2`;
  - the same for `sources` and `ffhq`;
  - then `ri1_read.py --out experiments/RI1_regional-identity-disagreement/ri1_read.json`.

## 9. Risks (from the draft)

- B_src and S_src are the very photos blended in. The bias is balanced between R4 and R3 and also printed with R.
- The keypoints of morphs sit at the mean geometry; the same holds for R2w4, which is a control.
- FR networks are robust to occlusion, so a small Δ may reflect robustness. G0 bounds this only partly.
