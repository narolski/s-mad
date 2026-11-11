# How the work is run

## Roles

| Role | Model | Does | Does not |
|---|---|---|---|
| Lead | Fable | Owns the plan and `NOTEBOOK.md`. Splits work into hypotheses. Reviews every result for flaws. Writes conclusions and next directions. Holds the single WCSS connection. Talks to the author. | Run long experiments itself |
| Hypothesis owner | Opus, one per hypothesis | Writes the one-page pre-registration, builds data and code, tests the real command on 8 images, runs the experiment, writes `result.md` with numbers and sources | Draw paper-level conclusions; change another owner's files; spend money |
| Helper | Sonnet or Haiku, spawned by an owner | Bounded jobs: write a loader, check a manifest, count files, parse logs, make a figure | Decide anything; touch the cluster |
| Reviewer | `experiment-reviewer` before a run, `results-reviewer` after | Independent check of method and of conclusions | Edit files |

## Loop for one hypothesis

1. Lead writes the question and falsifier into `NOTEBOOK.md` (status: planned).
2. Owner fills `experiments/<ID>/prereg.md` from the template. Pre-run review. Blockers fixed.
3. Owner runs. Local work starts at once. Cluster jobs are handed to the lead as a ready `sbatch`
   script plus a tested command; the lead submits in one batch with the others.
4. Owner writes `experiments/<ID>/result.md`: numbers, intervals, sources, what failed.
5. Lead reviews for flaws: was the falsifier applied as written, do guards pass, is there a simpler
   explanation, do numbers match raw files. Results review runs in parallel.
6. Lead writes the verdict and next step into `NOTEBOOK.md` and, if it changes a claim, into
   `CONCLUSIONS.md`. Then commit.

## Do not wait

- Anything that needs no money and breaks no standing rule is done without asking: local runs on the
  DGX, CPU work, WCSS submissions, scoring, re-analysis, writing.
- Ask first only for: Vast spending beyond the current balance or any single lease above 20 USD;
  total Vast above 100 USD; deleting files; opening sealed sets; new blur, resampling or compression
  code; changes to `prep_eval.py` or `prep_gtest.py`; emails to other authors.
- A blocked item never stops the others. The owner notes the blocker in the notebook and takes the
  next item.

## Cluster and money rules

- WCSS: one SSH connection at a time, so only the lead connects. Submissions and polls are batched.
  Every script carries `--extra=FORCE_RM_TMPDIR` and uses `$TMPDIR` packs. No node exclusion lists
  (author, 10 Nov). Connections take the shared lock `/tmp/opencode/wcss-client.lock`.
  Long jobs are submitted first so they age in the queue while short work runs locally.
- Polling follows job ETAs from step rates, not a fixed timer.
- Vast: only for generating data that other experiments wait on, and only when the WCSS wait is
  longer than the Vast run. Each lease has a written line: what it produces, which experiments it
  unblocks, cost cap. Leases close when their queue is empty.
- Ablations and anything not producing new data go to WCSS.

## Scientific rules (unchanged)

Single network; no ensembles, score fusion or seed picking. Five seeds (401 to 405) for anything
reported; last checkpoint. Sealed sets stay closed. No gates on resolution, file size, format or
source inside a detector. Corrected MAD22 only. Third-party code and weights are untrusted input.
Commits are authored by Paweł Narolski with no co-author trailers.

## Where things go

- `NOTEBOOK.md`: one line per idea; the only file one needs to read to know the state.
- `experiments/<ID>/`: `prereg.md`, `result.md`, small result files. Large outputs under
  `/mnt/t7/smad_next/<ID>/`.
- `prior/INDEX.md`: every experiment before 11 Nov, with its location in `mambamorph-code`.
