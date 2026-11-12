# FROZEN: section 3 of the fresh-seed plan v3 (contrasts, margins, seed rules)

Frozen at the git commit that adds this file. That commit comes before any amendment-14 tar exists or is pulled (pre-run
review `PRERUN_PN1_A14_AND_SEEDS_V3_20261112.md`, B2-F2).

**Nothing in this file changes except two things:**
- the budget decision;
- whether arm C is included.

C is printed only and enters no contrast. Every other change needs a new registration, written before any fresh result
exists.

## Networks counted

- Fresh networks only: arms A, B and Sb at seeds 403, 404, 405, 406 and 407.
- Seeds 401 and 402 and the replicate A seed 401 are printed beside the fresh seeds and never counted.
- Each seed runs whole on one machine. Results are printed per machine.

## Contrasts

Contrast 1, H1. Label: "fresh networks, re-read images, contrast set after the 401/402 H1 read".
- A seed meets it if both hold:
  - Sb − B ≥ +0.05 H1 AUC;
  - Sb − A ≥ −0.02 H1 AUC (non-inferiority).
- No-effect probabilities, with the per-seed SD of a difference taken as about 0.025 (0.018 × √2, from the reference-recipe seed SD):
  - Sb − A ≥ −0.02 on 4 or more of 5 seeds has probability about 0.72 under a true difference of 0. This part only guards against loss.
  - Sb − B ≥ +0.05 on 4 or more of 5 seeds has probability below 10⁻⁵ under no Sb − B effect.

Contrast 2, FFHQ landmark_combined orig morphs against landmark_combined resmatch genuine.
- Label: "second read of the images (first read on 401/402 under amendment 14); genuine pool = HN2 persons, re-shrunk".
- If amendment 14 is registered reduced (14R), the label is "first read of the images" instead.
- If the author reserves landmark_combined as an endpoint, contrast 2 is not read at all.
- A seed meets it if Sb − B ≥ +0.05 AUC and Sb − A ≥ −0.02 AUC.
- Ceiling: a seed with B ≥ 0.95 on this read is untestable for contrast 2.

Contrast 3, scale-free storage mark on FFHQ.
- The read: the share of the 2,000 FFHQ persons (amendment-13 list, paired by key) whose logit rises from native (ffhq_bona orig) to history-matched (landmark_complete resmatch).
- An arm passes on a seed if that share is ≤ 0.65.
- Positive control: A must fail (share > 0.65) on all but at most one read seed. Otherwise the mark is "uninformative on these seeds" and no arm passes it.
- B and Sb are each read against the mark.

## Seed counting

n is the number of read seeds for a contrast.

| n | Replicated | Not replicated | Otherwise |
|---|---|---|---|
| 5 | ≥ 4 of 5 | ≤ 1 | inconclusive, no claim |
| 4 | 4 of 4 | ≤ 1 | inconclusive, no claim |
| ≤ 3 | — | — | "not read (too few seeds)" |

- **Read seed.** A seed is read only if A, B and Sb all finished with a finite loss and a verified tar.
- **Lost or failed seeds.**
  - A seed with a lost or non-finite arm is dropped from every contrast. It is not replaced.
  - A non-finite run is never re-run.
  - An infrastructure failure is re-run once, unchanged, on the same machine type.
  - A seed that is untestable for contrast 2 (ceiling) does not count for contrast 2.
- **Ties.** Margins are inclusive (≥, ≤) at full float precision. AUCs use the rank form with ties counted half. There is no rounding.
- **When C is decided.** At the author's budget answer, before any fresh fit starts. It is recorded in the registration commit.
- **Deadline.** Seeds finished whole by the end of the experiments stage are read with the rules above. The end is 14 Nov 2026, 23:59 CET, unless the lead sets another time before any fresh result exists. Unfinished seeds are not read, and no extension is decided after a result is seen.
- **Intervals.** 2,000 bootstraps, `default_rng(20261118)`, printed per seed:
  - H1: resampling H1 hosts;
  - landmark_combined: resampling images within class;
  - paired share: resampling FFHQ persons.

## Outcome to claim

| Outcome | Claim |
|---|---|
| Contrast 1 and contrast 2 replicated, and Sb's landmark_combined AUC above the amendment-14 floor (bootstrap lower bound, floor maximum re-taken per draw) on every read seed | "Spliced positives raise face-splice detection over protocol-only training, across seeds and on a second engine" |
| Contrast 1 replicated, contrast 2 not replicated or not read | "Engine-specific: the gain holds on the Poisson H1 splices only" |
| Contrast 1 not replicated and contrast 2 not replicated | "The Sb lead was selection or seed noise" |
| Contrast 3: B and Sb pass, A fails (positive control met) | "The protocol removes the storage reaction on an unseen source, 5 seeds" |
| Any middle outcome | "inconclusive, no claim" |
