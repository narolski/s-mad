# Paired-ranking reporting repair v2: independent-review handoff

2026-11-14; owner Sol operational contribution, at root's explicit source-only repair instruction. **IMPLEMENTATION COMPLETE / INDEPENDENT REVIEW REQUIRED. No source acceptance, collector release or scientific-read release is issued.**

## Source and scope

New folder: src/SPRINT5/paired_ranking_reader_v2/.
New source manifest SHA256: 93b2ff226ee337fe3a486e0077be0a774a5229ce28ada45b46e41d6ed3ef42f4.
Frozen baseline src/SPRINT5/paired_ranking_reader/ manifest remains02c7401529a8ca8b2a7af220f7ef36f8cbd8a71ffc50052b0a52f6e2606d1b6c, historical acceptance e1ee3a5. Baseline unchanged; copied exact manifest-listed files, not caches. BASELINE.json and SOURCE_DELTA.patch record provenance.

New reporting.py is pure descriptive reporting from already allowlisted P/C/G and unchanged point_thresholds. For both camera-derived thresholds and strict own-rule logit>0, report:
- all3arms×5seeds absolute S3-control false alarms and S4 sensitivity, counts/n/rate, overall plus existing source groups;
- calibration-camera BPCER and all119 genuine source/processing-cell flag rates, with existing metadata and denominators;
- per-seed rate differences and their five-seed means for ranking−paired BCE, paired BCE−BCE, and descriptive ranking−BCE, with both arm/comparator counts/n retained.

No new inference, endpoint choice, bootstrap draw, reduction/adoption verdict or primary decision; no D/RNG/margin/support/journal changes. S3 flags explicitly distinguished from camera BPCER. Image-row n is not represented as independent-person support. All original inference output is retained alongside operating_point_report.

ranking_statistics.py changes only an import and one return-field function call after original computations. reporting.py has no file I/O or RNG. All v2 entry points use explicit paired_ranking_reader_v2 package imports; data imports its admit relatively. A new __init__.py makes identity explicit. No legacy top-level admit/data/ranking_statistics import remains. Existing fixed journal/output locations intentionally remain reader_once_v1 and reader_output_v1: a new version must not bypass an old claim. Root must select exact reviewed source before the first authorized read.

## Verification performed

Only generated fixtures, with CUDA_VISIBLE_DEVICES empty and isolated local Python /home/narolski/mambamorph-code/.venv-spark/bin/python -I,2CPU thread caps.

- SYNTHETIC_TESTS.txt: all23 inherited tests PASS, .751s.
- REPORTING_TESTS.txt: all5 new tests PASS, latest .771s.
- New differential test runs unchanged frozen pure statistics on generated arrays versus v2 and checks exact serialized equality after removing only added report; includes a frozen-source SHA assertion. Thus all original inference results and RNG behavior match on this generated fixture.
- New field tests cover all15 identities, all119 cells, all counts/denominators, per-seed/mean differences, source-specific populations, camera threshold ties and strict>, calibration flags5/132 in the ordered fixture, uniform-shift camera invariance and visible own-rule change, deterministic report, v2 module paths/identity, and historical-role/wrong-population rejection.
- Existing loader synthetic sentinel still proves historical scores never returned, and metadata-only collector fixture uses invalid NPZ/checkpoint bytes. No real collector was invoked.
- Inherited tests show ResourceWarning for an unclosed generated floor.csv handle in unchanged data.floors; tests pass. This pre-existing warning was preserved, not expanded into unrelated I/O edits.

Commands:
```sh
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/SPRINT5/paired_ranking_reader_v2/test_synthetic.py -v
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/SPRINT5/paired_ranking_reader_v2/test_reporting.py -v
```

## Independent reviewer/root checklist

Inspect exact manifest and original/v2 delta; verify inferential code unchanged apart from reporting call; check no shadow import and no new source/runtime bypass; rerun28 generated tests; compare scope against paired_ranking/prereg.md fixed-BPCER/own-rule reporting requirement and amended IUT policy. If accepted, root records a NEW source acceptance bound to this manifest, without claiming e1ee3a5 automatically covers it. Actual metadata/scientific releases need their own reviews and source hashes. Do not run real archive roster, collector or reader as part of code review.

All15 ranking fits still pending according to reused15:10UTC heartbeat. Zero new GPU work is requested. All52 sparse genuine cells remain INCONCLUSIVE; the report does not cure support or establish operational benefit. Joint operational third contribution remains unproven; Sb frozen, NEXT NOT ADMITTED,413–417 NOT READY.

Only new v2 folder and this reader_reporting_repair packet were edited in the repair. No manuscript, baseline reader, sibling breadth/HN/tail work or original registration was changed. No Git commit/staging, scheduler action, candidate payload, checkpoint or sealed score access. Owner stops after this handoff to release capacity.
