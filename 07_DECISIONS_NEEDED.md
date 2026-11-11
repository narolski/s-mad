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

## Still open

1. **Codex transcript "Eksperymenty z S-MAD"** from the author's Mac, to be read before the start.
2. **Start signal** after that.
