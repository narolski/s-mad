# NEXT — implementacja collectora technicznych metadanych v1

**Do niezależnej recenzji implementacji; wykonanie HOLD.** Źródło: `src/NEXT/technical_metadata_v1/technical_collector_v1.py`. Nie zmieniono istniejącego readera/native adapterów ani zamrożonych propozycji v1/v2. Nie otwarto rzeczywistych archiwów (także headers); wszystkie wykonania collector functions dotyczyły syntetycznych plików w TemporaryDirectory.

## Granica serializacji

TYPED_SCOPE.json rozwija 77 archive records i konkretne member→parser→typed keys/expected values z wcześniej zrecenzowanej listy. Priory pochodzą z source AST (bez importowania readera), cfg oraz metadanych manifestów. Parser SelectiveJSON pomija nieallowlistowane scalar values bez JSON decode/numeric conversion; sprawdza tylko składnię i duplikaty kluczy także w pominiętych obiektach. Wybrane struktury są sprawdzane przez json_checks. Zwraca wyłącznie booleans, counts, reason codes i zarejestrowane identyfikatory source/family z zamkniętej listy; nigdy surowe wartości dowolnych string/numeric fields. Exact gate max_abs/own_rule_agree są przekształcane w equality booleans. Opaque hashes ujawniają zmianę bajtów, co jest jawnie dopuszczone; nie ujawniają wartości.

TXT task/env wybiera jedynie jawne expected fields. Loss nigdy nie jest drukowany: tylko obecność/liczba/finite boolean dla pełnych jednoznacznych linii `loss=number` (obsługiwane też separatory space/colon). Szeroki regex starego readera mógłby objąć val_loss. Brak source-udowodnionej pełnej gramatyki runtime logu oznacza, że collector jawnie zapisuje native_loss_gate=HOLD i UNAMBIGUOUS_LINES_ONLY. To częściowy dowód, nie modyfikacja naukowego kryterium. Ambiguous lines nie są alternatywnym failed scientific gate.

Pozostałe jawne partial checks: config/status list members sprawdzają typy/membership, a nie pełne one-to-one połączenie source+seed+sha; RZ1R sprawdza wybrany identity/byte-gate subset. Niezależny odbiorca musi zachować HOLD pełnych registered gates; nie traktować samych true checks ani COLLECTED_TECHNICAL_ONLY jako fit PASS. Każdy member/seed zostaje w wyniku, także brakujący lub odmówiony. Collector nie podejmuje dyspozycji ośmiu ramion.

## Bezpieczeństwo i autoryzacja

Weryfikacja release i review następuje przed collect_archive. Release wiąże packet SHA, collector SHA, dokładny output, CPU-only i implementation review path/hash. Review musi mieć osobną linię `GO_NEXT_TECHNICAL_IMPLEMENTATION <collector_sha256>`; autor implementacji jej nie dostarcza. PINs source/v2 sprawdzane przed otwarciem archiwów. Packet ma dokładnie 77 records. Release template ma decision=HOLD, nie jest uprawnieniem do uruchomienia.

Po osobnym release: ten sam otwarty regular-file descriptor służy do opaque SHA i traversowania tar; O_NOFOLLOW, brak alias/symlink ścieżki archive. Tar odrzuca absolute/.., duplicate/normalized alias, link/device/sparse entries. Odczytuje zawartość tylko jawnych metadata members; nie wywołuje ekstrakcji na dysk, NPZ/header readers, modeli ani production loaders. Limit8MiB/member,256MiB parsowania/archive,100000headers,depth64. Kontrola całego tar może odmówić także niebezpieczny nieallowlistowany member. Wszystkie komunikaty błędów są stałymi kodami, bez interpolowania wyjątku pochodzącego z danych. Output directory create-only jest warunkiem wejścia; przerwanie może pozostawić niekompletny katalog, nie wolno traktować tego jako wyniku lub automatycznie retry.

## Weryfikacja syntetyczna

14 unit tests PASS na gx10. Dodatkowo wszystkie77 schema records uruchomione na2 synthetic canary variants (154synthetic archives); output bez hashów jest identyczny przy zmianach AUC/EER/APCER/BPCER/val metrics. Unit tests obejmują selective skip bez decode, unknown nested duplicates, typy/encoding/składnię, text canaries, finite/nonfinite/ambiguous loss, forbidden NPZ/weights never-extract, unsafe tar aliases/links/traversal, caps/truncation/hash mismatch, missing members, sanitized failures, retained failed models, release refusal przed archive call, zakazane importy. Test scope odczytuje wyłącznie TYPED_SCOPE.json i konstruuje nowy syntetyczny archive; nie dotyka archive path z packetu.

Dokładne komendy powtórzenia testów:

```sh
cd /home/narolski/smad-next/src/NEXT/technical_metadata_v1
python3 -m unittest -v test_technical_collector_v1.py
python3 test_scope_coverage_v1.py /home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/NEXT_TECHNICAL_COLLECTOR_V1_20261114/TYPED_SCOPE.json
```

## Proponowane wykonanie dopiero po review i root release

Root powinien zamknąć source/input clean commit, niezależny exact implementation review oraz release z nowym durable output namespace. Propozycja ograniczenia: lokalny CPU, CUDA disabled, timeout900s; brak klastrów/GPU/modeli. Nie uruchamiać podanej komendy z template HOLD ani zastępować jej release bez autoryzacji:

```sh
CUDA_VISIBLE_DEVICES='' timeout 900s python3 /home/narolski/smad-next/src/NEXT/technical_metadata_v1/technical_collector_v1.py --packet /home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/NEXT_TECHNICAL_COLLECTOR_V1_20261114/TYPED_SCOPE.json --release /mnt/t7/smad_next/NEXT/technical_metadata_v1_ROOT_RELEASE.json --output /mnt/t7/smad_next/NEXT/technical_metadata_v1_collection_20261114
```

Nie wykonano tej komendy. Po collection potrzebny niezależny przegląd rzeczywistych technical results. Exposure/eligibility, Sbc author ruling, SbMR512 kernel/adapter, GX, final admission i świeże413–417 pełne role pozostają niezależnymi HOLD. Nie ma canonical ADMISSION, batch_closed, scientific permission, NEXT preflight, journal ani training command.
