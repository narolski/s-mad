# Pre-run check of the selection rule for the next method version (draft 351a7f2)

Saved by the lead from the independent reviewer's report (experiment-reviewer, Opus), 13 Nov 2026.

**Verdict: GO WITH FIXES.** Sound in form (closed list, development data only, one arm, written before any challenger is read) but not applicable as drafted.

Findings:
1. Most challengers cannot supply the inputs: unseen-source and NIST rows (criterion c) do not exist for SbFM, SE, GX, Sbx; border rows (d) and the kernel cross table (e) are missing for most arms. Fix: one H100 rescoring job (about 1 GPU-hour) with the bit-identity gate for SbFM, GX (and SE if kept), registered by owner amendments before any tar is opened.
2. Sbx and SE are ineligible under their own registrations (Sbx: "cannot become the method", TT1 embargo; SE: A100 block already fails (a) on 4 of 4 seeds, and SE1 section 2 required an author clause first). Drop both to ablation rows. GXp is a control.
3. DINOv3 unpaired bar 0.904 is far laxer than the paired bar: a true +0.02 gain qualifies with probability about 0.7 unpaired, 0.01 paired. Fix: median >= 0.922 (AB1 H100 Sb median 0.892 + 0.03) and Mann-Whitney U <= 4.
4. Criteria (c), (d border), (e) lack counting rules or have zero margin (an arm equal to Sb fails (d) about 80% of the time). Replacement margins: (c) seed-mean difference <= +0.02 and MEDS transfer on 4 of 5; (d) S3 <= +0.05, border <= +0.01 with job-path check; (e) RZ1 resize arms only.
5. Largest gain with a 0.005 tie band is a coin flip. Fix: earliest in list order unless a later qualifier exceeds it by >= 0.015.
6. Seeds: failed or non-finite seed counts as failing every criterion; 3 or fewer read seeds = not read.
7. RZ1 had no committed registration at review time; its comparator must be its own Sb0, never AB1's Sb.
8. Late arms: not read by 15 Nov 18:00 = not challengers; rule applied once.
9. Disclosures: SbMR trains on shrink-and-enlarge (storage not held out); FRLL genuine photos are scored in the frozen candidate's MAD22 read; kernel cross table for non-RZ1 arms would need the author's word (resampling outside RZ1).
10. Binding needs the author's written yes to the text.

Questions for the author: approve the text and record it in FINAL; has anyone seen a MAD22 number of the frozen candidate (no, as of this entry); are sealed sets available as 512 px frames for a 512 or crop arm.
