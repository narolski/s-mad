# Check of the cross-field analysis: face anti-spoofing

11 Nov 2026, evening. Independent check of `literature/crossfield/antispoof.md` (the analysis). Reading
and page fetches only. Nothing was run. No sealed file was opened.

Terms. FAS = face anti-spoofing. MAD = morphing attack detection; S-MAD = single-image MAD. BPCER = share
of genuine images called attacks. MACER = share of morphs accepted as genuine. ACER and HTER = mean of
the two error rates. AUC = area under the ROC curve. ECE = expected calibration error. LoRA = low-rank
adaptation. Ladder rungs as in `ideas/ROUND3_BRIEF.md`: R0 camera photo, R1 the same photo with storage
history, R2w warp only, R3m mirror self-blend, R3 same-person morph, R4 two-person morph.

Limit of this check. The web search budget of the session (shared by all agents) ran out after my first
query. Everything below rests on direct page fetches of known addresses, on full texts I converted from
the fetched PDFs, and on the repository's own records. I could not re-run the analyst's "not found in
morph detection" searches. Section 6 lists the queries that should be run when the budget is back.

---

## 0. Result in twelve lines

1. The reference list is sound. I opened 48 of the 57 numbered references. 46 exist, with the stated
   authors, and say what the analysis says. Two could not be opened ([24], [33]). I found no invented
   reference and no wrong number in the tables I re-read.
2. Seven points need correction (section 2). Most of them weaken the support for an idea or for its
   first test.
3. PatchNet tested its two changes separately as well. Fine classes alone, on resized faces, move the
   error from 6.25 to 5.63% (Table 4 of [7]). That is our input regime. The 6.25 to 1.88 figure is mostly
   the patch input.
4. GD-FAS does not show that group reweighting aligns the threshold. In its own ablation the group term
   makes calibration worse on all four splits once the other module is present (Table 3 of [22]).
5. The style line of the field removes or mixes statistics in shallow layers. Its source paper reports
   that doing so at the last block falls below the baseline (MixStyle, Table 3). Idea 1 does it at the
   last layer.
6. Our own record is cited wrongly in one place. The earlier consistency loss (experiment A49) was a full
   run (four arms, five seeds, 20.5 GPU-hours), not a trial with 16 to 90 pairs. It gave no gain.
7. One measured fact was not used by the analyst. The warp-only rung R2w is warped towards a same-person
   shape. Its warp is smaller than that of a two-person morph. Warp size alone predicted same-person
   against two-person at AUC 0.81 and 0.92 in an earlier loop. The lead registered the warp-matched rung
   (R2w4) tonight. Three of the four first tests use R2w and must switch.
8. Same-person morphs labelled genuine already exist in morph detection (five papers of one group, from
   MorDeephy on). The repository's class-definition note lists them. The analysis says "none found" for
   idea 3.
9. Verdicts: idea 1 revise; idea 2 revise; idea 3 drop as a detector design; idea 4 revise, as one more
   arm of an ablation that is already registered.
10. Order for the three days: the one-hour premise test of idea 1; the leave-one-strength-out test of
    idea 2; idea 4 only if the blend-evidence map is still alive.
11. The reporting practices of the analysis (its section 2.4) need no test and should be adopted as
    written. They are the most useful part of the page.
12. Important work the analysis missed: an asymmetric invariant-risk method with one shared radius
    (Nov 2025), a data-synthesis paper that found detectors rely on synthetic artefacts and equalises
    risk (2024), and the general forms of ideas 2, 3 and 4 in fairness, robustness and anomaly detection.

---

## 1. Reference check

"Full" = I read the method and result sections or the tables. "Abstract" = I opened the arXiv or
publisher page and checked title, authors, venue line and abstract.

### 1.1 References behind the four ideas and behind the shortcut findings

| Ref | Work | Level | Result |
|---|---|---|---|
| [4] | Feng et al., Learning Generalized Spoof Cues, arXiv 2005.03922 | full | Exists. SiW protocol 3: 1.19 ± 1.39% ACER against 12.10, 8.31 and 7.66 (Table 1). All-one target worse: 1.7 against 0.4% ACER (Table 5, OULU-NPU protocol 1). See correction C3. |
| [7] | Wang et al., PatchNet, CVPR 2022, arXiv 2203.14325 | full | Exists. Margins 0.4 and 0.1 (Table 5). Leave-one-out 7.10 / 11.33 / 13.4 / 11.82 (Table 8). Ablation misdescribed, see C1. |
| [12] | Jia et al., SSDG, arXiv 2004.14043 (CVPR 2020; no venue on the arXiv page) | full | 7.38 / 10.44 / 11.71 / 15.61 (Table 5); without the single-side part 11.19 (Table 1); symmetric baseline 9.52 (Table 2). Correct. |
| [15] | Wang et al., SSAN, CVPR 2022, arXiv 2203.05340 | full | SSAN-R 6.67 / 10.00 / 8.88 / 13.72 (Table 2). Correct. Note: the paper keeps the liveness-related part of the style; it does not remove style. |
| [16] | Sun et al., SA-FAS, CVPR 2023, arXiv 2303.13662 | full | 5.95 / 8.78 / 6.58 / 10.00 (Table 1); 14.36 on the first split over the last ten epochs (Table 2). Quote on resolution, blurriness and camera setting confirmed (section 3). |
| [17] | Zhou et al., IADG, CVPR 2023, arXiv 2304.05640 | full | 5.41 / 8.70 / 10.62 / 8.86 (Table 1). Ratios 0.3% and 0.06% confirmed. Style mixing within one class confirmed. See C4. |
| [22] | Jung et al., GD-FAS, ICCV 2025, arXiv 2507.04006 | full | HTER and ECE numbers correct (Tables 1 and 2). Reading too favourable, see C2. |
| [23] | Zhou et al., Test-Time Domain Generalization, CVPR 2024, arXiv 2403.19334 | full | Style = channel-wise mean and variance of a feature map (its Eq. 4). Projection on learned style bases, no model update. Correct. |
| [27] | Liu et al., CFPL-FAS, arXiv 2403.14333 (CVPR 2024; not on the arXiv page) | full | 3.09 on the first split, average 3.60 (Table 1 and text). Style prompt from mean and standard deviation. Correct. |
| [28] | Wang et al., TF-FAS, ECCV 2024 | full (PDF text) | Exists. 3.44 / 0.81 / 2.24 / 2.26, average 2.19 (Table 1), as listed in [22]. |
| [25] | Srivatsan et al., FLIP, ICCV 2023, arXiv 2309.16649 | full | 25.86 / 6.00 / 3.48 (Table 5); FLIP-MCL 4.95 / 0.54 / 4.25 / 2.31 with CelebA-Spoof (Table 2). Correct. |
| [29] | Ozgur et al., FoundPAD, WACV Workshops 2025, arXiv 2501.02892 | full | 9.67% is the triple-source average for ViT-L (Table 2). Zero-shot near chance (Table 1). Frozen 31.89 against adapted 16.81 (Table 5). Correct. |
| [30] | Ozgur, Boutros, Damer, Tomatoes, Potatoes, and Onions, ACM Multimedia 2026 Workshops, arXiv 2608.21455 | full | 78 vegetables; 14.15% HTER and 92.70% AUC; synthetic faces 27.56 and 81.02; ImageNet ViT 36.97 (Table 2). Threshold at the test set's EER. Correct. |
| [36] | Fang et al., Unified Physical-Digital Face Attack Detection, arXiv 2401.17699 | full | 1,800 subjects, 2 + 12 attack types, 29,706 videos; both quotes confirmed; 22.42 ± 10.57 (Table 3). No morphing attack. Venue (IJCAI 2024) is not on the arXiv page. |
| [37] | Yuan et al., challenge report, arXiv 2404.06211 | full | Threshold at the development EER; winner ResNet-50, moiré and self-blending, weight 5 to 1 in one protocol, ACER 2.3396%; second team down-sampled live faces in one protocol and attack faces in the other. Correct. |
| [39] | Costa-Pazo et al., GRAD-GPAD, ICB 2019, arXiv 1904.06213 | abstract | Exists; venue confirmed. Numbers not re-read. |
| [40] | Neto et al., Myope Models, WACV Workshops 2022, arXiv 2111.11127 | abstract | Quote on background confirmed. |
| [41] | Fang et al., Fairness in Face PAD, Pattern Recognition, arXiv 2209.09035 | full | 64 x 64 patch swap; four methods; the paper attributes the gap to identity cues and does not test it. Correct. |
| [44] | Ngan, Grother, Hom, NIST IR 8491, Sept 2023 | full | 82 algorithms, 45 developers, 21,218 genuine stills, 1,417 stills per zoom condition, both quotes, Tables 1 and 2 values, fusion, reference group at 0.03. Correct. |
| [45] | Sahidullah et al., arXiv 2601.17782 | full | Exists. arXiv comment: accepted at IEEE Journal of Selected Topics in Signal Processing. See C5. |
| [47] | Damer et al., PW-MAD, ISVC 2021, arXiv 2108.10291 | full | 17.74 against 34.67% (Table 3). Target values per pixel are not stated in the text. Correct. |
| [52] | Kashiani et al., IJCB 2023, arXiv 2308.10392 | full | Domain discriminator per feature level; consistency on outputs and features; style transfer; self-morphs from two photos of one person used as morphs. Correct. |
| [53] | Zhang, Jia, Lyu, Li, arXiv 2210.15510 | abstract | Exists. Multi-class head over morphing algorithms. |
| [56] | Paulo, Proença, Neves, SRL-MAD, IWBF 2026, arXiv 2603.15050 | full | Exists. Relevant to idea 1 in a way the analysis did not note (section 4.1). |
| [59] | Marriott, Robustness of MAD to compression, NIST IFPC 2025 | full (14 slides) | All four quotes confirmed. The detector is the vendor's own algorithm (idemia_004). |

### 1.2 Other references opened (abstract level; all exist with the stated first author and title)

[2] ICB 2019. [3] CVPR 2020; 0.2% ACER in the abstract. [5] ECCV 2020. [18] CVPR 2024. [19] see below.
[20] ECCV 2024; "quality as prior information" confirmed. [21] WACV 2025, pages 1005 to 1015.
[26] IEEE TIFS 2024. [31] CVPR 2019, 13 attack types. [32] exists; the arXiv page gives no venue.
[34] FG 2024. [35] arXiv 2025. [38] 2,875 identities, 54 attack kinds. [42] CVPR Workshops 2023,
25,000 genuine samples. [49] IJCB 2022. [50] IWBF 2023. [51] IJCB 2022. [54] IJCB 2024.
[55] WACV Workshops 2025. [57] FG 2025. [58] arXiv 2022.

### 1.3 Errors and references I could not verify

- [24] Huang et al., Test-Time Adaptation for Robust Face Anti-Spoofing, BMVC 2023. The address in the
  analysis redirects twice and ends in "404 not found". Not verified.
- [33] Huang et al., OC-SCMNet, CVPR 2024. The proceedings page answered "403 forbidden". Not verified.
  The analysis also had it at abstract level only. Idea 4 cites it as a secondary source.
- [19] Yang et al., arXiv 2407.08243. The analysis says "venue not confirmed". The arXiv comment says
  "Accepted by ECAI 2024".
- [45] is listed as "arXiv 2026". It is accepted at a journal (see table).
- Venues of [12], [27], [32], [36], [37] are not stated on the pages I opened. I did not check them
  elsewhere. They are probably right.
- Not opened by me: [6], [8], [9], [10], [11], [13], [14], [43], [48]. None of them carries an idea.

---

## 2. Claims corrected

**C1. PatchNet's ablation.** The analysis says the binary network on resized faces has 6.25% ACER and
the fine-class patch network 1.88%, "two changes tested together". Table 4 of [7] also has the two
single-change rows: binary classes with patch input 3.54%; fine classes with resized input 5.63%. So
naming the classes gives 6.25 to 5.63 on resized whole faces, and 3.54 to 1.88 on raw patches. Our
detectors take a resized whole face. The cleaner evidence for fine classes is Table 7 of [7]
(cross-domain): one live class plus one attack class per data set gives 10.24 / 15.67 / 21.65 / 16.26%
HTER; the fine split gives 7.10 / 11.33 / 14.6 / 11.82. That table was not cited. Side note: the third
value is 14.6 in Table 7 and 13.4 in Table 8 of the same paper.

**C2. GD-FAS and the aligned threshold.** The numbers quoted are right, but the comparison is selective.
(a) The same Table 2 lists FLIP-MCL, which has no threshold alignment, at ECE 3.94 / 1.45 / 2.62 / 5.45.
GD-FAS has 3.39 / 1.82 / 2.37 / 2.86. The large gap is to SA-FAS only, which uses another backbone.
(b) The paper's own ablation (Table 3) gives ECE 5.60 / 2.02 / 3.55 / 3.21 for the baseline,
4.70 / 2.02 / 1.58 / 2.61 with the group term alone, 1.60 / 1.00 / 1.48 / 2.38 with the orthogonal
decomposition alone, and 3.39 / 1.82 / 2.37 / 2.86 with both. Adding the group term to the decomposition
makes calibration worse on all four splits. The authors say so: the group term "primarily focuses on
improving generalization" and "using only FOD can significantly reduce ECE" (section 4.5). (c) Table 1
is captioned "Best results considered across epochs", so the leader numbers in the progress table of
the analysis are best-snapshot numbers. Consequence: [22] supports "the offset matters and should be
measured". It does not support "reweighting groups aligns the offset".

**C3. The one-sided cue map [4].** The analysis says attacks get "no map target" and a "ranking loss
between classes". The paper has three parts: the zero-map regression on live images, a triplet loss on
intermediate features, and an auxiliary classifier that receives the image with the cue map added. The
classifier is what pushes the map away from zero on attacks. Without it the error is 1.7% against 0.4%
(Table 5, rows 4 and 7). The statement "an all-one target was worse" rests on one pair of rows (1.7
against 0.4% ACER) on an intra-data-set protocol. The 1.19% on unseen attack types is compared with
numbers copied from three other papers with other networks.

**C4. The asymmetry evidence in IADG [17].** Asymmetric whitening against symmetric is 8.86 against
10.69% HTER on one split (Table 5), and the effect is not monotone (ratio 1:0.1 gives 9.86). The same
paper says MixStyle and shuffled style assembly "only yield limited improvements" in its setting. The
follow-up paper of the same first author lists IADG at 11.45 / 11.04 / 8.45 / 12.74 (Table 1 of [23]),
not at the 8.86 / 10.62 / 5.41 / 8.70 of the original. I do not know the reason. It is a caution on how
far these tables can carry an argument.

**C5. The voice study [45].** "EER moves from near 0% to above 50% when the association is inverted" is
true for MP3 coding and added noise with the simple model, and for noise with the neural model. For the
neural model the MP3 inversion gives about 36%, loudness normalisation stays below 10%, and mu-law
coding changes almost nothing (result table of the paper, read through an automatic page summary). The
effect depends on the intervention and on the model.

**C6. Our own record.** The analysis says "a small consistency loss and group weighting failed with 16
to 90 pairs". The planning record separates two things. The consistency loss (experiment A49) was a
DINOv3 adaptation with four arms and five seeds, 20.5 GPU-hours; its gain was +0.0029 [-0.0049, +0.0106],
which is none (`docs/PLANNING_RECORD.md`, sections 1 and 14). The "16 to 90 pairs" belong to the first
twin-trained heads (T0 in `NOTEBOOK.md`). `ideas/IDEAS_v1.md` mixes the two, and the analysis copied it.
So the earlier evidence against a consistency loss is a full run, not an underpowered one. What it
lacked is interventional pairs.

**C7. Controls already registered that the proposed tests ignore.**
- Idea 4 puts its kill mark on FaceMorpher. `ideas/CONSOLIDATED_v2.md` section 3 says FaceMorpher is
  descriptive only and the OpenCV-style engine and the approved Poisson set decide.
- Idea 4 asks for a map correlation of 0.2. The registered control is the correlation after removing the
  template, plus the pair-swap test.
- Ideas 1, 2 and 4 use "R2w against R4". R2w is the host warped to the mean shape of two photos of the
  same person (`experiments/AF0/result.md`, terms). The warp of R4 is larger. The record holds that warp
  size alone predicted same-person against two-person at 0.81 pooled and 0.92 on FERET
  (`docs/PLANNING_RECORD.md`, section 14.1). The lead registered the warp-matched rung R2w4 tonight
  (`experiments/AR1/prereg.md`, amendment 4). The alpha-field set also has "zero-field" images and warped
  halves with the two-person warp. These are the right negatives.

---

## 3. Important work the analysis missed

All opened in this check unless marked. None is a morph paper unless stated.

1. **Asymmetric invariant risk with one shared radius.** Lin et al., "Learning Representation and Synergy
   Invariances: A Provable Framework for Generalized Multimodal Face Anti-Spoofing", arXiv 2511.14157
   (Nov 2025). The classifier is a sphere. Live features lie inside, attacks outside. The radius is the
   only classifier parameter and is shared by all domains. Domain information is kept in the angles. The
   authors argue that symmetric invariant-risk methods such as SA-FAS suffer from the class asymmetry;
   the support is a bound, not an isolating experiment (as far as I read: the first 100,000 characters).
   This is the nearest published form of idea 2. https://arxiv.org/abs/2511.14157
2. **Synthetic artefacts become shortcuts; risk equalisation.** Cai et al., "Towards Data-Centric Face
   Anti-Spoofing: Improving Cross-domain Generalization via Physics-based Data Synthesis", IJCV 2024,
   arXiv 2409.03501. Attack artefacts are synthesised on images. The paper states that "models may rely
   on the augmented artifacts, which are not environment-invariant". Its remedy is a penalty on the
   variance of the attack-side risk across domains, with a contrastive loss on real faces only. Low
   resolution is used as a label-preserving change on both classes. It bears on SelfMAD-type training
   and on our softened examples. https://arxiv.org/abs/2409.03501
3. **Counterfactual intervention and class-guided statistic mixing.** Fang and Damer, "Face Presentation
   Attack Detection by Excavating Causal Clues and Adapting Embedding Statistics", WACV 2024, arXiv
   2308.14551. The analysis has it under "recalled". It is the in-field version of idea 1, variant b.
   https://arxiv.org/abs/2308.14551
4. **Where style statistics live.** Zhou et al., "Domain Generalization with MixStyle", ICLR 2021, arXiv
   2104.02008. The analysis has it under "recalled". The paper applies the mixing in the bottom layers.
   At the last block accuracy falls below the baseline: 79.5 to 75.6 on PACS, mean average precision
   19.3 to 10.2 on re-identification (Table 3). Reason given: the last block "tends to capture semantic
   content", and mixing there "breaks the inherent label space". https://arxiv.org/abs/2104.02008
5. **Normalising away statistics removes signal.** Jin et al., "Style Normalization and Restitution for
   Generalizable Person Re-identification", CVPR 2020, arXiv 2005.11037: instance normalisation
   "inevitably removes discriminative information"; a module puts the task-relevant part back. In the
   field itself: Liu et al., "Adaptive Normalized Representation Learning", ACM Multimedia 2021, arXiv
   2108.02667 (the analysis: "recalled"). https://arxiv.org/abs/2005.11037
6. **The general form of idea 4.** Liznerski et al., "Explainable Deep One-Class Classification" (FCDD),
   ICLR 2021, arXiv 2007.01760: a fully convolutional map is pulled to zero on normal images and pushed
   up on anomalous ones with image labels only; the map is the explanation. The authors report that such
   detectors use spurious features such as watermarks, and that about five ground-truth maps improve
   the result clearly. Ruff et al., "Deep Semi-Supervised Anomaly Detection", ICLR 2020, arXiv
   1906.02694, is the image-level form. https://arxiv.org/abs/2007.01760
7. **The general form of the offset term of idea 2.** Prost et al., "Toward a better trade-off between
   performance and fairness with kernel-based distribution matching" (MinDiff), arXiv 1910.11779. Xu et
   al., "Consistent Instance False Positive Improves Fairness in Face Recognition", CVPR 2021, arXiv
   2106.05519: a penalty that makes the false-positive rate at one unified threshold equal across
   instances. Both make the negative-class score distribution equal across groups so that one threshold
   holds. https://arxiv.org/abs/2106.05519
8. **The general form of idea 3.** Sohoni et al., "No Subclass Left Behind", NeurIPS 2020, arXiv
   2011.12945: hidden subclasses are used for worst-group training of a coarse classifier. They are not
   made output classes. https://arxiv.org/abs/2011.12945
9. **Reliability by per-sample confidence.** Long, Zhang, Shan, "Confidence Aware Learning for Reliable
   Face Anti-spoofing", arXiv 2411.01263. https://arxiv.org/abs/2411.01263
10. **Morph detection work that is in our own record but was not used.** (a) Same-person morphs
    ("selfmorphs") labelled genuine in a binary detector: Medvedev, Shadmand, Gonçalves, "MorDeephy",
    arXiv 2208.03110, section 4.3 ("we consider selfmorphs as bona fide samples"); follow-ups listed in
    `14_CLASS_DEFINITIONS.md`. Its own ablation is mixed (its Tables 1 and 2; read through an automatic
    page summary, numbers not re-read by me). (b) Pimenta, Medvedev, Gonçalves, "Impact of Image Context
    for Single Deep Learning Face Morphing Attack Detection", arXiv 2309.00549: how much context around
    the face the detector sees. It is the morph-side relative of the NIST zoom control. (c) Zhang et al.,
    arXiv 2501.09817: GAN-reconstructed genuine images added "to reduce the bias between bona fide and
    morph samples" (quote from the repository's class-definition check). (d) Paulo, Proença, Neves,
    FD-MAD, arXiv 2601.20656, and SRL-MAD [56]: a per-image residual spectrum (section 4.1).
11. **Content of cited papers that was missed**: the single-change rows of PatchNet (C1), the ablation
    of GD-FAS (C2), the auxiliary classifier in [4] (C3), and the statement in SSAN [15] that style holds
    "not only liveness-related information, but also domain-specific one" (its section 3.2).

Recalled, not verified in this check (no search possible): Hu et al., hyperbolic prototype refinement
for anti-spoofing (CVPR 2024); a 2024 prompt-tuning method that appears as the row "BUDoPT, ECCV 24" in
Table 1 of [22]; language-model-based anti-spoofing with captions (2025); unsupervised domain
generalisation for anti-spoofing (ICCV 2023); Wen et al., image distortion analysis (2015); Belrose et
al., LEACE (NeurIPS 2023); Sagawa et al., group DRO, and Krueger et al., V-REx (both in our literature
file from memory).

---

## 4. The four ideas

Scores are 0 to 10 and deliberately low. "Feasible" means: a result that can enter the paper by 14 Nov.

### 4.1 Idea 1. History as style: remove per-image token statistics before the head

**Verdict: revise.** Run a one-hour premise test first. Expect a kill.

Closest work in morph detection. Not token statistics, but the same move in the spectrum. SRL-MAD [56]
and FD-MAD (arXiv 2601.20656) subtract from each image's log-spectrum the power-law trend fitted to that
same image. SRL-MAD states that "this residual is obtained per-image and does not involve subtracting
statistics estimated from the training set". That removes the global spectral slope, which is where
uniform softness sits. Neither paper tests benign processing of genuine images. Kashiani et al. [52]
transfer image styles. I could not re-run a search for token-statistic removal in morph detection.

Check against measured facts.
- The premise needs blending to be less uniform than storage history. The record says a two-person
  morph has 0.52 times the Laplacian variance of its own warped halves. That is close to what plain
  averaging of two uncorrelated fine-detail fields gives everywhere in the face. So the largest part of
  the blending trace is uniform too, and standardisation removes it together with the history. The
  analysis says so under "risk"; it is the main issue, not a side risk.
- A blur and an average both make textured patches look more like flat patches. The part of each that
  survives a per-image shift and rescale is of the same kind.
- The guarantee holds only for frozen tokens. In a LoRA fit the layers before the normalisation can
  write a global property into the spatial pattern. The field does not rely on the layer alone either:
  SSAN and IADG add losses on style-changed views.
- The field's evidence is for shallow layers (MixStyle, section 3, item 4). Idea 1 standardises the last
  layer, where the statistics carry the label.
- Step B as written cannot work with the present head. A linear patch scorer on per-image centred tokens
  has the same mean in every image. It cannot fit the constant target of a uniform morph. With top-tenth
  pooling its image score is roughly 1.75 times the spread of the patch scores (the forensics reviewer
  noted the same factor), which is a quadratic form in the token correlations of the image. Those
  second-order statistics are what IADG [17] treats as style. So the read-out moves to another style
  statistic.
- Variant b (swap statistics within a class) does not break a link between class and history. In
  anti-spoofing each data set holds both classes, so within-class mixing crosses domains. In our data the
  shortcut separates the classes (the analysis says this itself in its part 5, point 4). Within-class
  swaps leave it in place.

Cheapest confound and control. (a) Warp size: R2w has a same-person warp, R4 a two-person warp; local
warp traces are not uniform, survive standardisation and are untouched by history. A head can pass both
pass marks on warp alone. Control: R2w4 or the zero-field image against the morph of the same pair.
(b) Softness of the averaging kind: control is softened warp-matched negatives against R4, read as
excess over the Laplacian-variance AUC of the same contrast, plus R3 and R3m against R4.

Sharper first test.
- Step A' (one hour, cached DINOv3 tokens, face-hull patches). Measure two paired changes in the same
  way. History: FRLL photo to its history-matched frame, and ladder host to its softened copy (both
  registered strengths). Blending: zero-field image to the uniform-0.5 morph of the same pair (identical
  warp, alpha-field set). For each pair report the share of the token change that a per-image,
  per-channel shift and rescale explains. Premise holds if the share is at least 0.8 for history on both
  pools and at least 0.2 lower for blending. KILL if the two shares differ by less than 0.2. Then
  standardisation removes signal and nuisance alike, and the idea ends there.
- Step B (half a day, only after A'). A small non-linear patch scorer trained through the top-tenth
  pooling with image labels (two-person morph against photos, warped halves and softened copies), next
  to the identical scorer on raw tokens. Decide on the OpenCV-style engine and the Poisson set. PASS: at
  most 10% of history-matched FRLL photos flagged at the 5% threshold; R2w4 against R4 at least 0.90;
  softened warped halves against R4 at least 0.05 above the Laplacian-variance AUC of that contrast; R3
  against R4 not more than 0.02 below the raw-token scorer. KILL: the softened contrast is within 0.05
  of its Laplacian floor, or more than 10% are flagged.

Scores: impact 3, feasible 5, novelty 5. Reason: cheap and falsifiable in an hour, and Step A' is an
informative measurement whatever its outcome. As a network component it has no guarantee and by design
throws away the strongest landmark cue.

### 4.2 Idea 2. One-threshold training: align the genuine side only, and align the offset

**Verdict: revise.** Keep the read-out without any test. Test the loss with a left-out history strength.

Closest work in morph detection. Kashiani et al. [52]: symmetric consistency with discriminators. NIST
FATE MORPH reports false detections per photo pool at one threshold (our record). Marriott [59] fixes a
threshold and retrains on compressed images. The planning record (section 11) holds an earlier search
with no morph paper on invariant risk or group-robust training. I could not repeat it. Outside morph
detection the idea is published in parts: live-only alignment [12], asymmetric shared radius (section 3,
item 1), risk equalisation with a real-only contrastive term (item 2), equal false-positive rate across
groups at one threshold (item 7).

Check against measured facts.
- It fits the measured failure: a moved genuine score at a fixed threshold.
- The data-only route already brought flagged shrunk photos from 19 to 40% down to 4 to 8% (record). The
  pass mark "at most 10%" is therefore close to met without any loss term.
- A consistency loss already failed in a full run (C6). The cited source for offset alignment does not
  show that the loss term helps calibration (C2). So the expected gain over the data arm is small.
- Softness is also the real trace of a landmark morph (0.52). A genuine side that is invariant to
  softness costs detection. The proposed test sets no limit on the rise of MACER.

Cheapest confound and control. Storage history seen in training. The softened copies use the two
registered strengths, which are the family medians of FRLL-Morphs AMSL and of MAD22 FaceMorpher
(`experiments/AF0/result.md`, wave 4). The test frames on FRLL are built by the same path at family
medians. A head can learn two strengths by heart and pass. Control: leave one strength out. Second
confound: capture detail between photo pools moves the genuine level; the offset term cannot align a
pool it never saw. Control: hold one pool out with at least three genuine pools in training (FEI and
FFHQ photos can serve as genuine-only pools), and check that morphs made from a genuine-only pool with
the unchanged tools do not score lower than other morphs.

Sharper first test (one day, CPU, cached pooled CLIP and DINOv3 features).
- Use a two-layer head, not a linear one, so that the loss is not the known projection. Three fixed
  seeds, mean reported, no selection.
- Heads on identical images: (1) data only, with softened genuine copies of ONE strength as negatives;
  (2) plus the per-host term; (3) plus the offset term. Negatives of the warp kind are R2w4 or
  zero-field images.
- Threshold at 5% of native training-pool photos. Read BPCER on the LEFT-OUT strength (held-out hosts),
  on the FRLL history-matched frames per family and on FRLL native photos; MACER on FRLL two-person
  morphs at the same threshold; softened warp-matched negatives against R4. Repeat with the strengths
  exchanged.
- PASS: on the left-out strength BPCER at most 10% and at most half that of head 1, in both directions,
  with MACER not more than 2 points above head 1. If head 1 is already at or below 10%, stop: the data
  arm is enough and no loss is needed. KILL: no halving on the left-out strength. Then the terms only
  fit seen strengths.
- Only after a pass: one LoRA arm with the terms next to the planned data arm.

Scores: impact 5, feasible 6, novelty 3. Reason: it plugs into the paper's chain and the read-out is
needed in any case. The loss terms are a recombination of published parts with weak evidence of gain.

### 4.3 Idea 3. Name the nuisance: a classifier over ladder rungs

**Verdict: drop as a detector design.** Keep the negatives. Keep a multinomial probe only as a diagnostic
if someone has a spare half day.

Closest work in morph detection. MorDeephy (arXiv 2208.03110) and four follow-ups of the same group
label same-person morphs as genuine in a binary detector, in order to "focus morphing detection onto
the deep face features behaviour, rather than to detecting artefacts". MorDeephy's own ablation is
mixed. Kashiani et al. [52] and SelfMAD [57] label such images as attacks. Zhang et al. (arXiv
2501.09817) add reconstructed genuine images. Zhang et al. [53] name the morphing tool. So hard
negatives of this kind exist. What is new here is only the softmax over named rungs.

Check against measured facts.
- The source evidence is weaker than quoted (C1): 6.25 to 5.63% on resized faces.
- The claim "a binary head has only one place to put softness evidence" does not hold once softened
  genuine copies are negatives. The baseline of the proposed test already has them.
- The defining contrast, same-person against two-person, is where our signal is weakest and most
  confounded. Warp size alone gave 0.81 and 0.92. On GAN ladders the step is 0.65, and a head trained
  only on one-person mixes ranks two-person morphs as well as a head trained on them (0.78 against
  0.77). A head that never saw a same-person morph reaches 0.853 and 0.830 on the large pool but 0.948
  and 0.932 on FRLL (`experiments/AF0/result.md`). A gap of 0.10 between pools points to capture
  conditions, not identity.
- "Every host appears in every class" equalises the host. It does not equalise the partner. In R3 the
  partner is another photo of the same person, often from the same session, with the same backdrop,
  light and clothing. In R4 it is another person's photo.
- The class list needs a ruling the author has not made. A softmax score at a fixed threshold depends on
  the class shares in training.

Cheapest confound and control. Warp size, and the session match of the two contributors. Control: read
same-person against two-person inside thirds of landmark displacement; blank everything outside the face
hull with a constant colour; report the AUC of landmark displacement alone and of Laplacian variance
alone for the same contrast.

Test that would have to pass before the idea is taken up again (half a day, CPU, cached features).
Binary head and six-way head on identical images. PASS: within displacement thirds and with the surround
blanked, same-person against two-person exceeds the better of the two single-cue AUCs by at least 0.05
on both engines, and the six-way head beats the binary head by at least 0.02 there. KILL: either fails.

Scores: impact 2, feasible 6, novelty 2. Reason: on frozen features it will be close to the binary head
with the same negatives, and a pass on the raw contrast would not be believed.

### 4.4 Idea 4. One-sided zero map

**Verdict: revise.** Add it as a sixth arm to the registered five-arm ablation of the alpha-field probe
(AF0). Do not run it as a separate experiment.

Closest work in morph detection. PW-MAD [47] (two-sided, constant maps). One-class detectors [49][50]
[56]. The exact loss form is FCDD (section 3, item 6), outside morph detection. I could not re-run a
search for a one-sided map in morph detection.

Check against measured facts.
- Removing the positive template does not remove the objection of the round-2 review. A global flag
  (energy everywhere on any averaged image) satisfies the zero targets and the hinge. The analysis says
  the head "has little reason to localise". FCDD's authors report the same kind of map reading spurious
  features.
- Softened copies as zero targets do not close the softness route. Softness from shrink-and-enlarge and
  softness from averaging differ in the spectrum. The head can learn to call the first zero and the
  second energy. The zero targets that close it are averaged images with one identity: the mirror
  self-blend and the same-person morph. They are not in the proposal. With them the map reads a second
  identity, which is the brief's requirement; without them it reads blending.
- The kill mark sits on FaceMorpher, which is descriptive only (C7).

Cheapest confound and control. Type of softness plus an anatomy pattern (energy rises on textured
regions of any averaged image, and the true field is also larger there). Control: correlation after
removing the template and the pair-swap test, both already registered; warp-matched zero targets (warped
halves, zero-field images); R3m and R3 against R4 read next to the measured-map arm.

Sharper first test (CPU, after tokens; one arm added to the registered ablation).
- Arm (f): absolute-value loss to zero on photos, warped halves and their softened copies; hinge on the
  top-tenth map energy of a morph over its own warped half. A second variant adds R3m and R3 as zero
  targets.
- PASS on the OpenCV-style engine and the Poisson set: correlation with the true field after template
  removal at least 0.2 on gradient and bump images, with the pair-swap lower bound above 0.10; at most
  10% of softened halves flagged at the 5% threshold; morph against softened half at least 0.05 above
  the Laplacian-variance AUC of that contrast.
- KILL: template-removed correlation below 0.2, or arm (f) not better than the image-label arm with
  halves as negatives on any registered read-out. Then it is the image-level classifier under another
  name.

Scores: impact 3, feasible 7, novelty 3. Reason: almost free as one more arm, but it repairs a component
that is no longer the headline, and its loss form is published.

---

## 5. What stands without any test

The eight practices in section 2.4 of the analysis are supported by the sources I re-read: threshold
fixed on declared genuine development images [37][44]; BPCER per pool and per history at that threshold
[44]; both fixed-point summaries [44]; every identity in both classes [36]; last-epoch reporting [16];
no threshold that depends on file size [59]. Two additions from this check:

1. Report every history read-out on a strength that was not in training (section 4.2).
2. Next to every AUC against a processed negative, print the AUC of Laplacian variance alone and, for
   same-person against two-person, of landmark displacement alone. This is already the rule for the
   alpha-field probe; it should hold for every head.

One wording point for the paper. The vegetables result [30] is scored at the test set's own EER
threshold and only its pretrained backbone carries it (36.97% HTER from ImageNet weights). It shows
that recapture traces transfer. It does not show a fixed-threshold result.

---

## 6. Searches to run when the budget is back

1. "morphing attack detection" with "instance normalization", "feature statistics", "MixStyle", "AdaIN".
2. "morphing attack detection" with "single-side", "bona fide only" alignment, "asymmetric" loss.
3. "morphing attack detection" with "calibration", "threshold", "false positive rate" and "group".
4. "morphing attack detection" with "selfmorph", "three-class", "multi-class", "bona fide subclass".
5. "morphing attack detection" with "anomaly map", "one-class" and "pixel-wise" in one query.
6. Face anti-spoofing 2025 to 2026 with "shortcut", "spurious", "dataset bias", "resolution bias".

---

## 7. Sources opened in this check, beyond the reference list of the analysis

- Lin et al., Learning Representation and Synergy Invariances, arXiv 2025. https://arxiv.org/abs/2511.14157
- Cai et al., Towards Data-Centric Face Anti-Spoofing, IJCV 2024. https://arxiv.org/abs/2409.03501
- Fang, Damer, Excavating Causal Clues and Adapting Embedding Statistics, WACV 2024. https://arxiv.org/abs/2308.14551
- Liu et al., Adaptive Normalized Representation Learning, ACM Multimedia 2021. https://arxiv.org/abs/2108.02667
- Zhou et al., Domain Generalization with MixStyle, ICLR 2021. https://arxiv.org/abs/2104.02008
- Jin et al., Style Normalization and Restitution, CVPR 2020. https://arxiv.org/abs/2005.11037
- Liznerski et al., Explainable Deep One-Class Classification, ICLR 2021. https://arxiv.org/abs/2007.01760
- Ruff et al., Deep Semi-Supervised Anomaly Detection, ICLR 2020. https://arxiv.org/abs/1906.02694
- Prost et al., kernel-based distribution matching (MinDiff), arXiv 2019. https://arxiv.org/abs/1910.11779
- Xu et al., Consistent Instance False Positive Improves Fairness in Face Recognition, CVPR 2021. https://arxiv.org/abs/2106.05519
- Sohoni et al., No Subclass Left Behind, NeurIPS 2020. https://arxiv.org/abs/2011.12945
- Long, Zhang, Shan, Confidence Aware Learning for Reliable Face Anti-spoofing, arXiv 2024. https://arxiv.org/abs/2411.01263
- Medvedev, Shadmand, Gonçalves, MorDeephy, arXiv 2022. https://arxiv.org/abs/2208.03110
- Medvedev, Gonçalves, MorphGuard, arXiv 2025 (a face recognition training method; abstract only). https://arxiv.org/abs/2505.10497
- Pimenta, Medvedev, Gonçalves, Impact of Image Context for Single Deep Learning Face MAD, arXiv 2023. https://arxiv.org/abs/2309.00549
- Zhang, Ramachandra, Raja, Busch, Generalized Single-Image-Based MAD Using Deep Representations from Vision Transformer, arXiv 2025. https://arxiv.org/abs/2501.09817
- Paulo, Proença, Neves, FD-MAD, arXiv 2026. https://arxiv.org/abs/2601.20656
- Shahreza et al., Foundation and Multimodal Large Language Models for Face Presentation and Morph Attack Detection, arXiv 2026 (abstract only). https://arxiv.org/abs/2608.29802
