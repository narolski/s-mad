# Independent check of `deepfake.md` (cross-field analysis: deepfake detection)

11 Nov 2026, evening. Checker role: independent. Research and reading only. No experiment, no GPU, no cluster,
no git. Nothing sealed was opened. This file is the only file written in the repository.

How to read this file.

- S-MAD: single-image morphing attack detection. AUC: area under the receiver operating curve. EER: equal error
  rate. FR: face recognition. SBI: self-blended images. LoRA: low-rank adaptation. SD: standard deviation.
- Ladder rungs as in the brief: R0 photo; R1 photo with storage history; R2w warp only; R3m photo blended with
  its mirror; R3 two photos of one person; R4 two persons.
- "Opened" means I fetched the page during this task. "Content" means I put questions to the full text (arXiv
  HTML or ar5iv). "Metadata" means title, authors and the arXiv comment line only.
- Pages were read through an automated page reader. Every number below must be re-checked against the PDF
  before it enters the manuscript.
- **Limit of this check.** Seven web searches succeeded. Then the session's shared search budget ran out. After
  that I could only open pages whose address I already knew (arXiv numbers from the analysis, from our own
  notes, or from the seven searches). So part (2) of the job, the hunt for missed work, is thinner than it
  should be. What I recall but could not open is listed separately in section 6.

---

## 0. Result in ten lines

1. The reference list is sound. Of 70 references I opened 57 (24 at content level, 33 at metadata level). All 57
   exist. One page refused access (Huang et al., CVPR 2023). I found no invented work and no wrong first author.
2. Five statements of the analysis are wrong and matter (section 2): two table rows about morph detection
   ("same-person morph labelled genuine: once", "deepfake detectors scored on morphs: not found"), two readings
   of GenD and DF40, and two statements about our own record (the two-contributor head is "in the plan"; the
   audit use of subspace surgery is "new").
3. The most important missed work is inside morph detection: MorDeephy (Medvedev et al., ICPRAM 2023). It
   trains two identity embeddings, scores a single image by their dot product, and uses about 500,000
   same-person morphs as genuine images. Proposal 5.4 is close to it. Our own round-3 files already cite it.
4. The most important missed deepfake work is the Rebalanced Deepfake Detection Protocol (Wang et al., arXiv
   2405.00483). It is the deepfake field's version of our ladder: genuine videos passed through the forgery
   tool and labelled genuine, and the same processing applied to both classes.
5. One confound from our record hits three of the four proposals. Same-person against two-person (R3 against
   R4) is predicted by warp size alone at AUC 0.81 pooled and 0.92 on FERET (planning record, section 14.1).
   The alpha-field head, which fails its warp control, already reaches 0.853. So "R3 against R4 at least 0.85"
   is not a pass mark. It must be read inside geometry-matched groups.
6. Verdicts: 5.1 revise, 5.2 revise, 5.3 revise (keep the audit, drop the training rule as a method), 5.4 drop.
7. Best value for the three days: the label ablation of section 5.5 of the analysis (one-person blends labelled
   genuine, left out, labelled attack), run with the geometry and periphery controls given below.

---

## 1. Reference verification

### 1.1 What was opened

| Reference (number in `deepfake.md`) | Level | Exists, authors and year right | Says what the analysis claims |
|---|---|---|---|
| 1 Face X-ray, Li et al., CVPR 2020 (Oral) | content | yes | yes: Eq. 2 is `4 M (1 - M)`; 100 nearest landmark neighbours (Sec. 3.2); Table 2 values 93.47 / 71.15 / 74.76; Sec. 6 limits. Note: the paper names low resolution beside compression for 87.35 to 61.6 |
| 2 SBI, Shiohara and Yamasaki, CVPR 2022 (Oral) | content | yes | yes, with two small slips (section 2, item 12) |
| 3 Pairwise self-consistency, Zhao et al., ICCV 2021 (Oral) | content | yes | yes: target `1 - |m_p - m_q|` (Eq. 2); different identity within a landmark threshold; entire-face synthesis "should be self-consistent" |
| 4 ProDet, Cheng et al., arXiv 2408.17052 | content | yes | yes: four anchors, three binary attribute heads, attention from the attribute outputs, bridging of adjacent anchors only, argument against one-hot labels, Table 2 0.8070 against 0.7811, Table 1 0.8225 against 0.7814. Venue "NeurIPS 2024" is not on the arXiv page |
| 5 Implicit Identity Leakage, Dong et al., CVPR 2023 | content | yes | yes: Figure 2 probe; Table 1 ranges 81.5 to 99.6 and 44.4 to 49.5; quote on local areas |
| 6 Identity Consistency Transformer, Dong et al., CVPR 2022 | content | yes | yes: 112 px, MS-Celeb-1M, two tokens, consistency loss, 87.01 average, 51.48 on Celeb-DF v2 without the consistency loss (Table 3), reenactment limit |
| 7 Effort, Yan et al., arXiv 2411.15633 | content | yes | yes: Table 8 ranks 160 / 57 / 137 / 159; Table 1 average 0.917 over seven sets. ICML 2025 is not on the page (the analysis says so) |
| 8 ED4, Cheng et al., arXiv 2408.06779 | content | yes | yes: label rule, Table VII 0.8195 / 0.6832 / 0.7512, Table IV 0.6061 / 0.5419 / 0.5351 against 0.8765 / 0.8394 / 0.7427, the "mistakenly" quote. One slip (section 2, item 10) |
| 9 GenD, Yermakov et al., arXiv 2508.06248 | content | yes | mostly. Two errors (section 2, items 1 and 2). The arXiv page carries a WACV 2026 DOI |
| 10 OST, Chen et al., NeurIPS 2022 | abstract | yes | abstract agrees; the quoted table numbers were not re-checked |
| 11 DiffusionFake, Sun et al., NeurIPS 2024 | content | yes | yes: both targets equal the image for a real face; 75.80 to 81.88; stated limits |
| 12 DF40, Yan et al., arXiv 2406.13495 | content | yes | mostly. One error (section 2, item 3). The venue is not on the page |
| 13 S3, Wang et al., arXiv 2606.01843 | content | yes | yes: probe, singular vectors, Figure 2b, gradient projection, neuron scaling, 0.3774 to 0.9066, 0.7636 combined, one dataset, single runs. Three more cautions (section 2, item 11) |
| 17 Latent-space augmentation, Yan et al. | abstract | yes | abstract agrees. Venue "CVPR 2024" is not on the page |
| 25 muFlow, Pontorno et al., ECCV 2026 | abstract | yes | yes |
| 37 QAD, Le and Woo, ICCV 2023 | abstract | yes | yes: one model, several quality levels, dependence maximised between representations |
| 41 Alpha Blending Hypothesis, Yermakov et al. | abstract | yes | yes: withdrawn 4 Nov 2026; the comment line gives the train and test overlap as the reason |
| 50 SelfMAD, Ivanovska et al., FG 2025 | content | yes | yes: SBI "conceptually closest", blend factors, labels, Table I values. It also contradicts one row of the analysis (section 2, item 5) |
| 51 Kashiani et al., IJCB 2023 | content | yes | yes: Section 3.2 quote; self-morphs sit in the morph class (Section 3.3). IJCB 2023 is on the arXiv page |
| 52 Pimenta et al., arXiv 2309.00549 | content | yes | the quote is right. The framing is not (section 2, item 4). "BIOSIG 2023" is not on the arXiv page |
| 53 PW-MAD, Damer et al., ISVC 2021 | content | yes | per-pixel labels: yes. That the map is constant is not stated in the text I could read. Plausible, not confirmed |
| 54 Seibold et al., J. Inf. Secur. Appl. 53, 2020 | content | yes | yes: partial morphs take regions from the morph and the rest from the aligned photo; four-class region scheme. The arXiv title differs from the journal title |
| 61 OrthoMAD, Neto et al. | content | yes | partly (section 2, item 6). Venue is BIOSIG 2022, missing in the list |
| 62 Caldeira et al., EUSIPCO 2023 | content | yes | partly (section 2, item 7) |

Metadata only (title, first author and arXiv comment line agree with the list): 14 UCF, 15 Liang et al., 16 Fu
et al., 18 Nirkin et al., 21 FACTOR, 23 SeeABLE, 26 FSFM, 28 Luo et al., 29 Liu et al., 30 FreqBlender, 31
LAA-Net, 32 SLADD, 33 CDFA, 34 Forensics Adapter, 35 Yermakov 2503.19683, 36 Ojha et al., 38 T2A, 39 Trinh and
Liu, 40 Smeu et al., 42 DeepfakeBench, 43 Le et al. (EuroS&P 2025), 44 Deepfake-Eval-2024, 45 FaceForensics++,
57 MAD-DDPM, 58 SRL-MAD, 59 FD-MAD, 60 Colbois and Marcel, 63 MADation, 66 Zhang et al., 67 R-FLoRA, 68 Banerjee
et al., 69 Shukla and Ross, 70 Ramachandra et al.

### 1.2 Wrong or not verifiable

- **19 Huang et al., CVPR 2023.** The publisher page returned "403 Forbidden". Not verified by me.
- **Not opened** (no weight on any proposal): 20 ID-Reveal, 22 RECCE, 24 Real Appearance Modeling, 27 F3-Net,
  46 to 49 (Meta blog and press), 55 and 56 Debiasi et al., 64 Di Domenico et al., 65 Srivastav et al.
- **Venues that the pages I opened do not state.** ProDet (NeurIPS 2024), DF40 (NeurIPS 2024 Datasets and
  Benchmarks), latent-space augmentation (CVPR 2024), UCF (ICCV 2023), Liang et al. (ECCV 2022), Pimenta et al.
  (BIOSIG 2023), Fu et al. (AAAI 2025), Effort (ICML 2025). They agree with what I recall. They are not
  confirmed here. Check each against the proceedings before citing.
- **61 OrthoMAD.** Listed as "arXiv 2022". The arXiv comment line says "Accepted at BIOSIG 2022".
- **34 Forensics Adapter.** The arXiv record now shows the journal version: title "Forensics Adapter:
  Unleashing CLIP for Generalizable Face Forgery Detection", comment "TPAMI 2026". The CVPR 2025 title in the
  list is the earlier version. Cite one of them, not a mix.
- **54 Seibold et al.** The arXiv title is "Accurate and Robust Neural Networks for Security Related
  Applications Exampled by Face Morphing Attacks" (2018). The journal title is the one in the list (DOI
  10.1016/j.jisa.2020.102526). Both are the same work.

---

## 2. Claims corrected

1. **GenD, Table 4.** The analysis says "all methods retrained on the same data". The paper says the opposite
   for the two competitors: "we utilized their officially released weights and integrated their data
   preprocessing pipelines". Effort 88.5 and Forensics Adapter 88.4 are released weights, scored by the GenD
   authors. GenD itself is trained on FaceForensics++ only.
2. **GenD, supplement.** The range of the true-positive rate at 1% false positives for GenD (CLIP) is 10.9%
   (DSv2) to 92.9% (UADFV), mean 49.1% (Table S7). The analysis gives 92.3%, which is another dataset's value.
3. **DF40.** "DF40 uses the same real data for 40 forgery methods" is wrong. Table 2 of the paper lists the real
   source per method: FaceForensics++ and Celeb-DF for most, but UADFV, VFHQ, FFHQ and CelebA for others. The
   StyleCLIP collapse (0.006) happens exactly because the relation between real and fake resolution flips in a
   test domain with another real source. The finding and the quote "higher resolution, higher probability to be
   real" are right (Section 4.3; the explanation is given for the reenactment-trained models).
4. **"Same-person morph labelled genuine: yes, once" (section 4 of the analysis).** Not once. MorDeephy
   (Medvedev, Shadmand, Gonçalves, ICPRAM 2023, arXiv 2208.03110, posted August 2022) trains with about 500,000
   same-person morphs and states "we consider selfmorphs as bona fide samples". Pimenta et al. is the same
   group's follow-up and uses the MorDeephy scheme ("we follow the fused classification approach, where two
   parallel networks were trained simultaneously"; the score is "the dot product of the backbone outputs"). So
   Pimenta et al. is not "a binary choice" of label only. It is identity-based single-image detection with
   one-person blends in the genuine class. Our planning record (section 14.3) already lists two more papers of
   this group (arXiv 2309.00665 and 2402.14665).
5. **"Deepfake detectors scored on morphs: not found" (section 4 of the analysis).** SelfMAD, reference 50 of
   the analysis, does it. Its Table I scores SBI on morph benchmarks: EER 11.76 / 13.73 / 12.25 / 44.61 / 39.22
   on FRLL-Morphs (AMSL, FaceMorpher, OpenCV, StyleGAN2, WebMorph), average 27.55 over all its test sets
   (page-reader values; re-check). Face X-ray is cited there but not scored.
6. **OrthoMAD "trained on SMDD".** It is trained separately on five sets (MorGAN-LMA, MorGAN-GAN, LMA-DRD digital,
   LMA-DRD print-scan, SMDD) and tested on FRLL-Morphs. It has no identity supervision at all: binary
   cross-entropy plus a penalty on the inner product of two latent vectors. "Two identity vectors" is the
   authors' reading of the vectors, not something the training enforces.
7. **Caldeira et al. (EUSIPCO 2023).** Trained on SMDD: right. The targets are latents of an autoencoder trained
   on genuine images, not FR embeddings. The decision score is `1 - id1 * id2`, a function of the two slots.
   That is nearer to "the score is the distance between two slots" than the analysis admits.
8. **"The two-contributor embedding head already in our plan (T5)".** Our record says the opposite. The head
   failed twice (summer demorph head S8; the reference-free demorpher recovered 0.00 to 0.27% under the strict
   rule against 97 to 99% for the oracle) and `IDEAS_v1.md`, section E, item 2 drops it: "for landmark morphs
   it costs a day and its falsifier is likely to fire" (planning record, section 14.1).
9. **"New are the audit use on released detectors and the gradient rule" (proposal 5.3).** Both were proposed
   in round 1 and not taken into a theme (planning record, section 14.1; `ROUND1_raw.json`): "Null-space
   surgery: remove history directions estimated from paired differences, in closed form, from our head and
   from the released MADation heads", "History-null constrained adaptation" (keep the LoRA update in the
   complement), and "Counterfactual-pair erasure". New in 5.3 are only the "subspace only" read-out taken from
   S3's Figure 2b and S3 as an outside reference.
10. **ED4, spatial bias.** The evidence is not only attention maps. Figure 8 plots score changes under crop,
    resize and shift, and Table VI compares augmentations. Both are indirect, but they are numbers.
11. **S3, further cautions.** The abstract says the subspace is suppressed "in feature representations"; the
    method section projects the gradient with respect to the features. The abstract says "multiple benchmarks";
    all experiments use DF40. The best setting is given as rank 3 with strength 0.7 in one section and 0.5 in
    an appendix. Figure 2b has no numbers in the text. The analysis's own warning (single dataset, single runs)
    stands and should be stronger.
12. **SBI details.** The colour and frequency changes go to the source or the target copy at random; resize and
    shift go to the source only. The 69.11 result is on a 20,000-image set of FFHQ photos and StyleGAN renders,
    not on "20,000 StyleGAN faces".
13. **ProDet.** Table 2's average is over three test sets, Table 1's over four. Do not compare them. The module
    that turns three attribute outputs into an attention map is not specified in the paper, so "attention
    steered by the bits" cannot be rebuilt from the text alone. This matters for the second step of 5.2.
14. **Pass marks in 5.1 and 5.2.** "R3 against R4 at least 0.85" is already met by the alpha-field head that
    fails its warp control (0.853 [0.820, 0.883] on FaceMorpher, `experiments/AF0/result.md`), and geometry
    alone gives 0.81 to 0.92 (planning record, section 14.1). The mark does not test the idea.
15. **Folds.** "5 folds by person" must hold out both persons of every morph. The record found that folds by
    host alone leak the partner (planning record, section 14.1, `gate_c.py`).

Minor: the printed ICT average with a reference set is 96.34; the five values average 96.36. Face X-ray's
Table 5 and Table 2 disagree inside the paper on which model 93.47 belongs to.

---

## 3. Important work the analysis missed

Found and opened during this task.

1. **In Anticipation of Perfect Deepfake: Identity-anchored Artifact-agnostic Detection under Rebalanced
   Deepfake Detection Protocol.** W.-H. Wang et al., arXiv 2024. https://arxiv.org/abs/2405.00483
   The protocol has two parts. "Whitehat": genuine videos are re-created with the forgery tool from the same
   person ("self-deepfakes") and labelled genuine. "Surrogate": the same processing (resize, JPEG, video
   compression, blur) is applied to both classes. Reported in Table 1 (reenactment, VoxCeleb): Xception falls
   from about 0.92 to about 0.61 under whitehat and to 0.56 to 0.68 under the four surrogate operations; the
   average loss of non-identity baselines is 18 to 35%. This is our rung R2/R3 and our storage-history control,
   published in the deepfake field. It is the right outside precedent for the audit. Its own detector needs a
   reference video, so the method does not transfer.
2. **MorDeephy: Face Morphing Detection Via Fused Classification.** I. Medvedev, F. Shadmand, N. Gonçalves.
   ICPRAM 2023. https://arxiv.org/abs/2208.03110
   Two networks. For a morph, one is trained to output the first contributor's identity class and the other
   the second contributor's. The detection score is the dot product of the two embeddings. About 1,000,000
   landmark morphs and about 500,000 same-person morphs labelled genuine, from VGGFace2. No retrieval test.
   Closest prior work to proposal 5.4 and to the label choice in 5.2. Follow-ups: arXiv 2309.00665, arXiv
   2402.14665 (our record quotes it: self-morphs "didn't demonstrate significant impact to the performance"),
   MorphGuard, arXiv 2505.10497.
3. **SelfMAD's Table I as a cross-field measurement** (see section 2, item 5). SBI moved unchanged to morphs
   gives 12 to 14% EER on landmark cells and about 40% on StyleGAN2 and WebMorph. This is the measured answer
   to "what happens if the deepfake recipe is moved unchanged".
4. **Face Morphing Attack Detection and Localization Based on Feature-Wise Supervision.** L. Qin, F. Peng, M.
   Long. IEEE Trans. Inf. Forensics Secur. 2022, DOI 10.1109/TIFS.2022.3212276. Found by search, abstract level
   only. Its fine-grained loss "can locate the morphed regions". The analysis states that no morph-detection
   work with region knowledge beyond Seibold et al. was found. This paper is the open question for the novelty
   of 5.1. Round 2 could not read it either. Someone must read the PDF before 5.1 is called new.
5. **Closed-form and provable versions of what S3 does by heuristics** (for 5.3). LEACE: Perfect linear concept
   erasure in closed form, N. Belrose et al., NeurIPS 2023, https://arxiv.org/abs/2306.03819. Null It Out
   (iterative null-space projection), S. Ravfogel et al., ACL 2020, https://arxiv.org/abs/2004.07667.
   Conditional Variance Penalties and Domain Shift Robustness, C. Heinze-Deml and N. Meinshausen, arXiv 2017,
   https://arxiv.org/abs/1710.11469: images of the same object under a style change are grouped and the
   variance of the prediction inside a group is penalised. That is our photo with and without history. Last
   Layer Re-Training is Sufficient for Robustness to Spurious Correlations, P. Kirichenko et al., ICLR 2023,
   https://arxiv.org/abs/2204.02937. The analysis leans on one single-run preprint for a tool that has
   peer-reviewed forms. Our round-1 notes already name LEACE and last-layer retraining.
6. **Consistency under augmentation in forgery detection.** CORE: Consistent Representation Learning for Face
   Forgery Detection, Y. Ni et al., CVPR Workshops 2022, https://arxiv.org/abs/2206.02749. FreqDebias: Towards
   Generalizable Deepfake Detection via Consistency-Driven Frequency Debiasing, H. Kashiani et al., CVPR 2025,
   https://arxiv.org/abs/2509.22412 ("spectral bias": detectors rely on specific frequency bands; a frequency
   mixup plus two consistency terms). The first author is the author of the morph-detection consistency paper.
   Our record's own consistency loss (A49) gave no gain, so this line is a caution for the second arm of 5.3.
7. **The data-alignment line of generated-image detection** (abstracts opened; probably covered by the sibling
   analyses, but absent from the remedies list in section 3.6 of this one). A Bias-Free Training Paradigm for
   More General AI-generated Image Detection (B-Free), F. Guillaro et al., https://arxiv.org/abs/2412.17671.
   Aligned Datasets Improve Detection of Latent Diffusion-Generated Images, A. S. Rajan et al.,
   https://arxiv.org/abs/2410.11835. Fake or JPEG?, P. Grommelt et al., https://arxiv.org/abs/2403.17608.
   Stay-Positive, A. S. Rajan and Y. J. Lee, https://arxiv.org/abs/2502.07778. Their common result: build the
   fake from the real so that content, format and resolution agree. Note the label: in that field a
   reconstruction of a real image is "fake". Under our rule it is genuine. ED4 and the rebalanced protocol are
   the only two works I found that label processed real material as real.
8. **A 2026 robustness challenge.** Robust Deepfake Detection: Mitigating Spatial Attention Drift via Calibrated
   Complementary Ensembles, M.-K. Le-Phan et al., arXiv 2026, https://arxiv.org/abs/2604.25889 (4th of 94 teams
   in the NTIRE 2026 Robust Deepfake Detection Challenge). The field now runs a challenge on blur and heavy
   compression. The entry is an ensemble, so nothing transfers to us; it is evidence that the neighbouring
   field treats degradation robustness as a headline test.

---

## 4. The four proposals, one by one

Shared facts from our record that the analysis did not use.

- **Warp size.** R3 against R4 is confounded with warp size. Geometry alone gave AUC 0.81 pooled and 0.92 on
  FERET, and three fixes failed (planning record, section 14.1). In the landmark ladder the two sources of an
  R3 have FR cosine 0.87, those of an R4 0.23, "and everything that travels with it (ghost size, pose and shape
  gap)".
- **Outline ghost and symmetry.** The round-3 review of the ladder-ordered recipe concluded today: a loss that
  forces same-person and mirror mixes below two-person morphs makes the network find a separator, and the
  cheapest ones are left-right symmetry (mirror rung) and the size of the outline ghost in hair and shoulders
  (`ideas/round3/sota_vetting.md`, section 1.3). It recommends keeping R3 and R3m as test-only rows.
- **The mirror rung is not a clean one-person negative.** In identity and lighting terms it is a different
  face (planning record, section 14.1). Measured: mirror self-morph against two-person morph 0.49 to 0.69.
- **Our pair-trained heads already sit at the floor for storage history.** Heads trained on warp-only against
  morph pairs flag 3.9 to 5.4% of history-matched photos at the 5% threshold
  (`experiments/PD1_signal-isolation-paired-differences/landmark/result.md`, unreviewed).

### 4.1 Second-identity field with a one-person blend as its complement (5.1)

**Closest prior work in morph detection.** Seibold et al. (JISA 2020): partial morphs whose complement is the
untouched photo, with a four-class region scheme. PW-MAD: per-pixel labels. Qin, Peng and Long (TIFS 2022):
localisation of morphed regions, not read. Our own round-1 raw idea "Region-partial morphs with patch-level
mixing targets: each image is its own control" (complement: the warped host, with decoy seams). In the deepfake
field: ED4's composites of real faces. I found no work where the complement is itself an equal blend of one
person. That one element is new as far as this limited search goes.

**Check against measured facts.**

- The softness cross is not a cross. As written, the second-layer weight is 0.5 on the one-person part and 0.25
  to 0.3 on the two-person part. In those images the two-person part is always the sharper one. In the other
  images sharpness is equal. Over the training set "sharper" then predicts "two persons". That is a planted
  cue with the opposite sign of the natural one, not the absence of a cue. Fix: draw the weight field
  independently of the identity field, so that every image has all four cells (one or two persons, weight 0.5
  or 0.25 to 0.3).
- Mid-frequency cancellation is not crossed and cannot be. Two photos of one person line up; two persons do not.
  The band-power statistic that reaches 0.89 to 0.91 for warp-only against morph will also separate the two
  parts. The analysis calls this "the evidence". Then the head must be reported as excess over that statistic
  inside the image, as the paired-difference experiment does.
- The uniform rungs are not the uniform case of the composite. A composite's second layer is warped twice and
  its shape holds a quarter of the partner. Ladder R3 and R4 are single runs. The head can learn "second layer
  warped twice". The build must include the double-run uniform cases (field 0 everywhere, field 1 everywhere)
  and show that they score like single-run R3 and R4.
- The within-image contrast helps only in training. At test time the image is uniform. The round-2 controls
  already demand proof that a map adds something over an image label ("shuffled maps", "five-arm ablation").
  The first test in the analysis has no such arm.

**Cheapest confound.** Capture detail. The host H and its second photo H' usually share session, lighting,
camera and hair; the partner P does not. Inside one image the two-person part is then also the part whose
second layer has another light direction, colour and hair outline. The record names this: "hair, collar and
lighting mismatch drive ghost energy in the periphery". The field can read "second capture session", not
"second person". **Control:** cross session with person. Where the data allow (FRGC has several sessions per
person), build composites whose one-person part uses a photo from another session and whose two-person part
uses a partner from the same session and setup as that photo. Blank the periphery with the approved constant
colour in both parts. Report the within-image AUC separately for same-session and other-session complements.

**Verdict: revise.** The construction is the only new element of the four proposals. It is silent on generator
morphs, needs two rulings from the author (double run of the wrapper; class of a composite), and cannot be in
a trained network by 14 Nov unless the first test passes on day one.

**Revised first test (one day, CPU build, cached DINOv3 tokens, ridge patch head).**

1. Build from the landmark-ladder hosts, folds that hold out both persons of every pair: 1,500 composites with
   independent identity and weight fields; 300 seam-only composites; 300 double-run uniform images each for
   field 0 and field 1; where FRGC sessions allow, 300 other-session composites.
2. Three heads on the same tokens and persons: (a) the composite field; (b) the same patches with the image
   label broadcast (R3 as 0, R4 as 1); (c) the existing alpha-field head.
3. Read on held-out persons, OpenCV-style engine decides:
   - R3 against R4 inside thirds of the landmark displacement between the two sources (geometry-matched), with
     the periphery blanked;
   - within-image AUC, and the within-image AUC of the band-power statistic on the same patches;
   - shifts R0 to R2w and R0 to R1; double-run against single-run uniform scores.
4. **Pass:** geometry-matched R3 against R4 at least 0.75 with lower bound above 0.65 and at least 0.05 above
   head (b); within-image AUC at least 0.05 above the band-power statistic, also on other-session composites;
   R0 to R2w at most 0.3 SD on both engines; at most 10% of history-matched photos flagged.
5. **Kill:** head (a) not better than head (b) by 0.03 and no halving of the R2w shift (then the composites are
   decoration); or within-image AUC on other-session composites below 0.55 (it reads the session); or
   geometry-matched R3 against R4 below 0.65; or R2w shift above 0.5 SD on the OpenCV-style engine.

Scores: impact 5, feasibility by 14 Nov 4, novelty 6.

### 4.2 Cumulative ladder code instead of one morph label (5.2)

**Closest prior work in morph detection.** The label choice "one-person blend is genuine" is MorDeephy (2022)
and Pimenta et al. (2023). An ordered multi-bit code was not found (the analysis's search; I could not repeat
it). On our own table: round-3 recipe 1, "ladder-ordered CLIP ViT-L/14 LoRA network", with an order term in
the loss. Its review today says: drop the order term. The cumulative code is a sibling of that recipe. Its
third bit is trained on exactly the contrast the review warns about.

**Check against measured facts.**

- The first test does not test the idea. On frozen mean tokens three logistic bits are three separate probes;
  the analysis says so. What it measures is "one-person blends as negatives", which the paired-difference
  experiment already measures (R3 against R4 0.759 [0.683, 0.838] for a head never shown R3).
- The history bit is a risk, not a protection. If history is crossed with the labels, the attack bit has no
  reason to use it. A supervised history output asks the shared features to encode history more clearly. Our
  pair-trained heads already sit at the 5% floor for history flags without it. Leave the bit out, or show in
  one arm that it does not raise the R0 to R1 shift.
- R3m as a negative of the third bit invites a symmetry reader (asymmetry 2.1 for a mirror mix against 12.0
  for a two-person morph, experiment AD1b, four persons). Keep R3m out of the third bit's loss; read it at
  test time only.
- The soft label "rises with the mixing fraction" does not isolate identity. Warp size and ghost size rise with
  the fraction too. It needs the paired dose: the same six levels for a same-person pair must stay flat.
- ProDet's aligned anchors do not exist for us (the analysis says so), and its attention module is not
  specified. The second step is more than "one LoRA fit" of engineering.

**Cheapest confound.** Warp size and outline ghost, seen in the image as softness and as a doubled hair and
shoulder outline. Geometry alone reaches 0.81 to 0.92 on R3 against R4. **Control:** read the third bit inside
geometry-matched groups; blank the periphery in every rung with the approved constant colour; give the excess
over the best of three simple statistics (landmark displacement from the landmark files, Laplacian variance,
band power 0.125 to 0.25 cycles per pixel); hold out both persons.

**Verdict: revise.** Keep the label set (one-person blends are negatives of the attack score) and test the
code against the plain binary label on the same images. If the code does not beat the binary label, use the
binary label and cite ProDet and ED4 as the reason for the negatives.

**Revised first test (three small LoRA fits on the MADation recipe, same images, same folds, one seed each,
plus a CPU floor).**

- Arm A, binary: R4 against all one-person rungs (R0, R1, R2w, R3; R3m test-only).
- Arm B, cumulative code: three bits, no history bit, attack score = third bit.
- Arm C, one-hot: the same rungs as classes, attack score = probability of the R4 class (the control ProDet
  argues against).
- CPU floor first (hours): the logistic third bit on cached mean tokens, read as stated below. If the floor
  already fails the kill mark, do not spend the fits.
- Read on persons held out as pairs, OpenCV-style engine decides: geometry-matched, periphery-blanked R3
  against R4 with interval; excess over the three simple statistics; R0 to R1 and R0 to R2w shifts; share of
  history-matched photos flagged; native EER on the FRLL landmark cells against history-matched photos.
- **Pass (for the code):** arm B beats arm A by at least 0.03 on geometry-matched R3 against R4, or halves the
  R0 to R2w shift, at no more than 1 point of native EER, and is not worse than arm C.
- **Kill (for the code):** no such gain. Then the code is decoration. **Kill (for the third bit as such):**
  geometry-matched R3 against R4 below 0.65, or excess over the best simple statistic below 0.05.
- One seed per arm cannot rank arms that differ by less than the fold-to-fold spread. Report the spread.

Scores: impact 5, feasibility by 14 Nov 5, novelty 3.

### 4.3 History-subspace surgery (5.3)

**Closest prior work in morph detection.** None found for projection or erasure (the analysis's search). The
nearest published neighbour is Kashiani et al. (consistency across augmented views). The nearest work of all is
our own round-1 raw file, which holds the audit on released heads, the adaptation rule and the erasure variant
(section 2, item 9).

**Check against measured facts.**

- For a linear head the audit says little that is new. The score shift of a photo under history is the head
  weight times the feature difference. That is the image-level measurement we already have. The one new
  read-out is "subspace only": can the benchmark be solved from the history directions alone.
- Softness is shared. The analysis itself writes that the cancellation in a morph "is the same number that
  storage history moves". The history subspace then holds real blend evidence. Outcome three of the audit
  ("flags fall, EER rises strongly: the published number rested on the history subspace") cannot be told apart
  from "the encoder puts blend softness and storage softness on one axis". Round 1 already asked for this
  check: "measure the cosine between the history direction and the morph-versus-genuine direction: if they are
  collinear the problem is intrinsic to the backbone".
- No baseline. A random subspace of rank 16, or the top principal directions of genuine features, may also keep
  or destroy performance. S3 shows no such control either.
- The training rule has little room. A data-level change (the same processing chain on both classes) already
  cut the flagged share of shrunk photos from 19 to 40% down to 4 to 8% in four pretrained backbones at 0.4 to
  1.5 points (A30 amendment 6, planning record, section 14.2). Our pair-trained heads sit at the 5% floor. The pass mark "flags fall by half" has to be measured against these, not against an
  untreated network.
- The audit depends on the own-crop re-score. The ViT-L/14 release has no usable statement yet (brief). Only
  the ViT-B/16 release and SelfMAD can be audited now.

**Cheapest confound.** Softness (and, for the R2w directions, warp): the removed directions carry legitimate
blend evidence, so a rise in benchmark error after removal looks like "the benchmark number rested on storage
history" when it is the physics of blending. **Control:** (a) R2w against R4 on the ladder before and after
removal; both sides have the same history, so any loss there is lost blend evidence; (b) 100 random subspaces
of the same rank and the top principal directions of genuine features as baselines; (c) a placebo subspace
from an allowed intervention that does not touch softness (lossless flip: photo against its flipped copy);
(d) estimate on one photo pool, read on another.

**Verdict: revise.** Keep step A as a half-day audit figure with the four controls. Drop step B as a method;
at most one ablation row beside the data-crossed fit. Cite LEACE and the conditional variance penalty, not S3
alone.

**Revised first test (half a day, features and linear algebra only; ViT-B/16 release and SelfMAD, each through
its own preprocessing).**

1. Subspace from R1 minus R0 on pool A at rank 1, 2, 4, 8, 16. Before anything else: cosine between its span
   and (i) the benchmark mean difference morph minus genuine, (ii) the ladder mean difference R4 minus R2w.
2. Scores with full features, with the subspace removed, with the subspace only; the same for the random,
   principal-direction and flip subspaces.
3. Read on pool B and on the FRLL landmark cells: share of history-matched photos flagged at the fixed
   threshold; EER; ladder R2w against R4.
4. **Usable as an audit finding:** at some rank of at most 16 the subspace-only EER stays within twice the full
   EER while all three baseline subspaces are near chance, and R2w against R4 loses at most 0.03 after removal.
5. **Reported as "intrinsic collinearity", not as a shortcut:** R2w against R4 loses more than 0.10 after
   removal. Then no projection rule may be used in training.
6. **Kill:** no rank up to 16 lowers the flagged share on pool B by a quarter, or the baseline subspaces do as
   well as the history subspace.

Scores: impact 4, feasibility by 14 Nov 7, novelty 3.

### 4.4 Identity-agreement slots with a partner-retrieval test (5.4)

**Closest prior work in morph detection.** MorDeephy (two identity embeddings, dot-product score, same-person
morphs as genuine), its follow-ups including Pimenta et al., and Caldeira et al. (two identity scores from a
teacher's encoding of the two sources, score `1 - id1 * id2`). What remains new: one network instead of two,
FR-embedding targets instead of identity classes, storage history crossed in, and the retrieval test.

**Check against measured facts.**

- The head it "upgrades" was dropped after two failures (section 2, item 8). The reference-free demorpher's
  strict recovery of 0.00 to 0.27% predicts the outcome of a partner-retrieval test.
- The retrieval test can be passed without separating two identities. A morph matches both contributors by
  construction. A slot that copies the morph's own mixed identity ranks the partner near the top. Pairs are
  usually matched in sex and ethnicity, so even a demographics reader beats the stated chance level of 5%.
- A head on frozen tokens with about 430 training persons cannot learn a map into FR-embedding space that
  holds for new persons. The analysis itself says the idea needs "a training set with many partners". That
  set and an adapted network cannot be built and reviewed by 14 Nov.
- Slot distance for R3 against R4 meets the warp-size confound like every other head.
- Silent on generator morphs (the analysis says so). Our record estimates the identity ceiling for generator
  cells at 0.65 to 0.78 for the median ladder pair and 0.59 to 0.67 for strong look-alikes (an estimate, not a
  measurement; planning record, section 14.1).

**Cheapest confound.** For the score: warp size and ghost size (control: geometry-matched groups, periphery
blanked). For the retrieval test: mixed-identity reading and pair-selection demographics (control: a gallery
of the host's own sex and ethnicity group without the host; a baseline that uses the ArcFace embedding of the
morph itself for both slots; and a direction test, in which the difference of the two slots must align with
the difference of the two contributors' embeddings more than with the difference to a random third person).

**Verdict: drop as a method for this paper.** Cite MorDeephy in related work as the nearest neighbour of our
rule "one-person blends are genuine". Keep one thing: the direction test, as a diagnostic for whatever head
claims to read a second person (the third bit of 5.2, the field of 5.1).

**Revised first test (only if the lead wants the diagnostic; one hour, no training of slots).** On held-out R4
images with existing ArcFace embeddings: (i) baseline, rank the true partner by the ArcFace embedding of the
morph itself in a sex- and ethnicity-matched gallery of at least 100 held-out persons without the host; (ii)
for the head under test, regress its penultimate features onto the embedding difference host minus partner
(ridge, both persons held out) and read the cosine with the true difference against the cosine with a random
third person's difference. **Pass:** direction cosine above the random-person value with a lower bound above
0. **Kill:** not above it. A slot head is worth building only if it beats baseline (i) in partner rank.

Scores: impact 2, feasibility by 14 Nov 2, novelty 2.

### 4.5 The three diagnostics of section 5.5 of the analysis

These are the best part of the file for a three-day sprint. Two notes.

- **Label ablation** (one-person blends labelled genuine, left out, labelled attack). ED4 is a sound outside
  precedent (numbers verified). Inside morph detection the two ends are published habits: MorDeephy labels
  them genuine, SelfMAD and Kashiani et al. label them attack. Nobody seems to have run the three arms on one
  recipe. Read it with the geometry and periphery controls of 4.2, or the result will be the outline ghost.
- **Threshold table.** Use the corrected GenD numbers (10.9% to 92.9%, mean 49.1%, at one mean AUROC of 91.2)
  and add the rebalanced protocol (Xception about 0.92 to about 0.61) as the second outside precedent.

---

## 5. Summary table

| Proposal | Verdict | Impact | Feasible by 14 Nov | Novelty | One-line reason |
|---|---|---|---|---|---|
| 5.1 Second-identity field, one-person blend complement | revise | 5 | 4 | 6 | New construction, but its softness cross plants a reverse cue, the session of the partner is uncrossed, and no arm shows the map beats an image label |
| 5.2 Cumulative ladder code | revise | 5 | 5 | 3 | The frozen first test does not test the code; the third bit meets the warp-size and outline-ghost confound; the history bit should go |
| 5.3 History-subspace surgery | revise | 4 | 7 | 3 | Already in round 1; keep the audit with random, placebo and blend-evidence controls; the training rule has no room left |
| 5.4 Identity-agreement slots | drop | 2 | 2 | 2 | MorDeephy exists; the head failed twice in our record; the retrieval test is passed by a mixed-identity reader |

---

## 6. Recalled, not verified in this task

The search budget ran out before I could look these up. Do not cite them from this file.

- DRCT, Chen et al., ICML 2024 (reconstructions of real images as hard samples labelled fake). Named in
  `ideas/round3/sota_vetting.md` with a proceedings address; I did not open it.
- IDSwapMAD, Banas et al., EURASIP J. Inf. Secur. 2026 (face-swapped references as the genuine class for
  differential detection). In our planning record; not opened by me.
- A null-space method for CLIP features in generated-image detection ("NS-Net", 2025). Recalled only.
- Local Relation Learning for Face Forgery Detection (Chen et al., AAAI 2021) and other patch-relation methods
  that precede pairwise self-consistency. Recalled only.
- Multi-class morph "fingerprinting" or source attribution work (for example in the Colbois thesis, Idiap
  2025, seen as a search hit title only). Relevant to whether any ordered or multi-attribute label exists in
  morph detection. Not opened.
- Whether newer work (2026) audits morph benchmarks for resolution or compression differences. My one search
  found none; one search is not evidence of absence.

---

## 7. Sources opened for this check

Deepfake detection: arXiv 1912.13458, 2204.08376, 2012.09311, 2408.17052, 2210.14457, 2203.01318, 2411.15633,
2408.06779, 2508.06248, 2410.04372, 2406.13495, 2606.01843, 2605.10334, 2606.30528, 2309.05911, 2311.11278,
2405.00483 (each at https://arxiv.org/abs/ plus the number; full texts at https://arxiv.org/html/ or
https://ar5iv.labs.arxiv.org/html/); OST at
https://proceedings.neurips.cc/paper_files/paper/2022/hash/9bf0810a4a1597a36d27ceea58667d92-Abstract.html.

Morph detection: arXiv 2504.05504, 2308.10392, 2309.00549, 2108.10291, 1806.04265, 2208.07841, 2306.03002,
2208.03110, 2309.00665; Seibold et al. journal record via DOI 10.1016/j.jisa.2020.102526; Qin et al. via DOI
10.1109/TIFS.2022.3212276 (abstract level).

Method references for 5.3: arXiv 2306.03819, 2004.07667, 1710.11469, 2204.02937, 2206.02749, 2509.22412.

Data alignment and robustness: arXiv 2412.17671, 2410.11835, 2403.17608, 2502.07778, 2604.25889.

Metadata only, through the arXiv listing: the 33 references named at the end of section 1.1.

Repository files read: `ideas/ROUND3_BRIEF.md`, `ideas/CONSOLIDATED_v2.md`, `docs/PLANNING_RECORD.md` (sections
10, 14.1, 14.2, 15), `ideas/IDEAS_v1.md` (M3 and section E), keyword look-ups in `ideas/ROUND1_raw.json` and
`ideas/round3/*.md`, `experiments/AF0/result.md`,
`experiments/PD1_signal-isolation-paired-differences/landmark/result.md`.
