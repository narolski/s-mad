# NEXT v3 — bounded metadata-only closeout po RZ1 15/15

Obserwacja: 14 listopada 2026, ok. 19:48 CET. Repo snapshot HEAD `c67fd5dc00012648012878a4b571cdbb54e42fda` (inne workstreamy mogą później dopisywać commity). Status: **HOLD — final admission nie istnieje; selection/confirmation nie uruchomione**. To uaktualnienie `SOL_TRAINING_PROTOCOL.md`, nie nowa polityka lub eksperyment. Przeczytano AGENTS/CONTINUE, bieżące WORKSTREAMS/NOTEBOOK, approved v3, bieżące źródła i ostatni niezależny native review. Żadnych challenger tar members, NPZ, checkpointów, sealed scores, scientific readers/preflight/claims, GPU, query klastrów lub job mutations. Nie zmieniono prereg, source ani istniejących receipts. Zakres koordynowano z sol_sprint_experiments: jego SPRINT35/piloty i baseline auxiliary są oddzielne; nie ma nowszych W2/RZ1R receipts od niego.

## Najkrótsza ścieżka i co się rzeczywiście zamknęło

1. **Zamknięte:** wszystkie 15 RZ1 512 fitów A512/Sb512/SbMR512 ×408–412 mają opaque durable arrival; pięć candidate Sb512 oraz A512 control nie czekają już na trening. Root wykonał świeży hash inventory w `ROOT_RZ1_FIFTEEN_OPAQUE_ARRIVAL_VERIFIED_20261114.json` (SHA256 `e8baeeec16009f464eb85b81e81145058e9c560bda64f654fc793153eed375ba`). To arrival, nie fit/kernel eligibility.
2. **Zamknięte:** E3 freeze commit `b11a8c9`, `seed_mode_L.json` SHA256 `a46b407a7815a54f7609a666c5d5568df09dfe7f2229e8366a3f39ee14c344f2`: five403–407,15source hashes; frozen_at16:11:40 local. Nie wykonywać freeze ponownie. Nie zamieniać tego czasu bez timezone na `verified_at` — stosować oryginalne czasowe collection evidence.
3. **Zamknięte:** SbFM supplement durable: `AB1FMSUPP_20261114.tar`,51363840bytes, SHA256 `e4c815d952b07fdc964eb3991c82ecbdf0712ecce097539e0ec01db679eb704a`. Receipt `sbfm_collection_20261114T160056Z/COLLECTION_VERIFIED.json`, SHA256 `c9a42704ea348b0f4f6275f0edaa9e35025ec99631f1910011ede398cef7511f`, observed_at16:02:17.481001Z. Stare `durable_output_verified:false` w COMPUTE_QUEUE nie unieważnia konkretnego receipt; nie kopiować tego niespójnego booleana do admission.
4. **Teraz:** root powinien zebrać opaquely **istniejące** BB2LW2 (6319264) i RZ1R (6319491), nie submit/replay. Oba jobs ostatnio zapisane COMPLETED/0:0:13:07:42 i13:46:15CET. W odczytanym coordination inventory nie znalazłem final W2 ani nowych RZ1R collection receipts. Brak dowodu arrival nie oznacza braku outputu na WCSS.
5. **Równolegle zeroGPU:** znormalizować istniejące arrival records, source inventories, role maps i complete pin closure; rozwiązać wprost Sbc scope oraz SbMR512 kernel prerequisite i GX registered prerequisites. Dopiero exact independent admission review i clean committed checkout pozwolą na metadata-only preflight. Nie ustawiać `batch_closed:true` tylko dlatego, że RZ1 jest kompletne.

Cutoff bez zmiany: **15 listopada 2026,18:00CET =17:00Z**, wymagane fit/rescore tars landed+hash verified. Sam read może nastąpić później. Kolejność ośmiu arms, rows, margins i seeds pozostają v3. Wyniki SPRINT5 nie zmieniają NEXT ani Sb default.

## Source/review/input closure — aktualne, bez nowej polityki

| Element | Zweryfikowany pin / stan |
|---|---|
| Binding approval | `dbeb940`; v3 SHA256 `5188ad9a696d86c935191a4fd45bee0f0762186c199a5bbd7d8368e87bf62667` |
| Selector | `src/NEXT/read_selection.py` SHA256 `f20f42578275aa3d92b8c695ab86827a526b7f62016b98ec242bf17c0b390830` |
| Native adapters | `src/NEXT/native_adapters.py` SHA256 `ebb40edda27a08034a6087a737109509e65c3c5ad76c748767cd19a49f2ff17c` |
| Latest independent review | `experiments/reviews/PRERUN_NEXT_NATIVE_OPENCODE_20261114.md` SHA256 `085a2a2b6ed371c6d244b9f3085e53940a539bec42aa3ca706667d4a510a8f73`; appended Independent F1 recheck supersedes initial CHANGES REQUIRED:42synthetic tests PASS, GO-for-commit only; incorporated `78490ba` |
| Common input pins | SHA256 `24725bb96179ab07363abf2c1f0e77cb8720ebb28550dae0cb3e18ad4d9e4259`; fresh root-based `sha256sum -c`44/44PASS |
| Support pins | SHA256 `5e8d39f02345b39755ffbcd13def8af26a1be057e15f7499d7d5649784c2b02a`; fresh20/20PASS |
| Scoped Git state | Selector/native/seedmode tracked bytes clean; two OPENCODE_ADMISSION_READINESS files untracked. Shared worktree is NOT final clean admission checkout |
| Final admission / journals | Canonical `experiments/NEXT_method-selection-rule/ADMISSION.json` absent; selection_rule_v3_once and confirmation_rule_v3_once absent at observed paths |

Inputs/floors were hashed, not interpreted/recomputed. Historical input clean-checkout receipts076a5f9/8d00996 remain evidence; final receipt/source inventory/review pins still require a clean exact checkout. Current native code already supports SbFM and DINO E3; initial READER.md “not implemented” paragraph is superseded by actual sources and appended native review. Four observed DINO candidates supported against **all five** fixed comparator networks; failure denominator stays5. Missing comparator cannot become a four-comparator mean.

## Wszystkie osiem arms — fixed order, żadnych nowych exclusions

| Arm | Arrival/source | Adapter / roles | Remaining blocker; nature |
|---|---|---|---|
|1 SbFM|Five original recovered fits; final supplement now durable|Integrated native fit+supplement, original AB1 Sb408–412 paired comparator, AB1 A control; candidate/comparator border rows from SAME supplement; own trainSbFM transfer already pinned|Bind exact submitted config/source manifests/inventory/producer+receipt and exposure/eligibility review. H-fm3 and native gates assessed only in admitted read. Administrative/source closure; no new training indicated|
|2 GX|20generation tasks recorded complete; admitted image/train assets and fits not established|No invented output schema/adapter; strict complete-five requirement; comparatorAB1Sb|Existing registered image/identity admission→GX/GXp manifests→prefit floor/transfer→amendment2 producer/smoke→10fits/support remains. This is implementation+registered scientific prerequisites, not automatic ineligible. No new method design needed to start existing admission sequence; no fit command ready in current sources|
|3 SbMR|Five wave1 candidates/Sb0/A0 previously recovered; pending final RZ1R arrival closure|rz1_fit/refit; comparatorSb0, plainA0, AB1Sb refit yardstick|Collect6319491, source/time/role pins. Both nine training and four heldout kernel tests already required; retain outcomes/failures|
|4 SbM|Same wave1/common receipts|Same correct roles|Same RZ1R closure and both kernel criteria; no changed comparator|
|5 Sb512|FiveSb512+fiveA512 now fully durable|rz1_fit/refit; comparatorSb0, controlA512, AB1Sb yardstick|Collect6319491+final admission.512frames availability already documented; no need open sealed data|
|6 SbMR512|Five final fits fully durable|Current selector explicit refusal at line469 because no registered cross table/complete adapter|v3§3 item6 and§5(e) explicitly cannot qualify without preread kernel test. Find existing registration if root has one, otherwise prospective permitted kernel-registration/review+actual scoring/adapter needed, or authoritative disposition for unmet registered prerequisite. **Not** cost-drop (it was run), **not** prebinding-ablation, **not** software-gap exclusion|
|7 Sbc|Five wave2a crop fits previously recovered|rz1_fit/refit; controlA0 notAc; selector requires pinned crop_scope_ruling|Exact author scope ruling still not found in inspected source. v3§9row7/§12q4; RZ1M7: lead approved224crop, author interpretation asked. Supply existing explicit author ruling or resolve narrow scope; implementation cannot answer it. Also RZ1R closure|
|8 DINOv3E3|15BB2L original fit source hashes frozenb11a8c9; finalW2 durable not established|Integrated unpaired: E3Sb403–407 minus fixed fiveAB1Sb408–412 mean; E3Acontrol andBfitguard; W2 common supplemental rows|Collect6319264; bind producer/ms1 full manifest/fit inventories/seedmode/receipt. Native gate and E3adequacy/splice guard remain unexamined, not passed by scheduler completion|

SbFM transfer file is already `inputs/floors/transfer_SbFM_rows.csv`, SHA256 `50de9a543c4d8aaa9c4ccb2e229369c82026d05285717d7832fee55b73817aa5`; not a missing computation. No replacing its training-list learner with Sb. RZ1 transfer scope for on-the-fly resize remains qualified as v3 says.

## Exact opaque collection package for root — no job replay

Remote root `G=/lustre/pd03/hpc-narolski-1790461090/smad-next`.

**W2 registered producer:** `src/BB2/wcss/bb2l_w2.sbatch`, SHA256 `b44834782a552ab87c66518fa90563ce804963f763b2c54d0b6642d3120db507`; defaults lines31–32 `R=$G/results/BB2L`, `OUTN=BB2LW2`; source lines119–122 produce tar+sidecar. Job6319264 is the already-submitted recovery W2, not original6315676. Receipt/history references: recovery CONTINUE/STATUS, latest SOL_TRAINING_PROTOCOL and COMPUTE_QUEUE. Bind the actual recovery submission argv/environment from root's held submission receipt before assuming no output override; this audit did not locate a distinct canonical DINO submission receipt beyond these records. No held command should run again.

**RZ1R registered producer:** `src/RZ1/run_rz1r_linkfix.sh` SHA256 `6443fa0f389a1163702f240c6504461503e4b32e3c318dd44c9e999fa6c4ac74`; defaultOUT=$G/results/RZ1R, exact names RZ1R_{A,Sb}_s{408..412}. `src/RZ1/wcss/rz1-rescore-linkfix.sbatch` SHA256 `31e8bd1f2e14a027046a1083c439186928f572185898d8ee0cb991b727c40879`, reviewed commit899854e; submission `/mnt/t7/smad_next/coordination_20261114/RZ1_REVIEWED_SUBMISSION_RECEIPT.json` SHA256 `0074cd308f57012ca214f10d1e446464a9b72ea688a6f90e169f006bcb7d7203`. ExistingA408 is intentionally preserved by retry. Whole ten-network producer population should be collected; fiveSb are the needed yardsticks, A408 alone cannot substitute.

| Job | Exact remote relative output (each plus `.sha256`) | Proposed durable local destination |
|---|---|---|
|6319264|results/BB2L/BB2LW2.tar|`/mnt/t7/smad_next/coordination_20261114/archives/BB2L/BB2LW2.tar`|
|6319491|results/RZ1R/RZ1R_A_s408.tar|`/mnt/t7/smad_next/coordination_20261114/archives/RZ1R/RZ1R_A_s408.tar` — EXISTS,16844800bytes; verify equality, don't overwrite|
|6319491|results/RZ1R/RZ1R_A_s409.tar|same localRZ1R directory/name|
|6319491|results/RZ1R/RZ1R_A_s410.tar|same localRZ1R directory/name|
|6319491|results/RZ1R/RZ1R_A_s411.tar|same localRZ1R directory/name|
|6319491|results/RZ1R/RZ1R_A_s412.tar|same localRZ1R directory/name|
|6319491|results/RZ1R/RZ1R_Sb_s408.tar|same localRZ1R directory/name|
|6319491|results/RZ1R/RZ1R_Sb_s409.tar|same localRZ1R directory/name|
|6319491|results/RZ1R/RZ1R_Sb_s410.tar|same localRZ1R directory/name|
|6319491|results/RZ1R/RZ1R_Sb_s411.tar|same localRZ1R directory/name|
|6319491|results/RZ1R/RZ1R_Sb_s412.tar|same localRZ1R directory/name|

Local search bounded to recovery_MAIN,coordination,BB2,RZ1 found no finalBB2LW2 and only productionA408 above. Two **nonproduction duplicates** `RZ1/localtest/w_r/RZ1R_A_s410.tar` and `RZ1/localtest/results_r/RZ1R_A_s410.tar` are419840bytes each; never use them as productionA410. BB2LW2smoke.tar also is not finalW2. These are filename/stat observations, not archive checks. Other unindexed destinations may exist; root should reuse an existing independently verified exact copy if known. New destination namespace for W2 is proposed explicitly, not claimed canonical history.

Next exact remote **metadata command** to incorporate into root's single locked endpoint call (not executed here; standard existing collection driver copies afterwards). This command requests names/stat/opaque SHA only; no tar listing, member opening or raw logs:

```sh
flock -w 60 /tmp/opencode/wcss-client.lock ssh -o BatchMode=yes narolski@ui.wcss.pl 'set -eu
G=/lustre/pd03/hpc-narolski-1790461090/smad-next
for rel in results/BB2L/BB2LW2.tar results/RZ1R/RZ1R_A_s408.tar results/RZ1R/RZ1R_A_s409.tar results/RZ1R/RZ1R_A_s410.tar results/RZ1R/RZ1R_A_s411.tar results/RZ1R/RZ1R_A_s412.tar results/RZ1R/RZ1R_Sb_s408.tar results/RZ1R/RZ1R_Sb_s409.tar results/RZ1R/RZ1R_Sb_s410.tar results/RZ1R/RZ1R_Sb_s411.tar results/RZ1R/RZ1R_Sb_s412.tar; do
  for suffix in "" .sha256; do
    p="$G/$rel$suffix"
    if test -f "$p"; then stat --printf="%n|%s|%y\n" "$p"; sha256sum "$p"; else printf "MISSING|%s\n" "$p"; fi
  done
done'
```

Root collection driver should preserve all22 requested files and bind fresh remote/local/archive-sidecar agreement; use no-overwrite or equality check forA408 and retain old receipt. Hash logs opaquely only if source/job attestation needs them; do not print raw stdout. Record timezone-aware **verification completion** time and local resolved path. RZ1R is a yardstick rescore, not new candidate training. No additional GPU budget/command is warranted for these two completed jobs.

## Receipt evidence for fifteen 512 fits

Under `/mnt/t7/smad_next/coordination_20261114/`, the following exact COLLECTION_VERIFIED.json files jointly cover15uniqueRZ1 outputs (3+1+2+5+4). Root aggregate above freshly verifies actual local hashes; this owner did not independently rehash candidate archives.

| Receipt subdirectory | Verified time UTC | Count | Receipt SHA256 |
|---|---|---:|---|
|battery_rz1_collection_20261114T162056Z|16:22:35.181342|3|a8945a19f8dd201778ee7e938e31a85484f532671015e3f65e8bf6913f13ab14|
|new_completion_collection_20261114T164056Z|16:44:23.689522|1|baa6fa6448dce549d762b394cd2fe77b44fc2ff761c96f3c8e8df30b4864aa1b|
|sprint_rz1_collection_20261114T174257Z|17:47:13.533915|2|ebfe827636af62ce6384e395dc78074f4a0823438976bdcd22c13a72e3f4e38b|
|sprint_complete_cohorts_20261114T180257Z|18:07:00.107004|5|9bf5baa28cedfc5f6d24e5dc8e62061bb16ad20f6b3e04fb1a0faf0a43549ae0|
|rz1_pair_final_collection_20261114T184258Z|18:44:52.027977|4|fca961c6171ce536036f6ded958db44210cc964040a76cdbad70b458a2c4fcea|

Schemas differ (`archives` vs `files`, `observed_at` vs `at`). Normalization must reference exact original receipt+entry, not use filename time/remote mtime as verified_at. Final NEXT arrival record is keyed by network/supplement, with `archive`, `sha256`, `hash_verified:true`, timezone-aware `verified_at`; supplements also need actual registered `producer_sha256`. Source/config/border path identity must remain exact.

## Remaining zero-GPU closure and narrow authority questions

**Ready source without new selection policy:** SbFM, SbMR, SbM, Sb512 and E3 selection routes are already independently reviewed. Assemble final native inventories/manifests and per-arm exposure/eligibility reviews; bind all source fits plus supplementary artifacts; include actual full MS1 manifest rather than substituting FS1 row order. Preserve exact five comparator mean and same-supplement border route. Prepare source+receipt pins and independent `NEXT_ADMISSION_GO <sha256-of-admission-json>`. Eligibility expressed as `not_read` must have actual authorized registered reason, not guessed from a missing adapter.

**Sbc requires author evidence/interpretation:** exact source `experiments/RZ1_input-resolution-and-resize/prereg.md` M7 (around398–401), current SHA256 `8e4d249f06ec2f1bb99dcd8a4b14361e004dff5a47ffee004593d3e6389050d8`; v3§12q4 asks whether224interior crops fall under native-resolution ruling. General v3approval did not separately answer it. Supply existing explicit answer or ask the narrow question; no algorithm repair resolves scope.

**SbMR512 requires registered kernel prerequisite, not general new approval invented here:** v3§3item6,§5(e),§9row6 and source `read_selection.py:469`. Existing training recipe has no cross table. A preread amendment/test+independent review and compatible native adapter is allowed by that existing clause; no evidence of completed registered scoring package located. Do not relabel as cost-not-run, or automatically reject solely because source refuses. If prerequisite truly absent at batch closure, root/reviewer must bind that factual registered disposition. No exact new GPU command exists to replay.

**GX actual existing sequence, not a design detour:** `GX1_gan-morphs-in-training/READINESS_20261114.md` and prereg SHA256 `84c4c95641c098487c2bc6c632a5b58d81d6aa69dbf5e5805b0c623ede9f4c6c` require reviewed image/identity admission, manifests, floor/transfer and training producer; generation done≠fits eligible. If continuing GX before cutoff, first finish/review the existing admission code, not launch unspecified fits. No automatic scientific exclusion because this code is incomplete.

## Fresh413–417 support — needed after actual choice

No ready fresh-confirmation registration/producer mapping found in bounded inspected sources. Current native selection adapter deliberately refuses fresh native stage; RZ refit pins remain original408–412. Do not weaken them globally. A stage label alone is insufficient.

- SbFM orGX: fresh winner five + matched freshCLIPSb comparator five + appropriate plainA storage controls and all required supplemental TT1/MEDS/border/fit guards. GX retains its native all-five requirement and any own-reg controls.
- RZ1 winner: fresh winner five + freshSb0 comparator + appropriateA0/A512 control + same-seedAB1Sb refit yardstick (with sourcefit and exact rescore gate). Preserve kernel tests if applicable; Sbc scope remains required.
- E3: freshE3 A/B/Sb to establish adequacy/control/fit guards plus fresh fiveCLIPSb comparator and required W2 scoring; preserve unpaired estimator while independently binding operational fresh-seed map under v3's same-fresh-seed clause, never silently switch to a paired difference.
- Every case: unchanged recipe/rows/margins/lastcheckpoint, explicit source/input/producer/environment/smoke pins, failures retained, durable namespace/receipts and independent pre-run+admission review. Confirmation result tied to actual fixed-order selection_record. Fresh confirmation falls after selection arrival cutoff by existing rule; failure retainsSb. No benchmark release follows from this report.

After source/receipts/dispositions are independently bound and committed, root may use documented clean-checkout preflight command `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/NEXT/read_selection.py --admission experiments/NEXT_method-selection-rule/ADMISSION.json --preflight`. **Not ready to invoke now**: canonical admission absent, batch authority incomplete. This audit never invokes it or consumes a journal.

CLAIMS:
- commit b11a8c9 E3 five-seed source freeze exists (git log verified).
- commit 78490ba integrated native implementation; current selector/native hashes equal independent F1 recheck.
- number common_input_pin_checks=44PASS;support_pin_checks=20PASS @ root-based sha256sum checks in this audit.
- number RZ1_512_opaque_arrivals=15 @ five receipt rows and root aggregate; no candidate scientific eligibility claimed.
- No selected challenger, production admission, scientific read, independent self-approval or new training is claimed.
