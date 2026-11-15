# Sealed MAD22 read (FINAL_mad22): tables

Outcome (primary): **matched**

On corrected MAD22 (seen during development; genuine side the 204 FRLL photos), against genuine photos with aligned-frame history (our aligner plus history), the frozen network's mean EER over OpenCV, Webmorph, MIPGAN-I and MIPGAN-II (FaceMorpher is solvable without morphs and excluded) is within one point of the best released detector (SelfMAD (raw genuine photos)): difference -1.4 points [-3.5, 1.0] (non-inferiority margin +1.0 point).

## standard (native genuine)

| Family | ours seeds EER % | mean (SD) | best release | its EER % | diff [95%] | verdict | labels |
|---|---|---|---|---|---|---|---|
| FaceMorpher | 0.5, 1.5, 2.8, 3.9, 2.9 | 2.3 (1.3) | MADation ViT-B/16 | 0.0 | +2.3 [+0.9, +4.2] | lost | shortcut-saturated (a morph-free network reaches 0.0% EER on this cell, AD4): no state-of-the-art sentence |
| MIPGAN_I | 0.1, 0.4, 0.9, 1.0, 0.5 | 0.6 (0.4) | SelfMAD | 2.5 | -1.9 [-3.7, -0.3] | matched | not shown to be morph-specific: the network flags one-photo GAN renders |
| MIPGAN_II | 0.0, 0.0, 0.5, 0.5, 0.4 | 0.3 (0.3) | SelfMAD | 1.7 | -1.4 [-2.8, -0.2] | matched | not shown to be morph-specific: the network flags one-photo GAN renders |
| OpenCV | 2.9, 2.5, 3.0, 2.1, 0.8 | 2.3 (0.9) | SelfMAD | 1.0 | +1.3 [-0.6, +2.9] | comparable, not separated |  |
| Webmorph | 7.8, 16.2, 11.6, 12.3, 5.6 | 10.7 (4.1) | MADation ViT-B/16 | 11.0 | -0.3 [-6.7, +6.4] | comparable, not separated |  |
| mean4 | 2.7, 4.8, 4.0, 4.0, 1.8 | 3.5 (1.2) | SelfMAD | 4.7 | -1.3 [-3.4, +1.0] | comparable, not separated | not shown to be morph-specific: the network flags one-photo GAN renders |
| mean5 | 2.3, 4.1, 3.8, 4.0, 2.0 | 3.2 (1.0) | SelfMAD | 3.8 | -0.6 [-2.4, +1.4] | comparable, not separated | shortcut-saturated (a morph-free network reaches 0.0% EER on this cell, AD4): no state-of-the-art sentence; not shown to be morph-specific: the network flags one-photo GAN renders |
| mean2 | 5.4, 9.3, 7.3, 7.2, 3.2 | 6.5 (2.3) | SelfMAD | 7.4 | -0.9 [-4.6, +3.1] | comparable, not separated |  |

## history-matched: aligned-frame history (our aligner plus history)

| Family | ours seeds EER % | mean (SD) | best release | its EER % | diff [95%] | verdict | labels |
|---|---|---|---|---|---|---|---|
| FaceMorpher | 1.0, 2.5, 3.5, 7.8, 3.6 | 3.7 (2.6) | MADation ViT-B/16 (raw genuine photos) | 0.0 | +3.7 [+1.6, +6.1] | lost | shortcut-saturated (a morph-free network reaches 0.0% EER on this cell, AD4): no state-of-the-art sentence |
| MIPGAN_I | 0.1, 0.4, 0.9, 1.0, 0.5 | 0.6 (0.4) | SelfMAD (raw genuine photos) | 2.5 | -1.9 [-3.7, -0.3] | matched | not shown to be morph-specific: the network flags one-photo GAN renders; MIPGAN E7 pool = native genuine photos by construction |
| MIPGAN_II | 0.0, 0.0, 0.5, 0.5, 0.4 | 0.3 (0.3) | SelfMAD (raw genuine photos) | 1.7 | -1.4 [-2.8, -0.2] | matched | not shown to be morph-specific: the network flags one-photo GAN renders; MIPGAN E7 pool = native genuine photos by construction |
| OpenCV | 2.9, 2.5, 2.9, 2.1, 0.8 | 2.3 (0.9) | SelfMAD (raw genuine photos) | 1.0 | +1.2 [-0.5, +3.1] | comparable, not separated |  |
| Webmorph | 6.9, 15.6, 11.3, 13.0, 5.2 | 10.4 (4.3) | MADation ViT-B/16 (raw genuine photos) | 11.0 | -0.6 [-7.2, +6.2] | comparable, not separated |  |
| mean4 | 2.5, 4.6, 3.9, 4.2, 1.7 | 3.4 (1.2) | SelfMAD (raw genuine photos) | 4.7 | -1.4 [-3.5, +1.0] | matched | not shown to be morph-specific: the network flags one-photo GAN renders |
| mean5 | 2.2, 4.2, 3.8, 4.9, 2.1 | 3.4 (1.2) | SelfMAD (raw genuine photos) | 3.8 | -0.3 [-2.2, +1.6] | comparable, not separated | shortcut-saturated (a morph-free network reaches 0.0% EER on this cell, AD4): no state-of-the-art sentence; not shown to be morph-specific: the network flags one-photo GAN renders |
| mean2 | 4.9, 9.0, 7.1, 7.6, 3.0 | 6.3 (2.4) | SelfMAD (raw genuine photos) | 7.4 | -1.0 [-4.7, +3.0] | comparable, not separated |  |

## border-equalised standard

| Family | ours seeds EER % | mean (SD) | best release | its EER % | diff [95%] | verdict | labels |
|---|---|---|---|---|---|---|---|
| FaceMorpher | 4.2, 6.5, 2.9, 3.9, 4.4 | 4.4 (1.3) | MADation ViT-B/16 | 0.0 | +4.4 [+2.4, +6.5] | lost | shortcut-saturated (a morph-free network reaches 0.0% EER on this cell, AD4): no state-of-the-art sentence |
| MIPGAN_I | 0.5, 0.7, 1.5, 1.5, 0.6 | 0.9 (0.5) | MixFaceNet-MAD | 16.3 | -15.4 [-20.5, -11.1] | exceeded | not shown to be morph-specific: the network flags one-photo GAN renders |
| MIPGAN_II | 0.0, 0.3, 1.0, 0.9, 0.3 | 0.5 (0.4) | MADation ViT-L/14 | 16.3 | -15.8 [-20.2, -11.8] | exceeded | not shown to be morph-specific: the network flags one-photo GAN renders |
| OpenCV | 2.9, 2.5, 3.0, 2.1, 0.8 | 2.3 (0.9) | MADation ViT-B/16 | 4.0 | -1.7 [-5.1, +0.7] | comparable, not separated | no border in either class (mask empty): border-equalised = unblanked |
| Webmorph | 7.8, 16.2, 11.6, 12.3, 5.6 | 10.7 (4.1) | MADation ViT-B/16 | 11.0 | -0.3 [-6.7, +6.4] | comparable, not separated | no border in either class (mask empty): border-equalised = unblanked |
| mean4 | 2.8, 4.9, 4.3, 4.2, 1.8 | 3.6 (1.3) | MixFaceNet-MAD | 15.9 | -12.3 [-16.5, -8.2] | exceeded | not shown to be morph-specific: the network flags one-photo GAN renders |
| mean5 | 3.1, 5.2, 4.0, 4.1, 2.3 | 3.8 (1.1) | MixFaceNet-MAD | 13.7 | -9.9 [-13.7, -6.2] | exceeded | shortcut-saturated (a morph-free network reaches 0.0% EER on this cell, AD4): no state-of-the-art sentence; not shown to be morph-specific: the network flags one-photo GAN renders |
| mean2 | 5.4, 9.3, 7.3, 7.2, 3.2 | 6.5 (2.3) | MADation ViT-B/16 | 7.5 | -1.0 [-5.5, +3.1] | comparable, not separated |  |

## border-equalised history-matched

| Family | ours seeds EER % | mean (SD) | best release | its EER % | diff [95%] | verdict | labels |
|---|---|---|---|---|---|---|---|
| FaceMorpher | 4.8, 6.7, 2.0, 3.9, 4.9 | 4.5 (1.7) | MADation ViT-B/16 (raw genuine photos) | 0.0 | +4.5 [+2.4, +6.8] | lost | shortcut-saturated (a morph-free network reaches 0.0% EER on this cell, AD4): no state-of-the-art sentence |
| MIPGAN_I | 0.5, 0.7, 1.5, 1.5, 0.6 | 0.9 (0.5) | MixFaceNet-MAD (raw genuine photos) | 16.3 | -15.4 [-20.5, -11.1] | exceeded | not shown to be morph-specific: the network flags one-photo GAN renders; MIPGAN E7 pool = native genuine photos by construction |
| MIPGAN_II | 0.0, 0.3, 1.0, 0.9, 0.3 | 0.5 (0.4) | MADation ViT-L/14 | 14.9 | -14.4 [-18.7, -10.9] | exceeded | not shown to be morph-specific: the network flags one-photo GAN renders; MIPGAN E7 pool = native genuine photos by construction |
| OpenCV | 2.9, 2.5, 2.9, 2.1, 0.8 | 2.3 (0.9) | MADation ViT-B/16 (raw genuine photos) | 4.0 | -1.7 [-5.1, +0.7] | comparable, not separated | no border in either class (mask empty): border-equalised = unblanked |
| Webmorph | 6.9, 15.6, 11.3, 13.0, 5.2 | 10.4 (4.3) | MADation ViT-B/16 (raw genuine photos) | 11.0 | -0.6 [-7.2, +6.2] | comparable, not separated | no border in either class (mask empty): border-equalised = unblanked |
| mean4 | 2.6, 4.8, 4.2, 4.4, 1.7 | 3.5 (1.3) | MixFaceNet-MAD (raw genuine photos) | 15.9 | -12.4 [-16.6, -8.3] | exceeded | not shown to be morph-specific: the network flags one-photo GAN renders |
| mean5 | 3.0, 5.2, 3.7, 4.3, 2.4 | 3.7 (1.1) | MixFaceNet-MAD (raw genuine photos) | 13.7 | -10.0 [-13.6, -6.3] | exceeded | shortcut-saturated (a morph-free network reaches 0.0% EER on this cell, AD4): no state-of-the-art sentence; not shown to be morph-specific: the network flags one-photo GAN renders |
| mean2 | 4.9, 9.0, 7.1, 7.6, 3.0 | 6.3 (2.4) | MADation ViT-B/16 (raw genuine photos) | 7.5 | -1.2 [-5.6, +3.1] | comparable, not separated |  |
