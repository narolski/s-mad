# Cross-field analysis: face anti-spoofing, and what it gives single-image morph detection

11 Nov 2026. Written by the analyst for one neighbouring field, on the author's request to study the
solutions of neighbouring detection fields and derive new ways to solve our task. Research and writing
only: nothing below has been run. Numbers from our own record are quoted from
`ideas/ROUND3_BRIEF.md` and from the result page of the alpha-field probe (AF0); those from today are
owners' first numbers, not reviewed.

Terms. Face anti-spoofing (FAS) and presentation attack detection (PAD) are two names for one task:
decide from camera images whether a real face is in front of the camera or an artefact (a print, a
screen replay, a mask). The genuine class is called "bona fide" or "live". Morphing attack detection
(MAD) shares this vocabulary. Error rates (ISO/IEC 30107-3): APCER is the share of attacks accepted as
bona fide; BPCER is the share of bona fide images called attacks; ACER is their mean. HTER (half total
error rate) is the same mean, usually at a threshold chosen elsewhere. EER is the error where both rates
are equal. AUC is the area under the ROC curve. In MAD the attack-side rate is called MACER.

Source rule. Every numbered reference was found during this task (search result or fetched page), with
its URL in part 6. "Read" means I read the method and result sections, not only the abstract. Numbers
are quoted with their table. Works I remember but did not find are in the last list and are not used as
evidence.

---

## 0. The page in twelve lines

1. Anti-spoofing met our problem years before us. By 2019 its own evaluation papers showed that
   detectors with near-zero error inside one data set failed on the next [39]. The field named the
   causes: resolution, blur, camera, session, background, identity [16][25][39][36].
2. Its first cure was "make features equal across data sets" (2019). It did not hold. Three later
   corrections matter for us.
3. Correction one, asymmetry: only the bona fide class is pulled together across domains. Attacks are
   left spread out [12][17][7].
4. Correction two, alignment not invariance: keep the domain information in the features, but force the
   bona-fide-to-attack direction to be the same in every domain [16]. A 2025 paper adds that the offset
   (the threshold) must be aligned too, or one threshold does not hold [22].
5. Correction three, style: domain shift lives largely in per-image feature statistics (channel mean and
   spread). Methods shuffle, whiten or project these statistics [15][17][23][27].
6. Since 2023 the benchmark leaders are CLIP image encoders with light adaptation [25][27][22]. The same
   recipe is MADation in morph detection.
7. The strongest shortcut finding is from 2026: a detector trained on print and replay recordings of
   tomatoes, potatoes and onions reaches 92.70% mean AUC on four face benchmarks [30]. The face is
   incidental. The detectors read the recapture process.
8. The operational view (NIST, 82 algorithms) reports errors at fixed thresholds on 21,218 sequestered
   bona fide stills, and includes a matched control: print and replay attacks with and without the
   visible frame and hands (1,417 stills each). Errors rise for all algorithms when that context is
   removed [44].
9. Morph detection has borrowed pixel-wise supervision, one-class models, CLIP with low-rank adaptation,
   and once an adversarial consistency scheme. I found no morph paper with the asymmetric treatment, with
   threshold alignment, with feature-statistic (style) removal, or with processed-genuine sub-classes.
10. Four proposals follow (part 4): strip per-image token statistics so that storage history cannot
    reach the head; genuine-side-only score alignment with an aligned threshold; a classifier over
    ladder rungs where "two-person morph" is one class among named nuisance classes; a one-sided
    zero-map loss as a repair of the blend-evidence map.
11. What does not transfer: everything temporal or physical (pulse, depth, moiré), test-time model
    updates, fusion, quality-conditioned thresholds, and the habit of scoring at the test set's own
    threshold (part 5).
12. One industry talk already shows fixed-threshold false alarms of a morph detector rising under
    compression, and that a file-size-dependent threshold does not repair it [59]. Our audit claim must
    be worded with that in view.

---

## 1. Map of the field's solutions, 2019 to 2026

Grouped by the idea behind them. The field's survey [9] (abstract level) covers the first, second and
fourth group: pixel-wise supervision, domain generalisation, unseen attacks. "Leave-one-out" below means the standard cross-domain protocol: four data sets (OULU-NPU, CASIA, Idiap
Replay-Attack, MSU-MFSD; letters O, C, I, M), train on three, test on the fourth.

### 1.1 Auxiliary supervision: give the network a dense target that an attack cannot fake

- Idea. A binary label lets the network use any cue. A dense target ties it to physical evidence. For a
  live face the target is a face-shaped depth map; for a flat print or screen it is zero. Later variants
  add a reflection map or a plain per-pixel label.
- Works. Pseudo-depth supervision started this line [1]. George and Marcel replaced the depth map by a
  per-pixel binary label, arguing that depth synthesis is unnecessary because the task is not depth
  estimation [2]. Central difference convolution (CDCN) builds gradient-like filters into the network
  and reports 0.2% ACER on OULU-NPU protocol 1 [3]. CelebA-Spoof (625,537 images, 10,177 subjects, 43
  attributes) argues that rich annotations as auxiliary tasks help more than binary labels [5]. Spoof
  trace disentanglement writes an attack as "live image plus trace" and recovers both [6].
- The one-sided variant (read). "Learning Generalized Spoof Cues" [4] regresses a cue map to all-zero
  for live images only. Attack images get no map target. The paper reports that regressing attacks to an
  all-one map was worse. The test score is the mean magnitude of the map. On the unseen-attack-type
  protocol of SiW (protocol 3) it reports 1.19% ACER against 7.66 to 12.10% for three earlier methods
  (its Table 1).
- Patch variants (read). PatchNet [7] crops fixed-size patches from the raw capture and never resizes
  the face, "to avoid the distortion of discriminative FAS cues". It replaces the two classes by
  fine-grained classes, one per capture device and presentation material, several of them live classes
  (CASIA: three live, six attack). Margins are asymmetric: 0.4 for live classes, 0.1 for attack classes.
  On OULU-NPU protocol 1 a binary network on resized faces has 6.25% ACER and the fine-class patch
  network 1.88% (two changes tested together). Shuffled patch-wise supervision builds training images
  from patches of different subjects and labels each patch [8].
- Status. This family dominated intra-data-set results until about 2021. It is what small deployed
  models still use. An open-source example is the Minivision "Silent Face" model with a Fourier-spectrum
  auxiliary loss (seen only through secondary pages; see part 6).

### 1.2 Domain generalisation: train on several data sets so that a new one works

- Symmetric invariance (2019). MADDG trains one feature space that several domain discriminators cannot
  tell apart, for both classes [10]. Meta-learning variants simulate the domain shift inside training
  [11]. Leave-one-out HTER of MADDG: 17.69 / 24.50 / 22.19 / 27.89% (as listed in Table 5 of [12]).
- Asymmetric treatment (2020, read). Single-side domain generalisation (SSDG) [12] argues that live
  faces differ little between data sets while attacks differ a lot, so forcing attacks of all data sets
  into one cluster hurts. Only live features go through the domain discriminator. A triplet loss treats
  the attacks of each data set as separate classes and all live faces as one class. Features and
  classifier weights are length-normalised; the stated purpose is to reduce the effect of image-quality
  differences between data sets.
  Leave-one-out HTER: 7.38 / 10.44 / 11.71 / 15.61% (Table 5). Removing the single-side adversarial part
  raises the first from 7.38 to 11.19% (Table 1). The symmetric baseline has 9.52% (Table 2).
- Suppress named nuisance factors. One method trains several adversarial heads, one per
  spoof-irrelevant factor such as camera and illumination [13]. Another removes camera-specific
  variation in a high-frequency branch [14].
- Style (2022 to 2024, read). The shuffled style assembly network (SSAN) [15] splits a representation
  into content (batch-normalised path) and style (instance-normalised path). It swaps styles between
  samples and uses a contrastive loss so that liveness-related style is kept and domain-specific style
  is suppressed. Instance-aware domain generalisation (IADG) [17] drops domain labels altogether. It
  whitens the feature correlations that change most under a style change, per instance, and does it
  asymmetrically: the selection ratio is 0.3% for live and 0.06% for attack features. Its style
  augmentation mixes feature statistics only within a class. Leave-one-out HTER: SSAN 6.67 / 10.00 /
  8.88 / 13.72% (Table 2 of [15]); IADG 5.41 / 8.70 / 10.62 / 8.86% (Table 1 of [17]).
- Alignment instead of invariance (2023, read). SA-FAS [16] argues that removing domain signals fails
  because the shift comes back on unseen data, and that collapsed features let the classifier "leverage
  spurious correlations". It keeps domains as separate clusters and forces the live-to-attack direction
  to be the same in every domain. The tool is invariant risk minimisation (IRM): one classifier that is
  optimal in every training environment. Leave-one-out HTER 5.95 / 8.78 / 6.58 / 10.00% (Table 1).
- Threshold alignment (2025, read). GD-FAS [22] states that earlier methods align the classifier
  weights across domains while "the bias terms associated with these boundaries remain misaligned", so
  one threshold does not fit unseen domains. It reweights the loss per group, where a group is a domain
  and label pair, and it adds the expected calibration error (ECE, the gap between stated confidence and
  accuracy) as a metric of threshold alignment. ECE on the four leave-one-out splits: 3.39 / 1.82 / 2.37
  / 2.86 for GD-FAS against 18.12 / 17.77 / 7.77 / 13.85 for SA-FAS (Table 2).
- Other. Flat-minimum training with gradient alignment [18]. Identity as the domain variable, with
  liveness and identity features made orthogonal [19]. Image quality treated as a separate shift that is
  measured and fed to the network [20].
- Test time. One line updates the model on unlabelled target data during use [24]. Another projects the
  style statistics of each test image onto style bases learned in training, with no model update [23]
  (read; style is defined there as the channel-wise mean and standard deviation of a feature map).

### 1.3 Foundation models and vision-language models

- FLIP (2023, read) [25] fine-tunes the CLIP image encoder and aligns images with sentences such as
  "This is a real face". Its own ablation shows where the gain comes from: average leave-one-out HTER is
  25.86% from scratch, 6.00% from ImageNet weights and 3.48% from CLIP weights (Table 5). The text
  branch moves this to 3.01% (Table 2, with CelebA-Spoof as extra training data).
- Prompt learning without class names or domain labels (CFPL, 2024, read) [27]: 3.60% average HTER
  without extra data (Table 1). It builds a style prompt from the per-layer mean and spread of features
  and a content prompt from the normalised last layer. Fine-grained text per class (TF-FAS) [28].
  Statistical tokens and adapters on a frozen ViT (S-Adapter) [26].
- FoundPAD (2025, read) [29]: CLIP image encoder, low-rank adaptation (LoRA) on the query and value
  projections, one linear head. Average leave-one-out HTER 9.67% with ViT-L. Zero-shot CLIP is near
  chance (its Table 1). A frozen encoder with a linear head is clearly worse than the adapted one
  (single-source average HTER 31.89 against 16.81% for ViT-B, Table 5). MADation in morph detection is
  the same recipe from the same group [55].
- Current leaders of the leave-one-out table. GD-FAS reports 1.83% average HTER, and 0.95% with
  CelebA-Spoof added (Table 1 of [22]); it lists TF-FAS at 2.19%.

### 1.4 One-class and anomaly formulations

- Idea. Model bona fide images only. Call everything else an attack. The motive is unseen attack types.
- Works. Zero-shot anti-spoofing over 13 attack types with a tree of unsupervised clusters, and the
  SiW-M data set [31]. A compact bona fide embedding with a one-class Gaussian mixture on top [32]. The
  one-sided cue map above [4]. OC-SCMNet (2024) trains on live faces only: live images give an all-zero
  cue map, and attack features are synthesised in latent space, with a memory bank to explore new
  directions [33]. Hyp-OC trains on live faces with pseudo-negative points drawn from a Gaussian and
  losses in hyperbolic space [34]. A
  2025 method learns "unknown spoof prompts" in CLIP's text space from real faces only [35].
- Standing. One-class methods trail two-class methods on known attacks and are argued for on unseen
  ones. OC-SCMNet claims to be comparable with a two-class method on eight benchmarks [33] (abstract
  level; the PDF was not retrievable).

### 1.5 Unified physical and digital attack detection

- Idea. One detector for prints, replays, masks and for digital forgeries (face swaps, adversarial
  examples, generated faces).
- UniAttackData (2024, read) [36]: 1,800 subjects, 2 physical and 12 digital attack types, 29,706
  videos in the arXiv version (28,706 in the proceedings version and in [37]). Its design rule is "ID consistency": every identity has a live recording and every attack
  type. The stated reason is that earlier merged sets "cannot guarantee each ID covers the real face and
  all attack types", so models learn "liveness-irrelevant signals such as face ID, domain-specific
  information, and background". The leave-one-type-out protocol is hard: 22.42 ± 10.57% ACER for the
  paper's own method (Table 3). The extension has 2,875 identities and 54 attack types [38].
- Face morphing is not among the attack types of either set.
- Challenge practice (read) [37]. The 2024 challenge on this data fixed the threshold at the EER of the
  development set and ranked by ACER on the test set. The winner used a ResNet-50 with two augmentations
  that simulate attack cues (moiré overlays for replays, self-blending for digital forgeries) and a
  live-to-attack loss weight of 5 to 1 in the unseen-physical-attack protocol; test ACER 2.34% (Table
  3). The second team changed the resolution of one class per protocol (down-sampled copies of live
  faces in one, of attack faces in the other). The organisers note that the top five teams were all from
  industry.

### 1.6 What is deployed, and the standards view

- Standard. ISO/IEC 30107-3 defines APCER and BPCER and how to report them. I did not read the standard
  text; the definitions are quoted from the NIST report below. Test laboratories issue conformance
  letters by attack level (secondary sources only, part 6).
- NIST FATE PAD (2023, read) [44]. 82 software-only algorithms from 45 developers. About 20,000 attack
  images of 9 attack types and 21,218 bona fide stills, sequestered. Two summary numbers per algorithm
  and attack type: APCER at BPCER = 0.01 ("convenience") and BPCER at APCER = 0.01 ("security"). No
  overall ranking. Findings quoted from the executive and technical summaries:
  - "PAD performance varied widely across algorithms, use cases, and PA types, with only a small
    percentage of algorithms evaluated demonstrating notable detection capabilities."
  - Print and replay attacks are detected well by several developers when "the frame of the printed
    photo/electronic tablet and the subject's hands are typically visible". But "when the view is zoomed
    in such that the frame ... and the subject's hands are not visible, detection error rates increase
    across all algorithms, and in some cases, quite significantly" (1,417 stills in each condition,
    Table 5). Best APCER at BPCER = 0.01 in the
    impersonation task: 0.0 with context, 0.005 zoomed (Table 1). In the evasion task: 0.009 and 0.06
    (Table 2).
  - Bona fide error by demographic group is read at one fixed threshold, the one that gives BPCER 0.03
    on a reference group.
  - Sum-rule fusion of four algorithms beat the best single algorithm in all impersonation categories.
    Video beat stills for many algorithms.
  - The report names our application: "if a passport photo is collected in a retail outlet using a
    generic portrait camera, the passport issuer may check for presentation attack".
- A 2023 challenge on in-the-wild data covered 17 attack types, with one protocol for known and one
  for unknown attack types [43] (abstract level).
- Synthetic bona fide data is used for privacy reasons: 25,000 generated faces, presented as prints and
  replays to real sensors [42] (abstract level). Trained on it alone, the FoundPAD recipe is clearly
  weaker than trained on vegetables (27.56 against 14.15% HTER, Table 2 of [30]).
- So deployed practice differs from the academic table in three ways: thresholds are fixed in advance on
  bona fide data, bona fide sets are large and separate, and reports are per attack type.

### 1.7 Progress on the standard cross-domain table (as reported by each paper)

| Year | Method | Idea | HTER %, test on M / C / I / O | Source |
|---|---|---|---|---|
| 2019 | MADDG | symmetric adversarial invariance | 17.69 / 24.50 / 22.19 / 27.89 | Table 5 of [12] |
| 2020 | SSDG (ResNet) | live-only alignment | 7.38 / 10.44 / 11.71 / 15.61 | Table 5 of [12] |
| 2022 | SSAN (ResNet) | style shuffling | 6.67 / 10.00 / 8.88 / 13.72 | Table 2 of [15] |
| 2022 | PatchNet | fine-grained patch classes | 7.10 / 11.33 / 13.4 / 11.82 | Table 8 of [7] |
| 2023 | IADG | instance whitening, asymmetric | 5.41 / 8.70 / 10.62 / 8.86 | Table 1 of [17] |
| 2023 | SA-FAS | aligned direction (IRM) | 5.95 / 8.78 / 6.58 / 10.00 | Table 1 of [16] |
| 2023 | FLIP-MCL (extra data) | CLIP with text | 4.95 / 0.54 / 4.25 / 2.31 | Table 2 of [25] |
| 2024 | CFPL | CLIP, prompt learning | 3.09 / 2.56 / 5.43 / 3.33 | Table 1 of [27] |
| 2025 | FoundPAD ViT-L | CLIP with LoRA | average 9.67 | Table 2 of [29] |
| 2025 | GD-FAS | CLIP, aligned weights and bias | 0.42 / 0.93 / 3.33 / 2.64 | Table 1 of [22] |
| 2026 | FoundPAD trained on vegetables only | no face in training | 15.00 / 11.11 / 12.20 / 18.30 | Table 2 of [30] |

Two cautions on this table. SA-FAS itself shows that these numbers are "best snapshot" numbers: its own
HTER on the first split is 5.95% at the best epoch and 14.36% as the mean of the last ten epochs (Tables
1 and 2 of [16]). And HTER here is often computed at a threshold taken from the test data ([30] states
it uses the target set's EER threshold; [29] does not say).

---

## 2. What the field learned about shortcuts and bias, and how it excluded them

### 2.1 The findings

1. **The face is incidental (2026).** A detector trained only on recordings of 78 vegetables, with
   print and replay attacks built like those of face data sets, reaches 14.15% HTER and 92.70% AUC on
   average over the four face benchmarks. Training on synthetic faces gives 27.56% and 81.02% (Table 2
   of [30]). Models trained on faces transfer above chance to the vegetables. The authors conclude that
   "transferable PAD representations can be learned without using faces during downstream PAD
   training", and read the learned features as traces of the recapture process. Their frequency
   analysis shows that the attack-minus-bona-fide spectrum differs in sign between data sets, so no
   single spectral cue explains the transfer. The same paper shows that the pretraining carries the
   result: an ImageNet ViT trained on the same vegetables gets 36.97% HTER.
2. **Resolution, blur and camera are named as the easy cues.** SA-FAS: a plain classifier may exploit
   "the easiest difference (image resolution, blurriness, camera setting)" [16]. FLIP's error analysis:
   low resolution, lighting changes and pixelisation make real faces be called attacks, and the
   high-resolution OULU data in training may explain high-resolution attacks called real (its Figures 4
   and 6) [25]. This is said, not measured, in both papers.
3. **Context is a cue, and it has been measured.** NIST's zoomed print and replay attacks [44] are the
   same attack type without the visible frame and hands; errors rise for every algorithm. "Myope models"
   [40] finds that results are "consistently better when the background is present". PatchNet's score
   maps deviate at background and boundary regions, and its authors state that cues should come from
   the face region "but not the background's biases" [7].
4. **Identity.** UniAttackData [36] and its extension [38] argue that merged data sets teach identity
   and background, because no identity appears under all classes. The fairness study [41] finds higher
   error for women with every tested detector and for occluded faces with three of four (its Tables II
   and IV), and attributes it to identity and appearance cues; this is an attribution, not a direct
   test. Its remedy swaps a 64 × 64 patch between training images of different subjects. Identity-as-domain training [19] makes
   liveness and identity features orthogonal.
5. **Frequency shortcuts.** A 2025 paper frames the generalisation failure as reliance on easy
   frequency bands and masks those bands during training [21] (abstract level).
6. **Protocol and data set design.** GRAD-GPAD (read) [39] aggregated ten data sets and re-labelled
   them by attack instrument, capture device, lighting and face resolution. Intra-data-set results did
   not survive: in the cross-data-set protocol no method generalised across instruments (ACER above 22%
   in all cases), and a method that used image quality as its cue had 17.03% HTER where a colour-texture
   method had 6.33% on the pooled test. It adds protocols that change one factor: cross-device,
   cross-face-resolution, cross-conditions.
7. **Reporting.** SA-FAS reports mean and spread over the last ten epochs because best-snapshot numbers
   are optimistic [16]. GD-FAS adds calibration error because a good ranking can hide a moved threshold
   [22].
8. **Outside faces, the same result with interventions.** A 2026 study on voice anti-spoofing [45]
   (read) applies an intervention (MP3 coding, added noise, silence blanking) to one class only, in
   training, in test, or in both. EER moves from near 0% when the association is the same in training
   and test to above 50% when it is inverted. It recommends reporting how scores depend on such factors
   and not error rates alone.

### 2.2 How the field built training that excludes the cues

| Remedy | What it does | Works |
|---|---|---|
| Asymmetric alignment | Only bona fide features are made domain-independent; attacks stay spread | [12][17][7] |
| Aligned decision, kept domains | Same bona-fide-to-attack direction, and same offset, in every domain | [16][22] |
| Style removal or shuffling in feature space | Whiten, swap or project per-image feature statistics; within one class only | [15][17][23][27][19] |
| Named nuisance heads | Adversarial heads for camera, illumination and other factors | [13][14] |
| Fine-grained classes | One class per device and material, several bona fide classes | [7] |
| Local input | Patches from the raw capture, no resize; shuffled patches from several subjects | [7][8] |
| Identity-consistent data | Every identity under every class | [36][38] |
| Identity-free data | Train on non-face objects, or swap patches between subjects | [30][41] |
| Bona-fide-only training | Zero-map or compact embedding on live data; attacks only in latent space | [4][32][33][34][35] |
| Cue simulation on bona fide images | Moiré overlays, colour changes, self-blending as synthetic attacks | [37] |

### 2.3 How the field built evaluation that excludes the cues

| Practice | Where | Transfer to us |
|---|---|---|
| Threshold fixed on a development set, errors read on the test set | OULU-NPU protocol [46] (listing only), [39], [37] | direct |
| Two fixed-point summaries: attack error at bona fide error 0.01, and the reverse | [44] | direct; NIST's morph evaluation uses the same form |
| Bona fide error per sub-population at one threshold fixed on a reference group | [44] (BPCER 0.03 on a reference group), [41] | direct: per photo pool and per storage history |
| Large, separate, sequestered bona fide set | [44] (21,218 stills) | direct in spirit; our genuine pools are small (204 FRLL photos) |
| The same attack with a suspected cue removed | [44] zoomed attacks | this is our ladder |
| One factor changed per protocol | OULU-NPU, [39] cross-face-resolution and cross-device | direct: cross-history |
| Leave-one-data-set-out | [10][12] and all later | only after a change, see part 5 |
| Leave-one-attack-type-out | [31][36] | direct: leave-one-engine-out, leave-one-family-out |
| Every identity under every class; subject-disjoint splits | [36], OULU-NPU | direct |
| Bona-fide-dominated test with true-positive rate at fixed false-positive rate | [15] | direct |
| Mean over last epochs, not the best snapshot; calibration error per domain | [16][22] | direct, and it fits the no-seed-picking rule |

### 2.4 Practices that transfer directly, for a stable bona fide error at one threshold

These need no new idea, only adoption.

1. Fix the threshold once, on declared bona fide development images, and never on test data. State the
   target (BPCER 0.01 as in [44]; with small pools 0.05 is the smallest readable value).
2. Report BPCER for every cell of photo pool times processing history at that one threshold, and the
   worst cell. This is the NIST demographic analysis with "history" in place of "group" [44].
3. Report both fixed-point summaries (MACER at BPCER 0.01, BPCER at MACER 0.01) next to EER.
4. Keep every identity in both classes and make splits person-disjoint [36]. SMDD breaks this rule by
   design.
5. Treat the classes asymmetrically in training: pull bona fide images of all histories together, leave
   morphs of different engines apart [12][17][7].
6. Apply any augmentation to both classes or within one class with the same sampling [17][19]. The
   challenge entry that re-sampled one class per protocol [37] shows how easily the opposite is done.
7. Report the last checkpoint and the spread over late epochs [16].
8. Do not repair a moved threshold by conditioning it on file size. The one industrial test of that in
   morph detection found that it "does not help much" [59].

---

## 3. Has each technique family been used in morph detection?

Searches are listed where nothing was found. "Record" means our own planning record already holds the
item and I did not re-open it.

| Family | Used in morph detection? | Evidence or searches |
|---|---|---|
| Pixel-wise supervision | Yes | PW-MAD [47] (read) takes the per-pixel label of [2]; 14 × 14 map; it does not state how the target differs within an image. At APCER 0.1% it reports BPCER 17.74% against 34.67% for the next method on digital data (its Table 3). Partial morphs with region labels: record. Our alpha-field probe (AF0) is a content-dependent version. |
| One-sided (bona-fide-only) map loss | Not found | Searches: "morphing attack detection one-class anomaly detection bona fide only"; "PW-MAD pixel-wise supervision". One-class morph detectors exist (next row) but none regresses a map to zero on genuine images while leaving morphs free. |
| One-class and anomaly | Yes | Novelty against outlier detection [48]; self-paced auto-encoders, SPL-MAD [49]; diffusion reconstruction, MAD-DDPM [50]; frozen features with a Gaussian mixture [54]; Fourier residual latents, SRL-MAD [56]. None declares processed genuine images as part of the normal class. |
| Symmetric adversarial or consistency training | Yes, once | Kashiani et al. 2023 [52] (read): discriminators between source and augmented views, consistency of outputs and embeddings, style transfer between images, and a "self-morph" of two photos of one person that is treated as a morph. Reports APCER at fixed BPCER per test set. An earlier ensemble with domain generalisation by the same group [51]. |
| Asymmetric (bona-fide-only) alignment | Not found | Searches: "morphing attack detection domain generalization single-side OR adversarial OR meta-learning OR style"; "morphing attack detection adversarial domain gradient reversal OR domain discriminator OR domain-invariant single image morph". |
| Invariant risk, group-robust training, threshold or bias alignment | Not found | Search: "invariant risk minimization OR group DRO OR worst-group morphing attack detection" (no morph result). The record holds one earlier search with the same outcome and our own failed small trial of a consistency loss and group weighting. |
| Meta-learning for domain shift | Not found | First search of the asymmetric row. |
| Feature-statistic (style) removal, shuffling or projection | Not found | Search: "morphing attack detection instance normalization OR style OR AdaIN OR feature statistics". Only image-level style transfer in [52] and print-scan texture synthesis were returned. |
| Foundation and vision-language models | Yes | MADation [55] (CLIP with LoRA, the FoundPAD recipe); frozen general features [54]; prompts and multimodal models: record. |
| Fine-grained classes | Only on the attack side | Morph "fingerprinting": a multi-class head over morphing algorithms [53]. No paper with several genuine or single-subject classes was found. Search: "morphing attack attribution OR multi-class OR fine-grained classification morph type". |
| Unified physical and digital detection | Morphs are absent | UniAttackData [36] and its extension [38] list no morphing attack. Search: "unified detection physical presentation attacks and morphing attacks single model". |
| Test-time adaptation | Not on one image | A 2026 workshop paper adapts a detector online with bona fide images at the gate (search snippet only; the pages returned an error). Search: "morphing attack detection test-time adaptation OR test time OR source-free". |
| Synthetic or identity-free training data | Synthetic faces yes, face-free no | SMDD: record. Privacy-aware synthetic training data [58]. Search for a face-free analogue of [30]: "morphing attack detection trained without faces OR non-face OR face-free OR generic image blending" found none. Our paired-differences experiment (PD1) is the closest: a head trained only on one-person mixes ranks two-person morphs as well as a head trained on them. |
| Self-made attacks on bona fide images | Yes | SelfMAD [57]; self-morphing in [52]. |
| Fixed-threshold bona fide error under benign processing | Partly | Marriott, NIST IFPC 2025 [59] (read, 14 slides): four sets (three of ID-document photos, one of mugshots), threshold fixed at BPCER 0.01, then images compressed. "Lower quality, compressed images cause more false positives." "Even with no compression, pre-processing images increases the BPCER." "Adapting the threshold based on file-size does not help much to stabilise performance." Retraining on heavily compressed images helps but stays "far from base levels". NIST FATE MORPH per-pool false detections: record. |

---

## 4. Four ways to solve our task that follow from this field

Each is written against the ladder. The rungs in words: camera photo (R0); the same photo with the
morphs' shrink-and-enlarge storage history (R1); warp-only image (R2w); a photo blended with its own
mirror (R3m); a morph of two photos of one person (R3); a morph of two persons (R4). All four keep one
network on one image, no gate, and no new image operation. Suggested order for three days: 4.2 as an
add-on to the rebuild arms already planned; 4.1 as the one-day decisive test; 4.3 next; 4.4 only if the
blend-evidence map stays in the paper.

### 4.1 History as style: remove per-image token statistics before the head

- **Source.** The style line of anti-spoofing. Style is the channel-wise mean and spread of a feature
  map over spatial positions [23][27]. SSAN separates it by instance normalisation [15]; IADG whitens
  the style-sensitive part per instance [17]; test-time style projection replaces a test image's
  statistics by a mixture of learned bases, with no model update [23].
- **The observation behind the transfer.** Our measured shortcuts are mostly spatially uniform
  operations: the shrink-and-enlarge history, a storage size, global softness. A uniform operation
  moves all patch tokens of an image in a similar way. That is a change of the image's own token mean
  and spread, which is the field's definition of style. Blending two persons is not uniform: detail is
  lost where the two faces disagree and kept where they agree.
- **Method.** Take the patch tokens inside the face hull. Standardise each channel over the patches of
  that image (subtract the image's own mean, divide by its own spread). Score patches with the head.
  Pool with a rule that reads the upper tail (mean of the top tenth), because the plain mean of
  standardised tokens is zero by construction. Two variants in the same harness: (a) project the
  statistics onto bases learned from unprocessed camera photos [23] instead of removing them; (b)
  during training swap the statistics between images of the same class [17][19], which multiplies
  history diversity without any image operation. In the CLIP with LoRA recipe this becomes one
  normalisation step in front of a patch-token head.
- **Signal it reads.** The spatial pattern of evidence relative to the image's own level: where in
  this face detail is doubled or missing, compared with the rest of this face.
- **Cues it cannot use, and the contrast that shows it.** Storage history and global softness, to the
  extent that they are uniform: R0 against R1 on the FRLL photos and the softened copies of ladder hosts
  must fall to chance. It does not remove a border (local; blank it), expression or backdrop (content),
  or warping (local geometry; R2w must stay among the training negatives and the R0-to-R2w shift is
  read as before). Capture sharpness of the whole photo is uniform and is removed with the history;
  backdrop noise lies outside the face hull and is not read. Generator fingerprints are not addressed.
  It is a safeguard for landmark and other pixel-blend families. For GAN and diffusion morphs it only
  protects against history; it is not a signal source there.
- **Prior use in morph detection.** None found (search in part 3, style row). The nearest work
  transfers image styles between training images and adds discriminators [52].
- **First test (one day, CPU, cached DINOv3 ViT-L/16 patch tokens at 512).**
  Step A, one hour. For each FRLL photo and its history-matched copy (204 photos, four families), and
  for the softened copies of 200 ladder hosts, take the patch-wise token difference. Report the share
  of its energy that is the per-image mean shift, and the share left after the best per-image
  channel-wise shift and rescale.
  Step B, half a day. Refit the patch-level heads of the alpha-field probe (AF0), same script, same
  person folds, on standardised tokens, top-tenth pooling. Compare with the raw-token fit.
  Pass: genuine score shift from native to history-matched at most 0.3 standard deviations and at most
  half the raw-token value; at most 10% of history-matched photos flagged at the 5% threshold; R2w
  against R4 on the OpenCV-style engine at least 0.97 (raw first pass: 0.9948).
  **Kill:** in step A less than half of the history shift is removed by the per-image shift and rescale
  on both pools; or in step B the history shift is not halved; or R2w against R4 falls below 0.90.
  Between 0.90 and 0.97 the step is kept only as the training-time shuffle (variant b).
- **Path to the published tables.** If it passes, it enters the retrain of the CLIP with LoRA recipe
  as a normalisation step. Table numbers come from that retrain. If the landmark cells get worse
  because global softness was doing the work, that is reported next to the fixed-threshold gain.
- **Risk.** A blur changes textured patches more than flat ones, so part of the history shift is
  content-dependent and survives. Dividing by the spread can amplify noise in flat images. The softness
  that made landmark morphs easy is thrown away on purpose, so native error can rise. ViT tokens mix
  information across patches, so "per-patch" is approximate.

### 4.2 One-threshold training: align the genuine side only, and align the offset

- **Source.** SSDG: only bona fide features pass the domain adversary [12]. SA-FAS: keep domain
  information, align the direction of the decision [16]. GD-FAS: weights aligned is not enough, the
  offset moves and with it the threshold; reweight groups of domain and label; measure calibration per
  domain [22]. PatchNet: tighter margin for bona fide classes [7]. NIST: bona fide error per group at
  one threshold [44].
- **Why it fits our finding.** The measured failure of released detectors is a moved genuine score at a
  fixed threshold (0% of unprocessed photos flagged, 45% after a 50% shrink-and-enlarge, 97% of photos
  stored small, for one release). In the field's words this is bias misalignment across environments.
  A within-host paired fit (already on our table) cancels each host's level, so it aligns the direction.
  It does not control the absolute genuine level across pools and histories, which is what a fixed
  threshold needs.
- **Method.** Environments are genuine constructions: native photo, shrink-and-enlarge history,
  softened copy, warp-only, each per photo pool. Three terms, all on genuine images only. (i) Orbit
  term: for one host, the logits of its genuine versions must be equal (penalise their variance).
  (ii) Offset term: across environments, the mean and the upper tail (mean of the top tenth) of genuine
  logits must be equal. (iii) Margin: tight for genuine, loose for morphs. Morphs get no alignment at
  all, only "a morph must score above the genuine versions of its own host by a margin". Aligning
  morphs across engines would push the network to whatever all engines share, which is softness.
  Reporting: BPCER per environment at one threshold fixed on native development photos, the spread
  between the best and worst environment, and calibration error per environment.
- **Signal it reads.** Unchanged; it is a constraint on the recipe's score, not a new signal.
- **Cues it cannot use, and the contrast that shows it.** Any cue that changes between genuine
  versions of one photo: history and softness (R0 against R1), warp (R0 against R2w). The test is the
  worst-environment BPCER at the fixed threshold. Unseen histories are not covered by construction and
  are read on a left-out construction. Expression, capture detail and backdrop do not change inside
  one host's versions, so this loss does not touch them; they are equalised only by training on
  complete ladders, where every host appears in every class (the identity-consistency rule of [36]).
  Generator fingerprints are not addressed.
- **Prior use in morph detection.** Symmetric adversarial consistency between a training image and its
  augmented view exists [52]. Nothing genuine-side-only and nothing on offset alignment was found
  (searches in part 3). In our own record a small consistency loss and group weighting failed with 16
  to 90 pairs; data-level history crossing reduced flagged shrunk photos from 19 to 40% down to 4 to
  8%. This proposal is therefore an upgrade of ideas already listed (group-robust training, invariant
  risk, interventional nulling), with three specific changes taken from this field: genuine side only,
  the offset as an explicit target, and per-environment calibration as the read-out.
- **First test (one day, CPU, cached pooled CLIP ViT-L/14 and DINOv3 features).** Four heads on the
  same images, folds by person, ladder hosts for training (camera photos, warp-only images, two-person
  morphs, and the softened copies that exist for 200 hosts), the FRLL pool held out: (1) plain; (2)
  plain with softened genuine copies added as negatives; (3) as 2 with the orbit term; (4) as 3 with
  the offset term. Threshold at 5% of native training-pool photos. Read BPCER on FRLL native photos, FRLL
  history-matched photos per family, held-out softened copies and warp-only images; read MACER on FRLL
  two-person morphs.
  Pass: worst-environment BPCER at most 10% and at most half that of head 2, with R2w against R4 lower
  by no more than 0.01.
  **Kill:** heads 3 and 4 do not bring the worst-environment BPCER below three quarters of head 2.
  Then the loss adds nothing over the data arm and only the data arm is kept.
- **Path to the published tables.** The recipe and backbone stay. In anti-spoofing the single-side
  term improved cross-domain error (7.38 against 11.19% without it, Table 1 of [12]); there is no
  evidence of a native cost.
- **Risk.** On frozen pooled features the linear version is the already-proposed projection in soft
  form, so the first test may only confirm what is known; the real test is inside the LoRA fit.
  Alignment holds for histories seen in training only. Pairs exist only for our own ladder. An earlier
  small trial failed.

### 4.3 Name the nuisance: a classifier over ladder rungs, with "two-person morph" as one class

- **Source.** PatchNet [7]: replace two classes by fine-grained classes of capture device and material,
  several of them bona fide, with a tighter margin for bona fide classes. SA-FAS "separability" [16]:
  keep nuisance information as separate clusters and do not remove it. Fine-grained text per class
  [28] and specific-versus-unified class prompts [36] in the CLIP line.
- **Method.** One network, one softmax over construction classes: camera photo; stored-small or
  softened photo; warp-only image; mirror self-blend; same-person morph; two-person morph; and for
  generator families, one-photo reconstruction, same-person latent mix, two-person latent morph. The
  reported attack score is the log-odds of the two-person classes against all others. The mass on the
  single-subject classes is a second output, reported separately. This is the three-way class proposal
  that awaits the author (genuine; morphing attack; single-subject manipulation), carried into the
  head. Margins: tight for the classes that are genuine, loose for manipulation classes. In the CLIP
  recipe the class prototypes can be free weights or sentences that describe the construction [28].
- **Why this is more than "binary with hard negatives".** A binary head must find one direction that
  separates morphs from a mixture of very different negatives. Softness evidence has nowhere to go but
  "morph". With named classes, softness alone is explained by the stored-small class, warping alone by
  the warp-only class, blending alone by the self-blend and same-person classes. The two-person class
  must beat each of them. Every decision also comes with an audit trail: which class competed.
- **Signal it reads.** What distinguishes a two-person blend from a same-person blend of the same
  engine, after softness, warp and blending have been explained by other classes.
- **Cues it cannot use, and the contrast that shows it.** Softness alone (R1 has its own class), warp
  alone (R2w), blending alone (R3m, R3), generator fingerprint alone (one-photo reconstruction). The
  defining contrasts are R3 against R4 and same-person mix against two-person morph. Because every
  host of a ladder appears in every class, expression, capture detail, backdrop and photo pool are
  equal across classes by construction [36]. A border must still be blanked in all classes.
- **Prior use in morph detection.** Multi-class heads exist on the attack side only, to name the
  morphing algorithm [53]. No work with several genuine classes or a single-subject class was found
  (search in part 3).
- **First test (one day, CPU, cached features of the landmark ladder: 8,294 images, both engines, two
  pools; plus the softened copies of 200 ladder hosts and the FRLL history-matched frames).**
  Multinomial logistic head on six classes, with and without margins. The stored-small class is
  trained on the softened copies. Folds by person inside the large pool (FRGC and colorFERET hosts),
  also leave-one-engine-out; the FRLL pool is never trained on. Baseline on identical images: a binary
  head, two-person morph against everything else. Read: (a) R3 against R4 and R3m against R4 with the
  attack log-odds, large pool, held-out persons; (b) native-to-history shift and flag rate at the 5%
  threshold on the FRLL photos and their history-matched frames; (c) R2w against R4; (d) the confusion
  matrix among genuine classes.
  Pass: (a) at least 0.90 on both engines (the alpha-field probe's head, which never saw a same-person
  morph, has 0.853 and 0.830 on the large pool); at most 10% of history-matched photos flagged.
  **Kill:** the attack log-odds are within 0.01 AUC of the binary head on (a) and within a tenth of
  its history shift; or (a) stays below 0.85. Then naming the nuisance adds nothing over hard
  negatives.
- **Path to the published tables.** The backbone and recipe stay; published tables are binary and are
  scored with the attack log-odds.
- **Risk.** A same-person morph and a two-person morph differ in degree, not in kind; look-alike pairs
  will be confused, and the class border follows our data's mix of sessions. On GAN ladders the
  same-person against two-person contrast is weak so far (0.65). More classes need more data per class.
  The class list is a ruling the author has not yet made.

### 4.4 One-sided zero map: genuine images regress to zero, morphs get no template

- **Source.** The one-sided cue map of anti-spoofing: a regression to an all-zero map on live images
  only, no map target for attacks, a separate ranking loss between classes [4]; the live-only variant
  with latent attack features [33]; the per-pixel label that PW-MAD brought to morph detection [2][47].
  The reported gain is on unseen attack types (1.19% against 7.66 to 12.10% ACER, Table 1 of [4]) and
  the paper notes that giving attacks an all-one target was worse.
- **Why it may repair the blend-evidence map.** The alpha-field probe fits a measured per-patch target.
  The round-2 review found that "a global flag times an anatomy template" also fits such a target, and
  the first pass shifts warp-only images by 0.73 standard deviations on FaceMorpher. In the one-sided
  form there is no positive template to fit. The only per-patch target is zero, and it is put on every
  genuine construction: photos, warp-only images of both engines, softened copies. To be exact about
  what is new: the probe's training set already holds warp-only images of its own engine with a zero
  target. The changes are the missing positive target, the second engine's warp-only images, and the
  softened copies. Morphs enter through one image-level rule: the map energy of a morph must exceed
  that of the warp-only image of its own host by a margin. The graded-mixing set gives a second rule:
  energy must not fall as the mixing fraction rises.
- **Signal it reads.** Whatever local evidence is absent from every genuine construction of the same
  host.
- **Cues it cannot use, and the contrast that shows it.** Warp (the warp-only image of the same host
  is a zero target) and softness (softened copies are zero targets): R0 to R2w and native to softened
  shifts. Unseen engines play the role of unseen attack types.
- **Prior use in morph detection.** Two-sided pixel-wise supervision exists [47]. A one-sided map with
  free morphs was not found (part 3).
- **First test (one day, CPU after tokens, on the alpha-field training set and the landmark ladder).**
  Two heads on identical tokens: the current ridge fit to the measured target, and the one-sided head
  (absolute-value loss to zero on genuine constructions, hinge on image energy within host). Read the
  registered controls of the round-2 consolidation: R0 to R2w shift per engine, softened-genuine shift,
  and, as a free test because no map target was used, the within-image rank correlation of the
  predicted map with the true field on the gradient and bump images.
  Pass: R0 to R2w shift at most 0.3 standard deviations on both engines; correlation at least 0.2.
  **Kill:** the shift on FaceMorpher stays above 0.3; or the correlation is below 0.2. Then the
  one-sided map is a global flag and not a map, and it is dropped.
- **Risk.** With only an image-level rule for morphs the head has little reason to localise. The
  softness floor remains: a two-person morph has 0.52 times the detail energy of its halves, and the
  softened copies in the zero set may not match that level. It improves a component that is no longer
  the headline.

---

## 5. What does not transfer, and why

1. **Temporal, physiological and interactive cues** (pulse signals, motion, challenge-response,
   flashing light). We have one still image, and a morph is not a recapture: both classes were
   photographed live.
2. **Depth, reflection and moiré targets.** They describe a flat or screen surface. A morph has none.
   The matching dense target for us is local blend evidence, which is already on the table.
3. **Context cues** (frame, hands, bezel). They are real attack evidence in anti-spoofing. In an
   enrolment portrait there is no legitimate context cue; anything outside the inner face is a data-set
   cue. Only the control design transfers.
4. **Leave-one-data-set-out as practised.** It assumes each data set holds both classes from one
   capture pipeline, so the shortcut differs between data sets. In morph benchmarks the shortcut
   differs between the classes inside each data set (a file attribute separates the classes in all 17
   cells). Holding one data set out would not expose it. Environments must be interventions on one
   photo, which is the ladder.
5. **Symmetric invariance of both classes.** The field left it [12][16]. Landmark, GAN and diffusion
   morphs differ more than print and replay.
6. **Test-time adaptation with model updates** [24]. It needs a stream of unlabelled target data, moves
   the threshold during use, and breaks "one fixed network". Only the update-free style projection
   transfers [23] (4.1).
7. **Fusion and video.** Fusion of four algorithms and video input both help in the NIST test [44].
   Our constraints forbid both.
8. **Quality-conditioned decisions.** Feeding a quality score to the network [20] or adapting the
   threshold to file size is a gate in spirit, and the one morph-detection trial of the latter did not
   help [59].
9. **Image-level frequency masking and high-frequency branches** [21][14]. They need new filtering
   code, and frequency residuals are the most history-sensitive features we know.
10. **Cue-simulating augmentation and class-specific resampling** [37]. Overlays and blur are outside
    the allowed operations. Resampling one class is how a resolution shortcut is planted.
11. **Identity suppression as a goal** [41][19]. In anti-spoofing the face is incidental [30]. In morph
    detection the second identity is the definition of the attack. Identity-free training transfers
    only as a reference: what a detector reaches with no second identity. Our paired-differences
    experiment already plays that role.
12. **Language supervision by class name.** Zero-shot CLIP is near chance for anti-spoofing (Table 1 of
    [29]). FLIP's own ablation puts most of the gain in the image-encoder weights (Table 5 of [25]),
    which MADation already uses.
13. **Scoring habits of the academic table.** HTER at the test set's own EER threshold and
    best-snapshot reporting hide the very failure we measure. They must not be imported.

---

## 6. References

### 6.1 Verified in this task (57). "Read" = read beyond the abstract (23).

Anti-spoofing: auxiliary supervision, architectures, surveys
- [2] George, Marcel. Deep Pixel-wise Binary Supervision for Face Presentation Attack Detection. ICB 2019. https://arxiv.org/abs/1907.04047
- [3] Yu et al. Searching Central Difference Convolutional Networks for Face Anti-Spoofing. CVPR 2020. https://arxiv.org/abs/2003.04092
- [4] Feng et al. Learning Generalized Spoof Cues for Face Anti-spoofing. arXiv 2020. https://arxiv.org/abs/2005.03922 (read)
- [5] Zhang et al. CelebA-Spoof: Large-Scale Face Anti-Spoofing Dataset with Rich Annotations. ECCV 2020. https://arxiv.org/abs/2007.12342
- [6] Liu, Stehouwer, Liu. On Disentangling Spoof Trace for Generic Face Anti-Spoofing. ECCV 2020. https://arxiv.org/abs/2007.09273
- [7] Wang et al. PatchNet: A Simple Face Anti-Spoofing Framework via Fine-Grained Patch Recognition. CVPR 2022. https://arxiv.org/abs/2203.14325 (read)
- [8] Kantarcı, Dertli, Ekenel. Shuffled Patch-Wise Supervision for Presentation Attack Detection. arXiv 2021. https://arxiv.org/abs/2109.03484
- [9] Yu et al. Deep Learning for Face Anti-Spoofing: A Survey. IEEE TPAMI, online 2022. https://arxiv.org/abs/2106.14948

Anti-spoofing: domain generalisation and test time
- [10] Shao et al. Multi-Adversarial Discriminative Deep Domain Generalization for Face Presentation Attack Detection. CVPR 2019. https://openaccess.thecvf.com/content_CVPR_2019/html/Shao_Multi-Adversarial_Discriminative_Deep_Domain_Generalization_for_Face_Presentation_Attack_Detection_CVPR_2019_paper.html
- [11] Shao et al. Regularized Fine-grained Meta Face Anti-spoofing. arXiv 2019. https://arxiv.org/abs/1911.10771
- [12] Jia et al. Single-Side Domain Generalization for Face Anti-Spoofing. CVPR 2020. https://arxiv.org/abs/2004.14043 (read)
- [13] Kim, Kim. Suppressing Spoof-irrelevant Factors for Domain-agnostic Face Anti-spoofing. arXiv 2020. https://arxiv.org/abs/2012.01271
- [14] Chen et al. Camera Invariant Feature Learning for Generalized Face Anti-spoofing. IEEE TIFS 2021. https://arxiv.org/abs/2101.10075
- [15] Wang et al. Domain Generalization via Shuffled Style Assembly for Face Anti-Spoofing. CVPR 2022. https://arxiv.org/abs/2203.05340 (read)
- [16] Sun et al. Rethinking Domain Generalization for Face Anti-spoofing: Separability and Alignment. CVPR 2023. https://arxiv.org/abs/2303.13662 (read)
- [17] Zhou et al. Instance-Aware Domain Generalization for Face Anti-Spoofing. CVPR 2023. https://arxiv.org/abs/2304.05640 (read)
- [18] Le, Woo. Gradient Alignment for Cross-Domain Face Anti-Spoofing. CVPR 2024. https://arxiv.org/abs/2402.18817
- [19] Yang et al. Generalized Face Anti-spoofing via Finer Domain Partition and Disentangling Liveness-irrelevant Factors. arXiv 2024 (an IOS Press record FAIA240498 exists; venue not confirmed). https://arxiv.org/abs/2407.08243 (read)
- [20] Ge et al. DiffFAS: Face Anti-Spoofing via Generative Diffusion Models. ECCV 2024. https://arxiv.org/abs/2409.08572
- [21] Cao, Ma. Towards Generalized Face Anti-Spoofing from a Frequency Shortcut View. WACV 2025. https://mlanthology.org/wacv/2025/cao2025wacv-generalized
- [22] Jung et al. Group-wise Scaling and Orthogonal Decomposition for Domain-Invariant Feature Extraction in Face Anti-Spoofing. ICCV 2025. https://arxiv.org/abs/2507.04006 (read)
- [23] Zhou et al. Test-Time Domain Generalization for Face Anti-Spoofing. CVPR 2024. https://arxiv.org/abs/2403.19334 (read)
- [24] Huang et al. Test-Time Adaptation for Robust Face Anti-Spoofing. BMVC 2023. https://bmvc2022.mpi-inf.mpg.de/BMVC2023/379

Anti-spoofing: foundation and vision-language models
- [25] Srivatsan, Naseer, Nandakumar. FLIP: Cross-domain Face Anti-spoofing with Language Guidance. ICCV 2023. https://arxiv.org/abs/2309.16649 (read)
- [26] Cai et al. S-Adapter: Generalizing Vision Transformer for Face Anti-Spoofing with Statistical Tokens. IEEE TIFS 2024. https://arxiv.org/abs/2309.04038
- [27] Liu et al. CFPL-FAS: Class Free Prompt Learning for Generalizable Face Anti-spoofing. CVPR 2024. https://arxiv.org/abs/2403.14333 (read)
- [28] Wang et al. TF-FAS: Twofold-Element Fine-Grained Semantic Guidance for Generalizable Face Anti-Spoofing. ECCV 2024. https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/01098.pdf
- [29] Ozgur et al. FoundPAD: Foundation Models Reloaded for Face Presentation Attack Detection. WACV Workshops 2025. https://arxiv.org/abs/2501.02892 (read)
- [30] Ozgur, Boutros, Damer. Tomatoes, Potatoes, and Onions: Questioning the Need for Faces in Face Presentation Attack Detection. ACM Multimedia Workshops 2026. https://arxiv.org/abs/2608.21455 (read)

Anti-spoofing: one-class and unseen attacks
- [31] Liu et al. Deep Tree Learning for Zero-shot Face Anti-Spoofing. CVPR 2019. https://arxiv.org/abs/1904.02860
- [32] George, Marcel. Learning One Class Representations for Face Presentation Attack Detection using Multi-channel Convolutional Neural Networks. IEEE TIFS 2020. https://arxiv.org/abs/2007.11457
- [33] Huang et al. One-Class Face Anti-spoofing via Spoof Cue Map-Guided Feature Learning. CVPR 2024. https://openaccess.thecvf.com/content/CVPR2024/papers/Huang_One-Class_Face_Anti-spoofing_via_Spoof_Cue_Map-Guided_Feature_Learning_CVPR_2024_paper.pdf
- [34] Narayan, Patel. Hyp-OC: Hyperbolic One Class Classification for Face Anti-Spoofing. FG 2024. https://arxiv.org/abs/2404.14406
- [35] Jiang et al. Learning Unknown Spoof Prompts for Generalized Face Anti-Spoofing Using Only Real Face Images. arXiv 2025. https://arxiv.org/abs/2505.03611

Anti-spoofing: unified physical and digital attacks
- [36] Fang et al. Unified Physical-Digital Face Attack Detection. IJCAI 2024. https://arxiv.org/abs/2401.17699 (read)
- [37] Yuan et al. Unified Physical-Digital Attack Detection Challenge. CVPR Workshops 2024. https://arxiv.org/abs/2404.06211 (read)
- [38] Liu et al. Benchmarking Unified Face Attack Detection via Hierarchical Prompt Tuning. arXiv 2025. https://arxiv.org/abs/2505.13327 (read)

Shortcuts, bias, protocols, operational evaluation
- [39] Costa-Pazo et al. Generalized Presentation Attack Detection: a face anti-spoofing evaluation proposal. arXiv 2019 (ICB 2019 according to its code repository). https://arxiv.org/abs/1904.06213 (read)
- [40] Neto, Sequeira, Cardoso. Myope Models: Are face presentation attack detection models short-sighted? WACV Workshops 2022. https://arxiv.org/abs/2111.11127
- [41] Fang et al. Fairness in Face Presentation Attack Detection. Pattern Recognition 147, 2024. https://arxiv.org/abs/2209.09035 (read)
- [42] Fang, Huber, Damer. SynthASpoof: Developing Face Presentation Attack Detection Based on Privacy-friendly Synthetic Data. CVPR Workshops 2023. https://arxiv.org/abs/2303.02660
- [43] Wang et al. Wild Face Anti-Spoofing Challenge 2023: Benchmark and Results. CVPR Workshops 2023. https://arxiv.org/abs/2304.05753
- [44] Ngan, Grother, Hom. Face Analysis Technology Evaluation (FATE) Part 10: Performance of Passive, Software-Based Presentation Attack Detection (PAD) Algorithms. NIST IR 8491, September 2023. https://doi.org/10.6028/NIST.IR.8491 (read: executive and technical summaries, data tables)
- [45] Sahidullah et al. Shortcut Learning in Binary Classifier Black Boxes: Applications to Voice Anti-Spoofing and Biometrics. arXiv 2026. https://arxiv.org/abs/2601.17782 (read)

Morph detection
- [47] Damer et al. PW-MAD: Pixel-wise Supervision for Generalized Face Morphing Attack Detection. ISVC 2021. https://arxiv.org/abs/2108.10291 (read)
- [48] Damer et al. On the Generalization of Detecting Face Morphing Attacks as Anomalies: Novelty vs. Outlier Detection. BTAS 2019. https://publica.fraunhofer.de/handle/publica/408789
- [49] Fang, Boutros, Damer. Unsupervised Face Morphing Attack Detection via Self-paced Anomaly Detection. IJCB 2022. https://arxiv.org/abs/2208.05787
- [50] Ivanovska, Štruc. Face Morphing Attack Detection with Denoising Diffusion Probabilistic Models. IWBF 2023. https://arxiv.org/abs/2306.15733
- [51] Kashiani et al. Robust Ensemble Morph Detection with Domain Generalization. IJCB 2022. https://arxiv.org/abs/2209.08130
- [52] Kashiani et al. Towards Generalizable Morph Attack Detection with Consistency Regularization. IJCB 2023. https://arxiv.org/abs/2308.10392 (read)
- [53] Zhang, Jia, Lyu, Li. Fusion-based Few-Shot Morphing Attack Detection and Fingerprinting. arXiv 2022. https://arxiv.org/abs/2210.15510
- [54] Colbois, Marcel. Evaluating the Effectiveness of Attack-Agnostic Features for Morphing Attack Detection. IJCB 2024. https://arxiv.org/abs/2410.16802
- [55] Caldeira et al. MADation: Face Morphing Attack Detection with Foundation Models. WACV Workshops 2025. https://arxiv.org/abs/2501.03800
- [56] Paulo, Proença, Neves. SRL-MAD (one-class, structured residual Fourier representations). arXiv 2026. https://arxiv.org/abs/2603.15050
- [57] Ivanovska et al. SelfMAD. FG 2025. https://arxiv.org/abs/2504.05504
- [58] Ivanovska et al. Face Morphing Attack Detection Using Privacy-Aware Training Data. arXiv 2022. https://arxiv.org/abs/2207.00899
- [59] Marriott. Robustness of Morphing Attack Detection to Compression. NIST IFPC 2025, slides, 3 April 2025. https://pages.nist.gov/ifpc/2025/presentations/30.pdf (read, all 14 slides)

### 6.2 Found only as a search listing or through secondary pages (not counted, not used as evidence for numbers)

- [1] Liu, Jourabloo, Liu. Learning Deep Models for Face Anti-Spoofing: Binary or Auxiliary Supervision. https://arxiv.org/abs/1803.11097 (title and link seen in a result list; page not opened).
- [46] OULU-NPU data set, protocols and the rule "threshold at the EER of the development set". Project site https://sites.google.com/site/oulunpudatabase ; the FG 2017 paper itself was not opened.
- ISO/IEC 30107-3:2023. The standard text was not read. Definitions are quoted from [44].
- Test-laboratory conformance levels for presentation attack detection: trade press and one laboratory comparison sheet in a result list.
- Minivision "Silent Face" anti-spoofing model with Fourier-spectrum auxiliary supervision: a model listing and community ports; the official repository was not opened.
- Di Domenico, Franco, Borghi, Maltoni. Online adaptation of a morph detector with bona fide images at the gate, FG 2026 workshop: search snippet only; both pages returned an access error.
- FIQA-FAS (CVPR Workshops 2024) and a surveillance anti-spoofing paper on image quality (arXiv 2301.00975): result list only.

### 6.3 Recalled, not verified in this task

- Kim et al., bipartite auxiliary supervision with depth and reflection maps (ICCV Workshops 2019).
- Jourabloo et al., Face De-Spoofing: anti-spoofing via noise modelling (ECCV 2018).
- Liu et al., adaptive normalised representation learning for anti-spoofing (ACM Multimedia 2021).
- Chen et al., domain generalisation without domain labels for anti-spoofing, D2AM (AAAI 2021).
- Liao et al., domain-invariant vision transformer, DiVT (WACV 2023), and Huang et al., adaptive vision transformers, ViTAF (ECCV 2022). Both appear as baseline rows in tables I read, without a link.
- Fang et al., CF-PAD, causal clues and embedding statistics (WACV 2024). Named in [29].
- Zhou et al., MixStyle (ICLR 2021). Named in [42].
- Arashloo et al., anomaly formulation of spoofing detection (2017); Nikisins et al., anomaly detection against unseen attacks (ICB 2018); Baweja et al., anomaly-based unknown attack detection (IJCB 2020).
- Galbally et al., image quality assessment for fake biometric detection (2014).
- Deb et al., GrandFake, and Yu et al., joint spoofing and forgery benchmark JFSFDB. Named in [36].
- Seibold et al., partial morphs with region labels (2018) and reflection analysis for morph detection. In our planning record.
- NIST FATE MORPH reports (per-pool false detections, resolution effects). In our planning record.
- ISO/IEC 20059 on the evaluation of morphing attack resistance.
