# DRAFT: scoring registration of the threshold-transfer experiment (TT1)

Status: DRAFT for independent pre-run review. Nothing in this file is registered, and no TT1 image has been scored by any
network. Written after the pools were built (commit 3912ae4). The only network output computed so far in TT1 is an
8-row command test on FFHQ rows that were already scored (section 4.3). Development data only.

## 0. What this governs, and what no reading can claim

- It governs scoring the 12 existing networks of the protocol network first tests (PN1), seeds 401/402, arms A, B, Bn,
  C, Sb, Bv, on the TT1 genuine pools and on reference pools. Later it also governs the 16 fresh-seed networks of
  registration FS1 (A, B, Sb x 403-407 + replicate A 401), as a separate block (section 9).
- Development reads only. None of the TT1 sources is a benchmark of the sprint. FRLL, MAD22, MorDIFF, DiM, H1, FEI,
  CASIA-WebFace and the sealed sets are not touched. The reference pools are PN1 development rows (FRGC / colorFERET
  held-out persons, FFHQ).
- No reading can claim the following:
  - Any miss rate or morph detection. There are no morphs of these sources, so this is a false-alarm test only.
  - That a network "works" on a source. A low flag rate is only a low false-alarm rate.
  - A cause of a source effect. Source is confounded with capture device, conditions, compression, crop and the
    preprocessing of each pack.
  - A separate effect of enlargement. It is identified only weakly: about 1.7x in all anti-spoofing sets and about
    3.5x in all packs, with narrow ranges inside each group (`pools_summary.md`). So the between-group difference is
    confounded with "video frame vs web photo".
  - Any benchmark or generalisation statement.

## 1. Networks (fixed)

Result tars in `/mnt/t7/smad_next/PN1/results_rented/` (sha256):

| Tar | sha256 |
|---|---|
| A_s401 | 59696efdcf711381f28f3e083c8000552f3d4f95eea477ef8781eff9cb1ecda5 |
| A_s402 | 24ed27449a9a3531c9f7e6a1f35c7d7bb09c834f904a337d1f95c4f33f2c7731 |
| B_s401 | 343148a70d960dddf00a4455c9da9b130632fd9d4e8ea1c08ae521f891f40c6e |
| B_s402 | 461a54431af8a91f6dba372ec2139ec86234651a21d317a3c5424477d68d5f76 |
| Bn_s401 | 194841842c1d70c23e06c090c122268a2a4dd659aeef9cb33c9553335266207f |
| Bn_s402 | 8eda3a619445b331dc0974b439cfe8e595f164c5bb3ce8f688c984b10f03f78f |
| C_s401 | fbe4f2a395ccda4446a8e48b348cefc878fdad558e62c15268ecebf3a8a808aa |
| C_s402 | d6372e42c55c915a9122e11b2f54257cd5b1125f3423b8d39ddb3d56bfc2c6bb |
| Sb_s401 | ea96a20e9a90b38bd150f28b006d25c0e1de267e1de74320379014f76ce84eb2 |
| Sb_s402 | d2e5214683a3a6dc28de0d26ff8f6c3175d0d14942697791f659688804776d75 |
| Bv_s401 | 49ab0c0d8774130931f4853bf003ac4c8684ab7a91be73f88eef15bac58d99e2 |
| Bv_s402 | ca5eb37665028970471e9d23bcba1336b418acf36bcd3aeed304b0a756b1f52f |

- Each network is rebuilt from meta.json + last_trainable.pt on the PN1 pack code and base weights, through
  `src/PN1/rescore.py` unchanged (sha256 `6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e`).
- The score is the logit without flip averaging. Own rule: flagged if logit > 0.
- Last checkpoint, every network, no selection, no ensembles.
- Arm roles for the author's question: A = plain, B = protocol, Sb = protocol plus spliced positives (primary three).
  Bn (equal-size protocol), C (protocol plus JPEG copies) and Bv (volume control of Sb) are printed and enter no
  primary comparison.

## 2. Pools (fixed; images exist, built in commit 3912ae4)

Unseen genuine pools U. Manifests `/mnt/t7/smad_next/TT1/raw_manifest.csv` (`a7aebe16…`) and `aligned_manifest.csv`
(`8b3c6fa9…`).
- **Primary pool U_p.** aligned = 1 AND the enlargement lies in a plausible band for the crop: [1.2, 2.5] for the
  224 px anti-spoofing frames, [2.5, 5.0] for the 112 px packs.
  - The band excludes 54 aligned frames whose detection is implausible, e.g. a tiny background face: LFW 40, CALFW 9,
    CFP-FF 1, AgeDB 4. The owner viewed one of them (enlargement 35x): a wrong detection.
  - The band was fixed from the manifests before any score.
  - Counts: Replay-Attack 200, MSU-MFSD 65, OULU-NPU 989, CASIA-FASD 150, LFW 5,995, CALFW 4,978, CFP-FF 4,725,
    AgeDB 3,933 (21,035).
- **Secondary pool U_all.** All 25,241 frames, including prep_eval's plain-resize frames (aligned = 0). Printed for R1
  and R3 only.
- **Families.** replay_attack, msu_mfsd, oulu_npu, casia_fasd, lfw_calfw (LFW + CALFW pooled), cfp_ff, agedb_30: 7
  families, 8 sources. Family-level statistics weight the families equally. LFW and CALFW are printed separately but
  count once.
- **Persons.** Anti-spoofing sets: file-name person id. Packs: pseudo-identity = connected component of "same" pairs.
  - Components split true identities: CFP 1,586 components for 500 people, AgeDB 2,338 for 568.
  - LFW and CALFW components never merge across the two packs, although the people overlap.
  - So for the packs, a bootstrap over pseudo-identities is anti-conservative. Every pack interval is labelled
    "pseudo-identity bootstrap (anti-conservative)". The family-level decisions below need agreement on both seeds and
    across families, not one interval.

Reference pools (rescored in the same run and on the same platform as U; reads use only this run's logits):
- **R_cam: training-source camera photos of held-out persons, 417 native images.** FRGC / colorFERET:
  - development ladder R0 native: 100;
  - test ladder R0 native: 191;
  - AF0 development photos native: 126.
  These are the strength-empty rows of `/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv` (`f0f29f22…`).
  Persons = host column.
- **R_ffhq.** FFHQ genuine `ffhq_bona orig`, 2,000 images (HN2 list `pn1_hn2.csv` `4c0caa89…`). Each image is its own
  person.
- **M_ffhq.** FFHQ landmark_complete orig morphs, 1,000 (the same list, label 1). Used only to set the scale unit u
  (section 5), never read as detection.
- **R_cam^border(f) and R_ffhq^border: border-matched references.** Built with constant-colour region blanking, an
  allowed operation; no other image operation. Not yet built.
  - For each of the 417 R_cam images and each of the 7 families f, take the black mask of one U_p frame of family f.
    The mask is the pixels whose maximum over channels is 0. The frame is drawn with
    `numpy.random.default_rng(20261121)` in a fixed order (families in the order above, images by id). The masked
    pixels of the reference frame are set to (0,0,0). Result: 2,919 images.
  - R_ffhq^border: each of the 2,000 R_ffhq images gets one mask, drawn from all U_p frames with the same generator
    after the R_cam draws. Result: 2,000 images.
  - All reference frames share the canonical eye positions with U, so a mask transfers without any warp.
  - Script: `src/TT1/build_border_ref.py` (to be written, tested on 8 images, and pinned with the registration);
    lossless PNG; `/mnt/t7/smad_next/TT1/border_ref/`.
  - Caveat, stated now: blanking adds black and also removes the reference photo's own surround (hair, background,
    shoulders).

Scoring list: `tt1_score.csv` in PN1 manifest format, fam "tt1". About 33,577 rows: U_all 25,241, R_cam 417, R_ffhq
2,000, M_ffhq 1,000, border references 4,919. Built by `src/TT1/build_list.py` from the manifests above; its sha256 is
committed with the registration.

Fixed strata: `strata_edges.json` (sha256 `4aa95f038397bd45b4446e59b3c696b03e091d042c2bfd5ff99d423fe0fdb798`; script
`src/TT1/strata.py` `97ac2c60…`; computed from the manifests, aligned frames, before any score):
- sharpness quintile edges per pack and for the anti-spoofing sets pooled;
- enlargement and border-share quintiles over all aligned frames.

## 3. Thresholds

- **τ_0.5, the network's own rule (logit > 0).** Primary and the only deciding threshold.
- **τ_cam, printed only.** The network's tier-1 camera-photo threshold:
  - A, B, Bn, C: from `tier1/<arm>_s<seed>.json` "thresholds.cam".
  - Sb, Bv: the same rule (5% of development ladder R0 native and of AF0 validation photos above it; the larger of the
    two pool thresholds) applied to their stored `scores_eval.npz`.
  - Every τ_cam column carries the label "saturated band (head bounded at about ±3.87; review REVIEW_PN1_TIER1)".
- No new calibrated threshold is fitted in TT1. Multi-source calibration belongs to the multi-source training set
  experiment (MS1).

## 4. Platform, gate, cost

### 4.1 Recommended: the DGX (GB10), with an equivalence gate

Rationale:
- 0 USD, and no upload.
- Every TT1 read uses logits from one run on one platform.
- The gate only ties the run to the A100 scores on which PN1's own numbers rest.

Gate G-DGX, run first, on R_cam (417), R_ffhq (2,000) and M_ffhq (1,000), for all 12 networks:
- Compare with the stored A100 logits: R_cam from each network's `scores_eval.npz` (field logit); FFHQ from
  `PN1_HN2_s<seed>/scores_hn2_<arm>.npz` (A, B, Bn, C) and `results_a14/unpacked/PN1_A14/PN1_<arm>_s<seed>__ffhq.npz`
  (Sb, Bv).
- Pass, for every network, all of:
  - max |Δlogit| ≤ 0.02 over the 3,417 rows;
  - own-rule decision identical on every row;
  - |ΔAUC(R_ffhq vs R_cam)| ≤ 0.002.
- If any network fails, no DGX score of any network is read. The run moves to the rented A100 (4.2) unchanged, and
  the failure is reported with its numbers.
- The gate statistics are written before the U rows are scored. The script scores the gate rows first, writes
  `gate.json`, and stops unless every network passes.

Process: one GPU process, `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n
10`, 2 loader workers, Python `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`, with:
- `SMAD_DATA=/mnt/t7/smad_next/TT1/score_root/data`: symlinks to the aligned PNGs, the PN1 fs_tree eval files, the HN2
  files and border_ref;
- `HF_HOME=/mnt/t7/smad_next/PN1/fs_tree/pn1/hf`, `HF_HUB_OFFLINE=1`;
- `--code /mnt/t7/smad_next/PN1/fs_tree/pn1/code`.

Driver: `src/TT1/score_dgx.sh`, to be written and pinned. It loops over the 12 networks, calls rescore.py unchanged
with `--manifest tt1_score.csv --fam <gate|tt1>`, and writes `/mnt/t7/smad_next/TT1/scores/<net>__<fam>.npz` with
sha256.

Cost: about 33,577 images x 12 networks ≈ 403,000 forward passes on a shared GB10. The throughput at 512 px PNG decode
with 2 workers is not measured; at an assumed 120-200 images per second that is 35-55 minutes of GPU time. This exceeds
OWNER_BRIEF's half-hour guideline, so the lead decides. Athena is not usable (forecast December).

### 4.2 Alternative: one rented A100 40 GB, with the byte-identity gate (the PN1 rescoring pack approach)

- Pack `/mnt/t7/smad_next/TT1/tt1_pack.tar`, built by `src/TT1/build_pack.py` (to be written):
  - code + hf from PN1 pack 2, hash-checked;
  - the 12 networks' meta.json + last_trainable.pt;
  - all scoring images;
  - `tt1_score.csv` and `SHA256SUMS`.
  About 5.5 GB. The builder asserts that no row of a benchmark set is in it.
- Gate G-A100, as amendment 14: A_s401 and B_s402 on the 3,000 HN2 rows (R_ffhq + M_ffhq). Required: max_abs = 0 and
  ΔAUC = 0 against their pn1a / pn1b scores. If it fails, nothing is read and the lead is told.
- Cost: upload about 5.5 GB at the 3 MB/s measured on 12 Nov (about 30 min), setup about 10 min, scoring about 20 min.
  About 1.2 h at about 1 USD/h, so about 1.2 USD; guard cap 3 USD, deadline 3 h.
- The one command for the lead, after the pack and driver are pinned (same pattern as `src/PN1/rented/drive14.sh`):
  `bash /home/narolski/smad-next/src/TT1/rented/drive_tt1.sh <HOST> <PORT> /mnt/t7/smad_next/vast/tt1 start`, then
  `... pull` / `... loop`.
- The remote side keeps nothing that is not regenerable: inputs are local; scores come back in one tar with sha256.
  RELEASE only after the tar is verified locally.

### 4.3 Command test already done (no TT1 image)

- `date` Thu Nov 12 11:12:09 PM CET 2026, DGX: `rescore.py` unchanged scored A_s401 on 8 FFHQ bona fide rows that were
  already scored by pn1a.
- Max |Δlogit| against the stored A100 logits: 0.0015. Files: `/mnt/t7/smad_next/TT1/dgxtest/`.
- This shows only that the DGX path runs. It is not the gate.

## 5. Reads (per network; every number printed for every network; U_p unless stated)

Bootstraps: 2,000 draws, `numpy.random.default_rng(20261122)`. Persons are resampled within each source (U) and
within R_cam (host); R_ffhq images are resampled individually. The same draws are used for every network, so arm
differences are paired.

- **R1. Own-rule flag share per source and per family.**
  - 95% Clopper-Pearson interval (images) and person-bootstrap interval.
  - U_all printed beside it.
  - Also printed: R_cam and R_ffhq at the own rule, and every share at τ_cam (labelled).
- **R2. Logit location per source.** Median logit, interquartile range and the shift of the median from R_cam's
  median, in raw logits and in units of u. u = median logit(M_ffhq) − median logit(R_cam), per network. u is printed;
  if u < 1 logit, R2 and R4c are printed with the label "unit degenerate".
- **R3. Scale-free placement.** AUC with the source higher counting as above:
  - (a) U_s against R_cam;
  - (b) U_s against R_ffhq;
  - (c) U_s against R_cam^border(f(s));
  - (d) R_ffhq^border against R_ffhq, a border-only effect on one source.
  Person-bootstrap intervals.
- **R4. Sharpness, enlargement, border and source.**
  - (a) **Within-pack natural experiment** (fixed 112 px, enlargement about 3.5).
    - In each of the four packs: Spearman ρ of logit with log lap_var.
    - Own-rule flag share and median logit per fixed sharpness quintile (`strata_edges.json`).
    - Person-bootstrap intervals.
  - (b) **Anti-spoofing sets** (fixed enlargement about 1.7, 30-fold sharpness range).
    - The same per pooled quintile.
    - Per source: flag share and median logit against its median lap_var. With 4 points, only the order is printed:
      Spearman over 4 sources, no test.
  - (c) **Leave-one-family-out (LOFO) covariate model.** OLS of logit on four covariates: z(log enlargement),
    z(log lap_var), border_frac, greyscale.
    - Fitted on the U_p images of the other 6 families, each family weighted equally.
    - It predicts the held-out family's mean logit; prediction error e_f = observed − predicted mean logit, in units
      of u.
    - Logistic regression on the own-rule flag with the same covariates (sklearn LogisticRegression, C = 1e6,
      max_iter 5000, equal family weights) gives the predicted flag share. Printed beside e_f; it does not decide.
    - Interval of e_f: the person bootstrap, refitting the model in every draw.
  - (d) **Source beyond covariates, all families.** The same OLS with family indicators added.
    - Printed: the share of between-family variance of family mean logits that the covariates explain.
    - Printed: each family's indicator coefficient with its person-bootstrap interval, in units of u.
- **R5. Arm summary (the author's question).** For each network:
  - F̄ = mean over the 7 families of the own-rule flag share;
  - F_max = largest family flag share;
  - S_F = standard deviation of the 7 family flag shares (uniformity);
  - Ā = mean over families of R3(a);
  - S_A = standard deviation of R3(a) over families.
  For the pairs B − A, Sb − A and Sb − B within seed: paired bootstrap intervals of ΔF̄, ΔF_max, ΔS_F, ΔĀ, ΔS_A.

## 6. Hypotheses, predictions, falsifiers (fixed before any score)

An arm verdict needs both seeds; one seed one way and one the other way is "mixed". The 401/402 seed spread of the
reference recipe exceeds most arm effects (review Q5), so all arm statements are "on seeds 401/402" only.

- **TT-H1. The own rule does not transfer to unseen sources.**
  - Family f fails for a network if the lower Clopper-Pearson bound of its own-rule flag share is above 5%.
  - Prediction: A fails in ≥ 4 of 7 families on both seeds; B and Sb fail in ≥ 2 of 7 on both seeds.
  - Falsified for an arm ("the own rule transfers on these sources") if on both seeds every family's upper bound is
    ≤ 10%.
- **TT-H2. Unseen genuine photos sit above the training-source floor even when not flagged.**
  - Prediction: R3(a) ≥ 0.90 for ≥ 6 of 8 sources, for every network.
  - Falsified for a network if R3(a) ≥ 0.75 holds for ≤ 3 sources.
- **TT-H3. The alignment border carries part of the separation.**
  - "Border material" for a network if R3(c) ≤ R3(a) − 0.10 for ≥ 4 of 7 families, AND R3(d) ≥ 0.65.
  - "Border not material" if |R3(c) − R3(a)| ≤ 0.03 for ≥ 6 of 7 families AND R3(d) ≤ 0.55.
  - Otherwise "inconclusive".
  - Prediction: A "border material" on both seeds; no prediction for B, Sb (printed).
- **TT-H4. Softer photos score higher at fixed size.**
  - Prediction for A: ρ(logit, log lap_var) ≤ −0.15 in ≥ 3 of 4 packs on both seeds.
  - Prediction for B and Sb: |ρ| smaller than A's in ≥ 3 of 4 packs on both seeds (the protocol trains stored-small
    copies as genuine).
  - Falsified for an arm if ρ ≥ 0 in ≥ 3 of 4 packs on both seeds.
- **TT-H5. Covariates versus source** (the author's question: does the false-alarm rate follow sharpness and
  enlargement, or the source?).
  - "Explained by covariates" for a network if |e_f| ≤ 0.10u for ≥ 6 of 7 families.
  - "Source matters beyond the covariates" if, for ≥ 2 families, |e_f| ≥ 0.20u and the bootstrap interval of e_f
    excludes the band [−0.10u, +0.10u].
  - Otherwise "inconclusive".
  - Arm verdict: both seeds agree.
  - Prediction: "source matters" for A on both seeds, because capture differences beyond these four covariates
    (compression, video-frame noise, crop) are expected to move a softness reader.
  - The other branch is a real possibility, so it is not called a falsifier of the method. Whatever the result, the
    only claim allowed is "given these four covariates", because enlargement is weakly identified (section 0).
- **TT-H6. Arms (primary pairs B − A, Sb − A, Sb − B).**
  - "X has lower genuine flag rates than Y" if on both seeds ΔF̄ = F̄_X − F̄_Y ≤ −0.03 and its paired bootstrap
    interval excludes 0.
  - "X is more uniform than Y" if on both seeds ΔS_F ≤ −0.02 with interval excluding 0, AND ΔS_A ≤ −0.02 with interval
    excluding 0.
  - The scale-free version uses ΔĀ ≤ −0.03 with interval excluding 0. It is printed beside the result and decides
    nothing alone.
  - Otherwise "not distinguished on seeds 401/402".
  - Prediction: B and Sb lower than A, and Sb not distinguished from B.
  - Falsified (prediction wrong) if A is lower than B on both seeds by the same rule.
  - "Lowest and most uniform arm" is named only if one arm is lower AND more uniform than both others by these rules;
    otherwise "no arm is both lowest and most uniform".

## 7. Guards and rules

- No detector may gate on resolution, file size, format or source. The pools are scored whole; U_p is an analysis
  pool fixed above.
- No seed, network, threshold or pool is chosen after scores. Bn, C and Bv decide nothing.
- No re-run after seeing scores, except an infrastructure failure re-run unchanged (logged).
- Reader `src/TT1/tt1_read.py`, to be written. It is tested on random mock scores only and committed with its sha256
  before any score file exists.
- The gate (section 4) is computed before any U row is scored.
- TT1 sources stay development data. If the method is later frozen, they are not reported as a benchmark.

## 8. Stop rule and budget

- DGX: one GPU process, at most 1.5 h wall time for the 12 networks; stop and report if the GB10 is needed by a
  higher-priority job (lead).
- Rented route: cap 3 USD, deadline 3 h from the lease start. The driver writes RELEASE only after the result tar is
  verified locally.

## 9. Fresh-seed networks (FS1), later block

- The 16 FS1 networks are scored with the same list, platform rule and gate once all 16 tars are verified in
  `/mnt/t7/smad_next/PN1/results_fs/`. FS1's own registered reads are computed and committed first; TT1 does not
  touch FS1's verdicts.
- Same reads. TT-H6 is evaluated per seed (403-407); an arm statement there needs ≥ 4 of 5 seeds in the same direction.
- The replicate A 401 is printed as "platform plus nondeterminism" against A_s401 and enters no rule.
- Pins (tar sha256 from FS1's `fs_kept/`) are added in a short amendment before that block is scored.

## 10. Before this becomes a registration

1. Independent pre-run review of this draft; findings applied.
2. Write and test, on 8 rows, `build_border_ref.py`, `build_list.py`, `score_dgx.sh` (or the rented pack / driver)
   and `tt1_read.py` (mock scores).
3. Commit the registration with every sha256 (list, scripts, reader) and `date`. Then the gate, then the scores.
