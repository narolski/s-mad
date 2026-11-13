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

## Commands

See `prereg.md` section 10.

## Handover state

Registration committed; pre-run check requested; features to be computed; no floor computed.
