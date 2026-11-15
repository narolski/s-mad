# Readiness of GAN morphs with matched one-person renders

14 November 2026, Codex handoff. **Generation completed; image admission and training are not ready.** This check used generation plans, CSV logs, archive sidecars, source code and scheduler receipts only. No production PNG, latent, identity embedding, candidate archive, candidate score or benchmark output was opened. No image operation or model fit was run.

## Verified generation record

Scheduler receipt `/mnt/t7/smad_next/coordination_20261114/GX_GENERATION_AND_JOB_STATE.json` was captured at 10:37:02 CET. All twelve MIPGAN-I tasks of 6315654 and all eight MIPGAN-II tasks of 6315655 completed with exit 0. The registered generation smoke 6315653 also completed with its recorded success marker. The lead fetched logs and sidecars into `coordination_20261114/GX1_generation_metadata/`; generation archives remain on WCSS.

`GENERATION_METADATA_20261114.json`, produced by `src/GX1/gx1_generation_metadata.py`, verifies that every production log exactly matches its original shard plan's stems, contributors, generator, rung and alpha. Both generators have the same 1,446 logged rows:

| Split | Two-person R4 | Same-person R3 | One-photo R2 |
|---|---:|---:|---:|
| Training | 404 | 202 | 404 |
| Development | 109 | 109 | 218 |

No logged loss is non-finite and no logged PNG hash is malformed. These are metadata checks, **not image or identity admission**. All 2,892 production rows still require archive and image validation. The six smoke rows never enter training or evaluation.

Summed allocated H100 time was 8.989 hours for MIPGAN-I and 7.241 hours for MIPGAN-II. The original pinned shard plans estimated 16.717 and 6.55 hours, respectively; older prose estimates of 6.7 and 3.7 hours were optimistic. Generation is now complete, so none of that is an additional requested budget. MIPGAN-II remains descriptive and optional under the registration; its rows never enter training.

## Admission interpretation fixed before image access

The registration's identity gates apply separately by generator and by the literal existing shard/selection **group** field, `train` or `dev`. Database and gender strata are diagnostic; no new split-by-database or gender binding gate is added. The lead approved that operational interpretation in this Codex conversation before any image, latent or identity value was accessed.

Use the unchanged AG1 camera/oracle route and glintr100 impostor threshold at FMR 1e-3 within the same group. Only the registered identity bars bind: R4 verifies both contributors in at least 70%; R3 verifies its person in at least 90%. Do not add AG1's separate oracle-AUC ≥ 0.90 gate. Alignment must reach the registered 95% per rung; rows with alignment flag 0 are dropped and listed. Matched positive/render pairs are dropped together. This interpretation must receive the independent pre-run check before image processing.

## Draft implementation and remaining sequence

`src/GX1/gx1_admission.py` is **DRAFT, NOT APPROVED, NOT RUN**. It proposes archive/PNG/latent checks, unchanged AG1 alignment/oracle helpers, group admission and balanced training-manifest creation. Only parsing and a synthetic-vector boundary test were executed: exact 70%/90% identity boundaries pass, while below-bar R4 rows are excluded. No real image/model or oracle was loaded. The draft is reviewable code, not evidence that all admission edge cases have been resolved. It never calls AG1's benchmark-touching `stage_frames`.

Before any GX fit:

1. Independently review and commit the exact admission procedure and group interpretation. Check available durable storage against the standing 50 GB floor. The lead must obtain fresh remote archive SHA256 agreement before collecting/using generation archives.
2. Validate every mandatory MIPGAN-I archive against its sidecar and plan; validate each logged PNG's actual bytes, 1024×1024 RGB format and allowed chunks, finite loss and latent values, H100/torch provenance, plus the registered inversion-boundary reproducibility check. Process optional MIPGAN-II separately and preserve all failures.
3. Run the unchanged approved alignment/oracle route; apply the fixed alignment and identity gates, list dropped images/groups, and retain original and processed hashes. Commit `pins_images.sha256` before fitting.
4. Finalize `train_GX.csv` and `train_GXp.csv` from the byte-identical 8,386-row Sb prefix. At full admission, the target is 9,194 rows for GX and 8,790 for GXp. GX adds 404 positive R4 rows and exactly 404 paired negatives (cover 0: host R2 on s1; cover 1: host R3). GXp adds the same R4 rows only. Record actual admitted counts and composition; no unregistered rebalancing. New rows must remain `source=smdd`, `val=0`, `mixed=0`, `hist=native`.
5. Build the development `gx1_eval.csv` with original GD manifest rows unchanged, no closed benchmarks. Compute and commit the registered pre-fit simple-cue floor on training/development R3/R4. Add the same-data GX transfer learner and its per-row NEXT floor pins before applicable result access; another training list cannot substitute.
6. Finish and pin the AB1-derived GX runner, overlay and sbatch in amendment 2, with independent pre-run review. These training artifacts are not implemented or admitted by the current handoff. Include all required TT1, MEDS and border inputs through a registered gated path if GX is to qualify under NEXT.
7. Run the complete training-path smoke, then ten fixed fits (GX/GXp, seeds 408–412, last checkpoints) on WCSS H100, with same-row Sb rescoring and no change to the recipe. Preserve missing/non-finite failures. The GX registration requires all five seeds per arm for a verdict; partial batches remain partial.
8. Keep contrast results closed until the complete selection reader's admission succeeds. The fixed NEXT priority, guards, fresh-seed confirmation and benchmark seals remain unchanged.

## Delivery feasibility and budget

The counts needed for the planned training arms have been generated, so no new generation method or author decision is needed to proceed through the existing gates. The deadline is 15 November 2026 at 18:00 CET for required fit/rescoring archives to land and be hash-verified. Feasibility remains conditional on image admission, finishing/reviewing the missing training implementation, and actual queue starts.

Allow a conservative **10–15 H100-hours for ten fits including their added scoring**, plus **1–2 H100-hours for comparator/supplementary scoring** and a short training smoke. These are planning ranges, not measured GX runtimes or a resource cap. Admission and cue-floor CPU/oracle time are not yet measured and must be added from the reviewed real-command smoke. Parallel fits can fit within the remaining calendar window if admitted promptly; a scheduler forecast is not a guarantee. Preserve reader/pin completion as the immediate priority, and do not delay already-ready arms waiting for GX.

## Claims and provenance

- `GENERATION_METADATA_20261114.json` records every audited source-plan/log/sidecar hash and all twenty job states.
- Metadata-audit source SHA256: `a90ae05c69aecaf1f89db134d9aca8026c2eeef17dcbe5dace30f3671c1e7ae0`.
- Metadata-audit report SHA256: `bf7b86f09e7aded29a7739cf11e63b2bcc893d75ad8a989d362d990af80f0748`.
- Draft admission source SHA256: `87dc553042d27f3d64c2633b3196802c61e59c9b7dff2ead6e9fe902a012646e`.
- No image-admission pass, admitted training manifest, training smoke, fit, result read or cluster action is claimed by this handoff.
