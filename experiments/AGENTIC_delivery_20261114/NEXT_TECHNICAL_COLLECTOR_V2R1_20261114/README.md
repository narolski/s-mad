# NEXT technical collector v2r1 — narrow correction

**INDEPENDENT DELTA REVIEW REQUIRED; REAL EXECUTION HOLD.** Przeczytano finalny niezależny HOLD review v2 `9c93dd265add086db46f0c8a5d8e2ac424260ad4847de2efc00ea91b1fb1688c`; recenzent potwierdził brak innych blockerów w bounded review.

Zmiana ograniczona do native recipe RZ1 fit: TYPED_SCOPE zawiera teraz literalne sześć PINS bez trailing space oraz dokładne cztery fragmenty z read_selection.py572–576. Kontrole native wykonują tylko ten dokładny zestaw. Indywidualne unique-token checks pozostały jako strict_integrity_status; ich native_status=UNKNOWN z powodem INDIVIDUAL_TOKEN_INTEGRITY_ONLY. Sufiks poprawnego packSHA lub końcowego skip_tt1 0 nie powoduje już fałszywego native FAIL; strict integrity nadal może je odrzucić. Nie zmieniono canonical readera.

Nowy namespace `src/NEXT/technical_metadata_v2r1/`, evidence `NEXT_TECHNICAL_COLLECTOR_V2R1_20261114/`. Parser/pozostałe predykaty nie zostały poszerzone. Collector zmienia wyłącznie identyfikatory schema/release/review na v2r1. Dokładne77archive descriptors/member sets pozostają identyczne z v2; pięć SbMR512 metadata scopes i15BB2batchUNKNOWN bez zmian. UNKNOWN_PROOFS skopiowano byte-identical. DELTA.json wiąże rodzica i review.

30 testów jednostkowych PASS, w tym7 nowych differential testfamilies: wszystkie40RZfit × suffix/whitespace/tab/newline/order/adjacency variants; wszystkie30native-fit tokenrecipes; wszystkie5refit rawsubstr semantics; numeric Python equality vs literalBoolean; env/GPU/guard; native intcounter grammar; obie source lossconversion semantics. Reference fragment construction i token helper są izolowane z przypiętego sourceAST i wykonywane wyłącznie na syntetycznych stringach. Nie importowano ani nie wywołano canonical loaderów/readerów. Dodatkowo77×2=154synthetic canaryarchives PASS. To różnicowe sprawdzenie reprezentatywnych klas wejść, nie formalny dowód wszystkich możliwych danych.

```sh
cd /home/narolski/smad-next/src/NEXT/technical_metadata_v2r1
python3 -m unittest -v test_collector_v2.py test_predicates_v2.py test_source_equivalence_v2r1.py
python3 test_scope_coverage_v2.py /home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/NEXT_TECHNICAL_COLLECTOR_V2R1_20261114/TYPED_SCOPE.json
```

Przyszły osobny rootrelease musi mieć decision GO_NEXT_TECHNICAL_METADATA_V2R1_ONLY oraz niezależną linię review `GO_NEXT_TECHNICAL_V2R1_IMPLEMENTATION <collector_sha256>`, wiązać collector/predicates/scope/review/output/CPU i whole-log Boolean-only scope. Template pozostaje HOLD. Proponowana komenda po osobnym review,cleancommit,release — NIE WYKONANO:

```sh
CUDA_VISIBLE_DEVICES='' timeout 900s python3 /home/narolski/smad-next/src/NEXT/technical_metadata_v2r1/technical_collector_v2.py --packet /home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/NEXT_TECHNICAL_COLLECTOR_V2R1_20261114/TYPED_SCOPE.json --release /mnt/t7/smad_next/NEXT/technical_metadata_v2r1_ROOT_RELEASE.json --output /mnt/t7/smad_next/NEXT/technical_metadata_v2r1_collection_20261114
```

PRESERVATION_CHECK.json potwierdza hashe wszystkich frozen v1/v2 source/evidence entries i obu canonicalNEXT sources. Nie otwarto rzeczywistych headers/members/logs/NPZ/wag. Brak GPU/cluster/selection/admission/claim/commit. Wszystkie wcześniejsze scientific/policy/kernel/exposure UNKNOWN pozostają; przekazanie kończy bounded zadanie.
