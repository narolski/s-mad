# Independent reproducibility supplement review

Astra, 2026-11-14. **GO for the factual source-backed text and lossless admitted-text consolidation; HOLD for final integrated/publication supplement until the packaging/layout items below are resolved.** No new scientific result or scientific read release. Main files, WIP, author files, registered readers and canonical journals were not modified.

## Scope and result

Read mambamorph AGENTS/CONTINUE, current notebook/delivery instructions, Sol's handoff, proposed three supplement files, named source/review records, and the original checksum-bound trainer/common/architecture source as text. No NPZ, scores, candidate archives, checkpoints, images or sealed payloads were opened. No inference or reader was invoked. Historical missing-source findings were evaluated against the later preprocessing trace and independent review, not silently retained as current blockers.

1. **Loss/head/preprocessing: PASS at static source level.** Rehashed FS1 `code/smadcvpr/train.py`, `common.py`, `archs_a12.py` to the three full expected hashes below. `src/AB1/run.sh` binds the named architecture, 224 input, prior sampler, positive weight 1, no label smoothing, flip augmentation, AdamW and recipe v1. The trainer's default mean BCEWithLogits, hard targets, conditional teacher/pixel/orthogonality hooks, and architecture dispatch support the text: the selected CLIP builder returns no pixel term, initializes auxiliary weights to zero, keeps the visual projection, L2-normalizes its output and applies `nn.Linear(dim,1)` with the default bias. AdamW receives parameter groups without explicit betas/epsilon. Common loader source supports RGB, conditional PIL bilinear resize, float32 RGB/255 to CHW, probability-.5 index flip, and the exact CLIP channel constants. This does not verify full dependency closure, converted base equivalence, actual production execution or source-image byte identity.
2. **AD4 trace: PASS as the already-reviewed construction provenance.** The supplement correctly locates AREA 256→80 in the keyword-bound builder and bilinear 80→224 in the loader, retaining the positional-registration discrepancy and excluding invented alignment/enlargement. The independent preprocessing review supports these specific claims. Its native source-size-only check and assumed converted-base equivalence must not become stronger reproduction claims.
3. **Inventory/uncertainty/exposure: PASS within stated limits.** Eight-arm unique-image/final-row values match the earlier source audit; the PN1 pool definitions support the 536/8/191/100/156/124 and AF0 663/67/481/115 counts. These are pools, not additive final-arm person counts. The separate 80/69-host populations and 11 shape links remain explicit. Different seed blocks/platforms and conditional versus joint uncertainty are not collapsed. MAD22 exposure, FRLL-person overlap, 4483 morphs/204 genuine photos versus 5707 candidate input inventory, and unresolved rights/census issues are retained. No new independent census or numerical reproduction is claimed by this review.
4. **TT1 transfer: PASS lossless consolidation.** Independently read the three already-admitted source text files, checked each exact byte length and SHA256 against the JSON, then confirmed each entire byte sequence occurs exactly once in the consolidated Markdown. Thus every original table cell, denominator, missing value, failure, seed range, post-hoc label and qualification is preserved. The wrapper correctly distinguishes strict logit>0 from camera thresholds and genuine-only false alarms from sensitivity. This is verification of transfer fidelity, not a new validation of underlying logits. In particular no missing MEDS intervals/CP cells were imputed and Bn401's failed gate remains excluded.

## Required integration steps

- The TeX currently refers to `supplement_threshold_transfer.md`; it does not typeset its tables. Before calling the package a complete publication supplement, either explicitly deliver this Markdown as an accessible accompanying artifact or convert the already-admitted text/tables to a reviewed supplement format. Preserve all seed/platform blocks, denominators, failures, missing cells and registered/post-hoc distinctions; do not rerun scientific readers for formatting.
- Compile and visually check the integrated document in its actual CVPR template, including equations, table widths, references and the retained WIP. This review grants source-text acceptance, not final page-limit or submission clearance.
- Keep the Sol handoff and this review with the source JSON. The JSON currently pins only the three transfer texts; it is not a full machine-readable implementation dependency manifest. Prefer extending a separate manifest with the implementation/trace pins below if distributing the supplement independently. Do not describe that three-entry JSON as a complete dependency closure.
- Preserve explicit source-level provenance limits and unresolved final-arm/fallback/rights inventories. No factual correction to the current BCE/head or copied TT1 values was found. The historical statement in Sol's handoff that pdflatex was unavailable on gx10 remains valid; the independent local compile below is additional evidence, not a reason to rewrite historical checks.

## Isolated compilation and visual check

Local `/Library/TeX/texbin/pdflatex` compiled the unchanged fragment successfully in an isolated 10pt two-column article with amsmath: two pages, no overfull boxes, several underfull-box warnings. Both rendered pages were visually inspected using Poppler/PDF workflow. No clipped content or equation collision was observed; the long Markdown filename produces loose spacing. This wrapper is NOT the CVPR template and contains no TT1 Markdown tables. Local evidence resides under `work/supplement_review/` (wrapper, compile log, PDF and numeric text-only page renders). It does not modify the manuscript PDF. No full-template/layout GO is implied.

## Exact inspected bindings

| File | SHA256 |
|---|---|
| SOL_REPRODUCIBILITY.md | `c9a6b11f1dada9f9c6e17e5ba54bc4e9197e9693cd55fb15b6d954fae9c64440` |
| supplement_reproducibility.tex | `04c9d28fc88ff16eb3f2638dd38d36555c5f85bc5d19e3f013af0fafbd5aa513` |
| supplement_threshold_transfer.md | `8f479d5caa67ea93ae21784d4ba0cfee6409b8a8a7bf68506ffaf5d9781e6301` |
| supplement_reproducibility_sources.json | `ebaca2ab2e95da1339878c4832b60a360517506c69b9556b7c142ca49db35ddf` |
| FS1 train.py | `cbb2cbd1b9a3eb59ab080a540a98aab0f6ead51ea69364d2debe06a984b8c1c5` |
| FS1 common.py | `b5d42a99cae4f1f2f6dd2965d4973c8f9f65cf73212ffd0a17af4daee33bbea8` |
| FS1 archs_a12.py | `bedfeb86af2c92aed717e4f43e0b6c466306756d911afc93bcbdd1aae9994876` |
| src/AB1/run.sh | `cfa4ed26d747e1d50f66cfc2af823ed55fd7f31634d6285cff9363a5fa796ab4` |
| PN1 prereg.md | `89df6f155ec703b012dd0389d297e69469c1ec5c66439f3262c4405e83f3c9b2` |
| OPENCODE_PREPROCESSING_TRACE | `dc6e1fb647c4968b0590443171ae12c1eace5a776fec11324ebe4bb02074d30f` |
| OPENCODE_PREPROCESSING_INDEPENDENT_REVIEW | `f5e9a055016b506d4c81eff3ab29615daa1bf799a97f806b6de6f632a88b1483` |
| OPENCODE_REPRODUCIBILITY_AUDIT | `74d4da765d49b414e028023afd3be1f00a3eddd63d8dc11c9622b854c7fbe929` |
| TT1 result.md (36520 bytes) | `2d5e55ce783716f17e7b3f420def4d1ebb5bd123e2e333d6c5c29c5b703994c6` |
| TT1 tt1_read_tables.md (17759 bytes) | `2cf5899eb787fc7be5cc569495b01215c8a9857e8075a1ab2da4a129751a8ccc` |
| TT1 tt1_read_fs_tables.md (21719 bytes) | `2512f0295931e1b75f388e6c12431d7c54dfe95f79edd0b0637e17a75f7bab1c` |
