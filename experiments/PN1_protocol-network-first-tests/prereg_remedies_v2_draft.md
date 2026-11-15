# DRAFT v2 (not registered, nothing run): development-only remedy arms Sp and SbHI

Status:
- Replaces the stopped SbEQ and So sections of `prereg_remedies_draft.md`. Pre-run review `PRERUN_PN1_REMEDIES_20261112.md`, commit 4b424f2.
- For the author's decision and a further pre-run review.
- Frozen by commit before any FS1 tar is opened.
- Development marks only. No benchmark set is read anywhere.

Both arms run at seeds 403, 404 and 405 on the FS1 host (A100 PCIe 40 GB, kept after FS1), after FS1 ends. They are compared with the FS1 fits of Sb (seeds 403–407) on the same GPU.

**Plain limit (stated as the reviewer does).** None of these arms can fix threshold transfer to an unseen genuine source. They train on FRGC / colorFERET only; that needs multi-source genuine training (an author item) or a claim without a fixed threshold. Cross-source flags are printed only, and the expected result for them is null.

## 0. Zero-GPU check already done (note in prereg.md, fb818c4; `tier1/pairs_check.json`; training images only)

Medians for the B and Sb checkpoints, seeds 401 / 402, eval mode:
- Genuine pairs, |Δz|: 0.003–0.016. Each type: photo↔photo61 0.010–0.015, half↔half61 0.010–0.016, R0↔R2w 0.003–0.005.
- Genuine pairs, |Δcos| on the head input: 0.0006–0.0097.
- Morph pairs u50↔u50_61: |Δz| 0.006–0.012.
- Null pairs (a, a): 0 in eval mode.

Train mode (LoRA dropout on):
- Null pairs: |Δz| 0.007–0.024 and |Δcos| 0.005–0.009, as large as or larger than the eval-mode pair differences.

Pre-stated rule met: **the logit equality term is inert** (every median < 0.05). In train mode a pair term would mostly penalise dropout noise. These are training images, which the networks fit, so the differences are small partly by construction.

## (a) Arm "Sp": spliced positives without seam-matched negatives (review improvement 2; fixes F1–F5 of `PRERUN_PN1_SP_20261112.md`)

**Status.** Draft. Not registered, not run, pending the author's yes.

**Purpose (F4).** Sp tests whether the constituent-matched negatives (S0 seam-only and S3 same-person splices, removed together), rather than the spliced S4 positives alone, are what stop the network from flagging seam-matched genuine composites. Sp is Sb minus those negatives; it is not a reimplementation of SBI or SelfMAD.

**Must not be claimed:**
- anything about SBI or SelfMAD (Sp is not a reimplementation of SBI or SelfMAD);
- S0 versus S3 attribution;
- any benchmark, cross-source or MAD-performance effect;
- generalisation beyond the OpenCV splice engine and FRGC / colorFERET hosts.

Everything is labelled development, n = 3 seeds.

**Data read (lead's decision).** The development ladder and FFHQ only. The 191-host test ladder stays unread for remedy arms.

**Manifest.**
- train_Sp = the unique rows of train_Sb minus lad_S0 (156) and lad_S3 (156).
- It is re-balanced by the amendment-4 rule (`mkmanifests.balanced_strata`, unchanged).
- Size: 7,762 rows from 5,223 unique images. Strata, negatives / attacks: feret|native 1,550 / 372, frgc|native 1,714 / 604, feret|s61 392 / 166, frgc|s61 225 / 200.
- The S4 positives (124) and everything else of Sb are unchanged.
- Disclosure: with steps fixed at 6,250 × 256, each image repeats about 8% more in Sp than in Sb (7,762 against 8,386 rows).

**Predictions** (Sp against the FS1 Sb fit at the same seed, seeds 403–405):
1. At its own rule (logit > 0), Sp flags at least 10 percentage points more of the 100 development-ladder S0 images than Sb at the same seed, and at least twice Sb's share (Sp ≥ max(2·Sb, Sb + 0.10)). Shares are counted out of 100; the bounds are inclusive. Printed reference: B and Bv flag 0.00 of development S0 (Bv s401: S0 0.00, S4 0.04); Sb 401/402 flag 0/100.
2. Sp's raw development S0-vs-S4 AUC (field `auc` of D_ii, native OpenCV images, 100 vs 100) is at least 0.05 below Sb's at the same seed. Excess-over-floor3 and face-only AUC are printed only.

**Printed for both arms:** development S3 own-rule flags (Sb 401/402: 0.34 / 0.36), landmark_combined AUC, R1–R6, and the storage share (paired share rising).

**Reading (F2).**
- Supported if both predictions hold on ≥ 2 of 3 read seeds.
- Falsified if, on ≥ 2 of 3 read seeds, neither prediction holds.
- Otherwise "inconclusive, no claim".
- A seed is read only if both the Sp fit and the FS1 Sb fit at that seed are finite and complete. Infrastructure failures are re-run unchanged; non-finite runs are never re-run.
- With fewer than 2 read pairs the arm is "not read". With exactly 2 read pairs, "supported" or "falsified" needs both.
- All margins are inclusive. Ties count as meeting the bound.
- Under no effect, each margin is far outside seed noise: Sb's development S0 flags are 0/100 at both seeds, and its development S0-vs-S4 AUC is 0.9875 and 0.9927. So the chance of "supported" by luck is taken as negligible. This is stated, not computed.

**Operations and pins (F5).**
- Sp uses its own overlay: the FS1 pack plus train_Sp.csv and its regenerated SHA256SUMS only. The FS1 pack's train.py (`cbb2cbd1…`) is unchanged.
- Pins, written into the registration:
  - train_Sp.csv sha256 `cf386dc7aaaee5723e64010cadd742c21fed0236d34e52e65daabba33a5e6848`;
  - list script `src/PN1/mk_sp.py` `9c84daf62693733761332f5055f3872478d085bc5add4a3e829d368e875ddad2`;
  - overlay `pn1_overlay_sp.tar` `1c0d03f388834d59f293bdf2874b524c313948527ed646868ec3ebd7741a4bd9`;
  - pack `pn1_pack_sp.tar` = `cp pn1_pack_fs.tar` + `tar -Af pn1_overlay_sp.tar`, sha256 `76528f16c17aa017d43ca6e872b332907e2c3c857ed02ff545a83e0831340089`. It is assembled the same way on the FS1 host and checked against this pin; it is uploaded only if the check fails.
  - run.sh `6a23a7a4b3d22a9371e1a5929636c3e233952fe5f12846139dd4d703f3dcce02`, which adds "Sp" to the arm list; nothing else changed.
- The pack keeps build_pack_fs's assertion that it holds no FRLL, MAD22, MorDIFF, DiM, H1, FEI or sealed row. Its pn1_eval.csv is byte-equal to the FS1 pack's (`f0f29f22…`, checked), so the driver cannot score a benchmark row.
- Local smoke (20 steps, limit 8, arm Sp, seed 403): rc 0; the pack verified against its SHA256SUMS; train.csv = train_Sp.csv (`cf386dc7…`); pn1_eval.csv byte-equal.

**Cost.** 3 fits × about 75 min, about 3.8 A100-hours, about 1.7 USD at 0.44 USD/h.

## (b) Arm "SbHI": head-input consistency on Sb (review improvement 3)

**Loss.**
- L = BCE (unchanged) + λ · mean over a pair batch P of (1 − cos(f_a, f_b)), with f the L2-normalised head input.
- λ = 1.0 in cosine units, fixed a priori; no alternative value.
- The pair pass is in eval mode (no LoRA dropout). CLIP has no BatchNorm; gradients still flow to the LoRA weights. The main batch stays in train mode.
- Pair batch: 32 pairs per step, eq-bs 16 as the fallback if the smoke on the FS1 host exceeds 40 GB. Drawn uniformly with replacement by a torch.Generator seeded with the run seed. Both images of a pair get the same flip.
- P comes from both classes, existing training images only (pair CSV pinned):
  - photo↔photo61 (254);
  - half↔half61 (363);
  - u50↔u50_61 (366, morph);
  - R0↔R2w (156).
- Logged per step: the pair loss, ‖w‖ of the head, and a null pair (a, a) in eval mode, which must give 0.

**Expected size.** On trained Sb the eval-mode |Δcos| of these pairs is 0.0006–0.0097 (section 0), so the term may be nearly inert. A49 (`/home/narolski/mambamorph-code/experiments/A49_dinov3/`) used a paired processing-consistency term at λ = 1 on the same head type (L2-normalised feature → linear). Its primary failed: instability +0.0029 [−0.005, +0.011] (docs/PLANNING_RECORD.md:140). Registered expectation: a null result for cross-source transfer, and at most a small storage effect.

**Marks.** Against Sb's five fresh seeds 403–407 as the reference distribution.
- Deciding storage read, at sizes never trained (amendment 4):
  - Pools: development-ladder R0 → R0_112 (100 hosts) and AF0 validation photo → photo_112 (126).
  - Statistic per seed: s = |median paired logit shift| / SD of the native genuine logits, with the two pools pooled.
  - 61 px is printed only.
- **Primary.** Exact one-sided Mann–Whitney of SbHI's 3 values of s against Sb's 5, with SbHI lower. Pass if p ≤ 0.05; the smallest attainable p is 1/56 = 0.018, so all 3 must be below all 5. Ties count half.
- **Two-sided storage mark.** On each SbHI seed, s ≤ 0.1, or AUC(history-matched vs native, same pools) in [0.45, 0.55]. Required on ≥ 2 of 3 seeds. Inclusive bounds.
- **Non-inferiority.** landmark_combined AUC ≥ median(Sb's 5) − 0.03 on ≥ 2 of 3 seeds.
- **Reading.**
  - Supported if the primary, the two-sided storage mark and non-inferiority all pass.
  - Falsified if the Mann–Whitney p ≥ 0.5 (no shift toward smaller s).
  - Otherwise "inconclusive, no claim".
- **Printed only.** FFHQ own-rule flags and flags at the camera threshold; the FFHQ paired share rising; R1–R6; MAD-type reads on the ladder (face-only, face-blanked).

**Forks closed.**
- λ is fixed at 1, with no selection rule.
- An Sb reference seed that is missing or non-finite is dropped. With fewer than 4 Sb seeds, the primary uses the exact test for the remaining n, and is "not read" if n < 3.
- An SbHI seed that is missing or non-finite is dropped. With fewer than 2 read seeds, the arm is "not read".
- All margins are inclusive.
- P-c′ is not used; the storage marks above replace it.
- Disclosure: the marks were written knowing Sb's 401/402 storage shares (0.16 / 0.29) and the section-0 pair magnitudes.

**Operations (review F9).**
- train.py change of about 60 to 80 lines in Python 3.10 syntax: new flags `--hi-pairs CSV`, `--hi-w 1.0`, `--hi-bs 32`. Every new object sits behind `if a.hi_pairs`.
- Byte-identity test on CPU against train.py `cbb2cbd1…`: `--smoke`, random init, with the flags absent. The test requires identical logits and loss trace.
- A smoke on the FS1 host gives peak memory at hi-bs 32, with 16 as the pre-registered fallback.
- The FS1 host is kept. The new pack is assembled there from the FS1 pack plus a small overlay (changed train.py, pair CSV, train_Sp), and its sha256 is checked against the pin; there is no 8.75 GB re-upload.
- About 95 min per fit, because of the extra forward pass.

**Cost.** 3 fits × about 95 min, about 4.8 A100-hours, about 2.1 USD.

## Both arms on the FS1 host after FS1

- Sp first (no code), then SbHI: about 8.5 hours, about 3.8 USD, plus about 0.5 h for the overlay, smoke and byte test.
- Start about 06:30 on 13 Nov, end about 15:30 on 13 Nov.
- Needs: the author's approval of Sp (and of SbHI, or no loss arm), a pre-run review of this text, and a registration commit before any fit.
