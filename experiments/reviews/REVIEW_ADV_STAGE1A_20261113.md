<!-- Post-result review of the standing adversary's stage-1a floors (bffacb5) by the results-reviewer (Opus), ordered by the lead; hand-back saved verbatim by the lead, 13 Nov 2026. The reviewer's post hoc scripts are copied to experiments/reviews/scripts_adv/. -->

**Verdict: the numbers are correct and real, but they need qualification.** Every reported number reproduces from the committed files, and the registered rules were applied. The "nuisance" label is wrong for about half of what carries 0.964, and comparing it with the network is not like for like. So "dominated by a rendering/processing difference" and "the network lies far below" over-claim in one direction. Reading 0.96-0.98 as "landmark_combined (lcomb) is not a morph test" over-claims in the other. The construction confound itself is real, documented and partly old news.

## 1. Numbers, pins, rules: all pass
- I recomputed every floor from the held-out CSVs (`/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/adv/a1.py`). lcomb: logreg 0.9823, gbt 0.9801, nu_gbt 0.9642, single 0.8887. The intervals match `floors/lcomb.json`, and the four ladder JSONs match the owner's summary.
- The sha256 of all 10 files equals `floors/pins_stage0.sha256`.
- Regression gate: 0.8856 (noise_std_face).
- Folds are person-disjoint:
  - lcomb has 3,000 components for 3,000 rows. FFHQ-Morphs uses each contributor once, and the 2,000 morph contributors have zero overlap with the 2,000 genuine FFHQ keys (I checked).
  - Ladder: 130 components for 382 rows, with the partner linked.
- Ladder counts are 191/191 after amendment 1 F1.
- An untracked, unpinned stage-1b file, `floors/test_S4bg_vs_S0bg.json`, now sits in `floors/`. `check._pinned` would refuse it. Commit or move it.

## 2. Is 0.964 leakage or real?
**Not file leakage.**
- On lcomb, all 8 PNG-container values are constant on both sides: zlib 0, filter 1 only, colour type 2. One encoder was used.
- File size is content: png_bytes 0.634, png_n_idat 0.635.
- The pixel-only floor is 0.982, the same as the full floor.
- Size is matched. From the sidecar `ffhqm_meta.csv` (development set by the author's ruling; I read only the README and the metadata): pre_ied AUC 0.473, pre_w 0.516, border_frac 0.459.
- Restricting to morphs within ±1 px of the median eye distance (460 morphs / 1,843 genuine) leaves the nuisance floor at 0.964/0.969. The "spike against spread" residual of E7's design does not drive it.

**What carries it.**
- Families: RES alone 0.93, RENDER 0.92, BORDER+STORE 0.67.
- Top cues are all "smoother morph": resid_corr_gb 0.889, noise_std_face 0.886, band power b4 0.883, resid_corr_rg 0.875, lapvar_face 0.872.
- **The key defect:** `feats.py:197-206` computes RENDER's residual correlations, chroma noise and kurtosis on the face box `fb`, and RES computes face-box cut-offs. Those are regions that blending changes. The proof is on the test ladder: R4 against R2w uses the same pipeline and the same photos and differs only by blending, yet its nuisance floor is 0.986-0.996.
- So the "nuisance floor" is partly a blend detector. That contradicts its own definition (prereg amendment 2 F4, lines 277-282).

**The real confound.**
- Surround-only cues (noise_std_border with lapvar_border, cross-fitted) reach **0.789 on lcomb**, against **0.500** on our pipeline-matched face splices (dev S4 against S0) and 0.525 on test S4 against S3.
- The surround of a landmark_combined morph is contributor x after the generator's own 1024→256 resize. The genuine photos went through E7 INTER_AREA.
- The dataset README already says so (`/mnt/t7/smad_heldout/ffhq_morphs/README.md`, section "Resampling kernel"): no cv2 or PIL kernel matches, with a mean absolute error of 2.9-3.9 grey levels. It calls kernel history "a residual difference that cannot be removed".
- **Partly old news:** PN1 already found noise_std_border at 0.786 and 27 cues combined at 0.948 (`PN1_protocol-network-first-tests/result.md:226, :253`).

**Over-flexibility is not the issue.** Cross-fitting penalises overfitting. On lcomb, linear logreg wins. The max-of-three choice adds at most about 0.01. The fold-conditional bootstrap makes the intervals slightly too narrow.

## 3. A network below a shortcut-only model
- The floor is fitted on lcomb itself, in-distribution, on 2,400 rows. The networks are trained on the ladder and scored zero-shot on lcomb. Below the floor is the expected result for any transfer learner, so it shows neither "ignores the cues" nor "contrast invalid".
- A comparator trained on other rows does much worse. The 27-statistic baseline trained on the ladder gets 0.814 (amendment 15). My quick ADV-feature models fitted on the test ladder and applied to lcomb get 0.45-0.76 (`a2.py`). On that fair comparison the candidate's 0.873-0.906 is above the shortcut learners, which is currently under-claimed.
- **"Ignores the cues" is contradicted.** Sb's within-genuine Spearman correlation with noise_std_border is 0.18-0.22, above 0.2 on 3 of 5 FS1 seeds (`PN1/result.md:294`). Sb reads the surround confound a little.
- **Morph signal survives nuisance balancing.** I matched on the nuisance score (270 of 1,000 morphs have common support). A refit there gives nuisance gbt 0.52 (linear 0.76), all-cue 0.84-0.94 and F27 0.75-0.85 (`a6.py`).

**Re-word these conclusions:**
- **The +0.12 to +0.21 gain** (`18_EVENING_CONCLUSIONS:13`): keep "replicated", but add "on a development set whose surround carries a kernel-history cue (0.79) and which in-distribution shortcut models separate at 0.96-0.98; whether the gain holds at matched history is untested."
- **The RZ1 +0.03 bar** (`RZ1 prereg:248, :274, :326`): it is most exposed, because RZ1 arms change resolution and kernel handling, exactly the axis lcomb is confounded on. Before any RZ1 read, the selection-rule draft (not yet binding) should add the same paired test on a history-balanced lcomb subset. That needs the author's adoption.
- **The 0.886 floor** stays binding as registered. Print beside it that it is the weakest of the three floors.
- **The "exceeds" test** is effectively impossible on lcomb (quick bar 0.986), so "within the ADV floor" carries no information there. State that it is predetermined, so no one reads it as evidence of shortcut use.

## 4. The ladder
- **R4 against R2w:** a pure blending contrast. A floor near 0.99 is expected and shows the control works (blending is the only difference). It does not show a construction confound. Only R2w's higher DCT-comb score (0.75-0.80) is a JPEG-source trace that blending averages away.
- **R4 against R3:** same hosts on both sides. No single nuisance cue exceeds 0.62; the best are face_f95 and chroma noise, meaning two-person blends are softer. That is likely the blend difference D (the dissimilarity of the two faces), not session or size. After nuisance matching (127 pairs) the all-cue floor falls to 0.62-0.66.

## 5. Over- and under-claims (exact rewrites)
- **`FLOORS.md:37`** says "This set is dominated by a rendering/processing difference". Replace with: "Shortcut-only statistics fitted on this set separate it at 0.98; about 0.79 comes from the surround alone (a resampling-history difference documented by the dataset), the rest from face-region smoothness, which blending also produces."
- **The "Nuisance floor" label:** rename it "non-F27/non-BLEND floor (contains face-box texture)", or redefine it (proposal 1 below).
- **`FLOORS.md:21`**, "RENDER:resid_corr_gb … (demosaicing trace)": both sides were downsampled about 4x, so no demosaic trace survives. Call it "face-box noise-residual cross-channel correlation".
- **`FLOORS.md:34-36`**, "lies far below both": add "a floor fitted in-distribution; networks are zero-shot; the comparable learner is section 5.3."
- **The owner's "most consequential" framing:** it adds the nuisance split to PN1's existing 0.948 and 0.786; present it as a quantification, not a discovery.

## New hypotheses
- **H-new-1 (two components).** lcomb's separability is a surround history part (kernel) plus a face blend part.
  - Prediction: on a history-balanced subset the surround floor is ≤0.60 while the face-box floor is ≥0.80.
  - Falsified if the face floor falls below 0.65, which would mean the kernel acts on the face too.
  - Cost: zero GPU, CPU about 1 h. Can run before the reads.
- **H-new-2 (the gain is history).** Sb's gain over B on lcomb shrinks by at least half on the history-balanced subset.
  - Test: AB1's existing 408-412 scores, read by the arm owner. The ADV does not open scores.
  - Falsified if the gain stays ≥ +0.10 on at least 4 of 5 seeds. Zero GPU.
- **H-new-3 (R4 against R3 is D).** Within BD1's D quintiles, the R4-against-R3 nuisance floor is ≤0.60. Zero GPU.

## Next experiments (ranked)

| # | Experiment | GPU-h | When | What it decides | Approval |
|---|---|---|---|---|---|
| 1 | Masked re-measurement: the same features on the surround ring only and the face hull only, every stage-1 contrast; new "surround floor" | 0 (CPU about 1 h) | before the SbFM/RZ1 reads | whether the nuisance floor is history or blend | ADV amendment 3, post hoc label |
| 2 | `lcomb_bal`: 1:1 caliper matching (or inverse weighting) on the **surround-only** score plus pre_ied, never on the face-containing nuisance score (that would match away blending). Iterate until the refit surround and file floors are ≤0.60 for both models. Existing images only | 0 | tonight | a valid lcomb read | ADV amendment; arm owners adopt as a printed read |
| 3 | Sb, A and B 408-412 lcomb scores on `lcomb_bal` and within surround-score quintiles | 0 | before RZ1 | H-new-2; whether the +0.12-0.21 headline survives | arm-owner reader, labelled post hoc |
| 4 | Pull the section 5.3 same-data shortcut learner forward, before the SbFM/RZ1 reads | 0 | tonight | the fair comparator for zero-shot networks | none (already registered) |
| 5 | R4 against R3 floor within BD1 D quintiles (both engines) | 0 | tonight | H-new-3 | ADV amendment |
| 6 | Replace quintile stratification with matched subsets: `diff_within_floor_quintiles` is degenerate on lcomb (quintiles 0-1 hold 1-10 morphs of 600, quintile 4 holds 7-36 genuine of 600) | 0 | before any arm uses it | makes the F7 print readable | ADV amendment |
| 7 | Find the morphgen 1024→256 kernel from the Idiap code (reading only), then rebuild resmatch with it | 0 to find; the rebuild is the author's | after the deadline unless the author allows it | removes the confound at source | **author only** (resampling) |

## Risks to the story
- The sealed reads cannot rescue lcomb-based claims. If H-new-2 holds, the candidate's headline gain is mostly history-reading.
- Hedge now: compute items 1-4 before the SbFM/RZ1 reads, and print the lcomb_bal AUC beside every lcomb number.

## Edits for CONCLUSIONS.md
- **What we have learned:** "FFHQ landmark_combined is separable at 0.96-0.98 by statistics fitted on it; about 0.79 of that comes from the image surround, a resampling-history difference between how the morphs and the genuine photos were made."
- **How sure we are:** "The numbers are verified and pinned; the split between history and blending is not yet measured; the candidate's gain at matched history is untested."
- **Future directions:** "Re-read every landmark_combined number on a history-balanced subset built from existing images; compare networks with the same-data shortcut learner, not the in-distribution floor."

My analysis scripts (`a1.py` to `a8.py`, read-only, development features only) are in `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/adv/`. Main evidence files:
- `/home/narolski/smad-next/experiments/ADV_shortcut-floors/FLOORS.md`
- `/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/lcomb.json`
- `/home/narolski/smad-next/src/adversary/feats.py`
- `/mnt/t7/smad_heldout/ffhq_morphs/README.md`
