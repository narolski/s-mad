# AG1 drafts, not registered, not run (lead decides after the author has seen the review)

## H-new-3: a render-only pass is platform-neutral (about 0.2 GPU-h on the DGX)

- Question: R2s renders (and the AG3 / AG3T doses) were made on the rented A100 from latents made on Athena. Does a
  render-only pass depend on the platform?
- Data: about 20 Athena hosts of the primary pool. Their stored Athena latents exist only inside the Athena result tars
  (second verified copy at `/net/pr2/projects/plgrid/plggrestoration/smad-next/backup/AG1_originals/`): stream the
  `lat/mip1_R2_<host>__s1.npz` and the inversion latents out of the tars (as for `needs_lat.tar`), compute w_s with
  `ag1_spread.py`'s rule on the DGX GB10, align with `prep_eval.align`, compare with the stored rented R2s frames.
- Prediction: mean |pixel difference| of the 512 frames < 1 grey level; detector AUC of rerender vs stored frame within
  [0.45, 0.55] for the three primary release rows (paired by host; dyadic bootstrap).
- Falsifier: mean difference >= 1 grey level, or any primary row's AUC outside [0.40, 0.60].
- Caveat: the DGX is a third platform (GB10, torch 2.12 + cu130); a pass shows render-only output is insensitive to the
  platform at the frame level, not that the rented and Athena renders are identical.

## H-new-4: a deliberately look-alike second identity shrinks the identity step (about 3 A100-h)

- Question: the second-identity step (R3 vs R4) was 0.65 to 0.72 with partners chosen by a within-gender cycle cover
  (contributor w600k cosine 0.16 to 0.17). Is the step smaller when the second person looks like the host?
- Data: the 200 primary hosts; new partner = the host's top-1 impostor by w600k cosine among same-gender persons of the
  same database (not the cycle partner), photo from the other session. New rung R4la = MIPGAN(s1(p), s2(top-1)),
  generated on one platform (registration names it) with the vendored code unchanged; reuses the stored inversion
  latents where the platform matches, otherwise inverts again.
- Prediction: R3 vs R4la AUC moves toward 0.5, and R4la vs R4 favours R4 (higher score for less look-alike partners).
- Falsifier: R3 vs R4la within 0.03 of the R3 vs R4 value of the same release row (0.66 / 0.72 / 0.65).
- Guards: G-b on R4la (it must still verify both contributors at FMR 1e-3; look-alike pairs make this easier), the same
  baselines and stratified AUCs, platform label.
- Cost: 200 morphs + up to 200 inversions: about 3 A100-h (about 1.5 USD rented). Needs registration and the lead's go.
