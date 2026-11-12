# DRAFT — DG1 amendment: orthogonalised same-person and correlated two-person rungs (SAME_orth, X_corr)

Status: **draft, not registered, not run.** Written 12 Nov 2026 by the frozen-features owner (FZ2) at the lead's
request; it goes through the pre-run review, then the DG1 owner / lead registers it in `prereg.md` before any code runs.
Purpose: the causal test of the review's hypothesis H-A (`experiments/reviews/REVIEW_FZ2_AR1A10_20261112.md`):
**when the two inverted noise maps are correlated (same person), the A43 slerp amplifies their shared fine structure and
gives over-sharp renders; the frozen two-person-vs-same-person direction P_XS reads this, not a second identity.**
FZ2 facts behind it (post hoc): θ (angle between the two noise maps) alone separates X from SAME at 0.916 (SAME median
1.537 rad, X 1.564); face-box sharpness medians REC 87, X 96, SAME 128; along P_XS two-person mixes and doses sit with
reconstructions. FZ2 amendment 1 (commit dbc151d) adds the zero-GPU transfer part.

## Rungs (set B, all 536 hosts, 20 steps, unchanged generator and renderer)

Notation per host h: a = x_T(H_h), b = x_T(S_h) (same person, other session), p = x_T(S_partner(h)), flattened noise maps
(3 × 256 × 256); z(·) semantic codes; `interp`, `render`, `encode`, `encode_stochastic(T=250)` exactly as in
`src/DG1/dg1_addon.py` (A43 path, fp16 autocast, batch 16, `save_image`). cos(u, v) = u·v / (‖u‖‖v‖), in float64.

| Rung | Image | n |
|---|---|---|
| REC | render(a, z(H)) — in-process control | 536 |
| SAME | render(slerp(a, b, ½), lerp(z(H), z(S), ½)) — in-process control (A43 interp unchanged) | 536 |
| X | render(slerp(a, p, ½), lerp(z(H), z(S_partner), ½)) — in-process control | 536 |
| **SAME_orth** | b⊥ = b − (a·b / a·a)·a; b′ = b⊥ · ‖b‖ / ‖b⊥‖ (so b′ ⟂ a, ‖b′‖ = ‖b‖); x = the A43 slerp of (a, b′) at ½ (θ′ = π/2; checked \|cos(a, b′)\| < 1e-6); z = lerp(z(H), z(S), ½) unchanged | 536 |
| **X_corr** | θ_s = arccos(cos(a, b)) (that host's same-person angle); p⊥ = p − (a·p / a·a)·a; u = p⊥ / ‖p⊥‖; p′ = ‖p‖ · (cos θ_s · a/‖a‖ + sin θ_s · u) (so cos(a, p′) = cos θ_s, ‖p′‖ = ‖p‖); x = the A43 slerp of (a, p′) at ½; z = lerp(z(H), z(S_partner), ½) unchanged | 536 |

New images 1,072 (SAME_orth, X_corr); with the in-process controls 2,680 renders at 20 steps. The semantic half is never
touched; only the noise map entering the unchanged slerp is changed, and its norm is kept. Logged per image: θ actually
used, cos(a, b′) or cos(a, p′), ‖x‖. Guards as amendment 2 (finite θ and codes before rendering; tar always written).

## Process, platform, shards

One process per shard, 8 shards cut along partner cycles exactly as the add-on lists (`addon_s0..7` hosts), every rung of
a host in the same process (contrasts never mix processes or platforms). Codes: re-encoded in-process (deterministic,
η = 0; equal to the add-on's saved codes up to platform noise), so each shard is self-contained. Platform: one rented A100
or RTX 3090 through the existing driver path (the generator passed the registered equivalence gate on both); every row
carries `gen_run = rented_DG1_orth` and the platform.

## Readings (fixed here; read by FZ2 with its registered routines: partner-cycle folds, two-way person bootstrap B = 10,000)

P_XS = the FZ2 clip_mad probe X20 vs SAME20 trained on the **add-on** images, applied out of fold (each new image scored by
the model of its partner-cycle fold). L = face-box Laplacian variance (`dg1_validity.py` box).

- **H-A supported** if all of: P_XS on X vs SAME_orth ≤ 0.65 (upper bound ≤ 0.72); L on SAME_orth vs X within
  [0.40, 0.60]; L on SAME vs SAME_orth ≥ 0.70 (orthogonalising removes the extra sharpness).
- **H-A falsified** if P_XS on X vs SAME_orth ≥ 0.85, **or** L on SAME vs SAME_orth within [0.40, 0.60] (SAME_orth stays as
  sharp as SAME).
- Otherwise not decided.
- Secondary (direction of the effect, descriptive with intervals): X_corr — predicted P_XS on X_corr vs SAME ≤ 0.65 and L on
  X_corr vs X ≥ 0.70 (correlating the two-person noise maps makes them sharp and same-like). Also in-process controls vs
  the add-on (pixel and score agreement), the frozen SMDD head s401 and the five DG1 baselines on every new contrast,
  dinov2.

## Cost

Encodes 3 per host (H, S, partner S; about 1,608, partners shared within shards) at about 3.1 s on an A100 ≈ 1.4 GPU-h,
renders 2,680 × about 0.3 s ≈ 0.2 GPU-h: about 1.6 A100-hours (the lead's 0.5 A100-h estimate assumed reuse of the saved
codes; with codes reused from the add-on code tars where they exist, about 0.3 GPU-h). On a rented machine about 1 USD.
Images about 2,680 × 70 kB ≈ 0.2 GB on /mnt/t7.

## Code to be written after the review (not written yet)

- `src/DG1/dg1_addon.py`: two new modes `orth` and `corr` (the formulas above, in float64 on the flattened maps, then the
  unchanged `interp`), plus the log columns. Job lists `src/DG1/dg1_orth_lists.py` → `/mnt/t7/smad_next/DG1/orth_jobs/orth_s0..7.csv`
  (REC, SAME, X, SAME_orth, X_corr per host). An 8-image DGX check of the real command line first (cos(a, b′) ≈ 0 and
  cos(a, p′) = cos θ_s printed).
- `src/DG1/rented/remote_run.sh orth K` (as `shard K`, with the orth pack) and a driver `src/DG1/rented/drive_orth.sh`
  (copy of `drive.sh` steps 1–3 and a loop over orth shards 0–7; results to `/mnt/t7/smad_next/DG1/rented_results/`,
  unpacked to `/mnt/t7/smad_next/DG1/gen/orth_sK/` with `PLATFORM.txt`).

The one command the lead would run on the DGX once a machine is leased (same guard and lease folder convention as the
add-on run):

```
bash /home/narolski/smad-next/src/DG1/rented/drive_orth.sh <HOST> <PORT> /mnt/t7/smad_next/vast/dg1_orth
```
