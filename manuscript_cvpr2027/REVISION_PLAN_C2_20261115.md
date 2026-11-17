# Revision plan C2 — CVPR 2027 `manuscript_cvpr2027` (2026-11-15, v1.1)

Plan wykonawczy na bazie `INDEPENDENT_REVIEW_C2_20261115.md` (recenzent: niezależny C2,
przeczytany przy commicie recenzji `c1fa73d`, manuskrypt w stanie HEAD `1dc1581`).
Weryfikacja numeryczna recenzenta: **PASS** (zero rozbieżności, ~60 par wartość↔raport;
pełna rekomputacja z surowych logitsów poza zakresem — granica weryfikacji Batch-C,
patrz `REVIEW_AB1_BATCHC_OPENCODE_20261114.md`). Werdykt: **MAJOR REVISION**.
Recenzja zawiera **7 blokerów** (nie 6 — tabela poniżej 1–7) oraz **6 usprawnień**
istotnych; plan obejmuje wszystkie.

Ten plik jest planem, nie wdrożeniem: nie edytuje `.tex` poza niniejszym plikiem.

**Zmiany v1.1 (razy decyzja autorska):** A-D1 rozstrzygnięta — autor wydał author-ruling
unsealing odczytu FRLL-Morphs (z formalnym amendmentem preregu; odczyt audytowalny).
Komórki FRLL-Morphs w Tabeli 5 **zostają w submisji i zostaną wypełnione** danymi.
Pozostaje otwarte: uprawnienia/licencje do FRLL i pozostałych datasetów (B6/A-D5).
Zgodnie z tym wzmocnione: pełny exposure map i sekcja etyczna **muszą** obejmować FRLL.

---

## A. Tabela zmian

Kategorie: `auto-fix` = trywialne i bezpieczne, kandydat do commitu bez decyzji;
`decyzja` = wymaga decyzji autorskiej (rozdział B); `obliczenia` = wymaga nowych
odczytów/przebiegów; `składka` = praca składania z admitted materiałów (bez GPU).
Koszt: S ≤ 1 h, M = pół dnia, L = dzień+.
Miejsca obliczeń: **WCSS** (H100, jedyne dozwolone miejsce treningu), **Athena** (A100 —
projekt `plgmorphgeneral` nadal niedostępny w Slurm, patrz `COMPUTE_POLICY.json` — nie
planować tam), **DGX-GB10** (lokalnie; wystarcza dla scoringu FRLL wg sondy
`FRLL_READY_PLAN_20261115.md`: ~1–3,5 min GPU/model-seed przy batch 1 na 7 127 wierszach).
Ograniczenie globalne: żadna liczba/tekst nie wchodzi do wersji wysyłkowej bez źródła
w admitted report (odczyt FRLL wchodzi dopiero po niezależnym postresult review).

### Blokery (1–7)

| # | Bloker (recenzja) | Konkretne zmiany — co / gdzie / na co | Kategoria | Koszt | Zależności |
|---|---|---|---|---|---|
| B1 | Notatki WIP kompilowane do PDF: `results.tex:3` (`\input{publication_wip}`) wciąga `publication_wip.tex:1–7` ([WIP–TRANSFER], [WIP–CONFIRMATION], [WIP–REPRODUCIBILITY]) | 1) Usunąć `\input{publication_wip}` (`results.tex:3`) i wyłączyć plik z bundla. 2) Treść WIP–TRANSFER (brakujący akapit threshold-transfer TT1/MEDS) odtworzyć jako paragraf „Threshold transfer" — źródło istnieje i jest admitted: `supplement_threshold_transfer.md` (konsolidacja TT1/TT1-FS/Z1-Z4/X/MEDS z hashami). Umiejscowienie wg decyzji A-D7. 3) Nakazy WIP–CONFIRMATION i WIP–REPRODUCIBILITY zamknąć pozycjami B2/B3; co pozostaje niedokończone → backlog tego planu, nie PDF. | auto-fix (removal) + składka (paragraf TT/MEDS) | S | A-D7; supplement build (B3) |
| B2 | Obiecany „companion appendix" nie istnieje; odwołania wiszą w `results.tex:76, 114, 132, 173`; `results.tex:114` jest nośne dla twierdzenia NOT_QUALIFIED (119 cell guards) | Utworzyć `appendix.tex` (input przez `main_supp.tex`, NIE przez 8-pagowy main) i zasilić wyłącznie z admitted: (a) pełne tabele per-seed i component hypotheses z `AB1_protocol-ablation-and-replication/result.md` + `ab1_tables.md`; (b) 119 TT1 genuine-cell guards × 15 sieci × 2 polityki progów z `supplement_threshold_transfer.md` / reports TT1; (c) full operating errors + protocol coverage dla Tabel 4–5 z `FINAL_sealed-benchmark-read/result.md` + `final_tables.md`; (d) three-arm/per-seed/null-cell accounting SPRINT5 z raportów POSTRESULT w `SPRINT5_20261114/{breadth,hn1,paired_ranking,tail}`; (e) inventaria armów/liczby hostów z `AGENTIC_delivery_20261114/SOL_REPRODUCIBILITY.md` (spójne z `supplement_reproducibility.tex`); (f) **nowość v1.1**: zarezerwować sekcję pod wyniki FRLL-Morphs (per-seed, progi, NIE oddzielne z ad-hoc selekcji) — patrz B4. Zaktualizować 4 odwołania w `results.tex` na realny obiekt. | składka | M–L | B3; forma wg A-D6; dane FRLL do slotów (B4) |
| B3 | `supplement_reproducibility.tex:1–2` „Proposed supplement fragment; no main file inputs this yet" — brak supplement PDF i CVPR checklist | 1) Usunąć komentarze nagłówkowe linii 1–2. 2) Utworzyć `main_supp.tex` (ten sam stack cvpr.sty, anonimizacja zachowana) inputujący: `supplement_reproducibility.tex` + `appendix.tex` (B2) + rozdział ethics/exposure (B6) + registered-verdicts summary (U3). 3) Skompilować `main_supp.pdf`, dołączyć CVPR paper checklist 2027. 4) Włączyć do repo (untracked!): `preamble.tex`, `supplement_reproducibility.tex`, `references.bib`, `figures/` — git add + commit. | auto-fix (git add, odesłania) + składka | M | B2; A-D6 |
| B4 | Panel HOLD w Tabeli 5 (`results.tex:162–173`): tabela 5 metod × 5 rodzin, każda komórka „HOLD"; linia 173 „new reads remain gated" | **ZMIANA v1.1 — decyzja podjęta (A-D1): komórki zostają i zostaną WYPEŁNIONE.** Zaprojektować Tabelę 5 (właściwie: drugi panel Tabeli 4/5) pod pełne wyniki: (i) układ: Method/Form (S vs H) × rodziny AMSL, FaceMorpher, OpenCV, StyleGAN, Webmorph — analogicznie do panelu MAD22, EER (%); rozbudować o kwalifikatory: per-family attack-miss i genuine-FA przy development-frozen threshold (pole z preregu FINAL/FRLL), per-seed SD dla Sb (jak U6); (ii) podpis tabeli definiuje S/H i deklaruje ekspozycję (204 FRLL genuine, 102 osoby, przez MAD22) + odesłanie do author-ruling i formalnego amendmentu preregu; (iii) **miejsce na wzmiankę o rulingu/amendmentie**: dedykowany paragraf „Author ruling and prereg amendment" w supplement (provenance/policy) + jedno zdanie w podpisie tabeli main — zamiast obecnych 5×5 „HOLD"; (iv) usunąć linię „HOLD = …; new reads remain gated" i zdanie „new reads remain gated" z `results.tex:173`; (v) komórki wypełniać TYLKO wartościami z admitted FRLL read (single-pass; wyniki przyjdą od cvpr-continuation i wchodzą dopiero po postresult review); kwalifikatory negatywne/niekonkluzywne retentionować, nie usuwać; (vi) zero re-readów: jedno zamrożone manifest-ready odczytanie wg `FRLL_READY_PLAN_20261115.md`. Do czasu przyjścia wyników scaffold struktury tabeli pozostaje wyłącznie w planie; panel z komórkami HOLD nie może trafić do review PDF — finalny wariant podmienia panel całościowo. | składka (projekt tabeli) + obliczenia (fill z admitted FRLL report) | M (projekt) + S (GPU, patrz Obliczenia) | amendment preregu (użyte, audytowalne); gates 1–5 `FRLL_READY_PLAN_20261115.md`; B6 (udostępnienie FRLL w exposure/ethics); postresult review FRLL |
| B5 | Draft title i draft LLM disclosure: `main.tex:10` („Integration review draft" w tytule); `main.tex:58–59` („draft … authors must verify … finalize") | 1) Tytuł: usunąć `\\{\normalsize Integration review draft}`; tytuł finalny wg A-D3. 2) LLM statement: przepisać na ostateczny, weryfikowalny disclosure wg CVPR 2026+ policy (co/jakie narzędzie/które etapy), po potwierdzeniu przez autora zakresu historycznego Claude/OpenCode (A-D4). Placeholder wysyłkowy musi być definitivny, nie „draft". | auto-fix (usunięcie posfixu tytułu) + decyzja (finalny tytuł i statement) | S | A-D3, A-D4 |
| B6 | Prawa do datasetów + brak ethics/broader-impact dla metody attack (FRGC, colorFERET, FFHQ, SMDD, FRLL, MAD22/FRLL-photos) | **Wzmocnione v1.1: FRLL wchodzi do obowiązkowego zakresu** (obecnie także na stronie wyników, nie tylko jako genuine w MAD22). 1) Zebrać licencje/uwagi redystrybucyjne per dataset: FRGC (NIST), colorFERET (umowa), FFHQ (non-commercial, Flickr), SMDD, FRLL (psicofatale), MAD22 (publikacja), **FRLL-Morphs (to teraz pozycja obowiązkowa)**. 2) Rozdział „Ethics and broader impact" w supplement: responsible disclosure ataku, brak identyfikacji contributorów poza publicznymi zdjęciami badawczymi, use tylko badawczy, plan udostępnienia (scores/preprocessing, bez obrazów osób trzecich). 3) Exposure map: dodać pełną ścieżkę FRLL: 204 genuine w MAD22 → dev-exposure → unsealed FRLL-Morphs read (ruling + amendment, data rulingu, można wprost w supplement provenance). 4) Usunąć „dataset rights remain unresolved" z `supplement_reproducibility.tex:24` dopiero po rozstrzygnięciu rights (to zostaje otwarte, patrz A-D5). Sekcję etyczną napisać niezależnie od stanu rights — z jawnym stwierdzeniem statusu licencyjnego per dataset. | decyzja (A-D5, rights) + składka (napisanie sekcji) | M | A-D5; B4 (exposure FRLL) |
| B7 | Untraceable „registered composite rendering verdict" (`results.tex:15`) — brak takiego werdyktu w admitted; PR1 ma: GD1 „render path used" (5/5, A/B/Sb), GD2 „inconclusive" (A/B/Sb; R2 flag ≥ 50% na 5/5 A i Sb, 3/5 B), Z2a joint operational 2/5 | Zamienić zdanie na faktyczne registered verdicts, np.: „The registered render-path verdict is *used* (5/5, GD1) and the registered MIPGAN-control verdict is *inconclusive* (GD2), with one-photo renders flagged at 78–90%." + `% Source: experiments/PR1_protocol-reads-existing-networks/result.md, GD1/GD2`. Alternatywa (zdecydowanie odradzana w tym cyklu): zarejestrować nowy kompozytowy werdykt prioregem. | auto-fix (kandydat; zdanie nośne — autor zatwierdza formulację) | S | — |

### Usprawnienia (U1–U6, nieblokujące)

| # | Usprawnienie (recenzja) | Konkretne zmiany | Kategoria | Koszt | Zależności |
|---|---|---|---|---|---|
| U1 | Reintroduce render-controls table — bare ranges w `results.tex:15` | Kompaktowa tabela 3 ramy (A, B, Sb) × {R2-vs-R0 AUC, R4-vs-R3 AUC, % flag one-photo renders} z `PR1/result.md` GD2; placement po `results.tex:15`. | auto-fix | S | po B7 |
| U2 | Abstract o storage attenuation: „The full protocol attenuates storage-induced false alarms." (`main.tex`, abstract) | Doprecyzować: „…, at the trained image size; the registered combined storage verdict remains inconclusive (5/5 trained, 3/5 untrained seeds; score-movement failures)." zgodnie z R1/AB1. | auto-fix (kandydat) | S | — |
| U3 | Qualification density: tabela „registered-verdicts summary" (claim → verdict → population → interval type) | Zestaw ~12 zarejestrowanych werdyktów (XF1, AB1 R1/C2P/H, Batch C, PR1 GD1/GD2/Z2a, AD4, SPRINT5 breadth/HN/ranking/tail, FINAL; **v1.1: dodać słotkom FRLL-Morphs po odczycie**) z odnośnikami do admitted reports. | składka | M | B2/B3 (miejsce); B4 (slot FRLL) |
| U4 | Populacje raz centralnie (clean80, 69-host sensitivity, 11/80 shape-links, dev/clean split) | Jeden paragraf „Populations and exposure" w method.tex §Evaluation lub supplement (A-D7); odwołania z `results.tex` §training_results. **v1.1:** paragraf obełmuje też FRLL pipeline (MAD22 exposure → unseal). | składka | S/M | A-D7 |
| U5 | Fig. 1 = schemat tekstowy; VIS1 gated | Opcja A: zostawić + wzmocnić podpis. Opcja B: render graficzny drabinki konstrukcji lub D-stratyfikacji (bez gated example images). | decyzja (A-D9) | M–L | FIGURES owner; VIS1 gate |
| U6 | MAD22 ergonomia: per-seed SD Sb, marki Holm per-family, wizualne rozdzielenie S/H | Wartości per-seed w `FINAL_sealed-benchmark-read/` (final_read.json, final_tables.md); dodać SD po sparsowaniu, oznaczyć per-family Holm werdikty. **v1.1:** ten sam format kwalifikatorów stosować w panelu FRLL Tabeli 5 (spójność audytu). | składka | S/M | — |

### Nice to have (N1–N5)

| # | Pozycja | Zmiana | Kategoria | Koszt |
|---|---|---|---|---|
| N1 | Rebuild `main.pdf` | latex+bibtex po wszystkich zmianach; mtime PDF ≥ mtime źródeł. | auto-fix | S |
| N2 | Repo hygiene przed bundlem | Usunąć/wyłączyć z bundle: `results.tex.orig`, `main_plotly.*`, `legacy_references.bib`, lokalne katalogi review; scalić 3 duplikaty fragmentów w `supplement_*_review_20261114/`. | auto-fix (zakres wg A-D10) | S |
| N3 | Statement o zależności interwałów | W supplement: interwały are conditional on 5 fitted networks AND component counts (151/51 itd.) to saved denominators (mirroring Batch-C verification boundary). | auto-fix | S |
| N4 | Related work vs 2026 concurrent (non-CLIP detectors) | 1 akapit; weryfikacja bibliograficzna. | decyzja (scope) | M |
| N5 | Machine-checkable evidence manifest | Rozbudować `evidence_manifest.json` (szkielet istnieje) o mapowanie sentence → admitted report, **włącznie z nowymi komórkami FRLL i zdaniem o ruling/amendment**. | składka | M |

### Obliczenia (jedyné pozycje wymagające GPU)

**1. FRLL-Morphs read — COMMITTED (unsealed author-rulingiem, v1.1):**
- **Formalna ścieżka audytowalna:** author-ruling → formalny amendment preregu (zapis w repo eksperymentów; odczyt single-pass, bez re-readów) → gates 1–5 wg `experiments/AGENTIC_delivery_20261114/FRLL_READY_PLAN_20261115.md`: gate 1 (signed one-file FRLL roster z SHA256, create-only), gate 2 (freeze populacji/preprocessing/metryk/progów — policy już zarejestrowana w FINAL prereg i FRLL_READY_PLAN; potrzebny committed roster+freeze JSON), gate 3 (model roster: Sb 403–407 + released SelfMAD/MADation B/L/MixFaceNet; retrains tylko jeśli admission zamknięty PRZED readem), gate 4 (exposure disclosure), gate 5 (reproduction release + explicit evaluation release grant).
- Gdzie uruchomić: **DGX-GB10 wystarcza** (sonda: 7 127 wierszy; ~1–3,5 min GPU/model-seed przy batch 1; ograniczeniem I/O, nie forward) — alternatywnie WCSS. **Athena wykluczona** (account association absent).
- Wynik: per-family EER + attack-miss/genuine-FA przy development-frozen thresholds; outputs create-only `/mnt/t7/smad_next/FINAL/frll_read_v1/`; niezależny postresult review przed wstawieniem do Tabeli 5; jedyna droga do PDF.
- Ekspozycja (do ujawnienia niezależnie od rights): FRLL **nie jest** wholly untouched — 204 genuine przez MAD22.

**2. SPRINT5 paired-ranking analysis (pending, poza recenzją C2):**
- Status wg `OPERATIONAL_CLAIM_VERDICT_20261115.md`: joint operational claim UNSUPPORTED; `reader_v2` (ranking_statistics analyze v2, SHA 93b2ff22…) czeka na independent review.
- Gdzie: **WCSS** (H100; odczyt single-pass, po zamknięciu 15 fits i review reader_v2).
- Skutek dla manuskryptu: ewentualne wzmocnienie §training_results o absolute per-seed S3/S4 FA + achieved-BPCER. **Dozwolone do czasu:** narrower sentence: „Matched-control training improves selected development rankings and attenuates some own-rule artifact false alarms; preserved face-splice attack sensitivity at comparable genuine false alarms has not yet been established."

**3. VIS3 / seam render + print — gated, poza tym cyklem.** Fig. 1 zostaje schematem (patrz U5) do czasu VIS1/VIS3 release.

---

## B. Decyzje autorskie

**Rozstrzygnięte (v1.1):**

1. ~~FRLL-Morphs / panel HOLD~~ — **ROZSTRZYGNIĘTE:** komórki FRLL-Morphs zostają w submisji i zostaną wypełnione; author-ruling unsealing wydany, formalny amendment preregu wprowadzony, odczyt audytowalny. Efekty: B4 (projekt tabeli pod pełne wyniki + kwalifikatory), B6 (FRLL obowiązkowo w exposure/ethics), N5 (evidence manifest wpis). **Otwarty fragment tego wątku:** uprawnienia/licencja do FRLL-Morphs → patrz punkt 5.

**Otwarte (wymagają autora):**

2. **Kompozytowy rendering verdict (`results.tex:15`).** Przyjąć faktyczne registered verdicts (GD1 „render path used" 5/5 + GD2 „inconclusive") — czy zdefiniować kompozyt nowym prioregem. Rekomendacja: pierwsza opcja ( amendment nowym prioregem w poprawce koszt > wartość).
3. **Tytuł finalny** (usunąć „Integration review draft"). Wybrać przed rebuildem PDF.
4. **LLM usage statement.** Ostateczny zakres disclosure: weryfikacja historycznego użycia Claude/OpenCode vs statement ograniczony do Codex; finalny tekst przed submission.
5. **Prawa do datasetów i etyka — POZOSTAJE OTWARTE (wzmocnione przez FRLL decision).** Licencje/uwagi: FRGC (NIST), colorFERET (umowa), FFHQ (non-commercial), SMDD, FRLL, FRLL-Morphs (teraz na stronie wyników!), MAD22. Decyzja co udostępnić publicznie (scores/preprocessing vs wizerunki). Do czasu rozstrzygnięcia sekcja etyczna ukazuje status licencyjny per dataset zamiast milczenia. Wpływa na: B6 (treść), B4 (tym samym odwołanie w podpisie Tabeli 5 do rights/exposure).
6. **Companion appendix: tworzyć czy przerabiać odwołania.** Nowy `appendix.tex` w supp PDF (utrzymać 4 odwołania z `results.tex`) czy przenieść/load-bearing NOT_QUALIFIED (119 guards) do supplement reproducibility. Wpływa na page-budget supp.
7. **Threshold-transfer (WIP–TRANSFER):** compact paragraf w main §experiments czy tylko supplement + zdanie w main. Źródło gotowe (admitted).
8. **Sformułowanie wkładu 3 / abstract** po `OPERATIONAL_CLAIM_VERDICT_20261115.md` (UNSUPPORTED): przyjąć narrower permitted sentence teraz, czy czekać na zamknięcie SPRINT5 read. Bez decyzji: narrower wording zostaje (jest już zgodna).
9. **Fig. 1 / VIS1:** schemat pozostaje czy graficzna renderka drabinki/D-proxy (bez gated example images).
10. **Zakres bundle/hygiene (N2):** co wyłączyć z submisji (katalogi review, .orig, plotly, legacy bib), czy scalać duplikaty supplement_20261114, format wydania (review vs final anonymity).

---

## C. Kolejność wykonywania (DAG)

```
[FAZA 0 — natychmiast, bez decyzji i bez nowych obliczeń]
 0.1 Włączyć do repo: preamble.tex, references.bib, figures/, supplement_reproducibility.tex  [git add/commit]
 0.2 B1a: usunąć \input{publication_wip} (results.tex:3); plik out z bundla
 0.3 B7: zamienić „registered composite rendering verdict" na GD1/GD2 (autor zatwierdza słowa)
 0.4 U2: qualifier storage w abstract  [auto-fix]
 0.5 B3a: supplement_reproducibility.tex: usunąć linie 1–2, wciągnąć do supp build
 0.6 N3: statement o conditional intervals w supplement
 0.7 N1: rebuild main.pdf (+bibtex) — po 0.2–0.6

[FAZA 1 — po decyzjach autorskich, bez nowych obliczeń]
 1.1 B5: tytuł finalny (A-D3) + final LLM statement (A-D4)
 1.2 B6: ethics/exposure rozdział (z FRLL: MAD22 exposure → unseal → read) + zbieranie licencji (status per dataset jawnie, do czasu rights)
 1.3 B4-INFRA: scaffold Tabeli 5 pod pełne wyniki + kwalifikatory (EER, attack-miss/genuine-FA przy dev-frozen
     thresholds, per-seed SD) + paragraf „Author ruling and prereg amendment" w supplement/provenance;
     usunięcie linii „HOLD = …; new reads remain gated" — komórki zostają na czas przyjścia wyników
 1.4 B2: appendix.tex z admitted (forma wg A-D6) — największy pojedynczy koszt
 1.5 U1, U3, U4, U6: render-controls, verdicts-summary (slot FRLL), populations, MAD22 ergonomia
 1.6 B3: main_supp.tex → main_supp.pdf + CVPR checklist + threshold-transfer pkt (A-D7)
 1.7 N2, N5: bundle hygiene; evidence manifest rozszerzony (z wpisem FRLL/ruling)

[FAZA 2 — po obliczeniach]
 2.1 FRLL-Morphs read (COMMITTED): formal amendment preregu → gates 1–5 (FRLL_READY_PLAN_20261115.md)
     → read single-pass na DGX-GB10 (--/create-only outputs) → independent postresult review
     → wypełnienie Tabeli 5 + kwalifikatory (wartości wyłącznie z admitted FRLL report) → rebuild PDFs
 2.2 SPRINT5 paired-ranking read (WCSS H100, po review reader_v2) → decyzja o tekście wkładu 3 (A-D8);
     do tego czasu narrower permitted sentence obowiązuje
 2.3 VIS3/seam render/print — gated, poza obecnym cyklem

[Zamknięcie bez nowych obliczeń]
 Blokery: B1, B2 (strukturą i treścią z admitted; slot FRLL czeka na dane), B3, B5, B7
 Usprawnienia: U1–U4, U6 (U3 cząstkowo — slot FRLL); nice-to-have N1–N5
 GPU potrzebne już tylko do: wypełnienia Tabeli 5 (2.1, bardzo tanie na GB10) i SPRINT5 (2.2)
```

Szacunek: bez nowych obliczeń domyka się formalnie 6/7 blokerów + ~5/6 usprawnień; z unsealed
FRLL read (decyzja v1.1) **7/7 blokerów** domyka się w FAZIE 2.1 — koszt GPU jest minimalny
(minuty na GB10), wąskim gardłem jest prowadzenie gates i postresult review, nie compute.

---

## D. Checklista spójności przed submission

- [ ] Żadnych adnotacji WIP: brak `\input{publication_wip}`, brak `WIP--`/`publication_wip` w źródłach builda (grep obowiązkowy).
- [ ] Brak frazy „registered composite rendering verdict" bez źródła — i ogólnie: każde „registered verdict" w manuskrypcie ma pozycję w admitted report (enumeracja przez PR1/AB1/XF1/FINAL/SPRINT5/FRLL-postresult).
- [ ] **Tabela 5: zero komórek „HOLD"**; panel FRLL-Morphs wypełniony admitted wartościami + kwalifikatory (EER, attack-miss/genuine-FA przy dev-frozen thresholds, per-seed SD dla Sb); podpis deklaruje ekspozycję FRLL.
- [ ] Author-ruling i formalny prereg amendment mają miano w: (a) podpisie Tabeli 5 (jedno zdanie + odesłanie), (b) supplement/provenance (paragraf „Author ruling and prereg amendment"), (c) evidence manifest (wpis SHA raportu).
- [ ] LLM disclosure kompletne i finalne (bez „draft", bez „must verify"), zgodne z CVPR 2026+ policy i realną historią narzędzi.
- [ ] Supplement zbudowany: `main_supp.pdf` istnieje; inputuje `supplement_reproducibility.tex` + `appendix.tex` + ethics/exposure; CVPR paper checklist dołączony; brak linii „Proposed fragment / not yet integrated".
- [ ] Exposure map kompletna, w jednym miejscu: FRGC/colorFERET training, FFHQ dev, SMDD synthetic,  cykl MAD22-development-exposed, 204 FRLL genuine (102 osoby) przez MAD22 → konsekwencje dla FRLL-Morphs read (unsealed), 11-of-80 shape-links, 69-host sensitivity, clean80 split, 4 483 MAD22 morphs / 5 707 candidate inputs.
- [ ] Sekcja etyczna istnieje i obejmuje FRLL także jako eval dataset; status prawny per dataset jest jawny (jeśli rights nierozstrzygnięte — zapisane wprost jako otwarte, bez milczenia), patrz A-D5.
- [ ] Wszystkie 4 odwołania do „companion appendix" (`results.tex:76,114,132,173`) wskazują na realnie shipped materiał w supp.
- [ ] Abstract: qualifier „at the trained size; registered combined storage verdict inconclusive" obecny; wkład 3 zgodny z narrower permitted sentence (OPERATIONAL_CLAIM_VERDICT_20261115) albo wzmocniony dopiero po SPRINT5 close.
- [ ] Page limit: main ≤ 8 stron treści (bez references), obecnie ~8 + references — zweryfikować po dodaniu tabel FRLL/kwalifikatorów; supplement w limicie CVPR supp.
- [ ] Bibliografia: 19/19 kluczy resolvuje; `main.pdf` i `main_supp.pdf` zrebuildowane (mtime ≥ źródeł); brak missing refs.
- [ ] Repo hygiene bundla: bez `results.tex.orig`, `main_plotly.*`, `legacy_references.bib`, lokalnych katalogów review; untracked essentials (preamble, references.bib, figures/, supplement) w repo.
- [ ] Evidence manifest (`evidence_manifest.json`): mapa sentence → admitted report dla zmienionych zdań i nowych komórek FRLL (razem z SHA raportu FRLL read).
- [ ] Anonimowość zachowana (`\usepackage[review]{cvpr}` w wersji review; brak identyfikujących metadanych PDF).

---

Źródła planu: `INDEPENDENT_REVIEW_C2_20261115.md` (blokery 1–7, usprawnienia 1–6, nice-to-have),
`results.tex`/`main.tex`/`method.tex`/`related.tex`/`supplement_reproducibility.tex`/`publication_wip.tex` @ HEAD `1dc1581`,
`experiments/AGENTIC_delivery_20261114/{OPERATIONAL_CLAIM_VERDICT_20261115.md, FRLL_READY_PLAN_20261115.md, SOL_REPRODUCIBILITY.md, COMPUTE_POLICY.json}`,
admitted raporty: `AB1_protocol-ablation-and-replication/result.md`, `PR1_protocol-reads-existing-networks/result.md`,
`XF1_ffhq-facemorpher-matched-render/result.md`, `AD4/…`, `FINAL_sealed-benchmark-read/…`, `SPRINT5_20261114/…`,
`TT1_threshold-transfer-unseen-genuine/…` (via `supplement_threshold_transfer.md`).
Decyzja autorska (2026-11-15): unsealing odczytu FRLL-Morphs z formalnym amendmentem preregu.
