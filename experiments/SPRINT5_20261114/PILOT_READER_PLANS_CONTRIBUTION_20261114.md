# Breadth / HN / tail: plan readerów do niezależnej recenzji

Status: PLAN_CODE_ONLY; bez implementacji czytnika, candidate access lub zgody na odczyt. Przydział: bounded follow-up od progress_supervisor_luna, według dyspozycji lead; rozszerzenie wcześniejszego zakresu CONTRIBUTION3. Plik należy do `experiments/SPRINT5_20261114/`. Nie zmieniono wspólnego readera, rejestracji ani źródeł fitów. Czytano wyłącznie kod, rejestracje, source/release metadata i istniejącą recenzję paired readera. Nie otwierano rzeczywistych archiwów kandydatów, checkpointów, score'ów ani ich rosterów. Nie wykonano scientific read, nowych testów ani działań klastrowych.

## Najważniejszy blocker naukowy

Wspólne **populacje** primary i camera guards można odziedziczyć dokładnie, ale nie wolno przepisać między pilotami ich **estimandów**. W szczególności tail ma primary false alarms przy niezależnej kalibracji na atakach dla 90% sensitivity oraz zapis o simultaneous 2 pp NI. Paired reader ma kalibrację camera-only (132 osoby, order 127) oraz marginal 95% IUT. To nie są równoważne procedury. Camera panel należy zachować jako osobny wspólny auxiliary panel; nie może zastąpić primary tail bez jawnej, niezależnie ocenionej zmiany prospektywnej przed candidate access. Ten dokument nie dokonuje takiej zmiany.

Podobnie breadth i HN wymagają własnych 95% CI oraz własnych kontrastów/seedów; skopiowanie dwóch kontrastów 97.5% paired-ranking zmieniłoby rejestracje. Reuse oznacza te same ID, komponenty, D edges, source strata, threshold algorithm, floor predictions i guard populations; experiment policy pozostaje osobna.

## Niezmienny wspólny pakiet wejść

Źródło: `paired_ranking/prefit_binding_v1/BINDING.json`, SHA256 `519546ef7002930f620610f01deb0cc4e8889acf819b829a80c05f95fff6e923`.
Referencyjna implementacja: `src/SPRINT5/paired_ranking_reader/SHA256SUMS`, SHA256 `02c7401529a8ca8b2a7af220f7ef36f8cbd8a71ffc50052b0a52f6e2606d1b6c`; niezależna recenzja `paired_ranking/reader_implementation/ASTRA_CODE_REVIEW.md` daje GO_CODE_ONLY, nie GO_METADATA_COLLECTION_ONLY ani GO_READER_READ.

Dziedziczyć przez content hashes w nowym pilot binding, bez kopiowania i edycji samego BINDING:

- `primary_with_D_components.json` = `03202a4afd96ce5e2d65acf1b4285310747efb86983615f95f05abfae221e6ce`: dokładne 200 native S4/S3 na dev100, 40 pełnych komponentów; żadnych historycznych 191 jako inference.
- Fixed log-D edges `[1.9769309018521364,2.3174210341647377,2.5862256441557308,2.8261862388737633]`, pięć strata, równe wagi; brak domyślnego merging i zmiany granic. Primary AUC to średnia po sieciach, nie AUC uśrednionych logitów.
- `calibration_proposal.json` = `4ba959c555339e26275ce209140f882864b32982141d7f0f7de3b221944bbdca`: te same 132 osoby camera calibration, 128 components, oryginalny threshold order 127 ascending, strict `>`; bootstrap k=ceil(.95*(n+1)), infinity gdy k>n. Source-component resampling joint po porównywanych sieciach.
- `genuine_guard_cells_proposal.json` = `7f1c742fa8bd1d81e1183413f7659b41ff6fc94276eeae6ea1cb0799b3167a14`: wszystkie 119 genuine cells oraz ten sam S4 detection cell; ten sam calibration-component exclusion file i geometry-provider unions.
- `primary_floors.csv` = `ea2326dba40b43821e0d92aa864d9d2fead92491b455b3638f18989669bbf6de`: 15 nuisance predictors, maksimum przeliczane we wspólnych bootstrap draws, bez refit/select na wynikach pilotów. Zawsze opisać floor jako conditional na istniejących cross-fitted predictions.
- Pozostałe provenance, data/floor preparation i exclusion pins odziedziczyć z pełnego BINDING, a nie tylko z tej skróconej listy. BINDING zawiera dokładne ścieżki i SHA.

Camera utility panel zachowuje marginal upper 95% bound ≤ +.02 dla genuine i lower 95% bound ≥ −.02 dla detection; all-cells IUT, nie simultaneous-cellwise CI. Zachować support policy min20 niezależnych componentów, zero variance→INCONCLUSIVE, nonfinite→fatal, bez usuwania sparse cells. Z metadata paired readera 52/119 komórek są poniżej20; jest to znane ograniczenie użyteczności, nie powód do ich skreślenia. Nowe treningi mogą dodać overlap, więc przed odziedziczeniem tego panelu należy ponownie sprawdzić osoby/piksele/geometrię **każdego pilota**, zachowując pierwotne populacje. Overlap oznacza HOLD, nie automatyczne odfiltrowanie wiersza.

## Adaptery policy i rostery

| Pilot | Roster i fit | Własny primary | Co wolno odziedziczyć |
|---|---|---|---|
| Breadth SPRINT5_4 | 10 fitów: narrow_more_variants / broad_fewer_variants ×511–515;100steps,batch32,3200forwards;32unique/arm,100 exposures/image | broad−narrow, dev100 S4/S3 D-AUC, descriptive 95% CI,10000draws, RNG2026111404; brak adoption/superiority gate | Dokładne primary rows/D/floors; camera utility dopiero po osobnym binding przed candidate access. Nie importować .03/4-of5 success gate |
| HN SPRINT5_2 | 10 fitów: matched / self ×531–535;100steps,batch248,24800forwards; wspólny Sb408 warmstart | matched−self, dev100 transfer D-AUC;95%two-sided CI, gain≥.03 i≥4/5positive jako descriptive transfer-support; nie adoption | Primary rows/D/full components i floor inputs; camera battery descriptive. RNG i dokładna kolejność draws do jawnego binding, bez cichego defaultu |
| Tail SPRINT5_3 | 15 fitów: bce / mean / cvar ×521–525;100steps,batch256,25600forwards; wspólny Sb408/reference | cvar−mean: genuine FA przy90%sensitivity z independent positive calibration; BCE−mean control;10000draws,RNG2026111403 | Exact camera auxiliary panel i exact dev100 ranking jako descriptive, **nie zamiast primary**. Tail-specific positive partitions/multiplicity nadal do dopięcia |

Breadth seed oznacza łączną wariancję subset allocation/optimizer/dropout. HN i tail są conditional continuation na jednym historycznym warmstart; nie pięć niezależnych bazowych modeli. Żadnego łączenia seedów pilotów lub promowania najlepszego armu do NEXT. Seedy413–417 nienaruszone.

HN rejestracja nie dopina wprost implementacyjnej semantyki CI dla etykiety transfer-support (poza wymienionymi warunkami) ani RNG. Reader nie może sam dodać lower-bound>0, unstratified>0, unreadable threshold lub warunku przewagi nad floor jako nowych primary verdict gates. Należy dopiąć interpretację w prospectively reviewed policy przed score access. Raportować floor i unstratified jako descriptive zgodnie z rejestracją. Breadth „paired seed triplets” jest pozostałością nazewniczą: ma dwa ramiona; generator bootstrap powinien wspólnie resamplować pięć **par**, z jawną korektą dokumentacji przed read.

## Wspólny schemat metadanych (projekt, bez permissive release)

Każdy pilot otrzymuje własny `PILOT_READER_BINDING.json`, `EXPECTED_PLANS.json`, immutable `READER_ROSTER.json`, source manifest i osobny journal. Nie parametryzować przez dowolny CLI arm/seed/path bypass. Proponowane minimalne pola:

```text
binding: schema_version, experiment_id, scope, prereg_path/sha256,
  pilot_release_path/sha256, source_sums_sha256, arms, seeds,
  expected_fit_count, checkpoint=last, steps,batch_size,forwards,
  shared_input_binding_sha256, exact_input_pins,
  primary_policy, calibration_policy, guard_policy, support_policy,
  comparator_map, rng_streams, expected_plans_sha256,
  provenance_audit_path/sha256, reader_sums_sha256
roster_entry: experiment_id, arm,seed,task,archive_path,archive_sha256,
  receipt_path,receipt_sha256
fit_envelope: roster identity + metadata_only disposition,
  source/train/eval_manifest hashes, model/optimizer/software/GPU,
  steps,limit=0,last-checkpoint presence,finite-loss/completion,
  reference_gate(n2496,zero difference),ownfit_gate(n21277,zero difference),
  battery_sets(dev21277,tt134411,meds1018,gd11042),
  exact score-member allowlist/digests copied from scorer metadata,
  schedule/exposure receipt, warmstart/reference hashes where applicable,
  collector_review_sha256, payload_boundary
```

Training-specific assertions: breadth32unique and exact100/image plus perperson/source/orientation inventory for eachseed; HN124 identical positive images+124 negatives, exact matched/self pixel/contributor invariants and control124/exclusion pins; tail identical100-step schedule/exposure across all3arms,118camera+128positive+10other perstep, exact reference/eta/dual state **presence and metadata integrity**. Tail traces must not become a shortcut for inspecting candidate scientific results during metadata collection; any numerical objective/training diagnostic outside finite/completion eligibility requires explicitly allowed scope. No model loading.

Collector should parse only fixed JSON/TXT/LOG metadata members, never NPZ/weights; archive headers establish checkpoint/member existence, scorer metadata supplies expected score digests. After separate release and permanent claim, payload loader verifies full member bytes, complete finite float32 arrays, manifest IDs/order/hash, exact ownfit/battery equality, and returns **only exact allowlisted populations**. Historical191 remains opaque/platform-only. All10/10/15 exact fits needed unless an existing pilot-specific independently bound failure policy explicitly says otherwise; never silently copy paired reader's15-count or4/5fallback.

## Źródła i source pins do review

Sprawdzone SHA256 samych manifests/rejestracji podczas tego planowania:

- shared reader SHA256SUMS `02c7401529a8ca8b2a7af220f7ef36f8cbd8a71ffc50052b0a52f6e2606d1b6c`;
- shared prefit BINDING `519546ef7002930f620610f01deb0cc4e8889acf819b829a80c05f95fff6e923`;
- `src/SPRINT5/breadth_fit/SHA256SUMS` `debbea9496cdcd553cf2b18671f0868452cfdc9cc16fa7ee66b0e81b97361a04`;
- `src/SPRINT5/tail_fit/SHA256SUMS` `9b50eff7aa5a90f72be7330e3550b0f8a76917dcac9b89516cc0a64ae7086ae1`.

HN source manifest in bound `hn1/PILOT_RELEASE.json`: `3640adc6a2204e1d82ce455167e00e433859f4b63bf63970f67d3ca0910ca793`, source folder `src/SPRINT5/hn1_transfer/`. HN release also binds prereg `a0c8c18259d9b7ee5e78f2768178f017cbcf2a63616cbb7b935324f5dda8c266`, control receipt `4e32562e7e450fc4ea0304f01cfe85a85e97606ca7ba8a85c483777fb053d3b8`, exclusion audit `dca24cd494baa21c3f37f7683704b0340e0dacae40a1db06fa09feccbb3893cb`. These are transcriptions of release metadata, not fresh archive validation. Warmstart/baseline hashes remain as written in pilot releases; no bytes opened here.

Before implementation freeze, hash **all transitive reader source files**, copied policy snapshots, exact runtime plans and independent reviews. Do not rely on filename or current checkout HEAD. Existing paired `admit.py` hardcodes3arms/501–505/6250steps/trainSb/schedule and task prefixes: direct reuse is incompatible. Prefer a reviewed immutable policy adapter around pinned statistical/metadata utilities, with exact experiment-specific admission, rather than broadening the approved paired reader in place. New versions have separate source hashes; existing GO_CODE_ONLY cannot approve them by inheritance.

## Code-only synthetic test plan

1. Generated fixtures for exact10/10/15 roster; duplicate task/hash/path, wrong seed, lost arm,100vs2smokesteps,6250wrong schedule, source/prereg/review hash mismatch all reject before payload.
2. Invalid NPZ and invalid checkpoint fixture bytes still permit the fixed metadata parser to inspect allowed fields; sentinel tracking proves no payload deserialization. Unknown/duplicate/oversize metadata members reject.
3. Exposure invariants: breadth100/image and two arm actual IDs; HN shared positive rows/samewarmstart/control pins; tail exact identical schedules, four positive families, correct camera group and no auxiliary inclusion of non-camera controls. Generated counterexample for each invariant.
4. Exact borrowed200primary/132camera/119guard ID order, immutable D edges, all15floor max recomputation, full graph/source stratification and geometry union. Generated historical191 extreme sentinel cannot affect returned data or estimates.
5. Mean per-network AUC versus score fusion; paired seed/component resampling; deterministic RNG streams honoring each registration. Bootstrap pair labels cannot become independent perarm seed draws. No assumption that shared fixed metadata requires identical random seeds across different registered pilots.
6. Camera threshold127/132 strict>; ties, missing calibration, infinity behavior; joint calibration/seed draws; uniform score-shift counterexample demonstrates that fixed-zero false-alarm reduction is not matched-utility improvement.
7. Support min20, zero variance, all119+1 IUT; sparse/nonfinite handling; favorable ranking with inconclusive guard remains two distinct statuses. No reduction of119cells to eligible subset.
8. Tail-specific positive threshold and simultaneous NI tests only after their exact algorithm/partitions/multiplicity are bound. Synthetic example must fail if camera quantile is used in place of90%-positive-sensitivity threshold, or marginal IUT is labeled simultaneous coverage.
9. Read admission/claim ordering with injected failures before/after claim; create-only/fsync journal perpilot, no overwrite/retry via new output path; atomic result publication and terminal hash. `--admit-only` must touch no score arrays and consume no claim.
10. Differential tests against exact pinned paired statistical functions for generated equal-policy camera panels; pilot-specific primary output intentionally differs where prereg95%/RNG/contrasts differ. CPU execution only, isolated Python/thread caps; no generated fixture from candidate output.

Oczekiwany wynik testów to pass/fail code behavior, nie scientific pilot result. Plan nie deklaruje, że nowe testy już wykonano.23 synthetic tests paired readera są wcześniejszym zrecenzowanym wynikiem tamtego pakietu, nie testami nowych adapterów.

## Gates i remaining dependencies

1. **Policy pre-read review:** root + niezależny statistics reviewer rozstrzygają tail positive calibration/simultaneous confidence oraz HN unspecified details; dopinają camera auxiliary scope wszystkich3pilotów, nie zmieniając training/selection. Zachować „descriptive”, fixed seeds/steps i wspólny warmstart.
2. **Provenance metadata:** wykazać brak overlap nowych training pixels/persons/shapes z odziedziczonymi200primary/132calibration i guard exclusions; aktualne full expected schedules. Jeśli problem, STOP i jawna prospektywna decyzja, nie ciche usuwanie obrazów. Tail potrzebuje independent positive calibration i heldout attacks z pełnym component separation; dostępność takiego splitu nie została dowiedziona w tym planie. Bez niego primary tail HOLD nawet przy kompletnych fitach.
3. **Implementation and independent GO_CODE_ONLY:** osobne sources/adapters, wszystkie synthetic tests, bounded candidate-free input metadata checker. Zero real archive access.
4. **Root GO_METADATA_COLLECTION_ONLY:** osobny source-bound collector review, opaque roster/hashes oraz pełne10/10/15 eligible final outputs; independent review i staging paths związane hashami. GO_PILOT fit nie jest reader release.
5. **Root GO_READER_READ:** exact immutable augmented roster+envelopes, admission input checks, wszystkie required gates, independent reviewer≠author, exact source manifests/policies/reviews i perpilot permanent claim location. Nie invokować NEXT selector.
6. **One permitted read and independent conclusions review:** po permanent claim, bez restartu na alternatywną ścieżkę; failed/partial records zachować. Oddzielnie optimization/descriptive transfer, camera utility oraz tail primary. Żadnego automatycznego successor adoption, benchmark read lub zmiany manuscript claim.

Na dziś plan blokują: nieistniejące jeszcze odrębne reader implementations/admission bindings i reviews; brak tu potwierdzonego pełnego final-fit roster; niezamknięta tail positive-calibration/multiplicity spec; HN RNG/CI-verdict details; nowe pilot-specific provenance dla wspólnej camera kalibracji. Sama obecność GO_PILOT i source pins nie rozwiązuje tych braków. Priorytet implementacji: breadth (najprostszy descriptive adapter), HN po dopięciu policy, tail camera auxiliary równolegle z przygotowaniem oddzielnego primary; żadnego scientific access dla przyspieszenia projektu readera.

CLAIMS:
- file shared BINDING sha256 519546ef7002930f620610f01deb0cc4e8889acf819b829a80c05f95fff6e923 (sprawdzono plik)
- file paired reader SHA256SUMS sha256 02c7401529a8ca8b2a7af220f7ef36f8cbd8a71ffc50052b0a52f6e2606d1b6c (sprawdzono plik)
- number primary_rows=200;camera_people=132;genuine_cells=119 @ paired_ranking/reader_implementation/ASTRA_CODE_REVIEW.md (transkrypcja metadanych recenzji)
- No candidate archive/score/checkpoint access; no tests or scientific reader execution; no cluster action; no commit.
