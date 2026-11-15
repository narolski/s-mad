Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only, development data only, at 5a10e33. Saved by the PR1 owner; findings condensed, all numbers and replacement texts kept.

# PR1 part 2 (GD0, GD1, GD2; Z2b and Z2b-τ5) results review: accept with corrections

The numbers are right and every registered rule was applied as written. The main problem is wording.

**Recomputation.** All matched:
- tar bf560f53…; gate max |Δ| 0 on 15/15 networks over 19,797 rows; all GD logits finite;
- every GD AUC, flag and miss rate; row counts R0 227, R2 238, R4 74;
- Z2b ρ −0.3464; F̄ and the gate list identical to tt1_read_fs.json.

Text errors:
- X vs REC ≤ 0.60 is A 3, B 5, Sb 5 seeds;
- R2 flagged ≥ 50% is 5/5 for A and Sb;
- A's largest family on seed 406 is AgeDB.

## Findings
1. **Major. A StyleGAN "transfer" cannot be told apart from a GAN-render response.**
   - Sb flags 78-90% of one-photo MIPGAN renders; R2 vs R0 is 0.992-0.998.
   - Cross-set, descriptive: Sb's stylegan_wplus morph logits against its GD2 R2 logits give AUC 0.39, 0.51, 0.61, 0.45, 0.61.
   - Medians: R2 +3.2, R4 +3.4, wplus +3.1, FFHQ genuine −2.3.
   - stylegan_w is above the best single statistic on only 3/5 seeds.
   - "H-GD0 supported" must not fire the strategist's "GAN cells become a SOTA candidate".
2. **Major (under-description). GD2's "inconclusive" hides what the controls show.**
   - Sb R3 vs R2 0.79-0.83 and R3m vs R2 0.74-0.81, against R4 vs R2 0.86-0.93.
   - The identity step R4 vs R3 is 0.62-0.69 (A 0.53-0.63, B 0.58-0.67), as for AG1's released detectors.
3. **Moderate. Z2b-τ5 "usable" covers only the genuine side.**
   - At τ5, A misses 41-55% and B 62-70%.
   - Sb's τ5 is below 0 on every seed. Its CFP-FF flags are 0.042-0.163 at τ5 against 0.034-0.134 at the own rule.
   - Sb passes both Z2a and Z2b-τ5 on seeds 405 and 406 only (2/5). F10 is not answered.
4. **Minor. The TF32 mismatch flips no verdict.** Seed 407 would need about 82 CFP-FF rows to cross; 59 rows of any family lie within 0.035 above τ5.
5. **Moderate. GD1's "render path used" holds only in the 256 px DiffAE frame.**
   - The frame raises camera-photo flags to 2.4-52%.
   - Under-claim: SAME vs REC 0.21-0.27; X vs SAME Sb 0.78-0.85, A 0.64-0.74, B 0.68-0.75.
   - On DiffAE, only Sb s407 reaches noise_std (0.755).

## New hypotheses
- **H-new-1 (GAN render dominates).** One-photo StyleGAN inversions are flagged ≥ 50% and morph vs inversion ≤ 0.75. Falsified if ≥ 0.85 on 4/5. Needs new generation; after the freeze; author.
- **H-new-2 (Sb's identity step is larger).** Test on fresh networks (MS1 SbM3, SbV) with the same GD pack and gate: R4 vs R3 ≥ 0.62 and X vs SAME ≥ 0.78 on ≥ 4/5. About 0.5 GPU-h.
- **H-new-3.** A cut-off of max(τ5, own rule) gives Sb a joint pass on ≥ 4/5. Post hoc; confirm on MS1's TT1 scores.

## Next experiments
In order:
1. Amendment-4 printed table (0 GPU).
2. 27-statistic cues on the GD1/GD2 rows (CPU).
3. The F10 ruling τ5 against max(τ5, own rule) (author).
4. MS1 SbM3/SbV on the GD pack (0.5 GPU-h).
5. StyleGAN inversion control (after the freeze).
6. GX1 (after the freeze).

## Risks
GAN benchmark cells will probably score well through the render response alone. Say before the sealed read that GAN-cell scores are not shown to be morph-specific. F10 is still open.
