# Independent review: protocol network first tests (PN1) tier 1; AR1 amendment 9; AD4 follow-ups; PN1 amendment 11

Reviewer: results-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited.

## Post-result review: the protocol network's first tests (PN1), tier 1, plus AR1 amendment 9, AD4 follow-ups (b) and (c), and PN1 amendment 11

I worked read-only. I did not open valx.csv, FST or A12SP. My recomputation script is at /tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/pn1rev/recomp.py. It builds its own pools from `manifests/pn1_eval.csv` and reads the raw `scores_eval.npz` in `/mnt/t7/smad_next/PN1/results_rented/unpacked/`.

### Verdicts

**Subject 1 (PN1 tier 1): the numbers are sound, but the reading needs qualification.** I reproduced every headline number from the raw scores. Three things change how it should be read:
1. **The marks run on a saturated scale.** The recipe's head is a linear layer on L2-normalised features. Its weight norm is 3.84 to 3.86 and its bias about 0.01 (`last_trainable.pt` of A401, B401, C402). So logits cannot leave about ±3.87. Camera photos sit at −3.67, morphs at +3.68, and τ_cam sits 0.03 to 0.10 logits above that floor. P-c's standard-deviation unit, τ_cam itself, and therefore P-c2 and P-g all read a cosine band about 0.03 wide.
2. **The registered consequence was not applied.** Every B, Bn and C network fails P-c, P-c2 and P-d on both seeds. That is not one of the middle outcomes that amendment 4 item 5 labels "inconclusive". Prereg §7 says "B passes" needs every mark on both seeds, and its loss rule covers exactly this pattern (pass P-a and P-b, fail P-c): the next step is the equality term.
3. **P-g carries no information.** At τ_cam the gating-family miss is 0.05 to 1.3% for all eight fits. That low miss is paid for by flagging 30 to 95% of FRLL genuine photos and 99.5 to 100% of H1 genuine photos.

**Subject 2: needs qualification.**
- PN1 amendment 11's time label is impossible: git shows the text existed 20 minutes before the time it states.
- AR1 amendment 9 is mis-dated, and its "reads the blend" inference has no simple-statistic floor behind it.
- AD4 (c) H-new-4 calls a 0.03 to 0.05 logit difference inside the saturated floor "supported".
- AD4 (b) labels its platform "Athena, NVIDIA GB10"; it ran on the DGX.

### Q1. What I recomputed

All of the following reproduced to the printed precision:
- **Warp-only vs morph and softened-copy reads.** R2w vs R4 and R2w4 vs R4 are 1.000 in all 8 fits. R0_61 vs R4 is 0.999 to 1.000.
- **Raw logit shift from photo to 61 px copy.** A +1.73 / +2.64; B +0.15 / +0.13; Bn +0.22 / +0.16; C +0.19 / +0.11.
- **Standard deviation of the photo logits.** 0.019 to 0.060, except C401 at 0.187.
- **Shift in SD units.** 63.4 / 108.2 / 3.9 / 6.7 / 3.7 / 5.5 / 1.0 / 4.2.
- **Own-rule flag rate on 61 px copies.** 20.4, 1.6, 3.1, 2.1, 31.9, 1.0, 0.5, 1.0%.
- **Camera-threshold (τ_cam) flag rates.** All rows match, including FRLL native at 51 / 77 / 95 / 30 / 66 / 67 / 70 / 38%. result.md prints 78 for B401; the value is 77.45, so it should read 77. H1 genuine is 99.5 to 100%.
- **H1 AUC.** 0.847 / 0.781 / 0.747 / 0.838 / 0.827 / 0.680 / 0.661 / 0.816.
- **MAD22 history-matched (E7) EERs.** Within 0.25 points: my EERs use the plain ROC crossing; theirs interpolate. Examples: B401 OpenCV 1.65 against 1.8 printed; A401 Webmorph 18.51 against 18.4.
- **P-g and the reference row.** The P-g bootstraps come from `compare.json`. Reference row: 7 of 8 networks flag more than 10% of some history-matched pool at the own rule (s8's maximum is 6.3%). At τ_cam the largest pool is 43.1 to 74.0%, mostly MAD22 FaceMorpher E7.

**New fact: MAD22 genuine and FRLL genuine are the same 204 photos.** Their B401 logits correlate at r = 0.9999, with a largest difference of 0.006. So "FRLL and MAD22 genuine pools flagged" counts one source twice.

### Findings, most severe first

1. **(Blocker for interpretation) The τ_cam marks run on the saturation floor.** Evidence:
   - Camera-photo logits have a 5th-to-95th percentile of −3.69 to −3.60 in every PN1 fit; τ_cam is −3.56 to −3.63.
   - FRLL photos have a median of −3.55 to −3.61, which is why 30 to 95% are flagged.
   - The same ceiling was already documented in AD4 (`AD4/result.md`: natives −3.65, copies +3.62, 5th to 95th percentile within 0.03).

   Consequences:
   - P-c's SD unit, P-c2's τ_cam half, the JPEG marks at τ_cam, and P-g all inherit the defect.
   - A's "JPEG violation" exists only at τ_cam. At the own rule A flags 0% of jpeg50, and B flags 91 to 99% of jpeg50 at τ_cam as well.

   Fix: state the mechanism in result.md (text below). Do not change any mark.

2. **(Major) The wrong registered label was applied.** "Inconclusive, no claim" is amendment 4's sentence for middle outcomes: one seed passing and one failing, P-b between 0.75 and 0.90, or P-f unread. Here the failures hold on both seeds. The correct reading is:
   - "B, Bn, C: not passed. P-c, P-c2 and P-d fail on both seeds. Kill rules not met. Loss rule (prereg §7): pass P-a and P-b, fail P-c, so the registered next step is the equality term (outside PN1)."
   - The record should then add that P-c's failure is driven by the instrument (finding 1), so the loss-rule trigger is weak evidence that an equality term is needed.

3. **(Major) P-a and P-b are at ceiling and cannot tell the arms apart.** The excess is +0.112 with lower bound 0.076, identical for all 8 fits, because every network scores 1.000 and the floor (band5@224, 0.888) is fixed. "Keeps the morph signal" is therefore untestable with these contrasts. Say so.

4. **(Major) The training-gap sentence uses a different scale from P-c.** Gaps "within ±0.2 logits" include lad_R2w −0.14 (Bn401), −0.17 and lad_R0 −0.10 (C401). Those are 2 to 7 floor SDs, on the same scale P-c uses. Calling them small while P-c is read in SD units is inconsistent. Report both on raw logits and in floor-SD units.

5. **(Major) Registration timestamps are not machine-clock times.** Commit 1c52cbe (23:38:52) already contains amendment 10 ("23:50"), amendment 11 ("23:58") and the pack 2 pin ("12 Nov 00:05"). `pn1_pack2.tar` was written at 23:31:05. Details under Subject 2.

6. **(Minor) Stale records.** result.md's header says "tier 1 … pending", and its compute table lists Athena jobs as pending with no rented costs. README §1, §9 and the 19:55 status are stale. DOCUMENTATION.md requires current status and compute.

### Q2. Is P-c a defective mark or a real failure?

It is a defective instrument with a binding failure. Mark by mark:
- **P-a pass and P-b pass:** both at ceiling.
- **P-c fail:** it fails on the SD unit on all 6 non-A fits. It also fails on the τ_cam flag on 5 of 6 (7.9, 13.6, 10.5, 17.8, 11.5, 11.5%). The τ_cam part has the same saturation defect. Only the own-rule part passes (0.5 to 3.1%).
- **P-c2 fail:** a real deployment failure at τ_cam, because whole genuine sources are flagged. At the own rule, kernel and E7 pools are at most 5.4%.
- **P-d fail:** real. A also fails (0.847 / 0.827).
- **P-e pass:** reproduced, on point EERs.
- **P-f pass:** R4_61 miss is 0 to 0.5%.
- **A violation:** robust through the own rule alone (20.4 / 31.9% of 61 px copies flagged).

**What can be claimed (descriptive, labelled post hoc):**
- "At the own 0.5 rule, storing test photos at 61 px moves 20.4 / 31.9% above the decision boundary for A and 0.5 to 3.1% for B, Bn, C."
- "The share of hosts whose logit rises is 0.98 / 0.99 for A and 0.50 to 0.69 for B, Bn, C."

**What cannot be claimed:** that B does not react to storage; that P-c "effectively passes"; or any sentence that B removes A's failure.

**A properly pre-stated replacement (P-c′),** registered before any new fit is scored and applied only to fresh networks. Every part must hold on both seeds:
- (i) Own rule: at most 10% of R0_61 flagged, with a Clopper-Pearson upper bound of at most 15%.
- (ii) τ_multi (5% false alarms on a pooled development genuine set with equal weight per genuine source, at least 3 sources, none of them a training database): at most 10% of R0_61 flagged.
- (iii) Paired shift scale: median paired shift at most 0.05 × (median development R4 logit − median development R0 logit), and paired AUC(R0_61 vs R0) at most 0.65.

The current 8 fits and the test ladder cannot be used to "pass" P-c′.

### Q3. The method candidate's fixed threshold

τ_cam is calibrated on FRGC and colorFERET photos, the training databases, which sit on the floor. Every other genuine source sits above it: FRLL 30 to 95% flagged, CASIA/H1 99.5 to 100%. The SMDD reference networks transfer much better to FRLL (0 to 5.9% at τ_cam) but not to H1 (20 to 100%).

The claim "lowest miss at a fixed threshold among detectors that pass storage/softness controls":
- **Dead** for PN1 networks as configured: none passes the controls, and their low miss is bought with false alarms.
- **Untested** for the method family: no detector in the programme passes the controls.

It can only come back with (a) a pre-stated multi-source calibration pool and (b) a check, made first, that genuine flags hold on unseen sources, with miss compared only after that.

### Q4. Is warp-only vs morph = 1.000 evidence of blending, or a shortcut?

The separation is real but uninformative about where the blend is read. Existing data:
- **Same pipeline up to the mix.** The AF0 zero file is byte-identical to that morph's halfA in all 149 pairs (README §8). So the only R4-specific step is the mixing and its rounding; "pipeline trace" reduces to properties of averaging.
- **Not one tool's trace.** FaceMorpher, never trained, also gives 1.000.
- **Not identity mixing.** Same-person morphs (R3) are placed above the own rule 91 to 99% of the time, and mirror self-morphs (R3m) 90 to 98%. R4 vs R3 is only 0.73 to 0.77.
- **Mostly softness.** AD4's morph-free networks, which never saw a blend, reach R4 vs R2w 0.84 to 0.86 on the ladder. One band-power statistic gives 0.888.

The open question is location: surround or face. Frozen heads were face-blanked 0.99 against face-only 0.73 to 0.78. The amendment-12 rescoring of B on blanked and spliced rows answers this for LoRA networks; extend it to A and C.

### Q5. What two seeds can say

Seed is confounded with machine (40 GB vs 80 GB A100, amendment 7).
- H1 AUC with 598/598 images has a standard error of about 0.013. The 0.10 gap between B's seeds is training variance, not test noise.
- The reference recipe's 8 seeds span own-rule R0_61 flags of 5.2 to 50.3%, Webmorph E7 EER of 9.4 to 27.0%, and H1 0.819 to 0.869.

Patterns that hold within seed on both seeds:
- C vs A, Webmorph E7 EER: −10.7 and −13.7 points.
- B vs A, H1 AUC: −0.07 and −0.15.
- Bn vs A, H1 AUC: −0.10 and −0.17.

These are leads for fresh-seed re-tests, not effects.

### Q6. Reference row vs earlier reviewed findings

It is consistent:
- RS1 (reviewed): the released ViT-B/16 at a 5%-unprocessed-photo threshold flags 33 to 49% of history-matched photos.
- SM1: 10 to 25% of FRLL photos flagged at the camera threshold. Its single released-SMDD ViT-B/16 fit shows 5.4% at the own rule, which is the low end of PN1's reference range (s5 5.2%, s8 6.3%).

So a single-fit reference is not representative.

### Subject 2

- **PN1 amendment 11.** The label "23:58, before computing" is false. The text is in commit 1c52cbe at 23:38:52. Face-only and blanked features were extracted 23:31 to 23:34 (`gpu_fo.log`), `posthoc2.py` was written at 23:33, `posthoc2.json` at 23:41:29, and NOTEBOOK reported the numbers at 23:42. Probably written before the statistics, but not provably before the extraction. It governs no tier-1 mark, and all its items are post hoc, so no verdict changes. Rewrite the label as "written by 23:38 (git 1c52cbe); header times of amendments 10, 11 and the pack 2 pin were not machine-clock times".
- **AR1 amendment 9.**
  - It says "registered 12 Nov", but `swap_seam.csv`, `floor3_pn1.json` and `sp_floor.json` were written 11 Nov 23:58 to 23:59, in the same commit 9f1f810. The order cannot be verified.
  - "Twice the colour step" should be "1.7 to 2.0 times" (luma 15.6 vs 9.3, R-G 9.1 vs 5.4, step 15.2 vs 7.8).
  - "SelfMAD does not exceed the floor" should be "not shown to exceed the floor (+0.021 [−0.013, 0.057])".
  - S4 vs SW (0.888) has no simple-statistic floor. An inside/outside sharpness ratio may separate a blended interior from a single-warp patch. Write "SelfMAD does not read only the patch boundary", not that it reads the blend, until that floor is computed (zero GPU).
- **AD4 (b)/(c).**
  - `fu_blank_m3.md` lists "Athena, NVIDIA GB10"; it should be "DGX GB10" (amendment 4b).
  - H-new-4 "supported" rests on −0.03 / −0.05 logit differences inside a floor whose 5th-to-95th percentile spans 0.03, with no interval. Write "indistinguishable: both at the trained floor".
  - The scorer-gate misses (τ 0.987 to 0.989) are probably ties at the floor. Note this; do not rescue them.
  - H-new-5 (R4 vs R3 0.50 to 0.52) is well stated.

### Exact corrections for PN1 result.md

- Line 3: replace the status with "Status 12 Nov 03:00 CET: tier 1 read as registered on rented A100s (amendment 7); Athena jobs cancelled or discarded."
- Lines 77 to 83: replace "Registered reading for every arm: 'inconclusive, no claim'" with: "Registered reading: B, Bn and C do not pass (P-c, P-c2, P-d fail on both seeds); no kill rule met; loss rule (§7) applies (pass P-a and P-b, fail P-c → equality term, outside PN1). A violation on both seeds, robust at the own rule (20.4 / 31.9% of 61 px copies). No 'removes' sentence."
- Add after line 83: "Scale caveat: the head is linear on normalised features (‖w‖ 3.84 to 3.86, bias about 0.01), so logits are bounded at about ±3.87. Camera photos sit at −3.67 with SD 0.02 to 0.19, and τ_cam lies 0.03 to 0.10 logits above them. P-c's SD unit and every τ_cam mark (P-c, P-c2, JPEG, P-g) read this saturated band. At τ_cam the gating-family miss is 0.05 to 1.3% for every fit, bought by flagging 30 to 95% of FRLL and 99.5 to 100% of H1 genuine photos, so P-g carries no information. MAD22 genuine = the same 204 FRLL photos. P-a and P-b are at ceiling (identical excess in all 8 fits)."
- Line 83: "Training-row minus held-out logit gaps per kind: within ±0.2 logits (up to 7 floor-SDs: lad_R2w −0.17 C401, −0.14 Bn401)."
- Line 73: B401 FRLL native 78 → 77.

### New hypotheses

- **HN1. Saturation explains the collapsed scale.**
  - Statement: training accuracy 1.0 with a bounded cosine head pins training-source photos at the floor, and the SD of R0 measures how tight the floor is.
  - Prediction: R0 logits lie within 0.1 of −‖w‖+b in all 8 fits.
  - Falsified if ‖w‖ ≥ 5 or the R0 median sits more than 0.3 logits above the floor.
  - Cost: 0 GPU, 10 minutes.
- **HN2. Genuine-source shortcut.**
  - Statement: the genuine class has been learned as "FRGC or colorFERET photo".
  - Test: score a genuine database never used (FEI or FFHQ, only if aligned files already exist; building them is an author item).
  - Prediction: at least 30% flagged at τ_cam for B and Bn.
  - Falsified if at most 10%.
  - Cost: about 0.2 A100-hours.
- **HN3. Compression history explains C's gains.**
  - Statement: C's JPEG copies remove a compression cue, which explains Webmorph (−11 to −14 points) and the lower FRLL native flags (30 / 38% against 67 to 95%).
  - Test: read the raw-file format headers, and correlate the per-image C−A score difference with a JPEG blockiness measurement (no image written).
  - Falsified if the raw Webmorph files carry no JPEG history and |ρ| < 0.1.
  - Cost: 0 GPU.
- **HN4. The blend is read in the surround.**
  - Prediction from the amendment-12 rescoring: B face-blanked ≥ 0.95 and face-only ≤ 0.85.
  - Falsified if face-only ≥ 0.95.
  - Cost: about 0.1 A100-hours (already running).
- **HN5. Protocol negatives hurt H1.**
  - Statement: warp-only images and halves as negatives teach "warped face without ghosting = genuine", so B and Bn lose H1 AUC.
  - Prediction: the B−A H1 drop concentrates in the lowest ghost-energy quintile.
  - Falsified if the slope's interval includes 0.
  - Cost: 0 GPU.
- **HN6. Seed variance exceeds most arm differences.**
  - Prediction on seeds 403 to 405: C−A Webmorph E7 ≤ −5 points in 3 of 3; B−A H1 < 0 in at least 2 of 3.
  - Cost: about 6.6 A100-hours (6 fits), about 3.5 USD.
  - Register P-c′ before running.

### Next experiments, ranked by information per GPU-hour

| # | Experiment | Cost | When | Decides | Approval |
|---|---|---|---|---|---|
| 1 | Head norm and floor check (HN1); result.md corrections; loss-rule label | 0 | now | how every τ_cam mark is read | lead |
| 2 | Post hoc scale-free storage reads and per-source flag table | 0 | now | descriptive storage sentence | label post hoc |
| 3 | JPEG-history check (HN3) | 0 | now | whether C is a "compression fix" | none |
| 4 | Floor for AR1 S4 vs SW; noise-residual floor on R2w vs R4 | 0 (CPU, measurement only) | now | "reads the blend" wording | AR1 amendment |
| 5 | Read amendment 12; extend the rescoring to A and C (HN4) | 0.3 A100-h | 12 Nov | surround vs face | PN1 amendment |
| 6 | Unused genuine database (HN2) | 0.2 A100-h | 12 to 13 Nov | whether the source shortcut is the cause | author, if alignment is needed |
| 7 | Fresh seeds 403 to 405 for A, C (+B) with P-c′ pre-registered (HN6) | 6.6 to 10 A100-h | by 13 Nov | whether the C and H1 patterns replicate | new registration |
| 8 | Multi-source genuine training arm | 3 to 5 A100-h | 13 to 14 Nov, only if 6 confirms | whether calibration can transfer | author (images) |

### Risks to the story

- **Ceiling marks.** No fixed-threshold claim survives with source-specific genuine manifolds, and P-a and P-b cannot show that "the signal is kept".
- **Seed and platform noise.** Two seeds on two machines; the reference recipe's own seed spread is larger than most of the effects.
- **Timestamps.** The time labels undermine "registered before". Use git hashes, not header times, in the paper and the ledger.

Hedge now: write the hierarchical claim (genuine flags on unseen sources first, then miss) and P-c′ before any new score exists.

