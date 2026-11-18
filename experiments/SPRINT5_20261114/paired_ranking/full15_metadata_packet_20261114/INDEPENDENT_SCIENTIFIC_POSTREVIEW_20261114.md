# Niezależny postreview naukowy SPRINT5_1 full15 — 2026-11-14

Autor: training_contribution, niezależny od implementacji readera Sol. Status: **RESULT_CONSISTENT; optymalizacja NOT_ESTABLISHED; operacyjnie NOT_QUALIFIED**. Przyjęcie przez root pozostaje osobną decyzją. Nie jest to zgoda na następny odczyt ani zmianę protokołu.

## Zakres i dowody

Przeczytano wyłącznie dopuszczony RESULT, źródła oraz metadane/proweniencję. Nie otwierano archiwów, ich nagłówków ani członków, NPZ, score arrays, checkpointów, obrazów lub oryginalnych logów. Nie uruchomiono readera, bootstrapu, nowych testów statystycznych ani obliczeń modelowych. Kontrola liczb oznacza arytmetykę już opublikowanych agregatów i zgodność statusów z kodem; **niezależnego przeliczenia CI nie wykonano**. Katalog wyniku zawiera tylko RESULT.json, bez replik bootstrapu.

- RESULT: `/mnt/t7/smad_next/SPRINT5_1/reader_output_v1/RESULT.json`, SHA256 `31e68aadf8e2c451ce57bd6320469a33dc107fe34cf232ebd4fe5aaf7111e601`.
- ROOT_READER_READ_RELEASE SHA256 `f7f07580f6ebb194d7491c1e5688c016d8f336894b5bcadcf7dd15640ea58511`; binding `519546ef7002930f620610f01deb0cc4e8889acf819b829a80c05f95fff6e923`; reader manifest `93b2ff226ee337fe3a486e0077be0a774a5229ce28ada45b46e41d6ed3ef42f4`.
- Roster `6c115d91a8813e66a711ed612af71476459343ffcd2cde0e1977c66e35e542ee`; actual metadata review `d09399c9af89b087f7f28f3cdd5eb24f53feeeaab1c8724cc66e01991c792d17`; operational review `c85710a0314b59b1b3e50e8592df613219e88bd8a18e859de375ab1fb19ccb10`.
- Release 20:50:51.589099Z → ADMIT_ONLY exit0 20:50:54.822614Z (bez claim) → trwały CLAIM 20:50:57.827950Z → EXECUTION exit0 20:52:16.406901Z i TERMINAL COMPLETE z identycznym hashem RESULT. Ścieżki once/output pozostają stałe. Wszystkie 15 różnych hashy archiwów w claim i RESULT są identyczne i zachowane; nie czytano tych archiwów w recenzji.
- Świeży zewnętrzny ROOT_FRESH_PRELAUNCH_GUARD dokumentuje scoped tracked clean, rzeczywisty `verify_prefit --require-committed` exit0, 33 authority pins i 6 receipt pins, commit ff16f7f1f1dbf33415ab36d8b2913cd156ca980b. Ten dowód nie jest domniemaniem, że collector sam egzekwuje Git guard.
- Towarzyszący `INDEPENDENT_SCIENTIFIC_POSTREVIEW_CHECKS_20261114.json`, SHA256 `eebd0d1b5e280e526e7cf3f94b925d20092edcac09e87077a02c8d3bac0b3017`: 48 kontroli PASS; dokładne hashe provenance i źródeł. Zweryfikowano 252 bloki opisowych częstości, każdy z 15 sieciami oraz różnicami po seedach. Pierwsza próba skryptu audytu błędnie rozwiązała względne README manifestu względem repo zamiast katalogu readera; poprawiono wyłącznie skrypt recenzji i ponowiono arytmetyczny audyt, bez żadnego wywołania readera.

## Wszystkie sieci: rekomendowana tabela AUC

Wartości są AUC w stałych kwintylach D, z równymi wagami kwintyli; seed mean nie oznacza zespołu modeli. Nie wybieramy najlepszego seeda.

| Arm | 501 | 502 | 503 | 504 | 505 | Średnia | AUC niestratyfikowane, średnia |
|---|---:|---:|---:|---:|---:|---:|---:|
| BCE | .748008 | .713502 | .759334 | .726507 | .751664 | .739803 | .776140 |
| Paired BCE | .772512 | .722583 | .765402 | .732700 | .752790 | .749197 | .782380 |
| Paired ranking | .786933 | .741613 | .780222 | .762717 | .780473 | .770392 | .807660 |

Ranking−paired BCE: pięć efektów .014421, .019030, .014820, .030016, .027683; średnia **+.021194**; CI97.5% **[−.016593, +.059224]**. Paired BCE−BCE: .024504, .009081, .006068, .006194, .001126; średnia **+.009395**; CI97.5% **[−.001253, +.029119]**. Oba mają 5/5 dodatnich efektów i dodatnią zmianę niestratyfikowaną (+.025280 i +.006240), lecz oba nie osiągają wymaganej średniej .03 i oba CI obejmują zero: **NOT_ESTABLISHED**, a nie dowód braku jakiegokolwiek efektu. Ranking−BCE jest wyłącznie opisowym kontrastem, nie trzecim potwierdzającym testem.

Dokładnie dwa zadeklarowane kontrasty używają dwustronnych CI97.5% (Bonferroni dla dwóch kontrastów; nominalnie rodzinne 95%). Źródło zachowuje 10 000 replik; RNG komponentów 2026111401, seedów 2026111403 i kalibracji 2026111404; stałe kwintyle D, źródłowo stratyfikowane komponenty i wspólne tripletowe resampling seedów. Wynik podaje 2% nierozstrzygalnych replik primary, tj. 200/10000 po zaokrągleniu precyzji zmiennoprzecinkowej, poniżej progu >5%. Nie usuwano seedów ani nie zastępowano endpointu niestratyfikowanym. Primary ma 40 komponentów; to populacja development, nie nowy niezależny benchmark.

Floor: zachowano wszystkie 15 kolumn. Maksimum punktowe .750884; ranking mean minus max **+.019507**, CI97.5% **[−.113381, +.139464]**, **NOT_ESTABLISHED**. Kod ponownie wyznacza maksimum wszystkich 15 floorów w każdej wspólnej replice. Dodatnia różnica punktowa nie wykazuje niezależności od badanych skrótów.

## Rekomendowana tabela progowa

Wszystkie liczby poniżej są średnimi pięciu częstości sieci, w procentach. S3 i S4 mają po 100 obserwacji na sieć. W nawiasach podano wszystkie pięć seedów 501–505.

| Próg | Arm | S3 same-person flag rate % | S4 sensitivity % |
|---|---|---|---|
| Camera calibrated | BCE | 68.0 (70,65,66,67,72) | 96.2 (96,95,96,96,98) |
| Camera calibrated | Paired BCE | 65.6 (66,66,60,66,70) | 96.2 (96,96,95,96,98) |
| Camera calibrated | Ranking | 55.6 (52,58,56,52,60) | 94.4 (95,94,94,94,95) |
| Logit > 0 | BCE | 38.4 (38,37,36,42,39) | 80.6 (80,76,78,84,85) |
| Logit > 0 | Paired BCE | 37.2 (35,38,36,39,38) | 79.2 (79,79,77,79,82) |
| Logit > 0 | Ranking | 32.8 (31,36,29,34,34) | 78.0 (76,78,75,75,86) |

Kalibracja: 132 niezależnie wydzielone osoby/128 komponentów, statystyka pozycyjna 127 i ścisłe `score > threshold`. Każda z 15 sieci flaguje 5/132 = 3.7879% próbek kalibracyjnych. To osiągnięty BPCER na kalibracji, nie gwarancja 5% BPCER w nowych populacjach. Każda sieć ma własny próg; own-rule logit>0 jest osobnym opisowym panelem. Próg jest wyznaczany ponownie na resamplowanej populacji kalibracji w bootstrapie.

Ranking względem paired BCE zmniejsza flagowanie S3 punktowo o 10.0 pp przy spadku S4 o 1.8 pp. Przy logit>0 różnice wynoszą odpowiednio −4.4 pp i −1.2 pp. **S3 nie jest bona fide camera BPCER.** Mniejsza odpowiedź na szew same-person nie jest dowodem rozpoznawania dwóch tożsamości ani zachowania czułości przy porównywalnym heldout false alarm. Guard S4: punkt −.018, marginalne granice [−.041325,+.005128], wymagane dolne ograniczenie ≥−.02; **INCONCLUSIVE**, mimo że punkt mieści się w marginesie. Wszystkie 10000 replik tego guardu czytelne.

## Wszystkie genuine guardy i zakres rodzin

Zachowano 119 komórek genuine: 47 PASS, 5 FAIL, 67 INCONCLUSIVE (52 z powodu <20 komponentów; 15 z powodu granicy marginalnej). Łącznie z S4: 120 wymaganych guardów, 47 PASS/5 FAIL/68 INCONCLUSIVE, IUT all_pass=false, **NOT_QUALIFIED**. Nie traktować 52 komórek sparse jako PASS ani nie usuwać ich z mianownika. Pozostałe 67 genuine guardów mają po 10000 czytelnych replik, bez nieoczekiwanych nonfinite; sparse nie uruchamiają bootstrapu (zero prób, brak granic).

| FAIL cell | Źródło/rung/komórka | Δ FA ranking−paired BCE | Marginalne granice |
|---|---|---:|---|
| 102 | TT1 FRGC / R_cam_border / agedb_30 | +.106726 | [.021684,.180702] |
| 103 | TT1 FRGC / R_cam_border / casia_fasd | +.084305 | [.024572,.150666] |
| 106 | TT1 FRGC / R_cam_border / msu_mfsd | +.076233 | [.020600,.147171] |
| 109 | TT1 FRGC / R_cam_geo112 / g112 | +.182960 | [.062318,.287110] |
| 110 | TT1 FRGC / R_cam_geo224 / g224 | +.124664 | [.066349,.189909] |

Każda z tych pięciu komórek ma 223 wiersze/30 komponentów. Dolne ograniczenie jest >+.02; to zarejestrowane FAIL, nie tylko niepewność. Nie uogólniać nazw stylów komórek na niezależne testy całych zewnętrznych zbiorów.

Oba panele progowe zawierają wszystkie 119 komórek: dev53, gd21, MEDS4, TT1 41; osobne primary source FERET i FRGC. Przykładowo camera S4 mean FERET: .852632/.852632/.842105, FRGC: .987654/.987654/.967901 w kolejności BCE/paired BCE/ranking. To opisowe zestawienia source/cell, bez nowego family-pooled testu lub selektywnego wybierania korzystnych rodzin. Pełne komórki i seedy pozostają w dopuszczonym RESULT.

Obowiązują przyjęte przed odczytem binding/review: operacyjne IUT z marginalnymi jednostronnymi granicami 95%, minimum20 i sparse/zero-variance→INCONCLUSIVE. Nie opisywać ich jako jednoczesnej gwarancji pokrycia wszystkich komórek, nawet jeśli starsze prereg używało słowa simultaneous. Bootstrap komponentów/seedów jest przybliżony; IUT dziedziczy ważność testów marginalnych, nie dowodzi finite-sample coverage.

## Wniosek do manuskryptu i podpis

Proponowany ostrożny tekst: „In the registered development experiment, paired ranking increased within-D AUC point estimates in all five seeds relative to paired BCE, but did not meet the prespecified optimization criterion. Reduced same-person splice flagging was accompanied by lower attack sensitivity; detection non-inferiority was inconclusive and five genuine-processing cells failed the false-alarm guard.”

Podpis do tabel: „All 15 networks (three arms × seeds 501–505), without selection or score ensembling. Within-D AUC uses fixed equal-weight strata; two deciding contrasts use prespecified Bonferroni 97.5% bootstrap intervals. Operating rates are seed means under independently camera-calibrated per-network thresholds and the separate logit>0 rule. S3 flags measure same-person splice controls, not bona fide BPCER. All 119 genuine cells, including 52 sparse cells, remain in the operational assessment. Development results do not constitute external validation.”

Nie wspierać tym wynikiem mocnego claimu „reduces reliance on artifacts while improving face-spliced morph detection” ani adopcji operacyjnej. Równość całkowitej ekspozycji i identyczne plany obu paired arms izolują dodatek ranking loss bardziej bezpośrednio niż porównanie z niezależnym BCE; nie dowodzą tożsamościowego mechanizmu ani generalizacji. MAD22-informed development i historyczna ekspozycja zdjęć FRLL są ujawnione; historyczne191, zamknięte benchmarki i NEXT pozostają poza odczytem/wnioskiem. Wynik null/inconclusive należy opublikować z pięcioma operacyjnymi FAIL; bez zmiany marginesów, progów, rodzin, mianowników lub nowego journalu po wyniku.
