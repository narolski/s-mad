# Independent review of next-method support pins

Reviewer: baseline-recovery agent, independent of the inputs/floors author. Reviewed 14 November 2026, using the approved version 3 rule, registered RZ1/TT1/MEDS readers and source development manifests only. No candidate score, archive, checkpoint or image was opened.

## Verdict

**GO for the separate criterion (b)–(f) metadata package**, subject to the lead-owned commit and `verify --require-clean` from its clean worktree. It extends the committed 44-file detection package without rewriting it. This is input-integrity approval, not candidate-read admission, challenger eligibility, or an outcome of any criterion.

Reviewed `src/NEXT/prepare_support.py` SHA256: `e85c79356adbff6fc7b46dd42e4fa5595f0638db93f9a119c9f24c0dc1c49972`.
Reviewed `inputs/support/support_v3.json` SHA256: `5ac8d319dbec42044d9812e9deaccb25096c5ba945aaf6e5011eaaf815eacc7a`.
Reviewed `inputs/support/pins.sha256` SHA256: `5e8d39f02345b39755ffbcd13def8af26a1be057e15f7499d7d5649784c2b02a` (20 pins).

## Findings and checklist

1. **Question/design: ok.** This serializes already registered row sets, pairings, recipes and bootstrap definitions. It computes no candidate statistic, trains no floor and changes no image operation, rule margin, seed, challenger order or benchmark exposure. RZ1 is imported for definitions; its candidate-loading functions and main reader are not called.
2. **Storage: independently checked.** Native/stored IDs map exactly through the original holdout manifest: 291 genuine pairs and 150 morph pairs at fm61; 290 genuine and 149 morph pairs at amsl112. Native pairs are unique and every native/stored row exists. The metadata preserves the existing plain-control and H-new-1 definitions, native-logit sample SD (`ddof=1`), bootstrap count and registered draw seeds. It is not proof that any control or storage criterion passes.
3. **TT1: ok.** The seven primary genuine families are produced by the registered `load_pools()`/primary filter, with LFW and CALFW combined as specified. Counts are replay_attack 200, msu_mfsd 65, oulu_npu 989, casia_fasd 150, lfw_calfw 10,973, cfp_ff 4,725 and agedb_30 3,933. The support pins the canonical 34,411-row scoring-manifest hash and raw/aligned manifest provenance. The next reader must calculate the seven-family mean as registered, not weight the mean by family size or include secondary unaligned pools.
4. **Same-person and borders: independently checked.** All 100 development S3 IDs equal the source manifest's splice/dev/S3 list. All 1,582 camera-border IDs equal the required AB1x development subset and exist in TT1 with identical host, rung and genuine label. Full TT1 border aggregates are not a substitute for this subset. This establishes row correspondence, not identical scoring paths; each network's actual bit-identity gate and path still need validation.
5. **MEDS privacy and bootstrap: independently checked.** Full private MEDS-manifest order matches the scoring-manifest order. Every exported row index exactly selects `aligned == 1`: 865 rows across 400 persons. Opaque `pNNNNNN` groups match the ordinal ordering of sorted original person keys, so sorting groups preserves the original person-bootstrap draw mapping at seed 20261125. The package contains neither the original subject keys nor original MEDS row IDs; these remain in the external pinned private source. The reader resolves row IDs privately and emits aggregates only. Do not treat row indices as person groups or resample images independently.
6. **Kernel/platform metadata: ok within scope.** Nine training and four held-out transform strings are disjoint and match the registered RZ1 definitions. Cross-table genuine and morph IDs are drawn from the pinned cross manifest. No transform is executed by this package. In particular the 512 mix arm still has no registered cross table and cannot acquire eligibility merely from the presence of these strings. Recipe and yardstick metadata describe expectations; they do not establish that a model was trained correctly or its gate passed.
7. **Integrity: verified.** The validator passed all 20 pins. In a temporary copied root with the same pinned paths, one appended byte in `support_v3.json` was rejected. Preparation also pins the source reader definitions and external manifest hashes, checks canonical source hashes and exact MEDS ordering, and refuses replacing changed support outputs. Strict clean-tree verification remains a lead admission step after the commit. The returned `candidate_read_admission: false` is correct.

## Remaining requirements

The eventual full reader must independently verify candidate eligibility, native scoring adapters and all required per-arm gates, then apply the fixed rule once. This metadata package alone does not authorize opening an archive or silently relaxing a missing input. There are no author questions for the reviewed packaging scope and no new GPU cost.
