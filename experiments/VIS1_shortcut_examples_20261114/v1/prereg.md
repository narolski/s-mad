# VIS1 v1 — actual same-photo processing response, prospective private pilot

Status: PREPARED; independent code/methodology review and root execution release REQUIRED before any GPU/model inference. This is a new exact private research scope, not automatic extension of XAI00010 permission. No benchmark or candidate-selection read. Main/WIP untouched; layers/probes are explicitly deferred.

## Fixed estimand and cases before scores

Show two adult-appearing real photographs, FFHQ00042 and00056, each as its exact existing aligned native PNG and exact existing landmark_complete resolution-history PNG. Canonical PN1 development IDs are fq005006/7 andfq005012/13 (hn2), whose source bytes match exactly. They are not newly added still-sealed benchmark inputs. One separately admitted existing reference00010native reproduces numerical stack identity; it is not a publication candidate or new primary result.

Manual original-photo inspection:00042 has full beard/glasses and appears adult;00056 has visible facial stubble and appears adult. No actual age/consent metadata exists in the checked records; no documented-adulthood claim. The licence identifies Rebecca Brown/00042 and RAFFI YOUREDJIAN/00056, both CC BY-NC2.0. Private noncommercial research is proposed; root must explicitly bind it. Publication/likeness/consent review remains separate. No FERET pixels exported.

Cases fixed as first two additional lexicographic attributed genuine keys after original00010; no score selection. SelfMAD is the primary demonstration model selected after observing its earlier00010 response; explicitly post-hoc illustrative model choice. Required supporting controls A403 andB403 retain all outcomes, whether they change or not. No seed/model/photo substitution, no superiority or prevalence inference. Readable images plus measured responses are the communication goal; no heatmap or layer hypothesis is required to produce it.

## Exact operation history

No image is generated or modified by this package. prep_ffhqm.py217–235 documents the existing E7 path: original1024px source is downsampled with prep_eval.degradeR/INTER_AREA to the landmark_complete median inter-eye scale if required, THEN independently aligned to512px; native path is aligned without that initial shrink. Both exact aligned PNGs then receive unchanged ImageItems224px (A/B) or384px (SelfMAD), PILbilinear/RGB[0,1]. Thus the contrast combines resampling and realignment, not “onlyblur”, “onlyJPEG”, identicalcrop or a pure causal resolution effect. INPUT_AUDIT pins exact per-photo source scale/preIED/border metadata. No new alignment/encoding/occlusion is executed.

## Outcomes and controls

Each model runs all five fixedinputs individually, noTTA, float32/noAMP/TF32off, two consecutive no-grad forwards. Primary numerical outputs: every per-image attack logit and uncalibratedsigmoid, each pairΔlogit. Threshold=null anddecision_flip=null unconditionally; no arbitrary0.5 decisionrule. No confidence intervals, hypothesis verdict, bestcase/seed choice, population estimate or benchmark effect. Retain zeros, negative and opposite responses, failures and the other models. A positive/negative actual attack is absent, so this genuine-only pilot cannot establish utility or preserved attack sensitivity. Reference00010 is a numerical-reproduction control only; repeatedforward is a no-op control.

All proposednewinputkeys map toexisting PN1 development rows; training manifestsA/B checked for exact path/explicitFFHQkeymatches: none. They contain FERET/FRGC/SMDD-labelled constructions, not an identity census. Entire training-image-byte comparison, cross-dataset person/component overlap, pretraining and originalSelfMADtraining overlap remainUNKNOWN. Label as potentially exposed descriptive development examples; do not call person-disjoint/unseen/newbenchmark evidence.

## Technical gates

Exactinventory_v2 hash, source/weight/input hashes, fixedmodelroster, Python/packageversions androotreviewrelease. GPU must be NVIDIA GB10 on the original local stack; CPU/H100/A100 fallback refused. Ownmodels use unchanged XAI build_run_model/strict trainablekeyset accounting, fixedseed403last plus frozenCLIPbase; SelfMAD uses exact releasedHRNetW18 state, adapter andclasses2/morphindex1. Original published own-croppipeline is NOT used; this is existing aligned-frame protocol.

Reference00010 must match its already admitted noTTA logit for each model within1e-5. Two repeats perinput must agree within1e-5, finite throughout; no relaxation/retry after results. Any mismatch is technical failure, preserve partialSTARTED/FAILED, do not interpret new scores. Input/source/model pins must match; no download. Alloutputs go to fixed create-only /mnt/t7/smad_next/VIS1/20261114/v1/<model>. No overwritten/cycled namespace, auto-retry, model save or source-pixel export. Failure/timeout stays explicit; successful forward is not explanation-faithfulness proof.

## Source grounding and precision

Grounding skill was read and load_archive/check_grounding attempted: no dedicated model-provenance archive exists locally, so its mechanical check cannot certify this model. APIs and values were instead taken directly from the existing checksum-bound XAI FP32 runner, common.ImageItems/build_run_model/forward_logit and a12_released load/build/adapt/head functions. These source files and checkpoints are bound from the already verified XAI inventory; no API or Hub ID is recalled from memory or newly downloaded. The mechanical archive check remains unavailable, not a PASS. Independent reviewer must inspect exact source reuse.

Original XAI result recorded local NVIDIA GB10/Python3.12.3/torch2.12.1+cu130/numpy1.26.4; installedversion metadata also binds torchvision0.27.1+cu130,timm1.0.27,Pillow12.2.0,safetensors0.8.0. This is NOT cluster2.11+cu128. cudnnbenchmark/deterministicFalse are fixed explicitly for this new pilot; the old runner did not log those two flags, so their historical equality is not independently established. Reproductionanchor gates compatibility before newdata interpretation. No gradients/historicalTF32/TTA scores are computed; no claim of reproducing previous gradientgates.

## Resources, timing and stop

Localgx10 only, oneGB10, oneprocess/model, CPUthreads2, no rental/cluster scheduler. First exactSelfMAD command is the bounded smoke and its same scored outputs are retained, not rerun as a second smoke. Parent verifies GPUcontention/freeRAM and>=50GiBT7 reserve first. Fixedwalllimit10min forSelfMAD; eachA/Bcontrol also10minlimit. Estimate1–5min/model includingload for10batch1forwards; NOT measured, do not promise. Record load_seconds, perinput seconds_two_forwards andtotal_seconds fromsuccessfulRESULT without choosing examples fromscores. Nativeexit/timeoutstdout andstderrcopiedto/logs; timeout with onlySTARTED isINCONCLUSIVE notPASSED. No killing others orautomaticretry. Root may releaseA/B afterSelfMADtechnicalpass andmetadata/timingreview, irrespectiveofsize/direction ofSelfMADeffect; allthree models required for fullpilotpresentation.

## Review/execution/result gates

Source/scalarfixtures andmetadata-onlypreflight may run now (completed7testsPASS). GPUcommands inCOMMANDS.md require independentpre-review +root exactGO_VIS1_SCORE_ONLY release, committedsource/inputpins andfreshoutput/duplicatecheck. The author never executes GPU. Afterrun root verifies durablehashes/completeallmodeldispositions; independent reviewer checksnumericcopy, interpretation, andactualprint/private-rights scope beforedisplay. Newpublicationclearance is not granted bysource tests. Alllimitations remain visible if response is small or opposite.
