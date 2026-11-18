# Trzecia kontrybucja: protokół treningowy i dwa odrębne wymagania dowodowe

Data: 14 listopada 2026. Autor: dedykowany agent training_contribution. Status: **synteza i propozycja, nie niezależna zgoda na odczyt ani rejestracja**. Zakres: dopuszczone opisy wyników, rejestracje, recenzje i obecny `manuscript_cvpr2027`; bez otwierania score'ów, archiwów kandydatów i zamkniętych benchmarków. Bez treningów, readerów produkcyjnych, mutacji klastrów, wydatków, commit/push i zmian manuskryptu.

## Wniosek decyzyjny

Kontrybucja „We propose a training protocol that reduces reliance on artifacts while improving face-spliced morph detection” ma mocny, ale **ograniczony do development i konkretnego pakietu Sb** fundament. Nie ma dziś podstaw do dodania „at comparable false-alarm rates” jako formalnie potwierdzonej przewagi porównawczej na nowych źródłach. Najbliższy gotowy dowód operacyjny już istnieje: wieloźródłowy próg PR1 Z2 dla tych samych pięciu sieci Sb 403–407. Przy tej samej procedurze kalibracji Sb ma 15–25% przeoczeń dwutożsamościowych spliców, B 94–99%; największy odsetek flag na chronionych pulach genuine wynosi odpowiednio 4.9–8.7% i 7.2–10.0%. Są to zakresy po seedach, nie sparowane efekty ani test równoważności false alarm. Nie należy czekać na nowe treningi, żeby uczciwie pokazać tę tabelę.

Drugi człon ma być „smaller responses to **specified storage perturbations**”, nie ogólne usunięcie artefaktów. Same sieci Sb poprawiają ranking face-spliced morphs oraz mają mniejszy wzrost flag po zmianie historii przechowywania niż A; nie wolno dołączyć najlepszych wyników transferu B, redukcji R3 z SE ani wyników CFD z SbM3 i nazwać sumy jedną metodą. Ścisła replikacja złożonego kryterium storage w AB1 pozostaje inconclusive, mimo wyraźnie małych wzrostów flag.

Count-controlled batch C jest najtańszym brakującym dowodem **atrybucji**, a nie substytutem operacyjnego testu face-splice. Jego rozstrzygający endpoint dotyczy pełnokadrowych R4/R3, nie przeoczeń face-spliced S4 przy ustalonym false alarm. Dopuszczenie i jednorazowy odczyt prowadzą method_results i niezależny stats_controls_reviewer; ten raport ich nie dubluje.

## Definicje, które muszą pozostać rozdzielone

- AUC to ranking dwóch konkretnych populacji, nie skuteczność przy progu. EER również nie zastępuje przenoszonego progu operacyjnego.
- Bona fide / genuine camera photos służą do pomiaru false alarm/BPCER. Jednoosobowe obrazy przetworzone (same-person S3, R3, seam-only S0) są kontrolami mechanizmu; ich flag rate raportujemy oddzielnie. Ich automatyczne uznanie za dokumentowo poprawne bona fide byłoby dodatkowym założeniem.
- S4 to dwutożsamościowy face splice; S3 to same-person splice; S0 to konstrukcja seam-only; R4/R3 to pełnokadrowe morphy dwu-/jednoosobowe. FFHQ landmark_combined to odrębny developmentowy zestaw face-spliced morphs. Nie zamieniamy tych endpointów.
- Ten sam protokół oznacza identyczny przepis, listę, last checkpoint, platformę/gate i jawny zestaw seedów. Zestawienie bloków FS1/A100 403–407 i AB1/H100 408–412 jest replikacją przepisu przy jednoczesnej zmianie platformy i seedów, nie dziesięcioma wymiennymi powtórzeniami.
- Zerowe flagi S0 nie dowodzą braku korzystania ze wszystkich szwów. S0 i S4 mają szew dopasowany w rozmiarze, nie w rodzaju; także A i B są na podłodze S0. Rozdzielenie S4/S3 nie identyfikuje dwóch tożsamości, bo rozbieżność wejść, geometria i statystyki blendowania nie są całkowicie dopasowane.

## Macierz dopuszczonych dowodów

| Pytanie | Ten sam arm / blok | Dopuszczony wynik | Co rzeczywiście wspiera | Granica |
|---|---|---|---|---|
| Ranking face-spliced morphs | PN1 FS1 A/B/Sb 403–407 | FFHQ landmark_combined AUC: Sb 0.860 ± 0.030, B 0.674 ± 0.028, A 0.736 ± 0.031; poprawa 5/5 | Pakiet Sb poprawia ranking względem obu komparatorów na tych developmentowych obrazach | Nie ponad najlepszą pojedynczą statystyką 0.886; recipe selection i wcześniejsze MAD22 exposure pozostają |
| Detekcja przy kalibrowanym progu | PR1 Z2, dokładnie FS1 403–407 | Przy τ5: S4 miss A 97–99%, B 94–99%, Sb 15–25%; G_max A 19.2–21.8%, B 7.2–10.0%, Sb 4.9–8.7%; landmark_combined miss 41–55%, 62–70%, 24–39% | Najbliższy gotowy argument praktyczny dla tego samego Sb, z jawnie ograniczonymi genuine pools | τ5 to wspólna reguła kalibracji, różny próg każdej sieci. Zakresy nie stanowią formalnego paired non-inferiority. Z2a „usable” Sb 4/5 dotyczy landmark_combined, nie osobnego testu S4 |
| Resztkowe kontrolne flagi przy tym progu | PR1 Z2 Sb | S3 32–43% | Ujawnia koszt/ograniczenie niezależnie od genuine false alarm | G_max wyklucza S3; nie można go rozszerzyć na „wszystkie negatywy” |
| Storage na tym samym Sb | PN1 FS1, recenzja FS1, opis post hoc | Wzrost own-rule flag po history matching: A +14.7–21.8 pp, B +2.5–5.5 pp, Sb +0.5–2.7 pp | Opisowa redukcja wskazanej odpowiedzi w tych samych sieciach | Pierwotny contrast 2 uninformative: kontrola dodatnia nie spełniła progu share-rising. Nie przepisywać werdyktu |
| Replikacja storage i rankingu | AB1 H100 408–412 | C2P fm61 Sb Δf 0–4.5 pp vs A 26.5–38.5 pp; przy amsl112 Sb 0–2.1 pp; ranking landmark_combined Sb 0.873–0.906 | Mała reakcja flag i wysoki ranking współistnieją w tym samym przepisie | C2P formalnie inconclusive: 5/5 na fm61, 3/5 na amsl112; dwa braki przez dwustronny średni shift ku genuine. Nie zmieniać kryterium |
| Wkład matched negatives | AB1 408–412, amendment 5 | Sb−Sp na D-stratyfikowanym R4/R3 +0.049 [0.028,0.073]; Sb−B +0.042; Sp−B −0.008 [−0.033,0.022] | Usunięcie pakietu S0+S3 usuwa przewagę kontrolnego rankingu | −312 unikalnych obrazów, −624 wiersze, class mix; nie isolated content. Pooled Sp−B po sign cap inconclusive |
| Same-person splice vs seam | AB1 408–412 | S3 Sp 70–74%, Sb 36–41%; S4/S3 AUC Sp 0.69–0.72, Sb 0.76–0.80 | Matched negatives poprawiają rozdzielenie S4/S3 względem Sp | Nie S0-vs-S3 attribution; Sb sam flaguje znacznie więcej S3 niż A/B; S4/S3 przewidywalne z etykiet treningowych |
| R3-remedy | SE1 A100 408–411, 4 seedy | R3 flags Sb 83–90% → SE 25–32%; S3 Δ −0.010 [−0.063,0.040]; target not met | Oddzielna negatywna/ograniczona ablacja | Większość redukcji R3 to przesunięcie operating point. Nie podmieniać tym dowodów Sb ani dopisywać piątego seeda |
| Więcej źródeł | MS1 SbM3 vs Sb, L40S 403–407 | CFD median flags 3.5%→0%; FFHQ landmark_combined median miss 27.1%→58.5% | Kontrprzykład: mniejsze flagi przy zachowanym AUC mogą pogorszyć detekcję przy progu | P1-T floor, brak ataków CFD; SbV nie kontroluje dilution/diversity. Nie łączyć SbM3 z Sb |
| Oddzielny silnik i blend-vs-warp | XF1 FS1 403–407 | Face+halo AUC Sb 0.889, B 0.879, A 0.864; Sb−B +0.011 [−0.010,0.031] inconclusive | Ograniczony diagnostic blend-vs-warp | Bez potwierdzonej przewagi; szary surround flaguje 47–99% warp-only; nie deployed false alarm. Post-freeze, post-read diagnostic |
| Genuine-only transfer | TT1 FS1 i MEDS | TT1 F̄: A 0.023, B 0.0024, Sb 0.020 (średnie); PR1 τ5 Sb na unseen sources: 3/5 ≤10%, inconclusive; MEDS own rule wszystkie 15 sieci spełniają regułę | Kontrole przenoszenia progu i zależności od źródła | Brak morphów tych źródeł; TT1 nie dowodzi skutecznej detekcji, a wynik B nie jest wynikiem Sb |

Źródła każdej linii: odpowiadające `experiments/{PN1_protocol-network-first-tests,AB1_protocol-ablation-and-replication,PR1_protocol-reads-existing-networks,SE1_seam-shortcut-training-arm,MS1_multi-source-training-set,XF1_ffhq-facemorpher-matched-render,TT1_threshold-transfer-unseen-genuine}/result.md`; dla storage FS1 także `experiments/reviews/REVIEW_PN1_FS1_20261113.md`. Recenzje kluczowych granic: `REVIEW_PR1_PART1_20261113.md`, `REVIEW_SE1_A100_20261113.md`, `REVIEW_MS1_20261113.md`, `REVIEW_XF1_20261113.md`, `REVIEW_TT1_FS_20261113.md`. Historyczna nieudana próba C2P na L40S (`PN1/c2p_result.md`) nie jest dopuszczonym porównaniem z A; nie używam gate-failed score'ów ani nie traktuję jej jako końcowego stanu freeze.

## Minimalny brakujący pakiet, w kolejności

### 1. Bez nowych eksperymentów: połączyć dopuszczone tabele dla jednego Sb

Z istniejących zrecenzowanych outputów PR1/PN1/AB1 pokazać w jednej tabeli wszystkie pięć seedów, próg, genuine flags, S4 i landmark_combined misses oraz oddzielne S3/S0 flags. Zestawienie już opublikowanych liczb nie jest nowym confirmatory testem. Każdy brakujący numer pozostawić pusty do autoryzowanego odczytu konkretnego dopuszczonego summary; nie zaglądać przy okazji do tarów. Nie przedstawiać różnych worst-case zakresów jako sparowanej różnicy.

### 2. Dokończyć zarejestrowany batch C: zero nowych fitów

Obowiązują AB1 amendments 7/7b, niezależny `PRERUN_AB1_A6_A7_20261113.md` i aktualny admission packet. H-c1 = Sb−SpV; H-c2 = BN−BV, **nie BN−B**. Positive multiplicities są identyczne wewnątrz każdej pary. H-c1 kontroluje row count, class mix i positive repetition, lecz treść S0+S3 pozostaje nierozdzielna z dodatkowymi 312 unikalnymi obrazami; analogiczna luka diversity dotyczy BN−BV. BN−B i interakcja są wyłącznie drukowane opisowo.

Primary: R4/R3 OpenCV, D-stratified dev100+clean80, istniejące agreement/coverage/unreadable/sign-cap zasady, 2,000 joint-component draws. Zachować „present” ≥0.03 z lower 95% >0 i ≥4/5 dodatnich seedów oraz „absent” upper <0.03, bez reinterpretacji. Zachować 99.5% jako istniejącą sensitivity, z ujawnieniem że nie stanowi pełnego 16-test Bonferroni. S4/S3 jest secondary near-certain by design. Pokazać clean69 jako zapisaną shape-link sensitivity, nie nowy wybór podzbioru po wyniku. Zachować print-only same-data learners oraz oddzielić je od in-domain floors.

Stan z koordynacji method_results (handoff `METHOD_BATCHC_READINESS_20261114.md`): kod naprawiony/testowany syntetycznie; świeże sprawdzenie 49 dependency pins i 30 opaque archive hashes PASS. Upstream collection provenance 15 comparatorów pozostaje niezbindowane, a niezależny release binding nadal konieczny. Realny read pozostaje NO-GO; niniejszy plan nie udziela GO. Termin i eligibility pozostają istniejące; niedopuszczony/late output jest brakującą informacją, nie zerowym efektem.

### 3. Tylko jeśli potrzebny mocniejszy claim operacyjny: prospektywna rejestracja analizy wspólnego operating point

To **propozycja nowej, post hoc motywowanej analizy**; nie dodatek zmieniający AB1/NEXT. Najtańsza wersja używa już dopuszczonych score'ów istniejących A/B/Sb, bez nowych fitów. Same obrazy i wyniki były widziane: nowa rejestracja nie przywróci niezależności. W pierwszej kolejności zachować istniejącą τ5 PR1 i kalibrację z części native genuine; nie stroić progu na S4 ani na ewaluacyjnych genuine.

Przed wykonaniem niezależni controls/statistics ustalają: jeden primary comparator (proponowany A dla pełnego pakietu; B jako decomposition), jeden primary face-splice pool, chronione genuine sources, jedną regułę progu i parowane efekty. Potrzebne są łącznie (i) różnica miss/TPR ataków, (ii) false alarm na każdej chronionej puli, (iii) paired storage Δflag i score shift w tej samej sieci przy tym samym progu, (iv) attack retention pod storage, jeśli dana para ataków jest już zarejestrowana i dostępna. S3/R3/S0 pozostają oddzielnymi kolumnami.

„Comparable” wymaga uprzednio uzasadnionego marginesu non-inferiority false alarm i odpowiedniej precyzji; **ten raport nie nadaje żadnego nowego marginesu**. Reguła PR1 G_max≤10% jest historycznym kryterium użyteczności, nie automatycznym marginesem różnicy armów. Nie wybierać marginesu dlatego, że obserwowane zakresy pasują. Można bez nowego pass mark pokazać sparowane różnice i przedziały jako opisowe. Formalny joint claim wymaga oceny obu współpierwotnych osi, a nie korzystnego wyniku którejkolwiek. Uncertainty musi uwzględniać osoby/host-partner components i jawnie seed variability; host-only CI jest warunkowe na sieciach. Uwzględnić kalibrację w uncertainty lub nazwać wynik conditional-on-calibration. Nie scalać zależnych obrazów jako niezależnych obserwacji.

Silna niezależna konfirmacja wymaga późniejszego dopuszczonego, niewidzianego bloku z zamrożonym przepisem i kryteriami. Nie rezerwuję nowych seedów ani nie zajmuję 413–417: te pozostają przywiązane do NEXT. Nie otwieramy sealed benchmarków w celu domknięcia C3. Dla claims o czystej treści negatywów potrzebny byłby osobny, prospektywnie zaprojektowany equal-unique/diversity control; to nie minimalny warunek węższego claimu o całym protokole.

## Konkretne tabele do manuskryptu

**Tabela C3-A: detekcja i artefakty tego samego modelu.** Wiersze A/B/Sb × seed 403–407; drugi panel AB1 408–412. Kolumny: platforma/last checkpoint, próg (0 lub τ5, nigdy pomieszane), genuine flags native/history-matched osobno per source i G_max, S4 miss, landmark_combined miss/AUC, storage Δflag fm61/amsl112, S3/S0 flags. Opisowe storage FS1 oznaczyć post hoc; wszystkie złożone storage verdicts wydrukować, także inconclusive. Main paper może mieć zwięzłe podsumowanie po seedach, supplement wszystkie sieci. Zmiany operating point z MS1/SE umieścić w osobnym panelu limitation, nie w kolumnie sukcesu Sb.

**Tabela C3-B: atrybucja bez mylenia liczby i treści.** Wiersze Sb−Sp (już odczytane), Sb−SpV, BN−BV (pending), opisowe SpV−Sp/BV−B/interakcja. Kolumny: positive rows same?, balanced rows same?, unique images difference, primary D-stratified R4/R3 effect/CI, seedy dodatnie, native verdict, dev/clean80 sign, clean69 sensitivity, learner/floor licence. Osobny secondary panel S4/S3 z dopiskiem training-expected. Pending nie wypełniać zerami.

**Tabela C3-C: granice transferu.** XF1 (inconclusive gain; face+halo blanking), TT1 (genuine-only; τ5 poza calibration sources), MEDS (genuine-only), rendering controls, z kolumnami „brakująca oś” i „licencjonowany wniosek”. MAD22 wyłącznie jako osobny zrecenzowany benchmark panel, z exposure, nie jako dowód mechanizmu lub superior face-splice performance.

Każdy positive/null/inconclusive outcome wstawia się do **tych samych** wierszy i kolumn, bez usuwania niekorzystnych seedów, zmiany endpointu lub ponownego doboru progu. Wynik count-control „absent” oznacza wykluczenie zarejestrowanej wielkości +0.03, nie dowód dokładnego zera; inconclusive nie znaczy brak efektu. Niespełnione software/admission gate to „not read”, nie null.

## Warunkowe brzmienie kontrybucji

**Dozwolone dziś, wersja ostrożna:** “We study a matched-control training protocol that improves face-spliced morph ranking and attenuates measured storage-induced false-alarm increases on development data, while exposing residual responses to same-person manipulations.” Dalsze zdanie opisuje PR1 τ5 i jego ograniczone genuine pools. Jest to propozycja redakcyjna wymagająca niezależnej conclusions review, nie upgrade dawnych verdicts.

**Jeżeli obie osie prospektywnie ustalonego joint testu przejdą:** “Under the prespecified calibration rule, the same training protocol improves detection of the evaluated face-spliced attacks while maintaining the specified bona fide false-alarm bound and reducing the measured response to [named storage perturbations].” Wstawić konkretne dane, comparator i exposure; nie skracać do „artifact-independent”. Jeśli użyto tylko już widzianych danych, nazwać analizę development/post hoc, nie confirmatory.

**Jeżeli detekcja jest null, a redukcja artefaktu potwierdzona:** “The protocol reduces the measured storage response, but does not establish improved face-spliced attack detection at the specified operating condition.” Jeżeli przyczyną jest strata detekcji, podać koszt zamiast „null”.

**Jeżeli detekcja poprawia się, a artifact/comparability pozostaje inconclusive:** “The protocol improves the evaluated face-splice discrimination; reduced artifact reliance at a comparable operating point remains unestablished.” W abstrakcie nie używać wspólnego „while” jako dwóch potwierdzonych sukcesów.

**Jeżeli batch C positive:** wyłącznie dodatkowo „the ranking gain persists after matching row counts and positive repetition”; zawsze „negative content and added unique-image diversity remain inseparable”. **Jeżeli absent:** efekt removal ablation nie izoluje content od count/class mix i nie potwierdza zarejestrowanej wielkości content+diversity effect. **Jeżeli inconclusive:** pozostawić atrybucję nierozstrzygniętą. Żadna gałąź batch C sama nie uprawnia do „recognizes two identities”, „all seam cues removed”, „generalizes”, „shortcut-free”, „outperforms” na MAD22.

## Handoff i kontrola zapisu

Minimalna kolejność: (1) wstawić/zweryfikować istniejącą tabelę PR1+storage dla Sb, (2) niezależnie dopuścić i jednokrotnie odczytać zarejestrowany batch C, (3) niezależnie zrecenzować wynik i wybrać właściwą gałąź claimu, (4) dopiero gdy wymagany jest mocniejszy claim, zarejestrować joint operating-point analysis lub późniejszą konfirmację. Brak wyniku C nie blokuje punktu 1. Żadnych nowych treningów przed rozstrzygnięciem, czego nie odpowiadają istniejące dane.

Przeczytano AGENTS/CONTINUE, bieżące NOTEBOOK/OWNER_BRIEF/WORKFLOW, AGENTIC README, wskazane wyniki/rejestracje/recenzje i aktualne main/method/results manuskryptu. Nie dokonywano niezależnego przeliczenia liczb; są transkrypcją jawnych, zrecenzowanych raportów. Nie zatwierdzam własnej propozycji. Lead powinien powierzyć review innemu agentowi.

CLAIMS:
- number PR1_tau5_Sb_S4_miss = 0.15–0.25 @ experiments/PR1_protocol-reads-existing-networks/result.md:Z2
- number PR1_tau5_B_S4_miss = 0.94–0.99 @ experiments/PR1_protocol-reads-existing-networks/result.md:Z2
- number AB1_Sb_minus_Sp_R4_R3 = +0.049 [0.028,0.073] @ experiments/AB1_protocol-ablation-and-replication/result.md:amendment-5 table row 5
- number XF1_Sb_minus_B = +0.011 [-0.010,0.031] @ experiments/XF1_ffhq-facemorpher-matched-render/result.md:Gains
- Odczytano i transkrybowano raporty; nie zweryfikowano ponownie raw scores. Nie deklaruję nowych commitów ani zatwierdzenia admission.
