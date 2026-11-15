# Registered step: battery-scoring of the 15 AB1 networks on WCSS H100 (BATTERY v1, comparators and node identity)

Written 13 Nov 2026 before any of these scores exists. Approved by the lead (13 Nov, message relaying the pre-run check
`experiments/reviews/PRERUN_BATTERY_RC1_20261113.md`, Improvement 2): "battery-scoring the 15 AB1 networks (A, B, Sb, seeds
408-412) on H100, about 2-3 GPU-hours, as same-platform TF32-on comparators and a node-identity test; write it as a
registered step with its own queue file, placed behind every experiment fit". Development data only.

## What runs

- Networks: the stored AB1 fits `AB1_{A,B,Sb}_s{408..412}` (WCSS H100, torch 2.11.0+cu128, `results/AB1/*.tar`, sha256
  of each tar checked against its `.sha256`). Nothing is trained.
- Job: `src/battery/wcss/battery_nets.sbatch` (array 0-14, one network per task), battery code tar
  `battery_code_v1rc2.tar` built by `git archive` from the release-candidate commit. Per task: platform record, gate on
  the H100 reference AB1_Sb_s408, inference-settings check against the reference, all four sets (dev 21,277, tt1 34,411,
  meds 1,018, gd 11,042 rows), unique training rows of the registered manifest, network check `--expect-eval` against the
  network's own fit-job `scores_eval.npz`, `--stats no`. Statistics are completed on the DGX with `--stats-only`.
- Queue: `/mnt/t7/smad_next/dispatch/submit_queue/wcss_battery_ab1cmp.cmd`, header "place behind every experiment fit".
- Cost: 15 tasks x 15-30 min, about 4-7 H100-hours of wall time including pack copies (scoring itself about 2-3 GPU-hours).

## What is read, and how (fixed now)

1. **Node identity (platform question, decides only how battery records are labelled).** Per task: the node, the gate
   class (byte-gated / tolerance-gated / failed, the node rule in `DESIGN.md` fixed 20:03 before any GPU gate was read),
   and the network check: number of the network's 21,277 dev rows whose battery logit differs from its own fit-job logit
   (byte identity required; at least 19,797 ids). Printed as a table node x network. Reading:
   - all 15 byte-gated and all 15 network checks byte-identical: "H100 nodes reproduce the fit-job scores byte for byte
     on N nodes" (N = distinct nodes seen);
   - any tolerance-gated or failed task: reported with its node; records of that node are labelled as the node rule says;
     no tolerance is changed after seeing these numbers.
2. **Comparators (statistics only).** The battery reader prints the 20 audit rows for A, B and Sb (seeds 408-412) from
   these 15 records: the same-platform, TF32-on, battery-scored comparators that new H100 arms are set beside. No verdict,
   no claim about any shortcut is made from this step: these networks' registered reads (AB1) stand; their TT1, MEDS and
   GD statistics on H100 are new numbers and are printed only. They are never pooled with the A100 TF32-off TT1/MEDS
   cells of the audit table (reader NOTE).
3. What would make the step void: a gate failure on every node, or any network check failing on a byte-gated node
   (that would mean the battery does not reproduce the fit-job scorer); then the battery is not released and the owner
   reports.

## What it cannot show

It does not test the A100 path, the DINOv3 loader, or the full-`last.pt` loading path (all 15 load `last_trainable.pt`);
the first new arm's fit job exercises `last.pt` with `--expect-eval`.
