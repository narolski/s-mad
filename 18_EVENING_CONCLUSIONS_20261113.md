# Evening conclusions and freeze statement, 13 November 2026

Written by the lead at 17:45 CET, as promised in `16_PLAN_NIGHT_12_TO_13_NOV.md` (goals for 18:00). Plain English. Every statement below rests on a reading that was registered before it was computed and checked by an independent reviewer, unless it is marked otherwise. The review file is named for each. Experiments are named by what they do, with the ID in brackets. All readings of our own networks are on development data: no benchmark set has been read.

## Freeze statement

**No method is frozen today.** The freeze rule (final protocol, section 1, as amended on the author's approval at 6691adc) takes as its input the replacement storage test on the five fresh seeds 403-407 (contrast 2-prime [C2P]). That test was read once and its registered outcome is "uninformative": it was scored on a different GPU model with a different precision setting from the one that produced the stored scores, and the platform check removed every plain-training network, which is the control (REVIEW_PN1_C2P_20261113). The fault was in the set-up and was the lead's to catch. A re-run on the training platform is drafted and pre-run checked (amendment C2P-R); it needs the author's yes and has not run. Today's ablation on five other seeds cannot stand in for it, and its review warns against switching arms after seeing its data.

The candidate remains: protocol negatives plus face-spliced morphs with matched negatives, CLIP ViT-B/16 with LoRA (arm Sb).

## What the candidate is, on today's evidence

1. **It detects blending inside the face.** It flags 0 of 100 seam-only images and separates same-person splices from seam-only ones at 0.86-0.93 (REVIEW_PR1_PART1). Its advantage on landmark morphs over the protocol-only arm and over plain training has replicated on ten seeds across two platforms (+0.15 to +0.21 and +0.12 to +0.14 on the newest five; REVIEW_AB1). It is not shown to exceed the best single hand-made statistic (0.873-0.906 against 0.886).
2. **Its storage reaction is small against a working control, but no registered storage verdict is positive.** On five new seeds, plain training raises its flag rate on stored genuine photos by 27-39 points at the trained size and 6-15 at an untrained size; the candidate by at most 4.5 and 2.1. The registered verdict is "inconclusive" (two seeds miss a two-sided bar by moving toward genuine), and the candidate's pass at the untrained size does not replicate on fresh seeds (REVIEW_AB1, REVIEW_SE1_A100). We may not write "removes". No single component of the protocol carries the reduction.
3. **Its decision rule transfers to unseen genuine sources.** On about 21,000 photos from eight unseen low-resolution sources the protocol arm stayed within its rule on all seven seeds and the candidate on four of five fresh seeds (REVIEW_TT1_FS). On 865 NIST mugshots all three arms stayed within the rule, the candidate flagging 0.1-0.5%; the false alarms that occur sit in small images whose faces are enlarged about three times.
4. **It has no demonstrated second-identity signal.** It flags 83-90% of same-person morphs and 31-48% of same-person splices; on new persons the margin between two-person and same-person splices falls from about 4-5 to about 1-2 logits (REVIEW_PR1_PART1). On GAN and diffusion images it responds to the rendering: it flags 78-90% of GAN renders of a single photo, and on every contrast that isolates a second identity it is no better than hand-made statistics (REVIEW_PR1_PART2, PART3).
5. **It reacts to an image border.** With a border blanked into camera photos it flags 2.9-16.3% of them; the protocol-only arm 0-1.9%; neither flags any without the border (TT1 follow-up, reviewed).

## What did not move it

| Attempt | Outcome | Review |
|---|---|---|
| Training on three photo sources | fewer false alarms on an unseen source, but twice as many missed morphs at the same rule with unchanged ranking: a shifted decision point | REVIEW_MS1 |
| Same-person full morphs as genuine examples | target not met; same-person morphs flagged 25-32% instead of 83-90%, mostly a shifted decision point; same-person splices unchanged; detection held | REVIEW_SE1_A100 |
| Removing the matched splice negatives | same-person splices flagged 70-74% instead of 36-41%; no detection gain that repeats | REVIEW_AB1 |
| A second backbone (DINOv3) | inconclusive: at the unchanged learning rates the network did not fit its own splices; neither confirms nor refutes independence from the backbone | REVIEW_BB2_PART1 |

## What we established about the field

- **Released detectors and storage history.** With genuine photos aligned and stored like the morphs, MADation ViT-B/16 and MixFaceNet-MAD lose 13-20 points on landmark families on their own crop path; MADation ViT-L/14 barely moves. The column must be labelled "our aligner plus history": pure storage history is not yet separated (REVIEW_CB1_BORDER_HISTORY).
- **The SMDD partner shortcut.** Detectors trained on SMDD rank morphs made with its five recurring partners above morphs with other partners: 0.72-0.91 for three released detectors, 0.723 ± 0.032 for our five-seed retrain of the ViT-L/14 recipe (REVIEW_SM1_A23, REVIEW_SM1_VITL_5SEED).
- **Diffusion benchmarks are solvable without morphs.** Networks trained without a single morph reach 0.0% error on MorDIFF on every seed, on both backbones (AD4, reviewed). The released recipe's diffusion signal does not exceed the similarity of the source pair and shows no identity reading (REVIEW_SM1_A16-A22).
- **An audit table** of 20 shortcuts against 9 arms and detectors, 122 of 180 cells reviewed (`experiments/SA1_shortcut-audit-table/result.md`).

## What cannot be claimed today

"Shortcut-free"; "removes" for any shortcut; any benchmark number for our networks; detection of GAN or diffusion morphs; a second-identity reading; independence from the backbone; that the candidate beats simple statistics; state of the art on MAD22 or FRLL-Morphs.

## Still running or queued

On WCSS, waiting in a saturated queue (read when the fits end, latest 15 Nov 18:00, by the author's ruling of 17:15): a properly trained second-backbone arm, a second test of the same-person arm, 25 further ablation fits, 20 multi-source follow-up fits, IDistill with three seeds, retrains of released methods. On the DGX: IDistill, one seed, ends 14 Nov morning.

## Decisions with the author

1. The storage-test re-run on the training platform (C2P-R): yes or no. It is the only route to a registered freeze.
2. Whether to freeze the candidate by author ruling, disclosed as such, and give the go for the single sealed read of MAD22 and FRLL-Morphs.
3. The deciding measure of the final protocol (reviewer finding F10): proposal, ranking quality in history-matched cells with the own rule and a development threshold printed beside it.
4. Which closed sets are confirmatory.
5. Image operations that are his to allow: raw-file storage history for the released detectors; JPEG re-encoding of development evaluation images; aligning the Chicago and KDEF happy photos; shrinking the larger NIST photos.
6. The twice-as-long training arm, now with a registered trade-off prediction.

## Spend

About 48.5 USD of rentals today against the 50 approved.

## Corrections after the record keeper's check (19:06, ledger entry 1 at 486d089)

- **Released detectors and storage history.** "Lose 13-20 points on landmark families" is wrong as a general statement. It holds for the AMSL and WebMorph families (+12.8 to +19.6). The OpenCV family rises by +3.90 (MADation ViT-B/16) and +5.88 (MixFaceNet-MAD), and MixFaceNet-MAD on MAD22 FaceMorpher by +8.37. MADation ViT-L/14: −0.54 to +1.98 (unchanged). Source: `experiments/CB1_competitor-baselines-corrected-mad22/result.md` lines 227-235.
- **Morph-free networks on MorDIFF (AD4).** The 0.0% figure is confirmed for both backbones, but a saved review file exists only for ViT-B/16. The ViT-L/14 half is therefore "unreviewed" until a review is saved.
- **NIST mugshot block.** Numbers confirmed against the result file; no review file is saved, so it is "unreviewed" until one is.
- **Storage-test re-run (C2P-R).** Its pre-run check is written inside the draft only; no separate review file exists.
- **Times.** This document was committed at 17:38, not written at 17:45; the author's ruling cited as 17:15 was recorded at 17:13.
- **Update 19:08.** The review covering the ViT-L/14 half of the morph-free networks reading existed and is now saved verbatim (`experiments/reviews/REVIEW_AD4_CLUSTER_20261113.md`, 6d11728; verdict "the conclusions hold but need qualifying"). The "unreviewed" label on that half is lifted. The NIST mugshot block stays unreviewed until its file is saved.
- **Update 19:10.** The review of the NIST mugshot block existed and is now saved verbatim (`experiments/reviews/REVIEW_TT1_MEDS_20261113.md`, 2aef2ce; verdict "needs qualification", corrections applied in c4c2233). The "unreviewed" label on that block is lifted.
- **Update 20:18, qualification of every landmark_combined number above.** The standing adversary's floors (bffacb5), reviewed (REVIEW_ADV_STAGE1A_20261113.md): FFHQ landmark_combined is separable at 0.96-0.98 by statistics fitted on it; about 0.79 comes from the image surround alone, a resampling-history difference between how the morphs and the genuine photos were made (documented by the dataset; our face splices show 0.50 on the same cue). The candidate's replicated gain of +0.12 to +0.21 over the plain and protocol arms is therefore a gain "on a development set whose surround carries a kernel-history cue; whether it holds at matched history is untested". The floor is fitted on the set itself while the networks are scored without having seen it, so a network below the floor shows neither that it ignores those cues nor that the contrast is invalid; statistics fitted on other rows reach 0.45-0.81 there (post hoc).
