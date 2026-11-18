# Current resource policy — supersedes rental recommendations below

Author ruling, 14 November: **No paid H100 capacity. H100-only work stays on WCSS; A100 work uses Athena as its primary resource.** The existing USD10 fallback remains bounded and may only fund cheaper compatible hardware when it materially accelerates an admissible result. Earlier H100 rental estimates are historical arithmetic, not active recommendations or funding requests. Preserve registered platform requirements; report/defer work that cannot meet its deadline rather than weaken gates. See COMPUTE_POLICY.json.

# Paid fallback readiness under the authorized USD10 cap

14 November 2026. The user explicitly authorized USD10 of additional Vast fallback spending. This supersedes the earlier generation-only restriction for ready fallback training/scoring inside that cap; no repeated budget approval is needed. It does not waive scientific platform/gate rules or authorize a larger spend. This audit made no SSH connection, rental, submission, archive opening or scoring call.

## Decision

**None of the three short scorers can be deployed as-is on the quoted offers.** The safest first target is the paired second-engine supplementary scorer (SbFM), after a reviewed relocation wrapper and verified compatible device/software. It has a two-hour compute envelope, exact per-network reproduction gates, explicit complete-family admission and durable partials. The user’s USD10 can plausibly cover one such bounded job including modest setup if a compatible offer is found; this is not yet a deployable or guaranteed-completion lease.

The cheap live offers are **not established platform matches**. The BB2 registration records the WCSS device as `NVIDIA H100`, 95,830 MiB. The quoted SXM and PCIe devices report 81,559 MiB. `src/BB2/precision_probe.py` uses exact equality with `NVIDIA H100`, not substring matching. The SbFM driver additionally requires `gate['device'] == 'NVIDIA H100'`. A marketing label “H100” cannot substitute for actual PyTorch device identity and variant compatibility. Do not edit the expected name, loosen the identity gate or substitute an A100 container to make an offer pass.

## Live quote evidence and what USD10 buys

Source: `VAST_FALLBACK_QUOTE.json`, 14 November 10:45:58 UTC / 11:45:58 CET. Credit reported USD10.5305118, no instances. The authorized spend remains USD10, not the entire credit balance. Offers are point-in-time quotes and must be revalidated immediately before purchase.

| Offer | Provider label | Quoted instance USD/h | USD10 / rate, ignoring additional charges | Three billed hours | Compatibility |
|---|---|---:|---:|---:|---|
| 56442968 | 1 × H100 SXM, 81,559 MiB | 2.344444 | 4.265 h | USD7.033 | Unverified; differs from recorded WCSS memory/device description |
| 56885480 | 1 × H100 PCIE, 81,559 MiB | 3.204805 | 3.120 h | USD9.614 | Unverified; little room for extras at three hours |

These costs apply the recorded `dph_total` rate; the quote does not separately expose all storage/transfer charges. They are not all-in procurement totals. A conservative cheap-offer scenario is at most three billed hours (one hour setup/transfers/gates plus two-hour registered scoring envelope), leaving USD2.967 for explicitly priced extras and uncertainty. Do not spend that reserve before charges and transfer measurements are known. Set both a hard time stop and an independent USD10 budget stop; failure to finish is preserved as partial, not admitted as success.

## Workload audit

| Work | Existing executable status | Scientific/technical blockers to rental | Recommendation |
|---|---|---|---|
| SbFM supplementary scorer, WCSS 6319579 | Reviewed driver `src/recovery_20261114/sbfm_supplement/run_supplement.py`; two-hour limit; ten pinned networks; complete TT1/MEDS/border outputs required | Registration explicitly specifies one WCSS H100 and `~/dmenv`; configuration has absolute WCSS paths; exact Python/torch/CUDA/timm/numpy/Pillow checks; exact GPU string and whole-manifest bit identity; output/source precedence currently assumes WCSS | First fallback candidate. Relocation-only addendum and independent review, unchanged scientific algorithm and checks. Freeze transport mapping and receipt format before any compute. |
| RZ1 comparator rescore, WCSS 6319491 | Reviewed `src/RZ1/run_rz1r_linkfix.sh`; `PN1_ROOT`, `PN1_PY`, `AB1_RESULTS`, `RZ1R_RESULTS` allow path wiring; original A408 already completed | RZ1 prereg says WCSS H100 only, fixed build; recovery is already first allowed infrastructure retry; second execution cannot silently become another retry; exact gate and original-output skip rules must survive relocation | Potential second option, but requires explicit reviewed disposition of platform and retry/source precedence. Do not erase A408 or race another retry. |
| DINOv3 wave-2, WCSS 6319264 | Reviewed `src/BB2/wcss/bb2l_w2.sbatch`; four-hour limit; DINO + five paired AB1 comparators; numerous packs/families | Hardcoded WCSS layout and Python; exact GPU probe; full DINO/AB1 fit-manifest gates; pinned environment; up to four compute hours already exhaust cheap-offer cap after setup/transfer; source precedence for alternate result missing | Poor first use of USD10. Keep queued; do not truncate models/families to fit cash or treat an incomplete wave as complete. |

A same-platform relocation changes infrastructure, not the scientific hypothesis, only if its independently reviewed addendum preserves all gates and source rules. Changing the actual device variant/software or retry policy is not an automatic infrastructure exception. On the present evidence, no candidate is approved to migrate without that review/addendum.

## Exact readiness actions for the recommended SbFM path

1. Establish actual WCSS device variant, PyTorch name, memory and complete runtime build from already allowed technical records. The recorded AB1 build includes Python 3.12.15, torch 2.11.0+cu128 and timm 1.0.30; the driver checks all six packages against each fit, so obtain exact numpy/Pillow and CUDA values rather than infer them. The existing A100 torch2.2.1 container is not a replacement.
2. Find a provider offer whose actual hardware meets the registered platform requirement. Verify the host’s exposed device name through provider evidence or a budgeted technical probe. A paid probe may fail; record its cost inside USD10. Do not run candidate scoring after a hardware mismatch.
3. Before lease, prepare exact environment installation artifacts or a relocatable build with hashes, tested syntactically/local metadata where possible. Do not assume copying a virtualenv preserves interpreter and shared-library compatibility.
4. Preserve unchanged driver/config/scorer bytes where possible by constructing an isolated local mirror of the pinned absolute WCSS paths on the rental host. Alternatively register a deterministic path-only mapping with new config hash and independent diff review; never change model/package hashes, family lists, row order, transforms, precision, batch64, thresholds or numerical gates. Add a unique rental run identifier; do not forge a Slurm job identity.
5. Inventory bytes and hashes for all ten network tars, FS1 pack, AB1 v2 overlay, SbFM v2 overlay, TT1 and MEDS packs, unchanged scorer/gate/probe sources, pre-read receipt and support JSON. The existing registration requires 200 GB local scratch and 64 GB RAM. Account for transfer and extraction before claiming the three-hour lease envelope; do not treat advertised internet bandwidth as measured end-to-end throughput. The relevant restricted-data handling scope must continue unchanged.
6. Fix duplicate/source precedence **before either output is inspected**. Prefer the original WCSS result if it starts before paid launch; abort paid launch then. If WCSS remains pending and a reviewed relocation is ready, lead records its status, executes the specifically authorized migration disposition, and binds the rental as the single designated attempt before scoring. Do not cancel or overwrite existing jobs/outputs merely on this audit’s recommendation. If both execute unexpectedly, preserve both; choose the prespecified source, never the better score. A second complete result requires the recorded technical disposition, not silent substitution.
7. Verify every input and source pin before extraction. Retain exact software checks, full 24,859/21,277-row bit-identity gates, existing eight-row TT1 plumbing check, and complete twenty-family validation. Do not substitute partial gate rows or tolerate score differences.
8. Configure durable partial transfer and final transfer/hash verification to the existing local durable store, while keeping the result namespace distinct from the original WCSS job. Extend admission receipts to identify provider instance/offer, start/end, platform, driver, software, exact code and hashes. Scheduler COMPLETED cannot be fabricated for a rental; reviewed equivalent process exit/completeness evidence is required.
9. Before launch, price storage/network extras and install a USD10 cap with time-based teardown early enough to recover outputs. Owner records teardown/provider receipt. Do not consume the entire nominal USD10/rate interval and leave no budget for final transfer.

## Quantifying additional needs for all fifteen 512 fits

The registered smoke projection is 4.39766 h per fit: fifteen fits = **65.9649 H100-hours**. Scheduler limits allow **90 H100-hours**. These are alternative compute estimates, not additive.

| Hypothetical rate | Compute-only projected cost | Compute-only all-limits cost | Additional above authorized USD10 |
|---|---:|---:|---:|
| Cheapest quoted SXM, USD2.344444/GPU-h | USD154.65 | USD211.00 | USD144.65–201.00, plus overhead |
| Quoted PCIe, USD3.204805/GPU-h | USD211.40 | USD288.43 | USD201.40–278.43, plus overhead |

These are arithmetic scenarios, **not ready procurement recommendations**: neither quoted variant is established as eligible, fifteen equivalent slots are not demonstrated available, runtime on them is not measured, and setup/transfer/storage charges are extra. At five parallel eligible GPUs, projected compute is about 13.2 h or 18 h at task limits; at fifteen, about 4.4 h or 6 h. User would need a separately quoted and authorized larger envelope if clusters cannot supply the balance. USD10 cannot fund the complete fifteen-fit batch. It should target a short decisive dependency rather than start a training batch that cannot finish.

## Sources inspected

`VAST_FALLBACK_QUOTE.json`; `SUPPLEMENTAL_RESCORE_20261114.md`; supplementary config/driver/launcher; `src/RZ1/run_rz1r_linkfix.sh` and launcher; RZ1 registration platform/retry and amendment1; `src/BB2/wcss/bb2l_w2.sbatch`, `precision_probe.py`, BB2 amendments7c/7d and platform records. Only text source/metadata was inspected. No candidate archives or scores were opened.
