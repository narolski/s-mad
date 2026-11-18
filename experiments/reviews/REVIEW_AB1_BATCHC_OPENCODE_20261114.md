# Independent POST-RESULT review: count-balanced Batch C

14 November 2026. Reviewer independent of the Batch-C author and admission reviewer. Scope: the admitted completed C output, registered source and existing descriptive references only.

**Disposition: the four reported registered verdicts agree with the saved per-seed arithmetic and rules. H-c1 is present; H-c2 is absent on both registered outcomes. This is a development ablation, not a method-selection result. Verification is summary-level plus static source review, not independent reproduction of AUCs or bootstrap intervals from scores.**

## Execution and integrity

Read AB1 amendments 4/4b/5b/7/7b, final admission MD/JSON, the earlier statistics/controls review, `ab1_pm3_read.py`, its imported statistic and adversary rule, execution receipt, stdout/stderr, and both canonical journal records. The earlier pre-read blockers are superseded by final admission, not silently waived here.

- Final admission SHA256: `12745bb6f9150a0d16b637e51b1cb9d05f143a5d9fc426fd2f77e22240dd259d`.
- Output: `/mnt/t7/smad_next/AB1/c/read_20261114/ab1_pm3_read_C.json`, SHA256 `9b73b148c57b9dbfbfdf60da2360aa9825ac7ddd8c42a94cd2fe137e21c802ea`.
- Independently rehashed admission, stdout, empty stderr, output and both journal files against execution.json; all agree. All 49 source/transitive-input entries in final admission rehash correctly. Claim records reader `11dd5aef7e3a86a4d208e3ad75f81b6be80a62bce5ad958fad3c74f454cbf7f0` and the admitted overlay and directories.
- Claim: 11:47:16.475277 UTC, `claimed_before_score_access`; completion: 11:51:58.930760 UTC, same output hash. Process 11:47:16.373758–11:51:58.977770 UTC, exit 0, 282.597854 s. Claim/completion hashes respectively `ee94e4ebd7a8a37b9eef195595e30b6961bc714bc17ca16bd2f3da8d4750955c` and `3a1aa5e7556a2f8f1126c1d0d2050e1cf68d7256f2bad65ecad59de76de272ea`.
- All 30 networks are `read`: Sb, B, Sp, SpV, BN, BV, each seeds 408–412. **Zero per-network refusals; zero dropped seeds.** Every one of the 144 pair/population summaries uses all five seeds. No scientific failure is inferred from technical status. Archive-native provenance is supported by the successful guarded read and admission; this reviewer did not reopen archives.
- A reviewer shell probe initially used unavailable `python` (exit 127); repeated as `python3`. This was not a production-reader failure or rerun.

## Independent arithmetic and rule checks

Without importing or executing the production reader, recomputed all 144 stratified and unstratified pair differences from saved per-network AUCs, their seed means, all 16 deciding/printed interval-summary verdicts, positive-seed counts, interval half-widths, sign-disagreement caps, and both per-seed interaction vectors/means. All agree to numerical tolerance 1e-14. Stdout reports the same verdicts as the JSON.

All 18 population/contrast cells contain 30 per-network summaries. Rows per class / graph components are: dev+clean80 180/151; dev 100/100; clean80 80/51; dev+clean69 169/146; test191 191/130; test159 159/108. These are saved denominators, not independent score-level reconstruction.

Primary: OpenCV whole-frame two-person versus same-person morphs (R4/R3), D-stratified, 100 development + 80 clean test hosts. Secondary: face-spliced S4/S3, **unstratified**, clean80 only. Joint host-partner component bootstrap: 2,000 draws, fixed seeds, RNG 20261120. Primary has 0/2,000 unreadable draws. Secondary has 754/2,000 (37.7%) unreadable **stratified** draws; its registered unstratified decision uses all 2,000, not the 1,246 readable stratified draws. This is the pre-fixed amendment-5b rule, not a response to the result.

### Registered results

AUC differences, not relative percentages. CIs below are the saved component-bootstrap intervals, checked for rule use but not independently regenerated. Values rounded to nine decimal places.

| Outcome | Pair | Mean gain | 95% CI | 99.5% sensitivity CI | Positive seeds | Verdict |
|---|---|---:|---|---|---:|---|
| R4/R3 primary | Sb−SpV | +0.048098592 | [0.026893408, 0.072238231] | [0.016970693, 0.082324935] | 5/5 | present |
| R4/R3 primary | BN−BV | −0.002992958 | [−0.008883478, 0.004497694] | [−0.012053791, 0.008287089] | 1/5 | absent |
| S4/S3 secondary | Sb−SpV | +0.081781250 | [0.053514957, 0.108347349] | [0.039560269, 0.118322637] | 5/5 | present |
| S4/S3 secondary | BN−BV | −0.024656250 | [−0.045510204, −0.005024836] | [−0.053814792, 0.003143776] | 0/5 | absent |

H-c1 primary passes mean ≥0.03, lower bound >0, seed sign and positive unstratified gain (+0.050246914). Development/clean80 stratified means are +0.046243740/+0.072135785: no cap. H-c2 primary has upper bound <0.03, with development/clean means −0.002337229/−0.006789250: no cap. “Absent” concerns the registered +0.03 benefit; it is not proof of exactly zero effect or equivalence.

Secondary H-c1 full-set stratified gain is +0.117397454, satisfying its agreement check. H-c2 secondary stratified gain is +0.015275813 but unstratified gain is negative in all five seeds. Do not substitute the former for the deciding statistic. The negative 95% interval is descriptive evidence of worse ranking on these rows; its 99.5% interval crosses zero. Although the registration called secondary benefit near-certain by design, BN−BV does **not** deliver it. Report that failed expectation honestly; these secondary contrasts still are not fresh mechanism tests.

## Direct effects, interaction and training limitations

H-c1 supports a gain from replacing repeated native negatives by matched S0/S3 negatives **together with the 312 additional unique images**, in the recipe containing S4 positives. H-c2 does not support a ≥0.03 gain from the analogous replacement in the recipe without S4 positives. Counts/class mix and positive repetition are controlled within each pair; content and diversity are not separated.

All four arms have 8,386 balanced training rows. Unique counts Sb/SpV/BN/BV are 5,535/5,223/5,411/5,099. The registered positive multisets match within Sb/SpV and BN/BV, not across all four arms. Fixed steps do not mean identical unique-image exposure. BN−B is confounded by positive repetition (R4 499 versus 443), and Sb−BN is not a pure intervention on S4 content.

Printed interaction `(Sb−SpV)−(BN−BV)` is **+0.051091549 primary**, **+0.106437500 secondary**, positive in all five seeds for both. The output supplies **no interaction CI or registered interaction test**. These point estimates are consistent with recipe dependence; “significant synergy”, “negatives require positives” as a universal causal finding, or an interaction CI obtained by subtracting marginal endpoints would be unjustified. A significant direct effect and an absent direct effect do not themselves constitute an interaction test.

Printed primary controls: SpV−Sp +0.001338028 [−0.003509232, +0.007145058]; BV−B +0.003133803 [−0.001444073, +0.007285381]. Both receive the dev/clean sign cap. Their JSON verdict strings omit “printed only” after capping, but their role remains descriptive; do not promote them to registered hypotheses. BN−B +0.000140845 [−0.006226620, +0.007827197]; Sb−BN +0.041795775 [0.019561445, 0.067771475]. Reprints Sb−Sp +0.049436620 and Sb−B +0.041936620 are consistent with these decompositions, not additional replications.

Shape-link sensitivity dev+clean69 retains the primary directions: H-c1 +0.049203757; H-c2 −0.002531646. FaceMorpher on dev+clean80 gives +0.067077465/+0.004788732, respectively. Both are printed point estimates without new bootstrap verdicts. R4 positives are trained; R3 negatives are not. Interpret transfer from splice-negative training to whole-frame same-person morphs, not a wholly untrained contrast. D is a class-dependent host splice covariate, not the whole-frame morph's own energy.

## Floors and descriptive references

Within-D contexts reproduce saved pinned JSONs for 582-row ri and 382-row test populations: all-cue logistic AUC 0.785337621 and 0.767083027; pure-D references 0.572411576 and 0.584717120. They are **different populations** from the primary 360 rows. No subtraction from the primary network AUC is licensed.

Existing unstratified per-network ADV comparisons are separate context: Sb exceeds all-cue R4/R3 ri floor in 5/5 seeds, test OpenCV in 4/5, FaceMorpher in 0/5; Sb exceeds no all-cue S4/S3 floor (ri/dev/test: 0/5 each). SpV/BN/BV exceed no all-cue floor among the six printed contrasts. These counts retain all seeds and do not show shortcut freedom, nor establish a familywise superiority claim.

Descriptive transfer report `OPENCODE_BATCHC_B2_REVIEWER_TRANSFER_20261114.json` SHA256 `6aa92d51e7f5f9a9a3f514bab3c2bd03022a54cf495efc0cb1951da5888a07b5`: sel360 logreg/GBT AUCs SpV 0.725246914/0.725216049, BN 0.719012346/0.685833333, BV 0.716172840/0.667438272. Clean80 S4/S3: SpV 0.667968750/0.621875000; BN 0.597187500/0.456718750; BV 0.619531250/0.480781250. These are previously computed, unstratified training-list transfer learners, not in-domain floors, not candidate operating thresholds, and not independently refitted here. No network-minus-learner significance follows.

## Verification boundary and exact missing subset

The output has per-network AUC summaries and interval endpoints, but no row logits or bootstrap replicate vectors. Thus **full independent numerical reproduction is not possible from this output alone**. This is an evidence-resolution limitation, not evidence of a technical failure or grounds to rerun the once-only reader.

For an authorized independent verification of the four registered outcomes, the minimal additional score subset is an immutable export from the already-admitted evaluation payloads: **Sb, SpV, BN, BV × seeds 408–412**, OpenCV R4/R3 for dev+clean80 (360 rows/network), and S4/S3 for clean80 (160 rows/network): **520 rows per network, 20 networks, 10,400 logits**. Include exact IDs, arm/seed, host, rung/class, host-partner mapping/component membership, D(S4/S3), row order and mapping/hash linkage to the admitted archives/evaluation manifest. Existing pinned split/D metadata can supply the non-score columns. This permits independent AUC and fixed-stream bootstrap reconstruction without other candidate rows. To reproduce all descriptive comparisons, extend only to the six named arms and the explicitly printed populations/engines; floor verification additionally needs their matched candidate row IDs. Alternatively, saved paired replicate vectors would verify quantiles but would not independently verify AUC computation. No export or further read is authorized by this review itself.

Intervals condition on these five trained networks; seeds are not resampled. They do not quantify arbitrary retraining uncertainty. Nominal 95% rules are retained; 99.5% is sensitivity, not 16-verdict-family 95% correction. Post-freeze, development-informed ablation; amendment 7b followed the lead's MAD22 exposure. These are not frozen 403–407 network results, held-out benchmark evidence, or NEXT promotion. AUC gains alone do not establish fewer artifact false alarms while preserving attack sensitivity at a fixed operating point.

## Krótki projekt wniosków po polsku

Po wyrównaniu liczby wierszy treningowych model z dopasowanymi negatywami lepiej rozróżniał morfy dwóch osób od morfów tej samej osoby: **Sb−SpV = +0,048098592 AUC (95% CI: 0,026893408–0,072238231)**. Poprawa wystąpiła we wszystkich pięciu ziarnach. Kontrola bez pozytywnych przykładów wklejania twarzy nie wykazała zarejestrowanej korzyści: **BN−BV = −0,002992958 (−0,008883478–0,004497694)**.

Na wklejanych twarzach wyniki wyniosły odpowiednio **+0,081781250 (0,053514957–0,108347349)** oraz **−0,024656250 (−0,045510204–−0,005024836)**. Drugi wynik przeczy oczekiwaniu poprawy w tej kontroli. Różnica efektów wynosi opisowo +0,051091549 dla całych obrazów i +0,106437500 dla wklejanych twarzy; nie mamy przedziału ufności dla interakcji.

Wyniki wspierają użyteczność dopasowanych negatywów w pełnej recepturze, ale nie oddzielają ich treści od dodatkowych 312 unikalnych obrazów. To ablacja na danych rozwojowych i wskazanych czystych hostach testowych, nie niezależny test końcowy. Nie dowodzi braku skrótów ani przewagi na benchmarkach. Wszystkie 30 sieci odczytano poprawnie; nie odrzucono żadnego z pięciu ziaren. Sprawdzono rachunek zapisanych podsumowań i zastosowanie reguł; przedziały ufności pochodzą z dopuszczonego odczytu, bez niezależnego odtworzenia z logitów.
