# Review of CB1 amendment 7 "Black frame vs storage history" (results-reviewer, opus, 13 Nov 2026 about 10:12 CET)

Requested by the CB1 owner on the lead's instruction; reviewed state: smad-next commit faa19af (CB1 folder). Saved verbatim below.

---

## Verdict

**Needs qualification.** Part A is read correctly in direction, and it is stronger than the text says, but one interval is wrong because of a bootstrap bug. Part B's narrow statement holds: on the released detectors' own crop path, none of the pools in `cb1_released_rs1_bpcer.csv` has pure-black pixels. The inference drawn from it does not hold: "the rise = storage history plus a small aligner step". The history step is measured with history applied to our aligned frames on both sides of the comparison. Existing RS1 cells show that this aligned-frame history step can differ from history applied to the raw photos by up to 22 EER points, and can even reverse sign, in pools with no black pixels. So a frame effect other than black pixels exists and is not separated out. The table does not need a border-matched column for the own-crop rows. It does need its history column labelled "aligned-frame E7" with the aligned-native column next to it.

I recomputed the 60-row split from `cb1_released_rs1_bpcer.csv`: 0 mismatches against `border/history_split_own_crop.csv`. HEAD is 46cbf2e, but the CB1 folder last changed in faa19af, so the files are the ones under review.

## Findings

**F1 (major): the "history step" is not storage history alone; there is a non-black frame interaction.**
- Evidence: `RS1/rs1_history.csv`. Raw E7 files exist for DiM-A and Greedy-DiM, and their aligned E7 pools have 0 black pixels after the crop (`rs1_border.csv`, E7aln_dim_a and E7aln_greedy_dim = 0.0). Comparing history on raw photos with history on aligned frames, crop variant 1 (EER points):

| Release | DiM-A, raw | DiM-A, aligned | Greedy-DiM, raw | Greedy-DiM, aligned |
|---|---|---|---|---|
| ViT-B/16 | +34.4 [27.9, 40.1] | +52.9 [45.5, 59.2] | +49.5 | +61.7 |
| ViT-L/14 | −7.8 [−12.9, −1.9] | +14.2 [8.6, 20.8] | −4.0 | +10.8 |
| MixFaceNet-MAD | +41.2 | +48.1 | +38.1 | +46.8 |

  Variant 2 shows the same pattern. The aligner step alone is about 0 on DiM-A (ViT-B/16: aligned native 20.69 vs raw 20.59), so the difference is an interaction between aligner and history, or a difference in the E7 recipe. It is not additive.
- Why it matters: every FRLL landmark cell and every MAD22 cell in the table uses aligned-frame E7. "+18.97 history" for ViT-B/16 AMSL is therefore an upper-bound-type quantity that includes the frame, not pure storage.
- Fix: label the column "history-matched, aligned-frame E7 (our aligner + history)". Cite the DiM raw-vs-aligned contrast as the measured size of the interaction. Drop "plus a small aligner-path step".

**F2 (major): there is a black-frame effect on the own crop path, in the MorDIFF aligned pools; Part B does not mention it.**
- MixFaceNet-MAD, v1, MorDIFF:
  - Native EER 6.36 with raw genuine photos; 2.97 with aligned genuine frames, which carry 5.0% black (Galn_mordiff).
  - History effect +40.4 on raw photos; +20.2 on aligned frames.
  - The rise halves when the genuine side carries the frame, which is what you expect if MixFaceNet reads black as genuine.
- Not in the table rows (MorDIFF uses raw E7), so the table claim survives. But "the black frame contributes nothing on the own crop path" should be limited to the pools used in the table.

**F3 (moderate): bootstrap bug in Part A.**
- `src/CB1/border_mfn.py`, `auc_ci`: `reps.append((gt*W).sum()/max(W.sum(),1e-12))` counts a resample with no morph weight as AUC 0.
- Affected resamples: StyleGAN2 110/2000, AMSL 22/2000, WebMorph 0/2000.
- Recomputed with those resamples dropped:
  - StyleGAN2: 0.908 [0.706, 0.991], not [0.000, 0.990].
  - AMSL: 0.462 [0.295, 0.652], not [0.276, 0.651].
- The same pattern may be in the other SA1 scripts that copy this bootstrap. Worth a grep.

**F4 (moderate): the border-matched subsets are tiny, selected rather than random, and mislabelled.**
- How few people they cover:
  - n=26 AMSL morphs come from 13 persons.
  - n=10 StyleGAN2 morphs come from 10 persons.
  - n=74 WebMorph morphs come from 41 persons.
- Threshold label: "≤0.005, the genuine photos' range" is wrong. The genuine maximum is 2.3e-5, so 0.005 is about 200 times that. At exactly 0 black, WebMorph n=18 gives AUC 0.914 [0.817, 0.982].
- Selection: a morph is border-free because of its geometry (where the face sits, how much padding the alignment needs), so these subsets are not random samples.
- Fix: also report the dose-response by border quartile. It is monotone in all three families:
  - AMSL: 0.25 → 0.13 → 0.02 → 0.00
  - StyleGAN2: 0.89 → 0.87 → 0.80 → 0.51
  - WebMorph: 0.46 → 0.18 → 0.03 → 0.01
- Combined with the paired intervention already on file (AM2_B4 line 44: frame alone −38.8 logit, 0% of photos rise), this is strong evidence. The tiny subsets are not.
- AMSL at 0.46 is "at chance", not "no longer inverted".

**F5 (minor): two parts of the split are not what they look like.**
- The aligner-path step has no paired interval. For ViT-B/16 AMSL, aligned native 5.45 [2.99, 7.89] against raw 3.91 [1.94, 5.90] is within noise; one genuine photo is 0.49 points. The +6.4 for MixFaceNet-MAD AMSL needs an interval before anyone calls it "small" or "real".
- For StyleGAN2 and the MIPGAN cells, history is 0 by construction (E7 leaves the photo unchanged). Their "history-matched" rise is the aligner step alone and should not be presented as a history rise.

**F6 (minor): the SelfMAD split has no border reading on its aligned path.**
- `rs1_border.csv` covers SelfMAD's crop of raw files only, not the aligned native or aligned E7 frames. Our aligned genuine frames are border-free, so black pixels are very likely 0 there too. Say "not measured" rather than "absent".
- SelfMAD shows the F1 interaction as well: MorDIFF history +43.7 on raw photos vs +71.1 on aligned frames.

## Wording I would accept for the lead

> "On each released detector's own crop path, no genuine or morph pool behind the table's native and history-matched cells contains black-frame pixels (rs1_border.csv; MorDIFF aligned pools excepted, not used). A border-matched column is therefore not needed for those rows. The history-matched column there is not pure storage history: for FRLL landmark and MAD22 cells the history is applied to our aligned frames, and where raw-file history exists (DiM-A, Greedy-DiM) the aligned-frame history effect exceeds the raw-file effect by 7-22 EER points (ViT-L/14: raw −7.8, aligned +14.2 on DiM-A) without any black pixels. The column is labelled 'aligned-frame E7 (our aligner + history)' and the aligned-native EER is shown beside it. On our frames, morphs carry 3-26% black frame and photos none; MixFaceNet-MAD's AUC falls monotonically with border share and a frame-only edit moves its logit by −38.8 toward genuine, so our-frames numbers for released detectors carry a border caveat. A border-matched column is not feasible (no border-free FaceMorpher/OpenCV morphs; n=10-74 elsewhere)."

## What would close the gap

1. **Zero GPU, can be done now:**
   - Fix the bootstrap (drop empty resamples) and rerun Part A.
   - Add the border-quartile AUCs.
   - Compute paired person-bootstrap intervals for the aligner step from the RS1 score files.
   - Tabulate raw-vs-aligned E7 for MorDIFF, DiM-A and Greedy-DiM across all releases (already in `rs1_history.csv`).
2. **Needs the author:** raw-file E7 versions of the FRLL photos for the landmark families and MAD22, i.e. history without our aligner. That is resampling/storage code, which is an author-only item under hard rule 3. Once those files exist, scoring the released detectors is under 1 GPU-hour and separates the history step without the interaction.
3. **Optional, author item:** an aligned frame with the black padding filled by content, which would test MixFaceNet on our frames directly. This is also an author-only item.

Files:
- /home/narolski/smad-next/experiments/CB1_competitor-baselines-corrected-mad22/result.md (lines 186-244)
- /home/narolski/smad-next/src/CB1/border_mfn.py (`auc_ci`)
- /home/narolski/smad-next/experiments/RS1_own-crop-rescore/rs1_history.csv
- /home/narolski/smad-next/experiments/RS1_own-crop-rescore/rs1_border.csv (lines 118-143)
