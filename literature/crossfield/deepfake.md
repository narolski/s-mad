# Cross-field analysis: deepfake detection (face swap, reenactment, face editing) and what it gives single-image morph detection

11 Nov 2026. Written by the analyst for the neighbouring field "detection of manipulated face images and video
frames". Research and writing only: web search and page reads, light reads of this repository. No experiment was
run. Nothing sealed was opened.

How to read this file.

- **Verified** means: I found the work during this task (search result or page) and the title, first author and
  venue or arXiv number below come from that page. **Read** means: I read beyond the abstract (method, tables,
  limitations). There are 15 such works; they are marked "read" in the reference list.
- Numbers from other papers are quoted with their table or section. Most pages were read through an automated page
  reader. Re-check every number against the PDF before it enters the manuscript. Where the reader itself noticed an
  inconsistency inside a paper, I say so.
- Numbers about our own data come from the round-3 brief (`ideas/ROUND3_BRIEF.md`), the result page of the
  alpha-field probe (AF0) and the landmark result page of the paired-difference experiment (PD1). Several of them
  are first passes that are not yet reviewed.
- Acronyms. S-MAD: single-image morphing attack detection. AUC: area under the receiver operating curve. EER:
  equal error rate. FR: face recognition. SBI: self-blended image. CLIP: the OpenAI image-text encoder. LoRA:
  low-rank adaptation of a frozen network. TTA: test-time adaptation.
- Ladder rungs as in the brief: R0 camera photo; R1 the same photo with storage history; R2w warp only; R3m photo
  blended with its mirror; R3 two photos of one person; R4 two persons.

---

## 0. The ten-line answer

1. The deepfake field solved cross-dataset generalisation mostly with one trick: train on blends made from real
   images, and pair every fake with its own real. Its detectors are, by the field's own later admission, blend
   detectors. That is the same finding as our paired-difference result (a head trained only on one-person mixes
   ranks two-person morphs at 0.78).
2. The field's label for a one-image blend is "fake". Ours must be "not an attack". The construction transfers; the
   label does not. One deepfake paper (ED4) already shows what happens when real-with-real composites are labelled
   real: cross-dataset AUC 0.82; removed: 0.68; labelled fake: 0.54 to 0.61.
3. A face swap puts two sources in two places. A morph puts two sources in the same place. So everything that
   compares regions (blending boundary, patch consistency, inner against outer identity) has nothing to compare in
   a full-face morph. It survives only if we build the second region ourselves, in training.
4. The field has documented the same shortcuts we measured: "low resolution implies fake" (DF40), identity
   memorisation (Dong et al.), high AUC with a useless fixed threshold (GenD, the Deepfake Detection Challenge).
5. Four proposals follow (section 5): a second-identity field whose complement is a one-person blend; a cumulative
   ladder code; history-subspace surgery used first as an audit and then in training; identity-agreement slots with
   a retrieval test.
6. For morphs made by a generator from a mixed code, the whole blend family is silent, exactly as it is on fully
   synthesised faces in deepfake benchmarks. Nothing in this field changes that.

---

## 1. Where a morph differs from a face swap, precisely

Write a blend as `I = M * F + (1 - M) * B` with foreground F, background B and mask M in [0, 1].

| | Face swap or reenactment | Landmark morph | Morph from a generator (GAN code mix, diffusion autoencoder) |
|---|---|---|---|
| Mask M | about 1 inside the inner face, 0 outside, soft at the edge | a constant, about 0.5, over the whole face or the whole frame | no mask; one render from a mixed code |
| Where the two sources are | in two different places | in the same place, each at half weight | nowhere as pixels; mixed before rendering |
| Face X-ray map `4 M (1 - M)` | a ring at the edge of the mask | 1 everywhere inside: no spatial information | not defined |
| Geometry | source warped to the target's shape; target shape kept | both warped to the mean shape; the shape itself is averaged | set by the generator |
| Untouched reference inside the image | yes: outer face, hair, background | none for a full-frame blend; the surround of one contributor for a spliced morph | none |
| Identity | inner face one person, outer face another | one "between" identity that must match both persons | one "between" identity |
| Is a one-person version an attack? | yes by definition (any manipulation is fake) | no: a blend of one person with himself changes no identity | no: a one-photo reconstruction is not an attack |

Consequences.

- **The blending boundary does not exist** in a full-face morph. Face X-ray (Li et al., CVPR 2020) defines its
  target as `B = 4 M (1 - M)` (their Eq. 2). With M constant the target is constant. It reappears only for spliced
  morphs, where the blended inner face is pasted back into one contributor's photo.
- **There is no reference region.** Pairwise self-consistency learning (Zhao et al., ICCV 2021) asks whether two
  patches have the same "source feature". In a full-face morph every patch has the same mix of two sources. The
  consistency map is all ones, as for a real image.
- **Inner against outer identity does not exist.** The Identity Consistency Transformer (Dong et al., CVPR 2022)
  and Nirkin et al. (TPAMI 2022) compare the identity of the inner face with that of the surrounding head. A
  full-face morph has the same mixed identity in both. A spliced morph has the mix inside and one contributor
  outside, so the comparison works there, and only there.
- **The self-blend changes class.** SBI (Shiohara and Yamasaki, CVPR 2022) blends an image with a transformed copy
  of itself and calls it fake. Blend ratio is drawn from {0.25, 0.5, 0.75, 1, 1, 1}. With ratio 0.5 and a full-face
  mask that image is our rung R3m in spirit: one capture blended with a moved copy of itself. Under the binding
  rule "a genuine image that was only processed and is called a morph is an error" it is a negative for us.
- **A cross-identity blend with a constant mask is a landmark morph.** Face X-ray's training generator picks the
  second face among the 100 nearest neighbours in landmark space from other videos (their Section 3.2). Zhao et
  al.'s generator picks a frame of a different identity within a landmark distance threshold. That is morph pair
  selection. The deepfake field has been training on "partial morphs with a mask" since 2020 without calling them
  that.
- **What the two sources leave behind.** In a swap: a seam, and two regions with different noise, colour and
  compression statistics. In a morph: superposition (each person's own contours at half contrast where the warps
  do not agree) and cancellation (independent fine detail averaged, so about half the variance). Our measured
  softness floor (0.52 times the Laplacian variance of the warped halves) is the cancellation. It is the same
  number that storage history moves. This is why the deepfake recipe, moved to morphs unchanged, gives SelfMAD's
  behaviour.

What survives the difference.

| Deepfake construction | Survives? | In what form |
|---|---|---|
| Train on blends of real images only | yes | already SelfMAD and our ladder |
| Pair each fake with its real and give both the same augmentation (SBI: "the same augmentation is applied to each real image and its SBI") | yes | the within-host pairing of the ladder; history applied to both members of a pair |
| Self-blend labelled fake | no | becomes the hard negative (R3m, R3) |
| Real-with-real composite labelled real (ED4 ClockMix) | yes | direct precedent for one-person blends as negatives |
| Blending-boundary target | only for spliced morphs | not usable as the method under "one network, no gate" |
| Region-wise labels (ICT gives each token the identity label of its region) | yes, if we build regions | proposal 5.1: the other region is a one-person blend |
| Ordered attributes real, self-blend, cross-identity blend, deepfake (ProDet) | yes | proposal 5.2: this is the ladder |
| Identity consistency loss (ICT) | yes | proposal 5.4: consistent means one person, also for one-person blends |
| Shortcut-subspace suppression (S3) | yes | proposal 5.3 |
| Test-time training on a pseudo-fake made from the test image (OST) | no | section 6.7 gives the algebra |

---

## 2. Map of the field, 2019 to 2026

### 2.1 Blending supervision and self-blending (the family that leads the classic cross-dataset tables)

- **Face X-ray** (Li et al., CVPR 2020). Predict the blending boundary. Train on real images only, blended with a
  landmark neighbour; mask from the convex hull, deformed and blurred; colour matched. Trained on blended images
  only: AUC 93.47 on DFD, 71.15 on DFDC, 74.76 on Celeb-DF (their Table 2). Stated limits: may fail on entirely
  synthetic images; AUC falls from 87.35 on lightly compressed to 61.6 on heavily compressed FaceForensics++
  (their Section 6).
- **Pairwise self-consistency learning with the inconsistency image generator** (Zhao et al., ICCV 2021). Dense
  target: for every pair of patches, do they come from the same source. Target built from the mask as
  `1 - |m_p - m_q|`. The second face is of a different identity with close landmarks. Limits stated: unknown for
  entire-face synthesis, which "should be self-consistent".
- **Self-blended images** (Shiohara and Yamasaki, CVPR 2022). One image, two copies; one copy gets colour and
  frequency changes (among them downsampling or sharpening), the source copy gets a resize and a shift; blend with
  a deformed hull mask. Four simulated artefacts: landmark mismatch, blending boundary, colour mismatch, frequency
  inconsistency. Cross-dataset AUC with EfficientNet-B4: Celeb-DF 93.18, DFD 97.56, DFDC 72.42, DFDC preview
  86.15, FFIW 84.83 (their Table 1). On 20,000 StyleGAN faces: 69.11 (their Section 5).
- **Successors.** SLADD (Chen et al., CVPR 2022): an adversarial synthesiser picks the hardest blend configuration
  and the detector also predicts the configuration. LAA-Net (Nguyen et al., CVPR 2024): heatmap of the most
  vulnerable blended pixels plus a consistency branch, trained on real data only. CDFA (Lin et al., ECCV 2024): a
  curriculum that raises the share of pseudo-fakes and searches the augmentation per image. FreqBlender (Li et
  al., NeurIPS 2024): blends frequency components, not pixels. ProDet (Cheng et al., NeurIPS 2024): see 2.6.
  Forensics Adapter (Cui et al., CVPR 2025): a small adapter beside a frozen CLIP learns the blending boundary.
- **Where it stands.** These methods lead on the older swap benchmarks. On the DF40 benchmark SBI averages 0.514
  on unknown domains, with 0.342 and 0.426 on two entire-face-synthesis sets (Yan et al., NeurIPS 2024, their
  Table 5). The authors' comment: blending "might not be all you need".
- **The field's self-diagnosis.** "The Alpha Blending Hypothesis" (Yermakov et al., arXiv 2605.10334) claims that
  frame-level detectors are "alpha blending searchers". It was withdrawn on 4 Nov 2026 because training photos
  overlapped test sets. Cite the idea, not the numbers.

### 2.2 Reconstruction, anomaly and real-only formulations

- **RECCE** (Cao et al., CVPR 2022): reconstruct real faces only; the reconstruction difference guides the
  classifier.
- **SeeABLE** (Larue et al., ICCV 2023): one-class; local "soft discrepancies" on a face-part grid are mapped to
  fixed prototypes; trained on real faces only.
- **Real Appearance Modeling** (Tian et al., ECCV 2024): learn to restore real faces from slightly disturbed ones.
- **FSFM** (Wang et al., CVPR 2025): a face-specific foundation model pretrained on real faces with masked image
  modelling and instance discrimination; then fine-tuned for deepfake, spoofing and diffusion-face detection.
- **muFlow** (Pontorno et al., ECCV 2026): real-only, likelihood-based; uses the observation that averaging many
  images amplifies consistent generator traces.
- **AVH-Align** (Smeu et al., CVPR 2025): real-only training chosen because the fake classes of two audio-visual
  datasets carried a spurious cue (2.8 below).

### 2.3 Frequency-domain methods

- **F3-Net** (Qian et al., ECCV 2020): DCT-based decomposed components and local frequency statistics.
- **High-frequency noise features** (Luo et al., CVPR 2021): SRM high-pass filters at several depths; the argument
  is that detectors overfit to method-specific colour texture.
- **Spatial-phase shallow learning** (Liu et al., CVPR 2021): up-sampling in the generator changes the phase
  spectrum; feed the phase-only image as a fourth channel; keep the network shallow so that it cannot use
  semantics.
- **FreqBlender** (above).
- These methods read the generator's up-sampling or the spectral change of a blend.

### 2.4 Identity-consistency and face-recognition-feature methods

- **Face against context** (Nirkin et al., TPAMI 2022): one network for the face, one for hair, ears and neck; the
  disagreement of their identity outputs is the cue.
- **Identity Consistency Transformer** (Dong et al., CVPR 2022). A transformer at 112 pixels trained from scratch
  on about 10 million images of about 1 million persons, with swaps made from real images only. Two extra tokens
  give an inner and an outer identity vector; ArcFace loss on both; a consistency loss that pulls the inner vector
  of a swap to the outer vector of the reverse swap, applied only when both are classified correctly. Score at
  test: distance between the two vectors. Average AUC 87.01 over five sets; with a reference set of real
  identities 96.34 (their Table 1). Without the consistency loss: 51.48 on Celeb-DF v2 (their ablation). Robust to
  JPEG down to quality 20 (their Figure 5). Stated limit: reenactment, where identity does not change.
- **Implicit identity driven detection** (Huang et al., CVPR 2023): a swapped face has an explicit identity (what
  an FR network reads) and an implicit one (the target's); for a real face the two agree.
- **ID-Reveal** (Cozzolino et al., ICCV 2021) and **FACTOR** (Reiss et al., arXiv 2311.01458): compare the media
  with reference material or with a claimed identity. Trained on real data only. They need a reference or a claim.
- **DiffusionFake** (Sun et al., NeurIPS 2024): the detector's features must let a frozen Stable Diffusion
  reconstruct both the source and the target face of a fake; for a real image both targets are the image itself.
  A weight module is trained to predict the similarity of the fake to each of the two. No cost at inference.
  EfficientNet-B4 average cross-dataset AUC 75.80 to 81.88 (their Table 1). Stated limit: needs the source and
  target images in training; "multiple source identities" left for later study.
- **A caution from an independent benchmark** (Le et al., EuroS&P 2025, as reported by the authors' institution):
  ICT, trained on celebrity faces, was significantly less effective on non-celebrities.

### 2.5 Foundation-model adaptation (what leads the generalisation tables in 2025 and 2026)

- **Frozen CLIP with a linear probe or nearest neighbour** (Ojha et al., CVPR 2023, for generated images): a
  trained classifier makes the real class a "sink" for everything that lacks the trained fake pattern.
- **Effort** (Yan et al., arXiv 2411.15633): decompose each pretrained weight by SVD, freeze the principal part,
  train only the residual. Diagnosis: full fine-tuning collapses the feature space; effective rank 160 for the
  untouched model, 57 after full fine-tuning, 137 with LoRA, 159 with their method (their Table 8, face domain).
  Cross-dataset average AUC 0.917 with CLIP ViT-L/14 trained on FaceForensics++ (their Table 1).
- **Forensics Adapter** (Cui et al., CVPR 2025): CLIP frozen, a 5.7M-parameter adapter learns blending boundaries.
- **LN-tuning and GenD** (Yermakov et al., arXiv 2503.19683; WACV 2026, arXiv 2508.06248): tune only the layer
  normalisation parameters (0.03% of the model), L2-normalise the class token, add alignment and uniformity
  losses. Average AUROC over 14 benchmarks, all methods retrained on the same data: 91.2 (CLIP), 91.4 (Perception
  Encoder), 91.6 (DINOv3); Effort 88.5, Forensics Adapter 88.4 (their Table 4).
- **DF40** (Yan et al., NeurIPS 2024): CLIP beats all specialised detectors across protocols (their Finding 3).

### 2.6 Disentangling content, artefact and attribute

- **Content against artefact** (Liang et al., ECCV 2022): detectors use content more than artefact traces; two
  unbalanced datasets were built to measure it.
- **UCF** (Yan et al., ICCV 2023): split features into content, method-specific forgery and common forgery; a
  multi-class head names the method, the binary head sees only the common part.
- **ProDet** (Cheng et al., NeurIPS 2024). Observation: adding real deepfakes to blend-only training lowers
  cross-dataset AUC (0.807 to 0.781 average, their Table 2). Explanation: an unorganised latent space. Remedy:
  treat real, self-blend, cross-identity blend, deepfake as an ordered path. Three binary attribute heads: blending
  clue (present from the self-blend on), identity inconsistency (from the cross-identity blend on), generative
  artefact (deepfake only). The attribute outputs steer an attention map on the features. "Feature bridging" mixes
  the features of two adjacent anchors with a random ratio and mixes their labels. The authors argue that a
  one-hot multi-class label cannot give an order. Cross-dataset average 0.8225 against 0.7814 for SBI (their
  Table 1).
- **Latent-space augmentation** (Yan et al., CVPR 2024): augment in feature space, within and across forgery types.
- **ED4** (Cheng et al., arXiv 2408.06779): see 3.3.

### 2.7 Test-time adaptation

- **OST** (Chen et al., NeurIPS 2022). For each test image: pick a random template from the training set, blend it
  into the test image (hull mask, alpha or Poisson blending), label the result fake, take one gradient step on
  this pair, then classify the test image. Meta-learning prepares the network for that one step. Average AUC 0.854
  against 0.754 for the next method over twelve train and test combinations (their Table 1). The authors: "we are
  confident that the synthesized pseudo image is a forgery" whatever the test image is. Stated limit: not
  applicable when fakes are "totally synthesized by GAN-based methods".
- **T2A** (Nguyen-Le et al., IJCAI 2025): online, source-free adaptation over a stream for unknown
  post-processing; replaces entropy minimisation by an uncertainty-aware negative-learning loss.

### 2.8 What is deployed

- **Deepfake Detection Challenge, 2020.** All winners fine-tuned EfficientNet networks, most of them B7, in
  ensembles; augmentation by dropping face parts; some blended a real and a fake face and used the blend
  coefficient as the label. Best accuracy 82.56% on the public test set and 65.18% on the hidden one; public rank
  did not predict hidden rank (Meta AI report, 2020). No winner used forensic features such as sensor noise.
- **Microsoft Video Authenticator, 2020**: per-frame confidence from the blending boundary and subtle fading or
  greyscale elements; built on FaceForensics++, tested on the challenge data (press reports).
- **Intel FakeCatcher, 2022**: blood-flow signals from video. The 96% is a vendor figure; a BBC test reported
  false alarms on authentic videos and trouble with pixelated ones (press reports).
- **TrueMedia.org**: a service that ran many open detectors side by side and combined them; closed in January
  2025 and released its code.
- **Deepfake-Eval-2024** (Chandra et al., arXiv 2503.02857): on media that circulated in 2024, open detectors lose
  about 50% (video), 48% (audio) and 45% (image) of their AUC against earlier benchmarks; commercial detectors do
  better but stay below forensic analysts.
- Summary: practice is ensembles of pretrained classifiers plus many detectors side by side. The research state of
  the art for cross-dataset generalisation in 2026 is a CLIP-class encoder with a very small adaptation, trained
  on paired real and fake data, often with blend-based pseudo-fakes.

---

## 3. What the field learned about dataset shortcuts, and how it removed them

### 3.1 Resolution and compression

- **"Low resolution implies fake."** In DF40 the real training data have more high-frequency content than the
  fake training data. Detectors learn "higher resolution, higher probability to be real". On a sharp unseen fake
  set (StyleCLIP) AUC falls far below chance: 0.006 for Xception, 0.009 for another detector (Yan et al., their
  Table 5). Applying a super-resolution tool raises detection from 0.772 to 0.983 (their Table 8). This is our
  storage-history finding with the sign visible.
- **Compression removes the blend evidence.** Face X-ray: 87.35 to 61.6 under heavy compression. QAD (Le and Woo,
  ICCV 2023): one model, trained on several quality versions of the same image, with a loss that maximises the
  dependence between their representations; their bound says the error on low quality is the classification loss
  plus the distance between the high- and low-quality representations.
- **Preprocessing changes results.** DeepfakeBench (Yan et al., arXiv 2307.01426) exists because different
  pipelines fed detectors different inputs and comparisons were unfair. GenD reports reproduced numbers that
  differ from published ones (Effort on Celeb-DF v2: 93.2 reproduced, 95.6 reported; their Table 5). Our "own
  frames do not reproduce published numbers" is the same problem.

### 3.2 Identity

- **Implicit identity leakage** (Dong et al., CVPR 2023). A linear probe on the frozen features of binary
  detectors recognises identities, also on datasets never seen (their Figure 2). The part of the score that comes
  from the interaction of all image regions helps inside the training set and hurts across datasets: AUC of that
  part 81.5 to 99.6 on FaceForensics++, 44.4 to 49.5 on Celeb-DF, for five backbones (their Table 1). Remedy: an
  anchor-based module that decides on local windows, because "local areas usually do not reflect the identity",
  trained with multi-scale swaps of windows between a fake and its source.
- **Irregular swaps** (Trinh and Liu, IJCAI 2021). Swaps across gender or race make the detector tie the look of
  the face to "fake". Detectors trained on Face X-ray's blended images showed the strongest bias. Error-rate gaps
  between groups up to 10.7%.
- DF40 also suspects Xception of being "overfitted to ID".

### 3.3 Content, position, background

- **ED4** (Cheng et al., arXiv 2408.06779). Three biases: content (identity, background), specific forgery,
  spatial (the detector expects the forgery at the image centre). Remedy at data level. ClockMix splices sectors
  of up to four aligned faces around the face centre. The label rule: a composite is fake only if it contains a
  fake part; a composite of real faces is real. Without the real-with-real composites the cross-dataset average
  falls from 0.8195 to 0.6832, below the baseline 0.7512 (their Table VII). With real composites labelled fake it
  collapses to 0.54 to 0.61 (their Table IV). The evidence for the spatial bias is qualitative (attention maps).
- **Token shuffling and mixing** (Fu et al., arXiv 2501.04376): position and content bias; mixes tokens between
  two images of the same label.
- **Paired data** (Yermakov et al., WACV 2026). 20 training splits in which each fake shares the background video
  of a real, against 20 unpaired splits of the same size: mean test AUROC 90.0 against 85.3 over 14 benchmarks,
  higher on all 14 (their Table S1). The shortcut reading is the authors' interpretation.

### 3.4 Method fingerprints

- UCF and ProDet (2.6). **S3** (Wang et al., arXiv 2606.01843, June 2026): fit a linear probe that names the
  forgery method, take the top singular directions of its weights as the "method-sensitive subspace". Removing it
  keeps training-domain AUC and changes unseen-domain AUC strongly (their Figure 2b). Two remedies: project the
  gradients away from the subspace during training; scale down the neurons that are both decision-critical and
  method-sensitive at inference. Example: Xception trained on reenactment, tested on face editing, 0.3774 to
  0.9066 with the inference edit alone (their Table 1). The two remedies together are not additive (0.7636 in the
  same cell). Preprint, one dataset, single runs.

### 3.5 Evaluation

- **A high AUC hides a useless threshold.** GenD's supplement: mean AUROC 91.2, mean true-positive rate at 1%
  false positives about 49%, ranging from 10.9% to 92.3% across datasets (their Tables S4 to S7). The authors do
  not comment on it.
- **Hidden test sets reorder everything** (the Deepfake Detection Challenge, 2.8).
- **Train-test leakage sinks claims** (the withdrawn Alpha Blending paper).
- **Benchmarks that separate factors.** DF40 uses the same real data for 40 forgery methods and separate
  protocols for "new forgery", "new data domain" and both.
- **A spurious cue found by a blind baseline.** Smeu et al. (CVPR 2025): the leading silence alone separates real
  from fake in two audio-visual datasets.

### 3.6 The remedies, in one list

1. Make the fake from the real, in the same pipeline, and apply the same augmentation to both (SBI, GenD).
2. Label composites of real material as real (ED4).
3. Limit what the network can read: local windows (Dong et al.), a shallow network (Liu et al.), a frozen or
   nearly frozen encoder (Ojha et al., Effort, GenD).
4. Give the latent space an order of attributes instead of one "fake" class (ProDet), or split it (UCF).
5. Find the shortcut subspace with a probe and suppress it (S3). Tie representations of quality versions (QAD).
6. Train on real data only (SeeABLE, Real Appearance Modeling, muFlow, AVH-Align).
7. Evaluate on sets built to break the cue (DF40, Deepfake-Eval-2024).

None of these guarantees anything. Item 3 with a frozen encoder failed in our record (the frozen-encoder MADation
ViT-B/16 release also moves with storage history).

---

## 4. Has each technique family been used in morph attack detection?

| Family | Used in morph detection? | Reference, or the searches that found nothing |
|---|---|---|
| Blending-boundary map | Not as a boundary. Pixel-wise supervision with a constant map exists | PW-MAD, Damer et al., ISVC 2021, arXiv 2108.10291. Search "morphing attack detection Face X-ray OR blending boundary OR pixel-wise supervision": only PW-MAD |
| Partial morphs with region knowledge | Yes. The untouched part is the original photo | Seibold et al., J. Inf. Secur. Appl. 2020, arXiv 1806.04265. Search "morph localization pixel-level morphed regions partial morph dataset 2024 2025 2026": no dataset with masks found |
| Self-blending, one image, labelled attack | Yes | SelfMAD, Ivanovska et al., FG 2025, arXiv 2504.05504: cites SBI as "conceptually closest"; blending factor from {0.5, 0.5, 0.5, 0.375, 0.25, 0.125}; augmented copies (among them RandomDownScale or Sharpen) are genuine, blended ones are attacks; no resolution, compression or sharpness control described. FRLL-Morphs EER 0.99 / 0.00 / 0.00 / 10.34 / 3.45 for AMSL / FaceMorpher / OpenCV / StyleGAN2 / WebMorph (their Table I) |
| Same-person morph, two photos, labelled attack | Yes, as an augmentation | Kashiani et al., arXiv 2308.10392: "self-morphing" of two instances of one identity "enriches the diversity of morph attacks" (their Section 3.2) |
| Same-person morph labelled genuine | Yes, once | Pimenta et al., BIOSIG 2023, arXiv 2309.00549: "considering selfmorphs as bona fide samples" |
| Patch self-consistency and source features | Only as sensor noise | Debiasi et al., IWBF 2018 and BTAS 2018 (sensor pattern noise, its variance over image cells; the first version fails under histogram equalisation). No pairwise-consistency network found |
| Ordered attribute code along a ladder (ProDet) | Not found | Search "morphing attack detection ordinal OR progressive OR multi-label attributes same-identity morph OR self-morph negative class": SelfMAD and Kashiani only |
| Reconstruction, anomaly, real-only | Yes | MAD-DDPM, Ivanovska and Struc, IWBF 2023, arXiv 2306.15733; SRL-MAD, Paulo et al., arXiv 2603.15050; one-class Gaussian mixture on frozen features, Colbois and Marcel, IJCB 2024, arXiv 2410.16802 |
| Frequency, amplitude | Yes | FD-MAD, Paulo et al., arXiv 2601.20656 (deviation from a power-law spectrum; FRLL-Morph average EER 1.85%, MAD22 6.12%) and SRL-MAD |
| Frequency, phase | Not found | Search "morphing attack detection phase spectrum OR phase congruency OR amplitude normalisation": amplitude methods only |
| Inner against outer identity | Not found | Search "morphing attack detection identity consistency OR inner face outer face single image": nothing; a 2019 overview only notes that morphs can be made in the inner area alone (Scherhag, Frontex slides) |
| Two identity vectors in one network | Yes, without a one-person-blend control | OrthoMAD, Neto et al., arXiv 2208.07841; Caldeira et al., EUSIPCO 2023, arXiv 2306.03002. A kinship study uses FaceNet and ResNet50 embeddings, Srivastav et al., BMVC 2025 workshop |
| Demorphing as a detector | Not found | Search "single-image face demorphing used as morph detector reference-free": demorphing papers (Banerjee et al., IJCB 2022; Shukla and Ross, arXiv 2605.25442) treat detection as a separate task |
| Foundation-model adaptation | Yes | MADation, Caldeira et al., WACV 2025 workshops, arXiv 2501.03800 (CLIP with LoRA); R-FLoRA, arXiv 2604.17321; ViT features, Zhang et al., CVPR 2024 workshops, arXiv 2501.09817 |
| Subspace suppression, concept erasure | Not found | Search "morphing attack detection null space OR gradient projection OR subspace projection OR concept erasure": nothing in morph detection |
| Test-time training or adaptation | Not under this name | Search "test-time adaptation OR test-time training morphing attack detection": nothing. Closest: Di Domenico et al., FG 2026 (online learning in operation; synthetic morphs made on the fly from the current subject and an external identity; needs a stream) |
| Shortcut exposure (resolution, compression, identity leakage) | Not found for resolution or compression | Search "morphing attack detection identity leakage OR shortcut OR dataset bias OR spurious benchmark 2025 2026": demographic bias (arXiv 2111.12115) and remarks on "dataset-specific artifacts"; no audit |
| Deepfake detectors scored on morphs | Not found | Search "deepfake detectors evaluated on face morphing attacks SBI Face X-ray applied to morphs": nothing |

"Not found" means not found by these searches. It is not proof of absence.

---

## 5. Novel ways to solve our task that follow from this field

Each proposal names the signal, the control on the ladder, a first test of at most one day on existing data and
features, and a number that kills it. The limits for silence are the ones already registered for the alpha-field
probe (AF0): a shift of genuine scores of at most 0.3 standard deviations, and at most 10% of history-matched
genuine photos flagged at the threshold that flags 5% of native ones.

Known reference points on the landmark ladder (first passes, not reviewed): two-person head of the
paired-difference experiment (PD1), same-person morph against two-person morph 0.759 [0.683, 0.838], mirror
self-morph against two-person morph 0.694; one-person head 0.652 and 0.486. The alpha-field head (AF0) reaches
0.853 (FaceMorpher) and 0.830 (OpenCV) but moves warp-only images by 0.73 and 0.30 standard deviations.

### 5.1 A second-identity field whose complement is a one-person blend

**Source.** Face X-ray and Zhao et al. (a dense target that says where the second source is); ICT (each region
carries its own identity label); ED4 (composites of real material are real, and the detector must find the fake
sector, not the seam).

**The gap it closes.** Our alpha-field probe (AF0) contrasts a blended region with an unblended one. The blended
region is softer. The head learned softness and warp (the round-2 forensics review predicted it; AF0 shows it).
In the deepfake field the reference region is free: the outer face. A morph has none. So we build one, and we
make it equally blended.

**Construction (existing code only).** For a host photo H, a second photo H' of the same person and a partner P:

1. Run the alpha-field wrapper (`src/AF0/af_morph.py`, verified pixel-identical to the unchanged engine at a
   uniform 0.5) on the pair (H', P) with a spatial field a(x): a sector, a half, or one of the existing gradient
   and bump fields. Result Q: a second layer that is the same person where a = 0 and the other person where a = 1.
2. Run the unchanged morphing tool on (H, Q) at 0.5, with the mean of the two landmark files as landmarks of Q.

Every pixel of the result is a 50% blend of the host with a warped second layer. The two parts differ in one
thing: whose face the second layer is. Target map: a(x). Uniform images keep their labels: R0, R1, R2w, R3m, R3
are zero everywhere; R4 is one everywhere. The existing shrink-and-enlarge path is run unchanged on a random half
of the composites, after compositing, so both parts always share one history.

**A softness cross.** Two persons cancel more detail than two photos of one person, so inside one image the
two-person part can still be the softer part. The graded-mixing set breaks this: use a two-person part at mixing
fraction 0.25 to 0.3 against a one-person part at 0.5. Weights 0.75 and 0.25 keep 0.625 of the variance of
independent detail; weights 0.5 and 0.5 keep 0.5. In those images the one-person part is the softer one. Across
the training set local softness then does not predict the target.

**Network.** One network. A dense head on the patch tokens (as LAA-Net's heatmap branch and Forensics Adapter's
boundary head sit beside the classifier), trained with a per-patch loss plus the pairwise-consistency loss of Zhao
et al. The image score is the pooled field. No second network, no fusion.

**Why it cannot use our measured cues.** Storage history, border, capture detail and expression of the host are
identical in both parts of one image. Warp: both second layers are warped twice, the host layer once, in both
parts. Blending: both parts are 50% blends. Softness: crossed as above. Seam: composites with two one-person
parts (H' on one side, the mirror of H on the other) and with two two-person parts carry a seam and a constant
target. The ladder contrasts that show it: R0 to R1 and R0 to R2w must not move the pooled field; R3 against R4
must.

**First test (one day, CPU build plus cached-feature heads).** Build 2,000 composites from the landmark ladder
(AR1) hosts (each has a second photo and a partner), 5 folds by person, both engines; the wrapper built 1,165
images per minute at 6 processes. Extract DINOv3 patch tokens at 512 as in the alpha-field probe. Fit the ridge
patch head of that probe on the new target. Read on held-out persons, tool left out:

- within-image AUC, patches of the two-person part against patches of the one-person part;
- pooled score, R3 against R4 and R3m against R4;
- shifts R0 to R2w (both engines) and R0 to R1 (FRLL genuine photos with history);
- the same numbers on the softness-crossed composites alone.

**Pass.** Within-image AUC at least 0.75; R3 against R4 at least 0.85 with a lower bound above 0.80; both shifts
at most 0.3 standard deviations; history-matched genuine photos flagged at most 10%.
**Kill.** Within-image AUC below 0.60, or within-image AUC on the softness-crossed composites below 0.55 (then it
is reading local softness), or a warp-only shift above 0.5 standard deviations on either engine.

**State of the art.** Used as an auxiliary head inside the MADation recipe (CLIP with LoRA) on the rebuilt
training set. Published landmark cells contain two-person morphs against photos, where the two-person head
already reaches 0.98 to 0.99 on the ladder. Generator cells: the field is silent by design; the paper must say so.

**Risks.** Real morphs are uniform, so the head must work from absolute evidence at test time (the old critique
of the alpha field; the pooled R3 against R4 number is the direct check). The second layer is interpolated twice.
Step 2 needs landmarks for Q that were not detected on Q. The class of a composite is a ruling for the author: it
contains two persons in a part of the face.

### 5.2 A cumulative ladder code instead of one "morph" label

**Source.** ProDet (Cheng et al., NeurIPS 2024): real, self-blend, cross-identity blend, deepfake as an ordered
path with cumulative attribute bits; naive pooling of the fake kinds into one class lowered generalisation.

**Transfer.** Our rungs are that path. Train one network with three cumulative bits and one nuisance bit:

| Image | geometry moved | two captures superposed | second person | storage history (nuisance) |
|---|---|---|---|---|
| R0 | 0 | 0 | 0 | 0 |
| R1 | 0 | 0 | 0 | 1 |
| R2w | 1 | 0 | 0 | as built |
| R3m, R3 | 1 | 1 | 0 | as built |
| R4 | 1 | 1 | 1 | as built |
| graded mixing, fraction f | 1 | 1 | soft label rising with f | as built |

For generator ladders the first two bits read "is a render" and "two codes were mixed"; the third bit is shared.
The attack score is the third bit alone. The second bit is reported as "single-subject manipulation", which is
the class proposal now awaiting the author. Every rung is also present with history, so the history bit is
crossed with the other three.

Two elements of ProDet that our current heads lack. First, the bits are trained jointly and steer an attention
map over the features, so the network has to keep "a blend happened" and "a second person is there" apart.
Second, bridging between neighbours only: ProDet mixes features of adjacent anchors; we have real intermediate
images (six mixing levels for 300 hosts) and can mix features of R3 and R4 of the same host.

**Why it cannot use our measured cues.** One-person blends are explicit negatives of the attack bit, so "was
warped", "was blended" and "is softer than a photo" are all present at label 0. Storage history has its own bit
and is crossed. The ladder contrasts: the attack bit must separate R4 from R3 and from R3m, and must not move
from R0 to R1 or to R2w.

**First test (hours, cached features).** On the mean patch tokens (DINOv3 at 512, CLIP at 224) of the landmark
ladder: three logistic bits, 5 folds by person, one engine held out. On frozen features this is three probes;
the third is new: two-person morphs against all one-person rungs. Compare with the two-person head of the
paired-difference experiment (trained against warp-only images).

**Pass.** Third bit: R3 against R4 at least 0.85 and R3m against R4 at least 0.85, lower bounds above 0.80; R2w
against R4 stays at or above 0.95; shifts R0 to R1 and R0 to R2w at most 0.3 standard deviations; excess over the
best simple statistic for R3 against R4 at least 0.05.
**Kill.** R3 against R4 below 0.80 under direct supervision, or the excess over the best simple statistic below
0.05 (then "second person" is the cancellation statistic again), or more than 20% of history-matched genuine
photos flagged. On the GAN blocks report the third bit beside the 0.65 already measured; no kill number there,
because theory predicts a weak value.

**Second step (one LoRA fit).** Joint training with attribute-steered attention and neighbour bridging, against
a binary fit on the same images. It must lower the storage-history rise of the attack score by at least half at
no more than 2 points of native EER on the landmark cells.

**State of the art.** Same backbone and recipe as the comparator. Published tables are scored with the attack bit.

**Risks.** On frozen features the code adds nothing beyond its negatives; the gain, if any, appears only in the
adapted network. ProDet needs frame-aligned versions of one image; our rungs of one host have different shapes.
The third bit may be weak for look-alike pairs.

### 5.3 History-subspace surgery: first an audit of released detectors, then a training rule

**Source.** S3 (Wang et al., 2026): find the shortcut subspace with a probe, show by projection that the
benchmark number depends on it, then keep gradients out of it. QAD (Le and Woo, ICCV 2023): tie the
representations of quality versions of one image. Latent-space augmentation (Yan et al., CVPR 2024).

**Transfer.** Our subspace does not come from labels. It comes from interventions: the feature difference between
a genuine photo and the same photo with storage history (R1 minus R0), and between a photo and its warp-only
version (R2w minus R0). Take the leading directions of these paired differences at the layer before the head.

Step A, audit (new for morph detection). For each released detector whose features we can read, remove the
subspace from the features and leave the head untouched. Report, before and after: the share of history-matched
genuine photos flagged at the fixed threshold; the benchmark EER; R3 against R4. Three outcomes, each usable:

- flags fall, EER holds: the cue was not needed; a cheap repair exists;
- flags fall, EER rises strongly: the published number rested on the history subspace. This is causal evidence
  at feature level, beside the image-level interventions of the audit;
- flags do not fall for any small rank: the cue is not a low-rank linear direction at that layer.

Step B, training. In the LoRA fit, project the gradient at that layer away from the subspace (re-estimated every
epoch from a few hundred fixed photo pairs). A second arm randomises instead of removing: add sampled history
differences to the features of both classes. No pixel operation is created; only existing processed files are
used.

**Why it cannot use our measured cues.** By construction for the directions measured (history, warp). The check
is not the construction but the ladder: R0 to R1 on a second photo pool that was not used to estimate the
subspace.

**First test (one day, scoring and linear algebra).** Estimate the subspace on one photo pool (rank 1, 2, 4, 8,
16). Apply to the retrained MADation recipe and to our current heads. Evaluate on the other photo pool, on the
FRLL landmark cells and on the landmark ladder.

**Pass.** At some rank of at most 16 the flag rate of history-matched genuine photos falls by at least half and
native EER on the landmark cells rises by at most 2 points.
**Kill (for the training rule).** No rank up to 16 lowers the flag rate by at least a quarter. An EER rise above
5 points with falling flags does not kill the audit; it is the audit's finding.

**State of the art.** It is a rule on top of the main recipe, so tables are kept if the pass mark holds.

**Risks.** Linear at one layer; a LoRA fit can move the cue elsewhere (S3 reports that its two remedies do not
add up, with over-attenuation). Overlaps with the paired head with interventional nulling of round 1; new here
are the audit use on released detectors and the gradient rule that carries the nulling into LoRA training.

### 5.4 Identity-agreement slots with a retrieval test

**Source.** ICT (Dong et al., CVPR 2022): two identity vectors read from one image, a consistency loss, the
distance between them as the score; robust to degradation; collapses without the consistency loss. Huang et al.
(CVPR 2023): explicit against implicit identity. DiffusionFake (Sun et al., NeurIPS 2024): for a real image both
reconstruction targets are the image itself.

**Transfer.** This upgrades the two-contributor embedding head already in the plan (T5); it does not replace it
with something else. Three additions taken from ICT:

1. Consistent means "one person", not "unprocessed". For R0, R1, R2w, R3m and R3 both slots are pulled to the
   host's FR embedding. For R4 the two slots go to the two contributors' embeddings, in either order. One-person
   blends are thereby inside the consistent class. OrthoMAD and its successor have two identity vectors but no
   such class, so their vectors can follow the blend.
2. The score is the distance between the two slots. One network, one image, one number.
3. A falsifier that needs no detector: on held-out two-person morphs, rank the true partner among all held-out
   persons by the second slot. If the slots separate R3 from R4 but cannot find the partner, they are not reading
   identity.

**Why it cannot use our measured cues.** The targets are FR embeddings of the source photos. History, warp and
blending do not change them. The ladder contrasts: slot distance must rise from R3 to R4 and must not rise from
R0 to R1, R2w or R3m. The retrieval test shows what the distance is made of.

**First test (hours, cached features and existing ArcFace embeddings of the sources).** A two-slot head on the
patch tokens of the landmark ladder, 5 folds by person, one engine held out.

**Pass.** R3 against R4 at least 0.80; the true partner in the top 5 for at least 20% of held-out morphs among at
least 100 held-out persons (chance 5%); shifts R0 to R1 and R0 to R2w at most 0.3 standard deviations.
**Kill.** Partner in the top 5 for at most 10%, or R3 against R4 below 0.70.

**State of the art.** Needs a training set with many partners. On SMDD as released the second slot can learn five
faces; this is the identity leakage of Dong et al. in our setting. With the rebuilt set the slot distance is the
published score.

**Risks.** For generator morphs the image depends on the two persons only through the mixed code, so the slots
can at best read how average the face is. An identity reader can be bound to the population it was trained on
(the ICT result on non-celebrities). Low priority if the first two proposals pass.

### 5.5 Three diagnostics the field offers at almost no cost (not methods)

- **Identity probe** (Dong et al.): a linear probe for the five SMDD partner faces on the frozen features of each
  SMDD-trained detector. It belongs in the SMDD partner audit (SM1).
- **Threshold table** (after GenD's supplement and the Deepfake Detection Challenge): the detection rate at a
  fixed false-alarm rate per photo pool, beside every AUC and EER. This is the fixed-threshold re-read (EV1); the
  deepfake numbers (10.9% to 92.3% at one AUROC) are an external precedent to cite.
- **Label ablation** (after ED4's Tables IV and VII): the same recipe trained three times, with one-person blends
  labelled genuine, left out, and labelled attack. ED4's result predicts the order.

---

## 6. What does not transfer, and why

1. **The blending boundary.** Constant inside a full-face morph (section 1). Usable only for spliced morphs. A
   detector for one construction is a gate by another name.
2. **Self-blends as attacks.** The label is wrong under our rule, and the signal is "two layers" plus softness.
   SelfMAD is this transfer; its behaviour under storage history is in our record.
3. **Patch consistency and source features.** No contrast inside a uniform blend. Sensor-noise traces do not
   survive the shrink-and-enlarge history.
4. **Inner against outer identity.** Needs an untouched surround from one contributor. Tight crops remove it. It
   could serve as an audit probe for spliced-morph cells only.
5. **Frequency methods.** They read generator up-sampling or the spectral change of a blend. For us the first is
   the generator fingerprint, which a one-person reconstruction shares. The second is the softness floor. A
   phase-only or spectrum-flattened input does not help: a symmetric blur leaves phase alone, but storage at 63
   to 65 pixels removes the bands; flattening then amplifies residue, which is again a history cue. Only a hard
   band limit below what the stored-small images keep would be blind to history, and at that band the
   superposition is mostly gone.
6. **Reconstruction and real-only anomaly detection.** "Not like a camera photo" fires on R1, R2w and on one-photo
   reconstructions. Those are genuine under our rule. If they are put into the normal class, a two-person morph is
   barely anomalous (our 0.65 for the same-person mix against the two-person morph on GAN blocks).
7. **Test-time training on a pseudo-fake built from the test image (OST).** The references inherit whatever the
   test image contains. Blend the test image x with a template t. In an identity space with unit, unrelated
   identity vectors, the step from "x blended with itself" to "x blended with t" has squared length
   `0.25 (1 + |x|^2)`: 0.5 if x is one person, 0.375 if x is already a morph of two unrelated persons. The ratio
   of lengths is 0.87. That is the identity-shrinkage statistic again (0.725 on exact landmark shapes), measured
   with history-matched references. It cannot carry a detector. OST's authors also exclude fully synthesised
   images.
8. **Online test-time adaptation (T2A; in morph detection Di Domenico et al.).** Needs a stream. Not one image.
9. **Reference-based identity checks (ICT with a reference set, FACTOR, ID-Reveal).** They need a claimed
   identity or reference media. That is the differential setting.
10. **Video, temporal and physiological cues.** One still image.
11. **Ensembles and side-by-side detectors** (challenge winners, TrueMedia, the withdrawn 94.0% ensemble).
    Forbidden by our constraints.
12. **Identity-unaware design** (local anchors of Dong et al.). It removes identity, the one thing we want, and
    leaves local texture, where the softness cue lives. Its diagnostic transfers (5.5).
13. **Training only the residual subspace of the weights (Effort).** It steers learning toward what the
    pretrained model treats as minor detail. For us that is where the history cue is. The rank lesson stays: full
    fine-tuning collapses features.
14. **Everything blend-based, for generator morphs.** SBI reaches 69.11 on StyleGAN faces; 0.34 to 0.43 on
    entire-face synthesis in DF40. Face X-ray, Zhao et al. and OST state the same limit. Our StyleGAN3 and
    diffusion-autoencoder morphs are entire-face synthesis from a mixed code.

---

## 7. References

### 7.1 Verified during this task (title, first author, venue or year, URL)

Deepfake detection. "read" = read beyond the abstract.

1. Face X-ray for More General Face Forgery Detection. L. Li. CVPR 2020. https://arxiv.org/abs/1912.13458 (read)
2. Detecting Deepfakes with Self-Blended Images. K. Shiohara. CVPR 2022. https://arxiv.org/abs/2204.08376 (read)
3. Learning Self-Consistency for Deepfake Detection. T. Zhao. ICCV 2021. https://arxiv.org/abs/2012.09311 (read)
4. Can We Leave Deepfake Data Behind in Training Deepfake Detector? J. Cheng. NeurIPS 2024.
   https://arxiv.org/abs/2408.17052 (read)
5. Implicit Identity Leakage: The Stumbling Block to Improving Deepfake Detection Generalization. S. Dong. CVPR
   2023. https://arxiv.org/abs/2210.14457 (read, PDF text)
6. Protecting Celebrities from DeepFake with Identity Consistency Transformer. X. Dong. CVPR 2022.
   https://arxiv.org/abs/2203.01318 (read)
7. Effort: Orthogonal subspace decomposition for generalizable AI-generated image detection (title as on the
   arXiv page; venue not re-checked here, our planning record says ICML 2025). Z. Yan.
   https://arxiv.org/abs/2411.15633 (read)
8. ED4: Explicit Data-level Debiasing for Deepfake Detection. J. Cheng. arXiv 2024.
   https://arxiv.org/abs/2408.06779 (read)
9. Deepfake Detection that Generalizes Across Benchmarks. A. Yermakov. WACV 2026.
   https://arxiv.org/abs/2508.06248 (read)
10. OST: Improving Generalization of DeepFake Detection via One-Shot Test-Time Training. L. Chen. NeurIPS 2022.
    https://proceedings.neurips.cc/paper_files/paper/2022/hash/9bf0810a4a1597a36d27ceea58667d92-Abstract.html
    (read, PDF text)
11. DiffusionFake: Enhancing Generalization in Deepfake Detection via Guided Stable Diffusion. K. Sun. NeurIPS
    2024. https://arxiv.org/abs/2410.04372 (read)
12. DF40: Toward Next-Generation Deepfake Detection. Z. Yan. NeurIPS 2024, Datasets and Benchmarks.
    https://arxiv.org/abs/2406.13495 (read, first 100,000 characters of the page)
13. Suppressing Forgery-Specific Shortcuts for Generalizable Deepfake Detection. Y. Wang. arXiv, June 2026.
    https://arxiv.org/abs/2606.01843 (read)
14. UCF: Uncovering Common Features for Generalizable Deepfake Detection. Z. Yan. ICCV 2023.
    https://arxiv.org/abs/2304.13949
15. Exploring Disentangled Content Information for Face Forgery Detection. J. Liang. ECCV 2022.
    https://arxiv.org/abs/2207.09202
16. Exploring Unbiased Deepfake Detection via Token-Level Shuffling and Mixing. X. Fu. arXiv 2025 (a search
    listing gives AAAI 2025). https://arxiv.org/abs/2501.04376
17. Transcending Forgery Specificity with Latent Space Augmentation for Generalizable Deepfake Detection. Z. Yan.
    CVPR 2024. https://arxiv.org/abs/2311.11278
18. DeepFake Detection Based on Discrepancies Between Faces and their Context. Y. Nirkin. IEEE TPAMI 2022.
    https://arxiv.org/abs/2008.12262
19. Implicit Identity Driven Deepfake Face Swapping Detection. B. Huang. CVPR 2023.
    https://openaccess.thecvf.com/content/CVPR2023/papers/Huang_Implicit_Identity_Driven_Deepfake_Face_Swapping_Detection_CVPR_2023_paper.pdf
20. ID-Reveal: Identity-aware DeepFake Video Detection. D. Cozzolino. ICCV 2021.
    https://openaccess.thecvf.com/content/ICCV2021/html/Cozzolino_ID-Reveal_Identity-Aware_DeepFake_Video_Detection_ICCV_2021_paper.html
21. Detecting Deepfakes Without Seeing Any. T. Reiss. arXiv 2023. https://arxiv.org/abs/2311.01458
22. End-to-End Reconstruction-Classification Learning for Face Forgery Detection. J. Cao. CVPR 2022.
    https://openaccess.thecvf.com/content/CVPR2022/html/Cao_End-to-End_Reconstruction-Classification_Learning_for_Face_Forgery_Detection_CVPR_2022_paper.html
23. SeeABLE: Soft Discrepancies and Bounded Contrastive Learning for Exposing Deepfakes. N. Larue. ICCV 2023.
    https://arxiv.org/abs/2211.11296
24. Real Appearance Modeling for More General Deepfake Detection. J. Tian. ECCV 2024.
    https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/06913.pdf
25. muFlow: Leveraging Average Images for Improving Generalisation of Deepfake Faces Detectors. O. Pontorno. ECCV
    2026. https://arxiv.org/abs/2606.30528
26. FSFM: A Generalizable Face Security Foundation Model via Self-Supervised Facial Representation Learning. G.
    Wang. CVPR 2025. https://arxiv.org/abs/2412.12032
27. Thinking in Frequency: Face Forgery Detection by Mining Frequency-aware Clues. Y. Qian. ECCV 2020.
    https://www.ecva.net/papers/eccv_2020/papers_ECCV/html/1486_ECCV_2020_paper.php
28. Generalizing Face Forgery Detection with High-frequency Features. Y. Luo. CVPR 2021.
    https://arxiv.org/abs/2103.12376
29. Spatial-Phase Shallow Learning: Rethinking Face Forgery Detection in Frequency Domain. H. Liu. CVPR 2021.
    https://arxiv.org/abs/2103.01856
30. FreqBlender: Enhancing DeepFake Detection by Blending Frequency Knowledge. H. Li. NeurIPS 2024.
    https://arxiv.org/abs/2404.13872
31. LAA-Net: Localized Artifact Attention Network for Quality-Agnostic and Generalizable Deepfake Detection. D.
    Nguyen. CVPR 2024. https://arxiv.org/abs/2401.13856
32. Self-supervised Learning of Adversarial Example: Towards Good Generalizations for Deepfake Detection. L. Chen.
    CVPR 2022. https://arxiv.org/abs/2203.12208
33. Fake It till You Make It: Curricular Dynamic Forgery Augmentations towards General Deepfake Detection. Y. Lin.
    ECCV 2024. https://arxiv.org/abs/2409.14444
34. Forensics Adapter: Adapting CLIP for Generalizable Face Forgery Detection. X. Cui. CVPR 2025.
    https://arxiv.org/abs/2411.19715
35. Unlocking the Hidden Potential of CLIP in Generalizable Deepfake Detection. A. Yermakov. arXiv 2025.
    https://arxiv.org/abs/2503.19683
36. Towards Universal Fake Image Detectors that Generalize Across Generative Models. U. Ojha. CVPR 2023.
    https://arxiv.org/abs/2302.10174
37. Quality-Agnostic Deepfake Detection with Intra-model Collaborative Learning. B. M. Le. ICCV 2023.
    https://arxiv.org/abs/2309.05911
38. Think Twice Before Adaptation: Improving Adaptability of DeepFake Detection via Online Test-Time Adaptation.
    H.-H. Nguyen-Le. IJCAI 2025. https://arxiv.org/abs/2505.18787
39. An Examination of Fairness of AI Models for Deepfake Detection. L. Trinh. IJCAI 2021.
    https://arxiv.org/abs/2105.00558
40. Circumventing shortcuts in audio-visual deepfake detection datasets with unsupervised learning (title as in
    our planning record; the arXiv number and the finding were confirmed by search). S. Smeu. CVPR 2025.
    https://arxiv.org/abs/2412.00175
41. The Alpha Blending Hypothesis: Compositing Shortcut in Deepfake Detection. A. Yermakov. arXiv, May 2026;
    withdrawn 4 Nov 2026. https://arxiv.org/abs/2605.10334
42. DeepfakeBench: A Comprehensive Benchmark of Deepfake Detection. Z. Yan. arXiv 2023 (the page names no venue).
    https://arxiv.org/abs/2307.01426
43. SoK: Systematization and Benchmarking of Deepfake Detectors in a Unified Framework. B. M. Le. IEEE EuroS&P
    2025. https://arxiv.org/abs/2401.04364 ; institutional summary:
    https://www.csiro.au/en/news/All/News/2025/March/Research-reveals-major-vulnerabilities-in-deepfake-detectors
44. Deepfake-Eval-2024: A Multi-Modal In-the-Wild Benchmark of Deepfakes Circulated in 2024. N. A. Chandra. arXiv
    2025. https://arxiv.org/abs/2503.02857
45. FaceForensics++: Learning to Detect Manipulated Facial Images. A. Roessler. ICCV 2019.
    https://arxiv.org/abs/1901.08971
46. Deepfake Detection Challenge Results: An open initiative to advance AI. Meta AI, 2020.
    https://ai.meta.com/blog/deepfake-detection-challenge-results-an-open-initiative-to-advance-ai/
47. Microsoft launches a deepfake detector tool ahead of US election. TechCrunch, 2 Sep 2020.
    https://techcrunch.com/2020/09/02/microsoft-launches-a-deepfake-detector-tool-ahead-of-us-election/
48. BBC tests Intel "deepfake detector". Advanced Television, 24 Jul 2023.
    https://www.advanced-television.com/2023/07/24/bbc-tests-intel-deepfake-detector
49. TrueMedia.org open-source release note, 27 Jan 2025. https://www.truemedia.org/post/open-source-release

Morph attack detection.

50. SelfMAD: Enhancing Generalization and Robustness in Morphing Attack Detection via Self-Supervised Learning.
    M. Ivanovska. FG 2025. https://arxiv.org/abs/2504.05504 (read)
51. Towards Generalizable Morph Attack Detection with Consistency Regularization. H. Kashiani. arXiv 2023 (our
    planning record: IJCB 2023). https://arxiv.org/abs/2308.10392 (read, PDF text)
52. Impact of Image Context for Single Deep Learning Face Morphing Attack Detection. J. A. Pimenta. BIOSIG 2023.
    https://arxiv.org/abs/2309.00549
53. PW-MAD: Pixel-wise Supervision for Generalized Face Morphing Attack Detection. N. Damer. ISVC 2021.
    https://arxiv.org/abs/2108.10291
54. Accurate and Robust Neural Networks for Face Morphing Attack Detection. C. Seibold. J. Inf. Secur. Appl. 2020.
    https://arxiv.org/abs/1806.04265
55. PRNU-based Detection of Morphed Face Images. L. Debiasi. IWBF 2018.
    https://www.christoph-busch.de/files/Debiasi-PRNUMorphDetection-IWBF-2018.pdf
56. PRNU Variance Analysis for Morphed Face Image Detection. L. Debiasi. BTAS 2018.
    https://christoph-busch.de/files/Debiasi-PRNU-variance-MAD-BTAS-2018.pdf
57. Face Morphing Attack Detection with Denoising Diffusion Probabilistic Models. M. Ivanovska. IWBF 2023.
    https://arxiv.org/abs/2306.15733
58. SRL-MAD (structured residual Fourier representations, one-class). D. J. Paulo. arXiv, March 2026.
    https://arxiv.org/abs/2603.15050
59. FD-MAD: Frequency-Domain Residual Analysis for Face Morphing Attack Detection. D. J. Paulo. arXiv 2026.
    https://arxiv.org/abs/2601.20656
60. Evaluating the Effectiveness of Attack-Agnostic Features for Morphing Attack Detection. L. Colbois. IJCB 2024.
    https://arxiv.org/abs/2410.16802
61. OrthoMAD: Morphing Attack Detection Through Orthogonal Identity Disentanglement. P. C. Neto. arXiv 2022.
    https://arxiv.org/abs/2208.07841
62. Unveiling the Two-Faced Truth: Disentangling Morphed Identities for Face Morphing Detection. E. Caldeira.
    EUSIPCO 2023. https://arxiv.org/abs/2306.03002
63. MADation: Face Morphing Attack Detection with Foundation Models. E. Caldeira. WACV 2025 workshops.
    https://arxiv.org/abs/2501.03800
64. Quality-driven Adaptive Morphing Attack Detection in Operational Scenarios via Online Learning. Di Domenico.
    FG 2026. https://cris.unibo.it/handle/11585/1070891 (abstract only; the PDF returned an access error)
65. Identity in the Blood Relation: Unraveling the Complexity of Morph Detection in Kinship Biometrics. S.
    Srivastav. BMVC 2025 workshop.
    https://bmva-archive.org.uk/bmvc/2025/assets/workshops/PFATCV/Paper_3/paper.pdf
66. Generalized Single-Image-Based Morphing Attack Detection Using Deep Representations from Vision Transformer.
    H. Zhang. CVPR 2024 workshops. https://arxiv.org/abs/2501.09817
67. R-FLoRA: Residual-Statistic-Gated Low-Rank Adaptation for Single-Image Face Morphing Attack Detection. arXiv
    2026 (first author not read). https://arxiv.org/abs/2604.17321
68. Facial De-morphing: Extracting Component Faces from a Single Morph. S. Banerjee. IJCB 2022.
    https://arxiv.org/abs/2209.02933
69. Demorphing guided by multimodal language models (title not read in full). N. Shukla. arXiv 2026.
    https://arxiv.org/abs/2605.25442
70. Demographic bias of single-image morph detectors, a 2021 study (title not retrieved).
    https://arxiv.org/abs/2111.12115

### 7.2 Recalled, not verified in this task

These are named in the text or would belong in a full map, but I did not open a page for them here.

- SPL-MAD, unsupervised morph detection by self-paced anomaly detection (Fang et al., IJCB 2022). Seen only as a
  row in SelfMAD's Table I.
- Scherhag, Frontex 2019 slides on morphs restricted to the inner face area: seen as a search snippet only.
- Celeb-DF (Li et al., CVPR 2020) and the Deepfake Detection Challenge dataset paper (Dolhansky et al., 2020).
- Multi-attentional deepfake detection (Zhao et al., CVPR 2021); LipForensics (Haliassos et al., CVPR 2021);
  RealForensics (Haliassos et al., CVPR 2022); AltFreezing (Wang et al., CVPR 2023). Video and attention methods
  left out of the map.
- "Exploiting Facial Symmetry to Expose Deepfakes" (Li, Cao, Zhao, ICIP 2021): in our planning record as a
  snippet.
- The ICML 2025 venue of Effort and the IJCB 2023 venue of Kashiani et al.: from our planning record, not
  re-checked.
- Exact parameter values in the systems of section 2.8 beyond what the cited press reports state.
