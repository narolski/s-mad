# Independent check of the cross-field analysis on GAN-generated image detection

11 Nov 2026. Checker agent. Checked file: `literature/crossfield/gan.md`. Research and writing only: no
experiment, no GPU, no sealed file. Repository reads were limited to the brief, the consolidation of round 2,
the planning record, and the result files of five experiments named below.

**Abbreviations.** GAN = generative adversarial network. MAD = morphing attack detection; S-MAD = from a single
image. AUC = area under the ROC curve (0.5 = chance). EER = equal error rate. D-EER = detection equal error
rate. W, W+ = the latent spaces of StyleGAN (one code, or one code per layer). ψ (psi) = truncation factor.
SD = standard deviation. CI = 95% interval. JPEG, PNG, WEBP = file formats.

## 0. How this check was done, and its limits

- **References.** I opened 38 of the 71 references in the analysis's verified list: every reference behind
  the five ideas and behind the shortcut table. Pages were read through a page-reading tool, so any number
  that goes to print must still be checked against the PDF.
- **Searching was cut short.** One web search ran. Then the session's shared search budget was used up. All
  further work was done by opening pages at addresses I already knew (arXiv, code repositories, project
  pages). Consequences:
  - The "missed work" list (section 3) holds only works I recalled and then confirmed by opening the page.
    Works I recalled and could not open are in section 3.2.
  - I could not run new searches for "already done in morph detection". For that question this check rests on
    the analyst's searches, on the planning record (sections 3 and 10), and on pages I opened directly. Every
    "none found" below carries that limit.
- **Venues.** arXiv pages often do not show the venue. Where I could not see it, I say so. I have no reason to
  doubt those venues, but I did not confirm them.

## 1. Verdict in brief

1. **The reference list is sound.** No invented work was found. 37 of 38 opened references exist with the
   stated authors and say roughly what the analysis claims. One could not be opened (Pasquini et al.). Five
   statements about what a paper shows are wrong or too strong (section 2.2).
2. **The main argument holds, with two over-statements.** "A midpoint of two codes is, to second order, a
   truncated code" is correct algebra and is backed by the sources. But (a) "0.58 to 0.63 is the expected
   outcome of a correct control" is too strong: three of the four intervals exclude 0.5; (b) the proposed
   "step 0" does not bound what an image detector can do (section 4, idea 1).
3. **None of the five ideas raises a number in a published table by 14 Nov.** Four are audit experiments.
   One (idea 3) could reach the generator rows, but only by reading the generator, which is on our own list of
   cues, and only after the author's class ruling.
4. **Verdicts.** Idea 1 revise. Idea 2 revise (keep as one audit experiment, drop the training arm). Idea 3
   revise. Idea 4 revise (narrow to one reader and one new control). Idea 5 drop.
5. **One gap the analysis left open.** It applies the "wrong radius" argument only to StyleGAN. MorDIFF also
   mixes its semantic code by a straight average (verified in the MorDIFF paper). Our strongest "readable"
   numbers (0.945 to 1.000 on diffusion-autoencoder morphs) have no radius-matched control. This is cheap to
   check and is folded into the revised idea 1.

## 2. Reference verification

### 2.1 References opened (38)

"OK" = the work exists, the authors match, and the claim checked is on the page. Venue is marked only where a
page I opened showed it.

| # | Work | Checked claim | Result |
|---|---|---|---|
| 1 | Rajan, Ojha, Schloesser, Lee. Aligned Datasets Improve Detection of Latent Diffusion-Generated Images. https://arxiv.org/abs/2410.11835 | Figure 2 caption; Table 5 (54.16 → 83.58 real, 69.56 → 29.83 fake); limitations 9.59% and 25.87%; "10x" | OK. ICLR 2025 confirmed on the authors' code page (https://github.com/AniSundar18/AlignedForensics). Table 5 is the "Ojha-LDM" detector, images downsampled to 256 × 256. The 9.59 / 25.87 are detection rates on 1,950 FLUX.1-dev images |
| 2 | Guillaro, Zingarini, Usman, Sud, Cozzolino, Verdoliva. B-Free. https://arxiv.org/abs/2412.17671 | Tables 2 to 5; "careful dataset curation" quote; Figure 2 | Numbers OK (61.9 / 80.7 / 81.4; 68.5 vs 95.2; 65.0 → 83.2; 96.3, +20.7 over the second best). CVPR 2025 confirmed on the project page (https://grip-unina.github.io/B-Free/). **Figure 2 is misdescribed**, see 2.2 |
| 3 | Chen et al. Dual Data Alignment. https://arxiv.org/abs/2505.14359 | 90.7%, 15.7 points, worst 81.4%, 11 benchmarks (Table 2); 93% | OK. "NeurIPS 2025 Spotlight" is in the arXiv comments. The 93% is in the running text and refers to the SAFE detector, not to Figure 4 or 5. The text says DDA-COCO has five subsets; a results table shows six columns; the analysis says six |
| 4 | Agustsson, Sage, Timofte, Van Gool. Optimal transport maps for distribution preserving operations on latent spaces. https://arxiv.org/abs/1711.01970 | midpoint variance 1/2; fix by √2; "(strong) outliers" | Formula OK (variance factor 1 + 2t(t − 1), so 1/2 at the midpoint; rescaling restores it). "(strong) outlier" is in the appendix, for large dimension. The 100-dimension statement in the main text is "dramatically different, having almost no common support". Venue not shown on the pages I opened |
| 5 | Zhu, Abdal, Qin, Femiani, Wonka. Improved StyleGAN Embedding. https://arxiv.org/abs/2012.09036 | slope-5 inversion and whitening; 219 of 512; FID 76.63 / 3.28 / 2.81; "low-density portions"; Mahalanobis norm | OK. The FID numbers are in the text of Section 3, not in a table |
| 6 | Wulff, Torralba. Gaussianized Latent Space. https://arxiv.org/abs/2009.06529 | 89.9% user preference; sharper mean image, lower per-pixel SD | OK (Table 3, faces row; Section 4.1) |
| 7 | Karras, Laine, Aila. StyleGAN. https://arxiv.org/abs/1812.04948 | Figure 8 quote; ψ = 0.7 on 4² to 32²; Table 2; Figure 3 | Quotes OK. **Table 2 is misread**, see 2.2 |
| 8 | Karras et al. StyleGAN2. https://arxiv.org/abs/1912.04958 | Section 5 quotes on projection | OK |
| 9 | Kynkäänniemi et al. Improved Precision and Recall. https://arxiv.org/abs/1904.06991 | 500k paths, 2.4%, "highly convex"; truncation in Figure 5; Appendix C | OK. The 2.4% is in the text of Section 5.1; Figure 9 only shows four example paths |
| 10 | Grommelt, Weiss, Pfreundt, Keuper. Fake or JPEG? https://arxiv.org/abs/2403.17608 | Table 2 (80.45 → 100); Table 4 (+11.06, +11.74); size bias | Numbers OK. **Table 4 is attributed to the wrong remedy**, see 2.2 |
| 11 | Rajan, Lee. Stay-Positive. https://arxiv.org/abs/2502.07778 | WEBP = real; non-negative last layer; limits | OK |
| 12 | Colbois, Marcel. On the detection of morphing attacks generated by GANs. https://arxiv.org/abs/2209.00404 | Table 2: EER 0.00 / 0.56 / 0.00%; "strongly equivalent"; no fine-tuning | OK. BIOSIG 2022 in the arXiv comments. The released "Blur+JPEG(0.1)" weights were used unchanged. No one-person render control |
| 13 | Colbois, Marcel. Attack-Agnostic Features for MAD. https://arxiv.org/abs/2410.16802 | Table 7: DNADet 0.87 / 0.82 / 0.48 | OK, IJCB 2024 in the arXiv comments. **Quoted selectively**, see 2.2 |
| 14 | Zhang, Ramachandra, Raja, Busch. Generalized S-MAD using ViT representations. https://arxiv.org/abs/2501.09817 | "reconstructed bona fide images" quote; print-scan and compression on both classes | OK. The paper does not say which generator or inversion made the reconstructions, and has no latent radius control. Venue (CVPR Workshops 2024) not shown on the arXiv page; not confirmed |
| 15 | Tan et al. NPR. https://arxiv.org/abs/2312.10461 | 2 × 2 block differences; four ProGAN classes; weights public | OK. CVPR 2024 and the weights (`NPR.pth`, `model_epoch_last_3090.pth`) are confirmed on https://github.com/chuangchuangtan/NPR-DeepfakeDetection. The page states no licence |
| 16 | Yang, Huang, Cao, Li, Li. DNA-Det. https://arxiv.org/abs/2202.13843 | 170 transformation types on natural images; global and position-bound traces | OK. Venue not shown |
| 17 | Wang, Wang, Zhang, Owens, Efros. CNN-generated images are surprisingly easy to spot. https://arxiv.org/abs/1912.11035 | 83.6 → 74.9% after resizing (Appendix A.7); liquify at chance; DeepFake AP 98.2 vs 89.0 (Table 2) | OK |
| 18 | Ojha, Li, Lee. UnivFD. https://arxiv.org/abs/2302.10174 | Table 1: 3.05% of latent-diffusion fakes detected | OK |
| 19 | Gragnaniello, Cozzolino, Marra, Poggi, Verdoliva. Are GAN generated images easy to detect? https://arxiv.org/abs/2104.02617 | fixed-threshold quote; 2x downsampling "catastrophic" | OK. Authors confirmed. arXiv comments say only "conference" |
| 20 | Chai, Bau, Lim, Isola. What makes fake images detectable? https://arxiv.org/abs/2008.10588 | Table 5 on preprocessing; lossless saving; hair and background | OK |
| 21 | Sarkar, Korshunov, Colbois, Marcel. Are GAN-based Morphs Threatening Face Recognition? https://arxiv.org/abs/2205.02496 | W space; FaceNet 5.9% / 11.0%; "new identity" | OK |
| 22 | Damer et al. SMDD. https://arxiv.org/abs/2203.06691 | 500k renders, 2 × 250k, 50k kept by CR-FIQA(S); no ψ stated | OK |
| 23 | Reddy PN, Ramachandra, Rao, Mitra. MLSD-GAN. https://arxiv.org/abs/2404.12679 | spherical interpolation | OK |
| 24 | Ismayilov, Spreeuwers. SFDemorpher. https://arxiv.org/abs/2603.28322 | differential demorphing in StyleGAN latent space | OK ("joint StyleGAN latent and high-dimensional feature spaces") |
| 25 | Ren et al. Out-of-the-box benchmark. https://arxiv.org/abs/2602.07814 | 75.0% best, 37.5% worst, 20 to 60%, 18 to 30% | OK. Precisely: 16 methods in 23 pretrained variants |
| 26 | Chandra et al. Deepfake-Eval-2024. https://arxiv.org/abs/2503.02857 | image AUC down 45% | OK |
| 27 | Cozzolino, Poggi, Nießner, Verdoliva. ZED. https://arxiv.org/abs/2409.15875 | 90.0% average AUC, 30 test sets; limits; one threshold | OK. The margin over the best reference in AUC is 0.6 points (89.4) |
| 28 | Tov et al. e4e. https://arxiv.org/abs/2102.02766 and the code https://github.com/omertov/encoder4editing | encoder design | Exists. The design contradicts the "why shortcut-free" argument of idea 5, see section 4 |
| 29 | Pasquini et al. Applied Sciences 13(2):816. https://www.mdpi.com/2076-3417/13/2/816 | title, authors, content | **Could not be opened** (HTTP 403, twice). Not verified by me |
| 30 | Albright, McCloskey. Source Generator Attribution via Inversion. https://arxiv.org/abs/1905.02259 | exists, content | OK. Venue not shown |
| 31 | Li et al. SAFE. https://arxiv.org/abs/2408.06741 | crop instead of resize | OK, "KDD2025" in the arXiv comments |
| 32 | Zhang, Karaman, Chang. Detecting and Simulating Artifacts in GAN Fake Images. https://arxiv.org/abs/1907.06515 | simulator instead of real fakes | OK (extended version of the WIFS 2019 paper) |
| 33 | Liu, Yang, Bi, Xiao, Li, Gao. Detecting Generated Images by Real Images. ECCV 2022. https://www.ecva.net/papers/eccv_2022/papers_ECCV/html/5017_ECCV_2022_paper.php | "real-only training" | Exists. **Mischaracterised**, see 2.2 |
| 34 | Venkatesh et al. Can GAN Generated Morphs Threaten... https://arxiv.org/abs/2007.03621 | Table II: 0 to 0.68% against 1.57 to 15.42% | OK |
| 35 | Paulo, Proença, Neves. FD-MAD. https://arxiv.org/abs/2601.20656 | exists | OK |
| 36 | Paulo, Proença, Neves. SRL-MAD. https://arxiv.org/abs/2603.15050 | exists | OK, "Accepted at IWBF 2026" |
| 37 | Ramachandra. R-FLoRA. https://arxiv.org/abs/2604.17321 | exists | OK. Single author. Accepted at IEEE TIFS (arXiv comments). The analysis had it as "search result only"; it can move to the verified list |
| 38 | Zhang, Jia, Lyu, Li. Fusion-based Few-Shot MAD and Fingerprinting. https://arxiv.org/abs/2210.15510 | multi-class over morph tools | OK ("multiclass morphing attack fingerprinting", eight morphing algorithms in the database) |

Not opened by me: the other 33 entries of the analysis's list. They carry less weight. I make no statement
on them.

### 2.2 Errors found in what the analysis says a source shows

1. **Karras et al. 2019, Table 2.** The analysis: "90% gave the best FID when several codes are mixed at test
   time." The table: 90% is best with one code (4.40) and two codes (5.11 against 5.17). With three and four
   codes, 100% is best (6.63 and 8.40 against 6.88 and 9.03). The point the analysis needs (a crossover of two
   codes is something the discriminator was trained to accept) is not affected.
2. **Grommelt et al., Table 4.** The analysis gives the remedy as "train only on quality-96 images in both
   classes" with the result +11.06 and +11.74 points. Those gains come from training with **both** constraints:
   JPEG quality 96 only **and** real images limited to the generator's size range (Section 4.2). The paper has
   no ablation that separates the two. The JPEG-only effect is Table 3.
3. **B-Free, Figure 2.** The analysis: "the same generated images are called real or fake ... depending on
   which real photo collection they are paired with." The caption: the fakes of the two rows are generated
   from different source sets (RAISE, COCO) and each is tested against real images of its own set. What stays
   the same is the detector and the generator. The paper calls the three detectors "ViT-based"; that they use
   CLIP is stated in its supplement.
4. **Liu et al., ECCV 2022 (LNP).** Used twice as "real-only training" (family G, and source of idea 2). The
   authors' code page trains the final classifier with real and fake folders through the CNNDetection training
   code (https://github.com/Tangsenghenshou/Detecting-Generated-Images-by-Real-Images). Only the noise
   extractor is tied to real images. It is not a one-class method. The abstract does not claim one either.
5. **Colbois and Marcel 2024, Table 7.** The DNADet one-class row reads 0.87 / 0.82 / 0.48% on morphs built
   from FRGC **and 27.10 / 29.10 / 32.80% on morphs built from FFHQ**. The analysis quotes only the first
   half. The second half makes the analysis's own point stronger (the features read the source set, not
   morphing), but the row must be quoted whole.
6. **Agustsson et al.** "In 100 dimensions the midpoint norms are (strong) outliers" joins two passages:
   the 100-dimension statement in Section 2 and the "(strong) outlier" phrase of the appendix.
7. **Dual Data Alignment.** "About 93% (Figures 4 and 5)": the number is in the text and is for the SAFE
   detector. "Six autoencoders" for DDA-COCO: the text says five subsets.
8. **Kynkäänniemi et al.** "Figure 9 and text": the 2.4% is only in the text.

### 2.3 Unverifiable or unconfirmed

- Pasquini et al. 2023: page refused (HTTP 403).
- Venue not visible on any page I opened (not doubted, not confirmed): Agustsson et al. (ICLR 2019);
  Zhang et al. 2501.09817 (CVPR Workshops 2024); Albright and McCloskey (CVPR Workshops 2019); DNA-Det
  (AAAI 2022); Gragnaniello et al. (ICME 2021); and the entries the analysis itself marks "venue from memory".
- The analysis's statement that Zhang et al. "use GAN-reconstructed genuine images" is right, but the paper
  does not say how the reconstructions were made. "No radius control" should read "no generation detail given".

## 3. Work the analysis missed

### 3.1 Confirmed by opening the page

1. **Mandelli, Bestagini, Tubaro. When Synthetic Traces Hide Real Content: Analysis of Stable Diffusion Image
   Laundering.** arXiv 2407.10736, 2024. https://arxiv.org/abs/2407.10736. A real image passed through a
   generator's autoencoder is called synthetic by detectors. The authors build a two-stage detector that
   separates "pristine, laundered, and fully synthetic images". This is the field's closest precedent for our
   third class ("re-synthesised") and for idea 3. It is not in the analysis.
2. **NVIDIA and the SemaFor teams. StyleGAN3 Synthetic Image Detection.**
   https://github.com/NVlabs/stylegan3-detector. Seven detectors on StyleGAN3 faces, with a variant that adds
   random resizing and JPEG. Reported AUC 0.92 to 0.99. One detector trained only on ProGAN images reaches
   0.92. So the generator is still readable on StyleGAN3. Section 6 item 1 of the analysis ("StyleGAN3 was
   designed without aliasing") should not be read as "the generator trace is gone on our StyleGAN3 ladders".
   The page reports nothing per truncation level.
3. **Yang, Li, Qi, Lyu. Exposing GAN-synthesized Faces Using Landmark Locations.** arXiv 1904.00167, 2019.
   https://arxiv.org/abs/1904.00167. A support vector machine on landmark positions alone separates generated
   faces from real ones. With **Guo et al., irregular pupil shapes** (https://arxiv.org/abs/2109.00162) and
   **Hu, Li, Lyu, corneal highlights** (https://arxiv.org/abs/2009.11924) this is a whole family the map in
   section 1 leaves out: physical and anatomical consistency. For us the landmark paper is the field's version
   of our shape-typicality test (identity-shrinkage triage, experiment ID0). The eye cues are equal for a
   morph and a one-person render of the same generator, so they do not transfer; but the family belongs in
   the map and in "what does not transfer".
4. **Zheng et al. NoiseDiffusion.** ICLR 2024, arXiv 2403.08840. https://arxiv.org/abs/2403.08840. The
   diffusion counterpart of Agustsson et al.: latents of natural images do not follow the distribution the
   denoiser expects, and interpolating them gives artefacts. Together with the MorDIFF recipe (straight average
   of the semantic code, spherical interpolation of the noise code; verified in
   https://arxiv.org/abs/2302.01843) this carries the "wrong radius" question over to diffusion-autoencoder
   morphs. The analysis stops at StyleGAN.
5. **Mareen et al. TGIF.** IEEE WIFS 2024, arXiv 2407.11566. https://arxiv.org/abs/2407.11566. Spliced
   against fully regenerated inpainting. Generated-image detectors flag the regenerated images and cannot say
   what was changed; "both ... fail when exposed to stronger compression". Supports reporting "re-synthesised"
   apart from "manipulated".
6. **Pal et al. Semi-Truths.** NeurIPS 2024 Datasets and Benchmarks, arXiv 2411.07472.
   https://arxiv.org/abs/2411.07472. Real images with graded edits; detectors respond unevenly to the degree
   of the edit. This is the field's dose benchmark, the analogue of our graded-mixing rungs.
7. **Karageorgiou et al. SPAI.** CVPR 2025, arXiv 2411.19417. https://arxiv.org/abs/2411.19417. Models the
   spectrum of real images only and treats generated images as out of distribution, at any resolution. It
   belongs in family G. Like ZED it would formalise our softness cue.
8. **Li et al. AIGIBench.** NeurIPS 2025 Datasets and Benchmarks, arXiv 2505.12335.
   https://arxiv.org/abs/2505.12335. Eleven detectors under degradation and test-time preprocessing; common
   augmentation and preprocessing give "limited or inconsistent gains". A second 2025 source, beside Ren et
   al., for section 1.2.
9. **Konstantinidou, Koutlis, Papadopoulos. TextureCrop.** arXiv 2407.15500.
   https://arxiv.org/abs/2407.15500. Cropping textured regions instead of resizing or centre cropping. Same
   line as SAFE.
10. **Older forensic readers in morph detection.** The survey of Venkatesh, Ramachandra, Raja and Busch
    (arXiv 2011.02045, https://arxiv.org/abs/2011.02045, Table III and bibliography) lists: Makrushin et al.,
    VISAPP 2017 (Benford features of quantised DCT coefficients, a reader of JPEG history); Neubert,
    International Workshop on Digital Watermarking (image degradation analysis); Hildebrandt et al., IWBF 2017
    ("Application of StirTrace for impact simulation of different processing steps"). I verified these through
    the survey's bibliography, not through the papers. They matter twice: a processing-history reader applied
    to landmark morphs is **not** new (against idea 4's "none found"), and benchmarking morph detectors under
    processing steps has a 2017 precedent that the paper's audit half should cite.
11. **Medvedev, Shadmand, Gonçalves. MorDeephy.** arXiv 2208.03110. https://arxiv.org/abs/2208.03110.
    Single-image morph detection tied to a face-recognition classification task. The nearest morph detection
    work to "read identity from one image", missing from section 3 of the analysis.
12. Also relevant and already in our planning record, but not connected by the analysis to its "averageness"
    ideas: Fu and Damer, IET Biometrics (https://arxiv.org/abs/2208.05864), quality measures such as MagFace
    as an unsupervised morph signal.

### 3.2 Recalled, not verified (search budget exhausted or page refused)

- Mundra, Porcile, Mohanty, Farid, exposing GAN-generated profile photos from compact embeddings, CVPR
  Workshops 2023 (page refused, HTTP 403). As I recall it, StyleGAN faces share one fixed alignment, and a
  low-dimensional model of that regularity detects them: an alignment-frame cue in the field's own data.
- Nightingale and Farid, PNAS 2022, synthetic faces rated as more trustworthy, with averageness offered as a
  reason (page refused, HTTP 403).
- Spreeuwers et al., practical evaluation of face morphing attack detection methods (handbook chapter, 2022).
- Banerjee and Ross, single-image face demorphing (IJCB 2022).
- The University of Maryland "GAN-Scanner" inversion-based detector named on the NVIDIA page.
- Zheng et al., Breaking Semantic Artifacts (NeurIPS 2024); C2P-CLIP; D³; LaRE²; SIDBench.

## 4. The five ideas

Scores are 0 to 10 and deliberately low. "Feasibility" means: a decisive result by 14 Nov with the compute in
the brief.

### Idea 1. Radius-crossed generator ladder

**Already done in morph detection?** Not found. Closest: Zhang et al. (arXiv 2501.09817) put reconstructed
genuine images into the sets with GAN morphs; our own spread-matched render (the StyleGAN3 control pools,
experiment A37) is already further than any published control I know. Limit: no new search could be run.

**Check against measured facts.**
- Frozen-feature probe (experiment FZ1): morph against spread-matched render 0.615 [0.584, 0.645],
  0.632 [0.603, 0.661], 0.617 [0.587, 0.648], 0.583 [0.551, 0.616]. Three of four intervals exclude 0.5. The
  analysis calls this "the expected outcome of a correct control, not a lack of power". It is a small real
  remainder with an unknown cause. Both statements cannot be printed as they stand.
- Paired differences on GAN morphs (experiment PD1, first pass): same-person mix to two-person morph 0.65;
  a head trained on same-person mixes gives 0.58 on that step. So what is left beyond "two codes were mixed"
  is small. The best realistic outcome of idea 1 is a well-powered absence result. That has value for the
  audit, not for a table.
- A positive result would read "two codes were mixed". Under our class proposal a same-person mix is a
  single-subject manipulation. So even a pass does not give the contrast the ladder demands (two-person
  against same-person).

**Faults in the proposal.**
1. **Step 0 does not bound anything.** "No image detector can beat the best test on the exact code" is true.
   But step 0 is a logistic fit on a handful of summaries of 423 codes. That is a lower bound on what the code
   carries, not the best test. A low result would not show that an image detector cannot do better, so
   "print the limit and stop" is not justified. The analyst also expects a high result and declares a high
   result non-decisive. A first test whose expected outcome decides nothing should not be the first test.
2. **The Gaussian argument is about distributions; the control is built pair by pair.** The spread-matched
   render shares a contributor with its morph and matches one Euclidean radius. In a space that is not
   isotropic, direction and radius depend on each other, so equal radius does not make equal distributions.
   This is a sixth candidate cause beside the five in section 4.2 of the analysis, and it argues for matching
   per layer in whitened coordinates.
3. **Published GAN cells are not all midpoints.** MIPGAN optimises the code after averaging (our MIPGAN
   one-person controls, experiment AG1, record 150 optimisation steps with identity and perceptual losses).
   Radius must be measured on those cells, not assumed.

**Cheapest confound and its control.** Softness and other simple image properties, riding on a radius
mismatch that one scalar per code does not remove. Our record: truncated renders differ from plain renders in
simple image properties at 0.96. If the match is imperfect in some layers, a "mixing" head reads the same
sharpness and background cue. For the new arm (midpoint pushed back to full radius) the confound is the
generator's behaviour off its good region: stretched inverted codes give artefacts, and those are specific to
the "mixed" class. Controls: match the radius per layer around the mean of the set's own codes; report the
seven simple statistics on every contrast as the floor; keep the arm built from mapping-network samples, where
no inversion is involved; group folds by both contributors.

**Revised first test (zero GPU first).**
1. Re-read, one hour, CPU. From stored codes and stored probe scores of the 423 StyleGAN3 pairs and the 64 GAN
   blocks: (a) AUC of the 16 per-layer radii alone (set-mean centre) on morph against one-identity render;
   (b) the probe's remainder on morph against spread-matched render after the per-layer radii are regressed
   out, folds grouped by both contributors. Decision: if (a) is within 0.05 of the probe (0.89 to 0.94) and
   the interval of (b) includes 0.5, print "no trace beyond radius at n = 423" and stop. No new render needed.
2. Same re-read on the diffusion-autoencoder ladder, minutes. Radius of the generating semantic code for
   two-person morph, same-person mix and one-photo reconstruction at 20 steps. This contrast carries our
   strongest "readable" numbers (0.945 to 1.000) and has no radius control. Our identity-shrinkage triage
   (experiment ID0) found only 0.688 on that contrast with a statistic on re-encoded codes, so radius is
   probably not the whole story; but the exact-code check is missing and costs nothing. If radius alone
   reaches 0.90 or more, the sentence "frozen features read the mixing step" must become "read averageness",
   and a radius-matched one-photo reconstruction (decode only) should go into tonight's generation run.
3. Only if a remainder survives step 1: render the four arms from mapping-network samples (4 × 2,000) and run
   the probe. Pass and kill marks as the analyst set them (0.70 in both radius strata; 0.60).

**Verdict: revise.** Impact 4, feasibility 7, novelty 6.

### Idea 2. Truncation-dose training

**Already done in morph detection?** Not found. Closest: SelfMAD (arXiv 2504.05504; pseudo-morphs by pixel
blending) and the quality-as-signal line (Fu and Damer; "When Morphs Look Better", arXiv 2611.00074, in our
planning record), which read a morph's "better looking" face without training on truncation.

**Check against measured facts.**
- Consistent with the frozen-feature probe (0.89 to 0.94 falls to 0.58 to 0.63 against spread-matched
  renders) and with the release re-read (spread-matched 0.42 to 0.52).
- The record already warns: truncated renders differ in simple image properties at 0.96, "so this must not
  be read as 'the networks read typicality'". The same warning applies to a head trained on truncation.
- As a **training arm for our detector** the idea contradicts the ladder. By its own declaration the head
  cannot tell a two-person morph from a radius-matched one-person render, and it flags one-person renders.
  That is a detector of a single-subject property presented as morph evidence. It also fails as a route to
  the published generator rows, as the analysis itself says.
- "LNP" is not real-only training (section 2.2), so one of the three source techniques falls away. The idea
  does not depend on it.

**Cheapest confound and its control.** Softness and backdrop. Truncation toward the generator's mean code
also averages background, pose and lighting, and changes sharpness. A head trained on truncated against plain
renders can transfer to morphs through a smoother backdrop alone. Controls: fit the seven simple statistics
on the same training contrast and test them on the same morph contrast (the floor, trained the same way, not
fitted on the test contrast); repeat with everything outside the face box blanked in one constant colour in
both classes (allowed operation).

**Revised first test (under an hour, all images exist).** First read the generation record of the truncated
pools: centre, layers, base codes. Then fit the probe on ψ = 0.7 renders against plain renders, folds by
person. Report three numbers on held-out persons:
1. morph against one-identity render. Pass: at least 0.85 and within 0.05 of the morph-trained probe.
   Kill: below 0.75.
2. the simple-statistics floor trained and tested the same way. If the floor is within 0.03 of the probe,
   the reading is "simple image properties", not "averageness", and the row is printed with that wording.
3. morph against spread-matched render. Must be at most 0.60, else the head reads something other than radius.
Use: one audit row among the morph-free references ("a head that never saw a morph or a second person").
Drop the training arm and the "mixing-equivalent truncation" unit from the detector.

**Verdict: revise (audit experiment only).** Impact 3, feasibility 9, novelty 5.

### Idea 3. A declared "re-synthesised" output from aligned pairs

**Already done in morph detection?** Partly. Zhang et al. (arXiv 2501.09817) place reconstructions in the
genuine class and process both classes alike. Multi-class outputs over morph tools exist (Zhang, Jia, Lyu, Li,
arXiv 2210.15510). In the source field the three-way split exists: Mandelli et al. (pristine, laundered, fully
synthetic), which the analysis missed. A three-way morph detector with a same-photo aligned middle class: not
found (limit: no new search).

**Check against measured facts.**
- Camera photo to one-photo reconstruction is separable at 0.98, and the record says this step "contains
  frame, background and resolution changes besides the generator".
- The morph output, trained against reconstructions and same-person mixes, must do on GAN morphs what was
  measured at 0.65 (same-person mix to two-person morph) and 0.73 to 0.78 (reconstruction to morph). Under the
  policy "a reconstruction is genuine" the generator rows would stay far from the published numbers.
- Under the other policy the rows are reached through 1 − p(genuine), which reads the generator. "Generator
  fingerprint" is on the brief's list of cues. So the idea reaches the rows by a declared cue, not without
  one. That is an honest position, but it is not claim (b) of the paper.
- Fairness: our reconstructions come from the same generator families as the test cells. Published protocols
  do not train on them. Without a leave-one-generator-out result a reviewer will read the generator rows as
  trained on the test generator. The source field's own number is discouraging: 9.59% and 25.87% detection on
  a generator with a different autoencoder (Rajan et al., limitations).
- For diffusion morphs, morph against reconstruction at 100 steps is matched by Laplacian variance alone
  (0.966, morphs sharper). Only the matched 20-step contrast may train the morph output.

**Cheapest confound and its control.** Storage history and frame: the reconstruction is a 1024-pixel render
brought to our frame, the photo is a camera file of another size. A "re-synthesised" output can be a
resize-factor reader. Control: both members of a pair through one identical path from the shared 512 frame;
history-matched and stored-small photos in the genuine class at test; neither output may move by more than
0.3 SD from photo to history-matched copy.

**Revised first test (no training of the main network, half a day on cached features).** A three-way linear
probe on the cached features, folds by person:
1. photo against its history-matched copy on both outputs: shift at most 0.3 SD, flag rate at most 10% at the
   5% threshold;
2. leave one generator out: fit the middle output on StyleGAN3 reconstructions, test on diffusion-autoencoder
   reconstructions and on the MIPGAN one-person controls, and the reverse.
Pass: at least 0.90 across generators with (1) passing. Kill: below 0.75 across generators, or (1) failing.
After a kill the output reads one pipeline, the class cannot be offered, and the two-policy reporting stays as
decided in round 2. Needs the author's class ruling before any training run.

**Verdict: revise.** Impact 5, feasibility 4, novelty 3.

### Idea 4. Morph-free mechanism readers as instruments

**Already done in morph detection?** Largely yes. The ProGAN-trained classifier on GAN morphs, unchanged:
Colbois and Marcel 2022. DNADet features with a probe or a one-class model: Colbois and Marcel 2024.
Processing-history readers on landmark morphs: Makrushin et al. 2017, Neubert, Hildebrandt et al. 2017 (via
the survey, section 3.1 item 10). What is new is only the matched ladder and the one-person render control.

**Check against measured facts.**
- We already hold stronger evidence of the same kind: a file attribute separates all 17 cells perfectly. A
  further reader that separates a cell adds an outside witness, not a new fact.
- "No released detector separates a StyleGAN3 morph from a one-person render (best 0.61)" is already
  measured. The missing piece is the same statement on the **published** GAN cells for the detector that the
  literature credits with 0.00% EER.

**Fault in the proposal: the readers are not single-mechanism instruments.** The ProGAN-trained classifier and
NPR were trained against LSUN real images. Those were WEBP-compressed and then stored as PNG, and detectors
trained on them learned "WEBP = real" (Rajan and Lee, Section 3.1, cited by the analysis itself). The
classifier of Wang et al. was also trained with blur and JPEG augmentation. So a hit by such a reader does not
name a mechanism.

**Cheapest confound and its control.** Our own aligner. NPR reads differences inside 2 × 2 pixel blocks. Any
interpolation leaves such a pattern, and our aligner's resize factor depends on the source file size, which
differs by class in every cell. An NPR hit on a landmark cell would then read our preprocessing and the file
attribute (storage history and border), not an up-sampling step of the morph tool. Control: score native files
through the reader's own no-resize, no-crop path; require the photo against history-matched copy contrast on
the same path; print no mechanism word for a cell unless both agree.

**Revised first test (two hours).** One reader only: the released ProGAN-trained classifier of Wang et al., as
used by Colbois and Marcel.
1. Published GAN cells, camera photo against morph. Must reproduce their Table 2 within one point of EER.
2. Same cells, one-person control (MIPGAN one-person controls; one-photo reconstructions) against morph.
   Expected at most 0.60.
3. Photo against history-matched copy.
Useful if (1) reproduces and (2) is at most 0.60: then "the detector that wins the GAN cells without ever
seeing a morph is blind to morphing" is one sentence with two numbers. NPR and DNA-Det only if time is left,
on native files, and without mechanism claims. No licence is stated on the NPR page; check before use.

**Verdict: revise (narrowed).** Impact 3, feasibility 8, novelty 2.

### Idea 5. Inversion-encoder bottleneck

**Already done in morph detection?** Not found as stated. Closest: MorDeephy (single image, tied to face
recognition); quality and typicality scores (Fu and Damer; arXiv 2611.00074); our own identity-shrinkage
triage (experiment ID0).

**Check against measured facts. The idea fails on four of them.**
1. **The "discarded by construction" argument is wrong for this encoder.** In the e4e code one base code is
   computed from the coarsest feature map and copied to all 18 layers; each layer then adds a small offset,
   and training penalises the offsets (paper, delta regularisation; code, `Encoder4Editing.forward`). So the
   coarse and middle codes are mostly the base code, and the base code sees the whole image, softness
   included. Fine-layer content is not separated out.
2. **The nearest thing we have measured says the opposite.** The diffusion autoencoder's semantic code is
   also a 512-number code from an image encoder. In the identity-shrinkage triage its typicality statistic
   moved completely with storage history on the MorDIFF family (control AUC 0.000 [0.000, 0.000]). CLIP failed
   the control too. An encoder's code space is where storage history showed up, not where it "cannot reach".
3. **The pass mark sits inside the softness floor.** Pass is 0.75 for a two-person morph against its own
   warped halves. Laplacian variance alone gives 0.76 at 512 pixels and 0.87 at 224. The encoder's own input
   transform resizes every image to 256 × 256 (verified in the repository's `configs/transforms_config.py`).
   A pass could not be told from softness. That resize is also a resampling step inside the tool: it is
   allowed only as "tool run unchanged", and it is one more place where a file's size history enters.
4. **The pass mark sits above the shape ceiling.** Exact landmark shapes give 0.725 [0.689, 0.758] for photo
   against morph and 0.687 for warped half against morph. An encoder's estimate of shape cannot beat exact
   shape. So any pass would have to come from texture, which is the softness cue again.

**Cheapest confound and its control.** Softness, as above. Control: the photo blended with its own mirror
against the warped half must stay at or below 0.60 (blend softness and symmetry with no second identity); the
claim may only be carried by two-person against same-person morph, as excess over Laplacian variance on the
same pairs.

**If someone runs it anyway (two hours, GPU minutes).** Only that one contrast: two-person against same-person
morph on the landmark ladder, with the Laplacian-variance floor and the photo against history-matched copy
shift. Go on only if the excess over the floor has an interval above zero and the shift is at most 0.3 SD.
Expected: fails.

**Verdict: drop.** Impact 2, feasibility 6, novelty 5.

## 5. Summary table

| Idea | Verdict | Impact | Feasible by 14 Nov | Novelty | One-line reason |
|---|---|---|---|---|---|
| 1 Radius-crossed ladder | revise | 4 | 7 | 6 | Sound idea, unsound step 0; start with a zero-GPU re-read and add the diffusion ladder |
| 2 Truncation-dose | revise | 3 | 9 | 5 | A good one-hour audit row; as a training arm it contradicts the ladder |
| 3 "Re-synthesised" output | revise | 5 | 4 | 3 | Only route to generator rows, but by reading the generator; needs class ruling and a leave-one-generator-out test |
| 4 Mechanism readers | revise | 3 | 8 | 2 | Readers are mixed-cue; keep one reader and the one new control |
| 5 Inversion encoder | drop | 2 | 6 | 5 | Contradicted by the encoder's design and by our own measurements |

## 6. Corrections the lead should carry into any text built on the analysis

1. Do not print "0.58 to 0.63 is what theory predicts". Print the intervals; three exclude 0.5.
2. Do not print "our 0.89 to 0.94 is a truncation reading" as a fact. It is the leading explanation; the
   re-read in idea 1 tests it.
3. Do not present step 0 of idea 1 as an upper bound for image detectors.
4. Do not call NPR or the ProGAN-trained classifier "single-mechanism" readers.
5. Quote the DNADet row whole (0.87 / 0.82 / 0.48 on FRGC, 27.10 / 29.10 / 32.80 on FFHQ).
6. Fix the three misread sources (Karras Table 2, Grommelt Table 4, B-Free Figure 2) and the label on LNP.
7. Do not write "StyleGAN3 leaves no trace": seven detectors reach AUC 0.92 to 0.99 on it.
8. State that the "wrong radius" question is open for diffusion-autoencoder morphs as well.
