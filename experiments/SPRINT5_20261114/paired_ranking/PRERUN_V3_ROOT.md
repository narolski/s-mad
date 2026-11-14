# Independent execution repair v3 — GO_SMOKE only

14 November 2026, reviewer root, author Sol. Exact source tar SHA d72016448cca83b4aaab63476e0fdefc0d38ed6e4fdc2a3897d5724dddc76f06; internalSUMS ef6bccb43d1c8936af8730957ee4da35c0a04fb97ff5ee373920523d63d73f6f.

Observed v2job6320908 FAILED4:0 in2:03 before battery reference scoring: all21277devimages missingfromchecksumlookup, zeroactualhashmismatches. The synthetic data root parent lacks packchecksumfiles. v3 changes battery devroot to real $W/pn1/data whose parentcontains the pinned FS1/AB1checksumfiles. Root inspected complete v2/v3source diff: no training/scoringrecipe, gate, data, seed or scientificcriterion change; newnamespace smoke_v3 ensures nooverwrite. Reviewed CPUactualrc2allfoursetverification receipt67748images and mergedrootresolver21277covered0missing, wrongroot0entries. This repairs the checksum lookup, does not disable it.

Same approved bounded three-arm2step seed501 smoke, oneH1008CPU64GiBRAM200GiBscratch2h actualPTY commonlock durablelogs/hasharchives. v1/v2failures retained. Production HOLD; no scientificscoresread or sharedbatteryrelease. Strictv2 bytechecker unchanged. Recomputeall3arms, no outcome-driven selection.
