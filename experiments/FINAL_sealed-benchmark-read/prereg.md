# DRAFT registration: the sealed final benchmark read (FINAL), v2

**Not to be executed without the author's explicit go.** The author answered the design decisions on 12 Nov (section 10); the execution go for the read itself is still pending and needs the freeze outcome first. This is a draft. No benchmark file was opened to write it. No score of any candidate network on any benchmark exists for the fresh seeds or later fits.

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

**Amended 13 Nov 2026 (`date` at writing: Fri Nov 13 07:04:46 AM CET 2026) on the author's approval.** The author, asked "adopt the
replacement storage test and the amended freeze rule, yes or no?", answered "Yes". The replacement test is registration
C2P in `experiments/PN1_protocol-network-first-tests/prereg.md` (commit 2715e488bf87ad81a93cc4fede7b5899d97bc225). Lead
decision recorded with it: H-new-1 must be "falsified" (stricter than "not supported"). Superseded text: the previous
steps 1-3, which required FS1 contrast 2 "replicated"; FS1 contrast 2 was read "uninformative" (13 Nov 06:38, the plain
arm's positive control failed) and that result is reported beside contrast 2-prime in the paper.

Inputs: the registered readings only.
- FS1 contrast 1: `prereg_fresh_seeds_v4_frozen.md`, git ac585b7 (read 13 Nov 06:38: "replicated", 5 of 5 seeds).
- FS1 contrast 2 (reported, not deciding): read "uninformative".
- Contrast 2-prime, H-new-1 and the platform gate: registration C2P, commit 2715e488bf87ad81a93cc4fede7b5899d97bc225.
- Sp: registration 1b8fe48.
- MS1 part 2 as registered at commit f748da4195709ee84c8cc9872c5aac1d9007a049 (co-primaries P1-S on the Chicago Face Database and P1-T on the TT1 pools, each at p ≤ 0.025; arms Sb, SbM3, SbV; guards G1–G3), with deviations MS1-D1 (5eadc1b) and MS1-D2 (86b4b69).

No benchmark number enters.

1. **Sb** is frozen if all hold:
   - FS1 contrast 1 is "replicated" (it is);
   - contrast 2-prime "passes" for Sb, with A's positive control met (C2P.3);
   - H-new-1 is "falsified" for Sb (C2P.4).
2. **Otherwise, B** is frozen if contrast 2-prime "passes" for B with A's positive control met AND H-new-1 is
   "falsified" for B (contrast 1 is not required for B).
3. **Otherwise, no method** is frozen. The read is then an audit of the comparison set only, with no candidate claim.

Both the failed original contrast 2 and contrast 2-prime are reported in the paper, with the disclosure that contrast
2-prime was registered after the original failed on its control and that its margins were set knowing the FS1 effect
sizes on other FFHQ persons (fm61 replicates FS1 on new persons; amsl112 carries the evidential weight).

**MS1 rule (B3).** The three-source version is frozen only if both:
- the MS1 primary is "supported", meaning both co-primaries (P1-S and P1-T) are supported as registered in MS1 prereg.md part 2 at commit f748da4195709ee84c8cc9872c5aac1d9007a049;
- every MS1 guard (G1–G3) holds, as registered there.

If MS1 is unregistered, unread, or B is frozen, the single-source arm is frozen. MS1 has no B arm.

**Second backbone (BB2; author: "do the second backbone").** The second-backbone arm of the frozen recipe (experiment BB2, its registered fits) is scored in the same sealed read as a robustness row, never as an alternative method to pick from.

Sp's outcome does not change the frozen arm; it only qualifies the claim. The FS1 printed reads R1–R6 and the amendment-15 baseline do not change it either.

**Networks read.**
- Every fresh seed of the frozen arm: seeds 403–407, or all of MS1's seeds.
- One network per seed, last checkpoint, no seed picking, no ensembles and no score fusion.
- A lost seed is reported as lost and never replaced.
- Per cell: every seed's value, the mean, the SD and the minimum and maximum.

Thresholds (τ_dev from both pools, and the own rule) are fixed before the read from development scores. They are committed with the pack. No threshold is taken from any benchmark.

## 2. Sets and cells (B2)

**Confirmatory (author: "Yes, please.").** These are read once, in the same single read:
- **FEI gtest** (`smadcvpr_data/manifests/gtest.csv`, named from metadata only). It holds FEI genuine photos (neutral 198, smiling 187) and 1,000 StyleGAN W+ morphs (500 neutral, 500 smiling), with genuine photos no network of ours has seen. Caveats from the record: the G-test generator (StyleGAN W+) was used in the earlier MADMamba program, and FFHQ-Morphs, our development set, has a stylegan_wplus family that no PN1 network has scored.
- **The sealed sets.** The candidates are named only from the main registration's documents (10_ASSET_INVENTORY.md, mambamorph-code CONCLUSIONS.md, PLANNING_RECORD.md). No sealed file was opened.
  - **VAL-X** (`smadcvpr_data/manifests/valx.csv`): the sealed selection set built from the val10 FRGC/FERET subjects. These persons were excluded from every PN1 training, but they come from our training databases. VALX-A (`valx_a.csv`) is the allowed selection subset and was used for selection in the earlier program.
  - **FST** (the "final sealed test"): F1 splice and F4 diffusion components. CONCLUSIONS.md says it "has not been delivered" and is "not built with its diffusion family". Whether it exists on disk, and what it contains, is unknown.
  - **A12SP** ("tool diversity", ledger A12-SP): an A12 side-study set kept sealed. Its contents are not described in the documents read.
  - **Ambiguity for the author:** whether FST exists and which of its parts are assigned; what A12SP contains and whether it is a test set at all; whether VAL-X counts as confirmatory, since its persons come from our training databases although they are identity-disjoint.
- **The morph side of MorDIFF and DiM.** Label: "morphs unseen; genuine pool seen".

**Reported, labelled "seen during development":** MAD22, FRLL-Morphs and H1.
- The author's stated goal is a comparison with the state of the art on MAD22 and FRLL-Morphs. So a full standard-form table is reported for both, labelled, but it is not the confirmatory endpoint.

The sets:
- **Corrected MAD22** (`/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z`): FaceMorpher, OpenCV, Webmorph, MIPGAN-I, MIPGAN-II; genuine = the 204 FRLL photos.
- **FRLL-Morphs.** The headline is StyleGAN only, the only border-free family (M1). The landmark families (AMSL, FaceMorpher, OpenCV, Webmorph) carry our aligner's border; their mean is printed.
- **MorDIFF**, with the corrected MorDIFF crop of RS1 amendment 7 for the releases.
- **DiM**, six families.
- **H1**: 598 CASIA-WebFace Poisson splices against 598 genuine photos.

**Genuine pools.** Every cell is printed with the full genuine pool and the neutral-only genuine pool (the expression cue, C1).

**Not read:** FFHQ (development set by designation), and any sealed set the author does not confirm after the ambiguity above is resolved.

## 3. Metrics and endpoint

Every detector is reported under every form.

| Form | Per cell |
|---|---|
| Standard | EER; BPCER@APCER 1, 5, 10 and 20%; AUC printed |
| History-matched | EER and BPCER@APCER 1/5/10/20% on each E7 cell |
| Own rule | APCER per family; BPCER on the native, E7 and benign-variant pools |
| τ_dev | as own rule |

Exact Clopper–Pearson intervals are printed for every rate.

**Single confirmatory endpoint (M2).** The τ_dev form on the confirmatory cells: APCER per family at τ_dev(i), and BPCER on the E7 pool, combined as (mean APCER + BPCER)/2. It is read on the confirmatory cells, with Holm correction across all of them:
- FEI gtest (neutral and smiling halves pooled);
- each assigned sealed set;
- the MorDIFF family mean;
- the DiM family mean.

Everything else is descriptive. The author accepted this endpoint ("Yes."); the standard form is secondary.

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
| AD5 retrains (seed means) | MADation ViT-B/16, MixFaceNet-MAD and MADation ViT-L/14 at seeds 401–405 (required); SelfMAD if it finishes |
| Competitor baselines (CB1) | as registered in experiment CB1, by the same cut-off |
| Reference lines (printed only, never "best") | AD4's morph-free networks (M3, M3L); PN1 internal arms (A, and B or Sb, whichever is not frozen) |

**Cut-off (author: "Wait for retrains").**
- The read waits for the AD5 retrains and the CB1 baselines until **14 Nov 2026, 18:00 CET**, and starts after that cut-off and after the freeze.
- A retrain method counts only if at least 3 of its 5 seeds have verified result tars by the cut-off. Its row is the mean over the seeds present, with the count printed.
- A method with fewer than 3 seeds, a CB1 baseline not finished, or SelfMAD unfinished: printed "not available".
- Nothing is added after the read starts.

**Definition:**
- **Best comparison** = the lowest value among released checkpoints, AD5 retrain seed means and CB1 baselines only.
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

**Who runs it (author: "You!").** The lead runs the read. The disclosure stays: the lead is not blind (endorsed the Sb refit after H1 was seen). Safeguards that make blindness unnecessary:
- the freeze rule is mechanical;
- the pack and reader are pinned by sha256 before the read;
- outputs go to a sealed file shown only after the whole job finishes;
- no re-run;
- independent review before and after.

The PN1 owner prepares the pack and sees no score before the commit.

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

**Prediction (M5), stated now.** The frozen arm's E7 EER on MorDIFF/DiM is ≥ 30%. The releases' low standard-form EER there is read as render-path/storage detection (AD4, RS1). No claim is pre-committed either way (author: "only if we cannot propose SOTA"): the abstract's claim is whatever the registered criteria of section 5 give on the confirmatory endpoint.

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

**Deliverables (author: "sure"), with the files that feed them:**
- **Source-by-source protocol table.** Training sources against test sources. Feeds: PN1 README section 3; MS1 prereg.md; TT1; the FINAL manifests.
- **Ablation table** (A, B, Sb, Sp, SbM3, SbV). Feeds: `tier_fs/fs.json`, `tier_fs/sp.json`, the MS1 reader output, `tier1_a14/*.json`.
- **Paired seed tests.** Sign / Wilcoxon over seeds per contrast. Feeds: the same reader outputs; computed in the readers.
- **Compute disclosure.** GPU-hours including audits and rentals. Feeds: each experiment's compute section; the lease folders' LIVE.json / guard logs.
- **Limitations.** Threshold transfer unless MS1 passes; the shared 204-photo FRLL genuine pool; one generator per family; the second backbone (BB2). Feeds: this file, BENCHMARK_EXPOSURE.md, MS1 and BB2 results.

| Item | What | Cost by 14 Nov |
|---|---|---|
| Second backbone | run as experiment BB2 (author: "do the second backbone"); scored as a robustness row in the sealed read | BB2's own registration |
| Cross-dataset protocol table | training sources against test sources (FRGC/colorFERET, +FFHQ in MS1; tests: ladder, FFHQ, benchmarks) | 0 (writing) |
| Ablation table | A, B, Sb, Sp, SbM3, from registered development reads | 0 compute once FS1, Sp and MS1 are read |
| Paired seed tests | sign / Wilcoxon over seeds for each ablation contrast | 0 (in the readers) |
| Compute disclosure | GPU-hours including audits and rentals | 0 (collect from records) |
| Limitation statements | thresholds do not transfer to unseen genuine sources unless MS1 passes; all benchmarks share one genuine pool of 204 FRLL photos | 0 |

## 10. Author decisions (answered 12 Nov about 23:50 CET; recorded `date`: Thu Nov 12 11:30:53 PM CET 2026)

1. **Confirmatory set: "Yes, please."** FEI gtest and the sealed sets are assigned as confirmatory (section 2). The ambiguity about which sealed sets exist and what they contain is listed there, for the author.
2. **Endpoint: "Yes."** The development-threshold (τ_dev) form is the confirmatory endpoint; the standard form is secondary.
3. **Who runs the read: "You!"** The lead runs it, with the disclosure and the safeguards of section 7.
4. **Retrains: "Wait for retrains."** The cut-off rule is in section 4: 14 Nov 18:00 CET; ≥ 3 of 5 seeds per method; CB1 baselines included.
5. **SOTA on diffusion: "Well, only if we cannot propose SOTA... ;)"** The prediction and outcome table are kept, but there is no pre-commitment to "no claim": the claim is whatever the registered criteria give.
6. **Second backbone: "do the second backbone".** Experiment BB2 is scored in the same read as a robustness row (section 1).
7. **Writing items: "sure".** The deliverables are listed in section 9.

8. **Freeze rule amended (13 Nov 2026): "Yes"** to "adopt the replacement storage test and the amended freeze rule, yes
   or no?" (relayed by the lead; recorded Fri Nov 13 07:04:46 AM CET 2026). Section 1 above; registration C2P at 2715e48.
9. **Not yet decided (proposal, awaiting the author):** the confirmatory operating point (post-result review of FS1,
   F10). At τ_dev(i) every arm and seed flags 96-98% of FFHQ genuine photos, so BPCER at τ_dev(i) on an unseen genuine
   pool reads about 100%. PROPOSED, NOT IN FORCE: "The confirmatory endpoint is AUC and EER within each cell; BPCER and
   APCER at the own rule, at τ_dev(ii) and at τ_dev(i) are printed beside them, never deciding; M4's 'the decision uses
   (i)' is withdrawn." Until the author answers, decision 2 above stands.

The execution go for the read itself is still pending: it needs the freeze outcome first.
