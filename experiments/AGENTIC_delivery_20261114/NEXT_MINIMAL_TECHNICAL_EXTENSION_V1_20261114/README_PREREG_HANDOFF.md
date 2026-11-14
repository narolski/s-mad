# NEXT — minimal technical extension v1

**PROPOSAL / IMPLEMENTATION REVIEW REQUIRED. REAL EXECUTION HOLD.** Nowe źródła `src/NEXT/minimal_technical_extension_v1/`, evidence `NEXT_MINIMAL_TECHNICAL_EXTENSION_V1_20261114/`. Nie modyfikuje v1/v2/v2r1 ani ich wyników, canonical NEXT lub scientific admission. Nie wykonano rzeczywistego archive/header/member/log/NPZ/checkpoint access. Testy używają wyłącznie syntetycznych tarów, w tym syntetycznych opaque bytes bez modelu.

## Dokładna prospektywna specyfikacja

Scope20records,35members:

- 15BB2L A/B/Sb403–407: wyłącznie `{task}/task_info.txt` i `{task}/task.env`. Native helper wymaga jednego tokena bs z następnym literalnym256 i jednego accum z1. Spacje/tab/newline mają semantykę source `.split()`. Task.env sprawdza dokładne TASK/ARM/SEED: native count(expectedline)==1, dodatkowa strictunique key kontrola jawnie osobna. Ogólny status EXPECTED_MATCH wymaga wszystkich pięciu strictmatches; to nie zastępuje naukowej/native eligibility. Brak/incomplete tokena/membera→UNKNOWN; wrong/duplicate→FAIL technicznego dopasowania. Native Boolean pozostaje jawny także dla missing/duplicates. Observed128/2 jest mismatch, nie alternatywa. Nie czyta arch/meta/loss/GPU/score fields ponownie.
- 5RZ1_SbMR512408–412: dokładnie `{task}/last_trainable.pt`, nazwa wyprowadzona z rz1_score.py68 i run_rz1.sh118–122. Sprawdza regularność, unikatowość w całym tar i oblicza opaque SHA256 strumieniowo w chunk1MiB. Nie parsuje nawet nagłówka formatu checkpointu, nie torch.load, nie np.load, nie ekstraktuje na dysk. Hash nie wychodzi do wyniku przed ukończeniem całego header safety/uniqueness traversal. Absence→UNKNOWN/MEMBER_ABSENT. Wynik ma identity „trainable overlay”, bytes i hash; nie certyfikuje shapes/statekeys/reload/modela. **Nie podstawia oryginalnego full last.pt digest.**

Archive paths/SHA pozostają dokładne z v2r1. archive_bytes pochodzą wyłącznie z wcześniejszych opaque collection receipts, bez stat/open archive podczas przygotowania. Obowiązuje ta sama pełna denominator5/failure retention; wynik nie usuwa innych57records z wcześniejszego admission inventory, tylko wiąże nowy technical attachment.

Oczekiwane256/1 jest prebound proposal `9bec95b40e65695a2899c55ec54bc21fefd408bb699ee1060a2101ea7d19baac` plus independentexpectedreview `b5b3394f76aa000f765a3b49f46687f4b49612aa0845d805ee7077f8318fee4f` oraz przypięta ROOT_EXPECTED_BATCH_ADOPTION.json. Poprzedni wynik wiąże też ROOT_NEXT_TECHNICAL_RESULT_ACCEPTANCE_20261114T200359Z.json. Normatywne expectation nie jest dowodem faktycznego sbatch export ani wyłączenia BB2_TASKS/remap/rerun. Historyczne job/index są tak oznaczone. Actualmatch nie awansuje ich do verifiednative provenance. Source native_adapters.py dopuszcza ogólnie128/2 lub256/1, lecz obecny NEXTpreflight wymaga256/1; brak posthoczmiany.

Pinned prior typed output SHA `26e4c677da313ce39583a4a9cb9877089fbec325f0bfc319362fc2861dbc602b`, postreview `edecba0c4e75befb1b4ba9b225e88d969150dc81d8fb57c96380b5dca77337d2` i checks `1cf06d433e028f302e9e16e5ff17b0aafb5fbd04fdf5c7e242419376da50dcce` pozostają dokładne, bez modyfikacji/rekolekcji77. Pięć RZ1R gate.manifest strict-onlyFAIL pozostaje poza zakresem; nie oznacza nativeFAIL i nie jest naprawiane.

## Bezpieczeństwo i release

Standalone collector bez sibling importów i productionloaderów. Same regular descriptor SHA+size beforetar, O_NOFOLLOW, reject pathaliases/traversal/links/devices/sparse, max100000headers,8MiB/TXT; opaque member bounded by exact receipt archive size and streamed. Brak raw text/values/exceptionrepr output. Hashes/descriptors/stałe statusy i native-versus-strict booleans only. Nie czyta info.train_acc_rule0 ani innych scientificmetadata.

CLI przed jakimkolwiek actualarchiveopen wymaga exact scope/source/review/output pins, CPUenv, root literal adoptions expectedbinding+priorpostreview, explicit actualmemberaccess i checkpoint_hash_only_no_decode. Scope validator wymusza dokładne20nazw,35members, operacje i niezmienne256/1; nie można poszerzyć tylko edytując JSON. Wymagany independent review line: `GO_NEXT_MINIMAL_TECHNICAL_EXTENSION <collector_sha256>`. Template decisionHOLD nie jest release. Wynik create-only, exclusivepartial→fsync→atomicrename, końcowy fsynced marker NOT_SCIENTIFIC_ADMISSION. Incomplete output nie oznacza completion ani retrypermission.

## Testy i przekazanie

9synthetic unit tests PASS. Obejmują source token semantics/wrong128/2/duplicate/missing, native env vs strictduplicate, scientificcanaries,9MiBsyntheticcheckpoint streamed bez innychextracts, absentcheckpointUNKNOWN, tar aliases/traversal/symlink/hardlink/device z blokadą partialhash, archivehash/size mismatch, invalidencoding/textcap, hardcodedscope i pełne syntetyczne20record CLI z release-before-access, durability i create-only guard. Synthetic review/release istnieją wyłącznie w usuwanych TemporaryDirectory i nie uprawniają do prawdziwych archiwów.

```sh
cd /home/narolski/smad-next/src/NEXT/minimal_technical_extension_v1
python3 -m unittest -v test_minimal_extension_v1.py
```

Proponowana komenda dopiero po OTHERreview, rootadoptions, cleancommit/pins i osobnym rootrelease; NIE WYKONANO:

```sh
CUDA_VISIBLE_DEVICES='' timeout 900s python3 /home/narolski/smad-next/src/NEXT/minimal_technical_extension_v1/minimal_extension_v1.py --scope /home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/NEXT_MINIMAL_TECHNICAL_EXTENSION_V1_20261114/SCOPE_PROPOSAL.json --release /mnt/t7/smad_next/NEXT/minimal_technical_extension_v1_ROOT_RELEASE.json --output /mnt/t7/smad_next/NEXT/minimal_technical_extension_v1_collection_20261114
```

Scope przygotowano source-only przed actualextensionmetadataread; nie zmienia rejestracji metryki/populacji/threshold/kolejności/seeds. Po collection potrzebny niezależny technical postreview. Wszystkie scientificpayload/IDs/floor/C2P/NI/exposure/kernel/Sbc/GX/freshconfirmation gates pozostają. Kończę bounded handoff.
