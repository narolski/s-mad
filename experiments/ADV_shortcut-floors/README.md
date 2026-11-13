# Shortcut floors of the standing adversary (ADV): full record

Owner: standing adversary (ADVERSARY role, OWNER_BRIEF.md item 3). Registration: `prereg.md`. Code: `src/adversary/`.
Large outputs: `/mnt/t7/smad_next/ADV/` (feature caches `feats/<set>.npz`). Small outputs: `floors/` (one JSON and one
held-out score CSV per contrast), `FLOORS.md` (one line per contrast, attack sets).

## Timeline (machine clock, `date`)

- 18:55-19:10 Read OWNER_BRIEF, evening conclusions, SA1 (lines 1-156), the hand-made statistics code, the queued
  arms' registrations (AB1 fm and x, GX1, RZ1, BB2 plan and amendments 4-5, SE1 README). No arm result opened.
- 19:00-19:10 Wrote `src/adversary/` (feats, floor, contrasts, run_floors, check). Smoke: 8 landmark_combined frames,
  F27 identical to the cached `PN1/cues/a14_lcomb.npz` (max abs difference 0.0), 0.30 s per frame; synthetic-data
  test of the fitting and of `check.exceeds` (random features; informative column found; rule passes a strong and fails
  a floor-level score).
- About 19:12 Registration committed (see git log for `experiments/ADV_shortcut-floors/prereg.md`).

- 19:12-19:20 Owner-launched pre-run check (GO WITH FIXES) -> amendment 1 (032e8ae). Lead's message: RI1/TB1 rows.
- 19:26 Lead-ordered pre-run check (GO WITH FIXES, 112d50c) -> amendment 2 (eef59b3); go for stage 1a.
- 19:12-20:00 Features of the 19,208 evaluation frames (`/mnt/t7/smad_next/ADV/feats/ab1x.npz`), 2 worker processes.
- 19:56-20:05 Stage 1a floors (lcomb and the four test-ladder contrasts); regression gate passed (0.8856).
- **Stage 1a commit: bffacb5** (20:05; posted to the
  lead in the report; the lead holds SbFM, Sbx and RZ1 reads until it is posted).

- 20:06-20:30 Stage 1b evaluation rows; post-result review of stage 1a (6f7c181) -> amendment 3 (104ee36, post hoc):
  region floors, lcomb_bal (two builds before the rule was committed; disclosed), lcomb_ipw registered then computed
  (not usable, ESS 8 morphs, 35f25a7). Dead end: build 1 of lcomb_bal (logreg surround score) did not converge.
- 20:26-20:35 Stage 3 S4-vs-S3 and RI1 floors (35f25a7). A chained job waited forever on its own pgrep match and
  was killed; the same-data learner was then run directly.
- 20:42 Amendment 4 (1067700): naming, H-new-1 / H-new-3 registered; reads and transfer_Sb at 28cb468; all 15 arms
  at 735a65e. 20:56 amendment 5 (61c6466); products at bf96003. Stage 1c/2 floors at 9e496bb.
- The GD feature job failed once on 256-px DiffAE frames; fixed by the loader view (amendment 3 item 9) and resumed.

## Commands

See `prereg.md` section 10.

## Handover state

Stages 0-9 committed and pinned (see `floors/pins_stage*.sha256` and FLOORS.md). Pending: GD0 floors (StyleGAN /
DiffAE FFHQ-Morphs) once `/mnt/t7/smad_next/ADV/feats/gd0.npz` is complete; GX1's own rows when its frames and
`gx1_eval.csv` are committed; region floors for the GD rows (region features computed for evaluation rows only).
Large outputs: `/mnt/t7/smad_next/ADV/feats/` (ab1x, train, gd12, gd0, missing, pngmeta),
`/mnt/t7/smad_next/ADV/feats_regional/` (lcomb, ab1x), logs in `/mnt/t7/smad_next/ADV/logs/`.

## Correction (13 Nov, about 21:20)

Network values quoted in FLOORS.md now carry their seeds: landmark_combined 0.873-0.906 is the recipe at seeds 408-412;
the frozen candidate (403-407) is 0.814-0.885, mean 0.860; frozen S4 vs S3 0.716-0.744, R4 vs R3 0.80-0.85. The
lcomb_smatch note adds that the selection rule draft v3's 0.504 is the boosted-tree surround balance; the linear refit
reaches 0.662. Amendment 5's header now carries its git time (20:56:34). State: standby; remaining work is GX1's
floors when its frames and gx1_eval.csv exist, and floors for any newly registered arm.
