# Results review: H-new-1 to H-new-4 (post-read, MAD22-informed, descriptive), 13 Nov 2026

Reviewer: results-reviewer (Opus), read-only. Saved by the FINAL owner; corrections applied in
`experiments/FINAL_sealed-benchmark-read/result.md`.

**Verdict.** The numbers are right, and each verdict follows from its registered rule. The reviewer recomputed
H-new-1, H-new-2 and H-new-4 from the result tar (c5205a58…), the pack manifest (48335f86…) and the development JSONs.
The write-up needed qualification before any sentence is used.

**Findings.**
1. **Major: H-new-1 "supported" is fragile and partly circular.**
   - OpenCV reaches 4 of 5 only through s403 at exactly 2.0 (4 vs 2 photos) and s407 counted as inf (2 vs 0). With inf
     read as undefined, the verdict would be "inconclusive".
   - By subject, OpenCV is 6 vs 3 (p = 0.51) and Webmorph 31 vs 5 (p = 1.3e-5).
   - The hypothesis was formed from these same scores.
   - At the own rule, Webmorph errors are mainly missed morphs.
2. **Moderate:** "drives" is causal wording. Use "flagged more often".
3. **Moderate: H-new-2 shares above 1 need an explanation.**
   - Equalising the morphs lowers the EER on all 5 seeds (0.50→0.30, 1.47→1.20, 2.80→2.45, 3.92→2.94, 2.90→2.00).
   - Equalising only the genuine photos raises it on all 5 seeds (+6.4, +7.6, +1.1, +1.7, +3.1 points).
   - The effects do not add.
   - "Inconclusive" is right under the literal rule, which made support impossible once 2 seeds were not read.
4. **Moderate: H-new-4 "falsified" depends on seeds 401/402.** Over the five frozen seeds ρ = −0.10. Say "no negative
   relation was seen".
5. **Minor:** H-new-3 "not read" is faithful. FRLL .tem files exist only for the 102 neutral originals.
6. **Minor:** commit the script and JSON. "Fixed before computing" cannot be checked from git.
7. **Minor:** two stale lines (the "not run" line, "1-5 photos").

**Sentences that may be written** (label "MAD22-informed, post-read, descriptive; no method choice follows"):
- "On Webmorph, smiling genuine photos (_08) are rejected more often than neutral ones (_03) at the EER-point
  threshold: 4.5-5.75 times on 4 of 5 seeds; 31 against 5 subjects."
- "On OpenCV the same direction appears, on 0-5 photos per cell."
- "On FaceMorpher, scoring only the genuine photos in border-equalised form raises the EER on all five seeds;
  equalising the morphs lowers it."
- "Development landmark_combined AUC did not rank seeds by MAD22 EER (ρ = +0.29, n = 7; −0.10 on the five frozen
  seeds)."

**Sentences that may not be written:**
- expression drives or causes our errors;
- our MAD22 errors are due to smiling photos;
- the border rise is entirely on the genuine side, or any share above 100% read as a percentage;
- development AUC does not predict benchmark performance;
- anything about blend energy;
- any arm, threshold or selection rule motivated by these reads.

The reviewer's scratch recomputation is in the session scratchpad, not in the repo.
