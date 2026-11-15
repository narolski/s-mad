Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only. Saved by the lead because the TT1 owner agent stopped with an API authentication error before it could save and apply it.

**Post-result review: TT1-FS (seeds 403-407) and TT1-X Part 1 (Sp), smad-next at b82163c. I edited no files and touched no remote machines.**

## Verdict: needs qualification
The registered verdicts are applied correctly. The reader logic matches the registration. Every number I recomputed from the raw scores matches result.md. The gate is 15/15 and 3/3 byte-identical on 19,797 rows (`gate_fs.json`, max |Δ| 0). The problems are in how the result is framed:
- TT-H4 "falsified" for B is a label effect, not a finding against B (F2).
- The A/B effect shrank from seeds 401/402 to the fresh seeds, and the block is confounded with the machine (F3).
- Two predictions that failed on every fresh seed (A and Sb under TT-H1) are not named as such (F1).
- B's flag rate on sharp FFHQ genuine photos is printed but not discussed (F4).

## Numbers I recomputed (reproduce exactly)
Pool U_p = 21,035 photos; R_cam n = 417; R_ffhq n = 2,000.

| Network | F̄ | F_max | FFHQ genuine flag |
|---|---|---|---|
| A_s403 | 0.0070 | 0.030 | 0.076 |
| A_s404 | 0.0482 | 0.183 (LFW+CALFW) | 0.108 |
| B_s404 | 0.0073 | 0.019 | 0.108 |
| B_s406 | 0.0003 | — | 0.037 |
| Sb_s404 | 0.0411 | 0.134 (CFP-FF) | 0.050 |
| Sb_s407 | 0.0175 | — | 0.032 |
| Sp_s404 | 0.0297 | 0.114 | 0.154 |

Sp_s404 also flags 0.7% of R_cam.

I also re-derived every per-pack TT-H4 ρ from `tt1_read_fs.json`.

## Findings (most severe first)

**F1 (major): two predictions failed on 5 of 5 seeds and the text does not say so.**
- **A, TT-H1.** The prediction was at least 4 failing families. A fails 0, 2, 1, 0 and 0 families on seeds 403-407, so the prediction held on 0 of 5 seeds. A meets B's own transfer bar on 3 of 5 seeds; over seeds 401-407 that is 3 of 7. "Mixed" is the correct registered label, but it hides this.
- **Sb, TT-H1.** The prediction was at least 2 failing families. It held on 0 of 5 seeds; s404 fails one family. The registered falsifier ("transfers") is met on 4 of 5. This reverses the 401/402 verdict "supported narrowly". The table line 257 says "transfers on 4 of 5" without saying the prediction is falsified; only line 266 hints at it.

**F2 (major): B's TT-H4 "falsified" is misleading.**
- The rule checks "ρ ≥ 0 in at least 3 packs" before it checks B's own prediction (same order in `tt1_read.py:382-388` and `tt1_read_fs.py:107-112`), so it reads correctly.
- But "softer photos score higher" being falsified for B is exactly what B's own prediction implied. B's |ρ| is also below A's in at least 3 packs on 4 of 5 seeds (not on s406, where A itself is flat).
- B's ρ lies between −0.13 and +0.22. CALFW is +0.13 to +0.22 on every seed, so sharper photos score slightly higher there.
- Sb is "mixed" only because A is weak on s405/s406. Sb's |ρ| is at most 0.154 everywhere.
- A's pattern does replicate: ρ ≤ −0.15 in LFW on 5 of 5 seeds and in AgeDB on 4 of 5; CALFW and CFP-FF stay near 0. That is the same two-pack pattern as 401/402.

**F3 (major): the B − A effect shrank, and the block is confounded with the machine.**

| | Seeds 401/402 | Seeds 403-407 (mean ± SD) |
|---|---|---|
| B − A | −0.033 / −0.035 | −0.021 ± 0.016 |
| A, F̄ | 0.057 / 0.038 | 0.023 ± 0.019 |
| B, F̄ | 0.024 / 0.002 | 0.0024 ± 0.0028 |
| Sb − B | +0.021 / +0.031 | +0.018 ± 0.009 |

- B − A is negative on 7 of 7 seeds. The bar of −0.03 is met on 4 of 7.
- Sb − B is positive on 7 of 7, with every interval above 0. It is the more stable lead.
- Seeds 401/402 were trained on pn1a/pn1b and scored on tt1c (A100-SXM). Seeds 403-407 were trained and scored on pn1fs (A100-PCIe). So the difference between blocks mixes regression to the mean with host differences. Any statement pooled over 7 seeds must say "two training blocks on different hosts".
- Most of the B − A spread comes from A: its F̄ ranges from 0.004 to 0.048.

**F4 (major): B's low false-alarm rate holds on the low-resolution frames, not on sharp FFHQ photos.**
- B's FFHQ genuine own-rule flags over 7 seeds: 17.8, 6.4, 5.2, 10.8, 6.1, 3.7 and 2.5%. That is above 10% on 2 of 7 seeds.
- Paired B − A on FFHQ for seeds 403-407 is −0.024, 0, −0.028, −0.028 and −0.049. On s404, B equals A.
- Sb has the lowest FFHQ flags (2.4-5.1%).
- result.md prints these values (lines 305-308) but should state the consequence.

**F5 (minor): small precision fixes.**
- TF32 wording: the TT1 rows ran with matmul TF32 off but cuDNN TF32 on (versions.txt: `matmul.allow_tf32 False cudnn.allow_tf32 True`). "TF32-off logits" (line 247) should say "PyTorch defaults (matmul TF32 off)". The split is at most 0.042 (A_s403) with 0 decision flips, so nothing changes.
- B's "largest 3.3%" is the bootstrap upper bound. The exact (Clopper-Pearson) upper bound for zero-event MSU-MFSD is 5.5% on every seed. Both are under 10%.
- In the TT-H6 table, Sb − A and B − Sb have empty per-seed cells.

**F6 (minor): A's storage reaction replicates (printed read, no rule).**
- A's flag share on camera photos after the 112 px path is 18.5-50.4%, against B 0-1.2% and Sb 2.2-9.1%.
- R3(g) at 112 px is below 0.5 for A on every pack and seed (0.23-0.50).
- s406 is the weak seed (0.185; R3(g) 0.42-0.50).
- As in 401/402, A's TT-H5 verdict "source matters beyond geometry" rests on the 224 px anti-spoofing sets only. The fresh-seed section does not repeat that caveat.

**F7 (note): Sp, 3 seeds.**
- Sp F̄ is 0.023-0.033, against Sb 0.013-0.041 at the same seeds, so they cannot be told apart.
- Sp flags more FFHQ genuine photos (8.5-15.4%) and is the only arm with nonzero R_cam flags (0.2-0.7%).
- The reader was pinned after the tar was fetched but before any score was opened. That is disclosed; accept it.

## Text corrections for result.md
- **Line 257, A cell.** Change to: "**mixed** (3 of 5 'transfers'); the prediction (at least 4 failing families) held on 0 of 5 seeds; s404 fails 2 families, s405 fails 1."
- **Line 257, Sb cell.** Change to: "**transfers on 4 of 5 seeds**, so the prediction (at least 2 failing families) is falsified on fresh seeds (it held on 0 of 5). This reverses the narrow 401/402 'supported'. s404 fails 1 family (cfp_ff, 13.4%)."
- **Line 260, B cell.** Change to: "**'falsified' by the registered rule, 4 of 5** (ρ ≥ 0 in at least 3 packs): B shows no 'softer scores higher' effect. This agrees with B's own prediction; |ρ| is also below A's on 4 of 5 seeds. Not evidence against B."
- **Line 260, Sb cell.** Add: "the mixed count comes from A being flat on s405/s406; Sb's |ρ| ≤ 0.154 everywhere."
- **Line 247.** Change "this job's TF32-off logits" to "this job's logits (PyTorch defaults: matmul TF32 off, cuDNN TF32 on)".
- **After line 283, add:** "Across all seven seeds, B − A is negative on 7 of 7 and meets −0.03 on 4 of 7; Sb − B is positive on 7 of 7. The fresh-seed effect (−0.021) is about 60% of the 401/402 effect. The two blocks differ in training and scoring host (pn1a/pn1b plus tt1c, against pn1fs), so the shrinkage is not attributed."
- **After line 308, add:** "On FFHQ genuine photos, B is not clearly below A (paired −0.05 to 0; equal on s404), and B exceeds 10% on 2 of 7 seeds (s401, s404). B's low false-alarm rate is specific to the low-resolution bordered frames."
- **Line 299, add:** "A's TT-H5 'source matters' verdict rests on the 224 px anti-spoofing group only, as in 401/402."
- **Fill the empty TT-H6 cells:**
  - Sb − A per seed: +0.008, −0.007, −0.021, +0.010, −0.005.
  - B − Sb per seed: −0.013, −0.034, −0.011, −0.014, −0.017; mean −0.018 ± 0.009.

## What the paper may and may not say
**May say:** "On about 21,000 genuine photos from eight development sources not seen in training (small faces enlarged 1.7-3.5x, with a black border), the protocol-trained network kept its fixed decision rule on all seven seeds: at most 4.9% of any family flagged, mean F̄ 0.6%. The plain network exceeded the rule on 4 of 7 seeds (up to 23.5%). Both remain clearly displaced from the training camera photos, so a threshold calibrated on camera photos does not transfer." Add the seed/host note.

**May not say:**
- that B is the better arm overall;
- that B transfers to sharp sources (FFHQ: up to 17.8%);
- anything about misses or detection;
- that the B − A size is fixed;
- that the plain network "fails to transfer" in general (it passes on 3 of 7 seeds);
- that splice positives (Sb) "cost" false alarms in general. Sb is higher on these frames but lowest on FFHQ.

## New hypotheses and next experiments (ranked by information per GPU-hour)
1. **Repeat H-new-4 on fresh seeds (0 GPU; needs a registration amendment, post hoc).** The 15 FS networks' stored `scores_eval` already contain the ladder, AF0 and splice rows. Test ρ(F̄, development miss) over the 15 networks. Prediction: the trade is again driven by Sb's lower splice misses, with no B-against-A trade. Falsified if B's development misses exceed A's by more than 2 points on at least 4 of 5 seeds. This decides whether "B lowers false alarms at no cost in misses" can be said.
2. **A's false-alarm rate tracks its storage sensitivity (0 GPU, descriptive).** Within A at seeds 403-407, the ranking by F̄ and the ranking by 112 px geometry flag share agree almost perfectly (Spearman about 0.9). LFW |ρ| also tracks them: s406 is the weakest on all three. Mechanism: A reads missing high frequency or resampling history (H-new-1). Prediction: across seeds, F̄ is correlated with the 112 px geometry flag share and with the LFW |ρ|, with Spearman at least 0.7. Report 401/402 separately: there s402 has the higher 112 px share but the lower F̄, and the hosts differ. Falsified if ρ < 0.3.
3. **Sb's excess comes from CFP-sized borders (0 GPU).** Sb's excess is concentrated in CFP-FF (3.4-13.4%) and OULU, as in 401/402. Compare Sb against B on the already-printed per-family border-reference flag shares and on R3(c) for CFP-FF. Prediction: Sb's flag share on CFP-bordered camera photos is above B's on at least 4 of 5 seeds. Falsified if the two are equal, in which case border is not Sb's cue on CFP.
4. **Why B flags sharp FFHQ photos (0 GPU).** Correlate B's FFHQ flag with its TT1 F̄ across 7 seeds; B_s401 is high on both. Decides whether a single "seed instability" explanation covers both.
5. **Locating the onset of A's enlargement effect (H-new-2 onset still unknown).** This needs new resampling ladders. Those are an author item, not agent code. Only after the deadline.

| Item | GPU-h | When | What it decides | Approval needed |
|---|---|---|---|---|
| H-new-4 on fresh seeds | 0 | now | the B "no miss cost" claim | amendment (post hoc label) |
| A F̄ vs storage sensitivity | 0 | now | mechanism sentence for A | amendment (descriptive) |
| Sb on CFP borders | 0 | now | whether Sb's excess is a border cue | amendment (descriptive) |
| B FFHQ vs F̄ | 0 | now | the limits of the B claim | none (printed values) |
| Enlargement onset ladder | about 1 | after the deadline | where A's storage cue starts | author (resampling code) |

**Files reviewed:**
- `/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/result.md` (lines 232-325)
- `/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/tt1_read_fs.json`
- `/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/tt1_read_fs_tables.md`
- `/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/prereg_fs1_block.md`
- `/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/prereg_x_block.md`
- `/home/narolski/smad-next/src/TT1/tt1_read_fs.py` (lines 70-115)
- `/mnt/t7/smad_next/TT1/results/unpacked_fs/TT1_A100_pn1fs_fs/versions.txt`

Recompute script: `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/recomp.py`
