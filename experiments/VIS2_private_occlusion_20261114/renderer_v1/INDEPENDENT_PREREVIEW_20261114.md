# VIS2 renderer v1 — niezależny source-only pre-review

2026-11-14. Recenzent training_contribution, inny niż autor. **HOLD_EXECUTION — dwa potwierdzone blockery.** Nie wydawać real render grant dla obecnego v1. Naprawa powinna być nową immutable wersją; stary pakiet pozostaje zachowany.

Źródło SHA256SUMS `4b412cbbeea8ee3375b886db80ef39ec5f28acdd97b03e81e2d7fb93f0b921b3`, renderer `5abbc7005405bf0821014a813f6b42557efad66ba8715857213302bf446b6127`, CONFIG_MAC `424a14a8ba367280d18dd04e9248f2d9452d40f43e035192fc605397cc09cdad`, read contract `cc8b90e140ea2675c955ca170ffbbd23b8add3b41fe9473808227d72b4629323`, commands `8e25a303d02f7262d57a88ac86c1d5e3cd4b0829523eb0ad84d600840899e40f`: zweryfikowane.

## Blockery

1. **Niezdefiniowany zapis wyników.** `render_measured.py:242,259` wywołuje `write(...)`, którego nie ma w module ani importach. Bezpośredni import source-only potwierdził `hasattr(module,'write') == False`. Po tworzeniu PDF/SVG nastąpi NameError; nie powstaną wymagane CELL_RENDER_RECORDS/MANIFEST/TEXT_LAYOUT_RECORD. Dodać jawny create-only JSON writer z `allow_nan=False`, flush/fsync oraz testy syntetycznego zapisu, odrzucania nadpisania i finalnego kompletnego zestawu artefaktów. Przetestować wywołania finalizacji, nie tylko funkcje walidacji liczb. Partial render/failure musi mieć zewnętrzny lub wewnętrzny trwały receipt i nie może zostać uznany za COMPLETE.

2. **PDF resetuje alpha do1; SVG zachowuje0/.45.** `render_measured.py:191–192` wykonuje `setFillAlpha(alpha)` **przed** `setFillColor(Color(*rgb))`. Przeczytana rzeczywista implementacja bundled ReportLab4.4.9 `Canvas.setFillColor` wywołuje następnie `setFillAlpha(aColor.alpha)`; `Color(*rgb)` ma domyślne alpha1. PDF prostokąty są więc opaque: znikają source faces pod mapą, a przy L=0 ma być przezroczystość, lecz wychodzi biała zasłona. SVG i CELL_RENDER_RECORDS deklarują inny alpha. Naprawić jawnie `setFillColor(Color(*rgb), alpha=alpha)` albo ustawiać alpha po kolorze. Dodać generated canvas-state spy test dla0/.45/1, niezależnie sprawdzający realną kolejność/stan API ReportLab; porównać alpha PDF/SVG/record bez dostępu do prawdziwych obrazów/wyników.

## Drobna obowiązkowa korekta zgodności opisu

Caption w linii251 twierdzi, że „exact changed histories are in manifest”, lecz manifest pomija `cfg['history_facts']`. Dodać jawne history_facts (1024→265/249→alignment512), by odbiorca nie musiał odgadywać ich z samego SHA konfiguracji lub nazw plików; albo zmienić zdanie i jawnie dołączyć przypiętą konfigurację do artefaktów. To korekta provenance, bez zmiany danych lub interpretacji. Ograniczenie compound history/alignment/crop powinno pozostać widoczne.

## Co przechodzi audyt

Uruchomiono dokładne14 generated tests: **14/14 PASS**,0.005s; bez PDF/SVG, mock map, real RESULT, fotografii, modeli, wag lub GPU. Testy obejmują512-record contract, missing/duplicate/smoke/nonfinite/Boolean/arithmetic/geometry rejection, global scale z innego photo/fill, L0/tinyL/no-clipping, grayscale magnitude, geometry layout, legacy-grant rejection i brak seam/operational threshold. Nie testują finalnej ścieżki zapisu ani rzeczywistej przezroczystości; dlatego PASS14 nie wystarcza do GO.

Źródło prawidłowo buduje jeden L=maxabs wszystkich512 deltas/model przed wyborem strony, zachowuje signed Δz, oba fills i wszystkie3 modele×2 zdjęcia. Pure normalization nie używa epsilon/clipping/per-panel scaling, L0 ma w zamierzeniu literal zero/transparent, tinyL pozostaje rzeczywiste. Komórki mają8.5mm, mapy68mm, page180×322mm, minimalna wielkość tekstu8.2pt. Plan daje6 stron/edition,12 łącznie i3072 rekordy painted cells. Grayscale ma magnitude plus independent negative hatching. Geometria mieści się w stronie, bez nakładania paneli; **rzeczywistego print/font/clipping QA nie certyfikuje source review**.

Autoryzacja preceduje real data open: nowy GO_VIS2_PRIVATE_MEASURED_RENDER, config/sourceSUMS/code-review hashes, distinct authors/reviewers, dokładne data/out roots, wszystkie modele/fotografie, full-result canonical origins/hash roster i OTHER numeric review coverage. Legacy numeric/VIS1 grant odpada. Staging paths są ograniczone do stałych inputs/model RESULT names; hash checks wiążą exact4 PNG i3 RESULTS. To świadomy workflow gate, nie sandbox/OS security boundary. Root musi w nowym grancie przyjąć dokładne źródła i ich prawa/credits; nie dziedziczyć starej zgody. Konfiguracja wiąże lokalny interpreter, ReportLab4.4.9/Pillow13, dokładne Arial hashes; nie instalować reportlab naGX w ramach tej poprawki.

Widoczne plain-language labels i planned captions prawidłowo odróżniają zmierzoną zmianę score od przyczyny, sigmoid od calibrated attack probability i genuine zdjęcia od nieistniejącego splice seam. Zachowano private-only label, credits, ekspozycję, post-hoc model choice, compound history, różne rozdzielczości i brak anatomically aligned correspondence. Ranking NOT_QUALIFIED/5FAIL nie jest „naprawiony” tymi mapami. Publication/rights/consent/501 pozostają HOLD.

## Następny krok

Autor przygotowuje wąską immutable poprawkę dwóch blockerów plus history provenance; nowe source hashes, syntetyczne output/alpha tests i ponowna niezależna delta-review. Dopiero potem root może wydać nowy exact private render grant. Po real rendering potrzebny OTHER actual numeric-to-cell/PDF/SVG/print review wszystkich12 stron. Żywy manuskrypt, zamrożony worker i wcześniejsze wyniki pozostają nietknięte. W tej recenzji nie otwierano nowych real RESULT ani RGB i niczego nie renderowano.
