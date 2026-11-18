# NEXT admission readiness — independent metadata reconciliation

14 November 2026, snapshot at approximately 13:03 CET. Repository HEAD `78490ba` contains the exact independently reviewed native increment. **NOT ADMITTED.** This is preparation for MAIN's admission work, not a selection result, exclusion decision or independent admission GO. Machine-readable evidence/actions: `OPENCODE_ADMISSION_READINESS_20261114.json` beside this file.

## Concrete progress

**SbFM's training-specific transfer artifact is present, committed and already pinned.** It is not an outstanding computation:

- Original: `experiments/ADV_shortcut-floors/floors/transfer_SbFM_rows.csv`, committed `bf96003` on 13 November at 21:01:58 CET.
- Admission copy: `inputs/floors/transfer_SbFM_rows.csv`, packaged at `076a5f9`.
- SHA256: `50de9a543c4d8aaa9c4ccb2e229369c82026d05285717d7832fee55b73817aa5`.
- Training manifest SHA256: `1231204496664287e4513ac4cf004156a5140386987e3b6cc8a83084c242e491`.
- Reviewed package metadata records 4,080 rows: 3,000 landmark, 360 ladder, 720 matched. This audit did not parse scores. Producer `src/adversary/amend5.py:transfer_rows` calls `contrasts.train_rows('SbFM')`; its explicit training-path map and first-occurrence unique-path projection establish the intended training-list route. Wire the existing file into `transfer_files.SbFM` and its exact training-manifest reference. Do not refit it or substitute Sb.

**E3's formal freeze is a real local metadata gap, but the fifteen fits are not missing.** `experiments/BB2_second-backbone/seed_mode_L.json` is absent at its canonical path, and no all-ref git history for that file was found. The existing `seed_mode.json` is five-seed **earlier BB2**, frozen 13 November 15:35:50; its keys are `BB2_*`, not `BB2L_*`. It cannot authenticate E3.

All fifteen E3 archives are listed in the 09:34:59 CET recovery receipt. Their canonical `/mnt/t7/smad_next/BB2/results_L` files exist; all fifteen sizes and `.sha256` sidecars match the receipt. Archive bytes were not rehashed or opened here. MAIN can reconcile fresh opaque integrity/fetch evidence and complete the registered `freeze_mode_L.py` metadata procedure before member access, then commit/review the exact source map. Amendment 6 changes E3's cutoff to **15 November 18:00 CET**; stale comments saying 14 November do not override it. The rule allows freezing when all fits have ended and are fetched/verified, without waiting for the deadline. No new training is indicated to resolve this gap.

Search limits: canonical repository path, its all-ref history, experiment filenames, and durable filename inventory to depth five. No assertion is made that a remote or unindexed session-only freeze cannot exist; MAIN should supply such evidence if available rather than invent a replacement historical freeze.

## Current pin closure

Rehashed every file in the **44-input and 20-support** pin lists; zero hash mismatches. Compared repository-local pinned bytes to HEAD; zero mismatches. Both pin-list hashes exactly match the historical clean-checkout receipt at `8d00996`, `/mnt/t7/smad_next/coordination_20261114/pre_read_receipt.json`:

```text
24725bb96179ab07363abf2c1f0e77cb8720ebb28550dae0cb3e18ad4d9e4259  inputs/pins.sha256
5e8d39f02345b39755ffbcd13def8af26a1be057e15f7499d7d5649784c2b02a  inputs/support/pins.sha256
```

This makes the historical input/support verification byte-current. The shared worktree still has unrelated changes; it is **not** a clean production admission checkout. Native inventory, mode, complete manifests, receipts, producer and admission-review pins must still be assembled and independently verified. No numerical validator or existing code test was rerun.

Additional native manifests were located and hashed, without scores: original AB1 evaluation, FS1 evaluation, train_B, and the full MS1-pack evaluation manifest. Exact paths/hashes are in the JSON. The MS1 manifest has 42,366 rows, including the required 1,480 `ms1ffhq` rows; pin the full manifest and authenticate the W2 pack provenance. Do not confuse it with FS1's 19,797-row fit manifest. Existing common/support pins already identify train_A/train_Sb/train_SbFM, AB1x, TT1 and MEDS; complete the native manifest references rather than rebuilding these inputs.

## All eight arms, in fixed rule order

No final `read`/`not_read`/`ablation` disposition is assigned here. Queue-pending is not deadline failure, and an unsupported schema cannot itself remove a challenger. Each row also needs the common exact admission and exposure review.

| Arm | Established evidence / actual format | Remaining blocker and concrete action |
|---|---|---|
| **SbFM** | Five recovered v2 fits; native AB1FM/AB1 formats; existing SbFM transfer artifact; supplement 6319579 submitted with fixed config and producer receipt. | MAIN collect final supplemental arrival/hash evidence; bind same supplement for candidate/comparator TT1/MEDS/borders, original AB1 Sb and AB1 A roles. Preserve H-fm3 and fit/gate checks for admitted execution. A diagnostic partial is insufficient. |
| **GX** | Twenty completed generation tasks in reviewed metadata; registered admission requirements; draft admission code. No amendment 2 in current prereg (only 1/1b). | Image/identity admission, pinned GX/GXp manifests, pre-fit floor, transfer rows, reviewed training producer/schema/smoke, ten fits and support/comparator route remain unestablished. Complete registered sequence; implement adapter against actual outputs. Do not exclude because adapter is absent. Its stricter full-five-seed rule remains. |
| **SbMR** | Five candidates and Sb0/A0 in recovered wave-1 batch; `rz1_fit`, 9+4 cross table; registered refit retry 6319491. | Collect Sb yardstick rescores and exact-gate/source receipts, then bind role maps. The sole recovered `RZ1R_A_s408` is **not** the required Sb yardstick. Comparator is Sb0, not AB1 Sb. |
| **SbM** | Same completed wave-1 batch and source formats. | Same yardstick/admission closure as SbMR; both kernel criteria remain required. Reuse shared evidence without substituting comparator. |
| **Sb512** | Reviewed smoke and M6 submission 6319490; `rz1_fit`; aligned 512 target frames documented in DATA catalogue §7a. | Candidate/A512 production arrival receipts and Sb refit closure pending. Bind A512 storage control and Sb0 comparator. Frame availability is already answered without touching sealed inputs. |
| **SbMR512** | Included in reviewed 512 submission; current source sets `CROSS=""`. | V3 expressly cannot qualify absent a kernel test registered before read. No such registration was found. Find/complete that permitted prerequisite plus reviewed adapter support, or bind an authoritative nonqualification disposition under the existing rule. Do not call it a cost drop: submission includes it. |
| **Sbc** | Five crop fits recovered; `rz1_fit`; lead's 224-crop go recorded. | Exact author's 224-interior-crop scope ruling not located; MAIN supply existing ruling if elsewhere or resolve that specific interpretation. Common refit closure also pending. No assumed exclusion or cancellation. V3 control is A0, not Ac. |
| **DINOv3 E3** | Fifteen BB2L fit receipt entries and canonical sidecars; `native_fit`; five fixed AB1 comparators; W2 6319264. | Formal E3 freeze, final W2 arrival/hash/producer receipt and native pin closure pending. Four observed candidates are supported; fixed-five comparator availability remains necessary. Preserve adequacy/splice and per-model exact gates for execution. |

### Crop and kernel authority — no inferred ruling

RZ1 §0 quotes the author: **“For native resolution crops, yes, plan experiments on that with input size 512, and see if any particular resize method (or a mix of resizes in training) has an impact on shortcut learning alleviation”.** M7 distinguishes the lead's approved **224** interior crop from the author's still-requested interpretation. The exact v3 approval record explicitly says it does **not separately answer** the crop question. General continuation/takeover is not an affirmative or negative scientific crop ruling. Earlier archive references likewise record the question as open; no later explicit answer was found in this bounded audit.

SbMR512's condition comes directly from v3 §§3/5(e), not an invented global kernel demand. RZ1's current arm table and `run_rz1.sh:54` provide no cross table for it. A future permitted pre-read kernel registration would require corresponding reader/adapter review, since current preflight explicitly refuses this arm. Historical eligibility prose saying “keep it an ablation” is not automatically a valid machine admission disposition: the reader's `ablation` reason is specifically pre-binding scientific exposure. Bind the actual registered prerequisite failure/missing-input evidence; do not relabel a software gap.

## Receipt reconciliation and next actions for MAIN

Latest inspected local scheduler capture is **12:24:55 CET**, not a live query: W2 6319264 RUNNING; 512 6319490, refit 6319491 and supplement 6319579 PENDING. MAIN is obtaining fresh metadata separately. Existing submission receipts prevent duplicate submissions; they are not final archive-arrival receipts or scientific passes.

1. **Immediately recover/index E3 freeze evidence** using the already complete source metadata; bind the exact BB2L sources, not BB2. Preserve real freeze time and provenance, never backdate.
2. **Index the existing SbFM transfer artifact** and its training-list binding; this removes an incorrectly repeated artifact-absence blocker.
3. **Collect outstanding final output receipts** for W2, SbFM supplement, Sb yardstick and 512 fits. Normalize old collection records (`path`, top-level `at`, `sha256`) into reader-required per-network `archive`, `verified_at`, `hash_verified` fields with truthful provenance; add supplement producer hashes and exact source inventory. Existing receipts' copy/hash claims need current opaque integrity reconciliation by MAIN. Do not infer production gate success from exit 0 or smoke.
4. **Resolve actual arm eligibility**, including GX's missing admitted training sequence, Sbc scope evidence and SbMR512's kernel prerequisite. Keep all eight rows; do not close the batch using queue forecasts. Pre-binding exposure review remains required for every read arm.
5. **Assemble final clean committed pin closure and exact independent admission review.** This readiness JSON deliberately uses a different schema and null final dispositions; it cannot be supplied to the production reader. Fresh 413–417 confirmation still needs its registered producers, comparator/control mapping and source pins after selection.

Cutoff remains **15 November 2026 18:00 CET** for required archives landed and hash-verified. No post-result rule change, discretionary imputation or default-Sb decision is made here. This audit wrote only the two new readiness files; it opened no archive members or score values, used no cluster, made no commits/source edits and touched no production journal.
