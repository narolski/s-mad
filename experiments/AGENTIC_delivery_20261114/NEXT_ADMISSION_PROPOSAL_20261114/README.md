# NEXT — propozycja zamknięcia metadanych, 14 listopada 2026

Status **NOT_ADMITTED**. Pakiet nie jest kanonicznym admission: inny schema, approved=false, batch_closed=false, wszystkie osiem pozycji HOLD, exposure=null. Nie uruchomiono preflight, readera ani journal. Nie otwarto archiwów, nagłówków, NPZ, wag ani wyników. Nie wykonano operacji klastrowych. Normalizacja korzysta wyłącznie z jawnych źródeł i opaque collection receipts. Kod budujący pakiet nie importuje kodu NEXT.

ADMISSION_PROPOSAL.json przypisuje 65 istniejących sieci do ról według aktualnego readera; ARRIVAL_RECEIPTS_DRAFT.json zachowuje ścieżkę dowodu, jego hash i czas ze strefą. Hash_verified oznacza świadectwo wcześniejszej weryfikacji root, nie ponowny odczyt archiwum przez autora tego pakietu. Dodatkowe pięć RZ1R_A zachowano jako dostępny materiał; nie podstawiono ich pod oryginalne AB1_A. NATIVE_SOURCE_INVENTORY_DRAFT.json zawiera tylko rzeczywiście związane native_fit. Brak źródła daje null i jawny missing_archive_roles, nie brakujący seed naukowy.

| Kolejność | Ramię | Konkretny stan / pozostający HOLD |
|---|---|---|
|1|SbFM|Pięć AB1FM i wspólny supplement dostępne. Brakuje w wykorzystanych receipts dziesięciu oryginalnych AB1_A/Sb 408–412. Config i producent mają źródłowe priory; runtime gates nieodczytane.|
|2|GX|Brak dowodów pełnego amendment-2 inputs/producer/floors/fit/native closure. To nie automatyczna niekwalifikowalność.|
|3|SbMR|Pięć candidate, Sb0, A0 i RZ1R_Sb mają przypisane przybycia. Exposure i runtime metadata do niezależnego zamknięcia.|
|4|SbM|Jak SbMR, właściwe osobne candidate.|
|5|Sb512|Całe pięć candidate/A512/Sb0/yardstick dostępne. Bez zakładania wyniku bramek.|
|6|SbMR512|Wszystkie fit dostępne; §3/§5(e) wymagają kernel prereg i adaptera, obecny reader jawnie odmawia. Brak implementacji nie jest powodem wyłączenia naukowego.|
|7|Sbc|Fit i A0 comparator/control dostępne; pytanie autora M7/§12q4 pozostaje oczekujące. Nie podstawiać Ac ani domyślnej zgody.|
|8|DINOv3|E3 five-mode zamrożony i 15 fit + W2 przybyły. Brakuje receipts oryginalnych pięciu AB1_Sb; nie redukować średniej comparatorów.|

## Najkrótsza kolejność bez GPU

1. Niezależnie sprawdzić tę normalizację i odnaleźć istniejące receipts oryginalnych dziesięciu AB1 A/Sb. Nie otwierać checkpointów. Jeśli nie ma receipt, root może osobno wykonać opaque hash/stat/sidecar kolekcję dokładnych dziesięciu plików; źródłowy pin Sb pozostaje twardym warunkiem. Odnaleźć i jawnie związać wszystkie native manifest paths, ich dotychczasowe hardpins i train-list refs — obecny draft ma priory, nie pełną manifest closure.
2. Związać źródła faktycznych producentów z submission receipts i archiwami; producent w źródle nie dowodzi runtime. Draft arrival producer_sha256=null jest celowy: nie przepisywać tam sha programu tylko po to, aby przejść check_arrival.
3. Przygotować osobny minimalny collector technicznych metadanych, niezależną recenzję i dokładny root release. Zakres proponowany poniżej, jeszcze nie zaimplementowany ani uruchomiony. Pozostawić wszystkie próby/niepowodzenia, nie wybierać działających seedów.
4. Osobno zamknąć ruling autora Sbc, przegląd/prospektywną rejestrację kernel SbMR512 oraz GX provenance/native closure. Nie nadaje się tu nowego policy ani reason=code_gap. Zachować cutoff 15 XI 18 CET i istniejące powody v3.
5. Dopiero po tych dowodach: finalne dyspozycje wszystkich ośmiu, exposure review, czysty commit exact pins/admission, niezależna recenzja dokładnego hasha. Ten pakiet nie tworzy uprawnienia do tego kroku ani do scientific read.

## Proponowany ograniczony collector, wymagający osobnego release

CPU lokalny, bez CUDA, bez modeli/importu production readera. Roster dokładnie z finalnie związanych archive+sha; w pierwszej fazie tylko źródłowo uzasadnione poniższe nazwy. Bez extractall, symlinków, aliasów lub nieograniczonego discovery; limit 8MiB/member, odmowa duplicate/unsafe paths. Zapisać surowe hashe i znormalizowane techniczne pola, nie wyniki naukowe. Pełne logi mogą ujawnić metryki, dlatego nie publikować ich: parser wyłącznie finite-loss/guard status, żadnych AUC/logitów. Oddzielny output namespace i brak NEXT journal.

- native_fit: `{prefix}/gpu.txt`, `task_info.txt`, `task.env`, `meta.json`; `train.log` tylko kontrola istnienia i skończoności zarejestrowanej sekwencji loss. Priory z native_adapters.py load_fit: architektura, pack/overlay hash, 6250 kroków, limit=0, batch E3 [256,1], manifesty/seed.
- rz1_fit: te same metadata, dodatkowo `{prefix}/rz1_transform.json`, `guard.log`. Priory ARM_SPEC/PINS i właściwe n_items z support. Nie odczytywać score NPZ.
- rz1_refit: `{prefix}/gpu.txt`, `task_info.txt`, `gate.json`; exact AB1 source sha i 21277 wierszy, byte gate. Wartości technicznego gate wymagają jawnego release; brak dowodu nie oznacza failed gate.
- SbFM supplement: `config.json`, `pre_read_receipt.json`, `technical_status.json`, `gate_{source}.json` dla dokładnych pięciu SbFM i pięciu AB1_Sb. Config hash ze źródła, źródła i manifest rows dokładnie jak native_adapters. Bez rodzinnych NPZ.
- W2: `out/tasks.txt`, `out/gpu.txt`, `out/scripts.sha256`, `out/n_fail.txt`, `out/n_refused.txt`, `out/gate_{source}.json` dla 15 BB2L i pięciu AB1_Sb. W2_SCRIPTS z przypiętego adaptera, bez gd0/gd1/gd2 i bez NPZ.

To nie zamknie checks wymagających score/row identity lub splice-fit; pozostają w zarejestrowanym readerze po dopuszczeniu. Nie proponuje się ad hoc np.load nawet tylko nagłówków.

## Świeże 413–417 po selekcji

Nie uruchamiać teraz. Wygenerować osobny hash-bound roster z pięcioma candidate oraz świeżymi comparatorami, controls i yardsticks; dla E3 świeże A/B/Sb i pięć świeżych CLIP Sb (nierównoległe statystycznie tak jak v3). Dla SbFM wspólny supplement obu porównywanych ról i właściwy A; dla RZ wszystkie role z obecnej mapy, niezależnie od zwycięzcy. Wszystkie support/transfer/floor/identity/kernel i splice/adequacy bramki pozostają. Native source_identity i hardpins obecnie ograniczone do starych seedów — potrzebna prospektywna rejestracja producentów oraz przegląd stage adapterów, nie tylko pięć fit zwycięzcy. Brak komendy wykonawczej dla świeżej fazy jest jawnym brakiem implementacji, nie powodem zmiany reguły.

F1 review i aktualne źródła są związane w SOURCE_BINDINGS.json. Ten pakiet pozostaje propozycją do niezależnego przeglądu, bez self-GO.
