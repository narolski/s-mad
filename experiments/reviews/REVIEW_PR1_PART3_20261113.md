Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only, development data only, at bdd99da. Saved by the PR1 owner; condensed, all findings kept.

# PR1 part 3 (amendment 4) review: accept with corrections

The reviewer recomputed independently, with sklearn AUCs. All 6 floors match to 4 decimals. All 18 part-B verdicts, a sample of part-A numbers and the joint operating point for all 15 networks also match. The baseline check passes. The rule was applied as written: F = max(best single statistic on the same images, s-lad, b-lad); fixed direction; thresholds as registered.

## Findings
1. **Major: the times in the record are wrong.**
   - The registration commit 6b3af89 is at 12:10:23, not "about 12:25".
   - The read ran at 12:11:47, not "about 12:40".
   - An 8-row cue smoke run at 12:09:33-35 was not disclosed.
   - The full cues finished after the commit (12:11:03, 12:11:34), and the committed code is the code that ran.
   - The real post-hoc exposure is that the network AUCs were known from part 2; this is already labelled.
2. **Major: GD1 REC vs G is at ceiling** (F 0.996). "Not beyond" there carries no information.
3. **Medium: wording.**
   - The summary should include B's inconclusive X vs SAME.
   - Sb's X vs SAME cell should state the margins: seeds 403 and 405 miss the bar by 0.002 and 0.0015.
4. **Medium: "beyond" on R2 vs R0 is narrow for A and B** (B seed 407 margin +0.009). Print the margins.
5. **Medium: selection bias in F.**
   - Cross-fitted best single statistic (post hoc): 0.681, 0.721, 0.855, 0.878, 0.640.
   - Only Sb's X vs SAME would move; it stays inconclusive by the rule.
   - The GD2 identity verdicts rest on the ladder-trained b-lad and are unaffected.
6. **Minor: R4 vs R3 is not a pure identity contrast** (b-lad 0.70; R4 has 74 rows).
7. **Minor: the GD1 X vs REC floor is set by png_bytes of the 256 px file.** Without it the floor is 0.689; verdicts unchanged.
8. **Checked, correct.** The joint operating point is 2 of 5 for Sb under both cut-offs. max(τ5, 0) equals the own rule for Sb. H-new-3 is falsified.

## Consequences
- **Paper wording:** GAN and diffusion benchmark scores may reflect re-synthesis detection. Never write "detects GAN/diffusion morphs".
- **F10:** these reads give no evidence for the operating-point change. If the author rules, it must rest on other grounds.
