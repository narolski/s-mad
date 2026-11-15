# Pre-run review: protocol network fresh seeds 403-405 with replacement mark P-c' (PN1 draft)

Reviewer: experiment-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited. Verdict: GO WITH FIXES.

## Pre-run review: fresh seeds 403 to 405 of the protocol network with replacement storage mark P-c′ (PN1 draft)

I worked read-only. I did not open valx.csv, FST, A12SP or any eval/gtest score file. I read manifests (metadata columns only), the tier-1 JSONs and the reference-row JSONs.

### 1. Verdict: GO WITH FIXES

No hard rule is broken. All six fixes below must be in the registered text before any fit or any HN2 score exists. Without them the batch cannot compute its own marks (fix F1), would read its main mark on a self-calibrated scale (F3, F4), and could not falsify either hypothesis (F5, F6).

### 2. Findings, most severe first

**F1 (blocker, operations). τ_multi cannot be computed from the registered pack.**
- `pn1_eval.csv` in pack 2 has only the families bench 15,012, ladder 6,093, splice 4,365, af0 1,339 and h1 1,196. It has no FFHQ, FEI or SMDD rows.
- The draft says "unchanged pack 1, unchanged run.sh", but the live `src/PN1/run.sh` is `a208fcf8…` (the pack-2 version). The pack-1 run.sh registered in amendment 6 is `42b335b6…`.
- Fix:
  - Build a scoring list of the FFHQ bona 2,000, FEI 385 and seeded SMDD rows (existing files only, nothing built).
  - Pin its sha256, and the run.sh and scorer sha256s, in the registration.
  - Run it through `pn1_score.py` for every fresh network and the eight existing ones.

**F2 (blocker, internal contradiction).** §5 (i) reads "test-ladder R0_61". Line 52 says "the present test ladder cannot be used to pass P-c′". No other ladder exists, and no image may be built.
- Fix: replace line 52 with: "P-c′ is read only on networks fitted after this registration. It uses the same 191-host test ladder, which was already read once for tier 1 with other networks (stated)."

**F3 (major). Calibration and test sources are not independent.**
- FFHQ and FEI are split into a development half and a test half. Their test halves therefore come from the sources the threshold was fitted on. Under the max-over-sources rule they sit near 5% by construction. Under equal-weight pooling a hard source such as FEI can sit above 10% by construction.
- So step 1 is really read only on FRLL and H1.
- Fix: calibrate leave-one-source-out (fit τ on two of FFHQ, FEI and SMDD, test on the third, rotate), plus FRLL and H1. State the quantile rule exactly: equal-weight empirical CDF, the smallest t with weighted share(score > t) ≤ 0.05; or the max of per-source thresholds, the precedent of prereg §5 line 111.

**F4 (major). The calibration sources carry resolution, JPEG or synthetic history, which confounds HN2 and P-c′ (ii).** The canonical frame puts the eyes 132 px apart (`prep_eval.py:3`).

| Source | Native inter-eye distance | Native history | Consequence |
|---|---|---|---|
| FEI | 90 px (75 to 109), 640×480 JPEG | an enlargement of about 1.47×, plus JPEG | sits between R0_61 and R0_112 |
| H1 genuine | 37.7 px, 112×112 files | about 3.5× enlargement | its 99.5 to 100% flags at τ_cam may be the known storage sensitivity rather than "source" |
| FFHQ | 259 px native, downsampled to 256 px frames | the only sharp unseen source | its frame size differs from the 512 frames, a format cue |
| SMDD | 256 px | synthetic StyleGAN2 renders from an FFHQ-trained generator | not independent of FFHQ |

- SMDD `os25k_bf_t` is also the training set of the eight A12-BR reference networks (regime d0). τ_multi is therefore invalid for the reference row.
- Putting FEI into τ_multi lets the threshold absorb part of the storage shift, which makes (ii) easier to pass.
- Fix:
  - Keep FFHQ as the primary "source shortcut" pool.
  - Print every unseen-source flag rate with its native inter-eye distance and format.
  - State that the reference row is not read at τ_multi.
  - Author item: whether SMDD renders count as "genuine" for calibration.

**F5 (major). HN2 has no falsifier, and the inherited one cannot fail.**
- §6 only says "score them".
- The review's prediction (≥30% flagged at τ_cam) is near certain for any source off the saturated floor; H1 is at 100%.
- Fix: register both of the following before scoring:
  - (a) Flags on FFHQ bona at τ_0.5.
  - (b) A scale-free read, AUC(FFHQ morphs vs FFHQ bona) on `ffhqm` landmark_complete orig, person-split.
  - Rule:
    - Shortcut supported if FFHQ bona is flagged ≥30% at τ_0.5 AND the within-source AUC ≤ 0.75.
    - Calibration shift (not a shortcut) if the within-source AUC ≥ 0.90.
    - Otherwise inconclusive.
  - Cost: about 1,000 extra images per network, a few minutes.
- HN2 must run after this registration is committed, otherwise the pool choice can be tuned on it.

**F6 (major). HN6 cannot be decided as written.**
- The reference recipe's eight-seed SD is 6.1 points on Webmorph E7 EER and 0.018 on H1. Its own-rule R0_61 flag has SD 16.1 points (5.2 to 50.3%).
- Per-seed C − A has an SD of about 6 to 9 points. If the true effect is −12, "≤ −5 on 3 of 3" holds with probability about 0.5 to 0.7. With winner's-curse shrinkage to −8 it falls to about 0.25 to 0.4.
- "B − A < 0 on 2 of 3" has a probability of 0.5 under no effect.
- The draft gives no direction: the hypothesis says seed variance exceeds arm differences, but the predictions are that arm differences replicate.
- B is optional, yet half of HN6 is the B − A read.
- Fix:
  - Include B now; no "if budget allows".
  - State that confirming both predictions falsifies HN6 for those two contrasts.
  - Tighten the H1 rule to "B − A ≤ −0.03 on 3 of 3".
  - State plainly that 3 of 3 has probability 0.125 under no effect (weak evidence) and that 0 or 1 of 3 means "not replicated".

**F7 (major). P-c′ was fitted after seeing tier 1.**
- On tier 1, parts (i) and (iii) are already met by B, Bn and C and failed by A:
  - own rule 0.5 to 3.1% against 20.4 / 31.9%;
  - raw shift 0.11 to 0.22 against about 0.37 logits (0.05 × about 7.35, which is 0.1‖w‖), with A at 1.73 / 2.64.
- So the fresh seeds test replication of a mark designed with the answer known, not an independent prediction.
- Fix:
  - Label P-c′ "written after tier 1; confirmatory on fresh seeds only".
  - Add a positive control: P-c′ is informative only if A fails it on at least 2 of 3 seeds. Fresh A may pass (i), because the reference spread is 5 to 50%.
  - Define "paired AUC": unpaired AUC over the 191 hosts, or P(shift > 0) with ties counted half.
  - Note that (i) effectively means at most 18 of 191 flagged.

**F8 (major). Several decision rules are still open forks.**
- Step 1 "at the own rule likewise": both thresholds or either?
- The number of seeds step 1 needs.
- The step-2 margin; P-g used +3 points.
- The bootstrap: B, seed, and whether the FFHQ, FEI and SMDD development pools are resampled with τ_multi refitted in each draw.
- The hash function and salt for the person split; FEI splits by person, both images on one side.
- The SMDD draw (rng, seed, list sha).
- What A is compared against if A fails step 1.
- The middle-outcome sentence.
- Fix: fill each one with a number now.

**F9 (minor). Seed and machine.**
- The draft fixes one 40 GB SXM4 type and one fit at a time. That separates seed from machine within the fresh batch.
- Fix: specify one physical lease, record the GPU UUID, and require that all arms of one seed always run on one machine. If a replacement is needed it must be the same type, and that is disclosed.
- Pooling 401 to 405 still mixes pn1a and pn1b.

**F10 (minor).**
- The loss rule (prereg l.179) names the equality term as the registered next step. Fresh seeds are a parallel step, not that step; say so.
- The C contrast was chosen on the MAD22 Webmorph test images and is re-read on the same images; label it "first-test data, re-read".

### 3. Improvements, ranked by value per GPU-hour

1. **Native history table (0 GPU, allowed now).** Inter-eye distance, format and frame size per genuine source, beside the existing tier-1 own-rule flags. This shows whether "source" is really "resolution history" (FRLL is sharp but JPEG; H1 is at 37 px).
2. **HN2 with the within-source AUC (F5, about 0.3 A100-h).** Needs this registration. It decides whether multi-source training or a head change is even the right lever.
3. **Replicate fit of A at seed 401 on the new machine (1.1 A100-h, about 0.6 USD).** Measures platform plus nondeterminism against seed variance, which answers Q3 directly. Needs registration.
4. **Five fresh seeds for A and C (and B) instead of three.** That is 15 fits, about 17 A100-h, about 10 USD, about 20 h serial; it ends 13 Nov evening if started on 12 Nov. A sign test on 5 of 5 then reaches p = 0.031. Needs registration and the lead's budget call.
5. **Alternatives.**
   - A temperature-scaled or unbounded head, or the equality term: new code, needs the author.
   - Multi-source genuine training would use up FFHQ and FEI, the only unseen genuine pools. Do not run it before HN2.

### 4. Cost and schedule

Nine fits take 69 min each on a 40 GB SXM4, about 10.4 h, plus scoring, about 12 h serial, about 7 USD at 0.59 USD/h. That is feasible by 13 Nov morning if the 40 GB type is available. Register a fallback type rule now.

### 5. Questions for the author and lead

1. Are SMDD synthetic renders admissible as a "genuine" calibration source?
2. Is FEI (inside `gtest.csv`) released for use as a development pool in this sprint?
3. Should B be fixed in? (I recommend yes.)
4. Are 5 seeds acceptable within the budget?
5. Is the SMDD 256 px set aligned to the canonical frame?

### Files

- Draft: /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/prereg_fresh_seeds_draft.md
- Registration: /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/prereg.md
- Live run.sh: /home/narolski/smad-next/src/PN1/run.sh
- Evaluation manifest: /mnt/t7/smad_next/PN1/pack2_tree/pn1/data/manifests/pn1_eval.csv
- Source manifests: /mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm.csv, /mnt/t7/smad_heldout/h1_poisson/data/manifests/h1poisson.csv, /home/narolski/mambamorph-code/smadcvpr_data/manifests/gtest.csv
- Tier-1 and reference-row JSONs: /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/tier1/
