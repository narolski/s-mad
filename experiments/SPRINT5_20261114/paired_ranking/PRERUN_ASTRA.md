# Independent prereview: paired ranking sprint, 14 November2026

Verdict: HOLD dispatch pending smoke-safety fixes below; scientific three-arm intervention is suitable for a bounded smoke after fixes. Production and candidate read remain HOLD. This review is independent of Sol's implementation; no candidate payload was opened and no remote file changed.

Scope read: prereg.md; paired.py; patch_train.py; run.sh; battery.sh; config.json; check_cpu.py; CPU_PLAN_SMOKE.json; original FS1 train.py and common.py on gx10. Original trainer SHA256 cbb2cbd1b9a3eb59ab080a540a98aab0f6ead51ea69364d2debe06a984b8c1c5 verified. Source patch's indexed dataset aligns with FS1 for x,y,idx loop; ranking derivative increases positive and decreases negative logit. Observed CPU report shows exact row-index multiset across arms for all5seeds and identical paired schedules. This report was inspected, not independently rerun yet.

## Before bounded GPU smoke

1. Preserve failure evidence via EXIT trap: durable unique failure archive containing task/env/config/source receipt, stage/status, traceback/logs and available metadata even if train/scorer exits early. Existing set-e exits before archive; FORCE_RM_TMPDIR would erase evidence. Never call failed tar successful/eligible, never overwrite prior evidence. Signals/timeouts need best-effort trap plus scheduler receipt; SIGKILL cannot be guaranteed recoverable.
2. Enforce mode: smoke exactly2steps, no production task/output collision. Production must be hard-disabled until structured pinned GO receipt binds exact source digest, admitted seed audit and all3smoke hashes; existence of any file is not a receipt gate. Also guard existing-output early exit with expected mode/steps/source/task identity, not only SHA integrity.
3. Resolve scoring scope BEFORE invocation: prereg says only100development hosts and no191-host test read, but full ab1_eval scorer scores all rows. An opaque score is still candidate scoring. Filter permitted metadata manifest before scorer and align battery gate, or obtain an explicit applicable access ruling from lead and amend wording. Do not silently convert “no read” into “score everything opaquely.” Inspect trainer val10 behavior: FS1 train90 branch invokes train_items(val10); assert zero rows for this d0 pack or suppress that branch in pinned sprint patch. Avoid prohibited scores appearing in logs/meta.
4. CPU rank gradient and no-pair tests plus actual2-step schedule pair-count audit: smoke must contain rank pairs; log finite BCE, rank loss and count, nonzero gradient direction, not merely total loss. Record actual GPU model/software and exact smoke command. Source SHA256SUMS must exist and verify after final fixes.

These fixes are small, bounded and do not require changing the scientific question. Smoke can precede calibration/floor/reader completion because it is infrastructure only, provided no forbidden scoring and no output interpretation.

## Before production fits/read

5. Seed501–505 provenance audit admitted; no reuse for current NEXT413–417. Keep smoke vs production separate. Pin exact D, population/component, calibration files and count/power feasibility before production as prereg promises. Insufficient populations cannot be repaired after seeing candidate outcomes.
6. Source checks alone do not validate source/population provenance. pair_key's path substitution is acceptable only with manifest assertion that each paired key has exactly one actual person/host/processing identity, labels correct, partners eligible and no cross-split components. Save pair manifest and hashes. Paired sampling is the intervention control; baseline composition per batch may differ and is acknowledged.
7. Simultaneous guards are unspecified: two contrast97.5% CIs do not cover many source/processing FPR checks plus detection NI. Enumerate guard family and predeclare max-stat/bootstrap or Bonferroni rule before scores. Count calibration/heldout genuine identities and achievable CI width. If insufficient to establish2percentage-point NI, adoption is inconclusive by rule, not negative evidence of ranking effect. Primary optimization gain can still be reported separately. Fixed calibration quantile must state exact order statistic/tie rule and calibration uncertainty treatment; bootstrap calibration components as well if inference includes estimated threshold.
8. Training five seeds with one population supports limited seed inference; crossed component/seed bootstrap is defensible descriptive uncertainty, not robust confirmation with only5seeds. Retain all seed effects. Need source-stratified graph components and D assignments pinned independently of candidate logits. Floors must use identical sample/stratum weighting and shared bootstrap for model-minus-floor.
9. Production output currently declares runtime15–25H100h from historic allocation, not measured sprint evidence; keep qualified. Actual fit and full battery smoke elapsed time constrain walltime;2steps alone cannot extrapolate long-run throughput reliably. No scheduler command was reviewed here.

## Reviewed file snapshot SHA256 (pre-fix, invalidated by changes)

- prereg.md 89a72f90d9df87c3d8bc71eeda9f2335b7c942c6b7e79d75f3c9c026b7b9f364
- paired.py 34ea25e01672e1557612a53e780d3cc77a12b9bb5cec4f69bd1ceaed4cd1ed99
- patch_train.py 6b92a81b81a22300737b3b15565bf3e00e3abf39978714b3383bc29788fe3229
- run.sh f01dfcd645d0e29679ad1552f91862961911a7c2d455eed7a6f896093c604cca
- battery.sh 33c7913e4e30256f94b55b4f12da32e19ef924c891c61ac260839836fda5dbac
- config.json 816e9e8d4367090b5fe50648093896775b422f37ccc4dda6e2c6793bd1d735b3
- check_cpu.py 62fbc04cfa348270e51f5503b4960a7c70e4567d4352a085155e41049eba6681

No positive scientific result, full production GO, benchmark authorization or eventual method selection follows from this prereview.

## Follow-up observed before final pin receipt

Independently copied paired.py and train_Sb.csv metadata to local workspace and reran all15 full6250step plans: exact exposure equality PASS; paired schedules identical. Seed501first2paired batches contain5and4matched hosts, so actual2step smoke does exercise ranking.

Lead explicitly confirmed prospective permission to score ONLY exact existing admitted AB1/battery allowlisted rows (including historical191hosts) opaquely for path/bytegate and durable output. NO scientific191read or external/sealed rows. This resolves scope item3 once amended and runtime allowlist/val10 checks pinned. Lead also clarified normal lem-gpu-short sbatch is allowed; interactive mode requires srun --pty. Earlier blanket no-sbatch wording in design handoff is superseded.

Observed revised source implements strict2step smoke namespace, EXIT failure tar, durable worker log, and production JSON receipt binding source sum digest and3smoke archives. Production reviewhash is only checked as64character string, not actualfile hash, and existing-output eligibility remains incomplete: these stay production blockers, not first-namespace smoke blockers. Final source checksums pending; no GO issued yet.

## Final bounded disposition: GO_SMOKE, production HOLD

Final source manifest SHA256 independently verified with sha256sum -c:162b2846eed036aecae33adf3cb973abaa4dfdc5db5940ea01db02906df2f8ae. Reviewed prereg SHA2565fac669a61cd9af1290dc50b73bf26715af460ad6503b1fecbbf9c98a6db0c6d. Metadata audit8dbac7c9b063c6bbdfd458056b2cf356ac0eb1f575dcb5eefe9da80f838b4d2b. CPU image/gradient report58da9cde8c1db80f09b4fd955df93e0fe46a1ae3d3e44acb12af2a0cac8b845d. bash -n passed run/worker/battery scripts. Actual corrected source has zero-val10 assertion before training, rankcount/loss logs, exact train/eval hashes, pinned battery packs, strict smoke namespace, failure archives, and no silent existing-output reuse. Production checker now hashes actual review and seed-audit files.

GO only for ONE bounded H100 smoke, seed501, all3arms, exactly2optimizer steps each, full existing admitted AB1/battery opaque scorer and mandatory bytegate, worker.sh smoke. Parent's prospective exact-row permission recorded in prereg. No candidate metric interpretation, no191-host scientific read, no other/sealed dataset, no production receipt creation from this GO. Lead alone stages/commits exact package and dispatches under actual scheduler/lock rules. Source changes invalidate this pin and need delta review. Preserve successful AND failed smoke evidence; any failure requires diagnosis and recorded disposition before retry.

Production remains HOLD for full smoke outcome/bytegate admission, fresh-seed allocation binding, exact component/D/floor/calibration inputs, explicit guard multiplicity and precision, and independently reviewed fail-closed reader/release. Fixed scientific margins cannot be relaxed because calibration proves too small. GO_SMOKE is not GO_PRODUCTION and is not a scientific result.
