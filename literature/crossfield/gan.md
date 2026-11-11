# Detection of GAN-generated images: what it offers single-image morph detection

11 Nov 2026. Cross-field analysis for ideation round 3. Field: detection of fully generated images, faces
above all (StyleGAN family, ProGAN and others), 2019 to 2026. Written by the analyst agent for this field.
Research and writing only: no experiment was run, no sealed file was opened.

**How sources were handled.** Every work in the verified list (section 7) was found during this task by web
search or page fetch. "Read in full text" means the arXiv HTML page was read beyond the abstract. Numbers are
quoted with the table or section the page gave. They were read through a page-reading tool, so re-check each
one against the PDF before it is printed in the paper. Where the fetched page did not show the venue, the
venue is given from memory and marked "(venue from memory)". Works I recall but did not find are listed
separately and are not used as evidence.

**Abbreviations.** GAN = generative adversarial network. MAD = morphing attack detection; S-MAD = from a single
image. AUC = area under the ROC curve (0.5 = chance). EER = equal error rate. AP = average precision. bAcc =
balanced accuracy. W = the intermediate latent space of StyleGAN (one 512-number code per image); W+ = the
extended space with one such code per generator layer (16 or 18 layers). w̄ = the mean code. ψ (psi) = the
truncation factor. CLIP, DINOv2, DINOv3 = large pretrained image encoders. LoRA = low-rank adaptation (a cheap
way to fine-tune). JPEG, PNG, WEBP = file formats. FID = Fréchet inception distance (lower = generated set
closer to real set). LPIPS = a learned perceptual image distance. SD = standard deviation.

---

## 0. The answer in brief

1. **What leads this field today is data design, not architecture.** The best generalisation numbers of 2024 to
   2026 come from training sets in which each fake is a reconstruction of a real image, so that the two classes
   share content, size, format and compression (Aligned Datasets, B-Free, Dual Data Alignment). The backbone is
   an ordinary pretrained encoder.
2. **The field found our shortcuts before we did, in its own data.** JPEG against PNG, image size, resize
   direction ("downsampled = real, upsampled = fake"), WEBP, and a missing high-frequency band have each been
   shown to carry published benchmark numbers. One detector's verdict on a real photo moved from 80% to 100%
   "real" by compressing it. This is the same failure as our storage-history result.
3. **Nothing in this field tells a mixed latent code from a single one, except how far the code is from the
   mean.** Spectral traces, fingerprints, and "can the generator reproduce it" tests are the same for a morph and
   a one-person render. The midpoint of two codes is, to second order, a truncated code (ψ about 0.71 for
   unrelated persons). For a Gaussian code distribution the two are the same distribution, so no detector can
   separate them. Our 0.89 to 0.94 is a truncation reading. Our 0.58 to 0.63 against spread-matched renders is
   what the theory predicts, plus a small remainder with four testable causes (section 4).
4. **The published GAN morph cells measure generated-image detection.** A ResNet-50 trained only on ProGAN
   images of bedrooms, cars and cats, which never saw a morph, reaches 0.00%, 0.56% and 0.00% EER on three GAN
   morph sets (Colbois and Marcel, BIOSIG 2022, Table 2). Its authors conclude that detecting GAN morphs "is
   strongly equivalent" to detecting GAN images.
5. **Five proposals follow** (section 5): a radius-crossed generator ladder that removes averageness by design
   and measures what is left; truncation-dose training with no morph and no partner; a declared "re-synthesised"
   output built by the field's aligned-pair recipe; morph-free mechanism readers from this field as independent
   instruments; and an inversion-encoder bottleneck that reads identity typicality where storage history cannot
   reach.

---

## 1. Map of the field, grouped by the idea behind each solution

### 1.1 Table

| Family | The idea | Main works (all verified, see section 7) | Standing in 2026 |
|---|---|---|---|
| A. Learned classifier with a generalisation recipe | Train a standard network on one generator. Add blur and JPEG augmentation. Use diverse content. | Wang et al. 2020; Gragnaniello et al. 2021; Hulzebosch et al. 2020 | The baseline everyone compares against. Works across GANs, fails on diffusion models (Ojha et al. 2023, Table 1: 3.05% of latent-diffusion fakes detected). |
| B. Spectral and up-sampling traces | Up-sampling layers leave periodic patterns and a wrong high-frequency decay. Read the spectrum, or local pixel relations. | Zhang et al. 2019; Frank et al. 2020; Durall et al. 2020; Tan et al. 2024 (NPR); Corvi et al. 2023 | Strong on paper, fragile. The high-frequency gap is removed by changing the last up-sampling layer (Chandrasegaran et al. 2021) or by a cheap clean-up (Dong et al. 2022). StyleGAN3 was built to remove aliasing (Karras et al. 2021). |
| C. Fingerprints and attribution | Each generator leaves a stable noise-like pattern. Use it to say which model, or which architecture, made the image. | Marra et al. 2018; Yu et al. 2019; Yang et al. 2022 (DNA-Det); Laszkiewicz et al. 2024 | Used for forensics and intellectual-property questions. Fingerprints change with the training seed (Yu et al.). Architecture traces are global, weight traces are position-bound (Yang et al.). |
| D. Patch and local texture | Small receptive fields. Local texture is more stereotyped than global layout. | Chai et al. 2020; Liu et al. 2020 (Gram-Net); Li et al. 2025 (SAFE) | Generalises across resolution and seeds. For whole generated faces the decisive patches are hair and background (Chai et al., Section 4.2). |
| E. Gradient and residual representations | Remove the image content first, then classify what is left (gradients of a fixed network, a denoiser's residual). | Tan et al. 2023 (LGrad); Liu et al. 2022 (LNP) | Good cross-GAN numbers. Sensitive to any processing, because processing is what the residual shows. |
| F. Frozen foundation features | Do not train the encoder. Nearest neighbour or a linear layer on CLIP features. | Ojha et al. 2023 (UnivFD); Cozzolino et al. 2024 (CLIP, few-shot); Koutlis and Papadopoulos 2024 (RINE); Yan et al. 2025 (Effort) | A strong baseline since 2023. Later work shows it still inherits data bias (section 2) and that end-to-end training on aligned data is better (B-Free, Table 3: linear probe 68.5% bAcc, end-to-end 95.2%). |
| G. One-class, real-only, training-free | Model real images only. Flag what the model finds surprising or unstable. | Cozzolino et al. 2024 (ZED); He et al. 2024 (RIGID); Liu et al. 2022 (LNP); Ricker et al. 2024 (AEROBLADE) | No generator-specific bias by construction. ZED: 90.0% average AUC on 30 generators with one statistic. Authors warn that strong compression or resizing may make it unreliable. |
| H. Inversion and reconstruction tests | Ask whether a given generator can reproduce the image. | Karras et al. 2020, Section 5; Albright and McCloskey 2019; Wang et al. 2023 (DIRE); Ricker et al. 2024; Cazenavette et al. 2024; Pasquini et al. 2023 | Answers "was it made by this generator", well for StyleGAN2 in W, well for latent diffusion. Needs the generator. |
| I. Aligned, bias-free training data | Make each fake from a real image so the classes differ only in the generator trace. Then also align compression. | Rajan et al. 2025; Guillaro et al. 2025 (B-Free); Chen et al. 2025 (DDA); Chen et al. 2024 (DRCT); Rajan and Lee 2025 (Stay-Positive) | **Leads the generalisation benchmarks.** B-Free: 96.3% average bAcc over 27 generators, 20.7 points above the second best (Table 5). DDA: 90.7% over 11 benchmarks, 15.7 points above the second best (Table 2). |
| J. Scale of generator diversity | Thousands of generators in training. | Park and Owens 2025; Wang et al. 2020 (diversity of classes matters more than image count) | Works, at a cost we cannot pay in three days. |

### 1.2 What leads, and what is deployed

- **Benchmarks.** From 2024 the leading rows are data-centric: a pretrained encoder (DINOv2 or CLIP),
  fine-tuned end to end or with LoRA, on aligned pairs. B-Free states that "careful dataset curation and proper
  training strategy can be more impactful compared to developing more complex algorithms" and shows it: the same
  RINE architecture goes from 65.0% to 83.2% bAcc when only the training data change (Table 4).
- **Out of the box.** A 2026 zero-shot study of 23 released detectors on 12 datasets (Ren et al., arXiv
  2602.07814, abstract) finds no universal winner: the best reaches 75.0% mean accuracy, the worst 37.5%.
  Training-data alignment causes 20 to 60% variance inside detector families with identical architecture.
  Recent commercial generators are detected at 18 to 30% average accuracy.
- **In the wild.** Deepfake-Eval-2024 (Chandra et al., abstract): open-source image detectors lose 45% of their
  AUC against earlier benchmarks. Commercial detectors do better but stay below forensic analysts. Which methods
  commercial products use is not documented in any source I verified.
- **Honest summary.** Released detectors are learned classifiers of families A, F and I. Their published
  numbers do not predict their behaviour on new data. The field now treats that as a data-design problem.

### 1.3 The latent-space literature we need for our own case

This is not detection work, but it decides what a detector can know about a latent morph.

- **Truncation** (Karras et al. 2019, read in full text). w′ = w̄ + ψ(w − w̄). Smaller ψ gives higher average
  quality and less variation. At ψ = 0 "all faces converge to the mean face". The same paper's default figure
  uses ψ = 0.7.
- **Truncation trades diversity for fidelity** (Kynkäänniemi et al. 2019, read in full text, Figure 5): at
  ψ = 0 precision is high and recall is zero. Moving all codes toward the mean "raises precision" (Appendix C).
- **Midpoints look real.** Of 500,000 straight paths in W whose two ends lie on the real-image manifold, only
  2.4% cross unrealistic regions. The authors call the realistic part of W "highly convex" (Kynkäänniemi et al.,
  Figure 9 and text).
- **Midpoints have the wrong radius.** For independent prior samples the midpoint has half the variance per
  coordinate (factor t² + (1−t)² = 1/2 at t = 1/2). In 100 dimensions the midpoint norms are "strong outliers"
  against the prior. For a Gaussian prior the fix is one scalar: multiply by √2 (Agustsson et al. 2019, read in
  full text). White 2016 made the same point informally and proposed spherical interpolation.
- **W is not Gaussian.** Every layer of the mapping network, the last one included, ends in a leaky ReLU with
  slope 0.2 (Karras et al. 2019; the official StyleGAN3 code, read). Marginals of W are "heavily skewed".
  Undoing the last leaky ReLU (slope 5) and whitening gives a space that is close to Gaussian but still fails
  formal normality tests (Zhu et al. 2020, read in full text: 219 of 512 principal-axis marginals pass). A
  normal distribution fitted directly to W gives FID 76.63; sampling the Gaussianised space gives 3.28 against
  2.81 for the generator itself (same paper). Wulff and Torralba 2020 report the same transformation.
- **Inverted codes are not prior samples.** Unregularised W+ inversion "can find embeddings in low-density
  portions" of latent space (Zhu et al. 2020). Codes far from W are less realistic and less editable (Tov et al.
  2021, e4e). With a Gaussian prior as regulariser, midpoints between inverted faces were preferred by users in
  89.9% of judgments (Wulff and Torralba 2020, user study).
- **Style mixing is in-distribution by training.** StyleGAN is trained with two codes switched at a random layer
  for 90% of images (Karras et al. 2019, Table 2). A crossover of two codes is something the discriminator was
  trained to accept.
- **Projection as attribution.** A StyleGAN2 output can be projected back into W "so well that" it "can be
  almost unambiguously attributed to the generating network"; real images cannot. W+ "enables projecting
  arbitrary images that should have no latent representation" (Karras et al. 2020, Section 5).

---

## 2. What the field learned about dataset shortcuts, and how it removed them

| Finding | Evidence as reported | Remedy used | Our analogue |
|---|---|---|---|
| Format is a label. Real images are JPEG, fakes are PNG. | GenImage: most real images at JPEG quality 96, all fakes uncompressed. A Midjourney-trained ResNet-50 calls uncompressed real FFHQ photos real in 80.45% of cases; after JPEG at quality 95, 90, 80, 60 this becomes 94.84, 98.93, 99.95, 100% (Grommelt et al. 2024, Table 2). | Train only on quality-96 images in both classes. Result: cross-generator accuracy +11.06 points for ResNet-50 and +11.74 for Swin-T (Table 4). | In all 17 of our benchmark cells a file attribute separates the classes perfectly. |
| Size is a label. Each generator has one output size. | A BigGAN (128 px) detector misclassifies real images with a side of 100 to 150 px (Grommelt et al., Figure 3). | Restrict real images to the generators' size window. | The SelfMAD release flags 97% of photos stored small. |
| Resize direction is a label. | "Corvi associates downsampling with real images and upsampling with fake images" (Rajan et al. 2025, Figure 2). A frozen-CLIP detector's accuracy on real images rises from 54.16 to 83.58% when real images are downsampled, while accuracy on fakes falls from 69.56 to 29.83% (Table 5). | Make each fake by passing a real image through the generator's autoencoder only, at the real image's own size. The aligned detector stays flat across the resize range. Also 10 times cheaper to build. | Our 50% shrink-and-enlarge result (0% to 45% flagged). The remedy is our pipeline-matched, history-crossed rebuild. |
| Post-processing of one class is learned as that class. | Real images in one training set were WEBP-compressed; the detector learned "WEBP = real" (Rajan and Lee 2025, Section 3.1). | Retrain only the last layer with non-negative weights, so that no feature can vote for "real" (Stay-Positive). | Storage history of the morph class. But see the limit in section 6. |
| Aligning pixels is not enough: a frequency band still differs. | A reconstruction restores high-frequency detail that JPEG had removed from the real image. A frequency-based detector flags about 93% of such reconstructions; masking a few high-frequency coefficients makes detection collapse (Chen et al. 2025, Figures 4 and 5). | Apply the real image's own JPEG quality to its reconstruction (Dual Data Alignment). 90.7% bAcc over 11 benchmarks, worst case 81.4%. | Our softness floor: a morph has 0.52 times the Laplacian variance of its own halves. The band points the other way, the mechanism is the same. |
| Content and source are labels. | The same generated images are called real or fake by three CLIP-based detectors depending on which real photo collection they are paired with (Guillaro et al. 2025, Figure 2). | Self-conditioned reconstruction plus inpainted variants; content alignment alone lifts bAcc from 61.9 to about 81 (Table 2). | Half-smiling genuine class in 12 of 17 cells; five partners in SMDD. |
| Preprocessing in the training pipeline creates bias. | Small mismatches in interpolation, initial size or file format between classes give near-perfect AP that is only a formatting difference (Chai et al. 2020, Table 5). Resizing in training weakens the traces (Li et al. 2025). | Pass real images through the generator's own data transform; save both classes losslessly; resize both the same way (Chai et al.). Crop instead of resize (Li et al.; Guillaro et al.). | Our aligner leaves a black border around smaller morph files. |
| A fixed threshold is the hard part. | "Accuracy results are much less encouraging, since a fixed threshold is used" (Gragnaniello et al. 2021). A 2-times downsampling is "catastrophic". Accuracy on scraped StyleGAN faces falls from 83.6% to 74.9% after resizing (Wang et al. 2020). | Report detection at a fixed false-alarm rate; only ZED claims one global threshold across real-image sets. | Our fixed-threshold re-read (experiment EV1). |
| Evaluation sets need matched real images. | FakeInversion builds its test set with reverse image search so that real and fake share style and theme (Cazenavette et al. 2024, abstract). DDA-COCO pairs each real image with compression-aligned reconstructions from six autoencoders (Chen et al. 2025). | Matched real-fake pairs in the test set, not only in training. | Our ladder. |
| A feature extractor pretrained to recognise image processing "detects" fakes. | DNA-Det is pretrained to classify 170 kinds of compression, blur, resampling and noise applied to natural images (Yang et al. 2022, read in full text). | Not a remedy; a warning. | These same features give 0.87 / 0.82 / 0.48% one-class EER on landmark, GAN and diffusion morphs of FRGC (Colbois and Marcel 2024, Table 7). A processing reader separates a morph benchmark. |

**The rule the field converged on.** Build each positive from a negative by the smallest possible step, so the
only difference is the thing to be detected. Then check, band by band and format by format, that nothing else
differs. Then test on pairs built the same way from other sources. This is the logic of our ladder. The field's
experience says the ladder should also be the training set, not only the instrument.

**A caution from the same papers.** Each fix removed one bias and exposed the next (format, then size, then
resize direction, then the frequency band). None of these papers claims its training set is free of all cues.

---

## 3. Has each technique family been used in morph attack detection?

| Family | Used in MAD? | Reference, or the searches that found nothing |
|---|---|---|
| A. Learned classifier with augmentation | Yes, it is the standard. | MIPGAN paper, Tables XII and XIII (Zhang et al. 2021); SMDD (Damer et al. 2022); MADation (Caldeira et al. 2025). |
| A, zero-shot: a generated-image detector applied to morphs with no morph training | **Yes, for GAN morphs.** | Colbois and Marcel, BIOSIG 2022: the released ProGAN-trained ResNet-50 of Wang et al. gives AUC 1.00 and EER 0.00 / 0.56 / 0.00% on FRLL-StyleGAN2, FRGC-StyleGAN2 and FRGC-MIPGAN (Table 2). Bona fide images are camera photos; there is no one-person render control. Not found for landmark morphs or for up-sampling readers (search: "synthetic image detector zero-shot applied to face morphing attack detection landmark morphs NPR UnivFD"). |
| B. Spectral features | Yes. | Fourier radial bands with a linear classifier: 16 to 17% EER within a StyleGAN2 morph set, 53.25% across sets (Colbois and Marcel 2022, Tables 1 and 2). FD-MAD (Paulo et al., arXiv 2601.20656) and SRL-MAD (arXiv 2603.15050) use Fourier residuals. An ICME 2018 paper uses the Fourier spectrum of sensor pattern noise (seen in search results only). |
| C. Fingerprints, sensor noise, attribution | Yes. | PRNU (camera sensor noise) analysis: Debiasi et al., IWBF 2018 and BTAS 2018. Morph-tool "fingerprinting" as multi-class attribution over eight morphing algorithms: Zhang, Jia, Lyu and Li, arXiv 2210.15510. |
| D. Patch and pixel-wise supervision | Yes. | PW-MAD (Damer et al., ISVC 2021). |
| E. Residual representations | Yes. | Denoising residual: Venkatesh et al., WACV 2020. Learned residuals: Raja et al., Image and Vision Computing 2022. Laplacian patch statistics gating a frozen transformer: R-FLoRA (arXiv 2604.17321, seen in search results only). |
| F. Frozen foundation features | Yes. | Colbois and Marcel, IJCB 2024 (DINOv2, CLIP, AIM, DNADet with a linear SVM or a one-class Gaussian mixture); MADation; Zhang et al., CVPRW 2024 (ViT-L features and SVM). |
| G. One-class, real-only | Yes. | Damer et al., BTAS 2019; SPL-MAD (Fang et al., IJCB 2022); MAD-DDPM (Ivanovska and Štruc, IWBF 2023). |
| H. Reconstruction error | Yes, as one-class reconstruction. | SPL-MAD (autoencoder); MAD-DDPM (diffusion). Both report that morphs reconstruct more easily than genuine images. GAN inversion is used for making morphs and for differential demorphing (SFDemorpher, arXiv 2603.28322), **not found** as a single-image detector that reads the inverted code (searches: "morphing attack detection GAN inversion latent code encoder StyleGAN detect morph single image"; "single image morphing attack detection StyleGAN encoder latent code Mahalanobis typicality inversion pSp e4e"). |
| I. Aligned negatives | Partly. | Zhang et al., CVPRW 2024 (arXiv 2501.09817): for GAN morph sets the genuine images are GAN reconstructions, "to learn morphing artifacts rather than general GAN artifacts"; print-scan and compression applied to both classes. No radius-matched or history-crossed design found. |
| Latent averageness, truncation | **Not found.** | Searches: "morphing attack detection StyleGAN latent space truncation averageness one-identity render control"; "face morphing attack truncation StyleGAN mean face pseudo-morph training"; "detect interpolated latent code GAN truncation classifier". No MAD paper discusses the radius of the mixed code, a truncated control, or truncation as a pseudo-morph. |
| Higher-order statistics of mixing | **Not found.** | Search: "morphing attack detection kurtosis non-Gaussianity higher-order statistics blend superposition". Nearest: Laplacian mean, variance and energy (R-FLoRA). |
| Norm-preserving morph generation (the attacker's side) | Yes. | MLSD-GAN (Reddy et al., arXiv 2404.12679, abstract) makes morphs by spherical interpolation of StyleGAN latents. MorCode and one pSp-based pipeline also use spherical interpolation (seen in search results only). |

Two older results fit the same picture. Venkatesh et al. (IWBF 2020, Table II) detect StyleGAN morphs against
camera photos at 0 to 0.68% EER with hand-made texture features and name "residual noise from the GAN" as the
reason. Sarkar et al. (ICASSP 2022) built the FRLL StyleGAN2 morphs in W, not W+, and report that they fool
FaceNet in only 5.9% (as references) and 11.0% (as probes) of cases, because "StyleGAN2 interpolation produces a
new identity rather than a blend".

---

## 4. Mixed code or single code: what this literature says about our numbers

Our finding (frozen-feature probe, experiment FZ1, `experiments/FZ1/result.md`): a probe separates a StyleGAN3
morph from a one-identity render at 0.89 to 0.94, but from a spread-matched render only at 0.58 to 0.63.

### 4.1 The second-order picture: a midpoint is a truncated code

Write a code as w = w̄ + r. The morph code is the midpoint m = w̄ + (r_a + r_b)/2. If r_a and r_b have the same
length ρ and cosine c, then |m − w̄| = ρ·sqrt((1 + c)/2). For unrelated codes in high dimension c is near 0, so
the factor is 0.71. This is our own formula. Agustsson et al. give the same factor for prior samples (variance
1/2 at the midpoint) and show that the midpoints sit on a different shell from every prior sample.

Truncation moves a single code to w̄ + ψ·r. So a midpoint has the radius of a truncation with ψ about 0.71
(0.87 for look-alikes). And truncation is visible: quality up, variation down (Karras et al. 2019); precision
up, recall down (Kynkäänniemi et al. 2019); sharper mean image and lower per-pixel standard deviation (Wulff and
Torralba 2020). Our own record agrees: truncated renders differ from plain renders in simple image properties
at AUC 0.96 (StyleGAN3 render controls, experiment A37).

**Reading of 0.89 to 0.94.** The probe reads the truncation level. It is the same reading a probe would give
for one person rendered at ψ of about 0.7 to 0.9. No second identity is needed to produce it.

### 4.2 Why the spread-matched contrast should be at chance

If codes were Gaussian around w̄ with covariance Σ, then midpoints of independent codes follow N(w̄, Σ/2), and
single codes truncated with ψ = 1/√2 follow N(w̄, Σ/2) as well. These are the same distribution. A render is a
function of the code and of noise that does not depend on how the code was made. So the two sets of images have
the same distribution, and every detector has AUC 0.5 between them, at any sample size. Agustsson et al. state
the mirror image of this: multiplying a Gaussian midpoint by √2 gives back the prior exactly.

A truncated one-person code is also, literally, a morph of that person with the mean face, with weight 1 − ψ on
the mean face. So the spread-matched render is not a neutral control. It is a morph whose partner is nobody.

**Reading of 0.58 to 0.63.** The Gaussian picture predicts 0.50. The result is close to it. This is the
expected outcome of a correct control, not a lack of power. The remainder of 0.08 to 0.13 has four candidate
causes. Each can be tested on what is on disk.

| Candidate cause | What the literature says | Test on existing material |
|---|---|---|
| 1. The spread match fixes one number; the morph's shrink is not uniform. Two contributor codes can be correlated in some layers (shared photo style of the source set) and not in others (identity). One scalar cannot copy that profile. | Layers carry different content: coarse = pose and face shape, middle = facial features, fine = colour and microstructure (Karras et al. 2019, Figure 3). | From the stored W+ codes of the 423 pairs: shrink factor per layer for the morph and for its spread-matched code. If the profiles differ, a per-layer matched render is the tighter control. Zero GPU. |
| 2. W is not Gaussian. A mean of two skewed codes is less skewed and has thinner tails than one scaled code. | Skew from the last leaky ReLU; normality rejected even after undoing it (Zhu et al. 2020; Wulff and Torralba 2020). | Idea 1, step 0 below. Zero GPU. |
| 3. Inverted codes are not prior samples. Each inversion carries its own off-manifold part; averaging two cancels part of it, scaling one does not change its shape. | Zhu et al. 2020 (low-density embeddings); Tov et al. 2021 (distance from W). | Same step 0, with the per-code spread across layers as one of the statistics. |
| 4. Fold leakage. The probe's own record says a test morph's second contributor can be in the training part. | Not a literature point. | Refit with folds grouped by both contributors. Minutes. |

### 4.3 What this means for the paired-difference numbers

In the paired-difference test on GAN morphs (experiment PD1, first pass, not yet reviewed) a head trained only
on same-person mixes ranks two-person morphs above reconstructions at 0.78. The second-order picture explains
this without any identity signal. Two photos of one person differ in pose, expression and light. Their midpoint
shrinks along those directions only. A two-person midpoint shrinks along those and along identity directions.
Both are "more average than a single code", by different amounts. A head that reads averageness ranks
x1 below x2 below x3, which is the observed order (0.67, 0.65, 0.73). Prediction to check: the head's score is a
monotone function of the latent radius, and a spread-matched render scores like the morph. PD1 already records
the latent radius, so this is a re-read, not a new run.

### 4.4 Consequences

1. On latent-average morphs one image can show (i) that it is generated and (ii) how average it is. It cannot
   show that the averageness came from a second person, unless a higher-order trace exists. That is still open
   and idea 1 closes it either way.
2. Averageness can be undone by the attacker with one multiplication (Agustsson's matched operation), and
   spherical interpolation is already used in published morph tools (MLSD-GAN).
3. On the published GAN cells the genuine class is camera photos. The decisive difference is the generator. A
   detector never trained on morphs reaches 0.00 to 0.56% EER there (Colbois and Marcel 2022). So no detector
   that ignores the generator can match those rows, and a detector that matches them is not shown to detect
   morphing. Both class policies must be printed, as round 2 already decided.

---

## 5. Five ways forward that follow from this field

Each idea names its source, the adaptation, the cues it cannot use, prior use in MAD, a first test of at most
one day with a pass mark and a kill number, and the main risk. All obey the binding constraints: one network on
one image, no fusion, no gate, no new blur, resize, resampling or JPEG code. Latent arithmetic followed by an
unchanged generator run is the operation already used for the spread-matched and truncated pools.

### Idea 1. Radius-crossed generator ladder: remove averageness by design, measure what is left

**Source technique.** Aligned training sets, where the nuisance is equal in both classes (Rajan et al. 2025;
Guillaro et al. 2025; Chen et al. 2025). Distribution-matched latent operations (Agustsson et al. 2019). The
Gaussianised latent space (Zhu et al. 2020; Wulff and Torralba 2020).

**Transfer.** Our spread-matched render equalises the radius on the negative side only. The field's rule is to
cross the nuisance with the label. Add the missing corner, the midpoint pushed back to full radius:
x3r = G(w̄ + (m − w̄)/s), with s the measured shrink of that pair. Four arms result. Single code at full
radius (x1). Single code at the morph's radius (x1s, exists). Midpoint (x3, exists). Midpoint at full radius
(x3r, new, decode only). The label is "two codes were mixed". Radius carries no label information. Build the
same four arms from codes drawn from the mapping network, where the supply is unlimited and no inversion is
involved. Train the standard recipe on "mixed against single". Whatever the network learns is then a trace of
linear mixing itself, not averageness.

**Step 0, no image needed.** A render is a function of its code, so no image detector can beat the best test on
the exact code. Compute per-code summaries from the stored W+ codes: radius per layer; spread of the code across
layers; and, after undoing the leaky ReLU and whitening with statistics from 10,000 mapping-network samples,
the skewness and excess kurtosis of the coordinates. Fit a cross-validated logistic model, midpoints against
radius-matched single codes (computed arithmetically, 423 against 423), folds by pair with both contributors
held out. The same on the 64 GAN blocks for same-person against two-person midpoints.

**Why shortcut-free.** Both classes are outputs of one generator in one frame and one file path. So generator
fingerprint, storage history, border and capture detail are equal. The same persons feed both classes, so
identity pool and expression are equal. Radius is crossed, so averageness is equal. Ladder contrasts that show
it: x3 against x1s and x3r against x1 carry the claim; x1s against x1 must be separable by a radius probe
(positive control for power) and must not be separable by the mixing head.

**Used in MAD already?** None found. Zhang et al. (CVPRW 2024) use GAN-reconstructed genuine images, with no
radius control. Searches listed in section 3 (latent averageness; higher-order statistics).

**First test, at most one day.** Step 0 takes under an hour on CPU. Kill: code-level AUC at or below 0.60 with
upper bound below 0.65. Then even the exact code does not show mixing beyond radius; print that as the measured
limit and stop. If the code-level AUC is 0.75 or more, decode x3r for the 423 pairs and 4 × 2,000 prior-sample
renders (decode only), and run the FZ1 probe protocol plus one LoRA fine-tune. Positive control: radius
contrast at or above 0.90. Pass: mixed against single at or above 0.70 in both radius strata on held-out codes.
Kill: at or below 0.60 in both strata with the positive control passing.

**Risk.** A high code-level AUC is not evidence that the image shows it; only the low outcome is decisive at
step 0. Radius-restored midpoints of inverted codes may leave the generator's good region and show artefacts,
which would be read as "mixing"; the prior-sample arm guards against this. A positive result reads "two codes
were mixed", which is also true of a same-person mix. Most likely outcome: kill, which gives the paper a limit
measured with demonstrated power, and gives x3r as the evasion example.

**State of the art.** This idea does not raise a table number. It decides how generator cells are reported and
whether a generator arm belongs in the training set. It adds only same-generator images, so it cannot hurt the
landmark cells.

### Idea 2. Truncation-dose training: a pseudo-morph with no morph and no partner

**Source technique.** The truncation trick and its measured effect on samples (Karras et al. 2019; Kynkäänniemi
et al. 2019). Training on simulated traces instead of real fakes (Zhang, Karaman and Chang 2019). Real-only
training (Liu et al. 2022).

**Transfer.** A truncated render G(w̄ + ψ(w − w̄)) is one person morphed with the mean face. It has the one
property a latent-average morph has, and nothing else: no second person, no partner pool, no morphing tool.
Train a head to regress ψ on one-identity renders only. Test it on real latent morphs. If section 4 is right,
transfer is complete. The head then has a physical unit, the "mixing-equivalent truncation": 0.71 for unrelated
contributors, 0.87 for look-alikes, 1.0 for a single code. Two uses follow. As evidence: a network that never
saw a morph or a second identity matches a morph-trained probe, which shows constructively what "detecting GAN
morphs" reads. As a training arm: dose-labelled images at any scale from one photo per person, which removes
the five-partner defect of SMDD for the generator arm. Under the opposite ruling (averageness is not evidence),
the same renders enter training as genuine at several ψ, and the network is made blind to averageness.

**Why shortcut-free.** Both ends of the dose axis are renders of one generator through one file path. Storage
history, border, capture detail, generator fingerprint and partner identity cannot differ. Ladder contrasts:
the head must not separate a camera photo from its history-matched copy (shift at most 0.3 SD); it must not
separate x3 from x1s (it is declared unable to tell mixing from truncation); it must rank trunc50 above trunc70
above plain renders. Its AUC is reported as excess over the seven simple statistics, because A37 found that
truncation is visible in simple image properties at 0.96.

**Used in MAD already?** None found (searches in section 3 on truncation and pseudo-morphs). Self-blending
(SelfMAD) makes pseudo-morphs in pixel space with a blend; this one has no blend at all.

**First test, at most one day.** All images exist: the trunc50, trunc70, re-decoded and spread-matched pools
and the 423 morphs of the StyleGAN3 set. Fit the FZ1 probe on trunc70 against plain renders, folds by person.
Score the morphs and the one-identity renders. Pass: AUC at or above 0.85 (the morph-trained probe reaches
0.89 to 0.94). Kill: below 0.75; then truncation is not the whole story and section 4 needs revising. Side
check, same day: score SMDD's genuine renders against fresh renders of the same generator. SMDD keeps the 50,000
highest-quality of 250,000 renders (Damer et al. 2022); if the kept renders score as truncated, SMDD's genuine
class is shifted toward the mean face, and SMDD-trained detectors learn "average render = genuine". That would
explain why the SelfMAD release scores truncated renders as less morph-like (0.883 against trunc50 in A37).
This is a hypothesis; the paper does not state a ψ.

**Risk.** The head may read simple image properties rather than facial averageness; the floor decides. The
existing truncated pools may have been built on other base codes or layers than assumed; check the generation
record first. Behaviour on camera photos is untested; a head trained on renders only may be undefined there
(the first PD1 pass gives 0.51 for reconstruction against camera photo, which is encouraging). An attacker
restores the radius. Average-looking or beautified genuine faces would be flagged.

**State of the art.** Alone it will not reach the published generator rows, because those are won by reading
the generator. It supplies the morph evidence for generator cells under the policy "a reconstruction is
genuine", as an auxiliary regression target of the one network.

### Idea 3. A declared "re-synthesised" output, built by the field's aligned-pair recipe

This improves an item already on our table (the author question whether a re-synthesised photo is admissible).
The field supplies the recipe and the pitfalls.

**Source technique.** Fakes made by reconstructing real images (Rajan et al. 2025; Guillaro et al. 2025);
compression alignment of the pair (Chen et al. 2025); crops instead of resizing (Li et al. 2025); end-to-end
training rather than a frozen probe (Guillaro et al., Table 3).

**Transfer.** One network with three outputs: genuine, single-subject manipulation, morphing attack. The middle
class is trained on same-photo pairs: a camera photo and its own one-photo reconstruction, by the StyleGAN
inversion and by the diffusion autoencoder at each step count. Both members of a pair must share frame, size and
file path. Where a pair cannot be brought to the same frame without new resampling code, it is not used. The
morph output is trained on morphs against reconstructions and same-person mixes, as in the paired-difference
work. Error rates under both class policies are then read from one network: p(morph) alone, or 1 − p(genuine).
A one-photo reconstruction is never called a morph, so the binding rule on processed genuine images holds.

**Why shortcut-free.** The pair shares content, person, expression and, after alignment, storage history and
border. Only the generator step differs for the middle class; only the mixing step differs for the morph
class. Ladder contrasts: camera photo against its history-matched copy must not move either output (at most
0.3 SD; flag rate at the 5% threshold at most 10%); reconstruction against camera photo must move only the
middle output; morph against reconstruction must move only the morph output.

**Used in MAD already?** Partly. Zhang et al. (CVPRW 2024) put GAN reconstructions in the genuine class.
Colbois and Marcel (2022) show a generated-image detector wins the GAN cells. A three-way output with a
same-photo aligned middle class was not found.

**First test, at most one day.** Train the middle output on the 256 reconstruction pairs of the GAN blocks and
the diffusion-autoencoder reconstructions on hand, folds by person. Pass: reconstruction against frame-matched
camera photo at or above 0.95 on held-out persons, with the history controls above passing. Kill: history shift
above 0.3 SD or flag rate above 10% after frame and compression alignment. Then the output reads storage
history as the releases do, and the class cannot be offered.

**Risk.** Our first-pass number for reconstruction against camera photo (0.98) includes frame, background and
resolution changes; after alignment it may fall. The field's lesson is that each alignment exposes the next
cue. A detector trained on two generators may not transfer to a third (Rajan et al. report 3 to 26% accuracy on
a new autoencoder family).

**State of the art.** Under the policy "re-synthesised is inadmissible" this is the route to the published
generator rows. Under the other policy it changes nothing in the tables and still reports the class.

### Idea 4. Morph-free mechanism readers from this field as independent instruments

**Source technique.** Released generated-image detectors that each read one known mechanism and never saw a
morph: the ProGAN-trained classifier (Wang et al. 2020: generator traces); NPR (Tan et al. 2024: differences
inside 2 × 2 pixel blocks, the trace of up-sampling); DNA-Det (Yang et al. 2022: pretrained on 170 image
transformations).

**Transfer.** Score our benchmark cells and every ladder rung with these readers, unchanged. A cell that a
mechanism reader separates is separable by that mechanism. This is evidence for claim (a) of the paper from
networks that are not ours and were not trained on any morph, which answers the objection that the shortcut
claim rests on our own probes. Expected pattern: the up-sampling reader moves with the storage-history step and
with landmark cells whose morphs were stored small; the generator reader wins the GAN cells; none moves between
a same-person morph and a two-person morph. The same readers then serve as a control for our own network: its
score should be unrelated to each reader's score within a class.

**Why shortcut-free.** These are instruments, not our detector, so the one-network rule is untouched. They
cannot have learned any cue of a morph benchmark, any partner identity or any morph tool. The ladder shows what
they read: photo against its history-matched copy (storage history), reconstruction against photo (generator),
two-person against same-person morph (must stay near 0.5).

**Used in MAD already?** For GAN morphs with the ProGAN-trained classifier: yes (Colbois and Marcel 2022). With
DNADet features and a trained probe: yes (Colbois and Marcel 2024). An up-sampling reader on landmark cells, and
any such reader on a matched ladder: none found (search listed in section 3).

**First test, half a day.** Download the released weights of the ProGAN-trained classifier and of NPR. Score the
FRLL landmark cells, the MIPGAN cells, MorDIFF, and the ladder rungs. Useful if one reader reaches AUC at or
above 0.90 on at least one benchmark cell, separates a photo from its history-matched copy at or above 0.80, and
stays at or below 0.60 between same-person and two-person morphs. Kill: no reader reaches 0.75 on any cell.

**Risk.** NPR was trained on four ProGAN object classes at fixed size; its behaviour on our frames is unknown.
A negative outcome proves nothing about the cells. Licence terms of the weights must be read first.

**State of the art.** None directly. It strengthens the audit half of the paper.

### Idea 5. Inversion-encoder bottleneck: read identity typicality where storage history cannot reach

This improves identity shrinkage (idea 3 on our table), which failed its control in CLIP and
diffusion-autoencoder spaces because those spaces also encode storage history.

**Source technique.** Inversion-based tests (Karras et al. 2020, Section 5; Albright and McCloskey 2019),
inversion plus biometric traits for synthetic faces (Pasquini et al. 2023), encoders that keep codes near W
(Tov et al. 2021), and the Gaussianised latent space with its Mahalanobis radius (Zhu et al. 2020).

**Transfer.** The field asks "can the generator reproduce this image". We ask a different question of the same
tool: "where does the image land in the generator's code space". The detector is one inversion encoder. Its
output is a W+ code. The decision is a fixed formula on that code: the Mahalanobis radius, in the Gaussianised
space, of the coarse and middle layers only. Those layers carry pose, face shape and facial features. Colour,
microstructure and everything a file history changes go to the fine layers and are discarded by construction.
A landmark morph, a latent morph and a diffusion morph should all land nearer the mean in the identity layers.
The same quantity can serve as an auxiliary regression target for the main network at training time, so that
test time still uses one network.

**Why shortcut-free.** The code of the coarse and middle layers cannot represent file format, file size, border
or fine softness; the encoder works at 256 px from low-resolution feature maps. Ladder contrasts: photo against
history-matched copy and photo against warp-only image must stay within 0.3 SD; two-person morph against its own
warped halves and against the same-person morph carries the claim; the graded-mixing rungs must rise with dose.

**Used in MAD already?** None found (two searches in section 3, family H). StyleGAN latent spaces are used for
making morphs and for differential demorphing.

**First test, at most one day.** The e4e encoder with StyleGAN2 is on disk from the MIPGAN controls
(experiment AG1). Run it unchanged on the landmark ladder rungs of 300 hosts and on the graded-mixing set.
Pass: two-person morph against own warped halves at or above 0.75, history shift at most 0.3 SD, dose trend
positive with an interval excluding zero. Kill: AUC below 0.65, or history shift above 0.3 SD.

**Risk.** The ceiling is averageness of shape, which gave 0.725 on exact landmarks; this is a component, not a
headline. The encoder may push blur into the middle layers. Images must be brought to the encoder's frame with
the existing alignment only. A radius-restoring attacker defeats it for generator morphs, not for landmark
morphs.

**State of the art.** As an auxiliary target it costs nothing at test time. It does not by itself reach the
published rows.

---

## 6. What does not transfer, and why

1. **Spectral and up-sampling detectors, fingerprints, attribution.** A morph and a one-person render of the
   same generator carry the same trace. Against camera photos the trace is exactly the cue we must exclude. It
   is also fragile (Chandrasegaran et al. 2021; Dong et al. 2022), and StyleGAN3 was designed without aliasing.
2. **"Can the generator reproduce it" tests** (projection into W, DIRE, AEROBLADE). The answer is yes for the
   morph and for the control. A midpoint of two codes lies in the region the generator renders well
   (Kynkäänniemi et al.: 2.4% of paths leave it).
3. **One-class coding cost and noise models** (ZED, LNP). They measure how predictable the pixels are. Blending
   and softening both make pixels more predictable. In our own record PNG size alone reaches 0.80 on one
   diffusion contrast. These methods would formalise the softness cue.
4. **Stay-Positive.** It stops features from voting for the genuine class. Our failure is a spurious feature
   voting for the morph class (softness). The paper says so itself: "upsampled real images are still classified
   as fake" (Section 6).
5. **Blur and JPEG augmentation** (Wang et al. 2020). Barred by our image-operation rule. It also hides small
   edits: face-aware liquify edits were detected at chance, and DeepFake AP fell from 98.2 to 89.0 with
   augmentation (same paper).
6. **Frozen features as protection** (UnivFD). Refuted in our record and in theirs: the frozen-CLIP detector
   moves with resize direction (Rajan et al., Table 5), and a linear probe is far behind end-to-end training on
   aligned data (Guillaro et al., Table 3).
7. **Patch-only detectors.** They remove global content cues such as expression. They concentrate on local
   texture, which is where softness and storage history live. For whole generated faces the decisive patches are
   hair and background (Chai et al.), our border and backdrop cue.
8. **Thousands of generators** (Park and Owens 2025). The lesson transfers as "diversity of partners and tools
   beats image count". The scale does not fit three days.
9. **Averageness as the detector for generator morphs.** It is real but not specific (a truncated one-person
   render has it), and the attacker removes it with one multiplication.
10. **The published generator-cell numbers as a target under the policy "a reconstruction is genuine".** They
    are reached by a network that never saw a morph. A detector that ignores the generator cannot match them.

---

## 7. References

### 7.1 Verified during this task

"Full text" = read beyond the abstract. "Abstract" = arXiv abstract page read. "Search" = title, authors and
venue confirmed from search results and publisher pages; not opened further.

**Generated-image detection**

1. Wang, Wang, Zhang, Owens, Efros. CNN-generated images are surprisingly easy to spot... for now. CVPR 2020 (venue from memory). https://arxiv.org/abs/1912.11035. Full text.
2. Gragnaniello, Cozzolino, Marra, Poggi, Verdoliva (authors and venue ICME 2021 from memory; title and content verified). Are GAN generated images easy to detect? A critical analysis of the state-of-the-art. https://arxiv.org/abs/2104.02617. Full text.
3. Chai, Bau, Lim, Isola. What makes fake images detectable? Understanding properties that generalize. ECCV 2020 (venue from memory). https://arxiv.org/abs/2008.10588. Full text.
4. Zhang, Karaman, Chang. Detecting and Simulating Artifacts in GAN Fake Images. WIFS 2019. https://arxiv.org/abs/1907.06515. Abstract.
5. Frank, Eisenhofer, Schönherr, Fischer, Kolossa, Holz. Leveraging Frequency Analysis for Deep Fake Image Recognition. ICML 2020. https://arxiv.org/abs/2003.08685. Abstract.
6. Durall, Keuper, Keuper. Watch your Up-Convolution: CNN Based Generative Deep Neural Networks are Failing to Reproduce Spectral Distributions. CVPR 2020 (venue from memory). https://arxiv.org/abs/2003.01826. Abstract.
7. Chandrasegaran, Tran, Cheung. A Closer Look at Fourier Spectrum Discrepancies for CNN-generated Images Detection. CVPR 2021 (oral). https://arxiv.org/abs/2103.17195. Abstract.
8. Dong, Kumar, Liu. Think Twice Before Detecting GAN-generated Fake Images from their Spectral Domain Imprints. CVPR 2022. https://openaccess.thecvf.com/content/CVPR2022/html/Dong_Think_Twice_Before_Detecting_GAN-Generated_Fake_Images_From_Their_Spectral_CVPR_2022_paper.html. Search.
9. Tan, Liu, Zhao, Wei, Gu, Liu, Wei. Rethinking the Up-Sampling Operations in CNN-based Generative Network for Generalizable Deepfake Detection (NPR). CVPR 2024. https://arxiv.org/abs/2312.10461. Full text.
10. Tan, Zhao, Wei, Gu, Wei. Learning on Gradients: Generalized Artifacts Representation for GAN-Generated Images Detection (LGrad). CVPR 2023. https://openaccess.thecvf.com/content/CVPR2023/html/Tan_Learning_on_Gradients_Generalized_Artifacts_Representation_for_GAN-Generated_Images_Detection_CVPR_2023_paper.html. Search.
11. Liu, Yang, Bi, Xiao, Li, Gao. Detecting Generated Images by Real Images (LNP). ECCV 2022. https://www.ecva.net/papers/eccv_2022/papers_ECCV/html/5017_ECCV_2022_paper.php. Search.
12. Marra, Gragnaniello, Verdoliva, Poggi. Do GANs leave artificial fingerprints? 2018. https://arxiv.org/abs/1812.11842. Abstract.
13. Yu, Davis, Fritz. Attributing Fake Images to GANs: Learning and Analyzing GAN Fingerprints. ICCV 2019. https://arxiv.org/abs/1811.08180. Abstract.
14. Yang, Huang, Cao, Li, Li. Deepfake Network Architecture Attribution (DNA-Det). AAAI 2022. https://arxiv.org/abs/2202.13843. Full text.
15. Liu, Qi, Torr. Global Texture Enhancement for Fake Face Detection in the Wild (Gram-Net). CVPR 2020 (venue from memory). https://arxiv.org/abs/2002.00133. Abstract.
16. Ojha, Li, Lee. Towards Universal Fake Image Detectors that Generalize Across Generative Models (UnivFD). CVPR 2023 (venue from memory). https://arxiv.org/abs/2302.10174. Full text.
17. Cozzolino, Poggi, Corvi, Nießner, Verdoliva. Raising the Bar of AI-generated Image Detection with CLIP. 2023/2024. https://arxiv.org/abs/2312.00195. Abstract.
18. Koutlis, Papadopoulos. Leveraging Representations from Intermediate Encoder-blocks for Synthetic Image Detection (RINE). ECCV 2024. https://arxiv.org/abs/2402.19091. Abstract.
19. Yan, Wang, Jin, Zhang, Liu, Chen, Yao, Ding, Wu, Yuan. Orthogonal Subspace Decomposition for Generalizable AI-Generated Image Detection (Effort). ICML 2025 (venue from memory). https://arxiv.org/abs/2411.15633. Abstract.
20. Cozzolino, Poggi, Nießner, Verdoliva. Zero-Shot Detection of AI-Generated Images (ZED). ECCV 2024 (venue from memory). https://arxiv.org/abs/2409.15875. Full text.
21. Ricker, Lukovnikov, Fischer. AEROBLADE: Training-Free Detection of Latent Diffusion Images Using Autoencoder Reconstruction Error. CVPR 2024. https://arxiv.org/abs/2401.17879. Abstract.
22. Wang, Bao, Zhou, Wang, Hu, Chen, Li. DIRE for Diffusion-Generated Image Detection. ICCV 2023 (venue from memory). https://arxiv.org/abs/2303.09295. Abstract.
23. He, Chen, Ho. RIGID: A Training-free and Model-Agnostic Framework for Robust AI-Generated Image Detection. 2024. https://arxiv.org/abs/2405.20112. Abstract.
24. Albright, McCloskey. Source Generator Attribution via Inversion. CVPR Workshops 2019. https://arxiv.org/abs/1905.02259. Search.
25. Laszkiewicz, Ricker, Lederer, Fischer. Single-Model Attribution of Generative Models Through Final-Layer Inversion. ICML 2024. https://arxiv.org/abs/2306.06210. Abstract.
26. Pasquini, Laiti, Lobba, Ambrosi, Boato, De Natale. Identifying Synthetic Faces through GAN Inversion and Biometric Traits Analysis. Applied Sciences 13(2):816, 2023. https://www.mdpi.com/2076-3417/13/2/816. Search.
27. Cazenavette, Sud, Leung, Usman. FakeInversion: Learning to Detect Images from Unseen Text-to-Image Models by Inverting Stable Diffusion. CVPR 2024. https://arxiv.org/abs/2406.08603. Abstract.
28. Grommelt, Weiss, Pfreundt, Keuper. Fake or JPEG? Revealing Common Biases in Generated Image Detection Datasets. 2024 (ECCV Workshops 2024 from memory). https://arxiv.org/abs/2403.17608. Full text.
29. Rajan, Ojha, Schloesser, Lee. Aligned Datasets Improve Detection of Latent Diffusion-Generated Images. ICLR 2025 (venue from memory). https://arxiv.org/abs/2410.11835. Full text.
30. Guillaro, Zingarini, Usman, Sud, Cozzolino, Verdoliva. B-Free: A Bias-Free Training Paradigm for More General AI-generated Image Detection. CVPR 2025 (venue from memory). https://arxiv.org/abs/2412.17671. Full text.
31. Chen, Xi, Yan, Zhang, Wu, Xie, Chen, Xu, Guan, Yao, Ding. Dual Data Alignment Makes AI-Generated Image Detector Easier Generalizable. NeurIPS 2025 (venue from memory). https://arxiv.org/abs/2505.14359. Full text (first 100,000 characters).
32. Chen, Zeng, Yang, Yang. DRCT: Diffusion Reconstruction Contrastive Training towards Universal Detection of Diffusion Generated Images. ICML 2024. https://proceedings.mlr.press/v235/chen24ay.html. Search.
33. Rajan, Lee. Stay-Positive: A Case for Ignoring Real Image Features in Fake Image Detection. ICML 2025. https://arxiv.org/abs/2502.07778. Full text.
34. Li, Cai, Hao, Jiang, Hu, Feng. Improving Synthetic Image Detection Towards Generalization: An Image Transformation Perspective (SAFE). KDD 2025. https://arxiv.org/abs/2408.06741. Abstract.
35. Yan, Li, Cai, Hao, Jiang, Hu, Xie. A Sanity Check for AI-generated Image Detection (Chameleon, AIDE). ICLR 2025 (venue from memory). https://arxiv.org/abs/2406.19435. Abstract.
36. Zhu, Chen, Yan, Huang, Lin, Li, Tu, Hu, Hu, Wang. GenImage: A Million-Scale Benchmark for Detecting AI-Generated Image. NeurIPS 2023 (venue from memory). https://arxiv.org/abs/2306.08571. Abstract.
37. Park, Owens. Community Forensics: Using Thousands of Generators to Train Fake Image Detectors. CVPR 2025. https://arxiv.org/abs/2411.04125. Abstract.
38. Corvi, Cozzolino, Poggi, Nagano, Verdoliva. Intriguing properties of synthetic images: from generative adversarial networks to diffusion models. 2023. https://arxiv.org/abs/2304.06408. Abstract.
39. Hulzebosch, Ibrahimi, Worring. Detecting CNN-Generated Facial Images in Real-World Scenarios. CVPR Workshops 2020. https://arxiv.org/abs/2005.05632. Search.
40. Ren, Zhou, Shen, Zewde, Duong, Huang, Tiangratanakul, Ng, Wei, Xue. How well are open sourced AI-generated image detection models out-of-the-box: A comprehensive benchmark study. arXiv, February 2026. https://arxiv.org/abs/2602.07814. Abstract.
41. Chandra et al. Deepfake-Eval-2024: A Multi-Modal In-the-Wild Benchmark of Deepfakes Circulated in 2024. arXiv 2025. https://arxiv.org/abs/2503.02857. Abstract.

**Latent-space geometry**

42. Karras, Laine, Aila. A Style-Based Generator Architecture for Generative Adversarial Networks. CVPR 2019 (venue from memory). https://arxiv.org/abs/1812.04948. Full text.
43. Karras, Laine, Aittala, Hellsten, Lehtinen, Aila. Analyzing and Improving the Image Quality of StyleGAN. CVPR 2020 (venue from memory). https://arxiv.org/abs/1912.04958. Full text.
44. Karras, Aittala, Laine, Härkönen, Hellsten, Lehtinen, Aila. Alias-Free Generative Adversarial Networks. NeurIPS 2021 (venue from memory). https://arxiv.org/abs/2106.12423. Abstract. Official code, mapping network read: https://github.com/NVlabs/stylegan3/blob/main/training/networks_stylegan3.py
45. Zhu, Abdal, Qin, Femiani, Wonka. Improved StyleGAN Embedding: Where are the Good Latents? 2020. https://arxiv.org/abs/2012.09036. Full text.
46. Wulff, Torralba. Improving Inversion and Generation Diversity in StyleGAN using a Gaussianized Latent Space. 2020. https://arxiv.org/abs/2009.06529. Full text.
47. Kynkäänniemi, Karras, Laine, Lehtinen, Aila. Improved Precision and Recall Metric for Assessing Generative Models. NeurIPS 2019 (venue from memory). https://arxiv.org/abs/1904.06991. Full text.
48. Agustsson, Sage, Timofte, Van Gool. Optimal transport maps for distribution preserving operations on latent spaces of Generative Models. ICLR 2019. https://arxiv.org/abs/1711.01970. Full text.
49. White. Sampling Generative Networks. 2016. https://arxiv.org/abs/1609.04468. Search.
50. Tov, Alaluf, Nitzan, Patashnik, Cohen-Or. Designing an Encoder for StyleGAN Image Manipulation (e4e). SIGGRAPH 2021 (venue from memory). https://arxiv.org/abs/2102.02766. Full text (first 100,000 characters).
51. Abdal, Qin, Wonka. Image2StyleGAN: How to Embed Images Into the StyleGAN Latent Space? ICCV 2019. https://arxiv.org/abs/1904.03189. Abstract.

**Morphing attacks and their detection**

52. Zhang, Venkatesh, Ramachandra, Raja, Damer, Busch. MIPGAN: Generating Strong and High Quality Morphing Attacks Using Identity Prior Driven GAN. IEEE TBIOM 2021 (venue from memory). https://arxiv.org/abs/2009.01729. Full text (first 100,000 characters).
53. Sarkar, Korshunov, Colbois, Marcel. Are GAN-based Morphs Threatening Face Recognition? ICASSP 2022. https://arxiv.org/abs/2205.02496. Full text.
54. Colbois, Marcel. On the detection of morphing attacks generated by GANs. BIOSIG 2022. https://arxiv.org/abs/2209.00404. Full text.
55. Colbois, Marcel. Evaluating the Effectiveness of Attack-Agnostic Features for Morphing Attack Detection. IJCB 2024. https://arxiv.org/abs/2410.16802. Full text.
56. Damer, López, Fang, Spiller, Pham, Boutros. Privacy-friendly Synthetic Data for the Development of Face Morphing Attack Detectors (SMDD). CVPR Workshops 2022 (venue from memory). https://arxiv.org/abs/2203.06691. Full text.
57. Zhang, Ramachandra, Raja, Busch. Generalized Single-Image-Based Morphing Attack Detection Using Deep Representations from Vision Transformer. CVPR Workshops 2024. https://arxiv.org/abs/2501.09817. Full text.
58. Venkatesh, Zhang, Ramachandra, Raja, Damer, Busch. Can GAN Generated Morphs Threaten Face Recognition Systems Equally as Landmark Based Morphs? Vulnerability and Detection. IWBF 2020. https://arxiv.org/abs/2007.03621. Full text.
59. Venkatesh, Ramachandra, Raja, Spreeuwers, Veldhuis, Busch. Detecting Morphed Face Attacks Using Residual Noise from Deep Multi-Scale Context Aggregation Network. WACV 2020. https://openaccess.thecvf.com/content_WACV_2020/html/Venkatesh_Detecting_Morphed_Face_Attacks_Using_Residual_Noise_from_Deep_Multi-Scale_WACV_2020_paper.html. Search.
60. Raja, Gupta, Venkatesh, Ramachandra, Busch. Towards generalized morphing attack detection by learning residuals. Image and Vision Computing 126:104535, 2022. https://dblp.uni-trier.de/rec/journals/ivc/RajaGVRB22.html. Search.
61. Debiasi, Scherhag, Rathgeb, Uhl, Busch. PRNU-based Detection of Morphed Face Images. IWBF 2018. https://www.christoph-busch.de/files/Debiasi-PRNUMorphDetection-IWBF-2018.pdf. Search.
62. Debiasi, Scherhag, Rathgeb, Uhl, Busch. PRNU Variance Analysis for Morphed Face Image Detection. BTAS 2018. https://www.christoph-busch.de/files/Debiasi-PRNU-variance-MAD-BTAS-2018.pdf. Search.
63. Zhang, Jia, Lyu, Li. Fusion-based Few-Shot Morphing Attack Detection and Fingerprinting. 2022. https://arxiv.org/abs/2210.15510. Search.
64. Damer, Grebe, Zienert, Kirchbuchner, Kuijper. On the generalization of detecting face morphing attacks as anomalies: novelty vs. outlier detection. BTAS 2019. https://publica.fraunhofer.de/handle/publica/408789. Search.
65. Fang, Boutros, Damer. Unsupervised Face Morphing Attack Detection via Self-paced Anomaly Detection (SPL-MAD). IJCB 2022. https://arxiv.org/abs/2208.05787. Search.
66. Ivanovska, Štruc. Face Morphing Attack Detection with Denoising Diffusion Probabilistic Models (MAD-DDPM). IWBF 2023. https://arxiv.org/abs/2306.15733. Search.
67. Damer, Spiller, Fang, Boutros, Kirchbuchner, Kuijper. PW-MAD: Pixel-wise Supervision for Generalized Face Morphing Attack Detection. ISVC 2021. https://arxiv.org/abs/2108.10291. Search.
68. Caldeira, Ozgur, et al. MADation: Face Morphing Attack Detection with Foundation Models. WACV Workshops 2025. https://arxiv.org/abs/2501.03800. Search.
69. Paulo, Proença, Neves. FD-MAD: Frequency-Domain Residual Analysis for Face Morphing Attack Detection. arXiv, January 2026. https://arxiv.org/abs/2601.20656. Search.
70. Ismayilov, Spreeuwers. SFDemorpher: Generalizable Face Demorphing for Operational Morphing Attack Detection. arXiv, March 2026. https://arxiv.org/abs/2603.28322. Abstract.
71. Reddy, Ramachandra, Rao, Mitra. MLSD-GAN: Generating Strong High Quality Face Morphing Attacks using Latent Semantic Disentanglement. arXiv 2024. https://arxiv.org/abs/2404.12679. Abstract.

### 7.2 Seen in search results only, not opened

Used at most as pointers, never as evidence for a number.

- SRL-MAD, one-class S-MAD on structured residual Fourier representations, arXiv 2603.15050.
- R-FLoRA, residual-statistic-gated low-rank adaptation for S-MAD, arXiv 2604.17321.
- "Face morphing detection using Fourier spectrum of sensor pattern noise", ICME 2018, DOI 10.1109/ICME.2018.8486607 (authors not shown in the result).
- Dargaud et al., a principal-component-analysis approach for single morphing attack detection, WACV Workshops 2023.
- MorCode (arXiv 2410.07625) and StableMorph (arXiv 2511.08090): morph generation with spherical interpolation.
- "Approximating Optimal Morphing Attacks using Template Inversion", arXiv 2402.00695.
- DailyBench (arXiv 2607.24016), PGC (arXiv 2605.21207), the NTIRE 2026 challenge on robust detection: recent generated-image benchmarks.
- Zero-shot S-MAD with multimodal language models: arXiv 2602.15461, arXiv 2503.10937, arXiv 2608.29802 (the first and third are already in our planning record).
- FingerprintNet (Jeong et al., ECCV 2022).

### 7.3 Recalled, not verified

Not found during this task. Do not cite from this list without checking.

- Neubert et al., a face morphing detection concept with a frequency and a spatial domain feature space, about 2019.
- Scherhag, Debiasi, Rathgeb, Busch, Uhl, detection of face morphing attacks based on PRNU analysis, IEEE TBIOM 2019.
- Dzanic, Shah, Witherden, Fourier spectrum discrepancies in deep network generated images, NeurIPS 2020.
- Nataraj et al., detecting GAN generated fake images using co-occurrence matrices, 2019.
- McCloskey and Albright, detecting GAN-generated imagery using saturation cues, ICIP 2019.
- Schwarz, Liao, Geiger, on the frequency bias of generative models, NeurIPS 2021.
- Brock, Donahue, Simonyan, BigGAN (the truncation trick in the input space), ICLR 2019.
- Menon et al., PULSE (latent codes on a sphere), CVPR 2020.
- Kilcher, Lucchi, Hofmann, semantic interpolation in implicit models, ICLR 2018.
- Asnani et al., reverse engineering of generative models (model parsing), TPAMI 2023.
- Jeong et al., BiHPF and FrePGAN, 2022.
- Cozzolino et al., ForensicTransfer, 2018.
- Zhong et al., PatchCraft (rich and poor texture contrast), 2023; Chen et al., a single simple patch (SSP), 2024.
- Zheng et al., breaking semantic artifacts (patch shuffling), NeurIPS 2024.
- Tan et al., C2P-CLIP, AAAI 2025; Liu et al., FatFormer, CVPR 2024 (named inside B-Free and DDA as compared methods).
- Corvi et al., on the detection of synthetic images generated by diffusion models, ICASSP 2023 (the "Corvi" detector analysed by Rajan et al.).
- Yu et al., artificial fingerprinting for generative models, ICCV 2021.
- Richardson et al., pSp encoder, CVPR 2021.
- Damer et al., MorGAN, BTAS 2018.
- Provenance and watermark schemes used in deployment (C2PA, SynthID).

### 7.4 Searches that returned nothing relevant

- morphing attack detection StyleGAN latent space truncation averageness "latent" morph single image detection one-identity render control
- face morphing attack "truncation" StyleGAN "mean face" OR "average face" pseudo-morph training morphing attack detection synthetic "truncation trick"
- detect interpolated latent code GAN "interpolation" image "truncation" classifier distinguish truncated samples StyleGAN detection
- "morphing attack" detection "GAN inversion" OR "latent code" encoder StyleGAN detect morph single image latent space classifier
- single image morphing attack detection StyleGAN encoder latent code "Mahalanobis" OR "distance from the mean" OR "typicality" inversion pSp e4e
- morphing attack detection kurtosis OR "non-Gaussianity" OR "higher-order statistics" blend superposition single image
- synthetic image detector zero-shot applied to face morphing attack detection landmark morphs pretrained detector NPR UnivFD
- morphing attack detection resampling traces interpolation artefacts warping "resampling" morph detector robustness resize shortcut
