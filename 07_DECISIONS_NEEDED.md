# Decisions

## Made by the author on 11 Nov 2026

| # | Decision |
|---|---|
| 1 | All available data may be used; we hold the licences. Sources include `mambamorph/Datasety`. Only the corrected MAD22 is used. |
| 2 | The plan is hardened first. Nothing is launched until the author approves. |
| 3 | We take over from the other loop when the author approves. |
| 4 | WCSS: use as much as the scheduler allows and submit needed jobs as early as possible. Vast: 20 USD available now, up to 100 USD in total, each lease must show a concrete return. Ablations that do not produce new data go to WCSS. |
| 5 | Prior and future work is organised in `narolski/s-mad`. |
| 6 | A cue table is kept and cues are crossed out one by one (`08_CUE_MATRIX.md`). |
| 7 | A short notebook tracks all ideas (`NOTEBOOK.md`). |
| 8 | Work runs as lead (Fable) → hypothesis owners (Opus) → helpers (Sonnet, Haiku); the lead reviews every result. No waiting for approval except for large spending (`WORKFLOW.md`). |

## Assumed unless the author says otherwise

| # | Assumption |
|---|---|
| A | Pairs are stored as lossless PNG at the tool's or generator's output size. No new blur, resampling or compression code. The history control uses the already approved path only. |
| B | The claim wording follows the evidence per family; the three-number test in `11_AUDIT_PLAN.md` decides each cell. |
| C | MADMamba is one arm under identical data and stays in the paper only if it wins. |
| D | FST, A12SP and `valx.csv` stay closed; held-out tools and generators of TwinSet are the new test. |
| E | The paper releases pair lists and code, not images of licensed datasets. |
| F | The other loop's queued WCSS jobs (corrected MAD22 scoring, A138) stay in the queue; their results are used. |

## Made by the author on 11 Nov 2026, afternoon

See "Author rulings of 11 Nov (afternoon)" in `11_AUDIT_PLAN.md`. Also: commit everything to git;
branches and pull requests in `narolski/s-mad`; never let data sit only in volatile storage; push the
morph literature note to `narolski/research`.

## Author's positions of 11 Nov, about 16:00 CET (literature check running)

- **Mirror self-morph and same-person morphs:** if the morphing method is used, it is a morph.
- **One-photo reconstructions (GAN inversion, diffusion encode and decode of a single photo):** this
  is generated-image detection, a different task from morph detection. Lean: do not penalise morph
  detectors on it. The treatment must be consistent for every detector, ours included.
- Both points are to be checked against the literature; if research has no stand, the paper discusses it.
- The stuck LibreOffice process on the DGX may be stopped (done).

## Author's decisions of 11 Nov, late evening

- **SMDD licence:** accepted. Morphs derived from SMDD may be built and used; they will be published and shared with the SMDD authors as its terms require.
- **Softness:** yes, teach detectors that softness is not blending. The existing shrink-and-enlarge path may be run unchanged on training photos, warped halves and our own morphs. No other blur, resize or compression code.
- **Emails to other groups** (SelfMAD checkpoint selection, MADation scoring, SMDD pairing): yes, after the experiments stage. The lead reminds the author then.
- **Rented GPUs:** approved for the morph-free networks experiment (AD4); rental commands are run from the main session; A100-class cards where 40 GB suffices.
- **Codex CLIP fits:** stopped by the author. **CPU-heavy builds:** WCSS CPU nodes.
- **Author's idea under test:** learn the signal from morphs of the same input image and of the same person (experiment "Signal isolation by paired differences", PD1).

## Author's decision of 11 Nov, night: PLGrid grant

- The S-MAD work is within the scope of the overall grant behind `plgrestorearc` (Cyfronet rule 3 on the research agenda is satisfied, on the author's word). The work moves to a more specific grant once that is approved.
- The grant is on **Athena** (author, 11 Nov): A100 cards with 40 GB, x86; Slurm account `plgrestorearc-gpu-a100`, partition `plgrid-gpu-a100`, 48-hour limit; the login is the personal account `plgpnarolski` at `athena.cyfronet.pl`. Athena offers key login only (no password), so the key must arrive through the Portal sync. Athena is GPU-only: no CPU-only workloads there.
- Cyfronet rules followed: no computation or compilation on the login node; data under `$SCRATCH`; no `/tmp`; large transfers through a compute-node allocation.

## Author's decisions of 11 Nov, 19:13

- **JPEG in training: yes.** The JPEG branch of the existing registered function (`degrade` in
  `smadcvpr/prep_eval.py`, operations `jpeg90`, `jpeg70`, `jpeg50`) may be run unchanged on training images. The
  function is imported and called, never copied or edited. Not covered by this answer, so not used until the
  author confirms: the branches `blur1`, `resample50` and `chip` of the same function.
- **Class categories: accepted on a condition.** "Will it impact the performance of the networks? If yes, we need
  to use two classes only (bona fide / morph). If not, go with your proposal." The lead's answer: it does not. The
  network stays a two-class network with one score (morph or not a morph); single-subject images (warp-only,
  warped halves, stored copies, same-person and mirror blends, one-photo reconstructions) are never a third
  output. The three categories only arrange the tables: single-subject images are reported in their own table and
  are counted neither in the bona fide error rate nor in the attack error rate. Numbers on the published
  benchmarks are computed exactly as before, because those contain only bona fide photos and two-person morphs.
  What can change performance is the training protocol itself (constructed images as negatives); that is a
  two-label choice, it is the method under test, and its cost or gain on the benchmarks is measured by the SMDD
  rebuild (SM1) and the protocol-network tests (PN1). So the proposal of `14_CLASS_DEFINITIONS.md` is in force.

## Author's decisions of 11 Nov, 19:42

- **Oracle row for SelfMAD: ok.** One clearly labelled row may pick SelfMAD's best saved epoch on the FRLL test
  data, beside the last-epoch row, to measure what the public code's default selection on test data is worth. A
  diagnostic about their method only; never a headline and never used for our networks.
- **Crop storage in the own-crop re-score (RS1): ok** (the lead's settlement stands: primary rows through the
  authors' crop script run unchanged, secondary rows through the corrected crop stored losslessly; crops re-saved
  as JPEG by sprint code are not result rows).
- Still not covered by any answer, so not used: the `blur1`, `resample50` and `chip` branches of the registered
  function on training images.

## Still open

1. (Closed 11 Nov: class definitions accepted on a condition, see above.) Open instead: may the `blur1`, `resample50` and `chip` branches of the registered function also be run on training images?
2. **PLGrid access:** Athena works (author activated the access service; jobs are charged to `plgmultivision-gpu-a100` until `plgrestorearc` appears on Athena, by the author's decision). The Helios and WCSS login nodes still refuse connections from our address since about 16:55 on 11 Nov.
3. **Half-exchange images** for the smiling-half follow-up (a rectangular pixel copy): permitted image code or not.

## To do when the experiments stage ends

- Remind the author to email: the SelfMAD authors (which checkpoint-selection setting produced the release), the MADation authors (preprocessing used for the published numbers; release epoch), the SMDD authors (was five partners per split intended; sharing of derived morphs).
