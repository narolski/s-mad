Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only. Review of the SM1 ViT-L/14 LoRA audit reading (commit aeed4dc; registration A14, b4cb17b). Requested by the SM1 owner on the lead's instruction; saved verbatim by the owner.

**Verdict.** The reading is sound, but the wording needs fixing. I reproduced the AUC independently from the converted npz files and got 0.7555 [0.7463, 0.7649], with per-seed values 0.7554 and 0.7556.

**(1) Registration order: clean.** Timeline:
- A14 was committed as b4cb17b on 12 Nov 11:40:58.
- `a12_rank.py` was committed at 12:03 and 15:33, before any score existed.
- Job 3547052 wrote `scores_audit.npz` at 20:23:59 (s401) and 20:25:17 (s402).
- The files were fetched on 13 Nov at 08:56:25. The converted npz files appeared at 08:56:34, the JSONs at 08:56:34–35, and the result commit aeed4dc at 08:56:53.

Nothing shows the scores were opened before A14 was committed. The "stale pending" note in result.md:658 is consistent with this.

**(2) Rule and computation: as registered.**
- The audit list has 500 keys, each with exactly 5 KP and 5 KE. The AUC is per key over 25 pairs, with ties counted as one half (tie rate 0 and 0.00024).
- Per-key AUCs are averaged over the 2 seeds, then over keys. The bootstrap is 10,000 key draws with seed 20261111 (`sm1_common.SEED`).
- The logit is log(p/(1−p)) of `score_noTTA` (max diff 1e-7), the same convention as A15/A17.
- Result: 0.756 ≥ 0.70 and the gap is 0.045 < 0.2, so H-new-D is supported.

Caveats to state:
- The interval resamples keys only and leaves out seed variance. Per-seed means agree, but the per-key correlation between seeds is only 0.38.
- The 0.70 bar is absolute, and the null is not 0.5. The ViT-B/16 arms without SMDD's five partners give 0.53–0.59 (b′ 0.567, c 0.533, e 0.562, f 0.586). ViT-L/14 has no such baseline arm.
- `a12_rank.py` silently skips a missing seed file. That did not happen here, but it should fail loudly.

**(3) H-new-5: correct in substance, imprecise in wording.**
- The 1-logit bar is not reached (0.045).
- The registered falsification rule is the DiD interval against ViT-L/14 arm c. It cannot be computed because no arm c fit exists, and none will before 22 Dec, which is after the deadline.
- The verdict is therefore "prediction not met; decision rule not computable; untested for the paper". It is not "falsified".
- The stated reason is also loose. A head bounded near ±4 could still separate the two kinds by up to about 8 logits. The real problem is that both kinds sit at the upper bound: median KP 3.92 vs KE 3.91 (s401), and 99.9% of KP are above 3.5.

**(4) Table cell.** Suggested caption wording:
"SMDD partner trace, MADation-recipe ViT-L/14 (LoRA) retrained on SMDD release files: within-key AUC, morphs with SMDD's five training partners over morphs with SMDD evaluation partners (same first contributor, 500 keys), 0.756 [0.746, 0.765], 2 seeds (401: 0.755; 402: 0.756), key bootstrap B = 10,000 (seed variance not included); whole image, no TTA; audit set, not a benchmark."

How to keep it apart from the released detector:
- The released MADation ViT-L/14 number, 0.95 [0.78, 1.12], is a logit gap from one network on the crop path. On the whole-file path, which matches the retrain, that release gives 0.45 [0.37, 0.55] (result.md:215).
- Logit gaps cannot be compared across heads with different saturation. Put the two in separate columns ("retrained, 2 seeds, AUC" vs "released network, logit gap").
- Never place 0.045 beside 0.95.
- Next step: a within-key AUC for the release, computed from the existing release audit scores. It needs zero GPU and a short descriptive registration first. With it, the two could share one metric.

**(5) Text corrections (result.md):**
- :659 — replace "Both fits' logits are bounded (head ‖w‖ about 4.2)" with "Logits lie in [−4.20, +3.97]; KP and KE both sit at the upper bound (median 3.92 vs 3.91)."
- :663–665 — replace with "H-new-5 (registered 11 Nov): prediction not met (trained − KE 0.045 [0.032, 0.061] < 1 logit); the registered decision (DiD against a ViT-L/14 arm c, interval above 0) cannot be computed, since no arm c fit exists before 22 Dec; H-new-5 stays untested for this paper. The 1-logit bar cannot be met when both morph kinds sit at the head ceiling."
- :666 — "the standard ViT-L/14 recipe" → "the MADation-recipe ViT-L/14 LoRA". Append: "(interval over keys only; ViT-B/16 arms without SMDD's five give 0.53–0.59; no ViT-L/14 baseline arm)."
- :661 — add "(2 seeds)" after the interval.

Files: `/home/narolski/smad-next/experiments/SM1_smdd-partner-audit-and-rebuild/result.md`, `prereg.md` (lines 416–420 and 462–471), `a14_rank_vitl.json`, `/home/narolski/smad-next/src/SM1/a12_rank.py`.
