# Batch-C reader-context admission audit — 14 November 2026

**Disposition: production NO-GO.** Independent bounded source/metadata audit, not a scientific result or release approval. Existing 15 count-balanced fits should be reused after the remaining conditions below are satisfied. NEXT ownership and selection remain separate.

Read both continuation briefs, current notebook/owner/workflow/delivery records, STATISTICAL_PLAN, REVIEW_WORKFLOW (including addenda), METHOD_PLAN, AB1 registration amendments 4/4b/5/5b/7/7b, and reader/import/test sources. Repository HEAD at inspection: `3a2ca142df6e71da1c3042c61b09c0e56ca63d56`. Existing modified reader and untracked companion/tests were preserved. No cluster contact, commit, candidate archive member access, candidate calculation, or production claim was performed.

Floor files were inspected for identity/schema metadata and opaque byte integrity only: no floor prediction values or scientific summaries were printed or analysed. Learner inputs were byte-compared with HEAD and checked against committed pins; their real numerical reproduction was not run. Archive inspection was limited to filesystem existence and collection receipt metadata, not archive hashing or extraction.

## Verified now

- Independently reran `src/AB1/tests/test_pm3_admission.py`: **18 tests passed**, 0.026 seconds; three existing unclosed-manifest ResourceWarnings from `ab1_read.py:59` remain.
- Independently reran companion `--self-test`: PASS (ties, strict thresholds, summary roundtrip, duplicate/nonfinite/label/count refusal).
- Ran full `--pair C --mock`, using real permitted host/D/manifest metadata with generated scores. Exit 0; supporting output `OPENCODE_BATCHC_MOCK_20261114.json`, SHA256 `eb5048177a2f2e047726689359c404893a8596981bb5eae07fdccd35435784b5`. Its verdicts are synthetic software outputs, never empirical evidence.
- Interpreter: `/home/narolski/mambamorph-code/.venv-spark/bin/python`, Python 3.12.3, GCC 13.3.0, NumPy 1.26.4; `-I`, four BLAS/OMP thread limits of 2. No optimized Python (`-O`): these readers rely on assertions.
- Current reader/test/companion hashes equal REVIEW_WORKFLOW addendum B. Imported PM, AB1 and C2P hashes equal their recorded constants.
- Evaluation manifest: 21,277 distinct IDs; exact pinned hash below. Six floor ID sets have no missing evaluation IDs and no duplicate IDs. Counts: ri_R4_vs_R3 582; ri_S4_vs_S3 582; dev_S4_vs_S3 200; test_cv_R4_vs_R3 382; test_fm_R4_vs_R3 382; test_S4_vs_S3 382. All six declare/default to kind `floor`, not a ceiling. Required model columns exist: all-cue uses `logreg`; nuisance uses `nu_gbt` for test_cv_R4_vs_R3 and test_S4_vs_S3, otherwise `nu_logreg`.
- Host metadata agrees: dev 100, read test 191, clean 80, shape-linked 32, clean minus shape-linked 69. D has 873 unique (rung, host) keys, all positive finite; no missing S3/S4 D for the 180 primary hosts. Full mock completes the registered metadata/statistic path.
- All 24 named floor/context/learner input files below are byte-identical to HEAD and match a byte-identical committed stage pin. This closes their current byte-provenance question, not numerical reproduction.
- All 15 collected AB1C archive paths and sidecars exist in `/mnt/t7/smad_next/coordination_20261114/archives/AB1C`; all 15 AB1 comparator paths and sidecars exist in `/mnt/t7/smad_next/AB1/results` (Sb/B/Sp × 408–412). Existence does not certify bytes, internal identity or successful fits.
- Before the mock, canonical C claim, completion receipt and proposed production output were absent. The mock's source path bypasses claims and native loading; the final release must recheck absence, including dangling links.

## Exact unresolved blockers and admission checklist

### B1 — missing registered within-D context print (confirmed implementation gap)

AB1 amendment 4b item 3 requires `ri_R4_vs_R3_withinD.json` and `test_cv_R4_vs_R3_withinD.json` beside stratified AUCs, with different-row-set/context-only labels. Amendment 5 inherits prints, and batch C inherits the amendment-4/4b/5b rule. Parent `ab1_pm_read.py:211–214` prints both. Batch-C main does not invoke parent main and omits them. Companion prints transfer references only; it does not close this gap.

Both files exist, are HEAD-identical and stage-6 pinned (hashes below). Assign a narrow display-only companion/integration repair, independent source review, pin update and synthetic test. Do not alter the deciding statistic, pretend the rows are the 180-host primary, or silently waive the print. No reader was edited here.

### B2 — full external numerical path still unverified

`ab1_pm3_read.py:388–392` calls `check.exceeds` only outside mock mode, after native reading and calculations. Thus even the successful full mock does **not** exercise these dependencies. Each of 30 networks requests 6 contrasts × 2 floor types = 360 floor calls, normally 2,000 component draws each.

Before production, separately validate actual admitted floor JSON/CSV consistency, finite prediction columns, binary labels/components, nonempty classes, exact summary reproduction (`check._load`, tolerance 1e-9), and numerical bootstrap feasibility; then validate the companion's real-file joins, counts and 1e-12 summary reproduction in its permitted descriptive scope. These consume real existing floor/learner values and were outside this metadata-only assignment. No candidate is needed for these checks. Use synthetic candidate values if exercising `check.exceeds`; label all resulting differences synthetic and discard them as scientific evidence.

Source-specific caveats: `check.FDIR` and `pn1lib.SPLIT` are absolute live-repository paths even from a detached reader checkout. The companion ROOT is instead relative to its source. Bind the actual resolved paths and bytes in the release receipt. `check._pinned` checks committed pinfile membership, not a global clean repository; companion checks input bytes against HEAD. Do not rely on checkout cleanliness alone. PM's AB1 source-hash assertion and AB1's C2P assertion live in their respective main functions, which batch C does not call: manually bind those transitive hashes.

### B3 — complete source/archive release receipt and current pins

- [ ] Bind reviewed repaired reader/companion/tests and transitive sources below in the registered release record; historical amendment-7b reader `d21180d7…` is superseded by a reviewed repair, not currently identical code. Current reader is modified and companion/tests untracked; implementation review authorizes commit, not production. Lead must perform required pin/commit/review handling while preserving unrelated work.
- [ ] Bind all 30 exact archive names, byte sizes and cryptographic hashes, authoritative collection provenance and matching sidecars; verify opaque archive hashes through the authorized collector. The receipt `experiments/RECORDS_ledger/codex_20261114/NEW_COLLECTION_VERIFIED.json` (SHA256 `a4027f628d460a5f131b030962fd6e7c8031e084849787c30c47f101511177af`) records the 15 AB1C paths at 10:32:47 CET. Its historical hash verification is not a fresh check of current local bytes. Comparator provenance must be bound separately.
- [ ] Use reviewed `--c-results /mnt/t7/smad_next/coordination_20261114/archives/AB1C` and `--ab1-results /mnt/t7/smad_next/AB1/results`, or explicitly reviewed staging. The default C directory is not the collected location.
- [ ] Pin all six training manifests, eval manifest, two PN1 split tables, clean-host/D tables and applicable floor/learner pinfiles, including absolute resolved dependencies. Verify train_Sp under AB1/manifests, **not** the FS1 Sp manifest; Sb/B come from PN1/fs_tree.
- [ ] Independent admission reviewer binds exact source/input receipt, output locations, completed-fit/arrival evidence, registered late/missing-seed treatment, and interpreter/environment. No such complete release receipt is established here.

### B4 — facts that cannot be proven with unopened archive payloads

Actual TASK/ARM/SEED, native ID order and finite logits, embedded train/eval manifest hashes, H100 GPU provenance, 6,250 steps/limit zero, pack/overlay, n_items and finite training losses require native contents. The reviewed wrapper checks them on first authorized access. Do **not** call `_validate_native_archive` as metadata-only preflight: it opens `scores_eval.npz` and reads logits. File names and sidecars cannot prove internal seed identity.

Release must distinguish authorization for a guarded once-only read from a claim that its native guards already passed. Preserve every refusal/failure and the permanent claim; no automatic removal/retry. The existing reader can treat loader refusals as missing networks under its readable-seed logic, so report all such dispositions and obtain review rather than silently declaring a model scientifically failed.

### B5 — once-only output and conclusions handling

- [ ] Recheck no canonical `/mnt/t7/smad_next/AB1/READ_ONCE_PM3/C.claim.json` or `C.complete.json`, no production output (including symlink), and writable prepared durable output directory. Reader owns atomic claim creation; do not preclaim.
- [ ] Record exact command, start/end, stdout/stderr, exit status, source/admission hashes and output hash. A crash can leave partial output plus permanent claim: independent recovery disposition required.
- [ ] Integrate within-D context and descriptive learner references with correct populations. H-c1 = Sb−SpV, H-c2 = BN−BV; interaction printed only. Unique-image diversity remains unmatched. S4/S3 is near-certain by training design; 99.5% intervals are the registered sensitivity, not complete 16-verdict familywise control.
- [ ] Independent results review before any conclusion. No NEXT promotion, benchmark release, scientific GO or new fit follows from these tests.

## Source hashes (SHA256)

| Source | Hash |
|---|---|
| src/AB1/ab1_pm3_read.py | a31f51955b78f4c1e746446a0555b1dcd7d4f010e7b85c4e4715782dea8076fb |
| src/AB1/ab1_pm_read.py | ba6efdada789c2a42ef47fa1fa39e707012f66641be40b6346ce9b45b067ed5e |
| src/AB1/ab1_read.py | 74ecdf7a2ecb35812dcf4e5d5b9f5c3b1f095fc6846ae6f4813bfb28404d035b |
| src/AB1/ab1c_transfer_report.py | d47f597712bb793a00a7dff9da104a6b43eb09f5bac845fc2c90d462efddd9ef |
| src/AB1/tests/test_pm3_admission.py | c667782d57effc482587f031cd438ca82e3afabb938b7d3a6d301bff84c1a6aa |
| src/PN1/c2p_read.py | 45e72914d960214131a5b4a11aefd2e301a2236e908d77d20d94136c1d7d5840 |
| src/PN1/pn1lib.py | 136f78543af3747811919fcaf06cfc0abaeb0d64692f2c196c9320bfe4841482 |
| src/adversary/check.py | e08bcecb59d892daf8900d7e3993ba8f7620555ea93e698d59b095239f155837 |

## Metadata and external dependency pins

Paths below beginning AB1, PN1, DATA or BD1 are under `/mnt/t7/smad_next/`, except explicitly repository-relative split tables.

| Input | SHA256 |
|---|---|
| AB1/manifests/ab1_eval.csv | 93a5ba234f91e57951829c5536fabbe0f792ee4ad0a293f074aaca72f7465bd5 |
| AB1/c/manifests/train_SpV.csv (8,386 rows) | f6521d96de7d93ff62232c4eb8236d2560cf39f2e8ca6a56d676f3c0c39af759 |
| AB1/c/manifests/train_BN.csv (8,386) | c1b4497bb59343b7f5dd48149e300fb136533790724dfdf83aa395a703fe6af1 |
| AB1/c/manifests/train_BV.csv (8,386) | ee4e227b2cd6648d196b5d61300a9cf483c85f05a80afae0fd6e774153baf04f |
| PN1/fs_tree/pn1/data/manifests/train_Sb.csv (8,386) | 2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a |
| PN1/fs_tree/pn1/data/manifests/train_B.csv (7,762) | bd53dc3252a767671bd5b35651e9108a35f7b363fe4642bae593fa88a442da70 |
| AB1/manifests/train_Sp.csv (7,762) | cf386dc7aaaee5723e64010cadd742c21fed0236d34e52e65daabba33a5e6848 |
| DATA/overlap/test_hosts_clean_of_dev.csv | 814c44861d706553bd827e5dd5634817ee289c0b12bc45a553c5d759b8362358 |
| BD1/d_values.csv | cf2ba3fa87f434f72d195a6c6e96df6ad9b99ee0b7f887ff44625b9712177725 |
| experiments/PN1_protocol-network-first-tests/split/ladder_split.csv (repository) | 2299ac2b1f3a8a4798fe1730ab8722780933ba956d4b38080fdeeb730b391ec3 |
| experiments/PN1_protocol-network-first-tests/split/af0_split.csv (repository) | 091712ef4d68fe40943961cdfd5111b6a457cabfdf3b9058b490015c2f04a23a |

The following exact stage files under repository `experiments/ADV_shortcut-floors/floors/` bind the verified 24 input hashes without reproducing prediction values:

| Pinfile | Required members verified | SHA256 of pinfile |
|---|---|---|
| pins_stage0.sha256 | test_cv_R4_vs_R3 and test_fm_R4_vs_R3, each .json + _heldout.csv | a84371dcff361ba21579883abace32ec21456fd29c77a8f81349b5be3c897971 |
| pins_stage3.sha256 | ri_R4_vs_R3, ri_S4_vs_S3, dev_S4_vs_S3, test_S4_vs_S3, each .json + _heldout.csv | f2562ddfffe112d382e8ae33bb4342130d0165c9da5f38af08c24f5fbae80b67 |
| pins_stage6.sha256 | ri_R4_vs_R3_withinD.json, test_cv_R4_vs_R3_withinD.json | 827cab78dd590cea56ddabfed4a29e0e0626439214f89f93af69f6486b32a59f |
| pins_stage9.sha256 | sel360_rows.csv | 7325cc6245aa43bc7c1f0bbb76e49203f729f088b1c7cbddd23dc677fad36b8a |
| pins_stage11.sha256 | transfer_SpV and transfer_BN, each .json + _rows.csv + _rows_summary.json | 1b634f840a89046bb2192b74d6dc8841e8d029e0fbd0d9fb5851f470db002b23 |
| pins_stage12.sha256 | transfer_BV, .json + _rows.csv + _rows_summary.json | 536baa8ac7f98f51c74d5ca968ac6fb176f634e6c7770b8bad8c7576b942b4ac |

Within-D context hashes: `ri_R4_vs_R3_withinD.json` = `9d177165c79d0ea002c10983c1b18535b7fdd478cb65cdac13b8100b746d55c9`; `test_cv_R4_vs_R3_withinD.json` = `98187bd847afc8d314732f891bf09bd9855bb6740e9206a79d70142b6058e785`.

## Executable next step

Assign B1 display integration to the AB1 owner (not the NEXT owner), then independently review the exact patch and re-run the safe guard command from `/home/narolski/smad-next`:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 TMPDIR=/tmp/opencode \
  /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/AB1/tests/test_pm3_admission.py
```

The next release-critical execution is an explicitly authorized floor/learner-only preflight (B2), followed by opaque collection verification and exact independent admission (B3). The already successful full mock need not be repeated unchanged. After a code change, use a **new** mock output path; the supporting JSON is create-only. The production command in STATISTICAL_PLAN requires the explicit collected `--c-results` mapping and all B1–B5 release conditions; it is not authorized by this report.
