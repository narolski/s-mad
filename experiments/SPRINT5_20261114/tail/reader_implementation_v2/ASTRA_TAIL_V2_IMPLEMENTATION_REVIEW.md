# Independent Astra review — tail reader v2 implementation

Verdict: HOLD_CODE_INPUT_ADMISSION pending R1 below. Statistical/diagnostic implementation and existing26tests pass; the clean-commit guard omits the actual binding file. No collector/read/scientific GO is granted. Root input-binding adoption is separately pending.

Reviewer authored the earlier diagnostic proposal, which already received a distinct independent policy review and root adoption8cd6b8e. This review assesses Sol's code against those adopted policies; it does not re-review/modify policy or self-adopt anything. No actual collector/read invocation, candidate archive/score/checkpoint/image, closed/sealed payload, GPU or scheduler access. Only source, generated fixtures and admitted metadata used. Source files remain frozen and unmodified.

## Exact reviewed pins

- v2 source manifest5ae5f48e8b5525ae53a3603f24444a0efef833c567bc52caa308fb9119fba195: all14listed files independently SHA verified.
- v2 input binding36866c220c1df69b57ca69fb271121c9704ad417e2f93358eac4398cc8e8fdfa.
- v1 source manifestd2912f78818bc32ef7164eb9bd3327fc579453b2a216347c3e5405deb536dd30 preserved.
- primary tail_stats.py65bce2a72b53efbb312265f67e99af2074d5f6ef2ae3771f7d6ad04c2f16f802 independently byte-compared identical between v1/v2.
- Primary proposal007a6fbdb25221d9069a304b5cc25a789dcf9177ef5480e7ad4201908a54d414, packet4268acf24217e26342f64f6a0294fa60ccc911489f131825d579464a9a7fbc9b, rootadoptionf18f8d1.
- Diagnostic rootadoption3c679d59e513ab3fd405f73ee164229c7914bac80cd1afc650ed824942102f17/8cd6b8e binds proposal1bd8504f… and separate review12dba40a…; verified through metadata admission.

## Blocking finding R1: input binding omitted from clean-commit checks

admission.py validate_binding(path,require_committed=True) reuses argument `path` in `for path,h in b['exact_input_pins'].items()`. Later `own=[pathlib.Path(path).relative_to(repo)]+...` uses the LAST pinned input path (diagnostics.py), not original PILOT_READER_BINDING.json. The binding itself is not in exact_input_pins. Consequently neither git ls-files nor git status checks the binding, despite the documented requirement that it be tracked and clean before collection/read. Release SHA/rootadoption checks constrain bytes but do not satisfy this missing pre-read provenance/commit gate.

Independently reproduced with actual source/admitted input metadata, mocking ONLY Git/shared-verifier subprocess calls to capture path arguments. Both `binding_in_tracked_checks` and `binding_in_status_checks` are false. Receipt ASTRA_REVIEW_REPRO.json records pins and exact omitted path. This test did not run reader/collector or create a live claim.

Required correction: retain a dedicated immutable binding_path variable at function entry; use distinct pin_path loop variable; explicitly include binding_path in both tracked and status path sets. Add generated regression tests ensuring clean tracked binding passes, untracked binding fails, and changed binding fails even when its contents have matching newly supplied release hashes. Verify the exact passed path, not only arbitrary input files. Freeze a fresh amended source manifest (do not silently change bytes under this review's pin), update dependent binding if required, and request narrow independent delta review. The inherited v1 occurrence should remain frozen; no v1 read release should bypass its known issue. A new corrected adapter can retain the SAME once journal/output.

## Independent verification completed

Ran documented isolated CPU test command with CUDA_VISIBLE_DEVICES empty and four thread limits2:26tests,0failures (0.108s). Ran metadata_only_check.py independently: PASS, no candidate arguments or payload. Reproduced exactly70positive calibration/26components,180positive evaluation/27components,288genuine rows/six cells,15expected fit plans. Bootstrap10000attempts,0redraws, design SHA54ffe7325dfbd9d1821bafbdf916f8ed5cef24aed5388a66f5295e65749d5db4. Missing af0_u5061 in all10000draws; other positive families present; no empty required genuine/calibration draws.

Fixtures cover roster/platform/source/reference/schedule rejection, threshold ties, no camera threshold substitution, joint source-component and paired-seed sampling, resampled calibration, shift invariance, no score fusion,8NI slots, exact Bonferroni bound, sparse/zero-variance/no-event inconclusive behavior, nonfinite failure, diagnostic ranks/quantiles, source proxies, no RNG advancement, primary differential, shared once paths, claim-before-payload, postclaim failure permanence, metadata collector refusing payload interpretation and trace failure checks. Passing fixtures does not establish actual15fit eligibility.

## Implementation assessment against adopted specifications

Admission/collector: all three arms×521–525 and unique archive paths/hashes/task identities enforced.100updates,batch256,25600forwards,lastcheckpoint,architecture/resolution, exact schedule/reference/source/platform/TF32 and2496reference/21277own-fit byte gates checked. Collector only interprets fixed JSON/TXT/LOG metadata; weights/NPZ/objective state inspected by regular nonempty unique member headers, no payload loading. Objective trace requires100ordered steps,finite4-vectors,expected group counts and valid occupancy/dual ranges; BCE rejects auxiliary state. Actual provenance still needs distinct collection release and independently reviewed envelopes; static/source checks are not a fit pass.

Threshold/statistics: float64 nextafter(sorted positive[floor(.10n)],−infinity) with strictgreater correctly selects below eighth score at n70 and retains tied positives. Every network recalibrates independently; six image-weighted FAR differences average five paired seed differences. Bootstrap source-sorted full evaluation components then independent calibration components then shared five seed indices matches adopted call order;10000attempts, no rejection. Pointwise FAR percentile95% descriptive; all4families×2contrasts retained,alpha.00625,margin−.02,20component minimum/zero variance correctly INCONCLUSIVE. Current10/0/17/17support forces overallINCONCLUSIVE. No winner/adoption/extra CI gate.

Diagnostics: same-source native positive pools54FERET/13components and126FRGC/14components, mixtures46/4/4 and100/13/13 exactly validated. Six genuine cells use pair denominators3780/3276; shared rank-AUC uses half ties and image weights. All15per-network AUCs,arm means and five paired effects for both contrasts emitted. Eight distributions use [.10,.50,.90,.95]float64 linear quantiles, raw and Q−originaltau, per-arm mean of per-seed quantiles, both paired contrasts. No pooled-seed quantile/AUC, calibration population or processed-positive proxy. Caveats on source mixtures, processing mismatch, component dependence and n26tail retained. NOT_ESTIMATED_DESCRIPTIVE_DIAGNOSTIC+null interval explicit; no added RNG. Differential fixture compares all primary output numerics with identical shared constants; source byte comparison independently confirms unchanged primary implementation.

Once/read boundary: v1/v2 use exact same ONCE and OUTPUT. Admission and10000metadata-only design checks precede claim. Shared Journal uses O_EXCL/fsync; only afterward payload reads/hash-validates exact own-fit/dev NPZ, checks full ordered manifest/finiteness/byte agreement under existing parent opaque-byte-gate ruling, returns only538allowed IDs. Shared atomic_result hard-link refuses overwrite; any postclaim exception writes permanent FAILED. No CLI alternate journal/output or automatic rerun. Actual fullpack equality permission is not scientific permission for historical/auxiliary rows.

Baseline/camera: no baseline408 score member or camera panel opened/implemented. Current result says HOLD_SEPARATE_SCORE_MEMBER_ID_BINDING_REQUIRED and HOLD_NOT_READ, README explains baseline is required. Nonblocking reporting recommendation: result-facing baseline label should explicitly preserve adopted REQUIRED_BUT_HOLD_PENDING_SEPARATE_BINDING_AND_ADMISSION, or a companion required=true field, so consumers do not mistake it for optional omission. Do not edit byte-frozen primary tail_stats merely for this; a reviewed output annotation can preserve required status without numeric changes.

## Next step

Sol fixes only R1 in fresh source revision, adds regression fixture, regenerates exact pins/necessary binding and hands off narrow delta. Root separately reviews/adopts corrected input binding; distinct metadata-collection release, actual15fit admission, collector review and GO_READER_READ remain mandatory. Public/scientific read remains HOLD throughout. No change to primary90%FAR,8NI guards, diagnostic adopted policy or auxiliary scope is requested.
