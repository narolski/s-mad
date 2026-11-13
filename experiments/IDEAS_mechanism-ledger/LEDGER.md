# Mechanism ledger, ideas and literature role (IDEAS)

Version 1, started 13 Nov 2026 18:55 CET, written 18:56-19:07 CET (machine clock, `date`; first commit 6db5154 at 19:07). Owner: the standing ideas
and literature agent (IDEAS, OWNER_BRIEF "Five standing roles", item 1). **Proposals only.** Nothing here was run,
scored, trained or computed on an image. No benchmark file, no `valx`, FST or A12SP file and no image was opened. The
numbers quoted from our record come from committed result files named beside them; numbers quoted from papers come
from pages I opened in this session unless marked otherwise.

Read before writing: `OWNER_BRIEF.md`, `18_EVENING_CONCLUSIONS_20261113.md`, `experiments/SA1_shortcut-audit-table/result.md`,
`experiments/reviews/STRATEGIST_EVENING_20261113.md`, `experiments/NEXT_method-selection-rule/prereg_draft.md`, the 13 Nov
entries of `NOTEBOOK.md`, and, to avoid re-proposing what is already settled: `03_LITERATURE_AND_METHODS.md`,
`ideas/CONSOLIDATED_v3.md`, `ideas/round3/physics_vetting.md`, `ideas/round3/mechanism_vetting.md`, the identity-shrinkage
triage (ID0) result, the mirror-asymmetry test (AS0) result, the blend-difference attribution (BD1) result, the
look-alike pair search plan (LA1), and part 3 of the reads of the existing networks (PR1).

## The question every entry answers

The candidate (arm Sb, CLIP ViT-B/16 + LoRA, frozen at seeds 403-407) detects blending inside the face but has no
demonstrated second-identity signal (same-person morphs flagged 83-90%, same-person splices 31-48%), reacts to a
blanked-in border (2.9-16.3% of camera photos), responds to rendering on GAN and diffusion images, and is not shown to
beat the best single hand-made statistic (0.873-0.906 against 0.886). A mechanism is worth a training arm only if it
gives a reason why **a morph of two people must carry the signal while a genuine photo, a same-person morph and a
one-photo re-render must not**, and if a cheap test on development data can kill it.

Allowed image operations used by the tests below (OWNER_BRIEF line 41): constant-colour region blanking, the approved
warp script `h1_build.py`, the unchanged OpenCV and FaceMorpher morphers, existing E7 outputs, lossless PNG. Two
measurement steps need the lead's confirmation that they count as measurements (precedent cited): blanking applied
in memory to an aligned 112 px face-recognition crop (the registered glintr100 route of `src/AR1/fr.py`, used by AR1
and BD1, already does an in-memory similarity crop); in-memory FFT band images (registered as an allowed measurement in
the mirror-asymmetry test, AS0 `prereg.md` "Bands"). No image is written by any proposed test.

## Version 3 (13 Nov 2026, 21:45-21:49 CET by the machine clock): tonight's outcomes, and where a real effect is still possible

Nothing in this version uses, cites or was informed by the sealed MAD22 read. I did not open
`experiments/FINAL_sealed-benchmark-read/`.

### Outcomes of the four cheap single-image identity tests (all reviewed)

| Test [ID], ledger entry | Registered outcome | What it means | Source |
|---|---|---|---|
| Regional identity disagreement [RI1], M1 | **"inconclusive: P1 invalid (projection carries scale)"**: oracle premise 0.702, but its validity gate gave 0.934 / 0.873 against the required [0.40, 0.60]. Single image: S4 vs S3 0.540, R4 vs R3 0.595, against simple-cue floors 0.773 and 0.793; within D 0.522 (pure-D reference 0.524); gain over the hand cues −0.0002 | occluded face-recognition embeddings show no second identity; licensed sentence "Occluded face-recognition embeddings did not reveal a second identity in single images". The review traces the gate failure to cos_HB ≤ 0.65 < 0.68 ≤ cos_HS. M1 is not closed in principle (a trained region encoder is untested), but its off-the-shelf route is | `experiments/RI1_regional-identity-disagreement/result.md`; `experiments/reviews/REVIEW_TB1S_ME1_RI1_20261113.md` findings 6-7 |
| Texture band profile [TB1], M2 | oracle gain over band energy and landmark displacement +0.010 (**falsified**); single image 0.654 against the all-cue floor 0.773 (difference −0.118 [−0.151, −0.087]); equals the best single cue (0.657); its band statistics separate storage history as well as the classes (0.657) | closed | `experiments/TB1_texture-band-profile/result.md`; same review, findings 3-5 |
| Layer misregistration echo [ME1], M13 | oracle not measurable with the phase-correlation estimator (non-finite on about 91% of pairs; the calibration R2w4 against R2w failed on 142 of 291 hosts); single image "not measured" by the code, "invalid (control)" by the registered text (R2w4 vs R0 0.002, S0 vs R2w4 0.991) | the chosen echo statistic records resampling history (exactly 0 after one warp or one downscale on 287 of 291 warp-only images), not a second layer. The mechanism is not decided; the estimator failed | `experiments/ME1_layer-misregistration-echo/result.md`; same review, findings 1-2 |
| Nuisance erasure [NE1, NE1b], M10 (and M7 through its probe) | border cue linearly decodable, but mean-based erasers (rank-7 span, LEACE) leave 28-74% of the excess border flags: bordered copies keep 2.5-4.7 times the logit spread (a dispersion effect no first-moment eraser can fix); the splice probe on frozen features gains +0.003 to +0.039 over the frozen head (best 0.791), inside the simple-cue floor 0.773 | **line closed**: erasure cannot remove the border false alarms, and the frozen features hold no splice information beyond what simple cues give | `experiments/NE1_nuisance-erasure/result_ne1b.md` |

### Two further facts folded in

1. **Hard negatives by construction are the one lever that moved a two-person-versus-same-person ranking.** The
   protocol ablation (AB1 amendments 4-6, `experiments/AB1_protocol-ablation-and-replication/result.md`): removing the
   matched same-person and seam-only splice negatives (Sp) loses Sb's better ranking of two-person over same-person
   whole-frame morphs at equal blend energy (−0.049 AUC, 5 of 5 seeds); splice positives alone add nothing (−0.008
   [−0.033, +0.022]); the frozen networks show the same direction (+0.051 over B). But ranking is not rejection: every
   arm still flags most same-person whole-frame morphs (R3 own-rule flags A 0.99, B 0.93, Sb 0.85, Sp 0.89). Count and
   class mix are not controlled; the 2 x 2 with volume controls (SpV, BN, BV) is queued as batch C (WCSS 6316845).
2. **The standing adversary's floors** (`experiments/ADV_shortcut-floors/FLOORS.md`):
   - a shortcut-only learner trained on the candidate's own training list flags 44-48% of development same-person
     splices and 72-86% of same-person morphs, close to the candidate's 31-48% and 83-88%: **the candidate's
     same-person false alarms are what hand-made statistics learn from the same rows**;
   - at equal blend energy (within BD1 D quintiles) the two-person excess over same-person morphs is in luma texture
     statistics (0.723), not chroma (0.540) (H-new-3, "falsified" for chroma).
   With cos_HB ≤ 0.65 < 0.68 ≤ cos_HS, the luma excess is real but cannot yet be called identity: on our ladder "two
   people" and "two dissimilar inputs" coincide.

### Answer: the directions with the best chance of a real effect in the remaining time

Four cheap single-image statistics (regional FR, band profile, echo, erasure probes) gave nothing above simple blend
statistics. The evidence points away from a new statistic and towards **changing what the training data force the
network to separate**: that is the only intervention that moved the same-person ranking (AB1), and the residual failures
are a learned property of the training list (ADV). Three directions, ranked.

#### Direction 1 (rank 1): matched same-person negatives for whole-frame morphs, in the spirit of S3 [proposed: shape-matched same-person morphs, HN1]

**Why the same-person arm (SE1) mostly shifted the operating point** (`experiments/SE1_seam-shortcut-training-arm/result.md`,
"Post hoc descriptive readings"):
- *Its negatives were not matched to its positives.* A natural same-person morph R3 = blend(H, S) differs from the
  two-person morph R4 = blend(H, B) not only in identity but in everything that tracks input dissimilarity: landmark
  displacement W (oracle 0.869 by itself, TB1), blend-difference energy D, luma texture energy (ADV 0.723). The cheapest
  rule for such classes is a threshold on how different the two inputs were, which lowers the decision point without
  improving the ranking: R4 vs R3 AUC only 0.880-0.912 → 0.911-0.926, and at a threshold giving Sb SE's R4 miss rate, Sb
  itself flags R3 at 0.28-0.38, about SE's 0.25-0.32.
- *Most of its new negatives taught another cue.* 674 of the 830 new negatives were mirror self-morphs, which a symmetry
  cue separates: SE flags 0.00-0.01 of mirror self-morphs against 0.25-0.32 of ordinary same-person morphs.
- *Its residual flags are a host property and a label conflict.* 23 development hosts are flagged on 4 of 4 seeds;
  training flags (0.22-0.27) are close to development flags; host order correlates 0.83 with Sb's. For hosts whose two
  sessions differ strongly, R3 looks like R4 on every cue the network can use.
- *Why S3 worked where R3 did not.* Each S3 negative shares with its S4 positive the host photo, the hull, the outer
  region and the warp geometry; only the inner content differs, so the gradient sees a paired contrast. AB1 shows that
  this matching, not the extra positives, carries the gain.

**The matched version.** For each training two-person morph of host H with partner B, build a same-person negative from
H and a second photo S of H **at the two-person geometry**: H and S each warped once by the approved warp (the
`h1_build.py` path used for the warp-only images R2w4) to the mean landmarks of H and B, then blended with the same
alpha; and build the positive with the same code from H and B. The pair then shares the host photo, the target
geometry, the number of warps, the blend code, the alpha and the storage. It differs in whether the second layer's
texture is H's own other session or B's. W, the target mean shape and the warp count are equal by construction; D and
luma energy remain free and are printed. Also:
- keep natural R3 negatives but drop mirror self-morphs (they teach symmetry);
- stored-small copies of both members, as for every protocol rung;
- paired sampling: each positive and its matched negative in the same minibatch.
- Open point for the lead and the author: averaging two approved warps is a new composite (like the splice composite of
  amendment 7b), not a call of the unchanged morpher. Building both classes with the same composite code is what makes
  the pair matched. If only the unchanged morpher may be used, the next best is the unchanged engine on (H, S) after S
  is warped to B's landmarks; that adds one warp to the negative side and needs a warp-count control (a warp-only image
  of S with the same two warps, as a genuine row).

**Cheapest decisive test (before any fit, CPU only).** Build the pairs for the 291 development and test hosts only, and
ask the standing adversary for its floors on the new contrast (positive composite against shape-matched negative), within
D quintiles, all-cue and luma-only.
- All-cue floor ≤ 0.60 and luma ≤ 0.60: the construction removes the shortcuts the candidate is known to use; a network
  that separates the pair must use something else. Go to the arm.
- Floor ≥ 0.75: the construction leaks (warp strength, energy); fix it before any fit.
- In between: the arm may run, but its gain counts only beside this floor.
- Cost: about 4-6 CPU-hours to build (about 1,200 images with stored copies); floors under 1 CPU-hour. For the arm, the
  same build on the PN1 training hosts, about 6-8 CPU-hours.

**What makes it an arm.** Sb plus shape-matched negatives, five seeds 408-412 on WCSS H100. Batch C fits take about 36
minutes, so about 3-4 GPU-hours. Read with the battery. It earns a claim if, on 4 of 5 seeds:
1. the composite pair ranks ≥ +0.05 above its own list's shortcut learner;
2. natural R4 against R3 within D improves by ≥ +0.03 over Sb (a ranking gain, not a threshold move);
3. same-person flags fall **at matched two-person recall** (at the threshold that gives Sb's R4 miss rate), not only at
   the own rule;
4. the guards of the selection rule (NEXT) hold.
Batch C is read first or together, so that a gain is not volume. Even then, on our ladder the claim is "separates two
people from two sessions of one person at equal geometry", not "reads identity", until Direction 2 exists.

#### Direction 2 (rank 2): the look-alike set [LA1; entry M12], now also as matched training material

Unchanged in substance from version 2: the smallest decisive evaluation set is 100 disjoint look-alike pairs with 100
same-person pairs matched on FR similarity and W (±0.076 at 100 per class; about 200 per class for a true AUC between
0.62 and 0.68). What changes:
- it is the only route to the word "identity" for anything Direction 1 achieves, because cos_HB and cos_HS do not
  overlap on our ladder;
- the shape-matched construction of Direction 1 should be applied to the look-alike pairs too, so the decisive row is
  "look-alike two-person composite against shape- and similarity-matched same-person composite";
- cheapest decisive step: LA1-0 (labelled tail calibration, about 0.5 GPU-hour), which says whether 100 matched pairs can
  exist at all. If it predicts fewer than 50, the paper should say the identity question cannot be decided with the
  available data, and report Direction 1 as "two sessions against two people at equal geometry";
- arm: only after Direction 1 shows a ranking gain; look-alike composites then join training as positives with their
  matched negatives (a few hundred rows at most).

#### Direction 3 (rank 3): what the literature offers for learning "two sources" without identity labels

Three families; none gives a ready "two identities" detector, one gives a useful training target.
- **Self-consistency learning.** Huh, Liu, Owens, Efros, "Fighting fake news: image splice detection via learned
  self-consistency", https://arxiv.org/abs/1805.04096 (abstract opened; the page lists only arXiv, the paper is usually
  cited as ECCV 2018): trained on real photos only, with EXIF metadata as free labels for "do these two patches come
  from one imaging pipeline". Zhao et al., "Learning self-consistency for deepfake detection", ICCV 2021,
  https://arxiv.org/abs/2012.09311 (opened): pair-wise patch consistency of source features plus a generator of
  inconsistent images; cross-dataset mean AUC 86.03% → 92.18%. For us this covers splices (inner against outer), where
  S4/S3 already are such generated inconsistencies. In whole-frame blends every patch is a mixture, so patch
  consistency reads "mixed against pure", not two persons. Low.
- **Layer decomposition.** Gandelsman, Shocher, Irani, "Double-DIP", https://arxiv.org/abs/1812.00467 (opened): a mixture
  of layers has more complex internal statistics than either layer, so coupled priors can separate them per image. A
  same-person morph is also a two-layer mixture, so this reads "two captures", and it costs minutes of GPU per image.
  Low.
- **Source counting as the target.** Stöter, Chakrabarty, Edler, Habets, "Classification vs. regression in supervised
  learning for single channel speaker count estimation", ICASSP 2018, https://arxiv.org/abs/1712.04555 (opened): a
  network trained on synthetic mixtures with the number of sources as the label. The idea that transfers: predict two
  counts, **captures** and **persons**, from labels that construction gives for free (one capture; two captures of one
  person; two persons), instead of one binary label. The binary head then no longer has to put "two captures of one
  person" on the genuine side using the very features that detect blending: blend evidence gets its own output, and the
  person count must rest on what separates the last two classes. This is the three-level ordinal idea of round 3
  (`ideas/round3/mechanism_vetting.md`, idea 1, "revise"), now with matched data that make it meaningful. No test is
  cheaper than the arm. Cost: an extra head on the Direction 1 arm, five more fits, about 3-4 GPU-hours. Arm condition:
  the persons output separates the Direction 1 pairs ≥ +0.05 above the shortcut floor and beats the binary Direction 1
  arm by ≥ +0.02 on 4 of 5 seeds; otherwise an ablation row.

### Ranking, version 3 (supersedes version 2)

| Rank | Direction or mechanism [ID] | Status | GPU-h | CPU-h | Prior (my estimate) |
|---|---|---|---|---|---|
| 1 | Shape-matched same-person negatives for whole-frame morphs [HN1, proposed] | proposal; needs the lead's and the author's word on the composite | 0 for the floor test; 3-4 for the arm | 10-14 | 0.35 that the floor test passes; 0.25 that the arm then shows a ranking gain |
| 2 | Look-alike set [LA1; M12] | plan; LA1-0 drafted; build is an author item | 0.5, arm later | 4-8 | n/a (control) |
| 3 | Count target, captures and persons as two outputs, on Direction 1 data [variant of HN1] | proposal | 3-4 | — | 0.2 |
| 4 | AB1 batch C (volume-controlled 2 x 2) | queued (WCSS 6316845) | in queue | — | decides whether the matched-negative gain is volume |
| 5 | Border: data route (Sbx) under the selection rule; paired invariance loss [M9] | Sbx queued; erasure route closed by NE1b | — | — | — |
| 6 | Group DRO / JTT [M7] | lowered: NE1b found no splice information beyond the simple-cue floor to reweight towards | 6-12 | — | 0.1 |
| 7-11 | Landmark shape typicality [M4], noise mixing [M3], demorphing [M5], IRM / V-REx [M8], SBI / SelfMAD [M11] | unchanged, low | — | — | — |
| parked | Layer misregistration echo [ME1; M13] | estimator failed, mechanism undecided; a new estimator needs a new design and would still meet the W confound | — | — | — |
| closed | Regional identity, off-the-shelf FR [RI1; M1] | inconclusive (P1 invalid); Δ below every floor | — | — | — |
| closed | Texture band profile [TB1; M2] | falsified | — | — | — |
| closed | Nuisance erasure [NE1, NE1b; M10] | closed | — | — | — |
| closed | Frequency traces of warping [M6] | closed by design | — | — | — |

## Version 2 (13 Nov 2026, 19:55-19:58 CET by the machine clock): what the first test outcome changed

**Texture band profile (TB1, entry M2): closed as a texture mechanism.** Sources: `experiments/TB1_texture-band-profile/result.md`
(premise read at 19:37; amendment 2 read at 19:51, commit caa9404; review applied in f6bb559), the post-result review of
the premise `experiments/reviews/REVIEW_TB1_PREMISE_20261113.md` (needs qualification) and the review of amendment 2
`experiments/reviews/REVIEW_TB1_A2_20261113.md` (accept with corrections).
- The registered premise verdict "holds" stands: the cross-fitted band profile of the oracle half-difference separates
  two-person from same-person pairs at 0.758 within D quintiles (component-bootstrap interval [0.701, 0.801]).
- But the binding post hoc amendment 2 rule gives the profile a gain of only **+0.010 [−0.006, +0.021]** over
  [log band-limited energy E, log landmark displacement W] (base 0.888): registered verdict **"falsified"** (bar +0.02).
  By database: FRGC +0.018 (reviewer's interval about [+0.003, +0.030]), colorFERET −0.016 (n = 56).
- **My M2 prediction is contradicted.** I predicted relatively more mid-band energy for two people. The review finds the
  signal is a *smaller finest-band share* (B5 median 0.087 against 0.129; B5 share alone 0.708 within D), most simply
  read as extra structured energy diluting a fine-scale noise floor that both classes share (review H-new-1, not
  falsified). The FRGC / colorFERET split (0.864 against 0.554) looks like a source-detail effect.
- Combined licensed sentence (TB1 result, amendment 2): "two-person pairs differ from same-person pairs mainly through
  larger band-limited energy and larger landmark displacement ... not a texture trace of a second identity and not a
  detector." No arm may rest on a profile-shape premise.
- Consequence for the ledger: M2 moves to the closed list. What remains of it is not texture but **geometry** (W) and
  **energy** (E), both oracle quantities; the geometry part becomes the new entry M13.

**Two further facts of tonight, folded in.**
1. Landmark displacement W between the two source photos separates two-person from same-person pairs at **0.869** as
   an oracle (REVIEW_TB1_PREMISE F3; TB1 amendment 2 "Alone ... W 0.869"). Within same-person pairs the TB1 profile score
   rises with W (ρ 0.36) and falls with FR similarity (ρ −0.50) (same review, F3). New entry **M13** asks whether a single image can
   estimate "geometry averaged from two shapes" by a route that is not the landmark-shape statistic of M4.
2. The pre-run review of RI1 (`experiments/reviews/PRERUN_RI1_TB1_20261113.md`, line 25 and line 34): on our ladder FR
   similarity of two people (cos_HB, maximum 0.65) and of two sessions of one person (cos_HS, minimum 0.68) **do not
   overlap**. So every second-identity read on the current ladder (Sb, BD1, TB1, RI1 when it is read) is confounded with
   "FR-dissimilar inputs". The same holds for W, which tracks dissimilarity. **The look-alike contrast is therefore
   raised to rank 1**: it is the necessary condition for any "two identities" sentence, whatever RI1 or M13 show. Its
   smallest decisive size is given in M12.

## Ranking by expected information per GPU-hour, version 2 (superseded by version 3 above)

| Rank | Mechanism or control [ID] | Status at 19:58 | Why this rank | GPU-h | CPU-h | Prior (my estimate) |
|---|---|---|---|---|---|---|
| 1 | **Look-alike matched contrast**: two-person and same-person blends matched on FR similarity and on landmark displacement W [LA1; entry M12] | LA1 plan and LA1-0 drafted; morph build is an author item | without it no result on our ladder can say "two identities" rather than "dissimilar inputs" (cos_HB ≤ 0.65 < 0.68 ≤ cos_HS) | 0.5 (LA1-0) + FR embeddings of the build | 4-8 (build with unchanged engines) | n/a (control) |
| 2 | **Regional identity disagreement** [RI1; M1] | registered by the PR1/BD1 owner (`experiments/RI1_regional-identity-disagreement/`), W control added (amendment 1c); not read | still the only cheap single-image test of an identity route; a pass licenses only "regional leaning tracks input dissimilarity" until rank 1 exists | 0.3 | 2 | 0.35 full blends, 0.6 splices |
| 3 | **Nuisance directions in the candidate's features** [NE1; M10, M7, M9] | draft | unaffected by TB1; decides the border remedy and closes or opens group DRO | 0.5-1.5 | 2 | 0.5 border, 0.2 same-person splices |
| 4 | **Layer misregistration echo**: a single-image estimate of two superimposed shapes from doubled sub-landmark structure [new; M13] | proposal | the only route I see from TB1's W to one image that is not landmark-shape typicality; zero GPU; its premise check is cheap | 0 | 3 | 0.3 |
| 5 | Group DRO / JTT [M7] | only after NE1 | unchanged | 6-12 | — | 0.2 |
| 6 | Paired invariance losses [M9] | only after NE1 and Sbx | unchanged | 5-6 | — | 0.4 border, 0.15 identity |
| 7 | Landmark-geometry averaging (shape typicality) [M4] | measured (ID0, AS0) | W's 0.869 is an oracle *difference between two photos*; M4's single-image shape statistic reached 0.687 even on exact landmarks | 0 | 1 | 0.3 |
| 8 | Residual-noise mixing [M3] | proposal (kill read) | TB1's finest-band reading strengthens the "shared noise floor" view: noise reads capture count, not persons | 0 | 1 | 0.1 |
| 9 | Image-space demorphing [M5] | — | unchanged | 20+ | — | 0.15 |
| 10 | Self-blended images (SBI / SelfMAD) [M11] | — | anti-mechanism | n/a | — | n/a |
| 11 | IRM / V-REx [M8] | — | unchanged | 6+ | — | 0.1 |
| 12 | Frequency traces of warping [M6] | closed by design | unchanged | 0 | 0 | ~0 |
| closed | **Texture band profile** [TB1; M2] | **falsified** (gain +0.010 over energy and geometry, bar +0.02) | contradicted prediction; no arm | — | — | — |

Reading of version 2: the second-identity question is now a data question before it is a mechanism question. The
cheapest decisive next step is LA1-0 (labelled tail calibration, about 0.5 GPU-hour), because it says whether a
decisive look-alike set can exist at all. RI1 should still be read (it is registered and costs almost nothing), but its
outcome table should carry the sentence of the RI1 pre-run review: a pass cannot separate "two identities" from
"FR-dissimilar inputs".

## Ranking by expected information per GPU-hour, version 1 (13 Nov 19:07; kept for the record, superseded)

"Information" here means: how much the outcome changes what we can claim or which arm we run, times the chance the
test is decisive. GPU-hours are my estimates for a GB10 or one A100/H100, not measurements.

| Rank | Mechanism (plain name) [proposed test ID] | Kills or licenses | GPU-h | CPU-h | Prior that the premise holds (my estimate) | Test design |
|---|---|---|---|---|---|---|
| 1 | **Regional identity disagreement**: face-recognition embeddings of different face regions of a two-person morph point to different people [RI1] | the only cheap, direct, single-image test of a second-identity mechanism; licenses or kills an identity-consistency arm (ICT-style) | 0.3 | 2 | 0.35 for full blends, 0.6 for splices | `TEST_regional-identity.md` |
| 2 | **Nuisance directions in the candidate's own features**: is the border reaction (and the same-person-splice flag) a separable direction that erasure or group-balanced last-layer refitting can remove without losing detection? [NE1] | decides between adversarial debiasing / group DRO arms and "the features lack the signal" | 0.5-1.5 | 2 | 0.5 for the border, 0.2 for same-person splices | `TEST_nuisance-erasure.md` |
| 3 | **Texture band profile of two people against one person**: the difference between two people's aligned skin and feature textures has a different frequency profile from the difference between two sessions of one person, at equal blend energy [TB1] | kills or licenses every texture / skin-statistics mechanism with an oracle premise check before any single-image statistic | 0 | 3 | 0.4 | `TEST_texture-band-profile.md` |
| 4 | **Similarity-matched look-alike contrast**: two-person and same-person blends matched on face-recognition similarity [LA1, existing plan] | the decisive test of "second identity beyond FR similarity"; needs new morphs (author item) | 0.5 (calibration LA1-0) + build | 4 | n/a (it is a control, not a mechanism) | LA1 `plan.md`; my additions below |
| 5 | Group-robust training of the candidate (group DRO, JTT) | only after NE1 shows the features can move along the trade-off | 6-12 | — | 0.2 | entry M7 |
| 6 | Paired invariance losses (border equality, same-host S4 > S3 margin) | only after NE1; border-crossed data arm (Sbx) is already queued | 5-6 | — | 0.4 for the border, 0.15 for identity | entry M9 |
| 7 | Landmark-geometry averaging and geometry-texture inconsistency | largely measured (ID0 shape 0.687 on exact landmarks; AS0 "weak"); adds a statistic at best | 0 | 1 | 0.3 | entry M4 |
| 8 | Residual-noise (PRNU-like) mixing | reads "two captures averaged", which a same-person morph also is; zero-GPU kill read | 0 | 1 | 0.1 as a second-identity cue | entry M3 |
| 9 | Image-space demorphing (recover both faces) | ill-posed from one image, hallucinates on genuine photos; costly | 20+ | — | 0.15 | entry M5 |
| 10 | Self-blended training images (SBI / SelfMAD) | labels one-identity blends as attacks: the opposite of the target | n/a | — | n/a (anti-mechanism) | entry M11 |
| 11 | Invariant risk minimisation / V-REx | few environments; known to fall back to ERM | 6+ | — | 0.1 | entry M8 |
| 12 | Frequency traces of warping (resampling correlations) | a warp-only image carries them too; already a trained negative | 0 | 0 | ~0 as a second-identity cue | entry M6 |

The top three cost about 1-2 GPU-hours together, and each needs no training. RI1 and TB1 test the two physical routes
by which a second person can show in one image (identity features in face-recognition space; anatomy-level texture);
NE1 tests whether the failures we already know are removable from the features we already have. If RI1 and TB1 both
fail their premise checks, the honest consequence is the strategist's audit framing: on our data no single-image
second-identity mechanism was found, and the arms of the next version should target the named shortcuts (border,
rendering) rather than identity.

---

## M1. Regional identity disagreement (rank 1) [RI1]

**(a) Why a two-person morph must carry it and the three negatives must not.**
- *Splices* (our S4; also the common practice of pasting the blended inner face into one contributor's head): the
  inner face is a blend of A and B, everything outside the hull is A. Two regions of one image therefore carry two
  different identity estimates, and the gap grows with the dissimilarity of A and B. A genuine photo has one identity
  everywhere. A same-person splice (S3) has blend(A, A') inside and A outside: one identity, small gap. A one-photo
  re-render (GAN or diffusion) changes identity, if at all, coherently over the whole face.
- *Full-frame blends* (R4, the OpenCV and FaceMorpher landmark morphs, latent morphs): every region is a mixture, so
  inner against outer gives nothing. The physical reason here is weaker and is a hypothesis: each region of a morph
  resembles A and B by different amounts, because which contributor dominates a feature (eye shape, brow, nose, mouth)
  depends on the local contrast and geometry of the two sources. Occluding one region then shifts the face-recognition
  embedding towards A or towards B, by different amounts for different regions. For a genuine photo or a same-person
  morph occlusions shift the embedding along directions that do not point to two people. The premise is testable with
  an oracle (we know A and B on the ladder) before any single-image statistic is read.
- Re-renders could still fail this if the generator produces regionally inconsistent identity; that is a test row.

**Version 2 note.** RI1 is registered by the PR1/BD1 owner with W added as a control (amendment 1c). Its pre-run
review's sentence applies: because cos_HB and cos_HS do not overlap on our ladder, a pass reads "regional leaning tracks
input dissimilarity" until the look-alike set (M12) is read.

**(b) Evidence.**
- Dong et al., "Protecting Celebrities from DeepFake with Identity Consistency Transformer", CVPR 2022,
  https://arxiv.org/abs/2203.01318 (abstract opened): detects face swaps by "identity inconsistency in inner and outer
  face regions", learned with two identity tokens and a consistency loss; claims cross-dataset and degradation
  robustness. A reference-assisted variant exists; the abstract does not confirm the reference-free numbers.
- Gao et al., ICIAP 2023 workshops, inner/outer inconsistency for general deepfake detection,
  https://iris.unica.it/handle/11584/389063: **not verified** (search listing only).
- Our record: the ladder's FR oracle, with an independent photo of the host, separates two-person from same-person
  morphs at 0.998 and 99% of morphs verify against both contributors (`experiments/AR1/gate_b.json`, key
  `frgcferet.opencv`): the identity information is in the morph; the question is whether it is regionally unequal.
  BD1 amendments 2-3 (`experiments/BD1_blend-difference-attribution/result.md`, H1 "supported"): within same-person
  splices Sb's logit rises as the FR similarity of the host's two photos falls (partial ρ −0.15 to −0.26 given blend
  energy and colour), "consistent with an identity-weighted appearance cue but does not show one".
- Against: the earlier "identity-agreement slots" idea was dropped as MorDeephy-like and "failed twice in our record"
  (`ideas/CONSOLIDATED_v3.md`, section 6); that was a learned two-slot head, not a regional measurement. ID0 found no
  power for FR typicality (`experiments/ID0_identity-shrinkage-triage/result.md`, point 2), which is a different
  statistic (closeness to the mean face, not disagreement between regions).
- Partial-face recognition: ArcFace verification degrades when the lower face is masked (Damer et al., as summarised in
  https://arxiv.org/abs/2207.06478; **not verified**, search snippet only). So region embeddings are noisy; the test has
  a gate for this (G0 in the test design).

**(c) Shortcuts that could imitate it.** (1) Blur or blending softness lowers FR confidence and could raise dispersion
without identity: controlled by same-person morphs and splices (same softness) and by stored-small genuine photos.
(2) The splice seam: controlled by the seam-only image S0 (seam, no second person). (3) Pose or session difference
between the two source photos: controlled by stratifying on the host's same-person FR similarity (cos_HS) and on the
geometry gap G (BD1 measures). (4) Border: controlled by border-blanked camera photos. (5) The blanking itself: applied
identically to every row.

**(d) Cheapest kill test.** `TEST_regional-identity.md`: glintr100 embeddings of each development image under eight
constant-colour occlusion patterns, no training. Oracle premise first (does the A-versus-B leaning of the embedding vary
across occlusions more for R4 than the session leaning does for R3?), then the single-image dispersion statistic with
storage, border, warp and seam controls, then incremental value over Sb's logit.

**(e) GPU-hours.** About 0.3 (about 40,000 crops through glintr100), 2 CPU-hours.

**(f) Worth a training arm if** the oracle premise reaches ≥ 0.70 for R4 against R3, the single-image dispersion
separates S4 from S3 at ≥ 0.65 within blend-energy quintiles and R4 from R3 at ≥ 0.65, every nuisance control stays
≤ 0.60, and the statistic adds ≥ +0.03 AUC to Sb's logit on S4 against S3 (cross-fitted) on ≥ 4 of 5 seeds. The arm:
an identity-consistency auxiliary head on the CLIP LoRA network (two or more region tokens distilled towards glintr100
region embeddings of genuine images, with a disagreement penalty only on genuine and same-person rows), five seeds,
about 6 H100-hours, scored with the battery and beside the adversary floor.

## M2. Texture band profile, two people against one (version 1 rank 3; **closed in version 2**) [TB1]

**Outcome (version 2).** Premise "holds" at 0.758 within D, but the profile adds +0.010 [−0.006, +0.021] over band
energy and landmark displacement: registered verdict "falsified" (TB1 `result.md`, amendment 2; REVIEW_TB1_A2). The
prediction in (a) below, relatively more mid-band energy for two people, is contradicted: the signal is a smaller
finest-band share (REVIEW_TB1_PREMISE F2). The text below is version 1, kept unchanged for the record.

**(a) Reason.** Landmark warping aligns about 70-100 landmarks; between them, person-specific structure at the scale
of eyelid creases, brow hairs, nostril shape, lip outline, moles and skin texture does not coincide for two different
people, while for two sessions of one person most of it is the same anatomy at nearly the same place. So the
*difference* between the two warped halves should have relatively more energy at the mid frequencies where anatomy
lives for A-B than for A-A', where the difference is dominated by low-frequency illumination and high-frequency sensor
noise. A genuine photo has one texture layer; a re-render has one (generated) layer. This is the "layer-count" idea of
round 3, but tested first with an oracle on the halves and stated as a band profile at equal blend energy, which BD1
showed is the right control.

**(b) Evidence.** Raghavendra, Raja and Busch, "Detecting morphed face images", BTAS 2016 (BSIF micro-texture with an
SVM), https://www.christoph-busch.de/files/Raghavendra-FaceMorphingDetection-BTAS-2016.pdf: **not verified** (search
listing; PDF not opened). Raghavendra and Li, IEEE Access 2022 (region-wise BSIF/LBP on eyes, nose, mouth), DOAJ
listing https://doaj.org/article/d09b9741b4b14252a023eff619c19a91: **not verified**. Neither separates identity from
blending; both use different storage for the classes. Our record: AS0 found the mirror-asymmetric texture share
separates R4 from R3 at only 0.611 [0.573, 0.651] overall, best band 0.618 (`experiments/AS0_mirror-asymmetry/result.md`,
"weak"), so a texture-level second-identity signal, if present, is small in that statistic. BD1: blend-difference
energy D alone separates S4 from S3 at 0.636, and Sb keeps 0.70-0.73 within D quintiles: something beyond energy is
read inside the hull.

**(c) Shortcuts.** Colour and illumination differences between the two source photos (stronger across people and
sessions): BD1's D_dc and D_lin are the controls. Pose difference (geometry gap G). Storage history changes band
profiles: the single-image version uses the outer region of the same image as reference, which shares storage.

**(d) Cheapest kill test.** `TEST_texture-band-profile.md`: zero GPU; oracle band profile of the half-difference
(A_w − B_w against A_w − A'_w) within D, D_lin and G strata; then a within-image inside/outside band ratio as the
single-image statistic, with stored-small and seam controls.

**(e) GPU-hours.** 0; about 3 CPU-hours.

**(f) Worth an arm if** the oracle profile separates two-person from same-person differences at ≥ 0.70 cross-fitted
within D quintiles, and the single-image inside/outside ratio separates S4 from S3 at ≥ 0.65 within D with the storage
control ≤ 0.58. Arm: same-person blends at matched D as negatives plus an auxiliary band-profile target, or a
band-split input stream; about 6 H100-hours, five seeds.

## M3. Residual-noise (PRNU-like) mixing (rank 8)

**(a) Reason, and why it does not reach identity.** A blend of two captures averages two independent noise fields:
the noise variance falls by α² + (1 − α)² (one half at α = 0.5), and each sensor fingerprint is displaced by a
different warp. But a same-person morph is also a blend of two independent captures, so it carries exactly the same
trace; a one-photo re-render replaces sensor noise wholesale, so a noise detector flags it as "not a camera photo".
The mechanism therefore reads "two captures were averaged" or "not a camera image", never "two people". Storage
history (shrink and enlarge) also removes sensor noise, so it collides head-on with the storage shortcut.

**(b) Evidence.** Debiasi, Rathgeb, Scherhag, Uhl, Busch, "PRNU variance analysis for morphed face image detection",
BTAS 2018, https://www.christoph-busch.de/files/Debiasi-PRNU-variance-MAD-BTAS-2018.pdf (opened, text extracted):
961 bona fide FRGCv2 images against 2,414 landmark morphs at 320 x 320 px; D-EER 10.5% over all attacks; the
post-processing (histogram equalisation, 50% and 75% shrink-and-enlarge, sharpening) is applied to **morphs only**, and
the shrunk morphs become *easier* to detect (for the Ppos|Smean detector, D-EER 2.2-2.9% on unprocessed morphs against
0.0-1.5% on SCL50 and SCL75 morphs, over 4, 8 and 10 cells; the other detectors vary from 1.0% to 42%) while bona fide
images are never processed: the storage asymmetry is in the protocol. Debiasi et al., "PRNU-based detection of
morphed face images", IWBF 2018, https://www.christoph-busch.de/files/Debiasi-PRNUMorphDetection-IWBF-2018.pdf: **not
verified** (listing only). Zhang, Peng, Long, "Face morphing detection using Fourier spectrum of sensor pattern noise",
ICME 2018: **not verified**. Our record: the best single hand-made statistic on landmark_combined is a noise statistic
(noise_std_face, 0.886; 0.730 on the DiffAE mix against same-person mix, PR1 part 3, `experiments/PR1_protocol-reads-existing-networks/result.md`
"Part B").

**(c) Shortcuts.** Storage history, JPEG, rendering: all three imitate it.

**(d) Kill read (zero GPU).** On existing cue tables, noise_std_face and the other noise statistics for S4 against
S3 and R4 against R3 within D quintiles. Prediction: ≤ 0.58. If above 0.65 at equal D, the "two captures" argument is
wrong and the entry moves up.

**(e)** 0 GPU, about 1 CPU-hour. **(f)** No arm on this mechanism. It belongs to the adversary floor (ADVERSARY), where it
already is.

## M4. Landmark-geometry averaging and geometry-texture inconsistency (rank 7)

**(a) Reason.** A two-person morph has the mean shape of A and B, which is more average than a real shape; a
same-person mean shape hardly is. A splice adds a possible inconsistency between the averaged inner geometry and the
outer contour of A. Genuine photos and re-renders have one real shape.

**(b) Evidence.** Scherhag, Budhrani, Gomez-Barrero, Busch, "Detecting morphed face images using facial landmarks",
ICISP 2018, https://www.christoph-busch.de/files/Scherhag-LandmarkMAD-ICISP-2018.pdf: differential (probe against
document), distance- and angle-based features from dlib landmarks (search listing; **not verified**). Our record: from
exact landmark files, two-person mean shape against real shape 0.725 [0.689, 0.758], same-person mean against
two-person mean 0.687 [0.650, 0.720], photo against same-person mean 0.548 (ID0 result, points 4-5); detected
landmarks are noisier, and AS0 gave "weak".

**(c) Shortcuts.** Pose and expression dominate shape variance; the warp-only image toward the two-person mean shape
(R2w4) has the same averaged geometry with one identity, so geometry alone cannot separate R4 from R2w4 at all: a
geometry cue reads "was warped to a mean shape", which our protocol already trains as genuine.

**(d) Kill read.** Already effectively read: the exact-landmark ceiling (0.687) is below Sb's own S4 against S3 on
development hosts (0.78-0.82). The only open variant is the splice-boundary inconsistency, which S0 (seam with
two-person outer geometry and no second person) already controls for Sb (0 of 100 seam-only images flagged).

**(e)** 0 GPU. **(f)** No arm. Keep as an adversary-floor statistic (shape typicality from the aligner's own .tem).

## M5. Demorphing (recover both contributors from one image) (rank 9)

**(a) Reason.** If a single image can be decomposed into two faces whose FR embeddings differ, it holds two
identities. A genuine photo should decompose into two copies of one person.

**(b) Evidence.** Banerjee, Jaiswal, Ross, "Facial de-morphing: extracting component faces from a single morph",
https://arxiv.org/abs/2209.02933 (abstract opened): GAN decomposition, no reference, landmark and generative morphs,
"promising results"; no numbers in the abstract. Ferrara, Franco, Maltoni, "Face demorphing", IEEE TIFS 13(4)
1008-1017, 2018: differential (needs the live capture), **not verified** (search listing). Shukla and Ross,
diffDemorph, https://arxiv.org/abs/2505.14527: listed in `03_LITERATURE_AND_METHODS.md` as checked on 11 Nov, **not
re-opened**. The 2026 MLLM-conditioned demorphing paper there states that earlier reference-free methods assume
train-test identity overlap or a known morph method (same file, C2; not re-opened).

**(c) Shortcuts.** A decomposer always outputs two faces; on genuine photos it can hallucinate a second identity whose
distance tracks image quality or storage. The two outputs' FR distance may track blur.

**(d) Cheapest kill test.** Not cheap: it needs a trained decomposer (tens of GPU-hours). A cheaper proxy is RI1's
oracle premise: if regions of a morph do not lean towards different contributors, a decomposer has little to find
beyond what a blend detector finds.

**(e)** 20+ GPU-hours. **(f)** Only if RI1 passes strongly and the paper needs an identity-recovery figure.

## M6. Frequency traces of warping (rank 12)

**(a) Reason, and why it fails.** Warping resamples the image and leaves periodic interpolation correlations (Popescu
and Farid, "Exposing digital forgeries by detecting traces of resampling", IEEE TSP 53(2) 758-767, 2005,
https://farid.berkeley.edu/downloads/publications/sp05.pdf: **not verified**, bibliographic data from the DBLP listing).
A warp-only image of one person carries the same trace, and a warp toward a two-person geometry is only larger than a
same-person warp, not different in kind. Shrink-and-enlarge is itself resampling.

**(b-d)** Our record already contains the kill: warp-only images are not flagged by any arm (SA1 row 6), and the
networks exceed the simple-statistic floor only on one-photo render against camera photo (PR1 part 3).

**(e)** 0. **(f)** No arm.

## M7. Group-robust training: group DRO and JTT (rank 5)

**(a) What it would do.** Minimise the worst loss over groups (label x nuisance: border, storage size, source, engine,
render path, splice type), so that the network cannot buy average accuracy by failing a group such as same-person
splices or border-blanked photos.

**(b) Evidence.** Sagawa, Koh, Hashimoto, Liang, group DRO, https://arxiv.org/abs/1911.08731 (abstract opened; ICLR
2020 per the paper, the page lists only arXiv): naive group DRO fails on over-parameterised networks; strong L2 or
early stopping gives 10-40 point worst-group gains. Liu et al., JTT, ICML 2021, https://arxiv.org/abs/2107.09044
(opened): closes 75% of the ERM-to-group-DRO worst-group gap without training group labels. Gulrajani and
Lopez-Paz, "In search of lost domain generalization", https://arxiv.org/abs/2007.01434 (opened): carefully tuned ERM
matches domain-generalisation algorithms.

**(c) Why it may not help here.** Our failures are not under-weighted minority groups. Sb flags 26-37% of its own
*training* same-person splices, the same hosts on every seed (PR1 part 1; SE1 F5): a label conflict at the host level,
which reweighting does not resolve. AB1 measured a trade-off (r = 0.73) between fewer same-person-splice flags and lower
landmark detection; DRO would most likely move along that trade-off. The border is absent from training, so there is
no group to reweight.

**(d) Cheapest kill test.** NE1, head H2: a group-balanced last-layer refit on Sb's frozen features. If its front of
(same-person-splice flags at fixed two-person-splice recall) is within 0.03 of a threshold sweep of the original head,
reweighting the same features cannot move the trade-off and a full DRO fit will not either.

**(e)** Inside NE1 (no extra GPU); a full arm 6-12 H100-hours. **(f)** Arm only if H2 moves the front by ≥ 0.05 on ≥ 4
of 5 seeds.

## M8. Invariant risk minimisation and V-REx (rank 11)

**(b) Evidence.** Rosenfeld, Ravikumar, Risteski, "The risks of invariant risk minimization", ICLR 2021,
https://arxiv.org/abs/2010.05761 (opened): IRM often fails to recover the invariant predictor and can fail
catastrophically in the non-linear case; it does not improve on ERM in their model. IRM (Arjovsky et al.,
arXiv:1907.02893) and V-REx (Krueger et al., arXiv:2003.00688): **not re-opened**. **(c)** We have few environments
(two databases, one engine in training), and the nuisance that hurts (border) is absent from training environments.
**(f)** No arm unless a battery of at least four genuinely different environments exists; not before RI1, NE1, TB1.

## M9. Paired (counterfactual) invariance losses (rank 6)

**(a) What it would do.** We already train paired data (matched negatives). The next step is to tie the pairs in the
loss: an equality term on logits for the same photo with and without a border (or native against stored), and a margin
term that ranks each two-person splice above the same-person splice of the same host and geometry.

**(b) Evidence.** Aligned datasets (Rajan et al., ICLR 2025, https://arxiv.org/abs/2410.11835), B-Free (Guillaro et al.,
CVPR 2025, https://arxiv.org/abs/2412.17671), Dual Data Alignment (https://arxiv.org/abs/2505.14359): in
generated-image detection, pairing each fake with a reconstruction of a real image is what removes format and size
shortcuts. All three were marked "checked" in `03_LITERATURE_AND_METHODS.md` on 11 Nov; **not re-opened** in this session.
Stay-Positive (Rajan and Lee, https://arxiv.org/abs/2502.07778, opened): constrain the detector to use only evidence for
the fake class; claims less reliance on spurious "real" features and more robustness to post-processing.

**(c)** The border equality term needs border rows in training, i.e. the same data as the queued border-crossed arm
(Sbx); its additional value is only the loss. The identity margin term cannot create a signal the features do not hold
(BD1: the residual at equal D is generalisation within one construction).

**(d)** NE1 head H3 tests whether the border is a separable direction; if so, either the data arm (Sbx) or an equality
loss will likely remove it, and the cheaper one (data) should be read first. **(e)** 5-6 H100-hours per arm.
**(f)** Equality-loss arm only if Sbx leaves > 2% border flags and NE1 shows the direction is separable.

## M10. Adversarial debiasing against a nuisance head, and concept erasure (inside rank 2) [NE1]

**(a) What it would do.** Train the features so that a nuisance head (border present, storage size, source database,
render path) cannot read the nuisance, via gradient reversal; or remove the nuisance direction in closed form.

**(b) Evidence.** Ganin et al., "Domain-adversarial training of neural networks", JMLR 17, 2016,
https://arxiv.org/abs/1505.07818 (opened): gradient reversal layer, features indiscriminate between domains. Kirichenko,
Izmailov, Wilson, "Last layer re-training is sufficient for robustness to spurious correlations", ICLR 2023,
https://arxiv.org/abs/2204.02937 (opened): the features often contain the core signal; refitting only the last layer
on group-balanced data matches heavier methods. LEACE (Belrose et al., NeurIPS 2023, arXiv:2306.03819): **not
re-opened**.

**(c) Risk.** If the nuisance and the label share a direction (border and splice boundary are both "edges inside the
frame"), erasure removes detection too: this is what NE1 measures.

**(d)** `TEST_nuisance-erasure.md`. **(e)** 0.5-1.5 GPU-hours (feature extraction of the five frozen networks).
**(f)** Arm (gradient-reversal border head, or an erasure layer before the head) if erasure removes ≥ 70% of the border
flags with ≤ 0.01 landmark AUC loss on ≥ 4 of 5 seeds.

## M11. Self-blended images (SBI, SelfMAD) (rank 10)

**(a) Why it is an anti-mechanism for our target.** It labels a blend of an image with a transformed copy of itself
as an attack. A one-identity blend is by our class definitions not an attack (`14_CLASS_DEFINITIONS.md`), so the method
teaches exactly the blending reading that our candidate already has too much of.

**(b) Evidence.** Shiohara and Yamasaki, "Detecting deepfakes with self-blended images", CVPR 2022,
https://arxiv.org/abs/2204.08376 (opened): blends pseudo source and target from one pristine image; +4.90 and +11.78
points on DFDC and DFDCP cross-dataset. SelfMAD (Ivanovska et al., FG 2025, https://arxiv.org/html/2504.05504, opened):
trains on the 25,000 SMDD bona fide images only, blends with factors {0.5, 0.375, 0.25, 0.125} under full-face or
part masks, adds FFT-magnitude patterns; mean EER 5.63% against 15.75% (SPL-MAD); no validation set described, and the
HRNet-W18 backbone was chosen by "best overall performance on considered testing datasets". Our record: SelfMAD flags
92-96% of same-person morphs and reacts to warp-only images (SA1 rows 6-7). Cheng et al., "Can we leave deepfake data
behind in training deepfake detector?", https://arxiv.org/abs/2408.17052 (search listing; NeurIPS 2024 per the listing,
**not verified**): blend-only training is the current deepfake practice and mixing in real fakes needs care.

**(f)** No arm. Our SE1 already tested the inverse (same-person blends as genuine) and got a shifted decision point.

## M12. Look-alikes and twins (rank 4, control rather than mechanism) [LA1]

**(a) Role.** Any second-identity signal scales with the dissimilarity of A and B. Two-person blends of look-alikes
and same-person blends of dissimilar sessions, matched on FR similarity, isolate "is it the same person" from "how
different are the two inputs". Look-alike morphs belong in the attack class; their role is to remove the similarity
confound, not to be negatives.

**(b) Evidence.** Ramachandra, Venkatesh, Jaswal, Li, "Vulnerability of face morphing attacks: a case study on
lookalike and identical twins", IWBF 2023, https://arxiv.org/abs/2303.14004 (abstract opened): 16 pairs of twins and
look-alikes, landmark morphs; face recognition is more vulnerable to them; the abstract reports no MAD evaluation. Di
Domenico, Borghi, Franco, Maltoni, "Dealing with subject similarity in differential morphing attack detection",
https://arxiv.org/abs/2404.07667 (abstract opened): identity-based D-MAD becomes much less effective for look-alike
subjects; proposes ACIdA. A kinship-morph dataset (BMVC 2025 workshop,
https://bmva-archive.org.uk/bmvc/2025/assets/workshops/PFATCV/Paper_3/paper.pdf): **not verified**. No twins set is on
disk (LA1 plan, table 1). Our record: BD1 amendment 4 shows least-similar same-person splices flagged 2.2-3.4 times as
often as the most similar and ranked close to two-person splices (AUC 0.58-0.64 against 0.83-0.87): the candidate's
"second identity" reading follows input dissimilarity.

**(d)** LA1-0 (labelled tail calibration on 128 px CelebA, about 0.5 GPU-hour) as drafted. My additions to the LA1 read,
when it exists: (1) report RI1's dispersion and TB1's statistic on the matched pairs as well as Sb's logit, so the
mechanism tests get their decisive row; (2) print the oracle FR distance of each morph to both contributors, so that
look-alike morphs that do not verify against both are not counted as attacks with a weak signal.

**(e)** 0.5 GPU-h calibration; the morph build is an author item. **(f)** A matched training arm only if LA1 reaches
its go count (≥ 100 disjoint pairs) and RI1 or TB1 passed: without a mechanism, a matched arm will most likely learn
the same blending reading at lower margin.

**Version 2: raised to rank 1, and the smallest decisive set.**
- Why raised: on our ladder cos_HB ≤ 0.65 and cos_HS ≥ 0.68 do not overlap (PRERUN_RI1_TB1, lines 25 and 34), and the
  oracle W separates the two pair types at 0.869 (REVIEW_TB1_PREMISE F3). Any "second identity" reading of any
  detector or statistic is therefore indistinguishable, on existing data, from "the two inputs were dissimilar in FR
  space or in shape". Only pairs where two people are as similar as two sessions of one person break this. This is
  now the binding constraint on the claim, more than any mechanism.
- What must be matched (all from LA1's own-source rule: one source for both classes):
  1. FR similarity: each look-alike pair (two persons, glintr100 cosine in the overlap band, realistically 0.60-0.77)
     matched to one same-person pair of a third identity within ±0.03 cosine, without replacement.
  2. Landmark displacement W: the matched pairs fall in the same W quintile (W computed from the unchanged aligner's
     .tem files, as in TB1). Without this, a look-alike result could still be shape disparity.
  3. Pose (|Δyaw| ≤ 15°), inter-eye distance, sex, as in the LA1 plan.
- Images per matched pair: the two-person splice S4 and morph R4, the same-person splice S3 and morph R3, and the
  warped halves, with the unchanged OpenCV-style engine and the approved warp; lossless PNG. One engine is enough for
  the decisive read; a second engine is descriptive.
- **Smallest decisive size: 100 disjoint look-alike pairs with 100 matched same-person pairs** (one identity used once).
  By the Hanley-McNeil approximation the 95% half-width of an AUC near 0.65 is about ±0.076 at 100 per class, ±0.062 at
  150 and ±0.053 at 200 (my computation; a host bootstrap will be somewhat wider). With 100 per class the read is
  decisive when the true AUC is at least about 0.70 (lower bound above 0.62) or at most about 0.60 (upper bound below
  0.68). A true value between 0.62 and 0.68 needs about 200 per class. Fewer than 50 per class (±0.11) cannot separate
  a pass from a kill and should be an evaluation-only descriptive row, as LA1's no-go rule already says.
- Decisive reads on that set, fixed before the build: Sb's logit S4 vs S3 and R4 vs R3; RI1's dispersion Δ; M13's echo
  statistic if it passes its own premise; the oracle W and E, printed. Kill of "second identity" for a statistic: AUC
  ≤ 0.60 on the matched set with its upper bound below 0.68. Licence: ≥ 0.70 with the lower bound above 0.62, on both
  FRGC-like and CelebA-HQ-like sources if both exist, reported per source.
- Cost: LA1-0 about 0.5 GPU-hour; the build 4-8 CPU-hours; embeddings of the build under 0.1 GPU-hour. The yield of
  overlap-band pairs is the unknown: LA1 expects tens to a few hundred identity pairs at cosine ≥ 0.60 in CelebA-HQ
  before filters and about half after them, so 100 disjoint matched pairs is plausible, 200 is uncertain.

## M13. Layer misregistration echo: a single-image estimate of "geometry averaged from two shapes" (version 2, rank 4)

**(a) Reason.** A landmark morph warps both photos to the mean of their landmark sets with a piecewise-affine warp.
At the landmarks the two layers coincide; between landmarks they do not, because each person's sub-landmark
structure (eyelid crease, iris and limbus inside the eye opening, nostril rim, philtrum, lip outline, eyebrow hair
direction, ear and jaw shading) sits at a person-specific position that an affine map per triangle cannot bring into
register. The blend therefore contains each such edge twice, offset by the residual warp field: an "echo" at a few
pixels. The residual grows with the shape difference between the two sources (TB1's W, 0.869 as an oracle), so its
magnitude estimates "two different shapes were averaged" from the morph alone.
- A genuine photo: one layer, no echo (except natural double structures, see c).
- A warp-only image (R2w, R2w4): one layer warped, no echo. This separates M13 from M4: M4 reads where the landmarks
  are (mean shape, which R2w4 also has); M13 reads whether two layers disagree between landmarks, which R2w4 does not.
- A one-photo re-render: one generated layer, no echo.
- A same-person morph: an echo only from pose, expression and session differences, so smaller on average, but not
  zero. This is why M13, like W, reads "two shapes", and only the look-alike set (M12) can say whether those shapes
  belong to two people.
- Splices: the echo exists inside the hull only; the outer ring is a clean reference in the same image.
- Latent (GAN, diffusion) morphs decode one coherent layer, so M13 does not cover them; it is a landmark-family
  mechanism and should be stated as such.

**(b) Evidence.** Ghosting in the eye, nose and mouth regions of landmark morphs as a detection cue: Singh, Venkatesh,
Ramachandra, https://arxiv.org/abs/2305.03264 (search listing only, **not verified**). Echo detection by the cepstrum
(a superposition of a signal with a shifted copy gives a cepstral peak at the shift): Bogert, Healy and Tukey, 1963
(**not verified**, from memory). Our record: TB1's W 0.869 (oracle) and the finding that within same-person pairs the
TB1 score rises with W (REVIEW_TB1_PREMISE F3); BD1's D separates S4 from S3 at only 0.636, so energy alone is a weak
proxy for misregistration. I found no morph-detection paper that measures the residual displacement between the two
layers as such (one search; not exhaustive).

**(c) Shortcuts that could imitate it.** Natural double structures (spectacle frames and their reflections, double
eyelid creases, hair strands, motion blur from a moving subject); JPEG block grids (8 px periodicity, so offsets that
are multiples of 8 are excluded and PNG sources only); the splice seam (S0 control); blur from storage, which hides
echoes (toward genuine: it cannot flag stored genuine photos but can hide stored morphs, as with AS0); the border
(control rows). Expression difference in same-person pairs inflates their echo: that is a real "two shapes" effect,
not an artefact, and is why the decisive read is on the look-alike set.

**(d) Cheapest kill test (zero GPU, about 3 CPU-hours), in two steps.**
1. **Oracle premise.** On the 291 BD1 hosts, the residual misregistration between the two warped halves inside the hull
   (H_w against B_w for two-person, H_w against S_w for same-person), estimated by phase correlation in small windows
   (for example 24 px, in memory, no image written; whether dense flow or phase correlation counts as a measurement is
   the lead's call). Statistic: median residual shift magnitude. Read: two-person vs same-person AUC overall, within
   W quintiles, within E quintiles, per database. **Kill** if the AUC is ≤ 0.65 overall (the warp already removes the
   shape difference between landmarks) or ≤ 0.55 within W quintiles while W itself does the work (then M13 adds
   nothing a landmark reading would not give, and an image-only estimate has nothing to find beyond W).
2. **Single image.** Local echo strength inside the hull: in small windows of the luminance gradient, the ratio of the
   strongest secondary autocorrelation or cepstral peak at offsets 2-8 px to the zero-offset peak, aggregated over the
   eye and mouth windows, divided by the same quantity in the outer ring of the same image. Read: S4 vs S3 within D
   quintiles; R4 vs R3; controls R0_61 vs R0, R2w4 vs R0, S0 vs R0, border rows vs R0 (all must be ≤ 0.58); a
   spectacles stratum if the ladder carries such a label (otherwise stated as not controlled). **Kill** if S4 vs S3
   within D ≤ 0.60, or any control > 0.58. Beside the ADVERSARY floor (the splice shortcut features including the
   inside/outside sharpness ratio) and Sb's logit.

**(e) GPU-hours.** 0; about 3 CPU-hours for both steps.

**(f) Worth a training arm if** the premise reaches ≥ 0.75 and keeps ≥ 0.60 within W quintiles on FRGC, the single-image
echo separates S4 from S3 at ≥ 0.65 within D with every control ≤ 0.58, adds ≥ +0.03 over Sb's logit (cross-fitted) on
≥ 4 of 5 seeds, **and** holds at ≥ 0.65 on the matched look-alike set (M12). Before the look-alike set exists, a pass
licenses only "the detector can read two superimposed shapes", which is still a statement about construction. The arm:
an auxiliary residual-displacement target (the oracle residual field, available for every training morph) on the CLIP
LoRA network, five seeds, about 6 H100-hours.

---

## What the strongest recent S-MAD papers claim, and on what evidence

All entries are single-image unless stated. "Controls" = any of: genuine photos stored like the morphs, same-person
morphs, one-photo renders, look-alike pairs, a validation set separate from the test benchmarks.

| Paper | Claim | Training / test | Controls reported | Opened |
|---|---|---|---|---|
| MADation, Caldeira et al., 2025, https://arxiv.org/html/2501.03800v3 | CLIP + LoRA; MAD22 + MorDIFF mean EER 11.89% (ViT-B) / 11.94% (ViT-L); FRLL-Morphs 0.74-24.96% per set | SMDD / MAD22, MorDIFF, FRLL-Morphs (all share the 204 FRLL bona fide photos) | none; checkpoint after 40 epochs, no validation split described; the ViT-L values of Table 1 and Table 2 appear to be assigned to different sets (read through a page summariser; re-check in the PDF) | yes (HTML) |
| SelfMAD, Ivanovska et al., FG 2025, https://arxiv.org/html/2504.05504 | self-blends + FFT patterns; mean EER 5.63% | SMDD bona fide only / FRGC-, FERET-, FRLL-Morphs, Morph-PIPE, Greedy-DiM, MorCode | none; backbone chosen on test datasets | yes (HTML) |
| FD-MAD, Paulo, Proença, Neves, Jan 2026, https://arxiv.org/abs/2601.20656 | residual frequency domain per region + MRF; FRLL-Morph mean EER 1.85%, MAD22 6.12% (second) | SMDD / FRLL-Morph, MAD22 | none in the abstract; spectral residuals are the feature most exposed to storage history | abstract |
| R-FLoRA, Ramachandra, Apr 2026 (TIFS 2026 per the comments), https://arxiv.org/abs/2604.17321 | Laplacian-residual-gated LoRA on a frozen ViT; beats nine S-MAD methods | four ICAO-compliant sets, seven morph types | none in the abstract | abstract |
| Emergent MAD in open MLLMs, Ivanovska and Štruc, Feb 2026, https://arxiv.org/abs/2602.15461 | zero-shot LLaVA 1.6-Mistral-7B beats task-specific baselines by ≥ 23% EER | none / several | none in the abstract; a zero-shot model cannot have learned "two identities" from morph labels | abstract |
| LoRA ViT distilled from EfficientNet, Shekhawat et al., Nov 2025, https://arxiv.org/abs/2511.12602 | better than six S-MAD methods | a set built from three public face datasets, ten morph algorithms | no numbers in the abstract | abstract |
| When morphs look better, Peng et al., Oct 2026, https://arxiv.org/abs/2611.00074 | training-free FIQA as MAD; best FRLL mean D-EER 11.42%; FEI best 39.75%; thresholds do not transfer; up to 11 of 17 FIQA methods rate diffusion morphs as higher quality | none / FRLL, FEI | score directions fixed in advance (a good practice) | abstract |
| MADPromptS, Caldeira et al., 2025, https://arxiv.org/html/2508.08939v1 | zero-shot CLIP prompt ensembles | none / MAD22 etc. | — | **not verified** (search listing; summarised in `03_LITERATURE_AND_METHODS.md`) |
| SRL-MAD, https://arxiv.org/abs/2603.15050 | one-class, ring-wise Fourier residual latents | bona fide only / FERET, FRLL morphs, MorDIFF | — | **not re-opened** (checked 11 Nov per `03_LITERATURE_AND_METHODS.md`) |
| DifFoundMAD, Gonzalez-Soler et al., 2026 (differential) | foundation models + LoRA, D-EER 6.16% → 2.17% at high security | — | — | **not verified** (third-party review page only) |

What they share, as far as the opened pages show: none reports genuine photos stored like the morphs, same-person
morphs, one-photo renders or look-alike pairs; two (MADation, SelfMAD) give no separate validation set and SelfMAD
picked its backbone on test sets; most evaluate on sets that share the 204 FRLL genuine photos. Our audit results
(released detectors lose 13-20 EER points with history-matched genuine photos; networks that never saw a morph reach
0.0% EER on MorDIFF) are exactly what these protocols cannot see. None claims a second-identity reading with evidence
that would survive a same-person control. The 2024 D-MAD look-alike paper (Di Domenico et al.) is the only one that
measures subject similarity, and it does so with a reference image.

## Not verified, and limits of this version

- Pages marked "not verified" were seen only as search listings. Every number that goes into `references.bib` or
  the paper must be re-read from the PDF.
- I did not open the full texts of ICT, R-FLoRA, FD-MAD or the MLLM paper; their reference-free performance and
  training details are from abstracts.
- Priors and GPU-hours are my estimates.
- I did not check the queue or the dispatcher; the costs assume the DGX GB10 for the zero-training tests.

## Change log

- v1, 13 Nov 2026, 19:07 CET (6db5154): first ranked ledger; three test designs (RI1, NE1, TB1).
- v1.1, 13 Nov 2026, 19:07 CET: clock times corrected; v1 stamps (19:40) were written from an estimate, not from `date`.
- v2, 13 Nov 2026, 19:58 CET: texture band profile (TB1) closed as falsified and my M2 prediction recorded as contradicted;
  look-alike matched contrast raised to rank 1 with its smallest decisive size; new entry M13 (layer misregistration
  echo); RI1 note on the FR-similarity non-overlap.
- v3, 13 Nov 2026, 21:49 CET: outcomes of RI1, TB1 single image, ME1 and NE1b; AB1 amendments 4-6 and the adversary floors
  folded in; new rank 1 shape-matched same-person negatives (HN1, proposed), look-alike set rank 2, count target rank 3;
  RI1, TB1, NE1 closed, ME1 parked. Not informed by the sealed MAD22 read.
