Reviewer: experiment-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited. Verdict: STOP as drafted for both arms; alternatives proposed.

## Pre-run review: PN1 remedy arms SbEQ and So (draft `prereg_remedies_draft.md`, commit 6cf7dc8)

I worked read-only. I opened no benchmark, valx, FST or A12SP file, and no FS1 result.

**Verdicts**
- **SbEQ (equality term): STOP as drafted, GO WITH FIXES if it is re-specified.** Two reasons. Its comparator is B, so it would pass or fail on what it inherits from Sb, not on the term. And its storage mark rewards bias rather than invariance. My prior that the term reduces cross-source flags is about 10%.
- **So (splice-only positives): STOP.** Dropping the whole-frame positives also drops every stored-small morph, every AF0-built positive and 91% of the unique positives. H-new-3 cannot be attributed with existing images.
- **Instead:** one zero-code ablation arm, "Sp", and one zero-GPU check, both below.

### Findings (most severe first)

**F1 (blocker, SbEQ): the comparator is B, so the result measures Sb, not the term.**
- Marks 1 and 4 and the falsifier are all "versus B" (draft lines 51, 54, 58).
- On 401/402, Sb alone is 5.9 / 7.0% own-rule FFHQ flags against B's 17.8 / 6.4% (result.md:147, 151, 244). So mark 1 already holds for Sb at 401.
- Sb's landmark_combined is 0.13 to 0.19 above B (result.md:217), so "≥ B − 0.02" is guaranteed.
- The falsifier "within ±20% of B's" can fail just because SbEQ inherits Sb's offset.
- Fix: every mark and the falsifier are read against Sb. Use all 5 fresh Sb seeds (403 to 407) as the reference distribution. Primary test: exact one-sided Mann–Whitney of SbEQ's 3 values against Sb's 5 (smallest attainable p = 1/56 = 0.018). Require the median ratio to be ≤ 0.5.

**F2 (blocker, SbEQ): mark 3 rewards over-correction.**
- "Storage share ≤ 0.25" is the share of persons whose logit rises under storage.
- A network that ignores storage gives a share of about 0.5. B, which is nearly invariant (median shift −0.026 / −0.030), sits at 0.44 / 0.37 (result.md:172, 176).
- Sb's 0.16 / 0.29 means "stored ⇒ more genuine". An equality term that works would push the share up toward 0.5 and fail the mark.
- Fix: make the mark two-sided: |median paired shift| ≤ 0.1 genuine SD, or AUC(history vs native) in [0.45, 0.55].

**F3 (major): the term targets storage, but the marks test cross-source transfer.**
- All 773 pairs are FRGC/colorFERET storage or warp pairs. Storage is the shortcut Sb already nearly removes.
- Nothing in the term carries FFHQ-like source variation.
- Prior evidence: A49 used a paired processing-consistency term at λ = 1 on the same head type (L2-normalised feature → linear). Its primary failed (instability +0.0029 [−0.005, +0.011]; docs/PLANNING_RECORD.md:140). The draft does not cite it.
- Fix: register the expected null and cite A49. Restate H-new-4 as a storage-invariance hypothesis, or keep mark 1 printed only.

**F4 (major): the logit penalty is weak and acts mostly on the head.**
- z = w·f + b with ‖f‖ = 1 and ‖w‖ ≈ 3.85 (REVIEW_PN1_TIER1:12). Genuine images at −3.67 sit at cos ≈ −0.95. There dz/dθ = ‖w‖ sin θ is about 0.31 ‖w‖, so training pairs on the floor differ by little.
- The penalty is λ‖w‖²Δcos². The head LR (3.33e-5) is 10× the LoRA LR (run.sh), so the cheapest way to lower it is to reorient or shrink w, not to change the features.
- The term ignores labels, so it can also be satisfied by pushing genuine images deeper onto the floor. That narrows τ_cam and cannot improve transfer.
- Units: λ's justification ignores the averaging. Per image, the term is weighted 1/32 against BCE's 1/256. A genuine image on the floor has a BCE gradient of σ(−3.67)/256 ≈ 1e-4, against 2Δ/32 ≈ 6e-3 for the term at Δ = 0.1. So the term is not zero late in training, but what it acts on is the floor and the head.
- Dropout: with LoRA dropout 0.4 in train mode, the two images of a pair get different dropout masks. The term then partly penalises dropout noise (R-Drop). This confound was already flagged for CLIP consistency losses (PLANNING_RECORD:201).
- Fix: compute the pair pass in eval mode (CLIP has no BatchNorm; gradients still flow). Log ‖w‖ and a null pair (a, a).
- Better space: 1 − cos(f_a, f_b) on the normalised feature. It has a gradient throughout training and does not touch w.

**F5 (major): mark 2 cannot pass.**
- τ_cam sits 0.03 to 0.10 logits above the saturated floor (TIER1:12). The term tightens that floor further.
- All five marks are required together, so "pass" is close to unreachable.
- Fix: print mark 2 only.

**F6 (major): marks set knowing the values, and open forks.**
- "Half of B's" and "≤ 0.25" were written knowing Sb's 5.9 / 7.0% and 0.16 / 0.29 (REVIEW_A14:107-108). Disclose this, in the style of BENCHMARK_EXPOSURE §2.
- Freeze the registration before any FS1 tar is opened (about 06:20). Otherwise the fresh B and Sb values can shape the marks.
- Forks to close:
  - drop the λ ∈ {0.3, 1, 3} alternative (lines 43-46);
  - if an Sb fit is missing or non-finite, drop that seed; with fewer than 2 read seeds, the arm is "not read";
  - say whether "at most half" is inclusive;
  - P-c′ needs its positive control (A fails on ≥ 2 of 3 seeds).
- With the ±20% falsifier against B, my rough no-effect falsification probability is about 0.2, given B's spread across seeds (6.4 to 17.8%).

**F7 (major): P-c′ reads the trained storage size.** The term trains 61 px invariance, and P-c′ reads R0_61. Amendment 4 put the deciding storage reads on sizes never trained. Fix: decide on R0_112 and AF0 validation 112.7 px copies, and print R0_61.

**F8 (major, So): memorisation, and a new shortcut.**
- 6,250 × 256 = 1.6 M draws over about 8.4 k rows. So each of the 124 positives is seen about 6,400 times, not "about 35" (draft line 101).
- All s61 strata and every AF0 kind become purely genuine. That breaks the amendment-4 rule of balanced database-by-history strata and makes "stored small ⇒ genuine" a training cue (hard rule 2).
- The mark cannot tell memorisation from H-new-3: memorisation gives a random share and a low AUC, which reads as "inconclusive".

**F9 (minor, operations):**
- Memory: the smoke peak was 30.8 GB at batch 256, and 64 extra images per step may exceed 40 GB. Smoke on the PCIe host and pre-register eq-bs 16 as the fallback.
- Time: an extra forward pass means about 90 to 95 minutes per fit, not 75.
- Byte-identical claim: on GPU an "equal logits after 20 steps" test can fail through nondeterminism (HN9). Run it on CPU (`--smoke`, random init) against train.py `cbb2cbd1…`. Guard every new object behind `if a.eq_pairs`.
- Write the code in Python 3.10 syntax.
- Keep the FS1 host: it saves the 1-hour upload and keeps the machine the same as the comparator fits.
- Include the morph-side pairs u50 ↔ u50_61 (366 exist in train_Sb). Otherwise the term only touches genuine images.

### Improvements, ranked by value per GPU-hour
1. **Zero GPU, now:** score the 773 training pairs (plus 366 morph pairs and 50 null pairs) with the existing B and Sb 401/402 checkpoints. Report median |Δz|, |Δcos| and dropout noise. If median |Δz| < 0.05, the logit term is inert; drop SbEQ. Training data only, no registration beyond a note.
2. **Arm "Sp" (about 4 A100-h, 1.8 USD, no code change; needs registration and author approval):** Sb minus the seam-matched S0/S3 negatives, re-balanced by the amendment-4 rule. This is the self-blending-like control: splice positives without matched negatives.
   - Prediction: Sp flags development-ladder S0 at its own rule at least 2× Sb, and its development S0-vs-S4 AUC is ≥ 0.05 lower, on ≥ 2 of 3 seeds. Printed: landmark_combined, R6, storage.
   - Why it matters: it is what lets the paper defend "constituent-matched negatives" as the method's novelty over SBI and SelfMAD, on development data only.
3. **If a loss-based arm is still wanted, "SbHI":**
   - L = BCE + λ·mean over P of (1 − cos(f_a, f_b)), with f the head input and the pair pass in eval mode.
   - P = photo↔photo61, half↔half61 and u50↔u50_61 (both classes), plus R0↔R2w.
   - λ fixed a priori; a simple rule: λ = 1 in cosine units, stated.
   - Marks against Sb's 5 fresh seeds: the two-sided storage mark, the 112.7 px storage read, landmark_combined ≥ Sb − 0.03, and mark 1 printed.

Plainly: none of these arms can fix threshold transfer to an unseen source. That needs multi-source genuine training (an author item) or a claim without a fixed threshold.

### For the author
- Approve Sp instead of So.
- Accept that cross-source threshold transfer is out of reach with existing data.
- Choose SbHI or no loss arm.

Files: `/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/prereg_remedies_draft.md`, `/mnt/t7/smad_next/PN1/fs_tree/pn1/code/smadcvpr/archs_a12.py` (lines 253-278, the head), `/home/narolski/smad-next/src/PN1/run.sh`, `/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv`, `/home/narolski/mambamorph-code/experiments/A49_dinov3/EXECUTABLE_REGISTRATION.md`.
