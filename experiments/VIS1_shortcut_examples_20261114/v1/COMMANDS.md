# VIS1 v1 exact commands — lead only after independent GO

Preparation already performed; do not rerun create-only prepare_vis1.py. Source: src/VIS1/v1. Use INVENTORY_v2.json (v1 preserved before canonical development-ID addendum).

Metadata-only, CPU/no model import:

    cd /home/narolski/smad-next
    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/VIS1/v1/score_vis1.py --inventory experiments/VIS1_shortcut_examples_20261114/v1/INVENTORY_v2.json --metadata-only

Root creates ROOT_RELEASE.json only after independentreview/sourcecommit. Required fields: decision=GO_VIS1_SCORE_ONLY; author and distinct reviewer; inventory_sha256 exact; independent_review_path and independent_review_sha256; models initially[selfmad_hrnet_w18]. A/B require an explicitly updated or separate reviewedrootrelease preservingoriginalreceipt. No suchGOfile supplied byauthor.

GPU smoke (oneGB10, fixed10min, no automatic retry):

    cd /home/narolski/smad-next
    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 timeout --signal=TERM --kill-after=30s 10m nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/VIS1/v1/score_vis1.py --inventory experiments/VIS1_shortcut_examples_20261114/v1/INVENTORY_v2.json --release experiments/VIS1_shortcut_examples_20261114/v1/ROOT_RELEASE.json --model selfmad_hrnet_w18 --out /mnt/t7/smad_next/VIS1/20261114/v1/selfmad_hrnet_w18

Lead records exactargv, nativeexit, start/end andstdout/stderr to a fresh durableexecutionreceipt. Do notpipe throughhead orotherwise maskreturncode. After technicalsmokePASS/timing, samecommand for fixedA thenB uses modelA/out.../A andmodelB/out.../B and exact separateROOT_CONTROL_RELEASE.json granting[A,B], not outcome-dependentcontrolselection. The existingSelfMAD result is retained, neverrescored. Root must perform duplicate/process/output/contention checks before eachstart. No shelllaunch, scheduler query, cancel orGPU call was made byauthor.

Timing-only review may parse RESULT.json's load_seconds,total_seconds and eachrow's seconds_two_forwards without choosing cases fromlogits. SuccessfulRESULT+SHA256.json andexit0 allrequired; timeout/partialoutputfail. ROOT checksT7>=50GiBreserve; outputs<1MiBJSON/model pluslogs, no sourcephotos orcheckpoints. Root'scompletepostresultreviewpacket includesoriginalinv/hash, originalfailureattempts andallmodeldispositions.
