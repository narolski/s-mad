# Signal isolation by paired differences (PD1), GAN latent morphs: result

Owner run, 11 Nov 2026. Pre-registration: `prereg.md` (written 17:00 CET, before any number below).
Code `src/PD1/gan/`; large files `/mnt/t7/smad_next/PD1/gan/`.

## First small end-to-end pass (17:40 CET; CLIP pooled, set G, fold 0 of 5 held out)

Fold 0 = 13 of 64 blocks (52 hosts); heads trained on the other 51 blocks (204 hosts). Point estimates only,
no intervals (`first_pass_clip_pool_fold0.json`).

| Q1 step (held-out hosts) | share moving the expected way | AUC of the projection |
|---|---|---|
| pipeline: camera photo (x0) → one-photo reconstruction (x1) | 1.00 | 0.98 |
| same-person mixing: x1 → same-person mix (x2) | 0.79 | 0.67 |
| second identity: x2 → two-person morph (x3) | 0.63 | 0.65 |
| whole morph: x1 → x3 | 0.73 | 0.73 |
| camera photo → morph: x0 → x3 | 1.00 | 1.00 |

| Q3 head (trained on fold 1–4 hosts) | x3 vs x1 | x3 vs x0 | x3 vs x2 | x2 vs x1 | x1 vs x0 | hosts with s(x3) > s(x1) |
|---|---|---|---|---|---|---|
| one-person head (x2 vs x1 only) | 0.78 | 0.83 | 0.58 | 0.70 | 0.51 | 0.92 |
| two-person head (x3 vs x1) | 0.77 | 0.84 | 0.65 | 0.67 | 0.51 | 0.87 |

Not yet available at this point: floors, flag rates on softened photos, the spread-matched reference, intervals.
The full run follows below.
