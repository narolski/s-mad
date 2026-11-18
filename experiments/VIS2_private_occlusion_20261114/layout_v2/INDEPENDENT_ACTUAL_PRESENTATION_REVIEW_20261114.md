# VIS2 layout_v2 — rzeczywisty postreview danych, grafiki i wydruku

2026-11-14. Recenzent training_contribution, inny niż autor. **GO_PRIVATE_PRESENTATION_AND_NATIVE_SIZE_PRINT_ONLY** dla dokładnych plików poniżej. Jest to zgoda na prywatną prezentację i druk w100% rozmiaru180×279.4mm; **PUBLICATION/rights/likeness/consent/501 extension pozostają HOLD**. Nie jest to nowe ustalenie o skuteczności modelu.

| Plik | Strony | SHA256 |
|---|---:|---|
| signed_color.pdf | 6 | `958f34b74ca6c8be0cdfa9018cb11381573257f89270774f44bccb7d2e583c14` |
| gray_sign_hatching.pdf | 6 | `daa912fac7d0b8c9a632b73bdca4c1fc7878340ff965b75df62f05f1f6cc3062` |

## Zgoda i proweniencja

Odczyt dokładnych4 staged PNG i3 full RESULT oraz rzeczywistych outputów odbył się w zakresie nowego grantu `e3d8d7fcb252a12f4cd0871e4541974cc3b75405e5c5add472a3ec773ffa0343`, który jawnie dopuszcza OTHER actual numeric/12page print review. Source manifest `9ce196b3d0e53c58c0dedb0f182675222bb5c3ec2dd96eed07308453aeb40604`, config `a083f9e251367606604344c3def51bc13708d16110ff4ae5c449c399195c8180`, source review `a9992387262d6c3ee157cb4b46aa3a460dd003776d35fff727d5cc5699c368ec` i full numeric review `b9a6a9dd491dfd6f3189deef11855c367ccecbd6d61e8f77452d6c971b993d7c` zweryfikowane. Wszystkie piny staged source, fotografii, wyników i output manifest zgodne. Nie otwierano innych danych, modeli/wag ani benchmarków; brak inference i rerender.

COMPLETE wiąże manifest `b8957ed5c7e0fbc86cd0252c424b054e96cae1af1308736bd1c05f8842873970`; brak FAILED. Stdout potwierdza COMPLETE, stderr pusty. **Ograniczenie exit evidence:** root widział native exit0 w wyniku narzędzia chunk7f4577 i zapisał później ROOT_NATIVE_EXIT_ATTESTATION.json. Zweryfikowano jego zgodność z stdout/stderr/release/COMPLETE hashami. Nie istniał osobny współczesny trwały OS exit receipt; nie twierdzę, że niezależnie odtworzono native exit lub wywnioskowano go z samego COMPLETE. Root attestation jest jawnie posthoc. Nie wykonano powtórnego renderingu w celu „naprawy” tej historii.

## Niezależna kontrola numeryczna i wektorowa

Sprawdzono wszystkie **1536 dopuszczonych odpowiedzi** i **3072 narysowane rekordy** obu editions. Każdy Δz, identyfikator model/input/fill/cell, normalized value, kolor, alpha i negative hatch zgadza się ze źródłem. Każdy warunek występuje dokładnie raz/edition; żadnego wyboru modeli, komórek, historii lub fills.

Wspólne L=maxabs wszystkich512 wartości/model: SelfMAD1.77456533908844, A4.301288306713104, B5.546949625015259. Te same L są na obu zdjęciach/fills w danym modelu. Brak clipping, per-panel normalization, epsilon boost, interpolation lub smoothing; mało kontrastowe mapy kontrolne pozostają mało kontrastowe. To zachowanie danych, nie brakujące wyniki. Wszystkie rzeczywiste L są niezerowe, alpha=.45.

Niezależnie sparsowano **3072 komórki SVG** i **3072 faktycznie wypełnione prostokąty PDF content stream**: pozycje,58mmmap/7.25mmcell, RGB i alpha zgodne z rekordami. W SVG każda z282 negative hatch clips występuje dokładnie wtedy, kiedy Δz<0 w gray edition; w PDF dodatkowo sprawdzono282 odpowiadające clipping rectangles i ich współrzędne. Kolorowa edycja nie ma znakowego hatching. Naprawa przezroczystości działa również w rzeczywistych PDF — nie tylko w syntetycznych testach.

Wszystkie osadzone w12 SVG fotografie są bajtowo/pikselowo zgodne z odpowiednimi czterema PNG; obrazy XObject obu PDF po dekodowaniu mają dokładne RGB tych samych autoryzowanych fotografii. Brak reference00010 lub obcych twarzy. Normalne wyświetlenie źródła i nakładki nie zmieniło oryginalnych source pixel arrays. Raw baseline z jest zgodny z widocznymi wartościami do zadeklarowanego formatowania; nie ma sigmoid/probability interpretation.

Machine checks: `INDEPENDENT_ACTUAL_CHECKS_20261114.json`, SHA256 `a9512f35eb5e12cea0b3d0dedbc04a12d5a2f4042a4a0000d764dcf01fe8b14c`.

## Rzeczywista kontrola wszystkich stron

Przejrzano indywidualnie **każdą stronę1–6 signed_color i1–6 true grayscale print proof** wygenerowanego przez Poppler `-gray`, a nie tylko metryki lub miniaturę zbiorczą. Źródłowe fotografie, obie historie i cztery mapy/stronę są wyraźne; rzeczywista szarość zachowuje znak przez kreskowanie. Nie stwierdzono ucięcia, zasłonięcia podpisów, nakładania paneli lub brakującej strony. Instrukcja pod baseline i tytuł pierwszego fill są ciasno rozmieszczone, lecz znaki pozostają rozdzielone i czytelne; nie jest to blocker.

PDF ma faktycznie180×279.4mm, po6 stron. Minimalny rzeczywisty font8.2pt (odczyt zmiennoprzecinkowy8.199999999999996), baseline9.4pt; wszystkie bounding boxes tekstu wewnątrz strony. Mapy58mm, source faces58mm, footer czytelny i w obrębie strony. Brak dopasowania przez pomniejszanie. Drukować w100%/actual size, wycentrowany na A4 lub Letter; jeżeli konkretny sterownik wymusza mniejszy obszar drukowalny, nie akceptować automatycznego shrink poniżej8pt. To kontrola rzeczywistych renderów/print proofs, nie fizyczny test na konkretnym drukarce.

## Opis i ograniczenia

Polskie legendy poprawnie mówią: czerwony=zasłonięcie podnosi z; niebieski=obniża, większe z=silniejsze wskazanie morph. W grayscale wielkość i znak są rozdzielone; skala jest model-specific. Wyraźnie napisano, że nie jest to prawdopodobieństwo, maska tworzy artefakt i nie wskazuje przyczyny. Brak fałszywego seam/identity-causality claimu; native/history kadry nie są anatomicznie dopasowane.

Przeczytany English caption zachowuje dwa potencjalnie eksponowane developmental examples, post-hoc SelfMAD demonstration choice, all-model retention, różnice rozdzielczości, genuine/no seam, locality-not-causality i ranking NOT_QUALIFIED/5FAIL. Credits autorów/CC BY-NC2.0 są widoczne; exact URLs/licences i history265/249→alignment512 są w manifest. Do prywatnego udostępnienia dołączyć caption i MANIFEST, nie przedstawiać samego PDF jako kompletnego pakietu publikacyjnych praw. Użycie słowa „morph” opisuje kierunek wyjścia modelu, nie etykietę tych genuine fotografii.

Można teraz pokazać użytkownikowi wszystkie6 stron każdej edycji w tym dokładnym pakiecie, bez wybierania tylko mocnych map. Nie zmieniać naukowych wniosków ani manuskryptu. Stary322mm pack zachowany; nowy standard-page pack jest zatwierdzonym prywatnym materiałem prezentacyjnym. Publiczne użycie nadal HOLD.
