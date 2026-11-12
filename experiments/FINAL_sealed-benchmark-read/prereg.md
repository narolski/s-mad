# DRAFT registration: the sealed final benchmark read (FINAL)

**Not to be executed without the author's explicit go.** This is a draft for pre-run review. No benchmark file was opened to write it. No score of any candidate network on any benchmark exists for the fresh seeds or later fits. The text below is fixed by the commit that registers it, and the freeze rule (section 1) is applied mechanically afterwards.

Written 12–13 Nov 2026 by the PN1 owner, at the lead's request (night plan `16_PLAN_NIGHT_12_TO_13_NOV.md`, commit 0a378b8).

## 0. Terms

- **E7 pool**: the genuine photos of a benchmark given the morph family's shrink-and-enlarge history. Each pool is shrunk to the family's median inter-eye distance and enlarged again (`resmatch`), as defined in `experiments/EV1_fixed-threshold-reread/prereg.md` and the AD4 README.
- **Native cell**: a family's morphs against the set's own genuine photos.
- **E7 cell**: a family's morphs against that family's E7 pool.
- **Own rule**: a detector's own decision. For our networks this is logit > 0; for the releases, probability of morph > 0.5.
- **τ_dev**: the threshold fixed on development genuine photos before the read, at 5% false alarms on our development camera photos (development ladder R0 and AF0 validation photos), as τ_cam in PN1.
- **APCER**: share of morphs accepted as genuine. **BPCER**: share of genuine photos flagged. **BPCER@APCER x%**: BPCER at the threshold where APCER = x%, computed on the cell itself (ISO/IEC 30107-3 style).

## 1. Freeze rule (applied mechanically; fallback order fixed now)

Inputs: the registered readings only. These are FS1 contrasts 1–3 (`prereg_fresh_seeds_v4_frozen.md`, git ac585b7), Sp (registration 1b8fe48), and MS1's registered primary (its own registration). No benchmark number enters.

**Order:**

1. **Sb is frozen** if both hold:
   - FS1 contrast 1 is "replicated" (landmark_combined, Sb − B ≥ +0.05 and Sb − A ≥ −0.02 on ≥ 4 of 5 seeds);
   - FS1 contrast 2 is "replicated" for Sb, with A's positive control met.

   If, in addition, MS1's registered primary passes for its three-source version of the same arm, the frozen recipe is that three-source version (MS1's fits and seeds). Otherwise it is single-source Sb.
2. **Otherwise, B is frozen** if FS1 contrast 2 is "replicated" for B, with A's positive control met. The same MS1 rule applies.
3. **Otherwise, no method is frozen.** The read then covers only the comparison set (section 4), as the audit under both forms. No candidate claim is made.

- Sp's outcome does not change the frozen arm. It only qualifies the claim: if Sp is supported, the matched negatives are named as the active ingredient; otherwise they are not.
- The FS1 printed reads R1–R6 and the amendment-15 baseline do not change the frozen arm.

**Networks read:**
- Every fresh seed of the frozen arm (Sb or B: seeds 403–407; an MS1 arm: all of MS1's seeds).
- One network per seed, last checkpoint, no seed picking, no ensembles and no score fusion.
- A seed lost in training is reported as lost and never replaced.
- Reported per cell: the mean over seeds, the SD, the minimum and maximum, and every seed's value in a table.

**Thresholds** are fixed before the read:
- τ_dev per network, from its development scores (already computed; committed with the pack);
- the own rule.

No threshold is taken from any benchmark.

## 2. Benchmark sets and cells

**Primary:**
- **Corrected MAD22** (`/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z`). Families FaceMorpher, OpenCV, Webmorph (landmark) and MIPGAN-I, MIPGAN-II (GAN). The genuine pool is the set's bona fide photos, the 204 FRLL photos.
- **FRLL-Morphs.** Families AMSL, FaceMorpher, OpenCV, StyleGAN and Webmorph, against the FRLL genuine photos.
  - The standard pool is all 204 (neutral and smiling, as published); the neutral-only pool is printed.
  - The landmark cells carry our aligner's border and are printed, never headline (as PN1 section 8).

**Secondary:**
- MorDIFF, against its FRLL genuine pool.
- DiM, six families (DiM-A, DiM-C, Fast-DiM, Fast-DiM-ODE, Greedy-DiM, Greedy-DiM-S).

**Face-splice set:** H1, 598 CASIA-WebFace Poisson splices against 598 genuine photos (112 px native).

**Not read:**
- FEI (gtest): reserved by the main registration.
- The sealed sets (valx, FST, A12SP): only if the main registration assigns them, in a separate registration.
- FFHQ: development set by designation (12 Nov), never reported as a benchmark.

**Images:** every image goes through the scoring path registered for its detector. Our networks use the aligned 512 frame and `rescore.py`/`pn1_score.py` (logit without flip). The releases use the own-crop paths of RS1 / AD5. The manifests are pinned by sha256 in the pack.

## 3. Metrics (every detector under both forms)

**Standard form** (comparable with published numbers), per native cell:
- EER;
- BPCER@APCER 1, 5, 10 and 20%;
- AUC printed.

**Shortcut-controlled forms**, defined as in the audits (EV1 prereg; PN1 sections 5–6):

| Form | Per cell |
|---|---|
| History-matched | EER and BPCER@APCER 1/5/10/20% on each E7 cell |
| Own rule | APCER per family and BPCER on the native genuine pool, on each E7 pool and on the registered benign variants (JPEG 90/70/50, blur1, resample50 of FRLL) |
| Fixed-threshold transfer, τ_dev | APCER per family and BPCER on the native, E7 and benign-variant genuine pools |

- Released detectors in the fixed-threshold transfer form: their τ_dev equivalent is the EV1 threshold fixed on devbona (5% false alarms), as registered there.
- Exact Clopper–Pearson intervals for every rate. Bootstrap intervals for EER and AUC (persons as units, 2,000 draws, `default_rng(20261121)`).
- Family means:
  - over the five MAD22 families;
  - over the four non-border FRLL-Morphs families (StyleGAN and AMSL included, landmark cells printed);
  - over the six DiM families;
  - over MorDIFF.
- H1: AUC and EER native, plus own-rule and τ_dev rates.

## 4. Comparison set

| Group | Detectors |
|---|---|
| Released | MADation ViT-B/16 and ViT-L/14, SelfMAD, MixFaceNet-MAD (the checkpoints and scoring paths of RS1 / AD5) |
| Retrains (AD5) | MADation ViT-B/16 and ViT-L/14, SelfMAD, MixFaceNet-MAD at seeds 401–405, where finished and verified by the read date; otherwise printed "not available" |
| "No morph seen" reference | AD4's morph-free networks (M3, M3L), as registered there |
| Internal references (same data, same scorer) | PN1 arm A (plain recipe on our data) and, when B or Sb is frozen, the other one, at seeds 403–407 |

These internal references are read under the same rules, but they are not candidates.

## 5. What counts as matching or exceeding the state of the art (fixed now)

"Best comparison" for a cell is the comparison-set detector with the lowest value on that cell. A retrain counts by its seed mean. Each form is judged separately.

**Standard form:**
- **Matched** on a family mean if the frozen arm's mean EER ≤ the best comparison EER + 1.0 point, and the best comparison's EER lies within the frozen arm's seed range [min, max].
- **Exceeded** if the 95% bootstrap interval of (frozen mean − best comparison) lies entirely below 0, with persons resampled jointly.
- **Lost** if that interval lies entirely above 0.
- **Otherwise:** "comparable, not separated".

**History-matched form:** the same rules on E7 EER and E7 BPCER@APCER 5%.

**Own-rule and fixed-threshold forms:**
- **Exceeded** if the frozen arm's mean BPCER on the E7 pools and on the benign-variant pools is at most half the best comparison's, at an APCER family mean no worse than the best comparison's + 5 points.
- **Lost** if its BPCER is higher than the best comparison's on ≥ 2 of the 3 genuine pool kinds (native, E7, benign).
- **Otherwise:** "comparable".

**Claim scope:**
- MAD22, FRLL-Morphs and H1 results for a PN1-family network carry the label "seen during development" (section 6).
- MorDIFF and DiM carry "clean for this recipe".
- A state-of-the-art claim in the paper's abstract needs a "matched" or "exceeded" result on MorDIFF or DiM in the same form as on MAD22.

## 6. Exposure statement

`experiments/PN1_protocol-network-first-tests/BENCHMARK_EXPOSURE.md` is part of this registration. In short:
- **PN1-family recipes.** H1, corrected MAD22 (all cells) and FRLL / FRLL-Morphs (all cells and benign variants) were scored for every PN1 network of seeds 401/402, the tier-0 heads and the reference row. Choices of recipe, margins and marks were made after those numbers were seen: the selection of Sb, the 0.05 / −0.02 margins, P-c′, the C contrast, the threshold-transfer framing.
- **Fresh networks.** The fresh seeds (403–407), Sp and any MS1 network have never been scored on a benchmark. The networks are clean; the recipes are not, for H1, MAD22 and FRLL.
- **Clean for PN1 recipes:** MorDIFF and DiM were never scored by any PN1 network. FEI was not scored either (metadata only) and stays unread.
- **Released detectors and AD5/AD4.** Every benchmark cell above was read for them by the audits (RS1, EV1, AD4, C cue checks). These are not our recipes, so this does not taint them, but it is stated.

Every table prints the label of each cell.

## 7. One read

**Who.** The lead, or a person who did not tune the recipe, runs it once. The PN1 owner prepares the pack and does not see scores before the commit.

**Pack** (one tar, pinned by sha256 in the registration commit):
- the frozen networks' `last_trainable.pt` and `meta.json` (all seeds), and the internal references';
- base weights;
- `rescore.py` / `pn1_score.py` and the release scoring paths;
- the benchmark manifests (pinned);
- the τ_dev values;
- the reader script.

The reader is written and committed before the read and tested on development data only.

**Platform gate.** Before any benchmark row:
- rescore the amendment-13 FFHQ list with two pinned networks (A_s401, B_s402), with byte-identical scores required (shown for A100 SXM4 and PCIe);
- rescore 200 development rows of each frozen network against its FS1 scores, with max |Δ logit| ≤ 0.05.

If the gate fails, the read stops.

**Order.** Primary sets, then secondary, then H1, in one job. The results are committed unaltered with the pack hash. There is no re-run, except an infrastructure failure re-run unchanged.

**Reviews:**
- a pre-run review of this text and the pack;
- the author's go;
- a post-result review of the committed read;
- only then the paper text.

## 8. What the paper says under each outcome (fixed now)

| Standard form | Controlled forms | Paper statement |
|---|---|---|
| Matched or exceeded (incl. MorDIFF / DiM) | Exceeded | "On published benchmarks the method matches (exceeds) the state of the art, and under history-matched and fixed-threshold controls it removes the storage shortcut that the compared detectors use." |
| Matched or exceeded | Comparable or lost | "Competitive on published numbers; the shortcut controls do not separate it from the compared detectors." |
| Lost | Exceeded | "On the standard form the method trails the state of the art. Under history-matched pools and fixed thresholds, which remove the storage and resolution shortcut, it is better. We argue the standard form rewards that shortcut (the audit sections), and report both." |
| Lost | Comparable or lost | "The method does not improve detection; the contribution is the audit and the controlled protocol." |
| No method frozen | — | "Audit only: published detectors under standard and controlled forms; no new detector is proposed." |

- Every statement carries the exposure labels of section 6.
- No statement extends beyond the sets read.
- Threshold transfer to unseen genuine sources is claimed only if MS1's registered primary passed. Otherwise the paper says it is unsolved.

## 9. Open items for the author

1. The go itself.
2. Whether the sealed sets are part of FINAL or kept back.
3. Who runs the read.
4. Whether the AD5 retrains not finished by the read date are waited for, or printed "not available".
