# Batch C: independent numerical verification addendum

14 November 2026. Follow-up to `REVIEW_AB1_BATCHC_OPENCODE_20261114.md`, under MAIN's explicit authorization to export and verify only the four already-admitted registered outcomes.

**PASS: independently reconstructed AUCs, paired seed effects, fixed-stream component-bootstrap intervals and registered verdicts match the admitted output exactly. All 166 comparisons pass; maximum absolute numerical difference is 0.0.** This resolves the earlier review's score-level reproduction limitation for these four outcomes only. Scientific conclusions and limitations in that review remain unchanged.

## Preserved evidence

Create-only directory: `/mnt/t7/smad_next/AB1/c/independent_verification_20261114/`.

| Artifact | SHA256 |
|---|---|
| `verify.py` | `bb431ad9d7eb18dacd7b61593f9639023e67b42bd1cab8e08cce4915ec0da45e` |
| `subset.json` | `c408c57feb972856ab302030c829697621d2c872331b9252830be6a10ac1c3e3` |
| `comparison.json` | `1b5a789ba01666c3c91e619c0049371ffcb85a1664536e23948461be8dc21bb7` |
| `stdout.log` | `a1e8eff1bfa5eeae260b84a99366cadba499af44f34a9f310fe53f0cb4a905d5` |
| `stderr.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

`receipt.json` binds the verifier, subset and comparison; `execution.json` records first and only execution, 11:57:21.083977–11:57:26.698143 UTC, exit 0, empty stderr. Interpreter `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`, NumPy 1.26.4; OMP/OpenBLAS/MKL/NumExpr thread limits 2. Files were exclusive-created and made read-only (0444); this is an application/filesystem-permission safeguard, not a claim of WORM storage. No failed attempt, verifier correction or outcome-driven retry occurred.

## Exact export boundary

Reverified final admission SHA256 `12745bb6f9150a0d16b637e51b1cb9d05f143a5d9fc426fd2f77e22240dd259d`, original result SHA256 `9b73b148c57b9dbfbfdf60da2360aa9825ac7ddd8c42a94cd2fe137e21c802ea`, and all 49 bound source/transitive inputs before access. Selected exactly 20 admission entries: Sb/SpV/BN/BV × seeds 408–412. Verified each archive's full byte hash/size, sidecar hash and advertised archive hash.

Only `<exact archive stem>/scores_eval.npz` was extracted from each archive; no training scores, logs or other payload member was extracted. Checked unique member identity, embedded evaluation-manifest SHA256, full ordered ID identity against the bound manifest and logit-vector shape. NPZ decompression necessarily materializes the logit array; only the authorized index slice was converted, retained, numerically checked or exported. Other logits received no numerical inspection or interpretation.

Each network contributes exactly 520 selected rows: OpenCV R4/R3 on dev+clean80 (180+180), S4/S3 on clean80 (80+80), total **10,400 logits**. All selected logits are finite. The immutable export includes full selected manifest rows and indices, exact host split rows, partner links, component labels, class, D and its S4/S3 origin; full source archive admission records, score-member hashes, and metadata file paths/hashes provide manifest/source linkage. Twenty distinct arm/seed identities and 520 distinct row IDs per network were asserted. Archive arm/seed native checks from the admitted first read remain inherited; this export did not open task.env anew.

## Independent implementation and stream fidelity

No production reader, main function, loader or statistic function was invoked or imported. The standalone verifier implements AUC independently by sorted pair counting with half-credit for ties. It implements pooled log-D quintiles, right-sided boundary assignment, within-stratum AUC weighted by positive×negative counts, minimum ten rows per class and 50% coverage directly from the registered specification.

Components were independently reconstructed by graph traversal, preserving the source's first-host component order and host order within components. Primary uses ordered development hosts followed by clean80, secondary uses ordered clean80. The RNG is initialized once with 20261120; 2,000 primary component draws precede 2,000 secondary draws. The intervening source populations consume no RNG draws. The same draws are shared across all arms/seeds. Each draw reconstructs its D quintiles. No seeds are resampled.

Checked all 20 networks' stratified/unstratified full-set AUCs on both populations; each pair's five stratified/unstratified effects; means; sign counts; dev/clean cap inputs; 95%/99.5% intervals; alternative-statistic intervals; unreadable counts/shares; and final verdicts. Tolerance was fixed in code at absolute 1e-12, relative 0; observed difference was exactly zero. Per-field computed and saved values are retained in `comparison.json`.

Primary has 151 components and 0/2,000 unreadable stratified draws. Secondary has 51 components and 754/2,000 unreadable stratified draws (37.7%). Its unstratified decision uses all 2,000; its displayed stratified interval uses 1,246. There is no result-dependent statistic switch.

## Reproduced registered results

| Outcome | Pair | Mean AUC difference | 95% CI | Verdict |
|---|---|---:|---|---|
| Primary R4/R3, D-stratified | Sb−SpV | +0.048098591549295786 | [0.02689340793117823, 0.0722382308615375] | present |
| Primary R4/R3, D-stratified | BN−BV | −0.002992957746478897 | [−0.008883478404352399, 0.0044976944366990025] | absent |
| Secondary S4/S3, unstratified | Sb−SpV | +0.08178124999999999 | [0.05351495726495726, 0.10834734858107126] | present |
| Secondary S4/S3, unstratified | BN−BV | −0.02465625 | [−0.04551020408163264, −0.005024835763499499] | absent |

All five seeds remain in every comparison. “Absent” is the registered absence of a +0.03 benefit, not equivalence to zero. No new interaction interval was computed. The earlier review's descriptive floor comparisons, additional arm contrasts and sensitivity populations were not independently reconstructed in this narrowly authorized follow-up.

Canonical C.claim/C.complete hashes were rechecked after verification and remain identical to the original execution receipt. No production read was repeated, journal altered, cluster contacted, benchmark opened, method selected, manuscript edited or commit made.

## Uzupełnienie wniosków po polsku

Niezależne obliczenia na dokładnie 10 400 dopuszczonych wynikach odtworzyły wszystkie cztery zarejestrowane wyniki, w tym przedziały ufności, bez różnic liczbowych. Wniosek pozostaje ten sam: pełna receptura z dopasowanymi negatywami daje poprawę Sb−SpV, natomiast kontrola BN−BV nie wykazuje zarejestrowanej korzyści. To nadal ablacja rozwojowa; dodatkowe unikalne obrazy pozostają nierozdzielone od treści negatywów. Reprodukcja rachunku nie dowodzi braku skrótów ani przewagi na benchmarkach.
