# VIS2 — niezależny postreview pełnego pomiaru liczbowego

2026-11-14. Recenzent training_contribution, inny niż autor. **PASS_ALL3_TECHNICAL_FULL_NUMERIC_ONLY**. Wszystkie1536 odpowiedzi spełniają techniczne warunki kompletności, geometrii i arytmetyki. Wynik może zostać osobno przyjęty przez root jako źródło prywatnego renderingu po jego niezależnym source review i nowym render grant. Nie jest to dowód skuteczności, przyczynowości ani zgoda publikacyjna.

## Zgoda i wykonanie

ROOT_FULL_RELEASE SHA256 `04de9364ee7302c413e6279afae23bfb18325a80dc41a8deccffa21d6d19f61c`, commit `7fcc1cd5d186f7810c62787b36ecaadcfadb8dc9`, wiąże niezmieniony source commit `29da6d932c199e9f2ef0dd923cce0dabdc1fe0e0`, inventory `11316da9452632614dd85ae8cd659c7e363467a6f66590a8dc6b21125b1dfcf9`, source manifest `31ae2f57c2212c2ac85a90360753e9f20e5db98a6ba3e5c4a9dd5efaa686b0cb` i actual smoke postreview `5085f250a1b1b136029c700448adf12ba39648ec7a88f5d9de38b65edc00d6cd`. Zgoda jawnie dopuszcza OTHER full numeric postreview; nie dopuszcza renderingu. Bajty owned source i release porównano z właściwymi commitami. Nie czytano obrazów, wag, modelu lub sealed data; brak nowej inferencji/rerun/statystyki.

Driver `/mnt/t7/smad_next/coordination_20261114/vis2_full_execution_20261114T215734Z` uruchomił dokładne polecenia `--phase full` z ROOT_FULL_RELEASE i trzema modelami w stałej kolejności. STARTED podaje phase full, brak compute apps oraz99,963,150,336 wolnych bajtówT7 (≥50GiB). Związany driver zachowuje mutex/15min timeout/model. Wszystkie trzy native exit0; końcowy TERMINAL22:04:55.814321Z ma ALL_COMMANDS_EXITED_ZERO. Stdout każdego modelu potwierdza full512, wszystkie stderr puste. Żaden model nie zniknął, nie był zastępowany lub ponawiany.

**Jawna korekta metadanych:** oryginalny TERMINAL zawiera błędny odziedziczony literal `full_launched=false`. Osobny ROOT_DRIVER_METADATA_CORRECTION.json wskazuje true i przyczynę: skopiowany smoke driver. Zweryfikowano tę korektę wobec rzeczywistych CLI, release, STARTED i wszystkich trzech RESULT/output paths phase full. Oryginalnego drivera/TERMINAL nie przepisano; korekta i ich hashe są w checks. To błąd podsumowującego pola, nie zmiana obliczeń lub brak full. W `root_checks` zgody pozostało również odziedziczone sformułowanie „fixed smoke namespaces absent”; nie użyto go jako dowodu świeżości full. Świeżość fixed full namespace wynika z przypiętego `mkdir(exist_ok=False)` przed loadingiem i późniejszego successful completion. Nie wprowadzono nowego tolerowania błędów numerycznych.

## Kompletność i liczby

| Model | Odpowiedzi | Native exit | Max baseline residual | Worker time | RESULT SHA256 |
|---|---:|---:|---:|---:|---|
| selfmad_hrnet_w18 | 512/512 | 0 | 0.0 | 12.361615s | `09cd72628b90ccdae6f62b2033bebd3fe1d19eb59e3ce5899014308b2b43ca60` |
| A403 (CLI A) | 512/512 | 0 | 0.0 | 7.470570s | `0aa4fb2489a30f0fea2ce4f658d59e77f60a26a7ce88458023e0f914e6397722` |
| B403 (CLI B) | 512/512 | 0 | 0.0 | 7.656747s | `b02df0ec784662025bf4e6c6ed988718970e0686853157ddc4257bcba70f8ac4` |

Sprawdzono cały iloczyn4 wejścia×2fills0/128×64cells, kolejność i unikalność1536 rekordów. W każdym: współrzędne row-major8×8/native512, patch64×64/4096 pikseli, poprawny baseline i finite zorig/zocc/Δz. Wszystkie równania Δz=zocc−zorig zgodne do tolerancji arytmetycznego porównania1e−12 (nie jest to tolerancja reprodukcji modelu). Wszystkie12 zapisanych baseline logits są dokładnie równe starym dopuszczonym VIS1 anchors, residual0, przy prereg gate≤1e−5.

Każdy z12 progress JSON jest dokładną odpowiednią częścią RESULT. Rehash wszystkich STARTED/RESULT/progress oraz SHA256.json zgodny; katalogi zawierają dokładnie te JSON-y i nic dodatkowego, brak RGB/obrazów/features. Nie ma FAILED.json/partial result; successful terminal i kompletność stanowią dodatni dowód, nie sama nieobecność failure. Wszystkie odpowiedzi zachowane, bez wyboru znaków/magnitud i bez oceny wyglądu map.

Runtime: GB10, torch2.12.1+cu130/CUDA13.0, SelfMAD384 i A/B224, batch1, float32/no autocast/no gradients/noTTA, TF32matmul/cudnn off. Mandatory memoryprep↔ImageItems tensor equality, repeat/no-op≤1e−5 oraz eval/frozen są poświadczone control-flow exact worker przed COMPLETE; osobnych residuals tych checks worker nie serializuje. Nie przeliczano inferencji niezależnie i nie przypisuje się cudnn.deterministic=False gwarancji bitowej deterministyczności. Oprócz1536 perturbacji wykonanie obejmuje36 forwardów baseline/repeat/no-op, czyli1572 dla całej fazy. Czas worker nie jest pełnym rozliczeniem zasobów.

## Dyspozycja

Przyjąć jako pełne, technicznie poprawne dane opisowe Phase A. Zachować wszystkie modele, dwa fills i oba histories dla obu genuine fotografii. Sama occlusion może wprowadzać artefakty; wspólne image-grid coordinates nie gwarantują wspólnego położenia anatomii, a native/history różnią się alignment/crop. Nie istnieje tu empiryczna splice seam mask. Te dane nie uzasadniają identity causality, odczytu zamkniętych benchmarków, wybierania sieci, zmiany ranking NOT_QUALIFIED/5FAIL ani claimu operational utility.

**Rendering nadal HOLD:** osobna akceptacja numeric przez root, niezależnie zrecenzowany renderer i nowy prywatny grant są wymagane. Żadnego renderingu nie wykonano w tej recenzji. Publication/rights/likeness/consent/501 extension pozostają HOLD. Source i manuskrypt pozostały niezmienione.

Pełne machine checks: `INDEPENDENT_FULL_POSTREVIEW_CHECKS_20261114.json`, SHA256 `7e90507aabf1fef35565c7b8305b74d903461db20f1422c6817ecdb1543c1892`; zawierają piny zgody, commit-bound source, terminali, korekty i wszystkich numerical outputs. Nie uruchamiać ponownie full z powodu opisowego błędu drivera.
