# NEXT technical collector v2 — bounded source handoff

**IMPLEMENTATION REVIEW REQUIRED; REAL COLLECTION HOLD.** Przyjęty zakres: ROOT_NEXT_V2_IMPLEMENTATION_ADOPTION_20261114T192658Z.json, source plan oraz niezależna recenzja i SOURCE_GRAMMAR_MAP. Nie otwarto rzeczywistych headers/members/logs/NPZ/checkpointów. Brak native-reader imports, modeli, klastrów, GPU, commitów i naukowego admission. Propozycje v1/v2, collectorv1 oraz canonical NEXT pozostają bez zmian.

Źródła w `src/NEXT/technical_metadata_v2/`: collector, pure native_metadata_predicates_v2, builder i trzy pliki testowe. TYPED_SCOPE.json zachowuje77records (75networks+2supplements), role i denominator5. SOURCE_PREDICATE_MAP.json wiąże wszystkie człony/metadane z funkcją i liniami źródła; wyniki przyszłego collectora zawierają per-record native predicate matrix: źródło/evidence/raw type/native PASS–FAIL–UNKNOWN/strict integrity osobno. Żaden zbiór technicznych PASS nie oznacza całkowitej kwalifikowalności. NPZ/ID/floors/C2P/NI/kernel/exposure pozostają DEFERRED_TO_REGISTERED_ONCE_READER lub osobnym wymaganym rozstrzygnięciem.

## Zmiany względem v1

- Supplement: dokładne configured tuple(name,seed,SHA,manifest,rows), pojedynczy status po name/seed/gate, ten sam source-bound exact_gate, dokładnie tt1+meds bez duplikatów, literal valid=true, SHAshape. Config opaque bytes i pre-read receipt hash. Planned global roster jest osobną kontrolą integralności; cudze failed models nie wymazują pozostałych. Nie czyta familyNPZ.
- W2: wszystkie20planned tasks jako integrity, native unique/source-membership osobno,3script hashes, source-bound gates, H100 substring zgodny z konkretnym loaderem. Counter używa native int conversion; strict lexical grammar jest oddzielna. Ujawniane wyłącznie nonnegative count/conversion status, bez dowolnego raw tekstu. GD wykluczone.
- RZ1R: wszystkie PINS, historyczny scorer02628562…, train_Sb history, source_tar/SHA/limit i bytegate. Native substrings są odróżnione od silniejszej unique-token integrity. Gate.manifest pozostaje dodatkową kontrolą integralności, nie native wymogiem. Nie interpretować braku takiej kontroli jako failed scientific gate.
- Meta numeric native equality zachowuje Python bool==int; strict type raportuje różnicę. Literal Boolean gates zachowują isTrue/isFalse. res512 to tekst '1'/'0', bez bool(string). Nieobsługiwany niefundamentalny typ pola oznacza UNKNOWN, gdy jego pominięta projekcja nie pozwala odtworzyć native string conversion.
- Loss: dokładny oryginalny unanchored case-insensitive regex `loss[ =:]+(-?(?:inf|nan)|[-+0-9.eE]+)` na całym logu. Dozwolone jedynie presence,count,finite boolean i fixed conversion reason. Nie eksportuje values,captures,labels,lines. `val_loss` również może się dopasować; nie ma twierdzenia training-only. Osobno zachowane native_fit all(generator) short circuit oraz RZ najpierw pełna konwersja listy, więc późniejszy malformed token może różnie kończyć te źródłowe predykaty. Przyszły root release musi ponownie jawnie ustawić whole_log_original_regex_boolean_only=true; obecne source-only przyjęcie nie upoważnia do real log scan.

## Konkretne UNKNOWN

UNKNOWN_PROOFS.json enumeruje15BB2L A/B/Sb403–407: brak source-bound dowodu dokładnej zgłoszonej pary bs/accum. Dopuszczalne historycznie128×2 lub256×1 nie dają prawa wybrać dowolnej po odczycie. Nie kopiujemy starego draftu256×1 jako dowodu. Bez proof field native exact_submitted_batch pozostaje UNKNOWN; docelowe per-record proof musi zostać prospektywnie związane z source receipt i przeglądem kolejnego packetu. Same effective batch256 nie wystarcza. Pozostałe recipe pola nadal są kontrolowane.

Wszystkie77archiwa zachowane przy missing/failed/refused member. Brak dowodu nie jest automatyczną final ineligibility żadnego z8ramion. Nadal otwarte exposure/eligibility, independent code/release, Sbc author ruling, GX source/input/fit/floor closure, SbMR512 osobna rejestracja/scorer/kernel, fresh413–417 pełne role.

## Pięć SbMR512 — dodatkowe pola techniczne

Bez nowych modeli/populacji: wyłącznie RZ1_SbMR512_s408–412, już w77. Przygotowane member descriptors `{prefix}/info.json` (rz1_score.py123–129) i `{prefix}/env.txt` (run_rz1.sh119), istniejące meta.json/transform.json. Allowlistinfo: torchVersion, normalizedH100, seed,steps,res,primary,last_pt_sha256,common_py_sha256,rz1_kernels_sha256,limit. train_acc_rule0,train_hours,seconds,host,run,counts i wszystkie scientificsiblings są pomijane selektywnie bez decode wartości. Version eksportowana tylko przez ograniczoną gramatykę techniczną, digest tylko64hex, GPU tylko znaneH100. env wybiera tylko torch,cuda,tf32 przez literalne klucze/gramatykę, bez reszty linii.

`info.last_pt_sha256` to hash pełnego oryginalnego last.pt, **nie** wyeksportowanego trainable-only last_trainable.pt. Producent zapisuje trainable plik, lecz nie zapisuje jego indywidualnego hasha: descriptor jest stały, hashUNKNOWN; nie sprawdzać wag. Meta.arch/res/seed i res512 kontrolowane źródłowo; dodatkowe arch/res512 provenance nie udają istniejących native wymogów. Scorer source SHA jest przypięty w packet; nie oznacza actualruntime attestation. Source TF32=true/no-flip float32forward są prior; env.txt jest świeżym innym procesem i nie potwierdza TF32 scorera. CUDA/scorer runtime i byte identity/rebuild pozostająUNKNOWN do właściwego release i recenzji. Ten collector nie implementuje kernel supplementu.

## Testy oraz bezpieczne wykonanie

23synthetic unit tests PASS: original-loss edgecases i branch conversion semantics, literal Boolean/rawtypes, supplement duplicate/mismatchedtuple/family/literalvalid failures, native-vs-strict RZ/W2, missing BB2proof, res512 string, selectiveinfo canaries oraz wcześniejsze tar/release/payloadskip tests. Ponadto77schema records×2canary variants=154synthetic archives PASS: zmiany AUC/EER/APCER/BPCER/train_acc_rule0/val metrics nie zmieniają output poza opaque hashes; zmiany matching nonfinite lexical loss mogą zgodnie z przyjętą granicą zmienić tylko techniczne presence/count/finite/conversion booleans. Żaden PREDICATE_EVALUATION_ERROR nie jest akceptowany przez testcoverage.

```sh
cd /home/narolski/smad-next/src/NEXT/technical_metadata_v2
python3 -m unittest -v test_collector_v2.py test_predicates_v2.py
python3 test_scope_coverage_v2.py /home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/NEXT_TECHNICAL_COLLECTOR_V2_20261114/TYPED_SCOPE.json
```

Tar/release guards odziedziczone: same descriptor SHA beforetar, O_NOFOLLOW regularpath, reject traversal/aliases/duplicates/links/devices/sparse, fixedmembernames,8MiB/member256MiB/archive100000headersdepth64. Nie ma extractall ani NPZ/header parsing. Root release wiąże collectorSHA,predicatesSHA,packetSHA,exactoutput,reviewSHA,CPU-only i whole-logscope. Wymagany review line `GO_NEXT_TECHNICAL_V2_IMPLEMENTATION <collector_sha256>`. Source pins sprawdzane przed archiwami. Wynik create-only, atomicrename+fsync metadata/SHA/technical-completion marker; niekompletny katalog nie jest wynikiem ani retrypermission.

Propozycja komendy dopiero po independent review/clean source commit/rootrelease (nie wykonano):

```sh
CUDA_VISIBLE_DEVICES='' timeout 900s python3 /home/narolski/smad-next/src/NEXT/technical_metadata_v2/technical_collector_v2.py --packet /home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/NEXT_TECHNICAL_COLLECTOR_V2_20261114/TYPED_SCOPE.json --release /mnt/t7/smad_next/NEXT/technical_metadata_v2_ROOT_RELEASE.json --output /mnt/t7/smad_next/NEXT/technical_metadata_v2_collection_20261114
```

ROOT_RELEASE_PROPOSAL_NOT_AUTHORIZATION.json pozostaje HOLD. Root przed wykonaniem musi uzyskać niezależną recenzję dokładnego kodu/schema/output boundary, zaakceptować pozostałe UNKNOWN i wydać oddzielny technical-only release. Nie ma canonicalADMISSION/batch_closed/scientificjournal ani claimu.
