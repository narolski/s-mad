# SPRINT5 execution receipt — 2026-11-14T14:48:58.183558+00:00

User request: execute the five additional experiment directions on clusters. Four reviewed GPU series are submitted to WCSS H100. Scheduler snapshot: all four PENDING (Priority); none is reported as a completed scientific experiment.

| Direction | Job | Fits | Seeds | State |
|---|---|---:|---|---|
| Paired S4/S3 ranking: BCE / paired BCE / paired ranking |6321090|15|501–505|PENDING Priority|
| Native matched-target vs self-target HN transfer |6321261|10|531–535|PENDING Priority|
| Camera-tail objective: BCE / mean / CVaR |6321244|15|521–525|PENDING Priority|
| Breadth vs more capture/orientation variants |6321194|10|511–515|PENDING Priority|
| LA1 identity/label admission |CPU2000v2|diagnostic only|fixed selection|Completed diagnostic; HQ training BLOCKED|

Every GPU series passed actual H100 technical smokes using lem-gpu-interactive. Full arrays use lem-gpu-short, one H100 per fit, maximum3 concurrent perarray; no duplicate jobs or paid rentals. Three short series are100-update pilots; ranking uses6250 updates. Tail/HN five-seed variation is conditional on one common Sb408 warmstart, not independent full retraining. Breadth comparison changes capture/orientation allocation along with identity count. Scientific readers remain closed pending independently reviewed exact-fit admission. Fresh413–417 confirmation and NEXT selection are untouched.

HN train-only nuisance floor was measured and independently checked: maximum within-D AUC0.7433476296522621, conditional fixed-learner CI[0.712510492865163,0.7959151230372816]. This allows only qualified geometry-transfer interpretation, not identity-specificity or shortcut-free claims.

LA1 existing labelled variable-resolution CelebA calibration completed2000 images in598.4seconds,1999 faces found,1998 complete-pair images;500 calibration and499 validation persons after one pair exclusion, no replacement. Independent audit reproduced clean flags160/998=16.03%; injected errors99/99 flagged, with unchanged-image flags241/899=26.81% and70singleton images. This does NOT establish a useful noise filter. Only one raw cross-person image pair reached cosine0.60; none reached0.70/0.77. Local HQ file-to-official-person mapping remains unverified; no HQ training or mining admission. Actual source dimensions66–147 by79–169, only19exact128square; former128px wording corrected before fullrun. Original CPU8 and failed preflightv1 evidence preserved.

Athena: no new submission; latest access/account check unresolved and failed login not retried. New reviewed H100 workloads remain on WCSS. CelebA-Spoof download remains41/74parts due explicit GoogleDrive quota; not used as complete dataset.

Sources: per-direction preregistrations, source SHA256SUMS, ROOT/Astra reviews and release JSON in this directory; WCSS Slurm records; COMPUTE_QUEUE.json; LA1 ASTRA_LOWRES_CPU2000_REVIEW.json. Source/release commits include8f1137d,b28b695,544391a,eb4da8e,51e72bc,de72be0,9b6c0d5. This receipt authorizes no scientific candidate score read.
