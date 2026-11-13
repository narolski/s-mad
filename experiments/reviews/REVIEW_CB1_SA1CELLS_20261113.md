# Review of CB1 "SA1 gap item 10" released-detector cells (results-reviewer, opus, 13 Nov 2026 about 10:00 CET)

Requested by the CB1 owner on the lead's instruction; reviewed state: smad-next commit 4d5fede. Saved verbatim below.

---

**Results review: SA1 gap item 10, the released-detector cells (CB1 result.md:157-176, smad-next @ 4d5fede)**

**1. Verdict**

The numbers need qualification, not withdrawal. I recomputed or traced every value to its file and all of them match. The cells follow amendments 5 and 6, and the gates are reported correctly: the reproduction gate passed (median 0.0057, max 0.070) and the A43 consistency check passed (median 0.025, max 0.100).

The main problem is how the MixFaceNet-MAD (MFN) results are framed. The note says the release is "reversed on our frames, so −38.8 is not interpretable as a border cue". I think that gets it backwards. The −38.8 logit shift **is** a border cue, it points toward "genuine", and it accounts for both the C1b reversal and the split in the validity rule. Three smaller issues:
- The SelfMAD crop-path cell compares genuine pools from different score files with different score fields.
- The 4-ViTL cell reads a saturated detector as robustness.
- The 19-MFN cell leaves out the low catch rates.

**2. Findings (most severe first)**

**F1 (major): the "reversal" of MFN is a border effect, and the validity rule is in effect a border-matching test.** This answers your consistency question for 13 vs C1b.
- **A43 (row 13).** I read the border fraction of every arm from `border_frac` in `/mnt/t7/smad_heldout/a43/data/manifests/a43.csv`: medians 0.525 to 0.544 for arms A, B, B20, C, C20, D, D20 and E. R0 is `eval/mordiff/mordiff_bona/*_orig.png`. EV1 says these genuine MorDIFF frames share the tight frame (median 0.544, `AM2_B4_border_pairing.csv`). So every class has the same frame, and the rule passes (0.800 [0.732, 0.865]).
- **FRLL-Morphs (C1b).** Genuine borders are 0.000 and morph medians are 0.031 to 0.26 (EV1 result.md:88-90). This is where MFN reverses, with EERs of 75-98%.
- **AG1 (row 14).** I checked the zero-pixel share on 40 frames per pool. Camera R0 is 0.0 for FRLL, FERET and FRGC. PUB is 0.037 / 0.038. R2/R3/R4 are 0.040 to 0.049. So the validity contrast R0 vs PUB is border-mismatched, and it fails (0.548 [0.473, 0.623]).
- **Same file, both directions.** With the border held equal, the 65 px history shifts MFN by **+4.80** [4.45, 5.26] toward "morph". The frame alone shifts it by **−38.8**, with 0% of photos rising.
- **Dose.** Under our own crop the border is about 5-8% and the shift is −3.7 to −3.9. At 54% it is −38.8.

So: 13 passing and C1b reversing are consistent. Both follow from whether the two classes share a frame.

Rewrite for 5-MFN: "The frame alone lowers the score by 38.8 logits (0% of photos rise). This release reads the black border as genuine, which is consistent with its reversal on the FRLL-Morphs cells, where only the morphs carry a border."

Label the mechanism as post hoc and not reviewed.

**F2 (major): the SelfMAD crop-path cell (10-SelfMAD) mixes score files.**
- G_raw comes from A41 x7, using `logit_noTTA`.
- Galn_frll comes from A32-RSX `selfmad_own_eval.npz`. That file has only `score`, a probability (keys: id, score, cropped, ...). I could not establish whether that field is flip-averaged. Amendment 6 lists `logit_noTTA` only.
- The jump from 5.55 to 10.24 could therefore partly reflect the change of field.
- There is a zero-GPU bridge. The A43 SelfMAD own scores (`scores_a43.npz`, `logit_noTTA`) include 204 `frll_bona` rows from `eval/frllm/frll_bona/*_orig.png`, the same images. `analyse.selfmad_pools` currently skips them (the `else: continue` branch). Recompute with that pool before the cell is shown.

**F3 (moderate): the 4-ViTL cell is uninformative, not robust.**
- RS1 reports saturated genuine logits for ViT-L/14 on its own crop: median −12.80, SD 0.056 (SA1 19-ViTL).
- The same rule that flags 0.0% of FFHQ catches only 0.3% of AMSL and 4.3% of WebMorph.
- Rewrite: "Uninformative: the own rule flags 0.0% of FFHQ (n 1,934 / 1,997), but it also catches only 0.3% of AMSL (own crop, saturated)."

**F4 (moderate): the 19-MFN cell leaves out the low rates.**
- `rs1_pool_rates.csv` (v1) also gives FRLL FaceMorpher 83.1%, MorDIFF 26.6%, DiM-A 1.0%, Fast-DiM-ODE 0.0%, Greedy-DiM 10.2% and MAD22 Webmorph 14.2%.
- It also gives 95% intervals, which the cell omits.
- Add "diffusion families 0-48%" so the cell is not selective.

**F5 (moderate): the expression cell (16-MFN).**
- The C1b "our frames" change (−0.26) is measured where EERs are 75-98%. In that regime a change in the genuine class has no meaning for morph detection, so it should be shown as "not interpretable".
- The own-crop values are correct. I recomputed neutral-only minus all from `rs1_reproduction.csv`: v1 −0.45 / −0.62 / −0.99 / −0.49 / −0.37, mean −0.58; v2 −0.50 to 0.00.
- But they cover only 5 FRLL families, not C1b's 11 cells, and they carry no interval. Each family's interval is about ±4 points wide.

**F6 (minor): the AG1 descriptive values.**
- R2, R3 and R4 all share the same border (about 4-5%), so the AUCs between them are border-matched ranks. They are arguably meaningful as description.
- The flag rates are not. They use a threshold fitted on the border-mismatched R0 vs PUB contrast; for example, FRGC camera R0 is flagged 69.5%.
- Row 14's metric in the matrix is the flag rate, so keep the cell as "not interpretable". Show the AUCs only in the detail table.

**F7 (minor): differences from the existing row-13 cells.**
- The 13-MFN bootstrap uses B 2,000 with seed 0 (only the first 2,000 of 10,000 multinomial draws); AD1 used 10,000.
- 5-ViTL's +0.067 sits on a saturated scale: all genuine logits on our frames fall within 0.3 logit. Its logit value cannot be compared with ViT-B/16's +0.42, so lead with the share of photos that rise (93%).

**3. Answers**

**(1) Do the values follow from the files and match the existing definitions?**
Yes for every value. Definitions match the existing cells, except:
- 16: 5 families instead of 11.
- 10-SelfMAD: mixed score files and fields (F2).
- 4-ViTL: own crop, where the ViT-L/14 cells referred to our frames.

**(2) Should the reversed or near-chance MFN cells carry numbers?**
Split by row:
- **5-MFN: yes, keep the number.** There is no validity rule for row 5, and the number measures exactly this row's cue.
- **14-MFN: show "not interpretable" only**, as the registered rule requires.
- **16-MFN: put the own-crop value in the cell** and show our frames as "not interpretable (reversed)". This changes the presentation relative to amendment 6 and should be logged as a post-hoc presentation choice.
- **13-MFN: interpretable.** It is valid and border-matched, and it is consistent with C1b (F1).

**(3) Over- and under-claims**
- Under-claim: "not interpretable as a border cue" (F1).
- Over-claims: 4-ViTL (F3) and the selective 19-MFN list (F4).
- The phrase "makes photos look more genuine" should say "to this release".

**(4) Proposed cell text, one line per cell**

| Cell | Proposed text |
|---|---|
| 5-ViTL | Frame alone +0.07 logit [0.06, 0.08], 93% of photos rise (our frames, saturated scale); own crop +0.02/+0.03 |
| 5-MFN | **Used, toward genuine:** frame alone −38.8 logit, 0% rise (our frames); own crop (5-8% border) −3.7/−3.9 |
| 13-MFN | Partly: morph vs reconstruction 0.59 [0.53, 0.66] (our frames, validity passed); own crop 0.49 [0.41, 0.57]; crop-path dependent |
| 14-MFN | Not interpretable (validity rule failed: R0 vs published 0.55 [0.47, 0.62]; border-mismatched) |
| 16-MFN | Change under 1 pt, own crop (5 FRLL families, mean −0.6); our frames reversed, not interpretable |
| 10-SelfMAD | Crop-path dependent: FRLL 5-family mean EER 5.6 → 10.2 with aligned genuine frames (pending the logit bridge, F2) |
| 4-ViTL | Uninformative: 0.0% of FFHQ, but the rule catches 0.3% of AMSL (own crop, saturated) |
| 19-MFN | Own 0.5 rule: 0.5% of photos flagged; catches 10-94% of FRLL/MAD22 morphs and 0-48% of diffusion morphs (own crop) |

**4. New hypotheses**

**H-new-1: MFN's 'rel' score falls steeply with black-border share.**
- Prediction: within the genuine class of the eval frames, logit falls monotonically with border share. On FRLL-Morphs, restricting to border-matched pairs restores an AUC above 0.5.
- Test: zero GPU, using A12REL MFN eval scores (released weights, unsealed by the 31 Oct ruling) and the EV1 `AM2.json` border fractions.
- Falsified if: the slope's 95% interval includes 0, or matched AUCs stay at or below 0.5.
- Timing: before Nov 8 at no GPU cost; needs a ledger amendment.

**H-new-2: the 10-SelfMAD rise survives a same-field genuine pool.**
- Prediction: with the A43 `logit_noTTA` pool the mean EER stays above 8.
- Falsified if: it is below 7.
- Cost: zero GPU.

**5. Next experiments (ranked)**

| Experiment | GPU-h | When | Decides | Approval |
|---|---|---|---|---|
| SelfMAD logit bridge (A43 `frll_bona`) | 0 | now | Whether the 10-SelfMAD cell is shown | none (existing files) |
| MFN logit against border share, and border-matched FRLL-Morphs AUC | 0 | now | Whether F1 goes into the paper text | amendment (post hoc) |
| Border-matched AG1 MFN AUC table, descriptive only | 0 | now | 14-MFN detail line | presentation note |

**6. Risk**

If the border cue is real, any statement that our aligner's frame is "neutral" for released detectors is wrong. The protocol tables that score released detectors on our frames should carry a border-matched caveat.

Note for whoever reruns these: `analyse.selfmad_pools` (`/home/narolski/smad-next/src/RS1/analyse.py`) skips the A43 `frll_bona` rows. Including them is the first step of the F2 bridge.
