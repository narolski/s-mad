# Shortcut-free S-MAD: literature and method proposals

Date: 2026-11-11. Scope: single-image morphing attack detection (S-MAD) that detects identity blending and cannot use benchmark-construction cues. Target: CVPR 2027 (16 Nov 2026).

## How to read this

- **Checked** = I opened a search result or the arXiv page this session. **Memory** = cited from memory, arXiv ID not re-checked; verify before it goes into `references.bib`.
- Compute figures in Part 2 are my estimates, not measurements.
- Not found: any paper called "UniMAD". Two searches returned nothing under that name; it may be a different title.
- I found no published paper that audits MAD benchmarks for construction shortcuts the way your experiments do. The closest items are an IJCB 2026 tutorial slide deck and older "use PNG, equalise quality" advice (Section D). That gap is the paper's opening.

## A framing that organises everything below

Four kinds of cue separate a morph from a bona fide image. Only the last two are about the attack.

| Level | Cue | Example | Legitimate? |
|---|---|---|---|
| L1 | Incidental construction | file size, JPEG history, resampling, crop | No |
| L2 | Renderer fingerprint | StyleGAN/DiffAE decoder traces, DDIM step count | No (a one-identity render has it too) |
| L3 | Blending process | ghosting, texture smoothing from alpha-blending two warped images | Partly: intrinsic to landmark morphs, absent in latent morphs |
| L4 | Identity semantics | averaged shape/texture, "typicality", two recoverable identities | Yes |

Matched one-identity negatives through the same pipeline remove L1 and L2. Same-identity "self-morph" negatives (two photos of one person, morphed) also remove most of L3. What survives is L4.

One quantitative point about L4, worth putting in the paper. If identity codes are roughly isotropic, the mean of two independent identities has norm shrunk by sqrt((1+c)/2), where c is their cosine similarity: 0.71 for unrelated pairs, 0.87 for look-alikes at c=0.5. So a latent-space morph is a more "average" face, and that is the only single-image signal an ideal generator leaves. This matches your finding of a linear typicality direction in CLIP. It also sets a ceiling: attackers who pick look-alike pairs shrink the signal, and naturally average-looking bona fide faces are false positives.

---

# Part 1. Literature

## A. Shortcut-learning mitigation

**A1. Group DRO** (Sagawa et al., ICLR 2020; arXiv:1911.08731, memory).
Minimises worst-group loss over (label x spurious attribute) groups, with strong regularisation. Needs group labels.
- Our setting: groups = label x processing history (source resolution, JPEG Q, resampler, generator, DDIM steps). You know these because you build the data.
- Needs: history metadata per image; no extra compute.
- Risk: only helps if every history appears under both labels. If a group is empty, DRO has nothing to balance.

**A2. JTT** (Liu et al., ICML 2021; arXiv:2107.09044, memory).
Train an ERM model, then upweight the examples it gets wrong. No group labels.
- Our setting: a deliberately shortcut-prone first model (e.g. tiny CNN on 32x32 thumbnails or on JPEG quantisation tables) identifies "shortcut-conflicting" samples to upweight.
- Needs: two training runs.
- Risk: on SMDD the shortcut is nearly perfectly predictive, so there are almost no conflicting samples to upweight. Weak unless twins are added.

**A3. Last-layer retraining / DFR** (Kirichenko et al., ICLR 2023; arXiv:2204.02937, checked). Counterpoint: Le et al., arXiv:2308.00473 (checked).
ERM features often contain the core feature; retrain only the linear head on a small set where the shortcut does not hold.
- Our setting: freeze SelfMAD/MADation/MixFaceNet features, refit the head on the matched StyleGAN3 and DiffAE twin sets. This is the cheapest test of "do existing features contain any L4 signal at all".
- Needs: minutes of CPU/GPU on cached features.
- Risk: your clean-test result suggests the features do not carry it. A null here is still a clean, publishable diagnostic.

**A4. IRM / V-REx** (Arjovsky et al., arXiv:1907.02893; Krueger et al., ICML 2021, arXiv:2003.00688; both memory).
Seek predictors whose optimal classifier (IRM) or risk (V-REx) is equal across training environments.
- Our setting: environments = processing histories; V-REx variance penalty across them.
- Needs: at least 3-4 environments with different shortcut strength.
- Risk: known to fall back to ERM when environments are few or the model is over-parameterised. Use as a regulariser on top of matched data, not as the fix.

**A5. Counterfactual / matched-pair training.** In generated-image detection: Aligned Datasets (Rajan et al., ICLR 2025; arXiv:2410.11835, checked), B-Free (Guillaro et al., CVPR 2025; arXiv:2412.17671, checked), Dual Data Alignment (Chen et al., NeurIPS 2025; arXiv:2505.14359, checked).
Build each fake as a reconstruction of a real image so the pair differs only in the generator trace. DDA adds that pixel alignment is not enough: reconstructions stay misaligned in frequency, so it aligns that too.
- Our setting: the direct analogue has the labels shifted one step. Both classes are renders; the pair differs only in whether one or two identities went in. See M1.
- Needs: generator passes for both classes (you have DiffAE, StyleGAN2/3 inversions, landmark tools).
- Risk: DDA's warning applies. A two-image interpolation and a one-image reconstruction may still differ in spectrum (interpolated latents give smoother output). Check with a frequency-only probe.

**A6. Adversarial cue removal and concept erasure.** DANN (Ganin et al., arXiv:1505.07818, memory); LEACE (Belrose et al., NeurIPS 2023; arXiv:2306.03819, memory).
DANN trains features that a domain head cannot classify. LEACE gives a closed-form linear projection that makes a concept linearly unpredictable with minimal feature change.
- Our setting: erase "history" (JPEG Q, source resolution, generator ID) from frozen CLIP/FR features with LEACE, then fit the MAD head.
- Needs: history labels; LEACE is a covariance computation.
- Risk: LEACE is linear only; an MLP head can recover the cue. If history and label are perfectly confounded in the fitting data, erasure also removes the label. Fit LEACE on twin-balanced data only.

**A7. Domain randomisation of processing history.** MAD precedent: consistency regularisation (arXiv:2308.10392, checked via search).
Apply random resize/JPEG/blur chains so history carries no label information.
- Our setting: apply the same sampled chain to both members of a matched pair. Independent sampling per class is not enough.
- Needs: CPU augmentation.
- Risk: randomisation applied after the fact cannot hide earlier history (double-JPEG grids, upsampling traces survive). It reduces L1 but does not replace matching.

**A8. Shortcut-matched negatives / Stay-Positive** (Rajan and Lee, ICML 2025; arXiv:2502.07778, checked).
Constrain the detector to use only evidence for the positive class, ignoring "real-image" features. Reported implementation: non-negative last-layer weights.
- Our setting: bona fide images have no single signature, so a detector should fire only on positive evidence of blending. Combine with twins.
- Needs: a one-line constraint.
- Risk: if "camera JPEG" is encoded as absence of a feature, the sign constraint does not stop it.

## B. Deepfake-detection analogues

**B1. Self-Blended Images** (Shiohara and Yamasaki, CVPR 2022; arXiv:2204.08376, memory) and **SelfMAD** (Ivanovska et al., FG 2025; arXiv:2504.05504, checked).
Blend an image with a transformed copy of itself and label it fake, so the detector learns generic blending traces. SelfMAD adds FFT-magnitude patterns to mimic generator fingerprints.
- Hygiene in SelfMAD (checked in the paper): trains on SMDD bona fide only, 384 px, Dlib crops. No JPEG handling described, no matched controls, no discussion of resolution history.
- Our setting: SBI labels a one-identity blend as an attack. That is the opposite of what you need. By construction SelfMAD is an L3 (blending) detector and cannot be an L4 detector. This inversion is a strong talking point.
- Risk for us: none as a method; it is the baseline that M1 inverts.

**B2. LAA-Net** (Nguyen et al., CVPR 2024; arXiv:2401.13856, checked via search; journal version LAA-X arXiv:2604.04086).
Trains on real data plus pseudo-fakes, with heatmap attention on the most vulnerable blended pixels.
- Our setting: localisation supervision for landmark morphs (where the blend mask is known).
- Risk: same as SBI. It localises blending, not identity.

**B3. "Detectors are blending detectors" critiques.** Alpha Blending Hypothesis (Yermakov et al., arXiv:2605.10334, checked): **withdrawn 4 Nov 2026** because training reals overlapped with test sets. Also "Can We Leave Deepfake Data Behind?" (Cheng et al., NeurIPS 2024; arXiv:2408.17052, memory).
Claim: frame-level deepfake detectors mostly find compositing traces; relabelling self-blends as real collapses AUROC.
- Our setting: the same experiment for MAD (label self-morphs as bona fide, watch detectors collapse) is your StyleGAN3/DiffAE clean test in another form. Cite the idea, but note the withdrawal; do not lean on its numbers.
- Risk: a reminder that leakage between train reals and test sets sinks this kind of paper. Audit your FRLL/FRGC/FERET identity overlap before claiming anything.

**B4. Reconstruction-based detectors.** DIRE (Wang et al., ICCV 2023; arXiv:2303.09295, memory); DRCT (Chen et al., ICML 2024; code github.com/beibuwandeluori/DRCT, memory); AEROBLADE (Ricker et al., CVPR 2024; arXiv:2401.17879, checked); LaRE2 (CVPR 2024) and FIRE (CVPR 2025; arXiv:2412.07140), both checked via search.
Generated images are reconstructed by their generator's inverse better than real ones. DRCT uses reconstructions of reals as hard negatives in a contrastive loss.
- Our setting: these separate render from photo (L2). They cannot separate two-identity render from one-identity render. DRCT's hard-negative recipe is the useful part: a one-identity reconstruction is the hard negative for a two-identity interpolation.
- Risk: reconstruction error tracks DDIM steps and resolution, which is exactly what your diffusion results already follow.

**B5. Identity-consistency detectors.** ICT (Dong et al., CVPR 2022; arXiv:2203.01318, memory); DiffusionFake (Sun et al., NeurIPS 2024; arXiv:2410.04372, checked).
ICT: a face swap has different identities in inner and outer face; measure the disagreement. DiffusionFake: a forgery carries source and target identity; force detector features to let a frozen Stable Diffusion reconstruct both.
- Our setting: DiffusionFake is the closest published analogue to "detect two identities". The morph version supervises the detector to recover both contributors (M2). ICT applies only to spliced landmark morphs where the blended inner face is pasted into one contributor's head.
- Needs: contributor images or embeddings at training time (you have them).
- Risk: full-face and latent morphs blend uniformly, so there is no inner/outer contrast.

**B6. ID-unaware detectors.** Implicit Identity Leakage (Dong et al., CVPR 2023; arXiv:2210.14457, checked). Related: UCF (Yan et al., ICCV 2023; arXiv:2304.13949, memory); Effort (Yan et al., ICML 2025; arXiv:2411.15633, memory).
Detectors memorise training identities, which hurts cross-dataset results; fix by suppressing identity features.
- Our setting: a warning in the other direction. An identity-based MAD detector can memorise which SMDD identities appear in morphs. Split by identity, and make every identity appear under both labels.
- Risk: SMDD's bona fide and morph-contributor identity sets must be audited.

## C. Morphing-specific signals of two identities

**C1. Identity disentanglement.** OrthoMAD (Neto et al., BIOSIG 2022; arXiv:2208.07841, checked); IDistill (Caldeira et al., EUSIPCO 2023; arXiv:2306.03002, checked); MorDeephy (Medvedev et al., arXiv:2208.03110, listed in search, method not re-read).
OrthoMAD regularises two latent vectors to be orthogonal and to carry the two identities. IDistill distils an identity-separating autoencoder into the classifier.
- Hygiene: both train on SMDD and test on FRLL-type sets; no matched one-identity negatives, so the "identity" branches can still key on construction.
- Our setting: keep the idea (two identity slots), add twins and a retrieval test that proves the slots hold identity.
- Risk: without the retrieval test the slots are unfalsifiable.

**C2. Single-image demorphing.** Banerjee and Ross (arXiv:2209.02933, checked); diffDemorph (Shukla and Ross, arXiv:2505.14527, checked); MLLM-conditioned demorphing (arXiv:2605.25442, checked); SFDemorpher (arXiv:2603.28322, differential, checked via search).
Recover the two contributor faces from one morph, lately with coupled diffusion. The 2026 paper states earlier reference-free methods assume train/test identity overlap or a known morph method.
- Our setting: demorph, then score FR distance between the two outputs. Cheaper: predict two embeddings, not two images (M2).
- Needs: image-space demorphing is days of diffusion training; embedding-space is hours.
- Risk: a demorpher always outputs two faces. On bona fide inputs it may hallucinate a second identity, so calibrating on twins is essential.

**C3. FR-embedding and image-quality analysis.** "When Morphs Look Better" (Peng et al., arXiv:2611.00074, checked; the ID implies November 2026 but the page header says 15 Oct 2026, so confirm the reference); embeddings for pair selection and MAD (arXiv:2305.18216, title only).
17 face-image-quality scores used as training-free MAD. Best mean D-EER 11.4% on FRLL but about 40% on FEI; thresholds do not transfer (FRLL threshold gives 100% BSCER on FEI); many methods rate diffusion morphs higher quality than bona fide.
- Hygiene: all inputs aligned to 112 px; source resolution and JPEG history not reported; the authors say they cannot isolate the cause of the dataset shift.
- Our setting: this is independent evidence for your thesis (quality is a dataset-level construction variable). It also suggests a legitimate reading: FR feature norm and typicality (M3). Very recent, from the Darmstadt group; cite and differentiate.
- Risk: quality and typicality are entangled; the matched test must separate them.

**C4. Soft-biometric, landmark and physical cues.** Landmark-based detection (Scherhag et al., 2018); reflection analysis (Seibold et al., arXiv:1807.02030); both memory.
Morphs shift landmark geometry toward the mean and can break specular-highlight consistency.
- Our setting: landmark geometry "toward the mean" is the shape half of the typicality argument. Cheap to add to M3 as 3DMM or landmark-shape features.
- Risk: historically weak alone (high EER); pose and expression dominate shape variance.

**C5. Recent S-MAD papers and their data hygiene.**

| Paper | Idea | Train / test | Hygiene noted |
|---|---|---|---|
| MADation (Caldeira et al., WACVW 2025; arXiv:2501.03800, checked) | CLIP + LoRA + head | SMDD / MAD22, FRLL-type | None reported on history matching |
| SelfMAD (arXiv:2504.05504, checked) | Self-blend + FFT patterns | SMDD bona fide / FRLL, FRGC, FERET morphs, Morph-PIPE, Greedy-DiM, MorCode | No JPEG or resolution control described |
| MADPromptS (Caldeira et al., 2025; arXiv:2508.08939, checked) | Zero-shot CLIP, prompt ensemble | none / MAD22 etc. | Zero-shot, so whatever CLIP separates is what the benchmark offers; EER 18-28% reported |
| ChatGPT for MAD (Zhang et al., arXiv:2503.10937, checked) | Zero-shot MLLM and vision models | none / own print-scan set | Not examined |
| Open MLLMs (Ivanovska and Struc, arXiv:2602.15461, abstract checked) | Zero-shot LLaVA etc.; best beats task-specific baselines by 23% EER | none / several | Abstract gives none |
| FD-MAD (Paulo et al., arXiv:2601.20656, checked) | Deviation from power-law spectrum + MRF over regions | SMDD / FRLL (1.85% EER), MAD22 (6.12%) | Spectral residuals are the most history-sensitive feature there is |
| SRL-MAD (same group, arXiv:2603.15050, checked) | One-class, ring-wise Fourier residual latents | bona fide only / FERET, FRLL morphs, MorDIFF | Same concern |
| R-FLoRA (Ramachandra, arXiv:2604.17321, checked) | Frozen ViT, LoRA gated by Laplacian residual statistics | four ICAO sets, seven morph types | Same concern |
| ViT S-MAD (Zhang et al., CVPRW 2024; arXiv:2501.09817) | ViT features, digital / print-scan / compressed | cross-dataset | Tests compression robustness, not compression as a cue |
| Attack-agnostic features (arXiv:2410.16802) | Frozen general features + probe; one-class variants | several | Notes print-scan removes generator traces |
| Foundation-model benchmark (Sony et al., arXiv:2505.24214) | 41 VLMs zero-shot on biometric tasks | none | Not examined |

The pattern worth stating in the paper: zero-shot models with no MAD training reach 18-28% EER, or beat trained baselines. A model that was never shown a morph cannot have learned "two identities". The simplest explanation is that it reads construction cues or typicality. Your controlled tests can decide which.

## D. Benchmark-design and dataset-bias papers

**D1. Fake or JPEG?** (Grommelt et al., ECCVW 2024; arXiv:2403.17608, checked).
GenImage detectors learn JPEG compression and image size, because reals are ImageNet JPEGs of varied size and fakes are fixed-size PNGs. Removing the bias changes cross-generator results by more than 11 points.
- Our setting: the direct template for your audit. Same two variables.

**D2. GenImage** (Zhu et al., NeurIPS 2023; arXiv:2306.08571, memory) and **Chameleon / "A Sanity Check"** (Yan et al., arXiv:2406.19435, memory). The benchmark D1 audits, and a later test set on which standard detectors fail.

**D3. B-Free, Aligned Datasets, DDA** (see A5). All three argue dataset construction matters more than architecture. B-Free's own framing: "careful dataset design matters more than the detector itself".

**D4. Motion-bias audit for AI-video detection** (arXiv:2607.00948, checked via search). Scores depend on dataset motion bias and on JPEG order and downscaling; performance drops to near chance on an unbiased set. A current example of the same audit structure in a neighbouring field.

**D5. MAD-specific precedents.**
- Gomez-Barrero et al., NIST IFPC 2018 slides (christoph-busch.de/files/Gomez-NIST-IFPC-Vulnerability-181128.pdf, checked via search): bona fide and morphs must have equal image quality or the classifier becomes a quality detector.
- Spreeuwers et al., "Practical Evaluation of Face Morphing Attack Detection Methods" (2022, checked via search): single-pipeline training yields detectors of that pipeline, e.g. double-JPEG traces; recommends lossless storage; added noise defeats detectors.
- Raja et al., MAD database and benchmark (arXiv:2006.06458, memory): morphs stored as PNG to avoid JPEG cues.
- IJCB 2026 tutorial "When Two Faces Become One" (Ivanovska; slides at lmi.fe.uni-lj.si, found via search, not opened): lists shortcut learning from dataset, attack and quality bias as a risk.

So the community has said "equalise quality" since 2018, yet SMDD/MAD22/FRLL-era papers do not report doing so, and nobody has published the audit. I found no FRLL-specific bias analysis.

**D6. Shortcut learning in general** (Geirhos et al., arXiv:2004.07780, memory). Background citation.

---

# Part 2. Proposed methods

Shared rules for all designs:

1. **Twins.** Every positive has a one-identity negative from the same pipeline with the same parameters. Three constructions:
   - Latent morphs (DiffAE, StyleGAN2/3): positive = decode(interp(z_A, z_B)); twin = decode(interp(z_A, z_A')), where A' is a second photo of A (FRGC, FERET, CASIA-WebFace have several per identity). Fallback twin when no second photo exists: decode(z_A).
   - Landmark morphs: positive = morph(A, B); twin = morph(A, A') with the same tool, alpha and blend mask.
   - SMDD-only setting (synthetic identities, one image each): make A' with Arc2Face from A's ArcFace embedding, or with a StyleGAN2 pose/expression edit of A's latent.
2. **Shared history.** One sampled post-processing chain (resize, resampler, JPEG Q, optional blur) per pair, applied to both members.
3. **Identity-disjoint splits.** Every identity appears under both labels within its split.
4. **Primary test.** AUC and BPCER at fixed APCER on held-out matched twins, on a generator not used in training. FRLL/MAD22 numbers are secondary.
5. **Probes on every model.** A history probe (predict JPEG Q, source resolution, generator from penultimate features) and a thumbnail baseline (the same task at 32 px, and on file metadata alone). If the thumbnail baseline matches the model, the result is void.

Given your pre-registration practice, each design lists a falsifier that can be fixed before the run.

## M1. Twin-contrast training: self-morphs are negatives (rank 1)

- **Mechanism.** Invert SelfMAD. A one-identity blend is bona fide; only a two-identity blend is an attack. The detector is trained on pairs that share pipeline and history, so the only learnable difference is identity mixing.
- **Data.** About 60k pairs: 20k landmark (FRGC/FERET/CASIA, two tools), 20k DiffAE, 20k StyleGAN2/3. For the SYN-MAD-compliant variant, SMDD identities with Arc2Face second views. Hold out one pipeline entirely (suggest StyleGAN3) for the test.
- **Model and loss.** CLIP ViT-L with LoRA, or your MorphMamba backbone. Per-image BCE plus a within-pair margin ranking loss, s(morph) > s(twin) + m. Group DRO over pipeline x label.
- **Falsifier.** Held-out-pipeline twin AUC below 0.60 (bootstrap CI lower bound below 0.55). Or the 32 px thumbnail baseline within 0.03 AUC of the model.
- **Compute (estimate).** Data: 10-15 H100-hours, mostly DiffAE decoding. Training: 4-6 H100-hours per run; 3 seeds x 2 backbones fits in one day on 4 GPUs.
- **Why first.** It is the direct answer to the task, it reuses assets you have, and a null result is itself the paper's negative finding with the strongest possible control.
- **Main risk.** A' differs from A in pose and lighting, while B differs from A in pose, lighting and identity. If A-A' pose gaps are systematically smaller than A-B gaps, ghosting magnitude becomes a new shortcut. Fix: match pairs on head-pose and landmark distance before morphing, and report it.

## M2. Embedding demorphing: predict both contributors (rank 2)

- **Mechanism.** A two-slot head predicts two ArcFace-space embeddings from one image. For a morph the targets are the contributors' embeddings; for a twin they are the embeddings of A and A' (nearly equal). Score = 1 - cos(e1, e2). A construction cue cannot tell the head which two people went in.
- **Data.** M1's pairs plus frozen glintr100 embeddings of contributors.
- **Loss.** Permutation-invariant cosine loss to the two targets, plus a small BCE on the spread. AdaFace as a second teacher for a cross-embedder check.
- **Falsifier.** Contributor retrieval: with a gallery of 10k identities, e1 and e2 must retrieve both true contributors at a rate clearly above what the morph's own ArcFace embedding achieves. If retrieval is no better than that baseline, the slots hold no demorphed identity and the score is a relabelled classifier. Second falsifier: spread on twins equals spread on morphs.
- **Compute (estimate).** 6-8 H100-hours per run; embeddings precomputed in about 1 hour.
- **Novelty.** High. OrthoMAD/IDistill have identity slots without matched negatives or a retrieval test; DiffusionFake does this for deepfakes in pixel space; diffDemorph does it in image space without detection.
- **Main risk.** Demorphing from one image is ill-posed. The head may learn "embedding of morph plus or minus a generic direction". The retrieval test catches this.

## M3. Identity-typicality (norm-shrinkage) detector (rank 3)

- **Mechanism.** Test the sqrt((1+c)/2) prediction directly. Features: pre-normalisation FR feature norm, distance to the population mean and kNN density in ArcFace and AdaFace space, 3DMM or landmark-shape coefficient norm, and your CLIP typicality direction. A small logistic or GBM head on top.
- **Data.** Cached features of M1's pairs; a bona fide reference gallery (CASIA-WebFace, FFHQ) for density.
- **Loss.** Logistic regression on twin-balanced data, after LEACE erasure of history labels from the features.
- **Falsifiers.** (i) Dose-response: score must rise monotonically with alpha from 0 to 0.5 on morphs you generate at graded alpha. (ii) Pair-similarity: score must fall as contributor cosine rises, following the shrinkage curve. (iii) Twin AUC below 0.60.
- **Compute.** About 2 GPU-hours for feature extraction; the rest is CPU. Runs on the GB10.
- **Why it matters.** It gives the paper a principled statement of what is detectable in one image and a ceiling, with look-alike pairs as the hard case. It also explains why zero-shot CLIP and FIQA methods "work".
- **Main risk.** Typicality false-flags average-looking people and may differ across demographic groups. Report BPCER by group. FR networks may also normalise the shrinkage away, since the network re-embeds the morph image.

## M4. Alpha-dose regression (rank 4)

- **Mechanism.** Train a regressor for the mixing fraction min(alpha, 1-alpha) instead of a binary label. Alpha = 0 passes through the same pipeline and is the negative. A model that reads construction cues outputs a step; one that reads identity mixing outputs a ramp.
- **Data.** For each pair, alpha in {0, 0.1, 0.2, 0.3, 0.4, 0.5}, all three pipelines. Roughly 6x M1's positives, so subsample to about 150k images.
- **Loss.** Huber on alpha, plus within-pair ordinal ranking.
- **Falsifier.** Spearman correlation between predicted and true alpha on a held-out pipeline below 0.3, or predictions that jump between alpha=0 and 0.1 and stay flat afterwards (a step means a pipeline cue: for landmark tools, alpha=0 must still run the warp and blend code path).
- **Compute (estimate).** 20-25 H100-hours of data generation, 6 hours training.
- **Main risk.** Operational morphs sit at alpha near 0.5, so the ramp adds no accuracy there; its value is as evidence. Can be merged into M1 as an auxiliary loss if time is short.

## M5. Latent-canonicalised detection (rank 5)

- **Mechanism.** Push every image through one encoder and classify the code, not the pixels: DiffAE's 512-d semantic code z_sem (encoder only, no DDIM), optionally StyleGAN W+ from your inverter. Pixel history is largely discarded by the bottleneck; LEACE removes what remains.
- **Data.** z_sem for M1's pairs plus FRLL/MAD22 for the secondary test.
- **Loss.** MLP on LEACE-projected codes, BCE, twin-balanced.
- **Falsifier.** History probe on the projected codes above 0.60 AUC for JPEG Q or source resolution (canonicalisation failed), or twin AUC below 0.60.
- **Compute.** About 2 H100-hours encoding; training is minutes.
- **Main risk.** DiffAE is FFHQ-256 only, so passport-style FRLL/FRGC images are out of domain, and z_sem encodes blur and sharpness, which correlate with history. DiffAE-made morphs are also "in-distribution" for this encoder in a way landmark morphs are not.

## M6. History-crossed DRO with last-layer retraining of existing detectors (rank 6)

- **Mechanism.** The standard robust recipe as the reference line. Take SelfMAD, MADation and MixFaceNet-MAD features; (a) DFR: refit only the head on twin-balanced data; (b) fine-tune with group DRO + V-REx over history environments.
- **Data.** M1's pairs with history labels.
- **Falsifier.** For (a): twin AUC below 0.55 means the published features contain no identity-blending signal, which is a headline number for the audit section. For (b): no gain over ERM on twins.
- **Compute.** (a) under 1 GPU-hour; (b) about 4 H100-hours per detector.
- **Novelty.** Low as a method, high as a diagnostic. Run (a) on day 1 regardless.
- **Main risk.** None technical; it may simply confirm chance.

## M7. Part-wise identity agreement (rank 7)

- **Mechanism.** ICT for morphs. Compute FR embeddings from regions (eyes, nose-mouth, full inner face, outer face/contour) with a part-trained or occlusion-robust embedder, and score disagreement between parts.
- **Data.** Landmark morphs made by splicing the blended inner face into one contributor's head, with twins.
- **Loss.** Contrastive: parts of one image agree for twins, disagree for spliced morphs.
- **Falsifier.** No separation on full-face-blend or latent morphs is expected; the method is falsified if it also fails on spliced morphs against twins.
- **Compute.** 6-10 H100-hours including part-embedder fine-tuning.
- **Main risk.** Narrow coverage. Only one morph family has the cue, and the splice seam (L3) is a competing explanation.

## Ranking

| Rank | Method | Chance of a valid positive result | Novelty | Cost |
|---|---|---|---|---|
| 1 | M1 Twin-contrast (self-morphs as negatives) | Medium-high for landmark, low-medium for latent | Medium-high | ~1 day |
| 2 | M2 Embedding demorphing with retrieval test | Medium | High | ~1 day |
| 3 | M3 Identity-typicality with dose and similarity curves | Medium | Medium-high | hours |
| 4 | M4 Alpha-dose regression | Medium | Medium | ~1.5 days |
| 5 | M5 Latent-canonicalised detection | Low-medium | Medium | hours |
| 6 | M6 DRO / DFR retrofit of existing detectors | Low as method, certain as diagnostic | Low | hours |
| 7 | M7 Part-wise identity agreement | Low-medium, one morph family | Low-medium | ~1 day |

## Suggested four-day order

- **Day 1.** Build the twin set (all three pipelines, pose-matched pairs, shared histories). Run M6(a) and M3 on cached features the same day; both need only features.
- **Day 2.** Train M1 (3 seeds, 2 backbones) and M2. Generate graded-alpha data in the background.
- **Day 3.** M4 as an auxiliary loss on the best M1 model; M5. Dose-response and pair-similarity curves for all models.
- **Day 4.** Held-out-pipeline evaluation, probes, thumbnail baselines, FRLL/MAD22 secondary numbers. M7 only if GPUs are idle.

## What the paper can claim under each outcome

- **M1 or M2 works on held-out twins:** the first S-MAD detector shown to respond to identity blending, with a dose-response curve.
- **Only M3 works:** single-image MAD reduces to typicality; state the shrinkage ceiling and the look-alike failure case.
- **Nothing works on latent morphs, something works on landmark morphs:** L3 is detectable, L4 is not. Single-image detection of well-rendered latent morphs is not supported by evidence, and current benchmark numbers measure construction.

All three are consistent with your existing clean-test nulls, which predict that the third outcome is the most likely for latent morphs.

## Open risks across all designs

- A' quality. If Arc2Face second views of SMDD identities drift in identity (cosine well below a real same-person pair), the SYN-MAD-compliant twins are contaminated. Measure the A-A' cosine distribution against FRGC same-person pairs first.
- Spectral mismatch between interpolation and reconstruction (the DDA point) could be a residual L2 cue in latent twins. The fallback twin decode(z_A) is more exposed to this than interp(z_A, z_A').
- Identity leakage between training reals and FRLL/FRGC/FERET test sets (the reason the Alpha Blending paper was withdrawn).
