# Exact future metadata-only command; NOT EXECUTED/AUTHORIZED

Accepted collector source:
 /home/narolski/smad-next/src/SPRINT5/paired_ranking_reader_v2/collect_metadata.py
Source manifest93b2ff226ee337fe3a486e0077be0a774a5229ce28ada45b46e41d6ed3ef42f4.
No new collector/reader/statistics implementation is supplied.

Before live collection: OTHER independent reviewer must verify all15 real arrival records/sidecars and this exactpacket/collector design. Root must commit this packet and the two contract files listed in PREFLIGHT.json, verify real tracked/clean status and all exact input/source pins. Then root writes a NEW exact release with decision GO_METADATA_COLLECTION_ONLY, binding519546..., reader manifest93b2..., exact archive roster digest, real independent_review_path/hash and nonself author/reviewer. The proposal decision/emptyreview is intentionally rejected by existing collector. Root controls exact command/output; do not repurpose scientific-read release.

CPU-generated packet tests:
 cd /home/narolski/smad-next/experiments/SPRINT5_20261114/paired_ranking/full15_metadata_packet_20261114
 /usr/bin/python3 -m unittest -v test_receipt_roster.py

Root-only AFTER independently reviewed exactrelease, fresh output namespace:
 cd /home/narolski/smad-next
 CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/SPRINT5/paired_ranking_reader_v2/collect_metadata.py --archive-roster experiments/SPRINT5_20261114/paired_ranking/full15_metadata_packet_20261114/ARCHIVE_ROSTER.json --release experiments/SPRINT5_20261114/paired_ranking/full15_metadata_packet_20261114/ROOT_METADATA_RELEASE.json --out /mnt/t7/smad_next/SPRINT5_1/metadata_collection_full15_v2_20261114_v1 > /mnt/t7/smad_next/SPRINT5_1/metadata_collection_full15_v2_20261114_v1.log 2>&1

Collector itself hashes all15opaque archive bodies BEFORE reading fixed metadata. It returns15envelopes/READER_ROSTER/COLLECTION_COMPLETE or COLLECTION_FAILED; NPZ/weight bodies are never decoded in this phase. Score hashes are copied from actual scorer metadata, not guessed now. Only subsequent OTHER review of actual metadata eligibility + root GO_READER_READ can permit admit-only/read and permanent claim.

No live collector,reader,admit-only,journal,scientificrelease or GPU/scheduler action has been executed by this packet author. No scientific command is supplied as currentauthorization. Existing once /mnt/t7/smad_next/SPRINT5_1/reader_once_v1 and output /mnt/t7/smad_next/SPRINT5_1/reader_output_v1/RESULT.json stay fixed; no alternatejournal,14-fitfallback or rerun.
