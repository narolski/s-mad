# Experiments: plain names and IDs

Rule (author, 11 Nov 2026): an experiment is always named by a plain description with its ID in brackets, for example "the MorDIFF ladder re-read (AD1)". A bare ID is never used in a report, a table heading or a message. New experiment folders are named `<ID>_<short-name>`; folders created before this rule keep their name until their owner has finished and are then renamed.

| ID | Plain name | Family |
|---|---|---|
| AR1 | Landmark ladder | audit, landmark |
| AR2 | Landmark dose curve | audit, landmark |
| AR3 | Single-cue baselines | audit, landmark |
| AR4 | Face-blanked and background-blanked scoring | audit, landmark |
| AR5 | Border-matched history control | audit, landmark |
| AR7 | Look-alike bins | audit, landmark |
| AD1 | MorDIFF ladder re-read | audit, diffusion |
| AD1b | Identical and mirrored inputs for diffusion | audit, diffusion |
| AD2 | DiM ladder | audit, diffusion |
| AD3 | History control on a second photo pool | audit, diffusion |
| AD4 | Morph-free networks | audit, diffusion |
| AD5 | Retrains of released methods | audit, diffusion |
| AG1 | MIPGAN one-person controls | audit, GAN |
| AG2 | GAN-reconstructed genuine photos | audit, GAN |
| AG3 | GAN dose curve | audit, GAN |
| AG4 | Morph-free GAN network | audit, GAN |
| AG5 | StyleGAN3 ladder re-read | audit, GAN |
| C1 | Cue check: expression balance | cue checks |
| C2 | Cue check: person overlap | cue checks |
| C3 | Cue check: colour statistics | cue checks |
| C4 | Cue check: chroma subsampling | cue checks |
| C1b | Expression cue use | cue checks |
| AF0 | Alpha-field probe | method |
| ID1 | Ideation round 1 | ideation |
| FZ1 | Frozen features read mixing | method |
| T0 | First twin-trained heads | method |
| T2 | Last-layer refit of released detectors | method |
| T3 | Typicality detector | method |
| T4 | Twin-trained detector matrix | method |
| T5 | Two-contributor embedding head | method |
| T6 | Mixing-fraction regression | method |
| X0 | Derived data-extension numbers | data extension |
| X1 | Re-score of the 60 existing fits | data extension |
| X2 | Matched vs unmatched added data | data extension |
| X3 | Pipeline-count ablation | data extension |
| X4 | History control on FFHQ photos | data extension |
| X5 | Landmark twins from an unseen source | data extension |
| D1 | Pair lists | data builds |
| D2 | Landmark image build | data builds |
| D3 | GAN twin build | data builds |
| D4 | Diffusion twin build | data builds |
| F1 | Feature cache | data builds |
| EV1 | Fixed-threshold re-read of existing scores | evaluation |
| SM1 | SMDD five-partner audit and rebuild | audit, training set |
| ID0 | Identity-shrinkage triage | method, identity |
| ID2 | Ideation round 2, vetting | ideation |
| RS1 | Own-crop re-score of the audit rows | audit, released detectors |
| C1c | What the smiling half carries: expression or capture detail | cue checks |
| AD1b | Identical and mirrored inputs for diffusion | audit, diffusion |
| CN0 | Clean-negative test (inside the alpha-field probe) | method |

Rungs of the ladder, in words: camera photo (R0); the same photo with the morphs' shrink-and-enlarge history (R1, also called E7); the tool run on one photo (R2; for landmark tools this is the photo itself); warp-only image (R2w); mirror self-morph (R3m); same-person morph (R3); two-person morph (R4).

Live state of each experiment: `NOTEBOOK.md`. Experiments before 11 Nov: `prior/INDEX.md`.
