# Odzyskanie wyników po przerwie limitów — 15 listopada 2026

Zabezpieczono 14 pełnych archiwów, 17 205 616 640 bajtów: SelfMAD401/402 (WCSS), pełne MixFaceNet401/402 (WCSS), MADation B401–405 i L401–405 (Athena). Sumy SHA256 zgodne z sidecarami, źródłem przed/po transferze i kopią DGX. Oddzielne katalogi platform zapobiegają kolizjom nazw. Nie otwierano wnętrza archiwów ani scoreów; zebranie nie oznacza dopuszczenia naukowego.

Ostatni zapisany odczyt WCSS: SelfMAD403/404 RUNNING,405 PENDING; wcześniejsze wszystkie50SPRINT i5MixFaceNet ukończone. IDistill6312778 TIMEOUT. Próba runtime6324846 TIMEOUT, nie naukowy fit. Tablica6294928_4–14 nadal JobHeldUser; brak ingerencji. Athena: komplet5B+5L MADation COMPLETED, kolejka pusta. Brak nowego grantu nie oznaczał zatrzymania istniejących zadań na starym koncie.

Pełny inwentarz284 wierszy WCSS i14 Athena oraz nieprzetworzone stdout/stderr znajdują się obok. Wyniki historyczne sprzed przerwy pozostają w oryginalnych kolekcjach; zidentyfikowane77 archiwów bez lokalnej kopii tej samej nazwy/rozmiaru obejmuje głównie wcześniejsze smokes, diagnostyczne części i generację. To inwentarz metadanych, nie lista nowych nieodebranych ukończeń. Dwa brakujące pełne archiwa MixFaceNet zostały dodatkowo odzyskane. Nie zgłaszamy, że skopiowano każdy historyczny plik klastra.

Źródła i dokładne hashe: RECOVERY_SUMMARY.json oraz SELF_COLLECTION_VERIFIED.json, MIX_COLLECTION_VERIFIED.json, ATHENA_COLLECTION_VERIFIED.json. Kolejny etap to niezależne sprawdzenie kwalifikowalności i wykonania MADation przed dopuszczoną ewaluacją. Nie zmieniono cutoff ani nie odczytano FRLL/candidate scores. Nie submitowano/anulowano zadań ani nie wynajęto GPU.

Durable source: /mnt/t7/smad_next/coordination_20261114/post_limits_recovery_20261115T174931Z
