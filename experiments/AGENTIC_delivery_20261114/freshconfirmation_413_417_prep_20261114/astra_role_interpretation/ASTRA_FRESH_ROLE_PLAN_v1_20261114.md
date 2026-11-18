# Fresh 413–417 conditional role interpretation v1

Status: SOURCE-ONLY / HOLD. 2026-11-14. No selection, result access, scientific preflight, training or rescoring was performed. Only the authorized registrations and NEXT reader/adapter source were inspected, after AGENTS.md and CONTINUE.md. No archive/member, score, weight, NPZ, image, sealed data, journal or selection output was opened. This document is interpretation for prospective review, not an adopted registration or launch approval.

All citations below are repository-relative to /home/narolski/smad-next. NEXT means experiments/NEXT_method-selection-rule/prereg_draft_v3.md **at dbeb940**, not an amended rule. RZ means experiments/RZ1_input-resolution-and-resize/prereg.md; BB means experiments/BB2_second-backbone/prereg.md; FM means experiments/AB1_protocol-ablation-and-replication/prereg_fm.md; Reader means src/NEXT/read_selection.py; Adapter means src/NEXT/native_adapters.py.

## Binding interpretation

NEXT:48–65 fixes the original eight-arm order and comparator types. NEXT:181–194 selects the earliest qualifier once, then confirms only that arm on fresh 413–417 against its comparator at the same fresh seeds; failure leaves Sb. NEXT:86–87 explicitly defines DINO's difference against the comparator seed mean, while 63–65 requires independent candidate/comparator seed resampling with common component draws. The fresh phrase does **not** turn DINO into a paired contrast. The seed labels of the two independent five-fit cohorts coincide; the estimand remains unpaired.

NEXT:151–153 specifies AB1 A, RZ1 A0/A512 or E3 A as the platform control. NEXT:169–176 retains own-registration/platform/fit guards and five-seed counting. Consequently, fresh controls needed to instantiate those guards should be registered at 413–417, not replaced by historical controls. The rule states candidate/comparator freshness expressly; moving all ancillary controls and refit yardsticks to those same fresh seeds is the coherent prospective realization of “same rule,” but the detailed training task list is not itself enumerated in NEXT. Adopt that realization explicitly before runs/read.

## Conditional cohorts, never a decision to run all branches

Each item denotes five last-checkpoint fits, one at every seed 413,414,415,416,417. “Core” means sufficient role types for the NEXT deciding contrasts/implemented guards, **not** certification that every descriptive read of a source experiment has been reproduced.

| Fixed branch | Core fresh role types | Core fits | Additional descriptive/source-scope question |
|---|---|---:|---|
| 1 SbFM | AB1FM SbFM; AB1 Sb comparator; AB1 A control | 15 | FM:63–64,82–87,112–114 also print AB1 B. Full FM descriptive replication adds fresh AB1 B: 20 fits. B is not a NEXT decision guard in current Reader. |
| 2 GX | GX candidate; AB1 Sb comparator; AB1 A platform control | at least 15 | NEXT:61,151–153 establish these roles. GX own registration was outside this bounded source list; its full guards/cohort cannot be certified here. |
| 3 SbMR | RZ1 SbMR; RZ1 Sb0 comparator; RZ1 A0 control; AB1 Sb refit yardstick source | 20 | Full amendment-1 A reproduction prints add AB1 A: 25 fits. |
| 4 SbM | RZ1 SbM; RZ1 Sb0; RZ1 A0; AB1 Sb yardstick source | 20 | Same additional AB1 A question: 25 fits for full A/Sb yardstick prints. |
| 5 Sb512 | RZ1 Sb512; RZ1 Sb0; RZ1 A512; AB1 Sb yardstick source | 20 | Fresh A0 required to reproduce explicit against-A0 512 prints; AB1 A required for full A refit prints. Both additions give 30 fits. |
| 6 SbMR512 | RZ1 SbMR512; RZ1 Sb0; RZ1 A512; AB1 Sb yardstick source | 20 | Against-A0 prints add A0; full A yardstick prints add AB1 A (30). Repeating H-512d itself also needs fresh Sb512 (35 total), but H-512d support is not automatically a new NEXT pass bar. Existing preregistered kernel route must be inherited, never duplicated. |
| 7 Sbc | RZ1 Sbc; RZ1 Sb0; RZ1 A0; AB1 Sb yardstick source | 20 | Full A yardstick prints add AB1 A (25). Ac is a separate plain crop ablation, not NEXT's specified control. Crop ruling still applies. |
| 8 DINOv3 | BB2L/E3 Sb candidate; BB2L/E3 A control; BB2L/E3 B fit-guard; AB1 CLIP Sb comparator | 20 | No CLIP A requirement follows from NEXT/BB2 deciding gates. Adding CLIP A would be an extra descriptive extension, not a minimum requirement. |

Rescoring the fresh AB1 yardstick is an additional scoring task, not an additional fit. Counts are conditional counts, not an aggregate compute request. They exclude smokes/rescoring and imply no job authorization.

## DINO details: fresh A and B are required; CLIP A is not

BB:146–155 defines a read seed through completed finite A/B/Sb fits, with each arm's own-rule training accuracy at least 0.75 for adequacy. BB:509–512 adds candidate Sb training lad_S4-vs-lad_S3 AUC at least 0.80, requiring four passing seeds in five-seed mode. BB:321–324 requires both X and A adequate for a storage pass. NEXT:169–170 imports these fit gates and explicitly requires E3 splice-fit on at least four of five.

Reader:350–355 maps E3 A to control and E3 B to fit_guard, with AB1 Sb as comparator; 923–937 checks all three E3 accuracies, X/A storage adequacy and E3 A's storage bar. Thus E3 B cannot be discarded because it is absent from the cross-backbone effect contrast. E3 A cannot be replaced by CLIP A. Fresh CLIP A is not named by these gates.

At each fresh candidate seed s, every deciding difference uses E3 Sb_s minus mean(AB1 Sb_413,…,AB1 Sb_417). Independent seed/component bootstrap remains unchanged (NEXT:63–65; Reader:211–218,991–998). Reader:891–894 refuses an undefined five-comparator mean; there is no reduced comparator mean, seed matching, or historic 408–412 fallback. Missing candidate fits retain the original failure denominator (NEXT:174–176). A fresh E3 registration must preserve the rule-fixed LR and batch recipe (BB:494–502), not re-run the old three/five seed deadline choice on different seeds (BB:504–507).

## RZ1: comparator, yardstick and plain-control distinctions

NEXT:62 makes Sb0 the paired comparator for **every** RZ branch, never AB1 Sb. NEXT:91–92 also requires mean landmark_combined gain to exceed the largest same-seed Sb0-versus-AB1-Sb absolute refit difference. Fresh AB1 Sb is therefore the yardstick source, not the replacement comparator. RZ:420–434 requires exact original-manifest bit identity before its unchanged RZ scoring; 437–445 gives the same-seed refit differences and maximum; 462–465 specifies eligible gated pairs. NEXT's v3 mean-gain rule controls, not RZ section 8's older proposed median/threshold or its missing-yardstick relaxation.

RZ:156–157 explicitly uses A0 for 224 and A512 for 512, and **prints against A0 for 512**. RZ:250–255 additionally prints A512−A0 and Sb512 against both controls. Therefore a core 512 cohort with only A512 cannot reproduce those registered A0 descriptive outputs. It must not be labeled full RZ confirmation without a prospectively adopted scope decision or adding A0.

RZ:94–96 and 437–439 explicitly describe A0-versus-AB1-A as well as Sb0-versus-AB1-Sb reproduction prints. AB1 A is not needed to compute NEXT's deciding **Sb** refit maximum. It is needed to reproduce the **A** yardstick. For 224, A0 already exists in the core, so AB1 A is the sole extra fit type. For 512, both A0 and AB1 A are extra relative to the core.

What is direct versus ambiguous: the original descriptive requirements are explicit; their wholesale carry-forward into a selected-arm-only fresh confirmation is not enumerated. NEXT says “same rule,” imports every registration **guard**, and specifically requires floor prints, but does not say rerun every unrelated original hypothesis/ablation. A prospective registration must decide whether to preserve all applicable descriptive prints or narrow fresh output to NEXT decision/guard requirements with an explicit disclosure. Do not invent that adoption, silently omit explicit descriptive rows, or convert descriptive hypotheses (e.g. H-512d) into new deciding bars. Recommend preserving A0/A yardstick prints where claiming full RZ replication; otherwise retain HOLD pending a documented reviewed scope choice.

FM analogous distinction: FM:80–81's original-engine no-loss guard needs only SbFM and Sb. FM:82–87 and 112–114's full tables also use B; adding B is needed for those tables, not for that guard. Current Reader:854–861,920–922 implements the former.

## Separate confirmation implementation/registration required

Do not edit or reuse the one-shot original selection state to test fresh data. Preserve original selection source, admission, rule, pins and journal; use a separately versioned confirmation adapter/admission and distinct confirmation record linked to the immutable eventual selection record. This document did not open that record and does not identify a winner.

Concrete source barriers:

- Reader:313 explicitly refuses fresh native sources; 334–335 binds E3 403–407 mode; 350–370 binds historical native role seeds and AB1 source hashes. Adapter:93–107 restricts native families to historical seed ranges. Confirmation must introduce exact new identities/pins, never broadly disable provenance checks.
- Reader:478–497 recognizes RZ fresh seed labels but rejects their yardstick hashes because original AB1 source pins are fixed. A registered/reviewed fresh pin extension is explicitly required. Keep RZ refit bit identity and same-seed mapping.
- Reader:891 hardcodes historical CLIP comparator seeds; confirmation must use exactly five fresh CLIP Sb fits while preserving unpaired calculation/refusal semantics.
- Reader:455–469 demands dispositions for all eight and currently lacks GX native validation and refuses SbMR512. These are implementation barriers, not permission to exclude a scientifically eligible branch (466). Coordinate with the already owned kernel work; no duplicate UVv3 or kernel package is proposed.
- Reader:511–521 requires pinned confirmation registration, only the preselected arm read, pinned selection record, and validated linkage. Reader:1003–1006 already encodes confirmation failure→Sb. Preserve those semantics.
- Reader:435–450 requires committed exact rule/reader/admission/support/review/receipt/input pins and independent GO binding exact admission bytes. Fresh ancillary adapters, reporting scope, recipe provenance, scoring path and all role failures need equivalent prospective review before execution.

No checkpoint availability conclusion was drawn. Source-pinned frozen tower plus exact last_trainable reconstruction may be valid; absence of a full last.pt file is not independently asserted as a blocker.

## Source fingerprints at inspection

```
5188ad9a696d86c935191a4fd45bee0f0762186c199a5bbd7d8368e87bf62667  NEXT v3 at dbeb940
8e4d249f06ec2f1bb99dcd8a4b14361e004dff5a47ffee004593d3e6389050d8  RZ prereg
65752673addb1463c27c2622d9fb9ff446cc9bee4bedab285ee24f8879af1c17  BB prereg
09b6b5d56a564f739401ac952e4a405ee17ec9a3dd1efc2b305f3149a40cfd61  AB1 prereg
174ceead54745c92be15835b741afa43cf48ebe753407e0b5a7d0bd290b88ddd  FM prereg
f20f42578275aa3d92b8c695ab86827a526b7f62016b98ec242bf17c0b390830  Reader
ebb40edda27a08034a6087a737109509e65c3c5ad76c748767cd19a49f2ff17c  Adapter
```

Bounded handoff complete. No scientific executable was run and no launch/read authorization is implied.
