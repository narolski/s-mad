# Count-balanced ablation (Batch C): final independent admission

**GO only for MAIN's first guarded, registered pair-C read using the exact manifest below.** Admission timestamp: **14 November 2026, 11:45:30 UTC / 12:45:30 CET**. No remaining pre-read metadata blocker at this snapshot. This is not a scientific GO, NEXT selection, benchmark release, retry authorization or assertion that native guards have already passed.

Final manifest: `OPENCODE_BATCHC_FINAL_ADMISSION_20261114.json`.

**SHA256: `12745bb6f9150a0d16b637e51b1cb9d05f143a5d9fc426fd2f77e22240dd259d`.**

MAIN remains executor. This reviewer created no claim, opened no candidate archive, ran no production reader, contacted no cluster and made no commit or source edit. Accepted B1/B2 tests and numerical reference preflight were reused. New work was metadata reconciliation, opaque source/input and sidecar hashing, filesystem checks and an interpreter-version probe.

## Evidence verified

- **Committed implementation:** HEAD and binding commit are `7d5e06b7440269de37b338fa7be81940dd9c55a8`. All **49 source/transitive-input hashes** match the accepted receipt now; repository-resident entries match this commit's bytes. Registered launcher and registration files also match the binding commit. Absolute live floor/split dependencies remain explicitly bound, not replaced by an assumed detached-checkout root.
- **All 30 archive sources:** parsed raw remote `sha256sum` output in MAIN's `BATCHC_REMOTE_INTEGRITY.json`, not just its `matches` flags. Every exact remote path/hash agrees with the prepared manifest and MAIN's fresh local opaque receipt. Current local file sizes, sidecar hashes, sidecar advertised hashes and filenames match. Remote command exit 0, empty stderr. This reviewer relied on MAIN's archive hashing and did not reopen archives.
- **Batch C:** retained the independently reconciled historical collection receipt and individual scheduler completions for all 15 tasks of 6316845. All completed exit 0:0; latest end 14 Nov 10:26:14 CET. Verified collection existed by 10:32:47 CET.
- **Original comparators:** parsed fresh raw accounting in `AB1_COMPARATOR_ACCOUNTING.json`: exactly indices 0–39 of 6310270, all COMPLETED, exit 0:0. Mapped the requested 15 comparators using the registered array: index `8*(seed−408)+{Sb:1,B:2,Sp:3}`. Each individual start/end/elapsed/exit is retained in the final manifest. Latest selected-comparator end is **13 Nov 14:00:49 CET**; latest full-array end is **14:19:03 CET**. These raw scheduler times supersede approximate historical narrative ranges, without changing the historical record.
- **Comparator identity at the metadata boundary:** original registration `61f7994` and the saved submission/launcher identify AB1's own H100 array, remote `results/AB1`, not SE1 or FS1. All five Sb archive hashes also match the previously checked committed source pins. Fresh remote/local equality supplies the missing current byte linkage for B/Sp as well as Sb. Actual embedded identity remains guarded on read.
- **Output readiness:** independently checked MAIN's prepared `/mnt/t7/smad_next/AB1/c/read_20261114` exists, is owned by current uid 1000 and writable. Proposed output, stdout, stderr, execution receipt and both canonical claim/completion paths are absent by `lexists`. No dangling-link exception was ignored.
- **Environment:** Python 3.12.3, NumPy 1.26.4, isolated `-I`, optimization disabled; same accepted B2 environment. Resolved interpreter `/usr/bin/python3.12`, SHA256 `c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960`. Full accepted BLAS/build record is hash-bound alongside the fresh metadata probe.

The final JSON binds full hashes and paths for new receipts, prior reviews/preflight, registrations, launchers, source/input inventory, all archives/sidecars, environment and command. All 30 are admitted as present before the applicable cutoff; no late, missing or unfinished archive is inferred from absent evidence.

## Comparator arrival/provenance disposition under the actual rule

The earlier preparation appropriately left exact historical per-file collection times unknown. **They remain unknown.** The new evidence resolves admission without reconstructing them or imposing an extra rule:

1. **AB1 amendment 7, prereg lines 671–673**, registers this separate reader's once-only read when its fits end, latest **15 November 18:00**, with later rows labelled late. **Amendment 7b, lines 692–697**, expands the batch to 15 fits and changes H-c2 to BN−BV. All fits are now complete and exact local/remote archive bytes were verified on 14 November, before this cutoff.
2. **Original section 7, lines 203–207**, names `ab1_read.py --branch R`, the original 40-network read, and its **14 November 12:00 CET** deadline (or earlier when all fits ended). It does not impose that earlier deadline on the later amendment-7 registered Batch-C reuse, nor require a dated historical per-file copy receipt for that reuse. The original fit/read history remains documented; this admission does not retroactively certify its exact collection timestamps.
3. **Section 7, lines 208–212**, requires native provenance checks and two verified copies with the job's own hash. Current remote/local archive hash agreement, current local job-sidecar agreement, registered source/task mapping and individual scheduler completions satisfy the pre-read byte/source/completion conditions. Native identity/fit checks remain mandatory during the guarded read.

Thus current-before-cutoff verification is sufficient for this registered reuse. The preparation's unresolved historical receipt gap is **not an additional admission requirement**. Historical aggregate fetch statements remain supporting history, not invented per-file timestamps. No actual registered deadline or provenance requirement is waived.

## Exact admitted command and outputs

From `/home/narolski/smad-next`:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 TMPDIR=/tmp/opencode nice -n 10 \
  /home/narolski/mambamorph-code/.venv-spark/bin/python -I \
  src/AB1/ab1_pm3_read.py --pair C \
  --c-results /mnt/t7/smad_next/coordination_20261114/archives/AB1C \
  --ab1-results /mnt/t7/smad_next/AB1/results \
  --out /mnt/t7/smad_next/AB1/c/read_20261114/ab1_pm3_read_C.json
```

Exclusive-create logs in the same directory: `stdout.log`, `stderr.log`, `execution.json`. Record UTC start/end, elapsed time, exit status, this final admission JSON hash, exact source/input/archive/environment binding and output hash. Preserve failures and partial output as evidence. Attach the already validated descriptive `OPENCODE_BATCHC_B2_REVIEWER_TRANSFER_20261114.json`; no companion recalculation is needed.

Canonical journal: `/mnt/t7/smad_next/AB1/READ_ONCE_PM3/C.claim.json`; successful completion receipt: `C.complete.json`. **The reader alone claims atomically.** MAIN rechecks that the bound inputs and absence conditions still hold at invocation; changed bytes, an existing claim/output or a changed environment require review, not substitution.

## Native boundary and conclusions handling

This GO authorizes a **first guarded read**, not a claim that embedded TASK/ARM/SEED, ordered unique finite scores, train/eval manifest hashes, H100 provenance, 6,250 steps/limit zero, pack/overlay, n_items and finite training losses are already known. The native wrapper and historical loader check those at the authorized read. Do not separately invoke the native validator as preflight.

Retain every refusal and permanent claim. No automatic deletion or rerun. Preserve per-network dispositions and obtain independent review if native refusals occur; do not silently equate technical refusal with scientific failure. Registered lost/missing/late treatment and the fewer-than-four-readable-seeds “not read” rule stand. The historical infrastructure retry rule does not authorize a reader retry or a non-finite-fit retry.

Statistical rules and scope remain unchanged: H-c1 Sb−SpV, H-c2 BN−BV; primary D-stratified R4/R3, secondary unstratified S4/S3 with the registered agreement/cap conditions; interaction printed only. Context floors are different-row-set context; transfer learners are descriptive, unstratified references. Independent results review precedes any scientific conclusion. No NEXT promotion or sealed benchmark action follows.

CLAIMS:
- commit 7d5e06b7440269de37b338fa7be81940dd9c55a8 reviewed source binding, checked against actual bytes
- file OPENCODE_BATCHC_FINAL_ADMISSION_20261114.json sha256 12745bb6f9150a0d
- number remote/local archive matches = 30 @ OPENCODE_BATCHC_FINAL_ADMISSION_20261114.json:archives
- number original comparator individual completions verified = 15 @ OPENCODE_BATCHC_FINAL_ADMISSION_20261114.json:arrival_disposition.comparator_individual_completion_verified
- number source/transitive input hashes verified = 49 @ OPENCODE_BATCHC_FINAL_ADMISSION_20261114.json:source_and_transitive_inputs
