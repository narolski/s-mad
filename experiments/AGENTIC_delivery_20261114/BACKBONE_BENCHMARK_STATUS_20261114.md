# Porównania backbone’ów i tabele przed/po — audyt i plan, 14 listopada 2026

**Odpowiedź: historyczne porównania istnieją; nie znaleziono natomiast kompletnego porównania bieżącego protokołu Sb przed/po na tych backbone’ach.** Nie należy od zera powtarzać istniejącego W3 ani sklejać jego liczb z aktualnym corrected MAD22.

Audyt obejmował kuratorowane README, protokoły i już dopuszczone teksty wyników. Nie otwierano raw score JSON/NPZ, checkpointów ani zamkniętych benchmarków; nie wykonano inferencji, readera ani działania klastra. Statusy poniżej są dokumentacyjnym audytem, nie ponowną reprodukcją wyników. Pełne hashe źródeł i strukturalne wiersze: BACKBONE_BENCHMARK_STATUS_20261114.json.

## Co faktycznie wykonano

A9-W3_frozen-list/README.md ma aktualny status `analysed`: 260/260 sieci W3 i 36/36 LOTO, każde scored once na VALX-A*, eval i gtest, z odnotowaną niezależną kontrolą 147894 porównań bez błędu. W3 używał dziesięciu świeżych seedów 11–20. Wyniki były opisowe; właściwy endpoint claimu FST-U nie został dostarczony/wyliczony. Starsze sekcje tego samego README zawierają historyczne „jobs none/not started”; nie traktuję ich jako nowszych od aktualnego statusu/Results.

| Model / pretraining | Historyczne MAD22 | Historyczne FRLL-Morphs | Bieżący Sb: ten sam backbone przed/po |
|---|---|---|---|
| ConvNeXt-T, scratch (L0) | wykonane, bezpośrednia tabela README | wykonane, bezpośrednia tabela README | nie znaleziono |
| ConvNeXt-T, ImageNet-1k (L1) | W3 programme-level completed | W3 programme-level completed | nie znaleziono |
| ConvNeXt-T, ImageNet-22k (L2) | W3 programme-level completed | W3 programme-level completed | nie znaleziono |
| ConvNeXt-T DINOv3 (L2) | W3 programme-level completed | W3 programme-level completed | nie znaleziono |
| VMamba-T (L1), VMamba-S/B (L2) | W3 programme-level completed | W3 programme-level completed | nie znaleziono |
| MambaVision-B-21K (L2) | W3 programme-level completed | W3 programme-level completed | nie znaleziono |
| Vision Mamba / Vim | brak zweryfikowanego completed entry w sprawdzonych źródłach | jw. | nie znaleziono |
| Bieżący Sb, CLIP ViT-B/16+LoRA | corrected FINAL read, 5 seedów 403–407 | bieżący final read nie znaleziony; obowiązują sealed gates | aktualne ablations istnieją; brak całego backbone factorial |

„Programme-level” oznacza, że ukończenie oraz roster są udokumentowane przez zarejestrowany W3/kuratorowane źródła, lecz ten bounded audyt nie odczytywał per-model score arrays ani nie przepisywał wszystkich historycznych liczb. Bezpośrednio w kuratorowanej tabeli L0 znajdują się przykładowo:

| Historyczny model W3, d1, 10 seedów | MAD22 EER % ↓ | FRLL-Morphs EER % ↓ |
|---|---:|---:|
| MADMamba E10 | 14.72 | 13.61 |
| ConvNeXt-T scratch | 12.99 | 21.86 |
| ResNet-50 scratch | 9.81 | 8.64 |
| EfficientNet-B4 scratch | 21.15 | 11.96 |

**Ta tabela jest historycznym kontekstem, nie porównaniem aktualnego Sb.** W3 stosował E7 bona-fide pool i EER capped at 50; checkpointy i recipe/rozdzielczość różniły się. Bieżące 3.37% Sb dotyczy corrected MAD22, czterech rodzin (bez shortcut-saturated FaceMorpher), history-matched genuine versus SelfMAD raw-genuine. W3 headline „MAD22” nie jest tym samym estimandem. Nie wyliczać różnicy 3.37−12.99 ani nie pisać przewagi z takiego zestawienia.

## Ważne rozróżnienia

1. **Vision Mamba (Vim), VMamba i MambaVision to odrębne implementacje/model families.** Oficjalne źródła sprawdzone 14 XI: [Vim](https://github.com/hustvl/Vim), [VMamba](https://github.com/MzeroMiko/VMamba), [MambaVision](https://github.com/NVlabs/MambaVision), [ConvNeXt](https://github.com/facebookresearch/ConvNeXt). Obecność VMamba nie potwierdza eksperymentu Vim.
2. W2-L1/L2 dobierał konfiguracje na VALX-A*, a nie na MAD22/FRLL; W3 później raportował wyniki opisowe. Sześć seedów W2 nie jest dziesięcioma seedami W3. Scratch/IN1k/IN22k/DINOv3/CLIP wymagają osobnych etykiet, nie jednego rankingu „uczciwych backbone’ów”.
3. MambaVision ma także nowszą, odrębną gałąź A30. Accepted A/A replay z 10 XI jest technicznym wynikiem tolerance-close, nie nowym benchmarkiem ani production GO. Nie nadpisuje historycznej tabeli W3.
4. Starszy PROTOCOL jawnie nazywa MAD22 **i FRLL-Morphs** development datasets. Aktualny FRLL ma ograniczenia dostępu, ale nie jest globalnie nowy dla projektu. Dodatkowo bieżące Sb zostało wybrane po wcześniejszych MAD22 scores, a 204 genuine FRLL photos /102 persons były dostępne w MAD22. Nowe seedy nie usuwają tej ekspozycji.
5. W materiale z 8 XI występuje MAD22 subset185 genuine/4069 morphs, a późniejszy current FINAL wykorzystuje corrected population204/4483. Każda tabela musi mieć n i wersję; nie scalać ich w jedną kolumnę bez bridge audit.

## Tabele, których potrzebuje obecna praca

**Tabela A — efekt zmiany wejścia, bez zmiany modelu:** model/checkpoint/seed; ta sama fotografia oryginalna → resize/history/otoczenie; baseline score; transformed score; Δlogit; decyzja wyłącznie przy uprzednio dopuszczonym progu; liczba obrazów/komponentów i ograniczenie. Pure JPEG/blur osobno od złożonej historii. To najprostsza prezentacja skrótu dla czytelnika.

**Tabela B — efekt protokołu, ten sam backbone:** dwie ramiona „reference” i „matched-control protocol”, osobno pięć seedów i paired Δ; identyczna pozytywna populacja i wyrównane ekspozycje/masy klas. Zmienia się konstrukcja negatywów; remaining unique-image/content diversity confound musi zostać jawny. Pokazać S4 attack sensitivity przy zamrożonym source-independent operating rule, genuine FA, S3-control flags i reakcję na processing; nie zastępować tego samą AUC.

**Tabela C — benchmark per-family, before/after protocol:** backbone+pretraining+adaptation → before EER → after EER → Δpp, obok APCER przy dev-calibrated threshold i zrealizowane BPCER. MAD22 rodziny osobno, landmark-only i fixed four-family means z wymaganymi caveats; FaceMorpher oddzielnie. FRLL rodziny osobno, zgodna historia genuine/morph i fixed threshold transfer. Brak wyniku to `NOT_RUN`/`NOT_ADMITTED`, nie zera ani szacowana liczba.

| Backbone / adaptation | MAD22 przed | MAD22 po | Δpp | FRLL przed | FRLL po | Δpp | Genuine FA przed→po | status |
|---|---|---|---|---|---|---|---|---|
| CLIP ViT-B/16, LoRA | exact matching admitted reference or NOT_ADMITTED | exact matching admitted protocol | only same estimand | gated | gated | gated | fixed dev threshold | reuse audit |
| ConvNeXt-T IN1k, full FT | NOT_RUN | NOT_RUN | — | NOT_RUN | NOT_RUN | — | NOT_RUN | first new cross-backbone pair |
| VMamba-T IN1k, full FT | NOT_RUN | NOT_RUN | — | NOT_RUN | NOT_RUN | — | NOT_RUN | second pair |
| Vim-T, exact official checkpoint TBD | NOT_RUN | NOT_RUN | — | NOT_RUN | NOT_RUN | — | NOT_RUN | optional third pair |

## Prospective execution plan — no run release

**Stage0, CPU provenance/reuse audit first.** Freeze one table manifest with exact old/current input populations, source-photo/person/component overlaps, alignment/resize/codec history, training image IDs/exposure counts, checkpoint rule and weights hashes. Historical W3 used its registered checkpoint policy (not assumed last); current new experiment uses last only. Existing rows are reused only if all requested before/after factors, data, seeds, preprocessing and checkpoint rule actually match. Otherwise they stay labelled historical and we do not spend GPU merely to relabel them. Do not open historical per-image score members under a general narrative permission.

**Stage0b, recompute existing checkpoints versus retrain factorial — separate decisions.** If the goal is a current common-evaluator *pipeline leaderboard*, the cheapest route is metadata-only inventory of existing W3/current checkpoints followed by separately registered/admitted scoring of a fixed roster on the same corrected inputs. This can produce a comparable evaluator table without retraining, provided exact input identity, checkpoint identity and each original runtime's byte gate pass. It retains differences in historical training data/pretraining/adaptation/checkpoint policy and does not establish the effect of our matched-control protocol. It must never overwrite original W3 numbers or retroactively change their verdict. Existing score reuse is possible only under exact permission and row/transform/threshold identity; otherwise planned re-scoring is a new read, not a free conversion.

If the goal is *before/after our protocol for each backbone*, a genuine matched pair of reference/protocol checkpoints with five seeds and identical registered budgets is required. Existing W3 endpoints are generally not those paired treatments. Retrain missing pairs after the metadata reuse audit. Current CLIP pairs may be reused only if their exact two training compositions/schedules match the newly fixed contrast; SPRINT warmstart pilots and historical E10/MADMamba cannot stand in. Remaining truly untouched benchmark scope is UNKNOWN until source/version exposure audit; historical FRLL development use plus current restricted release must be disclosed separately. No claim of globally unseen FRLL follows from a newly gated reader.

**Stage1, minimal meaningful new comparison: ConvNeXt-T IN1k ×2recipes ×5seeds =10full fits.** Use the already registered count-balanced training-control populations and schedule once their exact source/input bindings are selected for this new study; do not inherit SPRINT warmstart pilots as full retrains. Choose five new seeds unused by the selected checkpoints after a metadata ledger check, not fixed here by guessing availability. If current CLIP's exact corresponding control/protocol5+5 fits are reusable, no CLIP refit; otherwise add10CLIPfits under the same study. This reuse question is a blocker before a resource quote.

**Stage2, VMamba-T IN1k ×2recipes ×5seeds =10additional fits.** Start only after code/preprocessing/numeric/complete-epoch gate. VMamba here is not Vim. Optional Vim-T adds another10fits if the actual requested family is important and dependency support passes. MambaVision-B21k is an optional separate-pretraining league, not mandatory under deadline; its known technical trajectory gates must be resolved before submitting.

**Fairness.** Freeze training populations/labels, exposure multiset, class/positive balance, augmentation and final resolution across architectures. Each architecture gets the same bounded development-only tuning allowance, specified candidate values and decision criterion before data; freeze then full fits. Report adaptation policy: CLIP LoRA versus full CNN/SSM FT is a pipeline comparison, not isolated architecture effect. If architecture causality is desired, separately register matched adaptation—not claim it from LoRA versus full FT. Report exact pretraining and licences, total/trainable parameters, updates/forward exposures, measured time/GPUh and memory. Equal exposures do not equal equal compute; report both, do not silently change schedule to make walltime equal.

**Stage3, development gates and threshold freeze.** Audit training/calibration/evaluation person/photo/component disjointness for each architecture; all variants of one image in one component. Use only approved development controls to bind operating points, uncertainty/multiplicity and selection; benchmark results cannot choose architecture, augmentation, seed, threshold or a protocol. Missing family support yields visible INCONCLUSIVE, not dropped rows. A five-seed paired bootstrap of dependent components and continuation/full-training seeds must match the estimand; do not reuse conditional fitted-network CIs as general training-population uncertainty. Freeze one primary protocol-effect contrast and multiplicity over backbone-specific claims prospectively; never choose the largest backbone gain.

**Stage4, gated MAD22/FRLL evaluation once.** Corrected MAD22 is development-exposed, all versions/denominators/family weights/history frozen. FRLL still requires existing gatekeeping/admission and a source-overlap/exposure ledger; planning does not authorize a fresh read. First fix the permitted roster, actual platform byte gate, source IDs and complete results rule; independently review, obtain exact lead release and once-only execution journal. Report uncapped EER (with orientation sanity) and all failed/missing seeds rather than importing W3's cap50. Print per-family and full-table outcomes even when unfavorable. New experiments do not silently amend NEXTv3 selection/fresh413–417.

**Resources/readiness.** New H100-only code stays on WCSS; Athena only for separately verified compatible A100 runtime and actual available association. Prefer real `srun --pty` short technical smokes in lem-gpu-interactive under durable launcher; no sbatch substitution to that partition. All cluster contacts/mutations remain lead-owned under the shared flock; no work was submitted by this audit. Source freeze, requirements/weights/data pins, numeric smoke, independent pre-run review and exact output/durability receipts precede training. Use TMPDIR plus FORCE_RM_TMPDIR, create-only results, fresh remote/local/sidecar hashes to T7.

No defensible measured new-backbone runtime is available in this bounded audit. Historical W2-L2's132runs consumed100.3GPUh, but different recipes/resolutions/GPU setups make that unsuitable as a current quote. First measure a reviewed representative short smoke per model; derive total walltime using the unchanged full-step count plus setup/scoring/copy margin, then bind the full budget. Baseline roster is20newfits without optionalVim and without extraCLIPfits; 30withVim; add10only if exactCLIPreuse fails. Tuning trials, smokes, scoring and CI work are additional and must be budgeted explicitly. Capacity/price unknown, no paid capacity requested or used.

## Immediate actions

1. Integrate already-admitted current before/after tables A/B with exact source references and limits now; do not delay them for a new backbone sweep.
2. Keep the historical W3 context in a separate appendix table with n/recipe/checkpoint/evaluator version and capped-versus-uncapped explanation. Do not splice it into current corrected MAD22.
3. Register the smallest ConvNeXt10-fit factorial, with the CLIP reuse decision and raw scientific read permissions explicit; independent methodological/code review before executable launch.
4. Queue VMamba's10-fit extension; Vim/MambaVision optional separate rows. Preserve all statuses `planned`, `source-ready`, `smoke-pass`, `fit-complete`, `scientifically-admitted`, `reviewed-result` as different states.

This audit supplies a plan, not permission to open benchmark outputs, launch jobs or claim superiority. No current manuscript/main/WIP was modified.
