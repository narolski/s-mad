# VIS2 renderer v1r1 — niezależna recenzja wąskiej poprawki

2026-11-14. Recenzent training_contribution, inny niż autor. **GO_EXACT_V1R1_SOURCE**. Oba blockery z recenzji v1 `9273bdad6d0a761f8373aea07f1b919c12e54c777d45acd0bc2d8c266b7b1d81` zostały usunięte; korekta history provenance także. To source GO, **nie zgoda na real rendering**, odczyt pikseli lub prezentację.

Dokładny source manifest `5ab609dfdb8d3c2a7df1ef9c9fa574b307d055bc44ff1f1282a39f84838768ab` i wszystkie3 wymienione pliki zweryfikowane. CONFIG_MAC pozostał `424a14a8ba367280d18dd04e9248f2d9452d40f43e035192fc605397cc09cdad`. Stary v1 manifest `4b412cbbeea8ee3375b886db80ef39ec5f28acdd97b03e81e2d7fb93f0b921b3` jest niezmieniony i nadal HOLD. Pierwotne14 testów ma identyczny hash `aec03bb5801bf0045ebc398e6dc07a86fc3288ed064b976f4fdfe1f33c938c0f` w obu wersjach. Źródła przeczytano dopiero po immutable handoff autora.

## Niezależne testy rzeczywiście wykonane

Lokalny bundled Python/ReportLab4.4.9: `python3 -I test_contract.py` **14/14 PASS** (0.005s), `python3 -I test_finalization.py` **4/4 PASS** (0.111s), bez skip. Nie otwierano realnych RESULT/RGB; nie uruchamiano modeli, GPU ani realnego/mockowego obrazu lub PDF. Generated scalar JSON/sentinels i temporary output zostały usunięte przez TemporaryDirectory; virtual SVG/mockPDF pozostały wyłącznie w pamięci.

- Writer jest teraz zdefiniowany. Serializuje z `allow_nan=False` przed utworzeniem pliku, otwiera `xb`, flush/fsync pliku i fsync katalogu. Test odrzuca overwrite i NaN, zachowuje stary plik, nie pozostawia pustego nowego JSON po serialization failure. E2E przechodzi rzeczywiste wywołania zapisu CELL_RENDER_RECORDS, MANIFEST, TEXT_LAYOUT_RECORD i COMPLETE; zniknął NameError.
- `set_overlay_fill` ustawia Color **przed** jawnym alpha. Fixture wywołuje rzeczywiste state setters ReportLab Canvas i potwierdza stan `ca`0/.45/1; nic nie rysuje ani nie zapisuje, BytesIO pozostaje pusty. Rozwiązuje to reset alpha przez Color(default1).
- Generated cały `main` z mockowanym canvas/ImageReader/fontparser daje3072 cell records,12 virtualSVG,2 mockPDF,6 stron/edition, complete marker i exact history_facts. Zebrane3072 prostokąty canvas mają alpha dokładnie takie jak rekordy, w tym wszystkie zerowe L→0 i niezerowe→.45; SVG zawiera te same opacity. Fixture obejmuje L0 model i niezerowe pozostałe modele. Nie mylić tego z realnym print QA.
- Wstrzyknięty błąd finalizacji powoduje wyjątek i trwały FAILED, bez COMPLETE/MANIFEST. Wrapper nie przejmuje istniejącego katalogu po failed mkdir. Jakikolwiek FAILED lub nonzero native exit unieważnia nawet ewentualnie wcześniejszy COMPLETE marker; root musi egzekwować tę regułę przy odbiorze.

JSON-y mają jawne fsync/create-only. PDF/SVG/caption używają normalnego close/write wewnątrz świeżo zarezerwowanego output directory; nie są osobno fsyncowane przez JSON helper. Nie deklarować więc crash-atomic/fsync gwarancji całego zestawu grafik. Final hashes i niezależne post-render rehash/native-exit admission są nadal wymagane; partial output należy zachować, nie nadpisywać. To nie blokuje ograniczonego, świeżego CPU renderu z osobnym odbiorem, ale określa rzeczywisty zakres trwałości implementacji.

## Zachowany zakres i warunki root

Delta nie zmienia walidacji danych, liczb, L=maxabs wszystkich512/model, kolorów, geometry,2fills,3 modeli,2 zdjęć,68mm map,180×322mm stron, min8.2pt ani praw/private labels. `history_facts` są teraz wprost kopiowane z exact config do manifestu, zgodnie z caption (1024→265/249→alignment512). Żywy manuskrypt, VIS1, worker v1 i prereg pozostały poza zakresem zmian.

Nowy root private-pixel/render grant musi wskazać **v1r1**, exact source/config oraz ten review; nie przenosić źródłowego hasha/grantu v1. Full numeric admission źródłem jest wcześniejszy niezależny raport `b9a6a9dd491dfd6f3189deef11855c367ccecbd6d61e8f77452d6c971b993d7c` i jego dokładne3 RESULT hashes; w tej delta-review nie otwierano ponownie realnych wyników. Root wiąże4 exact image hashes,3 exact full-results, source credits, konkretne data/output roots, author/reviewer i native render exit. Wszystkie3072 rekordy mają zostać zachowane.

Po faktycznym renderze potrzebny OTHER numeric-to-cell/PDF/SVG/print review każdej z12 stron, grayscale proof, pełne credits i no-clipping/minfont. Source GO nie stanowi actual layout/photograph QA. Nie ma seam mask na genuine fotografiach ani identity-causality/operational claimu. Ranking NOT_QUALIFIED/5FAIL bez zmian; publication/rights/likeness/consent/501 extension nadal HOLD. Nie uruchomiono nowego renderu ani żadnych obliczeń naukowych.
