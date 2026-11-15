# Independent narrow delta review: tail v2r1

Decision: GO_CODE_INPUT_FOR_ROOT_ADOPTION; R1 CLOSED for exact pins below. This is not root adoption, metadata-collection release, actual15fit eligibility, reader/scientific release, baseline admission or camera admission. Those gates remain HOLD. Earlier v2 remains frozen with its known R1 defect and is not retrospectively released.

Reviewer: Astra, independent of Sol implementation author; originally identified R1. Scope only repair/delta against reviewed v2, not reapproval or alteration of adopted policy. No actual candidate archive/logit/checkpoint/payload, collector/reader invocation, GPU, scheduler or WCSS access. Files created only for this independent review/receipt; author sources/evidence unchanged.

## Exact pins

- New source manifest943d47ef9ac0638c46dc1fdaf65782cabbd43d93405ce80305c4bac58c1fce5b.
- New input bindingff2aa74853658d1d318725e42eedbdd2ac16cde8d7da57971c04e4447626c6a2.
- EXACT_DELTA.patch37e4894613ab6855f6c8fbd76efb7f7bd569dfdb0690e7a411252aefb7c53e56.
- Compared frozen v2 manifest5ae5f48e8b5525ae53a3603f24444a0efef833c567bc52caa308fb9119fba195 and binding36866c220c1df69b57ca69fb271121c9704ad417e2f93358eac4398cc8e8fdfa.
- Independent test/capture receipt ASTRA_R1_DELTA_TEST_RECEIPT.json SHA2560f72c8ab9ddf8a77b0e76f6ad042753bbec5beb42225a91d468ef7c7d69e0c6d.

All new manifest source hashes independently verified. Recomputed unified diff from actual old/new file bytes and compared byte-for-byte to delivered EXACT_DELTA.patch: exact match. Changed source files only admission.py, policy.py/prepare_inputs.py revision pointers, read.py output annotation, tests and two documentation files. Binding changes only expected_plans_path, draw_metadata_path and exact_input_pins for this revision; semantic policy/population parameters unchanged.

## R1 correction: PASS

validate_binding resolves original argument once into binding_path; pin verification uses distinct pin_path, so no argument shadowing remains. committed_paths includes actual binding FIRST, followed by pinned repository inputs and manifest-listed code. require_clean_committed uses that same complete path list for both git ls-files --error-unmatch and git status --porcelain. Matching release hashes cannot replace this independent tracked/clean requirement.

Independently reran28synthetic tests (0.139s, all PASS), including real temporary-Git repository regression: clean tracked binding accepted, dirty tracked binding rejected, untracked binding rejected while other pins remain clean. Production-wiring regression verifies original dedicated binding argument reaches helper.

Independently repeated actual admitted metadata validate_binding(require_committed=True), mocking only subprocess execution to capture its Git/shared-verifier arguments without requiring root to commit the not-yet-adopted revision.109tracked path checks; actual new PILOT_READER_BINDING.json is first and also present in git-status arguments. This confirms original reproducer now passes. The capture is not a claim the production tree is already committed/clean; live release must actually enforce those checks after root commit/adoption.

## Delta invariants: PASS

Independently byte-compared tail_stats.py, diagnostics.py, collector.py, payload.py, shared.py and tail_inputs.py: all unchanged from frozen v2. Thus no change to primary90%positive calibration, six FAR cells,8NI guards, point-only diagnostics, RNG call order, payload allowlist or collector behavior.

Independent metadata-only check:70calibration positives/26components,180held-out positives,288genuine rows,15fit plans;10000attempts/zero redraws; design hash54ffe7325dfbd9d1821bafbdf916f8ed5cef24aed5388a66f5295e65749d5db4 unchanged. Missing AF0-s61 persists in all10000draws and component support10/0/17/17 still prevents overall NI utility claim. Native-positive diagnostic pools54FERET/126FRGC unchanged.

AST-compared ONCE/OUTPUT constants across v1,v2,v2r1: identical. No additional once path/output or second-read mechanism introduced. Claim-before-payload logic unchanged. read.py adds only result-facing baseline label REQUIRED_BUT_HOLD_PENDING_SEPARATE_BINDING_AND_ADMISSION after statistics/diagnostics, leaving frozen stats bytes and numeric results untouched. This closes the prior nonblocking reporting recommendation without opening baseline scores. Camera remains HOLD.

## Root handoff

Root may adopt/commit exact corrected code/input binding after its own pin checks. A distinct metadata-collection release, complete independently reviewed15fit envelopes and separate GO_READER_READ are still required; same permanent once journal applies to every revision. Actual baseline score-member/ID binding and camera provenance remain separately required. No remaining R1 correction requested for these exact bytes; future source changes require new hash-bound delta review.
