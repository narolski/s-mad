# MONITOR WCSS 2026-11-17T0140Z (02:40 CET) — H1 B + H3 X grids COMPLETE, H2 L running

## Tars in /lustre/.../AD6/results (10/15)
- **H1 B: 5/5 DONE** — `madation_B_v3sbr_s40{1..5}.tar` + sha256 receipts (e.g. s401 `d1cd679f...eb957f27`).
- **H3 X: 5/5 DONE** — `mixfacenet_X_sbr_s40{1..5}.tar` + sha256 (s401 `1c5483ad...a030207f`).
- Final log lines: X_s401 `Train Loss 0.0067 Acc 0.9976` (matches GB10 twin quality); B seeds Loss ~0.013–0.019
  at step 6250.

## Gridevidence (all v3 stack torch 2.1.2+cu121, recipe unchanged, seeds 401-405)
- 6340883 (B, 4xH100, nice 40): submitted 18:32Z; s401 started ~00:00Z r18-14, ~1.0 h/seed at 480–536 samples/s;
  grid spilled across r18-x / r10-15; last seed tar ~01:33Z.
- 6340884 (X, 1xH100, nice 41, TL 8:00): started 20:41Z, 5/5 parallel (r10-14, r14-8, r10-10, r10-3),
  2.32 s/it constant, ~4.0 h/seed, last tar ~01:3xZ.
- 6340885 (L, 4xH100, nice 42, TL 6:00): 4/5 RUNNING since ~01:19Z (401 r18-14 @ Step 1050/6250, 372 samples/s
  ≈ 1.2 h/seed; 402 r18-5, 403 r18-9, 404 r18-4), 405 PENDING (Resources). ETA: 401-404 tars ~02:30-02:40Z;
  405 after (~1.5 h more). Guard skips any already-done seed; fail-safe rerun if a task TLs.
- Epoch-1 checkpoint + tar + sha256 pipeline validated end-to-end on v3 (B_s401 first at ~01:00Z).

## HOLDS
- H1 DONE 5/5, H3 DONE 5/5 (updated in HOLDS_20261116.md), H2 RUNNING 4/5.
- Next: scoring handoff to main when L tars land (pipeline on /home, commit f987c31); B/X results are already
  scoreable — per gate, scoring allowed after smoke PASS + full receipts (both conditions met for B/X).

## Polling loop c761556c
Now reduced value: only H2 L s405 remains pending + L tars; loop stays until L complete, then cancel and hand
off. No errors, no drift, no operator escalation needed.
