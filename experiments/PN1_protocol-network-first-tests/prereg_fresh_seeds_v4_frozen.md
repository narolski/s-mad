# FROZEN: fresh-seed contrasts v4, development data only (registration FS1)

Frozen at the git commit that adds this file. That commit comes:
- after the author's rulings of 12 Nov 2026 and the lead's designation (`date`: Thu Nov 12 08:11:57 AM CET 2026; prereg.md, "Benchmark ruling and development designation");
- before any FFHQ landmark_combined score or statistic exists, and before any amendment-14 tar or fresh-seed tar exists.

This file replaces `prereg_fresh_seeds_v3_frozen.md` (git e4a4590), whose contrasts read H1 and are suspended.

**Nothing in this file changes.** The budget is fixed: 16 fits, approved by the author. C is not run.

## Data

Development data only. The scoring pack holds no FRLL, MAD22, MorDIFF, DiM, H1, FEI or sealed image or row, so the driver cannot score one.
- Pack: `pn1_pack_fs.tar`, sha256 `96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004`.
- Evaluation manifest: sha256 `f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045`, 19,797 rows:
  - af0 1,339, ladder 6,093 and splice 4,365, all built by us from FRGC / colorFERET;
  - FFHQ, the development comparison set of this sprint, not reported as a benchmark: the HN2 list 5,000 and landmark_combined 3,000.

## Networks counted

- Fresh networks only: A, B and Sb at seeds 403, 404, 405, 406 and 407.
- Seeds 401 and 402 and the replicate A seed 401 are printed beside the fresh seeds and never counted.
- Each seed runs whole on one machine. Results are printed per machine.

## Disclosures

- The margins below were set while knowing the 401/402 H1 gains of Sb (+0.13 / +0.23 over B, +0.06 / +0.09 over A) and the 401/402 face-only ladder reads.
- No landmark_combined score or statistic has been computed or seen by anyone at this commit.
- Sb was killed by its registered amendment-10 rule (read (i)). The author allowed the refit on 12 Nov.
- The 191-host test ladder is our own development data and has been read many times.

## Contrasts

Contrast 1 (primary), FFHQ landmark_combined orig morphs (1,000) against landmark_combined resmatch genuine (2,000; the HN2 persons, re-shrunk).
- A seed meets it if Sb − B ≥ +0.05 AUC and Sb − A ≥ −0.02 AUC.
- Ceiling: a seed with B ≥ 0.95 is untestable for contrast 1.
- Floor: "reads the face splice" is claimed only if, on every read seed, the 2.5% bound of (Sb AUC − floor maximum, re-taken in the same draw) is above 0.
  - The floor is the best of the 27 simple statistics (`cues27.py`), by direction-free AUC on the same 3,000 images.
  - The floor file and its sha256 are committed before any tar is pulled.
- No-effect probabilities, with the per-seed SD of a difference about 0.025:
  - Sb − A ≥ −0.02 on 4 or more of 5 seeds: about 0.72 (it guards against loss only);
  - Sb − B ≥ +0.05 on 4 or more of 5 seeds: below 10⁻⁵.

Contrast 2 (primary), scale-free storage mark on FFHQ.
- The read: the share of the 2,000 FFHQ persons whose logit rises from ffhq_bona orig to landmark_complete resmatch (paired by key).
- An arm passes on a seed if that share is ≤ 0.65.
- Positive control: A must fail (share > 0.65) on all but at most one read seed. Otherwise the mark is "uninformative on these seeds".
- B and Sb are each read against the mark.

Contrast 3 (secondary), ladder face-only.
- Face-only R4 vs R2w on the test ladder (T_S4_bg vs T_S0_bg).
- A seed meets it if Sb − B ≥ +0.05.
- Printed beside it: the face-blanked R2w vs R4 AUC (T_R4_face vs T_R2w_face) per arm, for surround reliance, and the development-ladder versions of both reads.

## Seed counting

n is the number of read seeds for a contrast.

| n | Replicated | Not replicated | Otherwise |
|---|---|---|---|
| 5 | ≥ 4 of 5 | ≤ 1 | inconclusive, no claim |
| 4 | 4 of 4 | ≤ 1 | inconclusive, no claim |
| ≤ 3 | — | — | "not read (too few seeds)" |

- **Read seed.** A seed is read only if A, B and Sb all finished with a finite loss and a verified tar.
- **Lost or failed seeds.**
  - A seed with a lost or non-finite arm is dropped from every contrast and not replaced.
  - A non-finite run is never re-run.
  - An infrastructure failure is re-run once, unchanged, on the same machine type.
  - Ceiling seeds do not count for contrast 1.
- **Ties.** Margins are inclusive at full float precision. AUCs use the rank form with ties counted half.
- **Deadline.** Seeds finished whole by 14 Nov 2026, 23:59 CET are read. The lead may set another time only before any fresh result exists. Unfinished seeds are not read.
- **Intervals.** 2,000 bootstraps, `default_rng(20261118)`, per seed:
  - images within class, for landmark_combined;
  - FFHQ persons, for the paired share;
  - test partner cycles, for the ladder.
- **Printed only:**
  - own-rule flags on the development genuine pools: development ladder R0 and its stored copies, AF0 validation photos, and FFHQ genuine;
  - HN9 ("platform plus nondeterminism"): the replicate A seed 401 against pn1a's A seed 401, with FFHQ own-rule genuine flags outside 22.5 ± 3% read as platform plus nondeterminism.

## Outcome to claim

None of these is a benchmark claim; benchmark numbers come only from the sealed final read.

| Outcome | Claim |
|---|---|
| Contrast 1 replicated, floor exceeded | "Spliced positives raise detection of face-spliced morphs over protocol-only training on a development set with an unseen splice engine (FFHQ landmark_combined), 5 seeds" |
| Contrast 1 replicated, floor not exceeded | "Higher AUC than B, but not shown beyond simple statistics" |
| Contrast 1 not replicated, contrast 3 replicated | "Engine-specific: the gain holds on our OpenCV ladder splices only" |
| Contrast 1 and contrast 3 not replicated | "The Sb lead was selection or seed noise" |
| Contrast 2: B and Sb pass, A fails | "The protocol removes the storage reaction on an unseen development source, 5 seeds" |
| Any middle outcome | "inconclusive, no claim" |
