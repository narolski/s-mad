# Sol reproducibility: bounded source-backed handoff

Observed 2026-11-14T15:48:46.216657+00:00. **Reporting patch prepared; NOT independently reviewed, NOT integrated, NOT submission clearance. No additional GPU dispatch is ready or justified by this audit.** Current frozen method remains Sb403–407; NEXT and fresh413–417 remain unconfirmed. Source-only E3 freeze b11a8c9 does not establish admission.

## Files and access boundary

Read mambamorph/AGENTS.md, its pointed .codex/imports/smad-2026-11-14/CONTINUE.md and historical CLAUDE.md; smad-next NOTEBOOK/AGENT_STATUS; delivery README/WORKSTREAMS and current Sol reports; actual modular manuscript and OpenCode reproducibility/trace/review records. Neither smad-next/CLAUDE.md nor manuscript_cvpr2027/CLAUDE.md exists. Historical flat IEEE instructions do not describe the current modular CVPR manuscript.

Only added:
- manuscript_cvpr2027/supplement_reproducibility.tex: proposed source-commented fragment, not input by either main variant.
- manuscript_cvpr2027/supplement_threshold_transfer.md: complete already-admitted TT1 result narrative plus both generated table files, copied without altering source text, all existing failures/missing cells retained.
- manuscript_cvpr2027/supplement_reproducibility_sources.json: full source hashes for that consolidation.
- this SOL_REPRODUCIBILITY.md.

No main.tex/main_plotly.tex, figures, existing WIP, manuscript PDF, registration or journal changed. No NPZ/checkpoint, candidate archive member, sealed image/score payload opened; no new score analysis, reader run, scheduler query, submission, rental, commit or external contact. Static source reads are not production reproduction. Existing untracked/modified work preserved.

## Resolved concrete reporting gap: actual original loss/head

Prior OPENCODE_REPRODUCIBILITY_AUDIT's missing-source finding is superseded by OPENCODE_PREPROCESSING_TRACE and its independent review. Rehashed readable already extracted FS1 code and inspected as text:

| FS1 code under /mnt/t7/smad_next/PN1/fs_tree/pn1/code/smadcvpr/ | SHA256 |
|---|---|
| train.py | cbb2cbd1b9a3eb59ab080a540a98aab0f6ead51ea69364d2debe06a984b8c1c5 |
| common.py | b5d42a99cae4f1f2f6dd2965d4973c8f9f65cf73212ffd0a17af4daee33bbea8 |
| archs_a12.py | bedfeb86af2c92aed717e4f43e0b6c466306756d911afc93bcbdd1aae9994876 |

archs_a12 matches the existing FS1 SHA256SUMS code entry. train/common match independently reviewed historical pins. Files are code-only paths, symlinked to the pre-existing AD4 extracted tree; no archive extraction. Relevant PN1 prereg §4 and src/AB1/run.sh68–72 bind a12_clip_vitb16_madation, no label smoothing, sampler prior, pos_weight1, recipev1 and no alternative loss-norm. train.py487 defaults loss-norm mean;655–657 honor explicit positive weight;780–817 implement scalar BCEWithLogits plus conditional unused auxiliary paths;844 leaves hard labels. archs_a12.py253–278 retains projection, L2-normalizes features, constructs nn.Linear(dim,1) with default bias and returns no pixel term;373–376 selects that builder. AdamW construction passes groups without explicit betas/epsilon (train.py255–259); do not invent version-independent values. common.py45–46 gives exact CLIP RGB normalization,854–893 loader conversion/resize/augmentation. Architecture dependency closure and original converted-base equivalence remain open, so this is source-level factual specification requiring independent integration review.

AD4 call/resize chain is already reviewed (OPENCODE_PREPROCESSING_INDEPENDENT_REVIEW and TEXT_REVIEW): keyword scale=.3125,256→80 AREA/lossless PNG, loader80→224 bilinear. No builder alignment or separate enlargement. Mutable legacy working copies have different hashes and are not substitutes. Historical native source-file checks used sizes, not proven source-byte identity; do not upgrade this into complete execution reproduction.

## Inventory, exclusions and uncertainty evidence map

| Topic | Source / exact usable scope | Remaining exact gap |
|---|---|---|
| Eight AB1 arms | AB1/prereg.md, ab1_summary.json, pins.sha256; prior reproducibility audit §3 gives all eight unique/final-row counts; supplement transcribes them | A/B/Sb/Sp final class/source/storage counts, each final arm's contributor-person union and pair multiplicities not independently recounted here; never add host counts as persons |
| Original pool selection | PN1/prereg.md §2; split/split_summary.json; prior audit §4 | Final manifest-to-source/version/pair/engine/blend/storage join plus reasons/counts of exclusions absent from publication-ready table; 191 readable original test hosts versus screened80/sensitivity69 are different analyses |
| AD4 exclusions | preprocessing trace §2:25000 native,25000 copies,15000 SMDD morph rows and29882 other-source rows dropped; fixed observed256/80 sizes | Native MorDIFF processed denominator, fallback alignments and face-detection failures still need admitted metadata reconciliation, not RS1 raw-pool substitution |
| Batch C | REVIEW_AB1_BATCHC_OPENCODE and INDEPENDENT_REPRODUCTION; all30 networks/all5seeds retained,166 reproduced comparisons; manuscript results103ff | Mean bootstrap intervals conditional on nets; no seed resampling, no inferred interaction significance;312 extra unique images remains confound |
| XF1 | XF1/result.md and REVIEW_XF1; frozen403–407,299 hosts, block intervals | Host-block not full retraining uncertainty; blend-control gain remains inconclusive |
| MAD22 | FINAL/result.md, final_pins.json, REVIEW_FINAL_MAD22; frozen403–407;2000joint person/seed draws | Corrected acquisition/raw-to-processed public exclusion chronology and comparator scored denominators not supplied by bare raw counts; parity threshold-fragile, no superiority |
| Exposure | manuscript method/results plus FINAL result; FRGC/colorFERET train,FFHQ development;MAD22 seen earlier and204FRLL photos/102persons | Dataset license/rights and later FRLL overlap not resolved here; FRLL identity independence cannot be asserted |
| SPRINT5 | notebook submission receipt; preregs and f18f8d1/4caa978 implementation evidence |50fits alreadyqueued; no closedfitresults admitted;100-update pilots/warmstart dependencies remain; NOT NEXT or413–417confirmation |

AD4 seeds401–405×2architectures=10, AB1 eight×408–412=40, count-balanced four primary arms×408–412=20 (reader retains30 including B/Sp), frozen Sb403–407. TT1 original401/402 and fresh403–407 on different hosts; Sp printed403–405, MS1 extension403–407. Exact auxiliary-arm seed coverage is preserved in transferred tables rather than silently rounded to five. Supplement does not claim a complete all-experiment score export; complete per-seed values for every paper table still reside in each admitted result source and require a separately reviewed publication table extraction. It opens none of the underlying score files.

## Complete admitted threshold-transfer consolidation

Three original text files are embedded losslessly, with full hashes/byte counts in supplement_reproducibility_sources.json:
1. experiments/TT1_threshold-transfer-unseen-genuine/result.md: original TT1, failed gates/Bn401 exclusion, FS block, Sp/MS1 extensions, MEDS and post-hoc Z/S followups.
2. tt1_read_tables.md: all printed initial per-network/source/geometry tables.
3. tt1_read_fs_tables.md: full generated fresh-block tables.

The report intentionally preserves missing MEDS intervals/CP cells: these are unavailable in the admitted printed table, not zero. Dedicated generated full MEDS, Sp and MS1 per-source table files were not found in the source directory listing; admitted result.md contains their published report-level extent. Producing missing exact cells would require an expressly admitted output-only table exporter and independent review; no new payload read is justified by this handoff. Current material is complete as a consolidation of these admitted text sources, not a claim that every possible threshold/source cell exists.

Qualifiers must travel with tables: no new-source attacks; own-rule is strict logit>0, camera τ is different; low-resolution/bordered B behavior does not imply sharp-source transfer; MEDS false alarms cluster in110small images/54persons;23TT1frames dropped from post-hoc reweighting, four-person sparse bin can move result7pp; original registered verdicts and unregistered dense-bin sensitivity stay distinct. Review files named in consolidation.

## Concrete remaining work and dispatch disposition

No new training computation is needed to publish these admitted threshold reports. Do NOT rerun src/TT1/tt1_read*.py or canonical journals for formatting: they are scientific readers, not free reporting tools.

1. Immediate zero-GPU independent review of these four new files against named immutable sources, especially actual architecture dispatch, BCE/auxiliary absence, all seed blocks, and byte-preserved threshold sources. Local text/hash commands below suffice; no candidate data. Accept only factual static claims, leave package/dependency evidence limits explicit.
2. Final person/pair inventory needs a metadata-only exporter operating on registered training CSVs and split/construction metadata, never candidate scores. Inputs already named in PN1/AB1 pins and split_summary. Existing registered command for a publication census was NOT located; do not invent one as registered or submit GPU work. Prepare a tiny source-reviewed exporter with exact deduplication rules: contributing-person union (hosts+partners+landmark donors), pair multiplicity, source×class×history rows, unique image IDs, all excluded/missing identities/reasons. Resource:gx10 CPU, no GPU; output proposed supplement_inventory.json plus input SHA256SUMS; runtime unknown until manifest inventory sized. Independent methodology and exact-input review required before treating census as verified. ASTRA_PLAN_REQUEST only if donor/person mapping remains ambiguous: which recorded key represents actual contributor versus shape-only donor, with PN1 split and AB1 construction definitions; do not choose a default.
3. Full native-MorDIFF alignment/failure inventory needs existing AD4 processed manifest and construction/evaluation metadata, not image reprocessing or sealed-score inspection. Existing publication exporter command NOT located; read-only metadata-only plan/review required. No registered rerun or GPU dispatch from this audit.
4. SbFM supplemental scoring already job6319579; RZ1512 already6319490, comparator6319491 and DINO6319264 tracked by root. Reuse exact registered receipts/commands in COMPUTE_QUEUE and SOL_TRAINING_PROTOCOL; do not duplicate. NEXT exact admission and selected-arm fresh413–417producer remain root/training-owner tasks. No scientific loss can be inferred from implementation/admission gaps.
5. SPRINT5 ranking6321090,breadth6321194,tail6321244,HN6321261 already cover50fits. f18f8d1 binds prospective input/policy and4caa978 pairedV2 is code-only. Tail af0_u5061missing and10/17/17component guards retain INCONCLUSIVE; camera127/132auxiliary differs from independentpositive90%sensitivity+simultaneous2ppNI. LA1HQmapping BLOCKED; low-resolution calibration is diagnostic only. No extra fits requested.

## Checks and integration hold

Source copies verified byte-contained and rehashed. TeX fragment structural braces checked; pdflatex is unavailable on gx10, so no compile/layout claim. Main variants and WIP were never edited. Parent should commission independent source and layout review, compile in established manuscript environment, then integrate fragment/choose publication table format. Rights, comparisons, actual results and NI blockers prevent WIP removal. No self-approval. This bounded owner exits after handoff.
