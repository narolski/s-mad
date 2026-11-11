# Round 3 ideas, lens "turn the author's idea into a training method"

11 Nov 2026. Idea generator for ideation round 3. Nothing here was run. I read records and small result
files only. No sealed file was opened, no image was loaded, no GPU or cluster was used.

Terms. S-MAD = single-image morphing attack detection. AUC = area under the ROC curve (0.5 = chance).
EER = equal error rate. Host = one photo of one person. Rung = one image derived from a host (photo,
warp-only image, mirror self-blend, same-person blend, two-person morph). Twin = the image that went through
every operation of a blend except the mixing (for a landmark blend: the host warped to the same shape). Dose =
how much two different source images disagree where they were mixed. Zero-dose image = any image made from
one capture without mixing. LoRA = low-rank adaptation of a pretrained network. DiffAE = diffusion
autoencoder (the generator behind MorDIFF-type morphs); z_sem = its semantic code; x_T = its noise map.
E7 = the existing, approved shrink-and-enlarge history control.

The author's idea, in the lead's words: by making morphs of the same input image and of the same person we
can clearly catch the signal; inside one host, everything constant cancels.

---

## 1. What the first numbers say, and what they do not say

All numbers in this section are owners' first passes, one fold, not reviewed. They are leads.

Measured (files cited):

1. GAN latent morphs, CLIP pooled features, 52 held-out hosts
   (`experiments/PD1_signal-isolation-paired-differences/gan/first_pass_clip_pool_fold0.json`).
   A head trained only on same-person mixes ranks two-person morphs above one-photo reconstructions at
   AUC 0.78. The head trained on two-person morphs reaches 0.77. Inside a host the one-person head puts the
   morph above the reconstruction in 92% of hosts.
2. Landmark morphs, DINOv3 mean patch token, OpenCV-style engine, 107 held-out hosts
   (`experiments/PD1_signal-isolation-paired-differences/landmark/first_pass_dino_opencv_fold0.json`).
   One-person head: warp-only against two-person morph 0.933. Two-person head: 0.980. One band-power
   statistic alone: 0.912. Excess of the one-person head over that statistic: 0.021 [-0.037, 0.081].
   The one-person head scores mirror self-blends like two-person morphs (0.486).
3. Mirror self-blends are perfectly symmetric. A training-free mirror distance separates the mirror
   self-blend from the two-person morph at AUC 1.0 on both engines
   (`experiments/AF0/mirror_clip224.json`, position-aligned rows). In the diffusion autoencoder the mix of a
   photo with its mirror has left-right asymmetry 2.1 against 18.3 for a reconstruction
   (`experiments/AD1b/result.md`, 4 persons).
4. Softened copies of zero-dose images exist for 200 hosts of the landmark ladder: the photo and the
   warp-only image, each at two registered strengths (`/mnt/t7/smad_next/AF0/lists/ar1soft.csv`, 1,200
   images). No softened blend exists yet.

What I read from them:

- **Pairs overstate one-image performance.** In (1) the paired win rate is 0.92 and the unpaired AUC is 0.78.
  Under a simple Gaussian model this means about 70% of the score spread inside one class is a per-host
  offset. A loss that only compares images of the same host never touches that offset. At test time there is
  no twin, so the offset is the error. Removing it completely would lift 0.78 to at most 0.92 (expectation
  from the model, not a measurement).
- **"Transfers fully" may be softness.** In (2) the one-person head is 0.02 above a band-power statistic.
  The registered pass mark of the paired-differences experiment (PD1) is 0.05. So the landmark transfer
  could be "less fine detail", which a shrunk genuine photo also has.
- **The mirror partner brings its own shortcut.** In (3) a mirror self-blend can be told from everything
  else by symmetry alone. A head trained on mirror self-blends can learn "symmetric means positive".
  Passport-style photos are frontal and evenly lit, so this would raise false alarms where it hurts most.
- **"The second identity is weak" is not yet shown for landmark morphs.** The 0.65 is a projection on a
  mean direction in one GAN fold. For landmark morphs a probe trained directly on two-person against
  same-person blends reads 0.88 to 0.93 (`experiments/AR1/README.md`, gate G-c on frozen detector
  features), and the two-person head of PD1 reads 0.76. But same-person blends disagree less than two-person
  blends (median pixel difference to the host photo 15.1 against 18.8 grey levels, 9.6 for the mirror
  blend, OpenCV-style engine; `experiments/AR1/README.md`). So these probes may read "more disagreement",
  not "another person". No dose-matched comparison exists. Idea 3 builds it.

---

## 2. Answers to the four questions

### Question 1: which objective

I compared the options on what they do to the host offset, to softness and to one-image use.

| Objective | Good | Problem | Verdict |
|---|---|---|---|
| Pairwise ranking inside a host only (the PD1 heads) | host-constant cues cancel in training | the per-host offset stays free; unpaired 0.78 against paired 0.92 in the GAN pass | keep as one of two terms |
| Difference-vector supervision (learn the mean step, or force step vectors to agree) | easy to state | the mean-direction score is weaker than the paired head in the same GAN pass (0.73 against 0.77, both from two-person steps); the direction is not consistent across hosts for the identity step (63% of hosts) | reject as the main loss |
| Per-step multi-head (one output per ladder step) | gives a cross-talk table | already on the table from round 1; adds reporting, not detection | optional diagnostic outputs only |
| Graded-dose regression on the nominal mixing fraction | dose curve as a certificate | the nominal fraction cannot be read where the two sources agree (noted in `experiments/AF0/result.md`, wave 2); dose and softness move together | use the measured dose as an ordering inside the host, not as a regression target |
| Projecting out a softening direction (PD1 question 4) | cheap, linear | a fine-tuned network can relearn it; the softening direction comes from 80-pixel SMDD copies | diagnostic only |
| **Signal from pairs, noise from the genuine pool** (below) | host offset and nuisance steps are attacked by a term that contains no morph | needs softened and warp-only zero-dose images in the pool | **chosen** |

The chosen objective has two terms and nothing else.

- **Pair term.** Inside one host, every image with a larger measured dose must score above every image with
  a smaller dose, by a margin. Pairs cross the history levels: a native blend against a softened twin, a
  softened blend against a native twin. No pair ever joins two hosts.
- **Noise term.** Every zero-dose image, of every host, source, history and warp, is pulled to the same
  constant score (squared distance to 0). The pull is two-sided. The pool for this term is much larger than
  the set of hosts with ladders: it also holds photos that never get a blend.

Why this is the right shape. The pair term says what the signal is. The noise term says what it must not be:
anything that varies among genuine images. No term compares a blend of one host with a genuine image of
another host, so a file or source property that separates "morph files" from "photo files" has no term to
enter through. A normal two-class loss pushes genuine scores as low as possible, which rewards "this source
is always genuine". The two-sided pull does not.

The linear version is the classical matched filter: weight = (covariance of genuine images)^-1 times (mean
paired step). It can be tested on cached features in an hour.

### Question 2: what should the network be asked to detect

**"Two captures were mixed", not "two identities were mixed".** Reasons:

- It is what the pixels of a landmark morph contain: two sets of structure at slightly different places, each
  at part contrast. Filtering one photo cannot create a second eyebrow edge.
- A mirror blend and a same-person blend carry the same thing at a lower dose. A photo blended with its
  mirror already carries 40 to 76% of the two-person value of the blend-disagreement target (brief,
  established). A one-person head detects two-person morphs (leads above).
- For generator morphs that only average codes (StyleGAN latent midpoints), one image carries no trace of
  the second person beyond "this face is more average". Measured so far: 0.73 on exact landmark shapes
  (`experiments/ID0_identity-shrinkage-triage/result.md`), 0.58 to 0.63 against spread-matched renders
  (`experiments/FZ1/result.md`, not reviewed). That is weak and an attacker can rescale it away.
- Whether a second identity adds anything readable at equal dose is open for landmark morphs. Idea 3 decides
  it with a number.

What this means for the class definitions (`14_CLASS_DEFINITIONS.md`, awaiting the author):

- Genuine (one capture, admissible processing) stays the negative class of every error rate. The network is
  trained to give it one constant score.
- Morphing attack (two persons) stays the positive class. Every two-person morph is also a two-capture mix,
  so the error rates need no change.
- The third category should be split in two, because the detector treats the halves differently by design:
  **single-subject, no mixing** (warp-only image, one-photo reconstruction): trained to score as genuine,
  so the detector does not flag them under either class policy; and **single-subject, with mixing**
  (same-person blend, mirror blend): flagged by design, listed in their own table, never counted as false
  alarms and never as detections.
- The paper's sentence becomes: "the detector reports that two face images were mixed; it does not claim to
  see a second person". The step from a same-person blend to a two-person morph is printed as its own
  number, dose-matched (Idea 3).
- The record holds two rulings that do not agree (see section 6). The design works under both; only the
  label of one table changes.

### Question 3: from pairs to one image, and across families

- **One image.** The noise term is the transfer. After training, a genuine image of any host sits at the
  constant, so the one-image score is "distance above the constant" and one fixed threshold (a fixed
  quantile of the genuine development pool, never FRLL) serves every benchmark. One network, one forward
  pass, no twin, no reference, no gate.
- **Across families.** The pair term is taken inside a host and inside a family. The noise term pools the
  zero-dose images of all families at one constant. So a pass-through of a generator (a one-photo
  reconstruction) is pinned to the score of a camera photo. "This image was generated" is then noise by
  definition and cannot serve as evidence.
- **Which families can share a signal.** My expectation, to be tested, not a fact: landmark morphs
  superpose pixels; diffusion-autoencoder morphs superpose two noise maps (Idea 2 tests this); GAN latent
  midpoints superpose nothing. So I expect transfer between landmark and diffusion ladders, and I expect no
  transfer to GAN latent midpoints beyond averageness. The paper should say so and report GAN cells as a
  measured limit under both class policies.
- **Leave one family out.** Train on the self-ladders of two families, test on two-person morphs of the
  third against that family's pass-through. The DiM families (other diffusion samplers) are a held-out
  generator for free.

### Question 4: one-person self-morphs at scale, allowed operations only

The partner is the **lossless mirror image of the host**. It exists for every photo. Where a database has a
second photo of the person, that photo is a second partner. No second identity, no benchmark morph.

| Family | Zero-dose twin | One-person positive | Tools, all existing | Scale |
|---|---|---|---|---|
| Landmark | host warped to the target shape (the warp-only rung) | host and mirror warped to the same shape, blended by the engine's own blend line, with the spatial mixing fields the alpha-field probe (AF0) verified | unchanged OpenCV-style engine and FaceMorpher; mirror landmark map `experiments/AR1/mirror_perm106.json`; AF0 `af_morph.py` (pixel-identical to the engine at 0.5); approved shrink-and-enlarge call verified bit for bit (`experiments/AF0/wave4_verify.json`) | 25,000 SMDD genuine renders (landmarks on disk; the SMDD rebuild (SM1) already runs the engine on them), plus FRGC, colorFERET, FFHQ. About 150,000 tool calls: about 1 hour at the rate measured with 12 idle processes (2,000 to 3,200 images per minute, `experiments/AR1/README.md`); the loaded DGX is far slower, so this belongs on cluster CPU cores |
| Diffusion autoencoder | one-photo reconstruction | mix of the photo's codes with the codes of its mirror (Idea 2: noise map only) | A43 generator unchanged; job-list driver of the diffusion generation on Athena (DG1) already takes flipped sources and a mixing fraction | two inversions and two renders per host, about 28 s at the idle-DGX rate (13 s per inversion, 1 s per 20-step render); 5,000 hosts are about 40 GPU-hours at that rate; the A100 rate is not measured |
| GAN (optional) | render of the inverted code | render of the midpoint of the code of the photo and the code of its mirror | encoder inversion (e4e) with StyleGAN2, or the MIPGAN paths staged for the MIPGAN controls (AG1), which already include a mirror rung for 302 hosts | hundreds now, thousands with the encoder path |

Three additions keep the mirror partner honest:

1. **Break the symmetry.** Use mixing fields that differ between left and right (gradient, bump; they exist),
   mixing fractions below 0.5, and target shapes that are not the symmetric mean (the host's own shape, or
   a quarter of the way). Target shapes other than the tool's mean use the approved warp path with another
   target, as the warp-only rungs already do; each must be verified against the unchanged tool at the mean
   shape first.
2. **Symmetric decoy (needs a yes).** The left half of a warp-only image joined to its lossless mirror. It is
   perfectly symmetric and contains no mixing. Zero dose. It teaches that symmetry is not mixing. It uses
   only a lossless flip and pixel selection, but it is a new construction, so the lead or the author must
   allow it.
3. **Cross every image with history.** Photo, twins and blends each also pass the existing shrink-and-enlarge
   call at the registered strengths (the author approved this path for training images).

---

## 3. Idea 1 (rank 1): self-morph ladder training, signal from pairs, noise from the genuine pool

**One line.** Train one network with no second identity: positives are one-person blends with exact twins,
crossed with storage history; the loss ranks dose inside a host and pins every zero-dose image to one score.

**Signal.** Superposition: two different face images present in one image, seen as doubled fine structure.
The same thing at growing dose in mirror blends, same-person blends and two-person morphs.

**Relation to what is on the table.** It upgrades item 2 (paired differences, so far linear heads on three
small ladders) into a training method, and it adds an arm to item 1 (the history-crossed SMDD rebuild, whose
arms all use two-person morphs: `experiments/SM1_smdd-partner-audit-and-rebuild/prereg.md`). New parts: the
two-term objective, positives without any second identity at scale, the symmetry devices, and the direct
comparison with SelfMAD on the same training data.

**Training data.** Section 2, question 4. Two variants. (a) Field protocol: the 25,000 SMDD genuine renders
only. This is exactly the data SelfMAD trains on (`experiments/AD5_retrains-of-released-methods/README.md`),
so the comparison changes only how the self-made positives and their negatives are built. (b) Real photos:
FRGC and colorFERET persons outside the sealed validation set, and FFHQ. FRLL is never used. Per host: the
photo, two warped halves, three blends (uniform 0.5, uniform 0.25 or lower, one left-right uneven field),
each at native and two history strengths. Regions the source does not cover are blanked with one constant
colour in every image. The genuine pool for the noise term adds photos without ladders and their existing
processed copies (25,000 SMDD stored-small copies exist).

**Objective.** L = pair term + lambda times noise term, as in section 2. Dose for the ordering = measured
disagreement of the two warped images inside the face, weighted by the field, flat regions excluded (the
variant the AF0 controls ask for). Computed in memory while the blend is built. Batches are built by host:
16 hosts times 5 or 6 rungs, plus 32 pool images.

**Architecture.** The MADation recipe unchanged (CLIP ViT-L/14, LoRA rank 2 on query and value, linear
header), so the comparison with MADation changes data and loss only. One scalar output decides. Optional
extra outputs (history, warp) are diagnostics and are never combined with the score.

**Test time.** One image, the benchmark's standard crop, one forward pass, one fixed threshold.

**Ablations that tie the audit to the method** (this answers the area chair's objection that the two halves
of the paper do not meet):

1. No twins, no history crossing: positives against plain photos only. Expected: the SelfMAD failure
   reappears (history-matched genuine photos flagged). That would show the cause, on the same cells as the
   audit.
2. Twins, no crossing. 3. Twins and crossing, normal two-class loss. 4. Full method.
   Read for each: flag rate of history-matched genuine photos at one fixed threshold, and EER on the
   landmark cells.

**Controls.**

| Rival explanation | Control | Pass |
|---|---|---|
| Softness | crossed contrast: softened warp-only image against native blend of the same host; the best simple statistic points the wrong way there | AUC at least 0.85 |
| Softness, second view | rank correlation of the score with each of the 27 simple statistics inside the genuine pool | at most 0.2 in size (the record's own limit) |
| Storage history | FRLL genuine, native against history-matched, fixed threshold from native | at most 10% flagged, shift at most 0.3 standard deviations |
| Warp | photo against warp-only image | shift at most 0.3 standard deviations |
| Border | constant-colour blanking of uncovered regions in all classes | number unchanged within 0.02 |
| Symmetry by-product | symmetric decoy flag rate; AUC of the plain mirror-difference statistic on training positives against twins | at most 10%; at most 0.65 |
| Capture detail, expression | FRLL neutral against smiling genuine photos (never trained on) | share near 0.5; reported, no claim |
| Generator fingerprint | one-photo reconstruction against photo, for families in the pool | AUC 0.45 to 0.55 |
| Second identity | never in training; same-person against two-person reported, dose-matched (Idea 3) | reported |
| Tool fingerprint | train on the OpenCV-style engine only; test FaceMorpher, the approved Poisson set (H1), AMSL and WebMorph cells | reported per tool |

**First test, at most one day, existing data, frozen features, linear heads.**

- Data: landmark ladder (AR1), 536 hosts, both engines, rungs photo, warp-only (two kinds), mirror blend,
  same-person blend, two-person morph (`/mnt/t7/smad_next/AR1/img`); softened photo and warp-only image of
  200 hosts (`/mnt/t7/smad_next/AF0/lists/ar1soft.csv`); AF0 images of 663 other persons: zero-field images,
  warped halves, uniform 0.25 and 0.5 blends (`/mnt/t7/smad_next/AF0/img`); FRLL and corrected MAD22 genuine
  photos native and history-matched (scoring only); benchmark subsample `bench_s`.
- Features: CLIP ViT-L/14 class token and mean patch token at 224, DINOv3 ViT-L/16 mean patch token at 512
  (caches under `/mnt/t7/smad_next/PD1/landmark/feat` and `/mnt/t7/smad_next/AF0/feat`; the 1,200 softened
  images may need extraction, minutes).
- Heads, all trained on one-person pairs only (mirror blend against its exact twin, same-person blend against
  its twin), 5 folds by person with the PD1 folds: (A) the PD1 paired logistic head; (B) matched filter with
  the genuine covariance from photos, warp-only images and AF0 zero-field images; (C) the same with softened
  copies in the covariance; (T) the two-person head as reference; (N) positives against plain photos, no
  twins.
- Metrics on held-out persons: (i) crossed contrast, softened warp-only (61-pixel strength) against native
  two-person morph, with the folded AUC of the best of the 27 statistics beside it; (ii) flag rate of
  history-matched FRLL and MAD22 genuine photos at the threshold that flags 5% of the native ones; (iii) AF0
  zero-field against uniform 0.5 blend (unseen persons, exact twins, two-person positives never seen in
  training); (iv) unpaired against paired separation, to see whether (B) closes the gap.
- Same heads on the GAN blocks and the diffusion blocks of PD1 for metric (iv) only.

**Kill and pass numbers.**

- Kill: head (C) below 0.75 on the crossed contrast, or more than 15% of history-matched FRLL genuine photos
  flagged, or below 0.85 on AF0 zero-field against uniform 0.5. Then the one-person signal in these
  features is softness and the line stops before any fine-tuning.
- Pass: crossed contrast at least 0.85 with lower bound above 0.75; at most 10% flagged on both
  history-matched sets; AF0 contrast at least 0.93 and within 0.03 of head (T).
- Sub-claim "the noise term is worth it": dead if (B) does not beat (A) by 0.03 unpaired AUC in at least two
  of the three families; then use a normal two-class loss on the crossed ladder.

**Path to state of the art.** Variant (a) is scored on the published tables (FRLL-Morphs, corrected MAD22,
MorDIFF) beside SelfMAD and MADation, each release through its own crop with its published number
reproduced (own-crop re-score, RS1). The claim is: equal or better EER on the landmark cells natively, and
the lowest false alarms of all detectors on history-matched genuine photos at one fixed threshold. Diffusion
cells come from Idea 2. GAN cells are reported under both class policies as a measured limit. Published
bars to meet are those quoted in `ideas/CONSOLIDATED_v2.md` (AMSL 7.26% for MADation ViT-L/14, 3.85% for
ViT-B/16); I did not check other published values.

**Compute.** First test: up to 0.3 GPU-hours for missing features, CPU heads, half a day with review. Full:
ladder build 2 to 6 hours on 48 CPU cores; one fit about 8 A100-hours (3 million image passes at the speed in
the MADation release log); two variants, four ablations, one pre-declared seed plus four more for the spread
(all reported, none picked): about 150 A100-hours, 1.5 days on ten cards.

**Risks.** The crossing may cost native accuracy because part of today's separation is softness. The mirror
partner may teach symmetry despite the devices. One-person doses are lower than two-person doses, so the
network must hold above threshold outside its training range; AMSL and WebMorph hide ghosting by splicing and
retouching and are the cells most at risk. SMDD renders are not camera photos.

---

## 4. Idea 2 (rank 2): noise-only mirror mix, the one-photo positive for diffusion morphs

**One line.** Split the two codes of the diffusion autoencoder: mix only the noise map of a photo with the
noise map of its mirror and keep the photo's own semantic code; use this as the one-photo positive, and use
the full two-by-two to decide what a detector reads in a diffusion morph.

**Why.** A DiffAE morph mixes two things at once: the semantic codes (linear) and the noise maps (on the
sphere). The record cannot say which one a detector reads. A frozen-feature probe separates two-person
morphs from one-photo reconstructions at 0.945 to 1.000 at matched step count (`experiments/FZ1/result.md`,
not reviewed), far above simple statistics (0.66 to 0.70). A round-1 generator already suspected the noise
map: mixing two noise maps may superpose fine detail of two images. Nobody proposed to separate the codes.
The mirror of a photo is as far from the photo in noise-map space as a stranger is (cosine distance 0.98
against 0.99, `experiments/AD1b/result.md`, 4 persons). So a noise-only mirror mix should carry the full
noise-map trace with one photo, one identity code, and no symmetric face, because the semantic code that
lays out the face stays the host's.

**Signal.** Expected, not measured: fine detail that belongs to two noise maps instead of one capture. It is
the diffusion form of "two captures were mixed".

**Design: five renders per host, generator functions unchanged.**

| Arm | Semantic code | Noise map | What it isolates |
|---|---|---|---|
| reconstruction | host | host | pass-through, zero dose |
| noise-only mix | host | host mixed with partner | noise-map mixing alone |
| semantic-only mix | host mixed with partner | host | semantic (identity) mixing alone |
| full mix | mixed | mixed | the published morph recipe |
| fresh noise | host | new random noise | "the noise map is not this photo's", no mixing at all |

Partners: the mirror (one photo), a second photo of the person, another person. The semantic-only mix with
another person is the second-identity step in isolation. The fresh-noise arm matters for the audit: if a head
flags it like a mix, then what separates a morph from a reconstruction is "the reconstruction copies its
photo too well", and the fair one-photo twin for a diffusion morph is the fresh-noise render, not the exact
reconstruction.

**Training use.** In Idea 1's ladder the diffusion family contributes: zero-dose = reconstruction (and
fresh-noise render, if it is ruled a one-photo pass-through); positive = noise-only mirror mix at several
mixing fractions. No second identity. Objective, architecture and test-time use are those of Idea 1.

**Controls.** Simple-statistic floor per contrast (the seven statistics of FZ1 plus the mirror-difference
statistic). Step count equal in all arms (20). Same writer and size for all arms, as DG1 registers.
Reconstruction against photo must stay near 0.5 for the trained head. Second photo pool: FRGC and colorFERET
for fits, FRLL only for scoring. Second identity: semantic-only mix with another person, reported.

**First test.**

- On existing images, can only kill. (1) The one-person head of the diffusion arm of PD1 (same-person mix
  against reconstruction, 516 FERET and FRGC hosts; `experiments/PD1_signal-isolation-paired-differences/diffae/prereg.md`):
  two-person morph against reconstruction on held-out hosts, and on FRLL at 20 steps. (2) After tonight's
  full run of the identical-and-mirrored-inputs check (AD1b): do heads trained on two-person morphs rank
  the 32 mirror mixes above their reconstructions? (3) CPU only, from the codes AD1b saves
  (`/mnt/t7/smad_next/AD1b/gen/codes_xT.npz`, when written): is a noise map plain white noise, or does it
  correlate with the photo's own edges? If it is white, superposition in the noise map is unlikely.
- Decisive part, needs new renders (not existing data): five extra renders per host for the 536 hosts of DG1
  set B (noise-only and semantic-only mix with the mirror, the same two with the other person, fresh
  noise). The inversions are already in that plan; the extra work is about 2,700 renders at 20 steps, about
  1 GPU-hour at the idle-DGX rate. Then frozen CLIP and DINOv3 features, heads trained on noise-only mirror
  mixes against reconstructions, 5 folds by person, tested on full two-person morphs against
  reconstructions.
- Needs a yes: calling the unchanged encoder, mixing and render functions with one code mixed instead of
  both. No image operation is added.

**Kill and pass numbers.**

- Kill on existing data: the PD1 one-person head below 0.60 on two-person against reconstruction, or mirror
  mixes not ranked above reconstructions (below 0.60).
- Kill on the decisive part: the head trained on noise-only mirror mixes below 0.70 on full two-person
  morphs against reconstructions while the head trained on two-person morphs is at 0.90 or more.
- Pass: at least 0.85, within 0.05 of the two-person head, at least 0.05 above the floor, and
  reconstruction against photo between 0.45 and 0.55.
- Reading rule, not a kill: if the fresh-noise arm is flagged like the mixes, the claim is renamed and the
  diffusion twin changes as said above. If the semantic-only mix with another person reaches 0.75, identity
  mixing is readable in diffusion morphs and the claim of Idea 1 must say so.

**Path to state of the art.** MorDIFF and the six DiM cells are in the published tables. Three adapted
releases cannot separate a two-person diffusion morph from a one-photo reconstruction (0.40 to 0.49,
established). A network trained on noise-only mirror mixes that separates them at 0.85 or more, having never
seen a two-person diffusion morph, is ahead on the column that matters, and its native numbers are reported
beside under both class policies. DiM samplers are the held-out generator.

**Compute.** Existing-data part: CPU, no new GPU time beyond PD1. Decisive part: about 1 GPU-hour of renders
plus 0.3 GPU-hours of features, one day including queue. Full: 5,000 hosts (FFHQ, FRGC, colorFERET), two
inversions and three renders each, about 40 GPU-hours at the idle-DGX rate (A100 rate not measured), half a
day on eight cards.

**Risks.** The noise map may be close to white noise, so that a mixed map equals a fresh one; then the idea
turns into the fresh-noise finding, which is still useful for the audit but is not a mixing detector. The
trace may live in fine detail and die at benchmark storage sizes. A fresh-noise render may be ruled not
admissible. The trace may be specific to this autoencoder and absent in other diffusion morphers.

---

## 5. Idea 3 (rank 3): dose-matched test, and an optional head, for the second-identity step

**One line.** Compare two-person and same-person blends of the same host at equal measured disagreement; if
nothing separates them, the paper states that one image shows mixing and not a second person; if something
does, it becomes a second, separately declared output.

**Signal.** Whatever is left of "two persons" when the amount of mixing is equal: averaged face shape,
structures that do not belong together. Expected to be small.

**Design.** For each host: the same-person blend at 0.5, and a two-person blend whose mixing fraction is
lowered until its measured disagreement inside the face equals that of the same-person blend. Two geometry
versions: each blend in its own mean shape (shape averaging stays in, it is a fair identity cue), and both in
the host's own shape (texture only). Within-host pairs, label "two persons". If it passes, the head is a
second output on the same backbone, trained only on these pairs, reported as the identity step, never
combined with the mixing score. Test time: one image, the same forward pass.

**Controls.** Dose matching itself removes softness and blend strength (the floor statistics must be at
chance on the matched pairs, to be printed). Same host and same kind of second photo in both blends (the
composition rule of the landmark ladder). Exact landmark-shape score beside it, to say how much is shape
(0.69 for same-person against two-person on exact shapes,
`experiments/ID0_identity-shrinkage-triage/result.md`). Background and clothing blanked with a constant
colour, because a same-person blend of two sessions ghosts the background like a two-person morph
(`experiments/AR1/README.md`, section 8).

**First test, existing images.** FaceMorpher graded mixing set (300 hosts, fractions 0 to 0.5 with the
partner) and the same hosts' same-person blends (`/mnt/t7/smad_next/AR1/img/frgcferet/fm_graded`,
`.../facemorpher/R3`). Dose proxy on CPU: mean absolute pixel difference to the host's warp-only image
inside the landmark hull. Pick per host the graded level closest in dose to the same-person blend. Probe:
logistic head on cached CLIP and DINOv3 features, 5 folds by person, two-person at the matched level against
same-person. FaceMorpher is the descriptive engine, so the deciding version needs matched uniform fractions
built with the OpenCV-style engine through the verified AF0 path (CPU minutes, new images of an approved
kind).

**Kill and pass numbers.** Kill: dose-matched AUC below 0.60 with upper bound below 0.65 on both feature
sets. Then no identity output, and the paper says so. Pass: at least 0.75 with lower bound above 0.65, at
least 0.05 above the floor on the matched pairs, and at least 0.65 in the texture-only geometry.

**Path to state of the art.** It does not change benchmark numbers. It makes the claim defensible: it tells
the reader, with one number, whether the detector could ever separate a same-person blend from an attack, and
so whether the "single-subject, with mixing" row can be anything but flagged.

**Compute.** First test CPU only, 1 to 2 hours. Deciding version: CPU build in minutes, 0.2 GPU-hours of
features. No extra training run: the head rides on Idea 1's fits.

**Risks.** The pixel-difference proxy may not match dose well enough; the measured disagreement of the two
warped images is better but needs the builds. A pass may still be shape averaging only, which an attacker
controls through the warp. Small sample (300 hosts).

---

## 6. Alternatives I rejected

- **Score the test image against a twin built at test time** (blend the test image with its own mirror and
  score the step). It would cancel the host offset at test time. But the size of that step grows with the
  fine detail the image has, so a soft genuine photo looks "already mixed". It also needs two passes, which
  may be read as fusion.
- **Mirror-difference input.** Measured weak on landmark morphs: warp-only against two-person 0.60 to 0.68
  (`experiments/AF0/mirror_clip224.json`, not reviewed).
- **An identity head as the main output.** The identity step is unsettled; Idea 3 gates it.
- **Training-time product with a simple-statistics model** (the network only gets credit for what the
  statistics cannot explain). Attractive because it needs no image operation. Rejected as the default
  because it adds a second model during training and the noise term does the same job when the genuine pool
  spans the statistics. Kept as a fallback if the registered softening strengths cannot balance the pool.
- **Same-person second photo as the only partner.** Exists only for databases with two sessions, mixes
  session and expression differences into the positive, and cannot use SMDD or FFHQ.
- **Nominal mixing fraction as a regression target.** See question 1.

---

## 7. For the lead: things noticed in the records

1. "The second identity is weak (0.65)" rests on one GAN fold and a mean-direction projection. Landmark
   probes trained directly on two-person against same-person blends read 0.88 to 0.93
   (`experiments/AR1/README.md`, gate G-c). No dose-matched control exists, so neither reading is safe.
2. Rulings disagree. `experiments/AR1/README.md` records "a same-person morph counts as a morph".
   `NOTEBOOK.md` says same-person morphs are a side study. `14_CLASS_DEFINITIONS.md` (awaiting a yes) puts
   them outside every error rate.
3. In the landmark first pass the one-person head is 0.02 above one band-power statistic and scores mirror
   blends like two-person morphs. Softened blends do not exist yet, only softened zero-dose images, so the
   crossed test is one-sided for now.
4. The warp-only rung of the landmark ladder is not the exact twin of the two-person morph (it is warped
   toward the same person's shape, the morph toward another person's). Exact twins for two-person blends
   exist only in the AF0 images.
5. Mirror blends are separable from two-person morphs by symmetry alone (AUC 1.0, training-free). The
   mirror arms planned at mixing fraction 0.5 in the diffusion and MIPGAN generation jobs will carry this
   by-product.
6. The exact one-photo reconstruction may be an easy twin for diffusion morphs; a fresh-noise render is
   another unchanged one-photo run and is in no plan.
7. Paired win rate 0.92 against unpaired AUC 0.78 in the GAN pass: pair statistics overstate one-image
   performance and should be printed with the unpaired number beside them.
8. Notebook entries are not in time order (entries dated 12 Nov 00:20 come before entries dated 11 Nov
   17:15), and the notebook says Athena is usable while the brief says it is expected.

## 8. Not verified

- Every number from "New today" and from first-pass files is unreviewed.
- That the noise map of the diffusion autoencoder carries capture detail: taken from a round-1 generator's
  note, not measured by anyone.
- That the engines run with target shapes other than their own mean without a change beyond the approved
  warp path: must be verified against the unchanged tool before use.
- Fit time per network: estimated from the speed in the MADation release log, not measured on an A100.
- Published benchmark values other than the two quoted in `ideas/CONSOLIDATED_v2.md`.
