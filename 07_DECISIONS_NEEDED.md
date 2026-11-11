# Decisions needed from the author

Each has a default that the plan assumes if nothing else is said.

1. **Data scope.** May FRGC, colorFERET and Multi-PIE photos be used to make morphs and self-morphs for
   training and testing? Default: yes for internal use; the paper releases pair lists and code, not
   images.
2. **Start.** Approve launching the plan (this lifts "plan only, no compute"). Default: nothing runs.
3. **Shared post-processing.** Keep pairs as lossless PNG at generator resolution, or apply one shared
   chain through the already approved `a37_restore` path? Default: lossless PNG; no new resampling or
   compression code.
4. **Budget.** Raise the Vast ceiling to 250 USD and allow 8 concurrent WCSS jobs. Default: stay at
   100 USD and 4 jobs, which stretches generation to two days.
5. **The other loop.** Pause it, or keep it on the WCSS jobs it already queued (MAD22, A138) and leave
   the DGX and Vast to this plan? Default: it keeps its queued WCSS jobs and starts nothing new.
6. **Claim wording.** Accept the narrowed thesis from `01_EVIDENCE_DOSSIER.md` (diffusion shown, GAN
   absence, landmark open until the twin test)? Default: yes.
7. **MADMamba.** One arm in T4 under identical data; kept in the paper only if it wins. Default: yes.
8. **Sealed sets.** FST, A12SP and `valx.csv` stay closed; TwinSet's held-out pipelines are the new
   test. Default: yes.
9. **Research repository.** Add the morph-specific literature note to `narolski/research` and push?
   Default: prepared locally, not pushed.
