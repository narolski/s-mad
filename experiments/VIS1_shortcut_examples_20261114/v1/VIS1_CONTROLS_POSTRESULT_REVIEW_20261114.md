# Independent VIS1 fixed-controls post-result review — 2026-11-14

Verdict: GO_TECHNICAL_ALL_THREE_FIXED_MODELS; GO_PRIVATE_DESCRIPTIVE_NUMERIC_PRESENTATION for the complete fixed six-pair comparison below. No population/utility/causal-mechanism, operational-decision or publication GO. No repeat/scorer/GPU action is requested or authorized by this review.

## Scope and admission

Root explicitly admitted only these private VIS1 JSON results and execution receipts. Reviewed A/B controls under separate ROOT_CONTROL_RELEASE SHAa34363e88425edd455a5bd04c0f7c05397a5d43576bfd185eec9c6944e6e050d, models exactly[A,B], private five-input grant and prerequisite technical reviewfd1c5caf6f2078adf545e91564ba71ff31f75c3bab14fc6cd785d45892431ab4. CONTROL_RELEASE_RECEIPTfd9320914fdaffd008b0ec995d408fb50829d85e596dbd6857389451e2bcf398 agrees with that release. A/B were fixed in preregistration before these results and released together based on technical SelfMAD validity, explicitly irrespective of its effect sign. Both controls completed; no model/seed/case was substituted.

Inventory061924577bf7762f76d3c5672c70d1017bfdc0c8c5dbbd3365c13f189f38a31b and sourceSUMSa16aa9e87e634bdd635c635cb109fa10f3fe464c77be2b9e453cffb8179518aa are unchanged. Independently compared all15owned files in each control prelaunch against both current prelaunch commitac2b2c908232fecef1cd23a207ffae2fc026f989 and release-bound2a1e908d656e2d248c006874b6b7a5121a86d27b: byte-identical and owned paths clean. Commit progression therefore does not alter reviewed code/inputs. No checkpoint or source image decoding occurred.

A PRELAUNCH8217a92547873dcb35304cca340174b4859b99e6271c4b87885c8643e5feb822 and B PRELAUNCH146c9d2ca5d3a4bda0d3a6c71b1f728a43e0789baec421581be921954ace750e record separate fixed10minute commands, two-thread/offline environment, source/input pins, metadata preflightPASS, idleGB10/no competingGPU process and private scope. Aggregate EXECUTION_COMPLETE075fc2b08a273ac13b22d787489a0f436b4bcda7b52fac86dea91573efeabc84 and individual completions report nativeexit0 for each. These are recorded prelaunch checks, not fresh GPU queries by this reviewer.

## Exact outputs and numerical verification

- SelfMAD RESULTa0c7793f2596e6ddc6f653a0a6e971fcfb63dc6410bd8f66478ce274d12e1d7e, SHAreceipt44026324080e532e3fd730aa68fc717ef483038366dcd0f550535f90303ccf66: unchanged from prior review, no new SelfMAD run required.
- A RESULT18c46b3d3fced82f6162bcd2a5542601a72a08739675aa7b0421e1d82fa5bc62, SHAreceiptf539dd649fec5abe5df6b82ada54948e061a3354eae525c41926fd2b232bef88.
- B RESULT35fa6ad2f0a74c152ca8b8437d543942c06a51423fc15c0393fe90898d456214, SHAreceipt814f4de5cdfe9a4a29e6b4468739cd5b30dcdacfba3a969563d1ce6770741b11.

Independently verified all sidecar-listed RESULT/STARTED hashes, threeCOMPLETE dispositions, all15ordered rows and exact inventory IDs/input hashes, all six pair deltas and null threshold/decision_flip fields. All logits/repeats/sigmoids/times are finite. Every one of15repeat differences is exactly0; all three reference errors are exactly0, satisfying1e−5. Independent sigmoid recalculation agrees within1e−7. Reference logits: SelfMAD−1.6904696226119995,A−3.5239243507385254,B−3.3419947624206543. No input, seed or sign was dropped.

Private presentation values; delta=history−native, model-specific logit units:

|Model|Fixed photo|Native logit|History logit|Delta logit|
|---|---|---:|---:|---:|
|SelfMAD|00042|0.325929523|4.213236809|+3.887307286|
|SelfMAD|00056|−1.534963369|−0.420897961|+1.114065409|
|A403|00042|−3.381847382|−3.518363476|−0.136516094|
|A403|00056|−3.431549549|−3.467275381|−0.035725832|
|B403|00042|−3.099207878|−3.383016109|−0.283808231|
|B403|00056|−3.375004053|−3.465831041|−0.090826988|

All four control changes are negative and retained alongside the two positive SelfMAD changes. This is a description of these exact checkpoints/inputs, not a cross-model robustness ranking. Sigmoid values are uncalibrated model scores; null operational threshold is binding. Neither arbitrary0.5 crossing nor absence thereof establishes an operational false alarm or correct decision.

Measured load/total seconds: SelfMAD2.47820/2.96875,A3.08313/3.51372,B3.23770/3.66676. All remain within fixed10minute budgets. Receipts report sameGB10,torch2.12.1+cu130,CUDA13.0,noTTA/no-grad/TF32off; SelfMAD384px versus A/B224px is the registered model-specific loader difference, not an isolated architecture comparison. No training update or source-pixel output occurred.

## Permitted private explanation and remaining limits

The useful plain-language finding is: “For these two fixed photographs, the same existing processing-history change raised SelfMAD's score and slightly lowered both fixed control models' scores.” Keep the actual values and all three dispositions with that statement. Do not say that A/B are generally robust, that SelfMAD uses only blur, or that attack sensitivity is preserved. No attack example or population sampling supports those claims.

History combines resampling and separate alignment/cropping; it is not a pure JPEG/blur/resolution experiment. SelfMAD was selected as the demonstration model after the earlier00010response, and this post-hoc model-choice disclosure remains. These two added cases were fixed before their new scores. Unknown cross-dataset person/component/fulltrainbyte/pretraining overlap means potentially exposed descriptive development examples, not unseen/person-disjoint data. Manual adult-appearing review is not an age certificate or consent. Recorded author attribution/private noncommercial scope does not resolve publication/likeness rights.

Root may release these exact numerical cases to the private preview author under existing private input grant, retaining all six rows and source-history/uncalibrated-score/counterexample caveats. Any new face-containing render still needs its own input-scope/layout check; this review exports no pixels and grants no public redistribution. Main/WIP and final publication remain unchanged/HOLD. No SPRINT/NEXT/benchmark payload, scoreNPZ, model checkpoint, GPU, scheduler or new inference was accessed.
