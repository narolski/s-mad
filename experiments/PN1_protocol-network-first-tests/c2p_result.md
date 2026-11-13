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
- **H-new-1: Sb "falsified"** (Δm_att(Sb, z) ≥ −0.10 on 4 read seeds at both sizes: fm61 +0.056, +0.105, +0.061,
  +0.071; amsl112 −0.024, +0.041, −0.012, +0.005 for seeds 403, 405, 406, 407; seed 404 not read, gate). **B
  "inconclusive"** (one read seed).
- **H-new-2: "inconclusive"** (no A network read).
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
