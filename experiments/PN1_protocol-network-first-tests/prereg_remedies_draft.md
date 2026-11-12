# DRAFT (not registered, nothing run): two development-only remedy arms after FS1

Status: this is for the author's decision and a pre-run review. It follows the review of amendment 14
(`REVIEW_PN1_A14_DEVREAD_20261112.md`, commit 7e68455), sections 5 and 6.
- Development marks only. No benchmark set is read anywhere.
- Temperature or Platt scaling is dropped: a monotone map cannot change a quantile threshold.
- Both arms would run after FS1, on the FS1 GPU type (A100 PCIe 40 GB), at seeds 403, 404 and 405. They are compared with the FS1 fits of A, B and Sb at the same seeds on the same GPU type, so no new A, B or Sb fit is needed.

## (a) Equality-term arm (H-new-4)

### Arm

**Recommended: on top of Sb ("SbEQ").**
- Sb is the lead candidate.
- Sb already has the lowest storage reaction (paired share rising 0.16 / 0.29) and the lowest own-rule FFHQ genuine flags (5.9 / 7.0%).
- The open problem is threshold transfer, which these marks test.

A "BEQ" arm on top of B is the alternative. It would isolate the term's effect from the spliced positives. It costs the same and could run instead or as well, which is the author's choice.

### Pairs

The pairs come from existing training images of the arm's manifest; no image is built. Each is a genuine (negative-class) image and its stored or warp-only copy of the same person:
- af0_photo ↔ af0_photo61: 254 pairs;
- af0_half ↔ af0_half61: 363 pairs;
- ladder R0 ↔ ladder R2w (the warp-only copy of the same host): 156 pairs.

That is 773 pairs from training persons only. The pair list is a CSV of path pairs, pinned by sha256.

### Loss

L = BCE (unchanged) + λ · mean over a pair batch of (z(a) − z(b))², where z is the network logit.
- Pair batch: 32 pairs per step, drawn uniformly with replacement by a torch.Generator seeded with the run seed. Both images of a pair get the same flip.
- The pair images go through the same model in train mode, in a second forward pass per step.
- Steps (6,250), batch size (256), recipe and optimiser are unchanged.

### Weight

λ = 1.0, chosen once and never tuned on FFHQ. Justification on the logit scale:
- The BCE gradient per example is bounded by 1.
- A storage shift of about 1 logit gives a penalty of about 1 per pair, so the term matters when a pair is about one logit apart.
- It is negligible below about 0.3 logits. B's mean shift R0 → R0_61 is 0.11 to 0.22 logits, A's 1.7 to 2.6.

Alternative, if the author prefers a selection rule over a fixed value:
- Fit λ ∈ {0.3, 1, 3} at seed 403.
- Pick, on the development ladder only, the largest λ with development R4 vs R2w AUC ≥ Sb's − 0.01 and development face-only S0 vs S4 AUC ≥ Sb's − 0.02.
- This adds 2 fits. It reads no FFHQ data.

### Marks

Development only, against B and Sb at the same seed. The arm "passes" on a seed if all of these hold, and the arm is read on ≥ 2 of 3 seeds:
1. Own-rule flags on FFHQ native genuine (ffhq_bona orig) are at most half of B's.
2. FFHQ native genuine flags at τ_cam are below 50%. They are now 95 to 98%. τ_cam is 5% on the development camera photos.
3. The storage share (paired share rising, contrast-2 read) is ≤ 0.25.
4. landmark_combined AUC (against history-matched genuine) and landmark_complete AUC (against history-matched genuine) are both ≥ B − 0.02.
5. Development-ladder P-c′, as defined in the v2 draft (own rule ≤ 10% of R0_61 flagged with Clopper–Pearson upper bound ≤ 15%; paired shift ≤ 0.05 × the development R4 − R0 gap; paired AUC ≤ 0.65), read on the development ladder.

Other outcomes:
- Falsified (H-new-4) if the own-rule FFHQ native flags stay within ±20% of B's on ≥ 2 of 3 seeds.
- Middle: "inconclusive, no claim".
- Printed: R1 to R6 of FS1 for the arm.

### Code change

- train.py (inside the pack; `code/smadcvpr/train.py`): about 60 to 80 lines.
  - New flags `--eq-pairs CSV`, `--eq-w 1.0`, `--eq-bs 32`.
  - A pair dataset built from `C.ImageItems` and a seeded pair sampler.
  - In `step_loss`, a second `C.forward_out` on the stacked pair batch plus the penalty term.
  - The pair loss is logged.
  - No other path changes: with `--eq-w 0` or no `--eq-pairs` the code path is byte-for-byte the old one, and a test checks equal logits after 20 steps.
- run.sh: a new arm "SbEQ" (manifest train_Sb plus the pair CSV and the three flags). The A, B and Sb invocations are unchanged.

### Pins

- New pack `pn1_pack_eq.tar`: the FS1 pack plus the changed train.py and the pair CSV. Its sha256 changes. The evaluation manifest is unchanged (f0f29f22…).
- New run.sh sha256.
- The drivers need only the new pack pin.

### Cost

- 3 fits × about 75 min on PCIe, about 3.8 A100-hours, about 1.7 USD at 0.44 USD/h.
- About 1 h more for the 8.75 GB upload at the measured 3 MB/s, unless the FS1 host is kept.
- BEQ would add the same again.

## (b) Splice-only-positives arm (H-new-3)

### Arm

"So": the negatives of Sb (B's negatives plus S0 and S3) with ONLY spliced positives.
- The positives are the 124 S4 OpenCV images of the training hosts with a usable partner.
- No whole-frame morph positive: no AF0 u50 or u50_61, no ladder R4.
- Hypothesis: the remaining surround reliance comes from the whole-frame positives.

### Prediction and falsifier

- Prediction: the share of pairs scored higher on the complete morph (R6) falls to ≤ 0.75, while landmark_combined AUC stays ≥ Sb − 0.03, on ≥ 2 of 3 seeds.
- Falsified if the share stays ≥ 0.9 on ≥ 2 of 3 seeds.
- Printed: landmark_complete AUC (expected to fall), R1 to R6, and storage share.

### Risk, stated

- 124 unique positives against about 4,300 unique negatives. Class balance by repetition draws each positive about 35 times per 6,250 × 256 batches, so overfitting to the 124 is likely.
- No other face-splice positive exists on disk. Building more, for example AF0 splices, is an author item.

### Code change

None in train.py.
- A new manifest `train_So.csv`, built by a new list script (about 40 lines) from pack-2 manifests and images, all existing.
- run.sh: add "So" to the arm list.

### Pins

- New pack: the FS1 pack plus train_So, with a new sha256.
- New run.sh sha256.

### Cost

3 fits, about 3.8 A100-hours, about 1.7 USD.

## Order and budget (the author decides)

- Both arms would run on one lease, about 7.6 A100-hours, about 3.4 USD plus upload, starting after FS1 ends (about 06:20 on 13 Nov).
- Reading would be on 13 to 14 Nov.
- Both need a registration committed before any fit, and a pre-run review.
