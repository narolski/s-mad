# Cross-field analysis: detection of diffusion-generated portraits, read for single-image morph detection

11 Nov 2026. Analyst for one neighbouring field (round 3 of ideation). Research and writing only: web search and
page reads, light reads of our own record. No experiment was run, no sealed file was opened.

How to read the source marks. **[R]** = the full text was opened and read beyond the abstract. **[A]** = the
abstract or landing page was opened. **[S]** = found in search results with title, authors and venue or arXiv
number, not opened. Numbers from other papers are quoted with their table or section. They were read through an
automated page reader, so check each against the PDF before it is printed in our paper. Numbers from our own
record are marked as ours and keep the status the brief gives them (reviewed, or first owner numbers).

Terms. S-MAD = single-image morphing attack detection. AUC = area under the ROC curve. EER = equal error rate.
VAE = variational autoencoder (the image encoder and decoder of a latent diffusion model). DDIM = the
deterministic sampler that also lets an image be mapped back to noise ("inversion"). DiffAE = diffusion
autoencoder (Preechakul et al.), the generator behind MorDIFF-type morphs; it has a 512-number semantic code
`z_sem` and an image-sized stochastic code `x_T`. LoRA = low-rank adaptation of a frozen network. MMPMR = share
of morphs that match both contributors in face recognition.

---

## Short answer

1. The field has no ready detector for "mixed latent against single latent". Its reconstruction and inversion
   methods test whether an image lies in the range of a generator. A one-photo reconstruction and a two-person
   morph from the same autoencoder both lie in that range.
2. The field does explain what our probes read on diffusion morphs. A stochastic code obtained by inversion is
   not Gaussian noise. It keeps image structure. Mixing two such codes leaves a footprint of the mixing
   operation. That footprint is the same for two photos of one person and for two persons. The first
   numbers of our paired-difference experiment on diffusion renders (PD1; one fold, unreviewed) show exactly
   this: mixing is read at 0.955, the second person is not (0.249).
3. The field's main lesson is about data, not architecture. Every leading method since 2024 builds training
   pairs in which the two classes differ only in the thing to be detected, and then finds one more leftover cue
   (resolution, then format, then frequency content).
4. On the question "is a one-photo reconstruction genuine or generated" the field is split by task. Detectors of
   generated images call it fake. Work on neural compression calls it real. One paper gives it a third class.
   This supports reporting it as a third category under both policies.
5. Four proposals follow (part 4): a common last hop through the unchanged autoencoder for both classes; a
   three-way output in one network; code-factorial rungs and footprint-matched pairs for diffusion morphs;
   alignment by selection with a frequency-only certificate.

---

## 1. Map of the field's solutions, 2019 to 2026

### 1.1 Families, grouped by the idea behind them

| Family | Idea | Main works (verified) | Status in 2026 |
|---|---|---|---|
| A. Learned artefact classifier with augmentation | Train a CNN on real against generated, add blur and JPEG augmentation, hope the artefacts are shared | Wang et al., CVPR 2020 [A]; Corvi et al., ICASSP 2023 [S]; Ricker et al., VISAPP 2024 [A] | Baseline. GAN-trained detectors fail on diffusion images; retraining on diffusion images fixes it for seen generators (Ricker, abstract) |
| B. Frequency and spectral | Generators leave spectral traces (GAN grid peaks; diffusion models under-produce high frequencies) | Corvi et al. 2023 "Intriguing properties" [S]; Ricker et al. [A]; SPAI, CVPR 2025 [S] (learns the spectrum of real images only, any resolution); SAFE, KDD 2025 [S] (crop, never downsample); FIRE, CVPR 2025 [S] (mid-band reconstruction error) | Strong in clean benchmarks, the first to break under recompression and resizing; also the first to pick up format bias (see part 2) |
| C. Reconstruction error and inversion | A generated image is reproduced by its own generator better than a real one | DIRE [A]; SeDID, ICML workshop 2023 [A]; AEROBLADE [R] (autoencoder only, training-free); LaRE², CVPR 2024 [S]; FIRE [S]; DNF [S] (noise estimated during inversion); FakeInversion, CVPR 2024 [S]; LatentTracer, ICML 2024 [A] | Works for latent diffusion models whose autoencoder is public. AEROBLADE reports mean average precision 0.992 over seven generators (abstract; Table 1 gives 0.978 to 0.999). Its own Sec. 9 says DIRE's public results are affected by JPEG against PNG storage |
| D. Training-free and zero-shot | No generated training data: a statistic of a pretrained model decides | AEROBLADE [R]; ZED, ECCV 2024 [S] (surprise under a lossless coder trained on real images); RIGID [S] (feature change under small noise); Brokman et al., ICLR 2025 [S] (curvature of a diffusion model's score) | Attractive because no dataset bias can be learned, but each statistic has its own confound (image complexity for AEROBLADE, Sec. on complexity) |
| E. Foundation-feature probes | A frozen CLIP or DINO encoder plus a small head generalises better than end-to-end training | UnivFD, CVPR 2023 [S]; Cozzolino et al. 2023/2024 [A] (a handful of examples suffices); AIDE, ICLR 2025 [S] (CLIP plus frequency patches); Zhou et al. 2025 [R] (linear probes on DINOv3, Perception Encoder, MetaCLIP-2) | Leads the in-the-wild sets in 2025: Chameleon averages 96.1 (PE), 92.4 (DINOv3), against 57.2 for UnivFD (their Table 1). The authors' own explanation for the vision-language models is exposure to generated images in pretraining (their Tables 4 and 5), which is a warning, not a mechanism we can use. On a set of private photos and generators newer than the encoders, real-image accuracy is 27.4 and 44.4% for the two vision-language models (Table 4) |
| F. Aligned-pair training | Make each fake a reconstruction of a real image, so the pair differs only in the generator trace | DRCT, ICML 2024 [A]; Aligned Datasets (Rajan et al.) [R]; B-Free (Guillaro et al.) [R]; Dual Data Alignment, DDA (Chen et al.) [R] | The leading recipe. B-Free: 96.3 balanced accuracy on its main table (Table 5), 20.7 points above the next method. DDA: 90.7 average over 11 benchmarks, 15.7 points above the next (its summary table) |
| G. One-sided evidence | Only evidence for "fake" may move the score; features tied to "real" are spurious | Stay-Positive, Rajan and Lee [R] | Last-layer retraining with non-negative weights. FLUX average precision 57.25 to 99.33 for the Corvi detector (Table 1) |
| H. Scale and diversity | More generators in training | Community Forensics, CVPR 2025 [S] (2.7 million images from 4,803 models); GenImage [A]; DF40 [S] | Helps, but the benchmark study of Ren et al. 2026 [A] finds training-data alignment matters more than architecture |
| I. Adversarial training on the generator manifold | Detectors latch onto the initial noise of the generator; attack by optimising that noise, then train on the result | Zhou et al. 2025, "latent prior bias" [R] | CLIP with LoRA rank 4: GenImage average 79.20 to 94.63 (Table 1) |
| J. Provenance instead of detection | Watermark at generation time | SynthID-Image [S] (over ten billion images and frames watermarked, authors' claim) | What large providers deploy. Not applicable to an attacker who makes a morph |

### 1.2 What is deployed and how it does outside the laboratory

- Providers deploy watermarking (SynthID-Image [S]); platforms use commercial classifiers.
- Deepfake-Eval-2024 [S] (content collected from social media in 2024) reports that open-source image detectors
  lose 45% of their AUC against earlier benchmarks; commercial and fine-tuned models do better and still do not
  reach forensic analysts (abstract).
- Ren et al., arXiv 2602.07814 [A]: 23 released detector variants, 12 datasets, 291 generators, used as
  released. Best mean accuracy 75.0%, worst 37.5%. Rankings are unstable across datasets (Spearman 0.01 to
  0.87). Within one architecture family the training data moves accuracy by 20 to 60 points. Flux Dev, Firefly
  v4 and Midjourney v7 are detected at 18 to 30% on average (abstract).
- TrueFake [S] and AI-Face [S] both report clear losses after social-network sharing or other post-processing.

### 1.3 Robustness to compression and resizing: who claims it and what backs it

| Work | Claim and number |
|---|---|
| Aligned Datasets [R] | A detector trained on unaligned data "associates downsampling with real images and upsampling with fake images" (Fig. 2). Aligned training: Playground accuracy after post-processing 24.27 to 61.25 and 76.36 with paired batches (Table 2) |
| B-Free [R] | Balanced accuracy "always above 80%" under resizing, JPEG and blur (read from Fig. 11); 98.5 AUC after a simulated upload (Appendix F, Table 11) |
| DDA [R] | On GenImage with JPEG 96 applied to fakes: 10.5 points above the next method at JPEG 60, 4.1 at resize 2.0, 5.7 at blur 2.0 |
| Mandelli et al. [R] | Fully synthetic against laundered: AUC 0.994 clean, 0.990 at JPEG 70, 0.970 after 0.5 times downscale; accuracy at the fixed threshold falls from 95.9 to 80.2% (Tables I and II). A fixed threshold does not survive resizing |
| AEROBLADE [R] | Weaker than a trained detector under perturbation; deeper feature layers are more stable (Fig. 7, no numbers in text) |
| Cannas et al., JPEG AI [R] | Neural compression at 0.12 bits per pixel raises the false-alarm rate on real images to 0.96 to 0.99 for four of nine detectors (Table 1). Retraining with 20% JPEG AI images only brings 0.96 down to 0.65 (Table 4) |

### 1.4 Face-specific diffusion forgery benchmarks

DiFF, ACM MM 2024 [S] (over 500,000 face images, thirteen diffusion methods, four conditioning types);
DiffusionFace [S] (eleven diffusion models; unconditional, text-guided, image-to-image, inpainting, face swap);
DF40, NeurIPS 2024 [S] (40 methods including diffusion face synthesis and editing); AI-Face, CVPR 2025 [S]
(demographic labels; all 12 detectors degrade under post-processing and cross-dataset tests); DiffFace-Edit [A]
(over two million region-level edits of eight facial regions; studies splices of real and edited content);
TrueFake [S] (FFHQ reals, shared through three social networks). Mandelli et al. [R] run their laundering study
on faces. None of these contains a two-person mix, and none pairs a generated face with a one-photo
reconstruction from the same generator and a matched control.

### 1.5 Timeline in one paragraph

2019 to 2020: one CNN with blur and JPEG augmentation generalises across GANs (Wang et al.). 2022 to 2023:
diffusion images break GAN detectors; spectral analyses; CLIP nearest-neighbour and linear probes (UnivFD);
DIRE and SeDID introduce reconstruction error. 2024: autoencoder-only reconstruction (AEROBLADE), latent
reconstruction (LaRE²), DRCT trains on reconstructions as hard examples, "Fake or JPEG?" shows the standard
benchmark is separable by format and size, FakeInversion adds content-matched evaluation, Chameleon shows
detectors fail on images that fool people. 2025: aligned-pair training becomes the standard (Aligned Datasets,
B-Free, DDA), Stay-Positive, latent prior bias, plain probes on new foundation models lead in-the-wild sets,
neural compression and laundering appear as a problem for the definition of "real". 2026: large out-of-the-box
studies conclude that there is no universal detector and that data alignment decides.

---

## 2. What the field learned about dataset shortcuts, and how it removed them

The field went through the same sequence we are in, one cue at a time. Each fix exposed the next cue.

| Cue | Evidence | Fix | Our analogue |
|---|---|---|---|
| File format | GenImage: reals are ImageNet JPEGs (mostly quality 96), fakes are PNG. A Midjourney-trained ResNet50 tested on uncompressed FFHQ photos: 80.45% correct as PNG, 94.84 at JPEG 95, 100.0 at JPEG 60 (Grommelt et al. [R], Table 2). AEROBLADE [R] Sec. 9 reports the same for DIRE's data | Train only on data with the same quality factor in both classes: robustness at JPEG 95 rises 53.91 to 67.17 (Table 3) | "A file attribute separates the classes perfectly in all 17 cells" (ours, reviewed) |
| Image size | Generators emit fixed sizes; real images vary. The BigGAN detector flags small real images (Grommelt, Fig. 3) | Keep only matched sizes: cross-generator accuracy 71.68 to 82.74 (ResNet50) and 74.09 to 85.83 (Swin-T), with a quarter of the data | Storage history; photos stored small flagged by the SelfMAD release in 203 of 204 cases (ours) |
| Resampling direction | Fakes are 256 px, reals larger, so random-resized-crop gives fakes only upsampling. Ojha's detector: real accuracy 54.16 to 83.58 when everything is downsampled to 256, fake accuracy 69.56 to 29.83 (Rajan et al. [R], Table 5) | Reconstruct each real with the autoencoder at its own resolution; no resizing | The shrink-and-enlarge history of morphs (R0 against R1) |
| A hidden codec | LSUN reals were WebP-compressed and stored as PNG; detectors learned WebP as "real" (Stay-Positive [R]) | Ignore real-side features: non-negative last layer | Any unlisted property of one photo pool |
| Semantic content | The same DALL·E 3 fakes get different scores when the real set is RAISE or COCO (B-Free [R], Fig. 2). Cross-scene drops (Zheng et al., NeurIPS 2024 [S]) | Self-conditioned reconstruction, so each fake has the content of its real; reverse-image-search matched evaluation (FakeInversion [S]); patch shuffling (Zheng et al.) | Half of the genuine class smiling against neutral morphs in 12 of 17 cells; five recurring partners in SMDD |
| Frequency content inside an aligned pair | A frequency detector (SAFE) flags 93% of visually identical autoencoder reconstructions; masking a few high-frequency DCT coefficients removes the detection (DDA [R], Fig. 5). Cause: real images lost high frequencies to JPEG, the decoder restores them | Give the reconstruction the JPEG history of its real image (DDA method section), plus pixel mixing | Morphs are softer than their halves (0.52 times Laplacian variance, ours); on diffusion renders at 100 steps the morphs are sharper than the reconstructions (Laplacian variance alone 0.966, ours, unreviewed) |
| Initial noise of the generator | For every one of 1,000 prompts an initial noise exists that makes a Stable Diffusion image pass as real; often within about 10 optimisation steps (Zhou et al. [R]) | Train on such on-manifold examples | The stochastic code state of a diffusion morph (part 4, proposal 3) |
| Pretraining exposure | New vision-language encoders match fakes to the words "AI generated" (similarity 0.828 and 0.861, Zhou et al. [R], Table 5), and on private photos with newer generators their real-image accuracy is 27.4 and 44.4% (Table 4) | None; the authors name it as the likely source of the gain | "A frozen encoder is not protection" (ours, reviewed) |

How the field now builds bias-free training and tests, in order of strength:

1. **Constrained subsets** (Grommelt et al.): keep only samples whose nuisance values overlap between classes.
2. **Autoencoder reconstruction of each real** (Rajan et al.; DRCT with a diffusion pass): the pair shares
   content, size and source. Rajan et al. add paired batches: each fake sits in the batch with its real and
   gets the same augmentation.
3. **Self-conditioned reconstruction plus local edits with the original background pasted back** (B-Free): the
   detector must find the trace locally. Their ablation: text-paired fakes 61.9, reconstruction 80.7,
   self-conditioned 81.4, plus local inpainting 92.2 to 96.4 balanced accuracy (Table 2). The construction also
   repairs calibration (negative log-likelihood 1.91 to 0.10).
4. **Frequency alignment on top of pixel alignment** (DDA), with a test set built the same way (DDA-COCO):
   detectors without alignment show a large gap between real and fake accuracy on it.
5. **A check in the other direction** (Stay-Positive): take a property tied to the real class, put it on fakes,
   and see whether the score drops.

Two points for our paper. First, the field shows its biases with transplant tests on whole sets. The closest
thing to our ladder is one matched step (a real image against its own reconstruction, as in DDA-COCO). A ladder
of several rungs per image is a finer instrument than the field has. Second, the field
never claims a detector is bias-free. Each paper shows that one named cue is no longer used. That is the claim
form we should copy: a list of named cues, each with its control.

### What the field says about a one-photo reconstruction

| Position | Who | Reason given |
|---|---|---|
| It is fake | DRCT (reconstructions of real images are labelled fake, code README); Rajan et al. ("can still be validly considered fake, at least for our task"); B-Free; DDA | It carries the decoder's trace. The task is to find that trace |
| It is a third class | Mandelli et al. [R]: pristine, laundered, fully synthetic; a second stage separates laundered from fully synthetic at AUC 0.994 (Table I) | The content is real, the trace is synthetic; calling it "synthetic" hides real content |
| It is real | Cannas et al. [R]: a JPEG AI file of a real photo is pristine ground truth, and a detector that flags it is wrong. DDA's limitations: smartphone photos already show synthetic-like traces from in-camera enhancement | Neural processing is becoming ordinary storage; forensics must tell "whether a neural processing step was harmful or innocuous" |

So the rule follows the task. A detector of generated images must flag a reconstruction. A detector of one
specific manipulation must not. Morph detection is of the second kind. The field gives no support for scoring a
reconstruction as a morph, and it gives a precedent (Mandelli) for the third category proposed in
`14_CLASS_DEFINITIONS.md`.

### What the field offers for telling a mixed latent from a single latent

1. **No direct method.** Reconstruction error, inversion and origin attribution (AEROBLADE, DIRE, LatentTracer)
   ask "can this generator reproduce the image". The answer is yes for both. Our identical-and-mirrored-inputs
   check (AD1b) agrees: in the limit, two identical inputs give the one-photo reconstruction.
2. **A reason why mixing is readable.** Inverted codes are not Gaussian. Staniszewski et al. [R]: the mean of
   the top correlations inside 8 by 8 patches is 0.382 for inverted codes against 0.039 for noise (ADM-32,
   Table 2); the spread in plain image areas is 0.46 against 0.72 elsewhere (IF model, Table 3; pure noise has 1.0); interpolations between
   inverted codes show a quality dip in the middle of the path (Fig. 5). NoiseDiffusion [R]: spherical
   interpolation is clean for images the model generated itself and leaves visible artefacts for natural
   images, because the encoded noise is off the level the denoiser expects. Fast-DiM [R]: "a silhouette of the
   head is clearly visible in the encoded x_T". The DiM paper [R] notes that the variant which encodes a
   pre-blended image "often removes many of the high frequency artifacts" of the variant that interpolates two
   stochastic codes.
3. **The footprint does not know about identity.** In the provisional numbers of our identical-and-mirrored-inputs
   check (AD1b; 4 persons) the stochastic codes of any two images are almost orthogonal: cosine distance 0.98 to the mirror image, 0.97 to another
   photo of the same person, 0.99 to another person. A spherical mix of two near-orthogonal structured maps is
   the same kind of object in all three cases. This predicts what the paired-difference experiment (PD1) found on diffusion renders.
4. **The second person sits mostly in the stochastic code, not in the semantic code.** Fast-DiM [R], Table III:
   when the encoded stochastic code is replaced by white noise (noise level 1.0), MMPMR falls to
   4.5 / 3.48 / 2.04% for three face recognition systems. For that table the paper notes that the model "is
   still conditioned on the morphed latent representation"; the sentence stands beside the partial-noise rows,
   and I read it as covering the white-noise row too. The authors conclude that the stochastic code must be
   computed by the forward solver. So a DiffAE morph is closer to a double exposure in an image-shaped code than
   to a semantic mix. This is my reading of one table in an attack paper, not a tested fact about detection;
   the factorial rungs of proposal 3 test it directly.
5. **Typicality of a mixed code.** A linear mix of Gaussian-like codes has the wrong norm (Bodin et al., ICLR
   2025 [S]). This is the statistic of our identity-shrinkage triage (ID0), which is weak and reads storage
   history in feature spaces.
6. **A caution.** Two populations that share a decoder can be separated at 0.994 (Mandelli). Separation inside
   one generator proves nothing about what is read. Our probe result (0.945 to 1.000) needs the same-person
   mix as the negative before it says anything about a second person.

---

## 3. Has each family been used in morph attack detection?

| Family | Used in morph detection? | Reference, or the searches that found nothing |
|---|---|---|
| Reconstruction error | Yes, as one-class detection | MAD-DDPM, Ivanovska and Štruc, IWBF 2023 [S] (diffusion model trained on genuine faces; score is reconstruction error). Colbois and Marcel 2024 [R] note the direction is inconsistent: lower error for morphs with a convolutional autoencoder, higher with diffusion. SRL-MAD, IWBF 2026 [A], states that it does not rely on reconstruction error |
| Inversion, noise-space or latent statistics | Not found for single-image detection | Search "morphing attack detection DDIM inversion OR inverted noise OR stochastic code OR latent inversion": only morph generators (DCMorph [A] uses DDIM inversion with spherical interpolation) and differential demorphing (SFDemorpher [A]) |
| Frequency and spectral | Yes | FD-MAD [S] (Fourier residuals; average EER 1.85% on FRLL-Morph, abstract); SRL-MAD [A] (ring-wise Fourier residual, one-class, tested on MorDIFF); R-FLoRA, TIFS 2026 [A] (Laplacian residual statistics gate LoRA adapters); Colbois and Marcel, BIOSIG 2022 [A] (spectral and texture baselines on GAN morphs) |
| Generated-image detectors applied to morphs | Yes | Colbois and Marcel 2022 [A]: a ResNet pretrained for GAN-image detection is near perfect on GAN morphs. Colbois and Marcel 2024 [R]: a probe on DNADet features (a GAN-attribution network) gives under 1% error one-class on FRGC (Table 7), but 35.78 and 42.65% on FRLL GAN and diffusion morphs when trained on FRGC (Table 5), and 60.50 and 56.55% after print and scan (Table 6). They state the framing openly: "treating MAD as a deepfake detection problem" |
| Foundation-feature probes | Yes | Colbois and Marcel 2024 [R] (frozen CLIP, DINOv2, AIM with a linear SVM); MADation and others in our record. Their bona fide images are untouched photos, all crops 256 px; no reconstruction control |
| Training-free and zero-shot | Yes | MADPromptS [S] (CLIP with prompt sets); face-quality scores and multimodal language models in our record (`docs/PLANNING_RECORD.md` sections 3 and 10) |
| Aligned real and reconstructed pairs | Barely | Zhang, Ramachandra, Raja and Busch, CVPR Workshops 2024 [R]: "reconstructed bona fide images are applied to the datasets with GAN-based morphing algorithms … we can reduce the bias between bona fide and morph samples". One sentence; how they are made is not described; genuine side only; no test. No morph paper builds B-Free-style or DDA-style pairs. Search "morphing attack detection laundering OR regeneration OR purification … bona fide reconstructed" found nothing else |
| Frequency alignment inside pairs | Not found | Same searches; also the 2026 search for morph detection and dataset bias returned only fairness and continual-learning papers |
| Equal post-processing of both classes | Yes, as evaluation practice | Zhang et al. 2024 [R]: both classes printed, scanned and compressed to at most 15 KB |
| One-sided evidence (non-negative head) | Not found | No hit in any of the morph searches |
| Third class for single-subject images | Not found | Search "face morphing attack detection three-class OR multi-class bona fide manipulated morph …": only tool attribution as a multi-class task and a differential system with bona fide, criminal and accomplice attempts |
| Laundering as attack or as control | Not found | Search as above |
| Adversarial training on the generator manifold; control of nuisance codes | Not found | Search "morphing attack detection StyleGAN style mixing OR noise inputs OR stochastic control latent morph versus single latent reconstruction": only generator papers |
| Published audit of dataset shortcuts | Not found | Agrees with our record: no published morph-detection shortcut audit |

---

## 4. Proposals for our task

Each proposal names its source, how it is adapted to the ladder and the constraints, what it cannot use, a first
test of at most one day on data we have, and the number that kills it. All keep one network on one image, no
score fusion, no gate, and use only operations on the allowed list.

### Proposal 1. A common last hop: pass both classes through the unchanged autoencoder

**Source.** Laundering (Mandelli et al.): one encoder and decoder pass makes real photos read as synthetic and
drops camera-model identification from 96.15% to 39.08 to 56.67% (their Section V). JPEG AI (Cannas et al.): a
neural codec overwrites earlier traces. Aligned-pair training (Rajan, B-Free, DDA) uses the same pass to create
the fake class. We turn it round: the pass keeps the label and equalises the last processing step.

**Adaptation.** Let L be the pinned DiffAE path run unchanged on one image (encode both codes, render). This is
the operation that already makes rung R2 of the diffusion ladder.

- *Audit use.* Apply L to both classes of a benchmark cell and to rungs R0, R1, R2w, R3, R4 of the landmark
  ladder. After L every image is a 256 px lossless file from one decoder. File size, codec, chroma subsampling
  and resampling grid are equal by construction. Softness and geometry survive (DiffAE reconstructs closely:
  SSIM 0.927 at 20 steps and 0.991 at 100 on CelebA-HQ 128, their Table 2). A released detector whose
  separation collapses on the laundered cell was reading the last-hop history. One that keeps it reads softness
  or geometry.
- *Training use.* Cross the last-hop state (raw, laundered) with the label on the standard recipe. A laundered
  genuine photo goes to the single-subject class and is never called genuine or morph. A laundered two-person
  morph stays a morph. The decoder trace then appears on both sides and cannot predict the label. Under our
  constraints this is the one permitted operation that changes low-level statistics.
- *A cheap side instrument.* Render from the semantic code with fresh noise (no stochastic encoding, so no
  13-second inversion). By Fast-DiM Table III this drops the contributors' identity. What is left is pose,
  expression, lighting and backdrop. A detector that still separates the two classes of a benchmark cell on
  such renders reads the semantic composition of the cell (for example the smiling half). This is a diagnostic
  only; the images are neither genuine nor morphs.

**Why shortcut-free.** It cannot use file attributes, format, codec or resampling grid (equal after L), and it
cannot use the generator fingerprint (both classes carry it). Ladder contrasts: L(R1) against L(R0) must not
separate; R0 against L(R0) must not move the morph score after training; L(R4) against L(R3) must keep the
signal. It does **not** remove softness; that still needs warped halves and the existing softened examples.

**Prior use in morph detection.** None found (searches in part 3). Closest: the one sentence in Zhang et al.
2024 on reconstructed bona fide images for GAN sets, and our own planned audit with GAN-reconstructed genuine
photos (AG2), both on the genuine side only.

**First test (about 2 A100 hours; about 22 hours on the shared DGX at 157 s per inversion, so Athena, or a cut
to 20 hosts).** Launder 100 hosts of the landmark ladder, OpenCV engine, rungs R0, R1, R2w, R3, R4 (500 images
at about 13 s each). Extract the
cached-feature types (DINOv3, CLIP). Fit host-disjoint logistic probes. Report: (a) L(R1) against L(R0) beside
R1 against R0; (b) L(R4) against L(R3) beside R4 against R3, each as excess over the Laplacian-variance floor;
(c) flag rates of the SelfMAD and MADation releases on L(R0) at their own thresholds.
**Pass:** (a) falls to 0.65 or below and (b) keeps at least 80% of its raw excess.
**Kill:** (a) stays at 0.90 or above (the pass does not equalise storage history, so it is useless as an
equaliser), or (b) falls below 0.60 (the pass erases the morph evidence itself).

**Published tables.** The base recipe is unchanged, so landmark cells should hold. The MorDIFF cell may get
worse, because the decoder trace no longer helps; that is the honest number and is reported under both class
policies.

**Risks.** DiffAE is trained on FFHQ at 256 px; passport-style photos are partly out of domain. Its aligner
re-crops. The pass may soften sharp and soft inputs differently and create a new history cue (test (a) catches
this). Inversion cost. If the Stable Diffusion autoencoder were allowed it would be a thousand times cheaper
and resolution-free, but it is not on the approved list and needs the author's yes.

### Proposal 2. One network with three outputs; the morph score is the contrast against both non-morph classes

**Source.** Mandelli et al. (pristine, laundered, fully synthetic; a detector of two classes puts laundered
images with the synthetic ones). Cannas et al. (the same failure for neural compression). B-Free (how the
training construction decides calibration: negative log-likelihood 1.91 to 0.10, Table 2). Rajan et al. (paired
batches).

**Adaptation.** One network, one softmax over the three categories of the class proposal: G genuine capture
(R0, R1), S single-subject manipulation (R2, R2w, R3m, R3; GAN and diffusion rungs x1, x2; laundered genuine
images), M two-person morph (R4, x3). The reported score is one number, s = log P(M) − log(P(G) + P(S)).
Train with whole within-host tuples in one batch and identical crops (the paired-batch device). No second
stage, no gate: it is a single forward pass.

Why this can beat a binary head with the same negatives: a binary head must give a camera photo and a
same-person morph the same output although they differ by the largest signal in the data (pipeline step read
at 0.91 to 0.98 in the paired-difference experiment, PD1). A three-way head may represent that signal and route it to S. For a camera photo the
score is then "M against G"; for a processed image it is "M against S". A morph is flagged only when it beats
both non-morph explanations. The single-subject table of the paper comes out of the same network as P(S).

**Why shortcut-free.** Storage history, warp, softness, pipeline and generator trace all have a class to go to
that is not "morph". Contrasts: s must not move from R0 to R1 or R0 to R2w (limit 0.3 standard deviations, as
for the alpha-field probe), and s must separate R4 from R3 and x3 from x2.

**Prior use in morph detection.** None found. Multi-class work exists only for attributing the morphing tool,
and one differential system classifies the verification attempt. Our class-definition check found nobody who
scores single-subject images with a label.

**First test (CPU, a few hours, cached features only).** Landmark ladder (536 hosts) and the DiffAE blocks of
the paired-difference experiment (PD1). Five host-disjoint folds. Multinomial three-way head against a binary logistic head with identical data
and identical regularisation grid. Report AUC for R4 against R3 and x3 against x2 from s; the shift of s from
R0 to R1 and to R2w; EER of R4 against R0.
**Kill:** the three-way score does not improve R4-against-R3 (or x3-against-x2) AUC by at least 0.03 **and**
does not halve the R0-to-R1 or R0-to-R2w shift relative to the binary head; or genuine-against-morph EER on
the landmark cells worsens by more than 1 point.

**Published tables.** Only the head changes. The benchmark score is P(M) in log-odds form, so numbers are
comparable.

**Risks.** A linear head on frozen features may show no difference while a LoRA fine-tune would; then the test
is underpowered, and one small fine-tune decides. S is a mixed bag (warp, same-person mix, reconstruction).
Soft two-person morphs may be drawn toward S and raise the miss rate. Single-subject images from tools we
cannot run may land in M; that is recorded, not hidden.

### Proposal 3. For diffusion morphs: code-factorial rungs and footprint-matched pairs

**Source.** DiffAE [R] (two codes). Fast-DiM [R] Table III (the semantic code alone does not make a morph).
Staniszewski et al. [R] and NoiseDiffusion [R] (inverted codes are structured; mixing them leaves artefacts).
DiM [R] (interpolating two stochastic codes leaves high-frequency artefacts that the pre-blend variant
removes). Latent prior bias, Zhou et al. [R] (detectors lean on the noise state; the remedy is examples that
vary the noise while the label stays). AEROBLADE [R] (more denoising steps change the error statistics).

**Adaptation.**

- *New rungs, made with the pinned generator and the existing `interp()` on other argument pairs.* For host A,
  second photo A′ and other person B: semantic code from (A, A′) or (A, B), crossed with stochastic code from
  (A, A′) or (A, B). Two corners exist already (same-person mix, two-person morph). The two new corners carry
  the second person in one code only. Two swap rungs use no interpolation at all: semantic code of A with the
  stochastic code of A′, and with that of B. The off-diagonal and swap rungs are diagnostics and enter no
  error rate. Whether calling the unchanged generator with these pairs counts as "run unchanged" needs the
  author's yes.
- *What the rungs decide.* Which code carries the part of the score that separates two persons from one
  (the "second identity" projection of the paired-difference experiment, PD1: 0.793 on one fold). The field predicts the stochastic code. If so, the
  readable signal on diffusion morphs is a double exposure of two head geometries in an image-shaped code, the
  same kind of evidence as on a landmark blend, and the diffusion and landmark positives can be trained as one
  concept. If the swap rungs separate (B's stochastic code against A′'s), a second person is readable with no
  mixing footprint at all, which is the cleanest statement the paper could make for this family.
- *Training rule for the diffusion family.* The negative of every two-person morph is a same-person mix made
  with the same interpolation and the same step count, never a reconstruction alone. Decoding steps (20 and
  100, both exist for the benchmark-linked set) are crossed with the label, so sharpness carries no label
  information. This is history crossing done with a generator parameter.

**Why shortcut-free.** It cannot use the mixing footprint (present in positive and negative), the generator
trace (both rendered), or sharpness (step-crossed; the Laplacian floor is subtracted). Contrasts: two-person
against same-person mix at equal steps; reconstruction against camera photo must not separate.

**Prior use in morph detection.** None found for the rungs or the rule. The attack papers vary which code is
interpolated to make stronger morphs (DiM variants, Fast-DiM), never to control a detector.

**First test (minutes of GPU; no new inversion).** The full run of the identical-and-mirrored-inputs check
(AD1b), in progress at the time of writing, encodes the stochastic codes of A, A′ and B for 16 persons. Render
the four corners and the two swaps at 20 steps (96 images). Score with the heads of the paired-difference
experiment (PD1) and its two-person-against-same-person projection. Paired sign test per
factor. Repeat on the set from the diffusion-autoencoder generation on Athena (DG1; 536 hosts) when it lands.
**Pass at n = 16:** one factor moves the projection in the expected direction in at least 13 of 16 persons
(one-sided binomial p = 0.011).
**Kill:** neither factor reaches 12 of 16 (p = 0.038); and, on the larger set, two-person against same-person
mix at equal steps stays below 0.65 after the Laplacian floor is subtracted. Then diffusion cells are reported
as "mixing is detected, a second person is not", for every detector including ours.

**Published tables.** Affects only the diffusion training data. The MorDIFF cell is then scored by mixing
evidence, not by the decoder trace.

**Risks.** n = 16 is small. FRLL same-person pairs differ in expression; FRGC and colorFERET second photos are
the cleaner source. With a second person only in the stochastic code the image may not match both contributors
in face recognition; check before any rung is called a morph.

### Proposal 4. Alignment by selection, with a frequency-only certificate

**Source.** Grommelt et al. (constrained subsets with overlapping nuisance values: cross-generator accuracy up
11 points with a quarter of the data). DDA (pairs aligned in pixels are still separable by frequency: 93%).
Rajan et al. (paired batches).

**Adaptation.** The field equalises cues by processing images. We may not write new blur, resize or JPEG code.
So we equalise by choosing and weighting images that exist. This upgrades item 1 of the round-2 chain and the
round-1 reweighting idea with a certificate.

1. A cue vector per image, measured and never applied: file size, Laplacian variance with three kernel sizes,
   eight radial spectrum bands, border fraction, chroma subsampling, history flag, expression label.
2. A cue-only classifier of the label on the training pool. Sample weights (inverse propensity, clipped) or
   coarsened exact matching until the weighted cue-only AUC is at most 0.55.
3. Whole within-host tuples per batch, identical crops.
4. The certificate printed in the paper: cue-only AUC on the weighted training pool and on every evaluation
   cell; and DDA's check, a radial-spectrum-only probe inside matched pairs (R4 against R3, x3 against x2).

**Why shortcut-free.** The named cues are at chance in the training pool by measurement. Contrast: R0 against
R1 at the fixed threshold.

**Prior use in morph detection.** None found. Equal processing of both classes exists as evaluation practice
(Zhang et al. 2024), not as a measured property of a training set.

**First test (CPU, hours).** Cue vectors exist from the cue checks. Fit the cue-only model on the SMDD rebuild
arms and the ladders. Then a weighted against an unweighted logistic head on cached CLIP features.
**Kill:** the cue-only AUC cannot be brought to 0.60 or below while keeping an effective sample size of at
least 30% (the classes do not overlap in cue space, so selection cannot work and only generated controls can);
or the weighted head does not at least halve the R0-to-R1 flag-rate change at the fixed threshold.

**Published tables.** Less effective data; the field's precedent is that matched subsets generalise better.
Report the cost on FRLL cells.

**Risks.** Only named cues are balanced. Softness is tied to blending physically (0.52 times), so overlap in
sharpness needs the existing soft genuine images and warped halves in the pool. Weights can explode.

### Smaller additions that follow from the field

- **A flip-rate figure for every detector.** Zhou et al. measure how easily a detector is turned by changing
  only the noise. Our discrete version: for each host, the share of nuisance-only variants on disk
  (history-matched, other step count, stored small, laundered) that cross the fixed threshold. One number per
  detector.
- **Write the claim as a list.** Each field paper shows one named cue is not used. Our abstract should list the
  cues and the control for each, not say "shortcut-free".
- **Do not print the 0.945 to 1.000 result of the frozen-feature probe (FZ1) without the same-person negative.** Mandelli's 0.994 between
  two populations from one decoder shows how easy such separation is.

---

## 5. What does not transfer, and why

| Technique | Why not |
|---|---|
| Reconstruction error and inversion as the detector (DIRE, AEROBLADE, LaRE², FIRE, DNF) | It asks whether the generator can reproduce the image. True for a one-photo reconstruction and for a morph. It needs the attacker's generator at test time. In morph detection the sign of the error already differs between models (Colbois and Marcel 2024). Useful only as a covariate that measures "generator trace" |
| Calling every reconstruction fake (DRCT, Rajan, B-Free, DDA) | Their task is the trace. Ours is the second person. Adopting their label would make a single-subject image a morph, which our rules call an error |
| Stay-Positive (non-negative head) | It removes cues tied to the *real* class. Our measured shortcut is on the other side: softness and storage history *raise* the morph score. The paper lists exactly this as its open limitation (upsampled images stay "fake") |
| Blur, JPEG and resize augmentation; DDA's JPEG alignment | Not allowed (no new blur, resize or JPEG code). Grommelt et al. also find random JPEG augmentation does not remove the format bias |
| Patch shuffling and patch voting against semantic bias (Zheng et al.; Mandelli's 96 px patches) | They push the detector to local texture. Local texture is where softness and storage history live. A second person is a property of the whole face |
| Native-resolution multi-crop testing with averaged logits (B-Free, SPAI) | Averaging crops is score fusion. A crop does not contain the face |
| Training-free statistics (ZED, RIGID, score curvature) | They measure distance from camera-image statistics. A history-matched genuine photo is also off those statistics; a morph of two camera photos need not be |
| Foundation-model linear probes as a safety argument | The field's own explanation for their success is exposure to generated images in pretraining. That has no counterpart for morphs, and our record already shows a frozen encoder follows storage history |
| On-manifold adversarial training as published | It needs a nuisance latent that carries no label. In DiffAE the stochastic code carries the contributors (Fast-DiM Table III); StyleGAN3 has no noise inputs. Only the measurement (flip rate) transfers, not the training |
| Scale (thousands of generators) | Three days; few morphing tools exist |
| Watermarks and provenance | The attacker makes the image |

---

## 6. References

### Verified during this task (59)

Read beyond the abstract [R]:

1. Ricker, Lukovnikov, Fischer. AEROBLADE: Training-Free Detection of Latent Diffusion Images Using Autoencoder Reconstruction Error. arXiv 2401.17879, 2024. https://arxiv.org/abs/2401.17879
2. Rajan, Ojha, Schloesser, Lee. Aligned Datasets Improve Detection of Latent Diffusion-Generated Images. arXiv 2410.11835, v3 2025. https://arxiv.org/abs/2410.11835
3. Guillaro, Zingarini, Usman, Sud, Cozzolino, Verdoliva. A Bias-Free Training Paradigm for More General AI-generated Image Detection (B-Free). arXiv 2412.17671, v2 2025. https://arxiv.org/abs/2412.17671
4. Chen, Xi, Yan, Zhang, Wu, Xie, Chen, Xu, Guan, Yao, Ding. Dual Data Alignment Makes AI-Generated Image Detector Easier Generalizable. arXiv 2505.14359, v6 2025 (the paper thanks NeurIPS reviewers). https://arxiv.org/abs/2505.14359
5. Grommelt, Weiss, Pfreundt, Keuper. Fake or JPEG? Revealing Common Biases in Generated Image Detection Datasets. arXiv 2403.17608, 2024. https://arxiv.org/abs/2403.17608
6. Rajan, Lee. Stay-Positive: A Case for Ignoring Real Image Features in Fake Image Detection. arXiv 2502.07778, 2025. https://arxiv.org/abs/2502.07778
7. Mandelli, Bestagini, Tubaro. When Synthetic Traces Hide Real Content: Analysis of Stable Diffusion Image Laundering. arXiv 2407.10736, 2024. https://arxiv.org/abs/2407.10736
8. Cannas, Mandelli, Popović, Alkhateeb, Gnutti, Bestagini, Tubaro. Is JPEG AI going to change image forensics? arXiv 2412.03261; ICCV Workshops 2025. https://arxiv.org/abs/2412.03261
9. Zhou, He, Lin, Fan, Ding, Li. Breaking Latent Prior Bias in Detectors for Generalizable AIGC Image Detection. arXiv 2506.00874, 2025. https://arxiv.org/abs/2506.00874
10. Zhou, He, Lin, Fan, Ding, Zeng, Li. Brought a Gun to a Knife Fight: Modern VFM Baselines Outgun Specialized Detectors on In-the-Wild AI Image Detection. arXiv 2509.12995, 2025. https://arxiv.org/abs/2509.12995
11. Preechakul, Chatthee, Wizadwongsa, Suwajanakorn. Diffusion Autoencoders: Toward a Meaningful and Decodable Representation. arXiv 2111.15640. https://arxiv.org/abs/2111.15640
12. Zheng, Zhang, Fang, Liu, Lian, Han. NoiseDiffusion: Correcting Noise for Image Interpolation with Diffusion Models beyond Spherical Linear Interpolation. ICLR 2024. https://arxiv.org/abs/2403.08840
13. Staniszewski, Kuciński, Deja. There and Back Again: On the Relation between Noise and Image Inversions in Diffusion Models. arXiv 2410.23530, v4 2025. https://arxiv.org/abs/2410.23530
14. Damer, Fang, Siebke, Kolf, Huber, Boutros. MorDIFF: Recognition Vulnerability and Attack Detectability of Face Morphing Attacks Created by Diffusion Autoencoders. IWBF 2023. https://arxiv.org/abs/2302.01843
15. Blasingame, Liu. Leveraging Diffusion for Strong and High Quality Face Morphing Attacks (DiM). arXiv 2301.04218; IEEE TBIOM 2024. https://arxiv.org/abs/2301.04218
16. Blasingame, Liu. Fast-DiM: Towards Fast Diffusion Morphs. arXiv 2310.09484, v3 2024. https://arxiv.org/abs/2310.09484
17. Colbois, Marcel. Evaluating the Effectiveness of Attack-Agnostic Features for Morphing Attack Detection. IJCB 2024. https://arxiv.org/abs/2410.16802
18. Zhang, Ramachandra, Raja, Busch. Generalized Single-Image-Based Morphing Attack Detection Using Deep Representations from Vision Transformer. CVPR Workshops 2024, pp. 1510-1518. https://arxiv.org/abs/2501.09817

Abstract or landing page opened [A]:

19. Wang, Bao, Zhou, Wang, Hu, Chen, Li. DIRE for Diffusion-Generated Image Detection. arXiv 2303.09295, 2023. https://arxiv.org/abs/2303.09295
20. Chen, Zeng, Yang, Yang. DRCT: Diffusion Reconstruction Contrastive Training towards Universal Detection of Diffusion Generated Images. ICML 2024, PMLR 235:7621-7639. https://proceedings.mlr.press/v235/chen24ay.html (code README read: https://github.com/beibuwandeluori/DRCT)
21. Ren, Zhou, Shen, Zewde, Duong, Huang, Tiangratanakul, Ng, Wei, Xue. How well are open sourced AI-generated image detection models out-of-the-box: A comprehensive benchmark study. arXiv 2602.07814, 2026. https://arxiv.org/abs/2602.07814
22. Ma, Duan, Kong, Shi, Xu. Exposing the Fake: Effective Diffusion-Generated Images Detection (SeDID). AdvML-Frontiers at ICML 2023. https://arxiv.org/abs/2307.06272
23. Wang, Sehwag, Chen, Lyu, Metaxas, Ma. How to Trace Latent Generative Model Generated Images without Artificial Watermark? (LatentTracer). ICML 2024. https://arxiv.org/abs/2405.13360
24. Ricker, Damm, Holz, Fischer. Towards the Detection of Diffusion Model Deepfakes. VISAPP 2024. https://arxiv.org/abs/2210.14571
25. Cozzolino, Poggi, Corvi, Nießner, Verdoliva. Raising the Bar of AI-generated Image Detection with CLIP. arXiv 2312.00195, v2 2024. https://arxiv.org/abs/2312.00195
26. Wang, Wang, Zhang, Owens, Efros. CNN-generated images are surprisingly easy to spot... for now. CVPR 2020. https://arxiv.org/abs/1912.11035
27. Zhu, Chen, Yan, Huang, Lin, Li, Tu, Hu, Hu, Wang. GenImage: A Million-Scale Benchmark for Detecting AI-Generated Image. arXiv 2306.08571, 2023. https://arxiv.org/abs/2306.08571
28. Ding, Yi, He, Xiao, Xu, Du. DiffFace-Edit: A Diffusion-Based Facial Dataset for Forgery-Semantic Driven Deepfake Detection Analysis. arXiv 2601.13551, 2026. https://arxiv.org/abs/2601.13551
29. Colbois, Marcel. On the detection of morphing attacks generated by GANs. BIOSIG 2022. https://arxiv.org/abs/2209.00404
30. Paulo, Proença, Neves. SRL-MAD: Structured Residual Latents for One-Class Morphing Attack Detection. IWBF 2026. https://arxiv.org/abs/2603.15050
31. Ramachandra. R-FLoRA: Residual-Statistic-Gated Low-Rank Adaptation for Single-Image Face Morphing Attack Detection. IEEE TIFS 2026 (accepted). https://arxiv.org/abs/2604.17321
32. Chettaoui, Caldeira, Ozgur, Ramachandra, Boutros, Damer. DCMorph: Face Morphing via Dual-Stream Cross-Attention Diffusion. CVPR Workshops 2026. https://arxiv.org/abs/2604.21627
33. Ismayilov, Spreeuwers. SFDemorpher: Generalizable Face Demorphing for Operational Morphing Attack Detection. arXiv 2603.28322, 2026. https://arxiv.org/abs/2603.28322

Found in search results with title, authors and venue or arXiv number [S]:

34. Cazenavette, Sud, Leung, Usman. FakeInversion: Learning to Detect Images from Unseen Text-to-Image Models by Inverting Stable Diffusion. CVPR 2024. https://arxiv.org/abs/2406.08603
35. Yan, Li, Cai, Hao, Jiang, Hu, Xie. A Sanity Check for AI-generated Image Detection (Chameleon, AIDE). ICLR 2025. https://arxiv.org/abs/2406.19435
36. Cozzolino, Poggi, Nießner, Verdoliva. Zero-Shot Detection of AI-Generated Images (ZED). ECCV 2024. https://arxiv.org/abs/2409.15875
37. He, Chen, Ho. RIGID: A Training-free and Model-Agnostic Framework for Robust AI-Generated Image Detection. arXiv 2405.20112, 2024. https://arxiv.org/abs/2405.20112
38. Brokman, Giloni, Hofman, Vainshtein, Kojima, Gilboa. Manifold Induced Biases for Zero-shot and Few-shot Detection of Generated Images. ICLR 2025. https://arxiv.org/abs/2504.15470
39. Luo, Du, Yan, Ding. LaRE²: Latent Reconstruction Error Based Method for Diffusion-Generated Image Detection. CVPR 2024. https://arxiv.org/abs/2403.17465
40. Chu, Xu, Wang, Zhang, You, Zhou. FIRE: Robust Detection of Diffusion-Generated Images via Frequency-Guided Reconstruction Error. CVPR 2025. https://arxiv.org/abs/2412.07140
41. Zhang, Xu. Diffusion Noise Feature: Accurate and Fast Generated Image Detection. arXiv 2312.02625, 2023. https://arxiv.org/abs/2312.02625
42. Corvi, Cozzolino, Zingarini, Poggi, Nagano, Verdoliva. On the Detection of Synthetic Images Generated by Diffusion Models. ICASSP 2023. https://arxiv.org/abs/2211.00680
43. Corvi, Cozzolino, Poggi, Nagano, Verdoliva. Intriguing Properties of Synthetic Images: from Generative Adversarial Networks to Diffusion Models. arXiv 2304.06408, 2023. https://arxiv.org/abs/2304.06408
44. Karageorgiou, Papadopoulos, Kompatsiaris, Gavves. Any-Resolution AI-Generated Image Detection by Spectral Learning (SPAI). CVPR 2025. https://arxiv.org/abs/2411.19417
45. Li et al. Improving Synthetic Image Detection Towards Generalization: An Image Transformation Perspective (SAFE). arXiv 2408.06741; KDD 2025 per a listing. https://arxiv.org/abs/2408.06741
46. Ojha, Li, Lee. Towards Universal Fake Image Detectors that Generalize Across Generative Models. CVPR 2023. https://arxiv.org/abs/2302.10174
47. Park, Owens. Community Forensics: Using Thousands of Generators to Train Fake Image Detectors. CVPR 2025. https://arxiv.org/abs/2411.04125
48. Zheng, Lin, Zhao, Wang, Guo, Liu, Shen. Breaking Semantic Artifacts for Generalized AI-generated Image Detection. NeurIPS 2024. https://proceedings.neurips.cc/paper_files/paper/2024/hash/6dddcff5b115b40c998a08fbd1cea4d7-Abstract.html
49. Bodin, Stere, Margineantu, Ek, Moss. Linear Combinations of Latents in Generative Models: Subspaces and Beyond. ICLR 2025. https://arxiv.org/abs/2408.08558
50. Cheng, Guo, Wang, Nie, Kankanhalli. Diffusion Facial Forgery Detection (DiFF). ACM MM 2024. https://arxiv.org/abs/2401.15859
51. Chen et al. DiffusionFace: Towards a Comprehensive Dataset for Diffusion-Based Face Forgery Analysis. arXiv 2403.18471, 2024. https://arxiv.org/abs/2403.18471
52. Yan et al. DF40: Toward Next-Generation Deepfake Detection. NeurIPS 2024 Datasets and Benchmarks. https://arxiv.org/abs/2406.13495
53. Lin, Santosh, Wu, Wang, Hu. AI-Face: A Million-Scale Demographically Annotated AI-Generated Face Dataset and Fairness Benchmark. CVPR 2025. https://arxiv.org/abs/2406.00783
54. Dell'Anna, Montibeller, Boato. TrueFake: A Real World Case Dataset of Last Generation Fake Images also Shared on Social Networks. arXiv 2504.20658, 2025. https://arxiv.org/abs/2504.20658
55. Chandra et al. Deepfake-Eval-2024: A Multi-Modal In-the-Wild Benchmark of Deepfakes Circulated in 2024. arXiv 2503.02857, 2025. https://arxiv.org/abs/2503.02857
56. Gowal et al. SynthID-Image: Image Watermarking at Internet Scale. arXiv 2510.09263, 2025. https://arxiv.org/abs/2510.09263
57. Ivanovska, Štruc. Face Morphing Attack Detection with Denoising Diffusion Probabilistic Models (MAD-DDPM). IWBF 2023. https://arxiv.org/abs/2306.15733
58. Paulo, Proença, Neves. FD-MAD: Frequency-Domain Residual Analysis for Face Morphing Attack Detection. arXiv 2601.20656, 2026. https://arxiv.org/abs/2601.20656
59. Caldeira, Boutros, Damer. MADPromptS: Unlocking Zero-Shot Morphing Attack Detection with Multiple Prompt Aggregation. arXiv 2508.08939, 2025. https://arxiv.org/abs/2508.08939

### Recalled, not verified

Works I know of but did not open, or details that the opened page did not show.

- Venues not shown on the arXiv pages I opened: DIRE (ICCV 2023), AEROBLADE (CVPR 2024), Aligned Datasets (ICLR 2025), B-Free (CVPR 2025; the DDA table prints "CVPR'24"), Fake or JPEG? (ECCV Workshops 2024), Stay-Positive (ICML 2025), DDA (NeurIPS 2025), Diffusion Autoencoders (CVPR 2022).
- Fang et al., SPL-MAD (unsupervised morph detection by self-paced anomaly detection, IJCB 2022): seen only as cited by Colbois and Marcel.
- Tan et al., NPR (up-sampling traces, CVPR 2024); PatchCraft; DE-FAKE; FatFormer; C2P-CLIP; RINE; Synthbuster; DistilDIRE; DiffusionForensics; D3 (seen only as a row in B-Free's Table 8).
- White, "Sampling Generative Networks" (2016): seen only as cited in a snippet of Bodin et al.
- TGIF and TGIF2 (text-guided inpainting forgery; localisation fails on fully regenerated images), FragFake, DiffSeg30k, Semi-Truths, SIDA and SID-Set: seen only as search snippets or recalled.
- AIGIBench (arXiv 2505.12335), OmniAID (2511.08423), GAMMA (2509.10250), DetectZoo (2606.04205), Spectral Collapse in Diffusion Inversion (2602.13303), and a CVPR 2026 paper "Layer Consistency Matters": titles seen in search results only.
- "Organic or Diffused" (Ha et al., CCS 2024) on commercial detectors: searched, not found.
- Greedy-DiM; PRNU-based morph detection (2018); Face X-ray; REPAIR and AFLite (dataset resampling against bias): recalled.
- The exact frequency-fusion procedure of DDA: the introduction speaks of fusing high frequencies of the real image into the reconstruction, the method section of applying the real image's JPEG quality to the reconstruction. I could not resolve which is the final method from the page.
