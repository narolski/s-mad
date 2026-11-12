# DRAFT registration: the sealed final benchmark read (FINAL), v2

**Not to be executed without the author's explicit go.** This is a draft. No benchmark file was opened to write it. No score of any candidate network on any benchmark exists for the fresh seeds or later fits.

- v1 (71fa6e4) was reviewed in `experiments/reviews/PRERUN_FINAL_SEALED_READ_20261112.md` (GO WITH FIXES, blockers B1–B4).
- v2 applies B1–B4, M1–M8 and the minor points, using the reviewer's replacement texts where given.
- The text is fixed by the commit that registers it; the freeze rule (section 1) is then applied mechanically.

## 0. Terms

- **E7 pool**: the genuine photos of a benchmark given the morph family's shrink-and-enlarge history. Each pool is shrunk to the family's median inter-eye distance and enlarged again (`resmatch`), as defined in `experiments/EV1_fixed-threshold-reread/prereg.md` and the AD4 README.
- **Native cell**: a family's morphs against the set's own genuine photos.
- **E7 cell**: a family's morphs against that family's E7 pool.
- **Own rule**: a detector's own decision. For our networks this is logit > 0; for the releases, probability of morph > 0.5.
- **τ_dev**: a threshold at 5% false alarms on a development genuine pool. Two pools are computed for every detector, and both are printed:
  - (i) R0+AF0, our training-source camera photos (development ladder R0 and AF0 validation photos);
  - (ii) EV1 devbona.

  **The decision uses (i) for all detectors (M4).**
- **APCER**: share of morphs accepted as genuine. **BPCER**: share of genuine photos flagged. **BPCER@APCER x%**: BPCER at the threshold where APCER = x% on the cell.
- **One metrics function**, pinned by sha256 in the pack, serves every detector: EER by linear interpolation of the ROC, and ties counted half.

## 1. Freeze rule (applied mechanically; fallback order fixed now)

Inputs: the registered readings only.
- FS1 contrasts 1 and 2: `prereg_fresh_seeds_v4_frozen.md`, git ac585b7.
- Sp: registration 1b8fe48.
- MS1 part 2 as registered at commit f748da4195709ee84c8cc9872c5aac1d9007a049 (co-primaries P1-S on the Chicago Face Database and P1-T on the TT1 pools, each at p ≤ 0.025; arms Sb, SbM3, SbV; guards G1–G3).

No benchmark number enters.

1. **Sb** is frozen if both hold:
   - FS1 contrast 1 is "replicated";
   - FS1 contrast 2 is "replicated" for Sb, with A's positive control met.
2. **Otherwise, B** is frozen if FS1 contrast 2 is "replicated" for B, with A's positive control met.
3. **Otherwise, no method** is frozen. The read is then an audit of the comparison set only, with no candidate claim.

**MS1 rule (B3).** The three-source version is frozen only if both:
- the MS1 primary is "supported", meaning both co-primaries (P1-S and P1-T) are supported as registered in MS1 prereg.md part 2 at commit f748da4195709ee84c8cc9872c5aac1d9007a049;
- every MS1 guard (G1–G3) holds, as registered there.

If MS1 is unregistered, unread, or B is frozen, the single-source arm is frozen. MS1 has no B arm.

Sp's outcome does not change the frozen arm; it only qualifies the claim. The FS1 printed reads R1–R6 and the amendment-15 baseline do not change it either.

**Networks read.**
- Every fresh seed of the frozen arm: seeds 403–407, or all of MS1's seeds.
- One network per seed, last checkpoint, no seed picking, no ensembles and no score fusion.
- A lost seed is reported as lost and never replaced.
- Per cell: every seed's value, the mean, the SD and the minimum and maximum.

Thresholds (τ_dev from both pools, and the own rule) are fixed before the read from development scores. They are committed with the pack. No threshold is taken from any benchmark.

## 2. Sets and cells (B2)

**Confirmatory:** the morph side of MorDIFF and DiM. FEI gtest and the sealed sets are added only if the author assigns them.

**Reported, labelled "seen during development":** MAD22, FRLL-Morphs and H1.
- The author's stated goal is a comparison with the state of the art on MAD22 and FRLL-Morphs. So a full standard-form table is reported for both, labelled, but it is not the confirmatory endpoint.

The sets:
- **Corrected MAD22** (`/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z`): FaceMorpher, OpenCV, Webmorph, MIPGAN-I, MIPGAN-II; genuine = the 204 FRLL photos.
- **FRLL-Morphs.** The headline is StyleGAN only, the only border-free family (M1). The landmark families (AMSL, FaceMorpher, OpenCV, Webmorph) carry our aligner's border; their mean is printed.
- **MorDIFF**, with the corrected MorDIFF crop of RS1 amendment 7 for the releases.
- **DiM**, six families.
- **H1**: 598 CASIA-WebFace Poisson splices against 598 genuine photos.

**Genuine pools.** Every cell is printed with the full genuine pool and the neutral-only genuine pool (the expression cue, C1).

**Not read:** FEI and the sealed sets unless assigned; FFHQ (development set by designation).

## 3. Metrics and endpoint

Every detector is reported under every form.

| Form | Per cell |
|---|---|
| Standard | EER; BPCER@APCER 1, 5, 10 and 20%; AUC printed |
| History-matched | EER and BPCER@APCER 1/5/10/20% on each E7 cell |
| Own rule | APCER per family; BPCER on the native, E7 and benign-variant pools |
| τ_dev | as own rule |

Exact Clopper–Pearson intervals are printed for every rate.

**Single confirmatory endpoint (M2).** The τ_dev form on the confirmatory cells: APCER per family at τ_dev(i), and BPCER on the E7 pool, combined as (mean APCER + BPCER)/2. It is read on the MorDIFF and DiM family means, two confirmatory cells, with Holm correction across them. Everything else is descriptive.

**Statistics (M3).** A two-level bootstrap: seeds first, then persons, 2,000 draws, `default_rng(20261121)`.
- **Exceeded:** the 95% interval of (ours − best comparison) lies entirely below 0, AND ≥ 4 of 5 seeds are individually better.
- **Matched (non-inferiority):** the upper 95% bound of (ours − best) ≤ +1.0 point.
- **Lost:** the interval lies entirely above 0.
- **Otherwise:** "comparable, not separated".
- The same rules apply to the BPCER ratio in the controlled forms.

## 4. Comparison set and "best comparison" (B4)

| Group | Detectors |
|---|---|
| Released checkpoints | MADation ViT-B/16 and ViT-L/14, SelfMAD, MixFaceNet-MAD |
| AD5 retrains (seed means) | the same four methods at seeds 401–405, where finished and verified by the read date; otherwise "not available" |
| Reference lines (printed only, never "best") | AD4's morph-free networks (M3, M3L); PN1 internal arms (A, and B or Sb, whichever is not frozen) |

**Definition:**
- **Best comparison** = the lowest value among released checkpoints and AD5 retrain seed means only.
- Morph-free and internal networks are printed reference lines.
- Any cell where a morph-free network has EER ≤ 5% is labelled "shortcut-saturated" and cannot support a SOTA claim.
- In the own-rule and τ_dev forms, best comparison = the released/retrain detector with the lowest (mean APCER + BPCER)/2 on that cell.

## 5. What counts as matched or exceeded

- Rules of section 3, against the best comparison of section 4, separately per form.
- A SOTA sentence in the abstract needs "matched" or "exceeded" on the confirmatory endpoint, after Holm correction, on a cell not labelled "shortcut-saturated".
- **Claim scope (B1):** MorDIFF and DiM morphs were never scored by a PN1-family network; their genuine photos are the FRLL photos seen during development, and the recipe ingredient (history crossing) was scored on MorDIFF in SM1. Label: "morphs unseen; genuine pool seen". No set read here is clean on both classes.

## 6. Exposure statement

`experiments/PN1_protocol-network-first-tests/BENCHMARK_EXPOSURE.md` is part of this registration.

- **PN1-family recipes.**
  - H1, corrected MAD22 and FRLL / FRLL-Morphs were scored for every PN1 network of seeds 401/402, the tier-0 heads and the reference row.
  - The candidate set {A, B, Sb}, the margins, P-c′, the C contrast and the threshold-transfer framing were chosen with that knowledge.
  - The fresh networks (403–407), Sp and any MS1 network have never been scored on a benchmark: the networks are clean, the recipes are not.
- **MorDIFF and DiM.** The morphs were never scored by a PN1-family network. Their genuine photos are the FRLL photos seen during development, and history crossing was scored on MorDIFF in SM1. Label: "morphs unseen; genuine pool seen".
- **MS1.** Its recipe is itself shaped by the benchmark-informed threshold-transfer framing (exposure choice 6).
- **Releases, AD5 and AD4.** Every cell above was read for them by the audits (RS1, EV1, AD4, C cue checks).
- **Disclosure: the lead is not blind.** The lead endorsed the Sb refit after the H1 result was seen.
- **Paper placement.** The paper states the candidate-set disclosure in its Experiments section, not only in a supplement.

## 7. One read

**Who runs it.** The lead is not blind (section 6), so the proposal is either an owner agent that has never seen a candidate's benchmark score, or the second author. The PN1 owner prepares the pack and sees no score before the commit.

**Pack** (one tar, pinned by sha256 at registration):
- the frozen networks' `last_trainable.pt` and `meta.json` (all seeds), plus the reference lines';
- base weights;
- `rescore.py` / `pn1_score.py`;
- for the releases: their checkpoints and RS1's precomputed face boxes and crops, the corrected MorDIFF crop, and a pinned Pillow/libjpeg build;
- the benchmark manifests;
- both τ_dev pools per detector;
- the pinned metrics function;
- the reader (written and committed before the read; tested on development data only).

**Reuse.** No existing RS1 or AD5 benchmark score is reused: every detector is rescored in the one job. If a path cannot score a form (no E7 pool exists for that input path), the cell is printed "not available". No new resampling code is written (hard rule).

**Detector × form → input path:**

| Detector | Standard | History-matched (E7) | Own rule / τ_dev |
|---|---|---|---|
| PN1 / MS1 networks | aligned 512 frame | aligned E7 pools | as standard + E7 + benign |
| Releases (MADation, SelfMAD, MixFaceNet) | RS1 own-crop path (pinned boxes) | RS1 E7 crops where they exist, else "not available" | as standard |
| AD5 retrains | AD5 scoring path | as releases | as standard |
| AD4 morph-free | AD4 path | AD4 E7 cells | as standard |

**Platform (M7).**
- GPU type and software stack: A100 PCIe or SXM4 40 GB, image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, pip pins of remote_setup.sh.
- Gate before any benchmark row:
  - rescore the amendment-13 FFHQ list with A_s401 and B_s402, requiring byte-identical scores;
  - rescore 200 development rows of each frozen network, and of one H100-trained MS1 network if MS1 is frozen or read, against their training-platform scores, with max |Δ logit| ≤ 0.05;
  - release gate: rescore 200 RS1 rows with every release, max |Δ| ≤ 0.05.
- If any gate fails, stop.

**Order.** Confirmatory cells, then the reported sets, in one job.

**No feedback; failure handling (M8).** After the read no network is trained, no recipe, threshold or freeze input is changed before the paper; later work is labelled post-read. Outputs go to a sealed file shown only after the whole job finishes; a crash is re-run unchanged with no partial output viewed. A failed gate may be repeated once after an infrastructure fix, still with no benchmark rows; a second failure → audit-only branch.

**Reviews.** A pre-run review of this text and the pack; the author's go; the read; a post-result review; then the paper text.

## 8. What the paper says under each outcome

**Prediction (M5), stated now.** The frozen arm's E7 EER on MorDIFF/DiM is ≥ 30%. The releases' low standard-form EER there is read as render-path/storage detection (AD4, RS1). Under this prediction the abstract carries no SOTA claim.

| Outcome | Paper statement |
|---|---|
| Confirmatory endpoint matched or exceeded (not shortcut-saturated) | "Under a fixed development threshold on history-matched genuine photos, the method matches (exceeds) the published detectors on unseen diffusion morphs (genuine pool seen during development)." |
| Matched on MAD22 (standard form), lost on diffusion | "Competitive with published detectors on MAD22 under the standard form (seen during development); on unseen diffusion morphs it does not match them, and their advantage there tracks the render path, not morphing." |
| Lost on the standard form, exceeded on the controlled forms | "On the standard form the method trails the state of the art; under history-matched pools and fixed thresholds it is better. We argue the standard form rewards the storage shortcut and report both." |
| Comparable or lost everywhere | "The method does not improve detection; the contribution is the audit and the controlled protocol." |
| No method frozen | "Audit only: published detectors under standard and controlled forms." |

- Every statement carries the labels of sections 5–6.
- Threshold transfer to unseen genuine sources is claimed only if MS1's registered P1 holds with its guards.

## 9. Missing for CVPR (reviewer's list), with the cost by 14 Nov

| Item | What | Cost by 14 Nov |
|---|---|---|
| Second backbone | a DINOv3 or ViT-B/16-variant rerun of the frozen arm, or an explicit limitation statement | rerun: about 5 fits × 1.4 h ≈ 7 A100-h (≈ 3.3 USD), needs code for a DINOv3 LoRA arm (author item); limitation statement: 0 |
| Cross-dataset protocol table | training sources against test sources (FRGC/colorFERET, +FFHQ in MS1; tests: ladder, FFHQ, benchmarks) | 0 (writing) |
| Ablation table | A, B, Sb, Sp, SbM3, from registered development reads | 0 compute once FS1, Sp and MS1 are read |
| Paired seed tests | sign / Wilcoxon over seeds for each ablation contrast | 0 (in the readers) |
| Compute disclosure | GPU-hours including audits and rentals | 0 (collect from records) |
| Limitation statements | thresholds do not transfer to unseen genuine sources unless MS1 passes; all benchmarks share one genuine pool of 204 FRLL photos | 0 |

## 10. Author decisions (reviewer's five items)

1. Release FEI gtest and/or the sealed sets as the confirmatory set (only matters if B2 is accepted).
2. Accept the controlled τ_dev form as the confirmatory endpoint, with the standard form secondary.
3. Who runs the read, given that the lead is not blind.
4. Wait for the AD5 retrains, or print "not available".
5. Accept that the expected outcome is no SOTA claim in the abstract.
