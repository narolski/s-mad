# Independent check of the cross-field analysis on diffusion-generated portraits

11 Nov 2026, evening. Checker for `literature/crossfield/diffusion.md`. Research and writing only. No
experiment was run, no sealed file was opened, nothing was written outside this file.

Terms. S-MAD = single-image morphing attack detection. AUC = area under the ROC curve. EER = equal error
rate. DiffAE = diffusion autoencoder (Preechakul et al.), the generator behind MorDIFF-type morphs; it has a
semantic code and an image-sized stochastic code (noise map). FR = face recognition. MMPMR = share of morphs
that match both contributors in FR. SSIM = structural similarity (1.0 = identical images). LoRA = low-rank
adaptation of a frozen network. L = the analysis's "common last hop", one DiffAE encode-and-render pass.

How sources are marked. **[P]** = I read the extracted text of the PDF myself. **[H]** = full HTML text read
through the automated page reader (numbers need a look at the PDF before printing). **[A]** = abstract page
only. Rungs R0 to R4 and x0 to x3 are those of `ideas/ROUND3_BRIEF.md`.

---

## 1. Bottom line

1. The reference list is honest. I opened 31 of its entries (26 numbered, 5 from its "recalled" list). Every
   work exists, and authors and years are right. No invented number was found.
2. Seven statements read more into a source than it says (section 3). The one that matters: "the second
   person sits mostly in the stochastic code" does not follow from Fast-DiM Table III. The DiffAE paper, the
   DiM paper and our own distance numbers point the other way for coarse identity.
3. Three "none found in morph detection" statements are too strong. Same-person morphs as genuine training
   images exist (MorDeephy). Equal degradation of both classes exists (Seibold et al. 2018; Ferrara et al.).
   A published demonstration that a detector learns the dataset and that shrink-and-enlarge changes the
   result exists (Spreeuwers et al. 2018).
4. Two of the four proposals repeat ideas that round 3 already holds and already vetted at 18:29
   (`ideas/round3/mechanism_vetting.md`): the three-way output (there: three-level ordinal score) and the
   code factorial (there: code-factorised twins). The analysis does not mention them.
5. Verdicts. Proposal 1 (common last hop): **drop**. Proposal 2 (three-way output): **revise**, as one more
   arm of the labelling comparison that already exists. Proposal 3 (code factorial): **revise**, merged with
   the round-3 design; keep its one real improvement. Proposal 4 (selection with a certificate): **keep**,
   with matching in place of weights and one added control arm.
6. None of the four raises a number in the published tables. Proposal 4 is the only one that adds a
   checkable property to the network the paper will report.
7. Limit of this check: the shared web-search budget ran out. I got 8 searches through (4 more were
   refused). Everything else is direct page reads. Statements of the form "not found" are bounded by that.

---

## 2. Reference verification

Checked = exists, authors, venue, year, and the claims the analysis draws from it.

| # in analysis | Work | Result |
|---|---|---|
| 7 | Mandelli, Bestagini, Tubaro, arXiv 2407.10736 [H] | Confirmed. Table I: AUC 0.994 fully synthetic against laundered (all data). Table II: 0.990 at JPEG 70, 0.970 at 0.5 times downscale; accuracy at the fixed threshold 95.9 to 80.2%. Section V: 96.15% to 39.08 to 56.67%. Two points to add: the pipeline is two detectors in sequence, each scoring 800 patches of 96 px; the camera-model test uses the Vision set (28 camera models, not faces) |
| 8 | Cannas et al., arXiv 2412.03261 [H] | Numbers confirmed (Table 1: four of nine detectors at 0.96 to 0.99 at 0.12 bits per pixel; Table 4: 0.96 to 0.65 with 20% JPEG AI training images). The "harmful or innocuous" sentence is there. **Venue "ICCV Workshops 2025" is not shown on the arXiv page** (v2, 18 Mar 2025): not verified |
| 2 | Rajan et al., arXiv 2410.11835 [H] | Confirmed: Table 2 (24.27, 61.25, 76.36), Table 5 (54.16 to 83.58; 69.56 to 29.83), "validly considered fake", paired batches ("Ours-Sync"). The quoted sentence is the caption of Fig. 2 and is about one detector ("Corvi associates downsampling with real images …"), not about unaligned training in general |
| 3 | B-Free, arXiv 2412.17671 [H] | Table 2 and Table 5 confirmed (61.9, 80.7, 81.4, 92.2, 96.4; negative log-likelihood 1.91 and 0.10 are the first and last rows; 96.3 and +20.7 over the next method). **Fig. 2 is misdescribed**, see section 3 |
| 4 | DDA, arXiv 2505.14359 [H] | 11 benchmarks, 90.7, +15.7 confirmed (Table 2; the abstract says 8 benchmarks). 93% confirmed (Section 3.1). Venue now confirmed: arXiv comment "NeurIPS 2025 Spotlight". Two corrections in section 3 |
| 5 | Grommelt et al., arXiv 2403.17608 [H] | All numbers confirmed (Table 2: 80.45, 94.84, 100.0; Table 3: 53.91 to 67.17; Table 4: 71.68 to 82.74 and 74.09 to 85.83 with about 23% of the data). The sentence on random JPEG augmentation is there |
| 13 | Staniszewski, Kuciński, Deja, arXiv 2410.23530 [H] | Table 2 (0.382 against 0.039) and Table 3 (0.46 against 0.72) confirmed; Fig. 5 as described. Update: now v5 (27 Jan 2026), arXiv comment "ICLR 2026" |
| 12 | NoiseDiffusion, arXiv 2403.08840 [A] | Confirmed, ICLR 2024 |
| 16 | Fast-DiM, arXiv 2310.09484 [H] | Table III numbers confirmed (4.5 / 3.48 / 2.04 for AdaFace, ArcFace, ElasticFace). **The reading built on it is not supported**, see section 3. Venue missing in the analysis: arXiv comment "Accepted as a paper in IEEE Security and Privacy" |
| 15 | DiM, arXiv 2301.04218 [H] | Quote on variant C confirmed. IEEE TBIOM vol. 6 no. 1, Jan 2024. The same paper says the semantic code carries most identity information |
| 11 | Diffusion Autoencoders, arXiv 2111.15640 [H, ar5iv] | SSIM 0.927 (20 steps) and 0.991 (100 steps) confirmed, on CelebA-HQ at 128 px, model trained on FFHQ. Table attribution unsure (the reader places 0.991 with MSE 6.07e-5 in Table 1, the step sweep in the ablation table). With a random noise map SSIM is 0.677 to 0.695 |
| 9 | Zhou et al., arXiv 2506.00874 [H] | "For every one of the 1000 prompts" and "≈10 optimization steps" confirmed (Section 3.4). **Baseline mislabelled**, see section 3 |
| 10 | Zhou et al., arXiv 2509.12995 [H] | Table 1 (96.1, 92.4, 57.2), Table 4 (27.4, 44.4), Table 5 (0.828, 0.861) confirmed. The pretraining-exposure explanation is worded by the authors as speculation |
| 18 | Zhang, Ramachandra, Raja, Busch, arXiv 2501.09817 [H] | Quote confirmed; no method and no test given, as the analysis says. Both classes are printed and scanned; the 15 KB limit applies to the compressed type. **Venue and pages (CVPR Workshops 2024, 1510-1518) are not shown on the arXiv page**: not verified by me |
| 6 | Stay-Positive, arXiv 2502.07778 [H] | 57.25 to 99.33 confirmed (Table 1); WebP finding and the stated limitation confirmed |
| 17 | Colbois and Marcel, arXiv 2410.16802 [H] | Tables 5, 6, 7 confirmed (35.78, 42.65; 60.50, 56.55; 0.87, 0.82, 0.48). The 256 px crop is stated in the print-and-scan paragraph only |
| 1 | AEROBLADE, arXiv 2401.17879 [H] | 0.978 to 0.999 confirmed (Table 1); 0.992 is in the introduction. Two wordings too strong, see section 3 |
| 29 | Colbois and Marcel, BIOSIG 2022, arXiv 2209.00404 [P] | Confirmed ("a pretrained ResNet effective for GAN image detection is the most effective overall, reaching close to perfect accuracy") |
| 14, 20, 21, 30, 31, 32, 33, 49 | MorDIFF; DRCT; Ren et al.; SRL-MAD; R-FLoRA; DCMorph; SFDemorpher; Bodin et al. [A] | All confirmed as cited (IWBF 2023; ICML 2024, PMLR 235:7621-7639; arXiv 2602.07814 with 16 methods, 23 variants, 75.0 and 37.5%, 0.01 to 0.87, 18 to 30%; IWBF 2026; TIFS 2026 accepted; CVPR Workshops 2026; arXiv 2603.28322; ICLR 2025) |
| recalled list | Semi-Truths; TGIF; REPAIR; AFLite; "Organic or Diffused" [A] | All five exist and can move to "verified": arXiv 2411.07472 (NeurIPS 2024 Datasets and Benchmarks); arXiv 2407.11566 (IEEE WIFS 2024); arXiv 1904.07911 (CVPR 2019); arXiv 2002.04108 (ICML 2020); arXiv 2402.03214 (Ha et al.; the analysis says "searched, not found") |

Not re-opened by me: the other 23 entries marked [S] in the analysis, and MAD-DDPM, FD-MAD, MADPromptS.

---

## 3. Errors and statements that go beyond the source

1. **Fast-DiM Table III does not show where the second person sits.** The table is built like this: the two
   photos are averaged pixel by pixel, noise is added "in accordance to the noise schedule at time t", and
   the model, "still conditioned on the morphed latent representation", removes it. At noise level 1.0 the
   start is pure noise. MMPMR then falls to 4.5 / 3.48 / 2.04%, against about 90% for the normal morphs
   (their Table VI). The table has no row for a one-person render with fresh noise. So it shows that a render
   from the averaged semantic code alone does not pass as both people. It does not show that one person's
   own render keeps or loses identity, and it does not place "the second person" in either code. Three
   sources say coarse identity is in the semantic code: Preechakul et al. (changing the noise map "only
   affects minor details, such as the hair and skin details, the eyes, or the mouth"); the DiM paper; and
   our own identical-and-mirrored-inputs check (AD1b): semantic distance 0.773 to another photo of the same
   person against 1.744 to another person, while noise maps are equally far apart for everyone (0.97 to
   0.99). The analysis marks its reading as its own. But Proposal 3 then says "the field predicts the
   stochastic code". It does not. The honest statement is: open question, both codes are needed for FR
   success.
2. **Same consequence for the "cheap side instrument" of Proposal 1.** A render from the semantic code with
   fresh noise is said to "drop the contributors' identity" so that only pose, expression, lighting and
   backdrop remain. No source shows that. By the three sources above it keeps coarse identity. A detector
   that still separates a cell on such renders could read the averaged semantic code, which is morph
   evidence, not benchmark composition.
3. **Zhou et al. (latent prior bias), Table 1.** 79.20 is the CLIP-plus-linear-head baseline. 94.63 is CLIP
   with LoRA rank 4 after the adversarial training. The analysis prints both as "CLIP with LoRA rank 4:
   79.20 to 94.63". Their Table 4 also reports that only 75% of attacks succeed in a second setup.
4. **B-Free, Fig. 2.** Not "the same DALL·E 3 fakes" scored against two real sets. The fakes are generated
   from RAISE images or from COCO images and tested against the real images of the same set. The "always
   above 80%" sentence is in the text of Appendix F; I could not confirm the figure number.
5. **DDA.** The paper says the detection rate "drops dramatically" when high frequencies are masked; it
   gives no rate after masking, so "removes the detection" is too strong. The open point in the analysis's
   last line is resolved: the frequency alignment is JPEG re-compression of the reconstruction at the real
   image's estimated quality (Section 3.2; applied with probability 50% in training, Section 4), plus a
   pixel mixing step (their Eq. 3). "High-frequency fusion" is wording of the introduction only.
6. **AEROBLADE.** The format problem of DIRE's data is stated as a suspicion in the part I could read
   ("we suspect that the DIRE representations … were saved inconsistently", Section 5.3; Section 9 was cut
   off by the reader). "Weaker than a trained detector under perturbation" holds against one detector
   (Corvi et al., trained on perturbed images); the paper reports it ahead of two other trained detectors
   in most settings.
7. **"Under our constraints this is the one permitted operation that changes low-level statistics"**
   (Proposal 1). The existing shrink-and-enlarge path, run unchanged, is permitted and changes them. It is
   rung R1 and the front end of the canonical-view idea in `ideas/round3/nuisance_ideas.md`.
8. **Proposal 2's score.** With a softmax, P(G) + P(S) = 1 − P(M). So s = log P(M) − log(P(G) + P(S)) is the
   log-odds of P(M). A binary head trained with the same negatives estimates the same quantity. "The
   contrast against both non-morph classes" is not a new score; only the training signal differs.
9. **"None found" for the same-person negative** (Proposal 3) contradicts our own
   `14_CLASS_DEFINITIONS.md`, which the analysis cites elsewhere. I confirmed it in the paper: MorDeephy
   (Medvedev, Shadmand, Gonçalves, arXiv 2208.03110) [P], Section 4.3: "we utilize selfmorphs, which are
   generated by applying face morphing to images of the same identity … we consider selfmorphs as bona fide
   samples", to "focus morphing detection onto the deep face features behaviour, rather than to detecting
   artefacts". The rule is new only for diffusion morphs and for the matched step count.
10. **"Published audit of dataset shortcuts: not found"** (part 3) needs one exception, see section 4.3.
11. **"The closest thing to our ladder is one matched step"** (part 2). Two works have graded steps, though
    not per-image controls: Semi-Truths (edits of graded type and degree) and FakeChain (chains of one, two
    and three manipulations). The sentence should say "no per-image ladder with matched controls".
12. Small: Mandelli et al. "run their laundering study on faces" is true for detection, not for the
    camera-model part. The pretraining explanation of Zhou et al. is speculation by the authors' own word.

---

## 4. Important work the analysis missed

### 4.1 Generated-image detection, 2024 to 2026

- **Liu, Liu, Wang, Soumik, "Exploiting the Final Component of Generator Architectures for AI-Generated
  Image Detection", arXiv 2601.20461 (v2, 10 Mar 2026)** [H]. https://arxiv.org/abs/2601.20461. Real images
  are passed through a generator's last component (autoencoder decoder, token decoder, or diffusion
  denoiser) and form the fake class. 98.83% average accuracy over 22 test sets of unseen generators with 100
  samples per component (abstract). This is the field's own "last hop" paper and the nearest source for
  Proposal 1. The reader flagged placeholder-looking entries in its reference list; treat with care.
- **Heo and Woo, "FakeChain: Exposing Shallow Cues in Multi-Step Deepfake Detection", arXiv 2509.16602**
  [A]. https://arxiv.org/abs/2509.16602. Chains of up to three manipulations. Detectors rely on "last-stage
  artifacts rather than cumulative manipulation traces"; F1 falls by up to 58.83% when the last step differs
  from training (abstract). Direct evidence for the "last hop decides" premise.
- **Zhou et al., "Simplicity Prevails", arXiv 2602.01738 (v2, Apr 2026)** [A].
  https://arxiv.org/abs/2602.01738. Follow-up to reference 10 of the analysis. Linear probes on frozen
  foundation features "remain blind to VAE reconstruction and localized editing" (abstract). A caution for
  our frozen-feature probes: what they read on diffusion morphs is probably not the decoder trace.
- **Liu et al., "Beyond Artifacts: Real-Centric Envelope Modeling", arXiv 2512.20937 (Dec 2025)** [A].
  https://arxiv.org/abs/2512.20937. Models the real-image side with near-real samples made by perturbed
  self-reconstruction; +7.5% average over eight benchmarks (abstract).
- **Li et al., "How Noise Benefits AI-generated Image Detection", arXiv 2511.16136 (v2, Apr 2026)** [A].
  https://arxiv.org/abs/2511.16136. Learned feature noise to suppress shortcut directions; 42 generators;
  +5.4 average accuracy (abstract).
- **Yan et al., "Orthogonal Subspace Decomposition for Generalizable AI-Generated Image Detection", arXiv
  2411.15633** [A]. https://arxiv.org/abs/2411.15633. Detectors collapse onto a low-rank set of fake
  patterns; the main singular directions of the pretrained weights are frozen and the rest adapted. An
  alternative to LoRA that is one network at test time.
- **Chai, Bau, Lim, Isola, "What makes fake images detectable? Understanding properties that generalize",
  arXiv 2008.10588 (2020)** [P]. https://arxiv.org/abs/2008.10588. The first statement of the common-pipeline
  rule: "we pass real images through the same data transform as used to train the generator. We then save
  the real and fake images using identical pipelines", because otherwise "the classifier can simply learn to
  detect the differences in preprocessing".
- **Partial edits and three kinds of images**: Semi-Truths (Pal et al., NeurIPS 2024 Datasets and
  Benchmarks, arXiv 2411.07472) [A]; TGIF (Mareen et al., IEEE WIFS 2024, arXiv 2407.11566) [A]: localisers
  catch spliced edits and miss fully regenerated images; SID-Set and SIDA (Huang et al., arXiv 2412.04292)
  [A]: authentic, fully synthetic and tampered images in one set. These are the field's precedents for a
  third category besides Mandelli et al.
- **Sun et al., "DiffusionFake", NeurIPS 2024, arXiv 2410.04372** [A]. https://arxiv.org/abs/2410.04372.
  Face-swap detection: during training the detector's features must let a frozen Stable Diffusion model
  reconstruct both the source and the target face; nothing is added at test time. It is the nearest
  published training signal for "a second identity is present" that keeps one network on one image. It
  belongs to the deepfake lens, but the diffusion analysis should have named it.

### 4.2 Bias removal by weighting or selection (bears on Proposal 4)

- Byrd and Lipton, "What is the Effect of Importance Weighting in Deep Learning?", arXiv 1812.03372 [A]:
  the effect of sample weights fades as a deep network trains on; L2 regularisation and batch
  normalisation partly restore it.
- Sagawa et al., arXiv 2005.04345 [A]: with large models, subsampling the majority group works better than
  up-weighting the minority group.
- Idrissi et al., "Simple data balancing achieves competitive worst-group-accuracy", CLeaR 2022, arXiv
  2110.14503 [A].
- REPAIR (Li and Vasconcelos, CVPR 2019, arXiv 1904.07911) and AFLite (Le Bras et al., ICML 2020, arXiv
  2002.04108) [A]: resampling against a bias classifier. AFLite lowers accuracy on the filtered set from 92%
  to 62% on its language task (abstract): filtering has a price.

### 4.3 Morph detection (prior art the analysis reports as not found)

- **Spreeuwers, Schils, Veldhuis, "Towards Robust Evaluation of Face Morphing Detection", EUSIPCO 2018**
  [P]. https://new.eurasip.org/Proceedings/Eusipco/Eusipco2018/papers/1570439319.pdf. A detector at about 2%
  EER inside one set reaches 80% and 79% EER across sets (Table II), "suggesting that indeed the morphing
  detector learnt features very specific for the dataset". Morphs that are scaled down and up again by 0.5
  raise the EER from about 5% to above 12%; a little added noise raises it above 20%. The manipulations are
  put on the morphs only. This is the nearest published relative of our R0-against-R1 finding, seen from the
  attack side. The paper must cite it.
- **Seibold, Samek, Hilsmann, Eisert, arXiv 1806.04265 (2018)** [P]. https://arxiv.org/abs/1806.04265.
  Section 4.2: noise and blur are applied "in the original and forged face images to prevent the network
  from discriminating on these characteristics". The same paper pretrains with a multi-class label (number
  of morphed face regions) before the two-class head. Prior art for "same processing on both classes" and
  for an auxiliary multi-class label in morph detection.
- **Ferrara, Franco, Maltoni, arXiv 1901.08811; IET Biometrics 10(3), 2021** [P].
  https://arxiv.org/abs/1901.08811. A simulated print-and-scan step is applied "on all Digital images"
  (560 genuine, 560 morphed) to build the training set.
- **Damer et al., "ReGenMorph", ISVC 2021, arXiv 2108.09130** [P]. https://arxiv.org/abs/2108.09130. A
  landmark morph "is processed into the latent space of a GAN structure, and simply re-generated by the GAN
  generator". Genuine images are not re-generated. "Both face recognition systems are less vulnerable to
  the ReGenMorph" than to the landmark morph. So a laundered morph exists in the literature as an attack,
  and the pass costs attack strength.
- **Kashiani et al., IJCB 2023, arXiv 2308.10392** [P]. https://arxiv.org/abs/2308.10392. "Different
  instances of the same identity are employed in our morphing attacks": same-person morphs as attacks, the
  opposite label to MorDeephy.
- **Neddo, Blasingame, Liu, IJCB 2024, arXiv 2404.06559** [A]. https://arxiv.org/abs/2404.06559. A
  single-image detector not trained on print-scanned morphs: error on morphs rises by up to 96.12%
  (abstract).
- **Di Domenico, Borghi, Franco, Maltoni, arXiv 2404.07667 (2024)** [P]. The differential system with three
  attempt classes that the analysis mentions without a reference.

---

## 5. The four proposals

Facts used below, all from our record. Reviewed: the SelfMAD release flags 45% of genuine photos after a 50%
shrink-and-enlarge and 97% of photos stored small; softness floor 0.76 (512 px) to 0.87 (224 px); three
adapted releases do not separate a diffusion morph from a one-photo reconstruction (0.40 to 0.49).
Unreviewed (leads): diffusion, two-person morph against same-person mix 0.249 [0.149, 0.358] under the
mix-trained head and 0.438 under the two-person head; dedicated second-identity direction 0.793 [0.700,
0.883], reading "not consistent"; diffusion morph against camera photo, mix-trained head 0.876 against PNG
size 0.877; Laplacian variance alone 0.966 at 100 steps; landmark, same-person against two-person morph
0.88 to 0.93 by a direct probe, thumbnail 0.62 to 0.65, background only 0.54 to 0.59.

### Proposal 1. Common last hop through the unchanged autoencoder. Verdict: DROP

**Closest prior work in morph detection.** ReGenMorph (the morph side only, as an attack). Zhang et al.
2024 (one sentence, genuine side only). Equal degradation of both classes: Seibold et al. 2018, Ferrara et
al. In the neighbouring field: Chai et al. 2020 and Liu et al. 2026 (section 4.1). In our own files: the
diffusion ladder (x1 is L applied to x0) and the canonical-view front end of
`ideas/round3/nuisance_ideas.md`, which uses the approved shrink path as a common last hop for every image.
A both-class autoencoder pass as an audit of morph detectors was not found.

**Why drop.**

1. *The training crossing already exists.* The decoder trace is on both sides of the label in the diffusion
   ladder (x1 and x2 against x3) and on neither side in the landmark ladder. So the trace already carries
   no label information in the planned pool. Laundering landmark rungs adds cost, not a new contrast.
   Laundering SMDD would cost about 144 A100-hours (40,000 images at 13 s).
2. *The audit result is predicted by a fact we have.* L returns a 256 px image. The SelfMAD release flags
   45% of genuine photos after a 50% shrink-and-enlarge and 97% of photos stored small. So its separation
   will collapse on any laundered cell for a reason already in the record. Test (c) is decided before it
   runs.
3. *The pass does not equalise earlier history.* Mandelli et al. separate two populations that share one
   decoder at AUC 0.994 by what came before. At 100 steps DiffAE reproduces its input at SSIM 0.991, so the
   softness of R1 passes through. What can remove history is the aligner's reduction to 256 px, not the
   decoder. At 256 px in FFHQ-style framing the eyes are roughly 60 px apart (my estimate, not checked in
   our code), which is the band of the registered 61.2 px history. Test (a) may then pass because of the
   resize alone.
4. *The pass changes sharpness by itself.* SSIM 0.927 at 20 steps is a visible loss. At 100 steps our own
   numbers show renders from a foreign noise map sharper than reconstructions. Softness is the main readable
   morph evidence on landmark cells (0.52 times). L can remove, keep or invert it depending on the step
   count.
5. *A laundered morph may stop being a morph.* ReGenMorph lost attack strength in the generator pass. Every
   L(R4) would need an FR check against both contributors before it may be called a morph.
6. "File size equal by construction" is wrong for lossless files: PNG size follows content (0.877 for
   diffusion morph against photo).

**Cheapest confound that gives the same result, and its control.** Storage history, in the form of output
size: the collapse of a released detector on laundered cells is produced by the reduction to 256 px, with no
help from the decoder. Second: softness changed by the pass itself. Control: an aligner-only arm (the 256 px
frame that enters the encoder, saved without encode and render), next to L at 20 and at 100 steps, with the
Laplacian variance of every arm printed.

**If the lead still wants one number (no new inversion).** Take hosts whose x0 and x1 exist at 20 and 100
steps (A43 or the Athena generation DG1). Save the aligner's 256 px frame for the same hosts (needs the
lead's reading of the rules: an intermediate of an unchanged tool). Score the SelfMAD and MADation releases
through their own crop path on four arms of the same genuine photos: raw, aligner only, L at 20, L at 100.
Decision: if the aligner-only flag rate is within 10 points of the L flag rate, the decoder adds nothing and
the idea ends with one sentence in the paper. Only if L adds 20 points or more over aligner-only is there a
new audit row; it is then reported in the single-subject table, never as a genuine-image error.

Scores: impact 2, feasibility by 14 Nov 3, novelty 4.

### Proposal 2. One network with three outputs. Verdict: REVISE (fold into the existing comparison)

**Closest prior work in morph detection.** In our own files: Idea 1 of `ideas/round3/mechanism_ideas.md`
(three-level ordinal score), vetted to "revise" at 18:29 with ten objections. The proposal is that idea with
an unordered head. Published: MorDeephy (same-person morphs merged into the genuine class of a binary
detector); Seibold et al. 2018 (multi-class pretraining by number of morphed regions); Di Domenico et al.
2024 (three classes, differential setting). A single-image head with a separate single-subject class was
not found (bounded by the search limit).

**What is right in it.** An unordered softmax does not force the order genuine below single-subject below
morph. The record shows that order is violated on diffusion morphs (0.249). On that point it is better than
the ordinal version.

**What is wrong in it.**

1. The score is the log-odds of P(M) (section 3, point 8). A binary head with negatives G and S estimates
   the same thing. The proposed CPU test compares two linear heads on frozen features, so it measures only
   the shape of the boundary (one plane against the smooth maximum of two). It cannot show what a LoRA fit
   would do. The analysis says so under risks; then the test should not be the decider.
2. The network is trained to separate G from S. That is the pipeline and storage step, the cue the paper
   criticises. With SMDD the genuine class is 25,000 StyleGAN2 renders and generator reconstructions sit in
   S, so the head must tell one generator's output from another's (objection 4 of the round-3 vetting).
3. For a processed image the score reduces to M against S. That contrast is weak where it is clean: 0.61 to
   0.66 on GAN morphs, unreadable or reversed on diffusion morphs. At a threshold that flags 5% of S images,
   most two-person morphs will be missed. EER hides this; the number must be printed.
4. No table number rises.

**Cheapest confound that gives the same result, and its control.** A gain of 0.03 AUC on R4 against R3 can
come from source disparity, not from a second identity: the two-person warp is larger, so softening and the
ghosted surround are stronger (background alone 0.54 to 0.59; thumbnail 0.62 to 0.65). On FRLL the second
photo of the same person is the smiling one, which brings the capture-detail difference (1.43 times file
size) into R3. Control: no FRLL pairs; R4 against R3 inside the overlapping band of landmark shape distance;
the best simple-statistic floor for this contrast printed beside it; a face-blanked read-out (constant
colour, allowed).

**Sharper first test.** One extra arm in the three-arm labelling comparison that the round-3 vetting already
defined, landmark family only, FRGC and colorFERET hosts, no generator rungs, the same images in every arm:
(i) binary, negatives G only; (ii) binary, negatives G and S (the MorDeephy habit); (iii) three-way softmax,
scored by the log-odds of P(M). Linear heads on cached features are a plumbing check. The decision is one
LoRA fit per arm, same seed and schedule. Read-outs: AUC of R4 against R3 inside the matched shape-distance
band, as excess over the floor; share of R4 caught at the threshold that flags 5% of R3; shift of the score
from R0 to R1 and to R2w; EER on the FRLL landmark cells. **Kill the three-way arm** if it does not beat arm
(ii) by 0.03 AUC inside the band with a person-bootstrap interval that excludes zero. Arm (ii) against arm
(iii) is the only comparison that isolates the head. Keep P(S) as a reporting device for the single-subject
table only if the author accepts the three categories.

Scores: impact 3, feasibility by 14 Nov 6, novelty 2.

### Proposal 3. Code-factorial rungs and footprint-matched pairs. Verdict: REVISE (merge with round-3 Idea 2)

**Closest prior work in morph detection.** For the training rule: MorDeephy and its four follow-ups
(same-person morphs as genuine, landmark tools); Kashiani et al. with the opposite label. For the rungs:
attack papers only (DiM variants A to D; Fast-DiM Table III, which is in effect a fresh-noise render from
the averaged semantic code; Greedy-DiM, recalled). In our own files: Idea 2 of
`ideas/round3/mechanism_ideas.md` (noise-only mix, semantic-only mix, transplant), vetted to "revise" with
an added fresh-noise cell. A detection-side factorial was not found in the literature.

**What is new against the round-3 design, and worth keeping.** The second photo A′ of the same person. In
the round-3 cells a code is either mixed or not, so "mixed at all" and "with whom" move together. Here both
codes are mixed in every corner and only the partner changes. That holds the mixing footprint and the
regained-detail effect constant.

**What must change.**

1. The prediction. "The field predicts the stochastic code" is not supported (section 3, point 1). Register
   the test two-sided, with no expected factor.
2. The read-out. The "second-identity projection" is the unstable instrument of the record (0.793 "not
   consistent"; 0.249 and 0.438 under the two heads). A sign test of that projection on 16 persons decides
   little. Two factors are tested, so the chance that at least one reaches 13 of 16 under no effect is about
   0.021, not 0.011. The heads must come from persons other than the 16.
3. The kill rule is one-sided ("stays below 0.65"). The record has 0.249: a strong signal in the wrong
   direction. A probe trained directly on x3 against x2 would turn it into about 0.75 and pass. That would
   be a pair-type cue, not a second person.
4. The training rule has no route to the published cell. Under the mix-trained head, diffusion morph against
   camera photo equals PNG size (0.876 against 0.877). "The MorDIFF cell is then scored by mixing evidence"
   is not supported. No training use before 14 Nov.
5. The inverted codes of the existing diffusion material are not on disk (round-3 vetting). The renders need
   the Athena generation (DG1) to save both codes.

**Cheapest confound that gives the same result, and its control.** Source disparity (capture detail and
layout). A pair of two persons is farther apart than a pair of two photos of one person: 1.744 against 0.773
in the semantic code, and more in hair, collar, pose and backdrop. An effect of "B in the semantic code" may
be "codes farther apart". An effect of "B in the noise map" may be the ghost of another head outline
(Fast-DiM: "a silhouette of the head is clearly visible in the encoded" noise map), which is an
alignment-and-surround cue. Controls: the semantic-code distance and the landmark shape distance of each
pair as covariates, and the contrast inside the overlapping distance band; a face-interior and a
surround-only read-out by constant-colour blanking; Laplacian variance and PNG size of every cell. Second
confound, softness with reversed sign: handled by the A′ design and by equal steps, but print the floor.

**Sharper first test.** Step 1, CPU, existing features, no render (129 FERET and FRGC blocks of the
paired-difference experiment PD1; A43): (a) rank correlation of the x3-against-x2 score with the
semantic-code distance of the pair and with FR dissimilarity, inside each class; (b) AUC of x3 against x2
inside the overlapping band of semantic-code distance, both directions reported; (c) the simple-statistic
floor for this contrast at 20 steps. **Stop here** if the within-class correlation with pair distance is 0.5
or more in absolute value (the score reads distance), or if fewer than 30 pairs per class fall in the common
band (the contrast cannot be interpreted). Step 2, only if step 1 passes and Athena saves the codes: six
cells per host at 20 steps for at least 200 FERET and FRGC hosts (the four corners with A′ or B in each
code, a fresh-noise cell, the reconstruction), scored by a probe trained on morph against reconstruction
with person-disjoint folds. The 16 persons of AD1b are a plumbing run, not a decision. **Pass:** one factor
has a paired effect whose person-bootstrap 95% interval excludes zero after the two covariates and the
Laplacian variance are included, and the effect is present in the face-interior read-out. **Kill:** both
intervals include zero; then every detector's diffusion cell is described as "mixing is read, a second
person is not". FR check before any off-diagonal cell is called anything. The author's yes for new argument
pairs is needed, as the analysis says. Step-crossing (20 and 100 steps on both sides of the label) is kept
as a reporting rule at no cost.

Scores: impact 4, feasibility by 14 Nov 5, novelty 4.

### Proposal 4. Alignment by selection, with a certificate. Verdict: KEEP (with three changes)

**Closest prior work in morph detection.** Equalising by processing both classes: Seibold et al. 2018,
Ferrara et al., Zhang et al. 2024, the print-and-scan sets. Showing that a detector learnt the set:
Spreeuwers et al. 2018. Selection or weighting of existing images until a cue-only classifier is at chance,
printed as a property of the training set: not found in morph detection. Outside it the device is standard
(Grommelt et al.; REPAIR; AFLite). In our own files: the three-part certificate of the canonical-view idea
(`ideas/round3/nuisance_ideas.md`), the round-1 reweighting idea, and the morph-free reference networks.
The novelty is modest: a reporting device plus a training-set property.

**Why keep.** It is the only proposal that attaches a checkable statement to the network the paper will
report. It needs no generator, no GPU for the first test, and no ruling on classes. It fits the claim form
the analysis recommends: a list of named cues, each with a number.

**Three changes.**

1. *Match or subsample; do not weight.* Sample weights lose their effect as a deep network trains on (Byrd
   and Lipton); subsampling is the reliable form (Sagawa et al.; Idrissi et al.). A weighted logistic head
   does not predict what a LoRA fit does with weights. Use coarse exact matching or matched subsampling and
   report the share of data kept.
2. *Measure cues on what the network sees.* File size and chroma subsampling are not in the pixels. Compute
   the pixel cues after the detector's own crop and resize (the softness floor is 0.76 at 512 px and 0.87 at
   224 px). Add what the vector lacks: partner identity (the five SMDD partners), source pool, morphing
   engine.
3. *Say what the certificate cannot do.* In all 17 benchmark cells a file attribute separates the classes
   perfectly, so the cue-only AUC "on every evaluation cell" will read 1.0. That line is the audit, not a
   property of our method. For the evaluation side the evidence stays the ladder: the score must not move
   from R0 to R1. And softness is caused by blending (0.52 times); balancing on it removes part of the true
   evidence on purpose. The cost must be printed, not hoped away.

**Cheapest confound that gives the same result, and its control.** "The matched head halves the R0-to-R1
flag-rate change" can be produced by less data alone: a weaker head flags less of everything at a fixed
threshold. And a cue outside the vector can take over (the five fixed partners; the generator and pipeline
step, readable at 0.91 to 0.98 by features and invisible to eight spectrum bands). Controls: an arm with a
random subsample of the same size; thresholds re-set per arm at the same false-alarm rate on unprocessed
genuine photos, with the miss rate on landmark cells printed; a strong reader as second certificate (a
probe on frozen patch features must not predict the label from the matched negatives and positives better
than the ladder contrast R4 against R3 allows; and the morph-free network refitted on the matched pool must
be at chance on every cell).

**Sharper first test (CPU, hours).** Pool: the SMDD rebuild arms plus the landmark ladder, FRLL excluded.
Cue vector at the detector's input size: Laplacian variance at three kernel sizes, eight radial bands, border
fraction, history flag, engine, pool, partner identity. Fit the cue-only classifier with person-disjoint
folds. Build the matched subsample. Three logistic heads on cached CLIP features: full pool; matched
subsample; random subsample of equal size. Read-outs: cue-only AUC before and after; share of data kept;
flag-rate change from R0 to R1 at each head's own 5% threshold; AUC of R4 against R3 and EER of R4 against
R0. **Kill:** the cue-only AUC cannot be brought to 0.60 or below while keeping 30% of the pool; or the
matched head does not beat the random subsample of equal size by at least half of the full-pool flag-rate
change; or R4 against R0 on landmark cells worsens by more than 2 points EER against the random subsample.
If it passes, the same matched pool goes into one LoRA fit beside the round-2 arm, with paired batches and
identical crops.

Scores: impact 5, feasibility by 14 Nov 8, novelty 3.

---

## 6. Remarks on the rest of the analysis

- Part 5 ("what does not transfer") is sound. One addition: the two-stage design of Mandelli et al. is two
  networks, so only its class scheme transfers, not its pipeline.
- "Do not print the 0.945 to 1.000 probe result without the same-person negative": agreed, and the 2026
  finding that frozen-feature probes are blind to autoencoder reconstruction (section 4.1) supports it from
  the other side.
- "Write the claim as a list of named cues": agreed. Spreeuwers et al. 2018 and Seibold et al. 2018 belong
  in the related-work paragraph that goes with that list.
- The flip-rate figure is a reasonable summary number. It needs the same class ruling as the rest (which
  variants are nuisance-only).

---

## 7. Sources opened in this check that are not in the analysis

1. Spreeuwers, Schils, Veldhuis. Towards Robust Evaluation of Face Morphing Detection. EUSIPCO 2018. https://new.eurasip.org/Proceedings/Eusipco/Eusipco2018/papers/1570439319.pdf [P]
2. Seibold, Samek, Hilsmann, Eisert. Accurate and Robust Neural Networks for Security Related Applications Exampled by Face Morphing Attacks. arXiv 1806.04265, 2018. https://arxiv.org/abs/1806.04265 [P]
3. Ferrara, Franco, Maltoni. Face morphing detection in the presence of printing/scanning and heterogeneous image sources. arXiv 1901.08811; IET Biometrics 10(3):290-303, 2021 (journal data from a search listing). https://arxiv.org/abs/1901.08811 [P]
4. Damer et al. ReGenMorph: Visibly Realistic GAN Generated Face Morphing Attacks by Attack Re-generation. ISVC 2021. https://arxiv.org/abs/2108.09130 [P]
5. Medvedev, Shadmand, Gonçalves. MorDeephy: Face Morphing Detection Via Fused Classification. arXiv 2208.03110, 2022 (venue ICPRAM 2023 per our record; not on the page). https://arxiv.org/abs/2208.03110 [P]
6. Kashiani, Sami, Soleymani, Nasrabadi. Towards Generalizable Morph Attack Detection with Consistency Regularization. IJCB 2023 (venue from a search listing). https://arxiv.org/abs/2308.10392 [P]
7. Di Domenico, Borghi, Franco, Maltoni. Dealing with Subject Similarity in Differential Morphing Attack Detection. arXiv 2404.07667, 2024. https://arxiv.org/abs/2404.07667 [P]
8. Neddo, Blasingame, Liu. The Impact of Print-Scanning in Heterogeneous Morph Evaluation Scenarios. IJCB 2024. https://arxiv.org/abs/2404.06559 [A]
9. Medvedev, Gonçalves. MorphGuard. arXiv 2505.10497, 2025. https://arxiv.org/abs/2505.10497 [A] (abstract does not mention same-person morphs)
10. Raja et al. Morphing Attack Detection: Database, Evaluation Platform and Benchmarking. arXiv 2006.06458; IEEE TIFS (accepted, per arXiv comment). https://arxiv.org/abs/2006.06458 [A] (abstract: morphs printed and scanned; whether genuine images got the same treatment is not in the abstract)
11. Chai, Bau, Lim, Isola. What makes fake images detectable? Understanding properties that generalize. arXiv 2008.10588, 2020. https://arxiv.org/abs/2008.10588 [P]
12. Liu, Liu, Wang, Soumik. Exploiting the Final Component of Generator Architectures for AI-Generated Image Detection. arXiv 2601.20461, 2026. https://arxiv.org/abs/2601.20461 [H]
13. Heo, Woo. FakeChain: Exposing Shallow Cues in Multi-Step Deepfake Detection. arXiv 2509.16602, 2025. https://arxiv.org/abs/2509.16602 [A]
14. Zhou, He, Lin, Fan, Ding, Li. Simplicity Prevails: The Emergence of Generalizable AIGI Detection in Visual Foundation Models. arXiv 2602.01738, 2026. https://arxiv.org/abs/2602.01738 [A]
15. Liu et al. Beyond Artifacts: Real-Centric Envelope Modeling for Reliable AI-Generated Image Detection. arXiv 2512.20937, 2025. https://arxiv.org/abs/2512.20937 [A]
16. Li, Yan, Wang, Zeng, Fu. How Noise Benefits AI-generated Image Detection. arXiv 2511.16136, 2025. https://arxiv.org/abs/2511.16136 [A]
17. Yan et al. Orthogonal Subspace Decomposition for Generalizable AI-Generated Image Detection. arXiv 2411.15633. https://arxiv.org/abs/2411.15633 [A]
18. Huang et al. SIDA: Social Media Image Deepfake Detection, Localization and Explanation with Large Multimodal Model. arXiv 2412.04292. https://arxiv.org/abs/2412.04292 [A]
19. Sun et al. DiffusionFake: Enhancing Generalization in Deepfake Detection via Guided Stable Diffusion. NeurIPS 2024. https://arxiv.org/abs/2410.04372 [A]
20. Byrd, Lipton. What is the Effect of Importance Weighting in Deep Learning? arXiv 1812.03372. https://arxiv.org/abs/1812.03372 [A]
21. Sagawa, Raghunathan, Koh, Liang. An Investigation of Why Overparameterization Exacerbates Spurious Correlations. arXiv 2005.04345. https://arxiv.org/abs/2005.04345 [A]
22. Idrissi, Arjovsky, Pezeshki, Lopez-Paz. Simple data balancing achieves competitive worst-group-accuracy. CLeaR 2022. https://arxiv.org/abs/2110.14503 [A]
23. Ozgur, Boutros, Damer. Tomatoes, Potatoes, and Onions: Questioning the Need for Faces in Face Presentation Attack Detection. ACM Multimedia 2026 Workshops. https://arxiv.org/abs/2608.21455 [A] (already in our record; re-opened)

### Recalled, not verified

- Ferrara, Franco, Maltoni, "Decoupling texture blending and shape warping in face morphing" (BIOSIG 2019): if it says what I recall, it is prior art for a warp-only rung. Not opened.
- Venues I know but did not see on a page: Chai et al. (ECCV 2020); "Organic or Diffused" (ACM CCS 2024); "Simplicity Prevails" (ACM Multimedia 2026, from a search summary only).
- Works on hidden subclasses and auxiliary subclass labels (Sohoni et al., NeurIPS 2020; Müller, Kornblith, Hinton, subclass distillation): relevant to Proposal 2, not opened.
- Frank et al. (ICML 2020) and Dong et al. (CVPR 2022) on spectral cues of generated images; Corvi et al. 2025 on forensic-oriented augmentation; Co-Spy; NPR; Greedy-DiM: not opened.
- R2BD (arXiv 2601.08867): title seen in a search summary only.
- Whether the SOTAMD set gives genuine images the same print-and-scan treatment as morphs: our class-definition check says so; I read only the abstract, which does not say it.

### Searches

Eight ran: reconstructed genuine images through a generator in morph detection (two wordings); Spreeuwers
2018; Ferrara print-and-scan simulation; three-class single-image morph detection; Kashiani self-morphing;
morph detection dataset bias or shortcut audit 2026; generated-image detection 2026 with aligned training
and reconstructed real images. Four were refused for budget: FakeChain; three-class or laundered class in
generated-image detection; follow-ups to image laundering; same-person controls for diffusion morphs. The
first of these was replaced by a direct page read. The other three stay open.
