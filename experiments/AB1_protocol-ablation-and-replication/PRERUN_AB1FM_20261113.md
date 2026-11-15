# Pre-run check of the second-engine arm SbFM (13 Nov 2026, experiment-reviewer, Opus; saved by the owner)

Verdict GO WITH FIXES. Clean: all 404 added rows are training-host FaceMorpher images (R4fm and R2w4fm the 124
train_morph hosts, R2wfm the 156 train_genuine hosts; 0 person overlap with development/test, including R2w4 partners;
no added id in ab1x_eval; the 32 catalog-"train" R2w4/R4 rows with a non-training partner correctly dropped), byte-equal
512×512 PNGs, no closed set, no new image operation; FaceMorpher splices and the partner-side half rightly excluded;
R2w4fm is the right host-side twin; border-share pattern as OpenCV; 0.94× exposure acceptable when disclosed; reader
directions, pools and counting correct; job pins and 1:15 fine.
Findings: F1 (major) the loading-path test on real AB1 tars computes the H-fm2/H-fm3 baselines: commit first or discard
its output; F2 (major) the whole-manifest re-balance gave FaceMorpher rows attack share 0.594 (engine prior) and changed
Sb's repetition: keep train_Sb.csv's rows and append a self-balanced FaceMorpher block; F3 (major) README entry and
pins file missing; F4 (major) no ceiling rule for H-fm2/H-fm3 (Sb ≥ 0.98 untestable); F5 (minor) state that the
author's go overrides the strategist's Z3 gate and why seeds 408-412; F6 (minor) wording ("unseen landmark tool";
falsified wording); F7 (minor) noise disclosure, seed-mean print; F8 (minor) mock does not exercise H-fm2/H-fm3.
Owner's action: all applied before the registration commit (the scratch JSON of the loading-path test was deleted
unopened at 18:42; the manifest and overlay were rebuilt: train_SbFM 12312044…, overlay 681525d8…).
