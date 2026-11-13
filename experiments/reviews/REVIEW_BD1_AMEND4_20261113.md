Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only, at db07b4b. Saved by the owner; condensed.

# BD1 amendment 4 (descriptive cos_HS-quintile read): accept with corrections

All numbers were recomputed and match: edges 0.8344 and 0.9025, 59/59 hosts, database counts, medians, and the FS1 flag rates and AUCs. The read follows its registration.

## Findings
- **F2 (major).** "Most of the colorFERET hosts" is false. The bottom quintile holds 22 of 56.
- **F3.** The flag ratio is 2.2-3.4 per seed, not "about 2.5".
- **F4.** "Ranked close" is too strong. It is 0.58-0.64, still above chance.
- **F5.** Seeds share hosts and are not independent replications.
- **F6.** The confound does not make the read uninformative.
  - The gap appears within each database: FRGC 0.49-0.70 against 0.17-0.28, colorFERET 0.68-0.82 against 0.17.
  - It cannot be attributed to cos_HS rather than to D.
- **Minor.** The reader loads all of pool.csv. It only looks up manifest hosts, so no FRLL row is used.
