# Hypothesis strategist: evening synthesis, 13 Nov 2026 (results-reviewer, Opus; read-only)

**Strategist report, evening of 13 Nov 2026 (read-only; I opened no valx.csv, FST or A12SP file, and nothing was scored)**

## Summary in plain English

The evidence supports a strong audit paper with a modest method inside it. It does not support a method paper that claims to be "shortcut-free and state of the art". Two things are solid:
- Released detectors' benchmark errors depend on how photos were stored, on SMDD's recurring partners and on the rendering path. Networks that never saw a morph solve MorDIFF.
- Our training protocol cuts the storage reaction at the decision rule by about an order of magnitude against a working plain control. It also adds about 0.12 to 0.21 AUC on in-face blends, on ten seeds.

No detector we tested, ours or anyone's, reads a second identity.

Tonight the author should:
- Freeze Sb at seeds 403-407 by his own ruling, with disclosure.
- Approve C2P-R only as a cheap way to complete the record. I expect it to come back "inconclusive", so it will not freeze anything by rule.
- Make within-cell EER on history-matched cells the deciding measure.
- Strike VAL-X, FST and A12SP from the confirmatory list. Add an unseen-source landmark ladder (MUCT) and a border-equalised form to the sealed read before it runs.

Keep at least 6 USD of the rental credit for the sealed read. It must run on an A100, and Athena is blocked.

---

## 1. The strongest paper the evidence supports

**Title-level claim:** *Single-image morphing attack detectors read storage, partner and rendering traces rather than a second identity: a paired-control audit, and a training protocol that reduces the storage reaction.*

**Headline results, with supported wording:**

1. **Audit of released detectors** (REVIEW_RS1, REVIEW_CB1_BORDER_HISTORY, REVIEW_EV1, REVIEW_SM1_A23, REVIEW_AD1_AG5_C, REVIEW_AD4_VITB):
   - "With genuine photos aligned and stored like the morphs, MADation ViT-B/16 loses 12.8 to 19.0 EER points on AMSL, WebMorph and MAD22 FaceMorpher, and MixFaceNet-MAD 18.5 to 19.6. On raw files the history effect is +12.2 [8.3, 16.3] (ViT-B/16) and +21.1 (MixFaceNet-MAD) on MorDIFF. MADation ViT-L/14 moves −1.0 to +2.0, with saturated scores."
   - "SMDD-trained releases rank morphs made with SMDD's five training partners above morphs with other partners (within-key AUC 0.72 to 0.91)."
   - "Three adapted releases do not rank diffusion morphs above one-photo reconstructions (0.40 to 0.49)."
   - "Networks trained without any morph reach 0.0% EER on MorDIFF."
   - The history column must be labelled "aligned-frame history (our aligner plus history)".
2. **The protocol, on development data only** (REVIEW_AB1, REVIEW_PN1_FS1, REVIEW_SE1_A100, REVIEW_TT1_FS):
   - "At the decision rule, the candidate's flag-rate rise on stored genuine photos of unseen persons was at most +4.5 points at the trained size and +2.1 at an untrained size, against +27 to +39 and +6 to +15 for plain training (5 seeds, H100). The registered verdict is 'inconclusive' in every block, because the candidate's genuine scores move toward genuine by more than a third of the plain shift."
   - "Face-spliced positives with matched negatives add 0.12 to 0.21 AUC on landmark morphs from an unseen tool over plain and protocol-only training (10 seeds, two platforms). This is not shown to exceed the best single hand-made statistic."
   - "The decision rule held on 21,000 genuine photos from eight unseen low-resolution sources (protocol arm 7 of 7 seeds, candidate 4 of 5) and on 865 NIST mugshots (5 of 5)."
3. **A field-level negative:** "No detector tested, released or ours, reads a second identity. Same-person morphs are flagged at 81 to 96% (releases) and 83 to 99.5% (our arms). Every contrast that isolates a second person stays at 0.60 to 0.75, within reach of simple statistics."

**Claims to drop:**
- "shortcut-free", or "removes" for any shortcut;
- "passes the registered storage test";
- second-identity detection;
- detection of GAN or diffusion morphs (our network flags 78-90% of one-photo GAN renders);
- independence from the backbone;
- beating simple statistics;
- threshold transfer to sharp sources or after calibration;
- that the three-source arm is better;
- any confirmatory reading of MAD22 or FRLL-Morphs.

**Is "shortcut-free and state of the art on MAD22 and FRLL-Morphs" reachable? No.**
- *Shortcut-free* is contradicted by our own reviewed cells: the candidate reacts to a blanked-in border (2.9-16.3% of camera photos flagged), flags most same-person blends, and responds to rendering.
- *State of the art* can at best be descriptive:
  - FINAL §2 labels both sets "seen during development".
  - FINAL §4 bars SOTA sentences on cells where a morph-free network reaches ≤5% EER. On the AD4 values that covers FRLL AMSL, FaceMorpher, Webmorph and MAD22 FaceMorpher, and history matching does not remove the cue on those cells.
  - What remains: FRLL OpenCV and StyleGAN, and MAD22 OpenCV, Webmorph and MIPGAN. The GAN cells will read as render response.
- **Nearest defensible claim:** "On history-matched cells of MAD22 and FRLL-Morphs (seen during development), the frozen network's EER is [comparable to / lower than] the released detectors', with a storage reaction at its decision rule about ten times smaller than plain training." This is FINAL outcome row 3, if the read gives it.
- My forecast, which is not a number: it trails MADation ViT-B/16 on the standard form for landmark cells.

## 2. The freeze: decisions for tonight

**(a) C2P-R: approve, but only as record completion, and only if at least 6 USD stays reserved for the read.**
- It would give the plain-recipe control for the very networks to be frozen. The paper needs that, because SE1 F8 notes that the freeze basis for storage rests on 403-407.
- I predict "inconclusive" with about 70% probability, "uninformative" about 20%, "pass" at most 10%. The reasons:
  - Sb's two-sided |Δm| leg at 112.7 px needs A's Δm ≥ 0.435 and 0.414 SD on seeds 403 and 405 (REVIEW_PN1_C2P F3).
  - A reached 0.19 to 0.40 on all five AB1 seeds (`AB1/result.md:89`), and 0.29 and 0.19 on the two SE1 A100 seeds where the |Δm| leg failed.
  - The same rule failed Sb on 2 of 5 (AB1) and 2 of 4 (SE1) seeds through over-correction toward genuine.
  - A's Δf at 112.7 px was as low as +0.055, just above the 0.05 control bar.
- pn1fs no longer exists. Use the fallback A100 PCIe clause with `rescore_tf32.py`, and disclose it.
- Commit the freeze ruling before reading C2P-R, so the ruling cannot depend on the outcome.

**(b) Freeze Sb, seeds 403-407, last checkpoints, by author ruling: recommend yes.**
- Without a freeze no number of ours exists, and the author's own rule forbids benchmark reads before one.
- Do not switch to SE, Sp, SbS or SbM3; the reviews forbid it.
- Do not add the H100 seeds 408-412: FINAL §7 says "if any gate fails, stop", and H100-trained networks scored on an A100 are exactly how C2P failed.
- Disclosure sentence: "No method met the registered freeze rule. Its storage test on seeds 403–407 was first scored on a different GPU model and precision setting than training, which removed every plain-training control; [a re-scoring on the training platform, registered after the candidate's first-run statistics had been seen, gave '…' / was not run]. On two further independent seed blocks the test was 'inconclusive' for the candidate (3 of 5 and 2 of 4 seeds at the untrained size), each time because its genuine scores moved toward genuine, while its flag-rate rise stayed at most +4.5 points against +27 to +39 for plain training. The authors froze the candidate by their own decision on 13 Nov 2026, before any benchmark score of these networks existed. Its recipe had been chosen after benchmark scores of earlier seeds (401/402) were seen."

**(c) Deciding measure (F10): EER per confirmatory cell on the history-matched form.**
- Print AUC beside it.
- Print own-rule APCER and BPCER and τ_dev(ii) as secondary.
- Withdraw τ_dev(i) as the decider.
- Disclosure sentence: "Before any benchmark score, the deciding measure was changed from error rates at a development threshold to EER on history-matched cells, because that threshold flagged 96–98% of genuine photos from an unseen source for every network."

**(d) Confirmatory sets:**
- Keep FEI gtest, with the pre-stated label "not morph-specific: the network flags one-photo GAN renders".
- Keep the morph side of MorDIFF and DiM, labelled "genuine pool seen". MorDIFF is shortcut-saturated, and FINAL M5 predicts ≥30% EER on history-matched diffusion cells. So the confirmatory endpoint will almost certainly not give a SOTA sentence; the author should hear this tonight.
- Strike VAL-X: the hard rule says `valx.csv` is never opened, yet FINAL §2 lists it as a candidate.
- Strike FST and A12SP: they stay sealed by the 31 Oct ruling, and their contents are unknown.
- Add the MUCT ladder (experiment 3 below) if it is registered before the read.
- Disclosure sentence: "MAD22 and FRLL-Morphs were scored with networks of the same recipe during development and share 204 FRLL genuine photos; they are reported as seen during development."
- Resolve the MS1-clause ambiguity (REVIEW_PN1_C2P F5).

## 3. Experiments for 14-15 Nov, ranked by value per GPU-hour

| # | Experiment | Hypothesis; pass / fail | Cost, platform | What each outcome changes | Author? |
|---|---|---|---|---|---|
| 1 | **Blend-difference attribution** (zero-GPU; register first) | The candidate reads blend-difference energy D = mean \|S − R2w4\| inside the face hull, computed by subtracting existing images, not identity. Pass: within D-quintiles, Sb's S4-vs-S3 AUC ≤ 0.62 on ≥4 of 5 seeds, and persistently flagged S3 hosts (SE1 F5) have ρ(D) ≥ 0.4. Fail, meaning an identity residual: ≥ 0.70 on ≥4 of 5. | 0 GPU, about 2 CPU-h, existing FS1/AB1/SE1 scores | Pass gives a mechanistic sentence explaining SE1, the AB1 r = 0.73 trade-off and SM1. Fail is the only lead toward real second-identity training: then run a difference-matched splice arm (look-alike S4 against dissimilar-session S3, about 6 H100-h, post-freeze). | no |
| 2 | **Additions to the sealed read:** (a) a border-equalised form (the same constant-colour ring blanked into every image of both classes, for every detector); (b) the best development statistic (noise_std_face, direction fixed) as a printed reference detector | Sb's border reaction inflates landmark cells where only morphs carry a border. Prediction: Sb's EER rises ≤2 points when borders are equalised, while MixFaceNet-MAD shifts the most. | about 0.3 A100-h inside the one read | Answers hostile sentence 2 before it is written. If Sb loses more than 3 points, the landmark rows carry a border caveat. | FINAL amendment before the read; blanking is an allowed operation |
| 3 | **MUCT unseen-source ladder** (R0, R2w, R3, R4, S4; unchanged OpenCV and FaceMorpher morphers, approved aligner, lossless PNG) as a confirmatory set | The in-face blend gain transfers to new persons and a new camera. Pass: Sb − A ≥ +0.05 AUC on ≥4 of 5 seeds; Sb's R3 flags printed. | 4-8 CPU-h to build; about 0.2 GPU-h in the read | This is the only confirmatory test of what the method actually does. It also gives a cue-matched comparison with the releases (which may win there; report it). | yes (confirmatory set), before the read |
| 4 | **Author-built storage packs:** (a) raw-file storage history of the FRLL genuine photos for the releases; (b) JPEG 90/70/50 of development evaluation photos, with the registered `degrade` used unchanged | (a) The aligned-frame effect overstates pure storage, as on DiM (+34.4 raw against +52.9 aligned). (b) JPEG is used if Δf(Sb) ≥ +0.05 at q50 on ≥4 of 5 seeds. | about 1 A100-h | (a) Turns the audit headline from "aligned-frame" into "storage". (b) Fills the empty JPEG row (row 3) and tests the format asymmetry in MAD22 (C4). | yes: resampling and JPEG are author operations |
| 5 | **Border-crossed Sb** (constant-colour borders blanked into both classes in training; 5 fits) | The border reaction is learned. Pass: ≤2% of border-blanked camera photos flagged on ≥4 of 5 seeds, with landmark_combined within −0.02. | about 6 H100-h on WCSS (do not rent) | Turns a limitation into a remedy, labelled post-freeze. It cannot become the method. | registration only |

Not recommended:
- **The twice-as-long arm.** SE1 F5 shows host-level residual flags, with training rows flagged about as often as development rows: a label conflict, not under-training. I predict training S3 flags fall, development S3 falls by ≤0.05, landmark_combined moves by at most ±0.01, and the arm is falsified or inconclusive. It would cost about 12 H100-h with no paper consequence.
- **Any second-identity training before experiment 1.** The record (AR1, AS0, FZ2, PD1, SM1, AG1, ID0) gives no basis for it.

## 4. Queued WCSS batches to cancel if the queue stays saturated

1. **AB1 batch B2** (25 fits). Post hoc row-drop attributions with predictions set after the data, giving mechanism-table detail only.
2. **MS1 part 4** (20 fits). MS1 already showed a shifted operating point, the three-source arm is not frozen, and dilution against diversity changes no claim.
3. **SE1 H100 block** (5 fits). It replicates an ablation row whose A100 read is clear. Keep it only if slots are free.

Keep:
- BB2 E2 (about 1 H100-h) and E3, the properly trained second-backbone arm, which answers "CLIP-specific?". It is development data only and cannot enter the read.
- The AD4 H100 re-score (cheap; it fixes the "incomplete 2 of 5" rows).

Lower the priority of:
- AD5 retrains. The author ruled they arrive when they arrive, and the released-weight rows suffice.
- The WCSS IDistill run. It is a re-implementation with no released weights, likely not to reproduce; the one DGX seed is enough as a labelled row.

## 5. Three sentences a hostile CVPR reviewer would write, and the best answers

1. **"The learned detector does not beat a single hand-crafted statistic on the authors' own development set (0.873–0.906 against 0.886)."**
   Answer: concede it on development data. The 0.886 floor is the maximum of 27-plus statistics on the same images; cross-fitted, the best statistic falls to 0.64-0.88 (REVIEW_PR1_PART3 F5). The statistic is printed as a reference detector in the sealed read (experiment 2b). The contribution is a protocol and an audit, not a margin.
2. **"None of the registered shortcut tests passed; the network reacts to borders and flags same-person blends, so 'shortcut-aware' is overreach."**
   Answer: report the verdicts as registered, with the cause: the two-sided bar penalises over-correction toward genuine. Give the effect sizes across three independent blocks (≤ +4.5 against +27 to +39 points). Present the border and same-person behaviour as measured limitations. Point out that the same paired controls, applied to the releases, expose larger failures. Add the border-equalised form.
3. **"MAD22 and FRLL-Morphs were used during development and share 204 genuine photos; the comparison is not independent."**
   Answer: the exposure is disclosed in the Experiments section. The frozen networks were never scored before one pinned, sealed read. Confirmatory claims rest on FEI, the morph side of MorDIFF and DiM, and the MUCT ladder. MAD22 and FRLL-Morphs are reported in standard, history-matched and border-equalised forms, labelled "seen during development".

## Risks to hedge now

- **The read's platform gate.** The read needs an A100 PCIe and pn1fs is gone. Run the FINAL §7 gate on development rows on the intended lease tonight. TT1-M was byte-identical on a second A100 PCIe host, which is encouraging.
- **Credit.** Reserve rental credit for the read.
- **Cut-off text.** Amend FINAL §4's 14 Nov 18:00 retrain cut-off to match the author's 08:30 ruling.
- **Two paper versions.** Prepare the "comparable or lost" and "audit only" versions of the abstract now.

Files:
- /home/narolski/smad-next/experiments/FINAL_sealed-benchmark-read/prereg.md (§1, §2, §4, §7, §10 item 9)
- /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/prereg.md (lines 836-878)
- /home/narolski/smad-next/experiments/AB1_protocol-ablation-and-replication/result.md (lines 28, 83-99)
- /home/narolski/smad-next/experiments/reviews/REVIEW_PN1_C2P_20261113.md (F3, Q2)
- /home/narolski/smad-next/experiments/reviews/REVIEW_SE1_A100_20261113.md (F2, F5, F8)
- /home/narolski/smad-next/experiments/SA1_shortcut-audit-table/result.md
- /home/narolski/smad-next/18_EVENING_CONCLUSIONS_20261113.md
- /home/narolski/smad-next/OWNER_BRIEF.md (line 41, allowed image operations)
