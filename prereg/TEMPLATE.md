# <ID> <short name>

- **Hypothesis (plain words):**
- **Data:** train / validation / test sets, pair counts, held-out pipeline
- **Model and recipe:** backbone, head, loss, steps, seeds 401–405, checkpoint rule (last)
- **Primary metric:** held-out twin AUC with 95% bootstrap interval over identities
- **Falsifier (fixed before the run):**
- **Guards:** thumbnail baseline, history probe, pose-gap baseline, identity-disjoint check
- **Stop rule and budget:** GPU-hours, wall time
- **Command (tested on 8 images):**
- **Pre-run review:** date, verdict
- **Result:** numbers, verdict, results-review date
