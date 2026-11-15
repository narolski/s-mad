Reviewer: results-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited.

## SM1 post-result review: SMDD partner audit and rebuild, ViT-B/16 reading and post hoc items 11 and 13

I only read files. I made no edits, did not open valx, FST or A12SP, and touched no cluster. I recomputed everything from the raw tars `/mnt/t7/smad_next/SM1/results_rented/SM1B_{a,c,e,f}_s40{1,2}.tar` (all nine sha256 match their `.sha256` files) and from the test lists in `flists/`. Scripts are in `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/sm1rev/scripts/` (`recomp.py`, `audit2.py`, `mordiff.py`, `miss.py`, `smddx.py`).

### 1. Verdict: the numbers reproduce, but two headline readings are not supported

Every number in the brief reproduces exactly:
- Landmark-7 EER: a 2.76, c 5.29, e 2.24, f 2.38.
- Diffusion-7 rise: a +18.04, c +29.09, e −3.10, f −1.21.
- Camera-threshold reads: 0.110 / 0.201 / 0.049 (untouched FRLL flagged), +0.245 / +0.515 / +0.120 (JPEG 50 − untouched), 0.020 / 0.002 / 0.150 (landmark-4 miss).
- Partner trace (trained − KE): 0.056 and 0.033.

The two readings that fail:
- **"History crossing removes the MorDIFF reaction" is wrong in substance.** On MorDIFF itself, arms e and f stop detecting the morphs.
- **The camera-threshold comparisons between e, f and a are not readable.** For e and f the threshold sits on the floor of a bounded head.

The partner trace is under-claimed: it is real when measured by rank.

### 2. Findings, most severe first

**F1 (blocker): the MorDIFF claim.**
- The +18 is the mean over 7 diffusion cells (MorDIFF plus 6 DiM). On MorDIFF alone, arm a rises +12.2 / +11.8 (native EER 7.4 / 8.3, history-matched 19.6 / 20.1).
- On MorDIFF, history-crossed e has native EER 33.8 / 47.1% and misses 95.2 / 98.9% of MorDIFF morphs at its own rule. At the camera threshold it flags 99.5% of native MorDIFF genuine photos. Arm f: 31.9 / 40.3%, own-rule miss 97 / 98%.
- So the negative "rise" (MorDIFF −10.3 / −14.8) comes from losing detection, not from robustness.
- Diffusion-7 native EER doubles (a 6.40 → e 13.76). This cost is missing from `result.md:586-589`.
- "e and f flag 0.00 of history-matched pools at the own rule" only says that they flag almost nothing at all at that rule. Landmark-4 own-rule miss is 0.49 / 0.51 for e and 0.45 / 0.43 for f.

**F2 (blocker for wording): every camera-threshold reading of the LoRA fits sits on a bounded head.**
- Head = Linear(512, 1) on normalised features: ‖w‖ 3.80 for a s401 and 3.87 for e s401, bias about −0.09. Logits range from −3.76 to +3.53.
- The camera threshold (95th percentile of AR1 R0) minus the R0 median is:

| Fit | a s401 | a s402 | e s401 | e s402 | f s401 | f s402 | c s401 | c s402 |
|---|---|---|---|---|---|---|---|---|
| Threshold − R0 median (logits) | 0.28 | 0.98 | 0.068 | 0.055 | 0.10 | 0.09 | 2.2 | 6.0 |

- The FRLL photo median lies only 0.04 (e) to 0.10 (f) logits below the threshold. "e doubles flags, f brings both below a" is therefore a difference of a few hundredths of a logit inside the floor band. The seeds disagree (e JPEG increment 0.38 / 0.65; f 0.05 / 0.19).
- The near-zero miss at this threshold (e landmark-4 0.002, MorDIFF 0.0) is bought by flagging whole genuine sources, the same pattern as PN1 (`REVIEW_PN1_TIER1_20261112.md:12,39-48`).
- Arms a, c, e and f are each in a different calibration regime, so they cannot be compared at this threshold.
- This affects every LoRA camera-threshold cell in SM1, including the ViT-L/14 line at `result.md:561-564`. It does not affect the frozen linear heads, which are unbounded, or the item-13 increments (frozen heads).
- Wording rule: call these "floor-calibrated; descriptive only", always print the threshold − R0 median gap beside them, and make no between-arm statement.

**F3 (major): the A11 validity condition is misdescribed and applied inconsistently.**
- At the own rule, arm a's MorDIFF pool flags are 0.034 / 0.368 (mean 0.20). The "0.05" at seed 401 is the DiM fast_dim pool (0.054). The "0.21" is the mean of each seed's maximum, taken over different pools. `result.md:581` mixes the two pools.
- Seed 401 alone fails the own-rule branch. The condition (`prereg.md:360-362`) passes on the two-seed mean.
- The camera branch passes trivially (MorDIFF 1.00 / 0.95) because the threshold is on the floor.
- For ViT-L/14 (`result.md:561-564`) the owner reported "does not count at own rule" even though the registered "either threshold" rule is formally met.
- Fix: apply the rule as written to both families (met), then add: "the camera branch is uninformative on bounded heads; the own-rule branch is met for ViT-B/16 on the mean only (1 of 2 seeds) and not met for ViT-L/14."

**F4 (major): what two seeds can support.**
- The PN1 reference (8 A12-BR ViT-B/16 retrains on the released SMDD, `PN1/result.md:93-95`): 7 of 8 flag more than 10% of some history-matched pool at the own rule. Own-rule R0_61 flags span 5.2 to 50.3% and Webmorph E7 EER 9.4 to 27.0% (`REVIEW_PN1_TIER1:110`).
- SM1's arm a (5.4% / 36.8% maximum pool) brackets that range. Two seeds cannot estimate a flag rate (between-seed SD about 0.24).
- They do support signs that repeat within each seed:
  - the diffusion-7 rise of a (+17.3, +18.8; above the 8-network +11.39 [8.00, 14.78] in `prereg.md:119`, but on a different manifest);
  - the a − e gap (about 21 points in both seeds);
  - the MorDIFF collapse of e and f (all four fits).
- GAN-3 (e 17.2 / 32.9) and every camera-threshold cell: no claim.
- There is no winner's-curse issue, since the arms were fixed in advance. But any later choice of f over e would be a selection made on benchmark cells.

**F5 (major): the exposure labelling is inconsistent.**
- `README.md:35-36` lists c (and b′, c′) as unaffected audit arms. `result.md:569-570` labels c as development exposure.
- README's own logic ("d, d+ … remedy steps toward e") covers c too: c is the morph base of d, e and f, and SMDD-T proposed it as a better SMDD. Label c as exposure.
- b′, c′, K = 5 random, K = 50 and K = 500 stay audit of SMDD's construction only as long as no sentence recommends them as a training set.
- The FRLL JPEG photos are benchmark-derived, so the e-vs-f JPEG comparison is exposure.
- PN1's record has no exposure note about SM1. Add one: the team has seen benchmark scores of history-crossing and JPEG remedies.

**F6 (major, under-claim): the partner trace is real; the ceiling compresses it.**
- Within-key AUC (trained-partner over KE, 500 keys, 10,000 key-bootstrap draws):

| Fit | a s401 | a s402 | a, both seeds | b s401 | c | e | f |
|---|---|---|---|---|---|---|---|
| AUC | 0.727 | 0.786 | 0.757 [0.745, 0.768] | 0.814 | 0.533 | 0.562 | 0.586 |

- Rank difference-in-differences: a − c 0.224 [0.210, 0.237]; a − e 0.194 [0.180, 0.209].
- The mean-logit gap is small because trained-partner scores sit at the head's ceiling (SD 0.02 to 0.03, mean 3.50, maximum 3.53). KE has a lower tail (SD 0.23 / 0.16; 1.7% / 0.6% below 3.0 logits). No decision changes (own-rule miss ≤ 0.3%).
- The registered H-new-5 threshold (trained − KE ≥ 1 logit, `prereg.md:416-420`) cannot be reached on a ±3.8 bounded head. Register a rank read before the ViT-L/14 audit scores (job 3547052) are opened.

**F7 (moderate): item 11 (five random partners) is correctly falsified, but the inference is narrow.**
- d5 = 5.07 (seeds 4.84 to 5.21, all ≤ 5.5), so H-new-1 is falsified by its rule.
- b → d5 −2.54 [−4.21, −0.88]; d5 → K = 50 −0.29 [−1.31, +0.89]. Most of the "partner count" gain is "these five".
- This rests on one alternative set of five, so the variance between partner sets is not estimated.
- d5 flags 0.46 of the MorDIFF pool against b's 0.21: whatever improves native EER raises history-pool flags.
- Conclusion 4 (`result.md:43-44`, "untested") is stale.

**F8 (minor): documentation is stale.**
- `result.md:7-9`, `596-600` ("11 and 13: done (above)", but no d5 or item-13 table exists in `result.md`) and `643` ("LoRA … readings not in this file") are out of date.
- `NOTEBOOK.md:62` still says "running" and shows only Part 1.
- The brief says "rented A100", but the machine was an RTX 6000 Ada (`prereg.md:456-458`).
- The registered SMDD-X falsifier, if read: not falsified (e rise −3.1 < 4; FRLL FaceMorpher / OpenCV E7 EER 0.0–0.9). It averages the MorDIFF collapse away.

### 3. Exact text corrections

**1. Replace `result.md:586-589` with:**
> "Reading (2 seeds, our frames): the standard ViT-B/16 recipe on the SMDD release files rises +18.0 EER points on the 7 diffusion cells (MorDIFF alone +12.0: 7.9 → 19.9) when genuine photos carry the morphs' storage history. Development exposure, not a method result: history-crossed fits (e, f) lose MorDIFF detection (native EER 34 / 47% and 32 / 40%; own-rule miss 95 to 99%); their negative rise reflects that loss. Diffusion-7 native EER doubles (6.4 → 13.8). Camera-threshold reads of these fits are floor-calibrated (threshold 0.06 to 0.10 logit above the camera-photo median for e and f) and are not compared between arms."

**2. Replace the validity sentence at `result.md:580-581` with:**
> "A11 validity: met as registered. MorDIFF pool at the own rule 0.20 (seeds 0.03, 0.37; seed 401's largest pool is DiM fast_dim 0.05, so 1 of 2 seeds). The camera branch is uninformative on this bounded head."

**3. Add to the audit paragraph at `result.md:591-594`:**
> "By rank the trace is clear: within-key AUC trained over KE 0.757 [0.745, 0.768] for arm a against 0.53 to 0.59 without the five; DiD a − c 0.224 [0.210, 0.237]. Mean gaps are compressed by the head's ±3.8 bound."

**4. Conclusion 4:**
- Replace "Whether the number or the identity … untested" with: "One draw of five random partners recovers most of the gain (b → d5 −2.5 [−4.2, −0.9]; d5 → K = 50 −0.3 [−1.3, +0.9]) and raises history-pool flags (MorDIFF 0.21 → 0.46). SMDD's particular five, not the count, account for most of the gap; the variance between partner sets is unmeasured."

**5. `README.md:35-36`:** move c from the audit list to the exposure list.

**6. Paper sentence (audit, allowed):**
> "Retraining the standard MADation ViT-B/16 recipe on the SMDD release (2 seeds; 7 of 8 in a larger reference set) gives a storage-history rise of +18 EER points on diffusion cells."

Not allowed as a benchmark result: anything about e or f. If mentioned at all, label it as a development observation: "it collapsed MorDIFF detection."

### 4. New hypotheses

**H-new-A: MorDIFF detection is mostly the storage cue.**
- Statement: the standard recipe on SMDD detects MorDIFF mainly through storage history. Removing that cue removes the detection.
- Why the result suggests it: arm a's MorDIFF EER nearly triples under history matching, and history-crossed fits lose MorDIFF entirely.
- Test (development data only): score the saved trainable weights of a, e and f on FZ2 / DG1's own diffusion ladder (FRGC / colorFERET) against camera photos with and without matched history.
- Prediction: e's AUC on history-matched development diffusion morphs ≤ 0.65; a's AUC drops ≥ 0.15 from native to history-matched.
- Falsified if: e ≥ 0.80.
- Cost: about 0.2 A100-h. Fits before 14 Nov.

**H-new-B: the camera-threshold differences between e and f are set by the floor gap.**
- Statement: the flag rates at the camera threshold depend on how far the threshold sits above the camera-photo median, not on how the network reacts to history.
- Prediction: across the 8 fits, the flag rate tracks (threshold − source median) with |ρ| ≥ 0.8. On AR1 development copies, a scale-free paired AUC (photo against softened copy) differs by < 0.05 between e and f.
- Falsified if: the paired AUC difference is ≥ 0.10 with an interval excluding 0.
- Cost: 0 GPU for ρ; the AUC part needs the item-13 copies scored by the LoRA fits (about 0.05 A100-h).

**H-new-C: partner-set variance at K = 5 is large.**
- Statement: performance at five partners depends strongly on which five.
- Test: 4 more seeded draws of five random partners, frozen heads, read on SMDD's own evaluation split and the AR1 ladder (not benchmark cells).
- Prediction: SD over draws ≥ 1 EER point, with SMDD's five inside the range.
- Falsified if: all draws fall within 0.5 of d5 and SMDD's five lie more than 2 SD out.
- Cost: about 1.2 CPU-h per draw at the 2-process DGX limit, plus about 0.15 A100-h of features. Fits by 14 Nov.

**H-new-D: the bounded head hides the trace on ViT-L/14 as well.**
- Prediction: ViT-L/14 arm a has trained − KE < 0.2 logit but within-key AUC ≥ 0.70.
- Falsified if: AUC ≤ 0.60.
- Cost: 0 GPU, but it must be registered before job 3547052 is read.

**H-new-E: e's negative rise is a penalty on camera detail.**
- Statement: e rates fine capture detail as morph-like, so native photos score above their softened copies.
- Prediction: on AR1 R0, the logit increment from softening (61.2 / 112.7 px) is < 0 for e and > 0 for a.
- Falsified if: e's increment is ≥ 0.
- Cost: about 0.05 A100-h, development data.

### 5. Next experiments, ranked

| # | Experiment | GPU-h | When | Decides | Approval |
|---|---|---|---|---|---|
| 1 | Text corrections F1 to F8; exposure relabel of c; PN1 exposure note | 0 | now | paper wording | lead |
| 2 | Register a rank read for the ViT-L/14 audit (H-new-D) before 3547052 is opened | 0 | now | H-new-5 testability | A12 note |
| 3 | Floor table for every LoRA fit (head norm, threshold − R0 median, per-source median) (H-new-B, ρ part) | 0 | today | how the camera-threshold cells are worded | none |
| 4 | Use PN1's 8 reference retrains as the seed spread for arm a, instead of new seeds of a | 0 | today | the "two seeds" sentence | none |
| 5 | Saved ViT-B/16 a, e, f scored on the development diffusion ladder and the AF0 softened copies (H-new-A, H-new-E) | 0.25 (about 0.12 USD rented) | 13 Nov | whether history crossing destroys diffusion detection, judged on development data | amendment, lead |
| 6 | Partner-set variance, 4 draws (H-new-C) | 0.15 + CPU | 13 to 14 Nov | "SMDD's five are atypical" | amendment; ruling on reading the SMDD evaluation split |
| 7 | b′ ViT-B/16 fits (item 12, queued) | about 2 | 13 Nov | partner diversity on the standard recipe (audit) | already registered |

No new benchmark scoring of any remedy arm or candidate network is proposed.

### 6. Risks to the story
- History crossing may only trade the storage cue for losing diffusion detection. A remedy claim needs development-data proof that detection survives (row 5) before any benchmark read.
- No fixed-threshold claim survives on bounded heads.
- The partner-audit headline should lead with rank effects and the frozen-encoder releases.

### 7. Edits for CONCLUSIONS.md
- **What we have learned:** "SMDD's five partner images leave a rank trace even in the standard ViT-B/16 recipe (AUC 0.76 against 0.53 to 0.59). The standard recipe's diffusion detection reacts strongly to storage history (+18 points; MorDIFF +12). Training with history crossing stopped that reaction but also stopped detecting MorDIFF (development exposure)."
- **How sure we are:** "Two seeds on one machine, our frames. Signs that repeat within each seed are solid; flag rates are not (seeds 3% and 37%; reference range 5 to 50%). Camera-threshold reads of the LoRA fits sit on a saturated floor and are descriptive. The five-random-partner result is one draw."
- **Future directions:** "Score saved fits on the development diffusion ladder and softened copies; a rank-based read of the ViT-L/14 audit, registered first; partner-set variance on SMDD's own split; no benchmark reads of remedy arms."

Files: `/home/narolski/smad-next/experiments/SM1_smdd-partner-audit-and-rebuild/{result.md,README.md,prereg.md,p3_full.json,a12_af0soft.json}`, `/home/narolski/smad-next/experiments/reviews/{REVIEW_SM1_20261111.md,REVIEW_PN1_TIER1_20261112.md}`, `/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/result.md`, `/mnt/t7/smad_next/SM1/results_rented/`.
