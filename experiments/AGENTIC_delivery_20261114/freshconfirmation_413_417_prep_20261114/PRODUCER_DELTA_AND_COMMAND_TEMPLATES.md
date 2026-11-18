# Concrete prospective producer changes (not executable releases)

New source root proposed: src/NEXT/fresh_confirmation_v1/. Never modify current selection producers or sources in place.

| New file | Pinned parent | Permitted proposed structural changes |
|---|---|---|
| run_ab1_fresh.sh | src/AB1/run.sh | Narrow arm list to A/Sb as registered; guard only 413–417; new NEXTCONF task/result root; scientific flags unchanged. |
| run_ab1fm_fresh.sh | src/AB1/run_fm.sh | SbFM only; guard413–417; new task/result root; pack/overlay/manifest/scorer unchanged. |
| run_rz1_fresh.sh | src/RZ1/run_rz1.sh | Only registered chosen role arms; guard413–417; new task/result root; all guards/transforms/scoring preserved. Fresh SbMR512 kernel adapter uses existing owner/review chain. |
| run_bb2l_fresh.sh | src/BB2/run_lr.sh | A/B/Sb at413–417; new result root; actual256/1 batch binding retained; fixed1.17e-5 LoRA/3.33e-5 head unchanged. |
| task_map.json | TASK_TEMPLATES.json chosen branch | Exactly registered fresh cohort only; source/hash/role and per-seed identity frozen. |
| fresh_native_adapters.py | src/NEXT/native_adapters.py | Separate source identities for registered fresh origin/task names; no selection identity relaxation. |
| read_confirmation.py | src/NEXT/read_selection.py | Registered fresh seed map, DINO five-fresh-comparator loop, unchanged statistical code/rules, fixed confirmation journal; independent diff review required. |
| runner.sh + dispatch.sbatch | relevant original wcss/*.sbatch | Exact selected map, producer/input pins, actual runtime identity, root-approved walltime/resources and durable failure retention; no full8-branch array. |

GX has no authorized producer parent. Its proposed files/recipe/manifest/task map stay HOLD rather than inheriting any row above.

The training invocation represented in BRANCHES.json is the parent scientific command (a source template only):

    <pinned-python> <original-train-entry> [<pinned-pack-code-for-RZ1>] --arch <registered-arch> --regime d0 --split train90 --lofo none --lr <registered-lr> --seed <413..417> --res <registered-res> --workers 7 --out <fresh-local-run> --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps=6250 --ft=lora --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw --wd=0.05 --head-lr=3.33e-05 --bs=<registered-batch> [--accum=<registered-accum-for-RZ1>] --aug=flip --sched=const --clip-grad=5 --pos-weight=1

Do not add --accum to a parent that does not pass it. DINO receives its existing source-controlled batch/accum recipe/environment, not an assumed new flag. The scientific training source is the original packed train.py (cbb2cbd1b9a3eb59ab080a540a98aab0f6ead51ea69364d2debe06a984b8c1c5); source-only acquisition receipt is already recorded in NOTEBOOK. Do not open a new candidate archive to find it.

A new runner's intended invocation shape is TASK_DIR=<fresh-task-dir> TASK_WORK=$TMPDIR/<fresh-work> PN1_ROOT=<WCSS-root> PN1_PY=<admitted-interpreter> <selected-result-env>=<new-durable-WCSS-root> bash <new-pinned-producer>. Input overrides and all inherited test knobs must be sanitized: production steps6250, limit0, original workers7, no RZ1_SKIP_TT1, no truncated scoring/test settings, no warmstart.

The actual literal commands stay null until source files exist, all input/runtime pins and reviews are real, and the winner is admitted. No placeholder is executable authority.

Expected durable per-task filenames follow parent scorer schema: task.env, meta.json, last_trainable.pt, last_pt.sha256 where source-persisted, train.log, env.txt, gpu.txt, task_info.txt, native evaluation/training/support score outputs; RZ1 adds guard.log/rz1_transform.json and registered TT1/MEDS/cross output. Exact member roster/counts must be fixed from producer source before launch, never inferred by opening candidates during preparation. A/B own-registration controls and the source-specific supplement have their separate rosters. Record every seed, failure status and missing required member; no fabricated success.

Post-result independent acceptance must check scientific original-rule confirmation; one static package PASS cannot establish source/recipe admission, result validity or final protocol choice.
