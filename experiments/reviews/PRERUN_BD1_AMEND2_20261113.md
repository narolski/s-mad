Reviewer: experiment-reviewer (Opus), 13 Nov 2026, read-only, at 7697fbf. Saved by the owner; condensed.

# Pre-run review of BD1 amendment 2: GO WITH FIXES

Pins, manifest rows, environment, the blanked-row definitions (`_bg` keeps the inside, `_face` keeps the outside) and the look-alike count (2 pairs > 0.6, 4 > 0.4, max 0.686) are verified.

## Findings
1. **Major.** The gap rule decides on the raw ρ, but its stated meaning claims "beyond FR similarity". Via cos_HS alone a raw value of about +0.11 is expected. Fix: decide on the partial ρ given cos_HS, D and D_dc.
2. **Major.** colorFERET n = 56 (SE about 0.135), so "both databases" makes both verdicts hard to reach. Fix: a database-stratified primary with per-database CIs; colorFERET descriptive.
3. **Major.** Part 3 is not fresh: development-host blanked flag rates are published in AB1 review_recompute.json, and the blanked AUCs are quoted in BD1 result.md. Fix: disclose, and relabel part 3 post hoc.
4. **Major.** The face-blanked rows are about 1% flagged in both classes, so the outside read is likely non-diagnostic. Fix: add a non-collapse condition and reword the meaning.
5. **Moderate.** H1 mixes databases. Fix: add a database covariate and a CI; reword "falsified" as "not replicated at n = 100".
6. **Moderate.** The implications are incomplete and conflate the reads. Fix: a table of outcome combinations.
7. **Minor.** H4 rests on one fold split. Fix: average over 20 splits. Also disclose the known development AUCs.
8. **Minor.** Code: add a missing-row assert, positivity asserts and the timestamp corrections. The same-person range is 0.77-0.93.
