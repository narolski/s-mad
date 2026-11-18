# SbMR512 v2 B(ii) — niezależna recenzja metodologii i źródeł

Recenzent: training_contribution/Sol, niezależny od autora tego pakietu Astra. **GO_PROSPECTIVE_METHOD_SOURCE_PLAN_ONLY. EXECUTABLE/GPU/ACTUAL_INPUT_ACCESS HOLD.** Ten werdykt pozwala rozważyć przyjęcie prospektywnego planu i dalszą implementację; nie jest code GO, dopuszczeniem rzeczywistych metadanych ani wynikiem kernel gate. Nie edytowano autora, własnego NEXTv2r1 ani canonical NEXT.

Zweryfikowane fingerprints: source manifest `88c63f27f829d15d52f0ba62d6ae7762a6b0f4986f9ac8b952d48504a330a4dc`; package manifest `3f19af962230acb0be2284eb916ac23c532bc863d6f60bb1548ef31ad1115367`; handoff `3978b3daeabc0d33b376376383bd9f634d32792e837820bf4a28e12a3980e680`. Wszystkie15 wpisów source/package oraz21 SOURCE_PINS zgadzają się. Root B(ii) i odwołanie do zachowanego v1 są przypięte. Odczyt ograniczony do źródeł, rejestracji, JSON metadanych i trzech CSV; żadnych archiwów/headers/members/logs/NPZ/checkpointów/obrazów/modeli/klastrów/GPU.

## Sprawdzone metadane i arytmetyka

Niezależnie zweryfikowano pełne59270 ordered context rows: eval24859 i TT134411, dokładnie ID/path/label w oryginalnych CSV. Każde z13771 target mappings poprawnie wskazuje population/index/batch=index//64/offset=index%64 i zgadza się z path/label cross oraz original-reference ID/member. Ponownie wyznaczone maski są identyczne:7257genuine,1000morph;5514pozostałych cross rows nie wchodzi doκ. Nie sprawdzano image bytes ani numericalreference.

**Istotny warunek implementacji:** tablica FULL_CONTEXT_BINDING.target_mapping NIE ma tej samej kolejności co INPUT_BINDING_PROPOSAL.cross_ids. Mapowanie jest kompletne i poprawne po ID; nie jest gotową kolejnością serializacji. Scorer musi użyć jawnego `cross_id→output_index` wyznaczonego z cross_ids, odrzucić duplicate/missing writes i porównać finalną kolejność. Nie dopisywać output w kolejności target_mapping/context traversal. Dodać fixture permutujący kolejność mapowania, przechodzący przez granice batch oraz porównujący finalny tensor14×13771 i ID listę. To warunek implementacji już opisanego remap, nie zmiana populacji/metody.

Source rz1_score.py73–113 potwierdza eval native potem flip w każdym batch, TT1 native only; native logit jest endpointem, TTAaverage nim nie jest. Przy batch64:389×2+538=1316calls/model/spec; eval kończy27,TT1 kończy43. Wszystkie14specs×5models dają **5,889,030image samples,92,120batched calls,963,970export values**. Counts obejmują pierwszy nativepass, nie obejmują startup/state reconstruction/gate administration. Nie są oszacowaniem czasu/memory/GPU budget.

## Testy i reguła naukowa

Niezależnie uruchomiono dokładną komendę autora przez `/home/narolski/mambamorph-code/.venv-spark/bin/python`, CUDA_VISIBLE_DEVICES puste, OPENBLAS/OMP=2: **7/7 PASS**. Systemowy python nie ma numpy; początkowy importfail był ograniczeniem środowiska, nie niepowodzeniem fixture. Właściwe środowisko autora zakończyło testy poprawnie.

Fixtures obejmują14unikatowych transformacji, deterministyczność/no transform RNG i nieidentyczność na wygenerowanej szachownicy, pełny schedule, NaN/±Inf/ujemne/Boolean/None, brak quantity i oppositefailedseeds. Reguła liczy osobno train≥4/5 i heldout≥4/5; nie wymaga tych samych4seedów. Missing/failed denominator5 pozostaje. Reguła max zmiany genuine/morph flagshare, osobne max9/max4 i threshold.05 są prospektywnie jawne. Heldout dotyczy nazw kernelów; skala300 mieści się w treningowymmixR256–400. To compoundshrink/enlarge robustness, nie izolowany efekt interpolacji ani wszystkie81par.

## Dlaczego to jeszcze nie runnable byte-equivalent producer

Plan poprawnie ujawnia różnice wobec całego historycznego jobu. Oryginalny scorer wykonuje train scoring między eval i TT1, potem MEDS; B(ii) ich nie autoryzuje. Model.eval/no_grad nie dowodzi braku mutablebuffers/caches/backendhistory. Oryginał wykonuje `l0.cpu().tolist()` przed flip i oblicza sigmoidaverage z transferem; selected-onlytransfer i „TTA expression if needed” pozostawiają jeszcze niedookreślony schedule synchronizacji. DataLoader inicjuje workers/RNG, a TF32true nie wiąże wszystkich backend defaults. Brak źródłowo kompletnego dowodu, że taki derivative już odtworzy strictbytes.

Przed code review trzeba zatem konkretnie ustalić i przetestować: identyczną rekonstrukcję frozenweights/buffers/LoRA/positionalinterpolation; forward mutations i state across populations/specs; deterministyczną politykę worker/RNG/backend; dokładne operacje i synchronizacje transient TTA oraz selected hosttransfer; zachowanie przy finalbatches i mapping. Nie wolno uzależniać tych wyborów od późniejszych κwyników. Exact native targetbytegate musi zakończyć się przed pierwszą perturbacją, a mismatch oznacza terminal HOLD/failure bez A, dodatkowych populations, tolerancji lub adaptive rebuild. Gate jest testem końcowym, nie obecnym dowodem przenośności.

Rzeczywiste runtime/source/pretrained/state/checkpoint/image fields pozostają UNKNOWN. `last_pt.sha256` i info.last_pt_sha256 odnoszą się do pełnego historycznego last.pt, nie automatycznie do last_trainable.pt. Required technical proposal to osobny future scope: ewentualne opaque member hashing wymaga osobnego release, nawet bez decode; nie wynika z tej recenzji. Info.train_acc_rule0 i scientificsiblings pozostają wykluczone. Reference NPZ field/target selection boundary musi być jawnie zrecenzowana przed oryginalnymi array reads.

## Najbliższe kroki

1. Root może przyjąć dokładny prospektywny B(ii)packet z powyższym remap wymaganiem; nadal osobne exposure attestation.
2. Zamknąć dopuszczone actual technical evidence oraz pretrained/checkpoint/image/runtime pins; nie imputować ich ze source expectations.
3. Zaimplementować nowy producer+adapter z ustalonym state/transfer schedule, output canaries, mapping fixtures, strictgate-before-perturbation, failure retention i create-only durable receipt. Następnie niezależna recenzja dokładnego kodu.
4. Osobno przypiąć real resource budget i wydać root release obejmujący pełny kontekst/flip computations, checkpointy i targetreference access. Żadnej komendy GPU nie zatwierdzono teraz.

Maszynowe sprawdzenia: INDEPENDENT_SOURCE_CHECKS_20261114.json w tym folderze. Sbc/GX/finalNEXT/freshconfirmation nie są rozstrzygane przez ten review. Kończę bounded zadanie.
