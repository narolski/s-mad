# Contrast 2-prime (registration C2P, 2715e48): registered read

Read once on 13 Nov 2026 (`date`: Fri Nov 13 09:27:21 AM CET 2026) with `src/PN1/c2p_read.py` (`45e72914…`) on
`/mnt/t7/smad_next/MS1/c2p/C2P_m1.tar` (45 of 45 score files; fetched, verified and second-copied 09:26:20; scored on
ms1m1b, NVIDIA L40S GPU-c1ff3444…, torch 2.2.1, timm 1.0.27, TF32 off). Output `c2p_read.json`. Owner's numbers, not
reviewed.

## Platform gate (registered: p99 |Δlogit| ≤ 0.05 AND max ≤ 0.10 AND own-rule agreement ≥ 99.5%, 6,339 rows)

| network | p99 | max | agreement | gate |
|---|---|---|---|---|
| A 403 | 0.039 | 0.249 | 1.0000 | fail (max) |
| A 404 | 0.043 | 0.122 | 0.9994 | fail (max) |
| A 405 | 0.040 | 0.153 | 0.9998 | fail (max) |
| A 406 | 0.039 | 0.119 | 0.9998 | fail (max) |
| A 407 | 0.036 | 0.205 | 0.9997 | fail (max) |
| B 403 | 0.027 | 0.120 | 1.0000 | fail (max) |
| B 404 | 0.036 | 0.102 | 0.9995 | fail (max) |
| B 405 | 0.026 | 0.075 | 0.9998 | pass |
| B 406 | 0.027 | 0.141 | 1.0000 | fail (max) |
| B 407 | 0.016 | 0.114 | 0.9997 | fail (max) |
| Sb 403 | 0.012 | 0.045 | 1.0000 | pass |
| Sb 404 | 0.019 | 0.115 | 0.9998 | fail (max) |
| Sb 405 | 0.017 | 0.071 | 0.9998 | pass |
| Sb 406 | 0.019 | 0.074 | 1.0000 | pass |
| Sb 407 | 0.012 | 0.052 | 1.0000 | pass |

All 15 pass the 99th-percentile and agreement conditions; 10 fail the maximum condition (the pre-run check's tightening
from 0.15 to 0.10). Under the draft's 0.15, A 403, 405 and 407 would still fail (A control on at most 2 seeds), so the
verdict below does not depend on that choice.

## Registered verdicts

- **A's positive control: not met on any seed** (every A network failed the gate, so by C2P.2 its seed counts as
  control failed).
- **Contrast 2-prime: "uninformative" for B and for Sb** (A's control met on 0 of 5 seeds at both sizes).
- **H-new-1: Sb "falsified" on 4 of 4 read seeds, seed 404 not read** (gate; Δm_att(Sb, z) ≥ −0.10 at both sizes:
  fm61 +0.056, +0.105, +0.061, +0.071; amsl112 −0.024, +0.041, −0.012, +0.005 for seeds 403, 405, 406, 407). **B: not
  read: one B seed passed the gate (C2P.2)** (the reader's label was "inconclusive").
- **H-new-2: not read: no A network passed the gate (C2P.2)** (the reader's label was "inconclusive").
- **Freeze rule implied (FINAL section 1 as amended, 6691adc): no method is frozen** (contrast 2-prime does not pass
  for Sb or B).

## Printed (gate-passed networks only; no decision)

| network | native own-rule flag | Δf fm61 | Δm fm61 (SD) | Δf amsl112 | Δm amsl112 (SD) |
|---|---|---|---|---|---|
| B 405 | 0.047 | +0.058 | +0.171 | +0.017 | +0.037 |
| Sb 403 | 0.017 | +0.017 | −0.237 | +0.007 | −0.145 |
| Sb 405 | 0.037 | +0.021 | −0.176 | +0.003 | −0.138 |
| Sb 406 | 0.060 | +0.038 | −0.021 | +0.034 | −0.026 |
| Sb 407 | 0.030 | +0.010 | −0.124 | −0.003 | −0.113 |

Not computed by the registered reader: any read of the A networks or of gate-failed networks (their hold-out scores
exist in the tar; any use of them is post hoc and needs the lead's decision and labelling).

## Attestation and quarantine (`date`: Fri Nov 13 09:36:59 AM CET 2026; post-result review `experiments/reviews/REVIEW_PN1_C2P_20261113.md`, e2af82c)

- `C2P_m1.tar` sha256 `4e25fcc1ed845229420337021831b54ca107336eb91073d38e7c14b747f8d542` (local
  `/mnt/t7/smad_next/MS1/c2p/C2P_m1.tar` and second copy `/home/narolski/ms1_results_copy/C2P_m1.tar`, identical);
  `c2p_read.json` sha256 `62ee0bf430388be8094158f3f3aac429521612751a29c91c2290ae28ff4e5598`.
- Statement by the owner: no hold-out (fam ms1ffhq) statistic of any gate-failed network (A 403-407, B 403, 404, 406,
  407, Sb 404) has been computed, plotted, printed or opened. The reader (`c2p_read.py` lines 137-141) loaded their
  hold-out logits into memory together with the gate rows and skipped them at line 149: **loaded, not used**. The
  owner opened no ms1ffhq member of the tar outside the reader; the tar is not unpacked anywhere. Nobody opens these
  scores until a re-scoring (amendment C2P-R, if approved) has been read; any later use is labelled post hoc.
- Cause (review F1): scoring on L40S with TF32 off against stored A100 PCIe logits made with TF32 on (pn1_score.py),
  contrary to `PLATFORM_PINS_FOR_FINAL_READ.md` item 7 (f2c2023) and C2P.2's "never two GPU models".

## What can and cannot be said today (review Q3, Q4)

Paper wording for the gate: "The registered gate (99th percentile ≤ 0.05, maximum ≤ 0.10, tightened from 0.15 before
any score) failed on its maximum condition for all plain networks because scoring used another GPU model and TF32
setting than training. We report the test as uninformative [and the registered re-scoring on the training platform
beside it]."

Can be said: "On 300 FFHQ persons no network was trained on, the four protocol-plus-splice networks that passed the
platform gate (seeds 403, 405, 406, 407) raised their own-rule flag rate on stored genuine photos by +1.0 to +3.8
points at the trained size (61.2 px) and by −0.3 to +3.4 points at an untrained size (112.7 px). Their mean genuine
logit moved toward genuine (−0.02 to −0.24 genuine SD). Stored morphs did not become easier to miss (morph shift +0.06
to +0.11 SD at 61.2 px and −0.02 to +0.04 SD at 112.7 px; storage evasion falsified on 4 of 4 read seeds). Development
data only. No plain network passed the gate, so these reactions are not compared with the plain recipe, and the
registered storage contrast is uninformative." Sb 406 is the largest (native flags 6.0%; upper 95% bounds of Δf 6.5
and 5.9 points).

Cannot be said: "reduced relative to the plain recipe" or "at most one third of it"; "removed", "absent" or
"shortcut-free"; anything about B (one seed) or A; anything about H-new-2; any generalisation beyond development data.
