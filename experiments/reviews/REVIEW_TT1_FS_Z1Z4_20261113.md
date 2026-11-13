Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only. Post-result review of the TT1-FS post-result items Z1-Z4 (result.md at 34a2eef). Report as returned, unedited; saved by the TT1 owner after the record keeper's ledger (486d089). Wording fixes were applied in cdb79b4.

## Verdict: sound, with three wording fixes

All four rules were applied as registered in prereg.md §12 (62139a7, registered before computing). The labels are carried: Z1 is post hoc, Z2-Z4 are descriptive. The numbers in result.md match zfs.json, and the ones I recomputed independently match too. Three places need rewording. Z1's "no cost" result sits on a floor/ceiling. Z3 says B flags nothing, but B flags a few. Z3 also leaves out the other-family rows and the clean-photo baseline that §12 says to print. Z2 has one value sitting exactly on its threshold.

## What I recomputed (from stored scores_eval.npz, pn1_eval.csv and zfs.json)

- **Pool sizes.** 582 / 180 / 291 rows. The ladder R4 pool is the `strength==""` rows (opencv plus facemorpher). That is 582 of the 1164 R4 rows, which is the registered "native" pool.
- **Splice miss shares.** A_s405 0.9553, B_s405 0.9863, Sb_s406 0.1924. All three match.
- **Z1 ρ.** −0.346, matches.
- **Z4 ρ.** 0.964, matches. Without seeds 401/402 it is still 0.90 on the five fresh seeds alone, so it holds across the two hosts.
- **Rules.** The Z1 rule threshold (> 0.02 on at least 4 of 5 seeds) and the Z3 rule threshold (≤ 0.005 on at least 4 of 5 seeds) are coded as registered.

## Findings, most important first

1. **(Major) Z1 "no cost" is uninformative on 2 of 3 pools.**
   - Ladder R4 and AF0 u50 misses are 0 to 0.6% for all 15 networks, so they cannot show a cost.
   - On splice S4, A and B both miss 92 to 99%, so y is effectively splice miss divided by 3.
   - "No B-against-A miss cost shown" therefore means "none visible on pools where both arms are at the floor or the ceiling".
2. **(Major) Z1's pooled ρ is a between-arm effect; within each arm the sign flips.**
   - Within-arm Spearman of F̄ against y (my post hoc check, from zfs.json): A +0.2, B +0.7, Sb +0.8.
   - So inside every arm, more false alarms go with more misses, not fewer. The pooled −0.35 comes only from Sb's level shift. The current text says this qualitatively; it should say it explicitly.
   - The p of 0.10 is one-sided (`perm <= obs`, zfs.py). Say so.
3. **(Major) Z3 says "B does not" flag; B flags a few.**
   - B's CFP-FF border-reference flag share is 0.000 to 0.019 (0.014, 0.010, 0.007, 0.000, 0.019).
   - The excess is not specific to CFP. §12 says the other six families are printed, but result.md omits them. Sb − B is +0.026 to +0.060 on MSU-MFSD and +0.026 to +0.048 on Oulu-NPU. CFP-FF is the largest gap on 3 of 5 seeds; on seed 404 it ties MSU-MFSD at 0.050.
   - The text can be strengthened in one respect. On the same photos without a blanked border (pool R_cam in tt1_read_fs.json), both B and Sb flag 0.000 on all 5 seeds. That ties Sb's flags to the border itself, not to a generally higher flag rate.
4. **(Minor) Z2 has one value exactly on the threshold.**
   - Spearman(F̄, |ρ_LFW|) is 0.70, exactly the ≥ 0.7 cut. With n = 5, Spearman values come in steps of 0.1, so one swapped rank gives "weak". Report it as "0.70, at the threshold".
   - The word "related" is not in the prereg. It is the coded label for ≥ 0.7, which the prereg states only as a prediction. Say that.
   - Seeds 401/402 do not fit the pattern. A_s401 has the highest F̄ of all seven seeds (0.057) but a middling geometry-112 share (0.460).
5. **(Minor) Z4 "consistent" means co-variation only.** Seeds 401/402 were trained on pn1a/pn1b and scored on tt1c, a different host from seeds 403-407. Seed 401 is the extreme on both axes. Say "association, 7 seeds".

## Text corrections for "Post-result items Z1-Z4" in result.md

**Z1, replace the last bullet with:**
"- Ladder R4 and AF0 u50 misses are at the floor (≤ 0.6%) for every network, and A and B both miss 92-99% of S4 splices. So y can show a B-against-A cost only on splices, and both arms are near the ceiling there. The verdict is therefore weak evidence of no cost. The pooled ρ is between arms. Within each arm, Spearman(F̄, y) is +0.2 (A), +0.7 (B) and +0.8 (Sb) (post hoc, from zfs.json), so within an arm more false alarms go with more misses. The p value is a one-sided permutation p."

**Z2, change the first sub-bullet to:**
"Spearman(F̄, geometry-112 flag share) = 0.90 and Spearman(F̄, |ρ_LFW|) = 0.70, the latter exactly at the 0.7 cut. With n = 5, Spearman moves in steps of 0.1. 'Related' is the coded label for ≥ 0.7."
**Add:** "A_s401 has the highest F̄ of all seven seeds but a middling geometry-112 share."

**Z3, replace the "So Sb flags ..." bullet with:**
"- Sb flags more training-source camera photos once a CFP-FF-shaped constant border is blanked in (Sb 0.029-0.163; B 0.000-0.019). On the same photos without the border, both flag 0.000 on all five seeds. The excess is not specific to CFP: Sb − B is +0.026 to +0.060 on MSU-MFSD and +0.026 to +0.048 on Oulu-NPU, and +0.00 to +0.03 elsewhere. CFP-FF is the largest gap on 3 of 5 seeds. This is descriptive and Sb is splice-trained, so it does not show that Sb uses borders on unseen CFP-FF images."

**Z4, replace the last sub-bullet with:**
"- This is an association over 7 seeds from two hosts. Seeds 401/402 were trained on pn1a/pn1b and scored on tt1c; seed 401 is the extreme on both axes. On seeds 403-407 alone, ρ = 0.90."

## Files
- /home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/result.md (section under review)
- /home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/prereg.md (§12)
- /home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/zfs.json
- /home/narolski/smad-next/src/TT1/zfs.py
- /home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/tt1_read_fs.json (source of the R_cam 0.000 baseline)
