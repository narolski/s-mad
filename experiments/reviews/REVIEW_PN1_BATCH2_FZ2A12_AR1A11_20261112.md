Reviewer: results-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited.

# Post-result review: protocol network first tests (PN1), second batch; FZ2 amendments 1 and 2; AR1 amendment 11

I worked read-only. I did not open valx.csv, FST or A12SP. The only FFHQ data I read were the amendment-13 list and the metadata in the ffhqm manifest. My scripts are in /tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/pn1b2/: rc.py (recompute), h1b.py (paired H1), ci.py (bootstrap intervals), pair.py (paired FFHQ history shift) and th.py (θ against band cosines). Every number I add here is post hoc.

## 1. Verdicts

**Subject 1 (PN1, second batch): the numbers are sound and the rules were applied correctly, but two labels need qualifying and one important result is under-claimed.**
- All 12 tars pass their sha256 checks. Every headline number reproduced from the raw npz files.
- "Killed" is the correct registered verdict for the spliced LoRA arm (Sb). But kill read (i) measures whether the network stops using the surround. It does not measure whether the network reads the face. On the face, Sb improved.
- "Calibration shift (not a shortcut)" is supported for B, Bn and C. My check of history-matched against native FFHQ genuine images settles the 0.51× shrink / 2.0× enlarge caveat: those three networks are blind to that history.
- Under-claimed: the same FFHQ data replicate, on a source no network was trained on, the tier-1 scale-free storage finding (plain arm A reacts to storage history; the protocol arms do not).

**Subject 2: the rules were applied correctly, but the wording is wrong in two places.**
- FZ2 amendment 2 should read "lowest-band version falsified". The general shared-structure H-A is not falsified.
- AR1 H-D should read "untestable (floor 1.000)", not "falsified".

## 2. Findings, most severe first

**F1 (major, interpretation): the Sb kill rule answers a different question from "does Sb read the face".**
- Recomputed values:

| Read | B (401 / 402) | Sb (401 / 402) | Bv (401 / 402) |
|---|---|---|---|
| Face-blanked R2w vs R4, development | 0.9998 / 0.9999 | 0.991 / 0.999 | 0.9998 / 0.9999 |
| Face-only R4 vs R2w, test | 0.840 / 0.865 | 0.938 / 0.957 | 0.838 / 0.861 |
| S0 vs S4, test | 0.682 / 0.725 | 0.983 / 0.989 | — |
| Sb excess over the 3-statistic floor, test | — | +0.125 / +0.131 (lower bounds +0.08 / +0.09) | — |

- Sanity checks:
  - Face-blanked S4 vs face-blanked S0 is exactly 0.500 in every network, so the blanking removes everything inside the hull.
  - Face-blanked R4 vs face-blanked S4 is 0.995 to 1.000. OpenCV full-frame morphs carry a real blend in the hair, ears and background.
- So a surround read on R4 is a real signal, not a shortcut. Spliced positives added a face-interior read and did not remove the surround read.
- Replace result.md lines 131–135 with: "Registered reading: killed by the amendment-10 rule; (i) fails on both seeds (face-blanked 0.991 / 0.999 vs B 1.000). Read (i) asks whether surround reliance falls. It did not, and on OpenCV full-frame morphs the surround carries a real blend. It does not show that Sb ignores the face. Post hoc: face-only R4 vs R2w rose from 0.840 / 0.865 (B) to 0.938 / 0.957 (Sb). Bv equals B (0.838 / 0.861), so the change is not row volume."

**F2 (major, under-claim): FFHQ replicates the protocol's storage result on an unseen source.**
- These are the history-matched (resmatch) and native images of the same 2,000 FFHQ persons, paired by key.

| Network | AUC history-matched vs native (401 / 402) | Share whose logit rises (401 / 402) | Mean shift, logits (401 / 402) |
|---|---|---|---|
| A | 0.683 [0.665, 0.698] / 0.665 | 0.78 / 0.72 | +2.0 / +1.6 |
| B, Bn, C | 0.476 to 0.513 (intervals include or sit just below 0.5) | 0.30 to 0.44 | +0.17 to +0.39 (median about −0.03) |

- Wording to add, labelled post hoc: "On 2,000 FFHQ persons (unseen source), shrinking to the morphs' 65 px eye distance and enlarging back raises the plain network's logit for 72–78% of persons (AUC 0.67–0.68). It raises B, Bn and C for 30–44% (AUC 0.48–0.51). This replicates the tier-1 scale-free storage reading on a second source. A small upper tail remains: own-rule flags rise by 5 to 8 points."

**F3 (major, wording): HN2's label and what the history-matched control shows.**
- Recomputed exactly: own-rule flags 22.5 / 17.8 / 22.4 / 17.7 / 9.9 / 6.4 / 5.4 / 3.5%; AUC 0.988 to 1.000; history-matched AUC 0.935 / 0.994 / 0.993 / 0.997 / 0.971 / 0.995 / 0.995 / 0.999.
- Answer to your question 3: for B, Bn and C, the resolution-history difference between the classes does not explain the within-FFHQ AUC. Those networks do not separate history-matched from native genuine images (F2), and the morphs against history-matched genuine images stay at 0.993 to 0.999.
- For A, part of the native-frame AUC is history: it falls from 0.988 to 0.935 on seed 401.
- What HN2 does not show:
  - That the networks read the blend. landmark_complete is a whole-frame morph with ghosting in the surround, and no simple-statistic floor was computed on FFHQ.
  - That there is a calibration shift at the own rule for C 402. It flags only 3.5%; its shift is only at τ_cam, 95.7%.
- Rewrite: "Not a source-identity shortcut for ranking: within FFHQ the networks rank whole-frame landmark morphs above disjoint genuine persons (AUC ≥ 0.988; against history-matched genuine 0.993–0.999 for B, Bn, C; 0.935 / 0.971 for A). The decision threshold does not transfer: 3.5–22.5% flagged at the own rule, 95–98% at τ_cam. No simple-statistic floor on FFHQ, so 'reads the blend' is not shown."
- "Not decidable on FFHQ" would be too timid for ranking. It is the right label only for "reads morphing".

**F4 (major, calibration of the H1 gain): most of Sb's +0.13 / +0.23 is B's own loss.**
- Sb minus A on H1 AUC: +0.062 [0.041, 0.085] and +0.086 [0.063, 0.110]. Sb minus B: +0.127 [0.103, 0.154] and +0.233 [0.205, 0.264]. Intervals are image bootstraps, which do not cover training variance.
- H1 pairs each morph with its own host photo at the same 112 px history. The share of morphs scored above their own host:

| A | Sb | C | B | Bv |
|---|---|---|---|---|
| 0.955 / 0.958 | 0.950 / 0.948 | 0.953 / 0.905 | 0.905 / 0.696 | 0.903 / 0.669 |

- So Sb's gain over A is in consistency across hosts, not in paired ranking. At the own rule Sb is better on both errors on seed 402 and similar on 401: genuine flagged 7.0 / 9.7% against A's 22.2 / 15.6%; morphs missed 26 / 22% against 24 / 37%.
- It is not seed noise. B and Bv on the same seed differ by only 0.004 / 0.009. The reference recipe's 8-seed SD is 0.018. Sb is above all 8 reference seeds (0.819 to 0.869).
- It is still first-test data, read once, on 2 seeds that are confounded with machine.
- Rewrite: "raises H1 AUC over B by 0.13 / 0.23 and over A by 0.06 / 0.09; paired host-matched ranking equals A's (0.95). First-test data; a lead for a fresh registration, not a result."

**F5 (minor, timestamps): amendment 12's header is false as written.**
- It says "03:20, before any Sb/Bv result exists". It was committed in 1ab1256 at 03:19:01, and PN1_Sb_s401.tar had been on disk since 03:08:28.
- The sb_read.json committed at 1ab1256 holds B rows only, so Sb was probably not read first. Read (i)'s 0.05 rule was also fixed in amendment 10. No verdict changes.
- Rewrite: "registered at git 1ab1256 (03:19:01); PN1_Sb_s401.tar was already local (03:08:28) but not read (sb_read.json at 1ab1256 has B only)."
- HN2 is clean: the reader was committed in a1c6664 at 03:33, the tars arrived at 04:09 and 04:55, and the readers have not changed since.

**F6 (FZ2 amendment 2, major wording): "H-A falsified" covers only the lowest-band version.**
- The verdict follows correctly from the registered rule: ΔR² +0.183 [0.110, 0.267].
- θ is mathematically the power-weighted average of the band cosines. On 67 hosts the two correlate at r = 0.999999. The lowest band holds 0.3% of the noise map's power; bands 2 to 4 hold 4%, 18% and 77%.
- So "θ adds beyond c0" means "shared structure in bands 2–4 adds beyond band 1". Bands 2 to 4 track sharpness within SAME at ρ 0.34 to 0.44, with lower bounds of 0.24 or more.
- The second falsifier was built so that shared structure anywhere except the lowest band would falsify a shared-structure hypothesis.
- Rewrite: "Falsified as registered for the lowest-band version (c0, 0.3% of the noise power; ρ +0.095 [−0.016, 0.206]). Post hoc: θ is the power-weighted mean of the band cosines, and shared structure in the mid and high bands tracks sharpness within SAME (ρ 0.34–0.44). Coherent-noise sharpening in general is not falsified (descriptive)."
- Amendment 1 reproduced: NOISEX vs NOISES 0.907 [0.884, 0.928]; SEMX vs SEMS 0.579; residual floors 0.810 / 0.827.
- H-C "supported" rests only on the point estimate: 0.569 [0.455, 0.684], and the interval includes the falsifier 0.65. Add that sentence.
- Order: registrations dbc151d and c258935 come before the result commits. The code mtimes (03:39:51, 03:51:08) are after the registrations. That is consistent, but because the gaps are about 60 s it cannot be proved the computation came second.

**F7 (AR1 amendment 11, H-D): the test could not fail any other way.**
- Recomputed: the combined floor is 1.000 for both tools. The best excess is 0.000 [0.000, 0.000], so "lower bound > 0" was impossible.
- Rewrite: "H-D untestable on FRLL: the combined floor is 1.000 (smiling-file confound, stated in the registration), so the falsifier fires mechanically; no information on whether AR1(b) replicates."
- Registration a265476 (03:36:37) comes before floors11.py (03:37:00) and the json (03:37:38).

## 3. Honest summary of the method candidate (your question 5)

- Training-data protocol (warp-only images and halves as negatives): removes most of the plain recipe's reaction to storage history at the own rule and in scale-free reads, on the test ladder (2 seeds) and on unseen FFHQ (F2). It costs face-spliced detection: H1 drops 0.07 to 0.17 against A. It does not give a threshold that transfers to unseen genuine sources: τ_cam flags 95 to 100% of FFHQ and H1, and 30 to 95% of FRLL.
- Adding spliced positives: restores H1 and raises the face-interior read. It still fails the storage and kernel marks at τ_cam, and was killed by a rule that tested the wrong thing.
- Novelty: spliced positives are close to self-blending practice (SBI, SelfMAD). The contribution is the controlled demonstration, not the augmentation.
- No positive method claim survives yet.

A clean diagnostic paper is supported:
1. Standard recipes read storage history, and protocol negatives remove that.
2. Ranking transfers across genuine sources but thresholds do not, because of a saturated bounded head and source-specific genuine floors.
3. Full-frame morphs can be detected from the surround alone (0.999). The face-interior read (0.84 to 0.87) governs face-spliced attacks, and only spliced positives raise it.
4. Released detectors do not beat simple-statistic floors on controlled contrasts (AR1).
5. On diffusion morphs, the separability is in the render path.

## 4. New hypotheses

- **HN7, cue redundancy.**
  - Statement: the surround is a sufficient and easier cue on full-frame morphs, so a network's face-interior sensitivity, not its full-frame AUC, sets its transfer to face-spliced attacks.
  - Prediction: across the 12 networks, face-only R4 vs R2w AUC rank-predicts H1 AUC with Spearman ≥ 0.6, and A's face-only AUC is above B's on both seeds.
  - Falsified if Spearman ≤ 0.2. B 402 is already a within-arm counterexample (face-only higher, H1 lower).
  - Cost: rescore A, Bn and C (and Sb, Bv as needed) on the 4,365 splice rows, about 0.3 A100-hours. Needs a PN1 amendment. The original machines are released, so the platform change must be disclosed.
- **HN8, independent face-splice test.**
  - Prediction: on FFHQ landmark_combined (Neubert "combined": the morph face inside a real surround) against its history-matched genuine pool, Sb exceeds B by at least 0.05 AUC on both seeds, and Sb ≥ A.
  - Falsified if Sb ≤ B on either seed.
  - Cost: about 0.1 A100-hours. Needs the lead's approval to score landmark_combined, and registration first.
- **HN9, common-mode seed or machine offset.**
  - Statement: every arm's FFHQ own-rule flag falls 8 to 14 points from seed 401 to 402, which points to a shared seed or machine offset.
  - Test: the planned replicate fit of A at seed 401 on the new machine.
  - Machine-driven if it lands outside 22.5 ± 3%; seed-driven if inside.
  - Cost: 1.2 A100-hours, already in the draft.
- **HN10, FZ2 mediation.**
  - Prediction: within SAME, θ has no partial correlation with L once c1 to c3 are controlled, and c2 keeps ρ ≥ 0.2 once θ is controlled.
  - Cost: 0 GPU. Register in FZ2 first.

## 5. Next experiments, ranked by information per GPU-hour

| # | Experiment | Cost | When | Decides | Approval |
|---|---|---|---|---|---|
| 1 | Text fixes F1 to F7; the post hoc FFHQ paired-history and H1 paired tables | 0 | now | the claim wording | lead |
| 2 | HN10 | 0 | now | the FZ2 mechanism sentence | FZ2 amendment |
| 3 | One lease: rescore A, Bn, C on the splice rows (HN7); score all 12 networks on FFHQ landmark_combined and its history-matched pool (HN8); score Sb and Bv on the HN2 list | about 0.5 A100-h, about 0.3 USD | 12 Nov | whether the Sb lead survives an independent face-splice set before fresh seeds | PN1 amendment 14; lead for landmark_combined |
| 4 | Fresh seeds, revised (below) | about 19 A100-h, about 12 USD | start 12 Nov, read 13–14 Nov | whether the Sb vs A vs B pattern replicates | new registration; author's budget |
| 5 | Head change, equality term, multi-source genuine training | new code or new images | after the deadline | calibration transfer | author |

**Fresh-seed recommendation: run V5, but change the arms to A, B and Sb, plus the replicate fit (16 fits).** C becomes optional at 3 seeds if time allows.
- Selecting Sb this way is compliant with amendment 10, because the selection uses development-ladder reads only: face-only 0.925 / 0.938 against B's 0.836 / 0.862, and the S0 vs S4 excess lower bound +0.049 / +0.051.
- Primary contrasts:
  - Sb − B on H1 ≥ +0.05 and Sb − A ≥ 0, each on at least 4 of 5 seeds. H1 is labelled "re-read".
  - The same on FFHQ landmark_combined.
  - A scale-free storage mark: FFHQ paired share rising ≤ 0.65. A must fail it as the positive control.
- Keep step 1 printed only. On this evidence I expect every arm to fail it.
- Two leases of the same type, each seed whole on one machine, bring wall time to about 10 h.
- V3 as drafted (A, B, C) mostly re-tests contrasts whose outcome would not change the paper.
- The head change, the equality term and multi-source genuine training are new code or new images (author items). They do not fit a responsible schedule before 14 Nov.

## 6. Risks

- The Sb gain could be engine-specific: OpenCV splices in training, Poisson splices in H1. Run item 3 before item 4.
- No arm will pass the threshold-transfer marks. Write the paper's claims on scale-free reads now.
- Timestamps: cite git hashes only.

## 7. Notebook and conclusions wording

There is no CONCLUSIONS.md in smad-next; use this in the NOTEBOOK row and the "learned / sure / next" sections.
- **Learned:** "Protocol negatives remove the plain recipe's reaction to storage history, on the ladder and on unseen FFHQ. They cost face-spliced detection, and spliced positives restore it (H1 0.91, 2 seeds). No network gives a threshold that transfers to unseen genuine sources."
- **How sure:** "Two seeds confounded with machine; H1, MAD22 and the ladder are first-test data; FFHQ reads are post hoc except the registered HN2."
- **Next:** "Score an independent face-splice set (FFHQ landmark_combined); fresh seeds 403–407 for A, B, Sb with scale-free marks."

Files reviewed:
- /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/result.md (lines 119–157)
- /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/prereg.md (lines 439–531)
- /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/tier1_sb/sb_read.json
- /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/tier1/hn2.json
- /home/narolski/smad-next/experiments/FZ2_frozen-read-new-diffusion-ladder/result.md (lines 118–133)
- /home/narolski/smad-next/experiments/AR1/result.md (lines 401–422)
- /home/narolski/smad-next/experiments/AR1/floors11.json

