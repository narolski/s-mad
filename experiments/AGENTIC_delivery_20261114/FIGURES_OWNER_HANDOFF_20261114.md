# Owner handoff: figures explaining model behavior

Owner role: Sol, row “Figury wyjaśniające zachowanie modeli”. Bounded turn ready to close and release the slot after this handoff. **Status: real computation and reviewable outputs ready; OCC1 independent post-run and print approval PENDING. Do not show OCC1 to the user as finished.** No external publication or source-face export is authorized.

## What is complete

Earlier three-image FFHQ gradient pilot: seven actual models×three conditions, raw gradient and gradient-times-input, individual noTTA logits/uncalibrated scores. Independent result review `ASTRA_XAI_RESULTS_REVIEW_20261114.md` SHA256 `b0275313b13e7fde3d08ef9c814b8a97684cc9238a03b7b5748e2d7d71e6fc6a` granted private descriptive display only. Raw maps retain the black-pixel caveat, fixed within-model scales, explicit precision repairs and two failed attempts. Its verified durable whole-copy is `/mnt/t7/smad_next/XAI/backup_20261114/shortcut_attribution_20261114__20261114T123518_431783Z`,144files/100486394bytes, receipt SHA256 `0265ec3440eadf32813350b1d4018253066ecc5a44c742715da57d64f7db095f`. See existing XAI handoff; this is separate from seam evidence.

New actual constant-occlusion seam/surround pilot (OCC1): five complete models, eight fixed matched source/control rungs, two fixed constant fills,64patches. **5120actual full occlusions**, plus320smoke views. Models A/B/Sb fixed frozen seed403, official MixFaceNet and SelfMAD completed all gates. Official MADation B failed batch-parity smoke; official MADation L failed CUDA OOM smoke. Both remain explicit and were not swept/retried. No criterion, fill, example, checkpoint, tolerance or region was changed after seeing scores.

The full matched development example is FERET host00026 with partner00140, selected lexicographically before scores. Existing same-R4-hull amendment7b S0/S3/S4 and R0/R2w/R2w4/R3/R4 were used **in place**. Parent explicitly admitted internal numeric-only research after independent exact-hash pre-run GO; no source-face, occluded-image or overlay pixels were exported, including no source RGB arrays in NPZ. Display/publication rights remain a separate decision. Current Color FERET and older local Gray agreements differ; the OCC1 README records that distinction and primary sources without claiming unrestricted export.

## Exact review packet and hashes

Experiment record `/home/narolski/smad-next/experiments/OCC1_seam-surround-pilot_20261114/`:

| Artifact | SHA256 |
|---|---|
| `prereg.md` | `e57b042df42fcfe6f0d261b2d7995d1d8699594638e39c72a4d15e11f57c484a` |
| `INPUT_MODEL_PINS.json` | `42f6f16c17a34b501dbb87ce98872186a6ffcb3510743a95ede29a9eda9057d4` |
| `ASTRA_PRERUN_REVIEW_20261114.md` | `e4494f0021934c90ff89f26348cf5ec9c073467893708060df4f633dab6ddb0f` |
| `PARENT_INTERNAL_RESEARCH_ADMISSION_20261114.json` | `9e1bd122966c6b9ac45984cdb3b6f0d9f25ba352d0e454ef6a48078270fd464c` |
| `src/OCC1/occlusion_runner.py` | `2d89d00054bdcae2a4f3f99b791b8af6280f702d3ea071a876b0307f8388776a` |
| `src/OCC1/verify_outputs.py` | `5f0be9a0373da675fe29b92cc5bdd2232d565a5d28415dfe6680ce870a29d5b3` |
| `src/OCC1/render_numeric_v2.py` | `504582fdf39d975ac19db8b6180a0fa1769f35dbc6a8baf2cdbfd0ac4c36b886` |

Durable output root `/mnt/t7/smad_next/OCC1/20261114/`:

- `NUMERICAL_OUTPUT_VERIFICATION.json`, SHA256 `193ec7ff4c57353b8bc79486abaf7028ff7f37659e610e48b2c8ee4d8e8495d8`: per-file/full-result hashes, five complete sweeps, two failed smokes. Exact CSV/NPZ deltas, grid completeness/finite values, regional means and paired-rung differences verified by the author; independent reproduction still required.
- `{A,B,Sb,mixfacenet_mad_smdd,selfmad_hrnet_w18}_full/`: `raw_responses.npz`, `per_patch_scores.csv`, `result.json`, start receipt. NPZ contains numeric logit grids and geometric masks, no source images. Each full grid8×2×8×8; every requested rung/fill/patch retained.
- `madation_vitb16_smoke/failure.json`, `madation_vitl14_smoke/failure.json`; no full directories for failed models. MADation B error reports the gate name only: exact failing rung/discrepancy was not captured. MADation L failed during CUDA allocation; cause remains unresolved. Do not invent values or a diagnosis.
- `baseline_scores.csv`40rows; `regional_effects.csv`80rows; `paired_rung_effects.csv`50rows. All7requested model dispositions must remain visible in a final presentation, including failures.
- `execution_20261114.jsonl`: exact argv/start-end/exit/stdout/stderr for full A and remaining model smoke/full commands. A's initial smoke has its own result/start receipts. Source-provenance/time details are in these receipts, not inferred from PDF metadata.
- `numeric_print_v2/FIGURE_MANIFEST.json`, SHA256 `e44f8cf76ac4b810b14b3c54c63b36fcbf322c7f25302cf369a3e0b468b64272`: five model-specific color and grayscale pages, PNG/SVG/PDF. **Review candidates only.**180×210mm, minimum configured8pt, measured8×8tiles with no smoothing, signed colorbar or negative-value hatching. Shared maximum across all8rungs/twofills per model. Baseline and preselected P18occluded logits plus actual regional means are printed; no source-face pixels.
- `numeric_print_v2/SVG_PRINT_SIZE_FONT_QA.json`, SHA256 `c4ebad0e37f930cd162b407bd1e51a6ff07db696aead4ad90b9e6c2335034f31`: all10actual SVGs minimum8text units; page geometry recorded. Representative PDF dimensions confirmed180×210mm with pdfinfo. PyMuPDF unavailable: PDF font-span QA NOT RUN. Author visually checked A color/SelfMAD grayscale. Initial v1 had overlapping labels and is retained as a rejected layout, not a deliverable.

## Proposed independent bounded review

Assign the statistics/controls reviewer, or another model/code-independent reviewer if its thread slot is unavailable. A re-engagement attempt returned `agent thread limit reached`; this is coordination, not scientific approval. Reviewer should:

1. Bind exact pre-run source/input/model pins and parent numeric-only admission. Confirm no source pixels/closed challenger or sealed data were exported/read. Preserve separate image-rights decision.
2. Independently reproduce complete CSV/NPZ deltas, sigmoid-score convention,17seam-overlapping/17control cells, region/paired effects, all5full finite grids, all7model dispositions and both failed-smoke receipts. Confirm no retries/criterion changes and no full sweep after failed smoke.
3. Assess interpretation of paired rung comparisons: S4/S0 share R2w4outside; S3outside is R2w, so S4/S3does not isolate identity. Seams are **64px patches overlapping a narrow ring by>=10%**, not pure seam erasure; they remove other facial information. Controls match area/shape only; lexicographic controls mostly occupy top rows, not matched texture/position. Two fills do not remove mask artifacts. Large broad response shifts cannot be promoted to localized seam mechanisms.
4. Read actual180mm v2color/grayscale pages, check font/overlap/colorbar/contrast/legend/P18values against raw outputs. Preserve no-face display and all caveats. If improvements are needed, change rendering only in a fresh revision and rebind hashes; no new inference or response-map smoothing.
5. Return GO/GO_WITH_FIXES/NO_GO separately for numerical correctness, descriptive interpretation, print readability and source-image display permission. Reviewer must not certify population, detection improvement or causal identity/seam localization from this single fixed example.

## Remaining blockers and next action

- Independent OCC1 numerical/results/print review remains mandatory; no finished user-facing seam panel yet.
- Original-plus-map face display is NOT released; only numerical plots were rendered. Applicable source-image permission must be resolved separately. Licensed FFHQ candidates found have actual morph/warp pairs but not complete same-person S0/S3control coverage; no silent substitution or new construction occurred.
- MADation B/L missing maps remain explicit failures. Any new platform, batch, precision, instrumentation or retry proposal needs a separate prospective review/parent release; no outcome-driven repair was attempted.
- Five complete sweeps and plots are durable; no cluster mutation, spending, commit/push, deletion or interruption of another process occurred. Root remained near98%used, so all substantial new outputs were written to /mnt/t7.

The owner can now release the slot. Main agent can verify this packet and assign bounded corrections; no idle wait or automatic monitoring is claimed.
