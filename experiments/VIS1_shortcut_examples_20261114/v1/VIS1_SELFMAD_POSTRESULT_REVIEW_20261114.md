# Independent VIS1 SelfMAD technical/descriptive review — 2026-11-14

Verdicts: GO_TECHNICAL_SELFMAD_SMOKE and GO_PRIVATE_DESCRIPTIVE_NUMERIC_TRANSCRIPTION for the exact five-input pilot. Fixed A403/B403 controls are technically ready for a SEPARATE root release, irrespective of observed effect signs/magnitudes. This is not authority for this reviewer to execute them. Full three-model presentation remains incomplete until their dispositions are retained. Publication, calibrated-decision, utility and population claims remain HOLD.

Scope: root explicitly admitted this new VIS1 private result JSON for numerical/technical review. No SPRINT/NEXT/benchmark payload, scoreNPZ, checkpoint contents, source-pixel decoding/export, new inference, GPU or scheduler access. No source edits or rescore.

## Admission and reproducibility

Exact sourceSUMS a16aa9e87e634bdd635c635cb109fa10f3fe464c77be2b9e453cffb8179518aa and inventory061924577bf7762f76d3c5672c70d1017bfdc0c8c5dbbd3365c13f189f38a31b remain unchanged. Root releasefc628818b92569dd63df5689484259aaea15f5f15d10176eb68014413e36de75 binds the independent prereview5348ec99…3f0eb, prereg bd77d7eb…5fd2eb, commands90edcc31…bf5453, exact five-input private grant and SelfMAD-only model list.

Source/input initial commit734dd4ec906d773bb9d1dd46b7017b241c8dad7c is an ancestor of actual prelaunch HEAD2a1e908d656e2d248c006874b6b7a5121a86d27b. Both release and PRELAUNCH record the latter consistently. Independently compared all15prelaunch-owned files against that exact commit: byte-identical, currently clean for those paths. Thus the different commit abbreviations in the task handoff are chronology, not a source mismatch. SourceSUMS entries, prelaunch inventory/prereg/commands/review pins and input opaque byte hashes independently pass. No image decoding or checkpoint loading was required.

PRELAUNCH a4b8d455155874a37aa59cf6be48e6b6c8c3f518a6bc7c695dc206127546e690 records metadata preflightPASS, no competing GPU process, GB10idle,111920418816freebytes (>50GiB), sanitized two-thread/offline environment and exact10minute timeout command. This review checks those recorded checks, not a fresh GPU query. PID7408614717b1b96eb1302b5810e49f8542404d55f5024fd2ff8f29a5866d9204 records459460. EXECUTION_COMPLETE07f65994be3a55b40f35a5aed01bf0f6074ecf8f313ab5e088e9fa5aefcd06b2 has nativeexit0 and matching release/prelaunch hashes. stdout141d8529384433a8d4f6f4b2183852d3f105e155b23611eadae12277dfec0638 confirms completion; stderr is empty SHAe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

RESULTa0c7793f2596e6ddc6f653a0a6e971fcfb63dc6410bd8f66478ce274d12e1d7e and SHA256receipt44026324080e532e3fd730aa68fc717ef483038366dcd0f550535f90303ccf66 verified. Both hashed result/STARTED files agree with sidecar. No failed outcome is substituted or hidden.

## Independent numerical checks

Exactly five ordered unique rows match inventory and source hashes: reference00010,00042native/history,00056native/history. All logits/repeats/sigmoids/times finite. Every repeat is exactly equal, within prescribed1e−5. Reference logit−1.6904696226119995 equals the previously admitted reference exactly (absoluteerror0). Independent double-precision sigmoid recomputation matches printed float32 scores within1e−7. Both stored pair deltas exactly equal history minus native, with threshold=null and decision_flip=null throughout.

|Fixed photo|Native logit|History logit|Delta logit|Native→history uncalibrated score|
|---|---:|---:|---:|---:|
|00042|0.325929523|4.213236809|+3.887307286|0.580768645→0.985417426|
|00056|−1.534963369|−0.420897961|+1.114065409|0.177268639→0.396301895|

These are both fixed examples, not selected from a newly searched population. No operational threshold is bound; neither pair may be labelled an approved accept/reject flip. Scores are not calibrated attack probabilities, and change magnitudes do not establish a model ranking.

Runtime receipt: GB10,torch2.12.1+cu130,CUDA13.0,res384,TF32matmul/cudnnfalse,noTTA/no-grad. Load2.47820s,total2.96875s; paired-forward times0.29772,0.04885,0.04006,0.03789,0.03594s. Prelaunch-to-completion receipt span is about4.31s, consistent with the execution being well within10minutes. These measured SelfMAD timings are not estimates for another model's loading or full research run.

## Interpretation and next control release

The result supports the narrow statement that these exact existing compound-history variants increased this SelfMAD checkpoint's score. History includes prior resampling and separate alignment/cropping, not an isolated JPEG/blur/resolution intervention. Manual adult-appearing source review is not age certification or consent. Source-photo keys are not identities; person/component/training-byte/pretraining/SelfMADtraining overlap remainsUNKNOWN. Use potentially exposed descriptive development examples. Rebecca Brown/RAFFI YOUREDJIAN attribution and private scope do not settle publication/likeness rights. No attacks are present, so preserved sensitivity/utility or morph-specificity is untested. SelfMAD was chosen as the illustration model after the earlier00010pilot; retain that selection disclosure and the control outcomes.

The preregistered progression criterion was technical completion, not a large positive effect. It is met. Root may now issue separate exact ROOT_CONTROL_RELEASE granting onlyA/B, retaining the same inputs, seed403last, own-model anchor/repeat1e−5, noTTA/precision/source/threshold rules, fixed create-only outputs and10minute cap per model. Recheck current owned pins, resource/contention/storage and absence of outputs immediately before each start; do not rerun SelfMAD. Preserve both controls even if null/opposite/failure, with independent post-result review. This does not promote the pilot into population or benchmark evidence.
