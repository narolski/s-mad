<!-- Independent results review by the results-reviewer agent (on Opus), 11 Nov 2026 about 23:55 CET; saved verbatim by the lead. -->

# Review: morph-free networks, CLIP ViT-B/16 arm (AD4), 11 Nov 2026

## Verdict
**The conclusions need qualification, and one is partly wrong.** Conclusion 1 holds in substance: it agrees with the earlier morph-free run (A47 I-3: three seeds, another machine, same result). But it holds only on our frames, and "never saw a morph" hides what the network was actually trained to do. Conclusion 2 is wrong for MorDIFF and only partial for DiM-C. Where the error does reverse, the history-matching control (E7) has overshot: it made the genuine photos softer than the morphs. It does not show "chance". The fixed-threshold statements are close to true by construction and leave out one important rate. Conclusions 3 to 5 need small rewrites.

Reviewer readings below are unregistered. I made them read-only from the five morph-free `scores_eval.npz` files and two `scores_train.npz` files (copies in `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/ad4rev2/`), from the PNG file sizes under `/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401/data/eval/`, and from `ad4_cells_m3.csv`.

## Findings (most severe first)

1. **Major: what the task teaches.** The prereg (lines 8–14) defines the two classes as SMDD synthetic renders (label 0) against their own copies shrunk to 31% and enlarged again (`degrade R 0.3125`, label 1).
   - The network is therefore a resampling or softness detector, trained on GAN-rendered faces.
   - Training saturates. Natives sit at a logit of about −3.65 and copies at +3.60 (seeds 401 and 403, 5th to 95th percentile within 0.03).
   - "Never saw a morph" is literally true but misleading. The right wording: "trained with no morph and no blended image, only to flag shrink-and-enlarge copies of synthetic faces".
   - Averaging two imperfectly aligned faces is itself a softening of the image. So conclusion 1 does not show that the cells have no morph signal. It shows that a softness detector passes them.

2. **Major: conclusion 2 is false for MorDIFF and partial for DiM-C** (Table 1).
   - MorDIFF history-matched EER is 2.9% (per seed 0.4–5.4), AUC 0.996. DiM-C is 21.7%, AUC 0.85. Matching the history does not remove these networks' cue on either cell.
   - Median logits show it directly. MorDIFF morphs −1.41 to −0.57 against −3.33 to −3.12 for the history-matched genuine photos (seeds 402–404). For DiM-A, DiM-C, Fast-DiM and Fast-DiM-ODE the two groups are equal to within 0.1 logit.
   - Only those DiM families lose the cue under matching.

3. **Major: a reversed AUC is a reaction to the E7 processing itself.**
   - E7 applies the same kind of operation as the training positives (`prep_eval` shrink-and-enlarge). A network trained to flag it will flag E7 photos.
   - PNG size of our frames, used as a crude softness measure (smaller file = softer), separates history-matched genuine photos from morphs at AUC 0.10 (Fast-DiM-ODE) and 0.04 (Greedy-DiM). The history-matched genuine photos are softer than the morphs, so E7 over-matches.
   - Across the seven diffusion history-matched cells, the network's AUC roughly follows the file-size order (MorDIFF and DiM-C highest on both).
   - Wording: "the control removes the cue or overshoots it", never "chance". Also call it **resolution history**, not storage history: E7 imitates shrink-and-enlarge, not file format or compression.

4. **Major: the fixed-threshold statements.**
   - Everything genuine sits at the trained floor, so "0.0% flagged at the 0.5 rule" is near-automatic.
   - The FRLL-5% threshold lies at p = 0.027–0.036, a hair above the floor. "Flagged" there means "just off the floor".
   - "100% of history-matched genuine photos flagged" follows from the training task and says nothing new about the benchmark.
   - The summary leaves out that 50.7% of MorDIFF's own native genuine photos are flagged at FRLL-5% (per seed 1.0, 70.1, 54.9, 87.7, 39.7%). MorDIFF's genuine files differ from FRLL's (mean PNG 180 KB against 372 KB; the 54% border in the MorDIFF frame noted in the review of the fixed-threshold re-read, EV1).
   - Always print the flag and miss rates together. Also say that DiM natives are "passed" with morph logits about 0.15–0.2 above the floor (about 3% of the trained span), while 86–100% are missed at 0.5.

5. **Major: "our frames" limits conclusion 1.**
   - PNG size alone separates the native cells at AUC 0.95–1.00 (MAD22 FaceMorpher 1.000, MorDIFF 0.999, DiM-C 0.992, FRLL FaceMorpher 0.998, AMSL 0.979).
   - Within each cell, the network score correlates with smaller file size (Spearman 0.38–0.84).
   - Our aligner's border around smaller morph files lowers file size, so softness and border are confounded.
   - Conclusion 1 is about our preprocessing until the own-crop re-score (RS1) or a border control exists.

6. **Medium: seed means hide two opposite behaviours.**
   - Greedy-DiM history-matched AUC per seed is 0.014, 0.987, 0.294, 0.949, 0.168. "About 50%" is an average of networks that separate strongly in opposite directions; none is at chance.
   - The same pattern of seeds appears on Fast-DiM-ODE history-matched (0.10, 0.38, 0.09, 0.30, 0.02) and on MIPGAN-I (0.02, 0.33, 0.07, 0.44, 0.06).
   - Seed 401 is the least saturated network (genuine −3.49, history-matched −1.0). It also drives the reproduction miss (8.72%), Greedy-DiM 11.2% and FRLL OpenCV 40.2%.
   - Report the per-seed range wherever the range is wider than 30 points. No seed means for reversed or bimodal cells.

7. **Minor: the reproduction flag.**
   - The miss is 1.0 point over a bound on a secondary cell. It is driven by one of five new seeds (seeds 401–405 are not A47's seeds 1–3).
   - MorDIFF (0.0 in all five) and the A47 numbers (MorDIFF 0.00, DiM 0.00 to 1.17%) agree. Conclusion 1 survives the flag as "seen on two stacks, cluster rerun pending".
   - Keep the flag. Do not let it weaken conclusion 1 beyond that wording.

8. **Minor: multiplicity.**
   - About 34 rows; only seven are registered (one primary, six secondary). The native margins (−33 to −41 points) do not need correction.
   - Borderline descriptive rows should not be headlined: DiM-C history-matched (margin −13.5 [−22.0, −6.5]) and MAD22 Webmorph "passable" (3/5 seeds, above 15% in 5/5).
   - "Below every reference" on landmark cells is the right wording; the untrained network already reaches AUC 0.72 there.

9. **Minor: conclusion 4.**
   - The label-permuted networks partly learned the true task: true-label accuracy 0.40–0.69 (seed 403: 0.686).
   - That makes them conservative references, which is fine. They show the effect needs the true labels. They do not show which feature carries it.

10. **Conclusion 3 (MAD22 FaceMorpher).**
    - Morph logits are +1.6 to +3.2, near the "resampled" class. History-matched genuine photos sit at −3.4, and file size still separates at AUC 0.93 after matching.
    - Say "not removed by resolution-history matching; candidates: surround, watermark, border, blending softness (untested here)".
    - FRLL landmark cells keep AUC 0.95–0.97 after matching. The cue is not identified there; blending softness and border are the leading candidates.

## Corrected wording

**Notebook:** "On our frames, CLIP ViT-B/16 LoRA networks trained only to flag shrink-and-enlarge copies of synthetic SMDD faces (no morph, no blending; 5 seeds; flagged 'not reproduced on this stack', one gate cell 4.0 against 3.0) reach 0.0% EER on MorDIFF and 0.0–4.0% on six DiM natives, against 37–61% for five label-permuted networks and the untrained network. The same holds for FRLL AMSL, FaceMorpher and Webmorph (1.0–4.1%) and corrected MAD22 FaceMorpher (0.0%). Matching resolution history removes or reverses the cue on DiM-A, Fast-DiM and Fast-DiM-ODE: the history-matched photos come out softer than the morphs. It does not remove it on MorDIFF (2.9%), DiM-C (21.7%), MAD22 FaceMorpher (0.1%) or the FRLL landmark cells (7.8–11.1%). Greedy-DiM cells split by seed (AUC 0.01–0.99). Fixed thresholds sit at the trained floor: 50.7% of MorDIFF's own genuine photos are flagged at FRLL-5%."

**Paper:** "In our preprocessing, a network trained only to detect resampling of synthetic faces, which never sees a morph or a blended image, reaches 0.0% EER on MorDIFF and at most 4.0% on six DiM families (five seeds; label-permuted and untrained references 37–61%). Low error on these cells therefore cannot by itself be read as evidence of morph detection."

## New hypotheses

**H-new-1: a single softness measure explains the network's scores.**
- Prediction: a sharpness statistic computed only inside the face region (FFT high-frequency energy; a measurement, not an image operation) reproduces the network's per-cell ranking. Spearman with the network score is at least 0.7 in the native cells.
- Falsified if the face-only statistic gives AUC below 0.7 on cells where the network reaches at least 0.99.
- Cost: 0 GPU, one single-thread CPU job of about 20 minutes. Fits before 14 Nov. The lead should confirm that an FFT measurement falls outside hard rule 3.

**H-new-2: E7 overshoot causes the reversal.**
- Prediction: the network's AUC on history-matched cells rises monotonically with how soft the morphs are relative to the history-matched photos.
- Falsified if, at a matched softness level, the AUC stays below 0.4.
- A graded control needs resampling code, so it is an author item. The rank test on the existing seven cells costs 0 GPU.

**H-new-3: the border, not resolution history, carries MorDIFF and MAD22 FaceMorpher.**
- Prediction: setting the region outside the face to a constant value in both classes raises MorDIFF history-matched EER above 15%.
- Falsified if it stays at 5% or below.
- Cost: re-score the five existing networks, about 0.5 A100-hours. Needs a registration and the lead's yes that blanking is allowed (EV1 follow-up 3 proposes it). Fits before 14 Nov.

**H-new-4: the generator texture prior explains the reversed MIPGAN cells.**
- The networks score MIPGAN at or below SMDD-native level (seed 401: −3.61 against FRLL genuine −3.49 and SMDD natives −3.64).
- Mechanism: label 0 was StyleGAN renders, so generator texture reads as "unprocessed". MIPGAN's file sizes equal those of the genuine photos.
- Prediction: StyleGAN non-morph faces held out of training score below FRLL photos.
- Falsified if their median logit is at or above the FRLL genuine median.
- Cost: about 0.1 A100-hours of scoring with a new registration.

**H-new-5: blending softness, not the second identity, carries the FRLL landmark cells.**
- Prediction: same-person blends of two captures (the ladder's same-person morphs, existing images) are flagged as often as two-person morphs.
- Falsified if the gap in AUC is above 0.1.
- Cost: about 0.2 A100-hours. Needs a registration.

**H-new-6: the seed pattern is fixed by the seed.**
- Prediction: the WCSS rerun of seeds 401–405 reproduces the per-seed pattern on Greedy-DiM history-matched and MIPGAN (same sign per seed).
- Falsified if two or more seeds flip.
- Cost: already queued. It also tells us whether the stack matters for the reproduction flag.

## Next experiments (ranked by information per GPU-hour)

| # | Experiment | GPU-h | When | What it decides | Approval needed |
|---|---|---|---|---|---|
| 1 | Register and print the reviewer readings above (floor logits, MorDIFF genuine flag rate, file-size null per cell) | 0 | now | wording of conclusions 2 and 4 | none (descriptive) |
| 2 | Face-only sharpness null (H-new-1) and rank test on history-matched cells (H-new-2) | 0 | 12 Nov | whether "softness detector" is the mechanism | lead (rule 3 check) |
| 3 | Border-blanked re-score of the five networks (H-new-3) | 0.5 | 12–13 Nov | whether MorDIFF and FaceMorpher survive outside our frames' border | new registration; lead |
| 4 | Same-person blends and StyleGAN non-morph pool scored by the five networks (H-new-4, H-new-5) | 0.3 | 13 Nov | "averaging" against "second person"; MIPGAN reversal | new registration |
| 5 | ViT-L/14 arm reading (running) | 0 extra | 12 Nov | whether the effect is specific to the recipe (the morph-trained ViT-L/14 recipe is itself above 10% on four DiM/MorDIFF cells) | none |
| 6 | WCSS rerun of the ten ViT-B/16 tasks (H-new-6) | 9 | when WCSS reopens | the reproduction flag | registered |
| 7 | Own-crop re-score (RS1) of the morph-free networks | about 0.5 | before 14 Nov | conclusion 1 outside our frames | RS1 amendment |

## Risks to the story
- If RS1 or the border-blanked re-score removes the native passes, conclusion 1 becomes "our aligner's cue" and not "the benchmark's cue". Hedge now: write "in our preprocessing" everywhere.
- If H-new-5 holds, the landmark cells measure blending, which is a real morph trace. The paper must then not say those cells "measure nothing", only that the trace is not specific to a second identity.
- If H-new-6 fails, every per-seed statement depends on the stack. Keep the claims at the level of the five-seed range.

Files: `/home/narolski/smad-next/experiments/AD4/ad4_reading_m3.md` (Tables 1, 2, 3b and 4), `/home/narolski/smad-next/experiments/AD4/prereg.md` (lines 8–14 and 43–50), `/home/narolski/smad-next/experiments/AD4/ad4_cells_m3.csv`.
