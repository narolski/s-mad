
#### Ladder A: R0 -> R2 -> R3 -> R4 (main contrast R2 vs R4)

| Detector | Pool / tool | R0->R2 AUC [CI] (share) | R2->R3 AUC [CI] (share) | R3->R4 AUC [CI] (share) | R2 vs R4 AUC [CI] (share) | R0 vs R4 | main verdict | side R3 vs R4 | side R2 vs R3 |
|---|---|---|---|---|---|---|---|---|---|
| SelfMAD | frgcferet/opencv | 0.500 [0.50, 0.50] (0.00) | 0.964 [0.95, 0.97] (0.82) | 0.689 [0.65, 0.73] (0.23) | 0.986 [0.98, 0.99] (1.00) | 0.986 [0.98, 0.99] | reads morphing | mixed | identity reading |
| SelfMAD | frgcferet/facemorpher | 0.503 [0.49, 0.51] (0.00) | 0.976 [0.97, 0.98] (0.82) | 0.663 [0.63, 0.70] (0.17) | 0.991 [0.99, 1.00] (0.98) | 0.992 [0.99, 1.00] | reads morphing | mixed | identity reading |
| SelfMAD | frll/opencv | 0.500 [0.50, 0.50] (0.00) | 1.000 [1.00, 1.00] (1.00) | 0.604 [0.50, 0.70] (0.10) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| SelfMAD | frll/facemorpher | 0.530 [0.51, 0.56] (0.03) | 1.000 [1.00, 1.00] (1.00) | 0.573 [0.47, 0.67] (0.07) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-B/16 | frgcferet/opencv | 0.500 [0.50, 0.50] (0.00) | 0.962 [0.95, 0.97] (0.77) | 0.695 [0.65, 0.73] (0.22) | 0.990 [0.98, 0.99] (1.00) | 0.990 [0.98, 0.99] | reads morphing | mixed | identity reading |
| MADation ViT-B/16 | frgcferet/facemorpher | 0.503 [0.50, 0.51] (0.00) | 0.953 [0.94, 0.96] (0.75) | 0.672 [0.63, 0.71] (0.20) | 0.987 [0.98, 0.99] (1.00) | 0.987 [0.98, 0.99] | reads morphing | mixed | identity reading |
| MADation ViT-B/16 | frll/opencv | 0.500 [0.50, 0.50] (0.00) | 0.976 [0.96, 0.99] (0.77) | 0.877 [0.80, 0.94] (0.45) | 0.999 [0.99, 1.00] (1.00) | 0.999 [0.99, 1.00] | not applied | not applied | not applied |
| MADation ViT-B/16 | frll/facemorpher | 0.529 [0.51, 0.55] (0.03) | 0.968 [0.95, 0.99] (0.72) | 0.828 [0.74, 0.90] (0.37) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-L/14 | frgcferet/opencv | 0.501 [0.50, 0.50] (0.00) | 0.881 [0.86, 0.90] (0.50) | 0.749 [0.71, 0.79] (0.28) | 0.991 [0.98, 1.00] (1.00) | 0.991 [0.98, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frgcferet/facemorpher | 0.488 [0.48, 0.49] (-0.01) | 0.922 [0.90, 0.94] (0.57) | 0.737 [0.70, 0.77] (0.26) | 0.993 [0.98, 1.00] (1.00) | 0.993 [0.98, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frll/opencv | 0.499 [0.50, 0.50] (-0.00) | 0.805 [0.74, 0.87] (0.33) | 0.941 [0.90, 0.98] (0.61) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-L/14 | frll/facemorpher | 0.479 [0.46, 0.49] (-0.02) | 0.869 [0.81, 0.92] (0.44) | 0.887 [0.82, 0.94] (0.47) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| MixFaceNet-MAD | frgcferet/opencv | 0.499 [0.50, 0.50] (-0.00) | 0.867 [0.85, 0.88] (0.76) | 0.619 [0.58, 0.65] (0.21) | 0.928 [0.91, 0.95] (1.00) | 0.928 [0.91, 0.95] | reads morphing | mixed | identity reading |
| MixFaceNet-MAD | frgcferet/facemorpher | 0.503 [0.50, 0.51] (0.01) | 0.857 [0.84, 0.87] (0.78) | 0.598 [0.56, 0.63] (0.18) | 0.912 [0.89, 0.93] (0.99) | 0.914 [0.89, 0.93] | reads morphing | no identity reading | identity reading |
| MixFaceNet-MAD | frll/opencv | 0.498 [0.49, 0.50] (-0.00) | 0.900 [0.87, 0.93] (0.60) | 0.794 [0.69, 0.88] (0.39) | 0.983 [0.96, 1.00] (1.00) | 0.983 [0.96, 1.00] | not applied | not applied | not applied |
| MixFaceNet-MAD | frll/facemorpher | 0.505 [0.48, 0.53] (0.01) | 0.885 [0.85, 0.92] (0.61) | 0.728 [0.62, 0.82] (0.31) | 0.976 [0.95, 0.99] (1.01) | 0.975 [0.94, 1.00] | not applied | not applied | not applied |
| M3 s1 | frgcferet/opencv | 0.500 [0.50, 0.50] (0.00) | 0.975 [0.97, 0.98] (0.76) | 0.765 [0.73, 0.80] (0.28) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s1 | frgcferet/facemorpher | 0.513 [0.51, 0.52] (0.01) | 0.973 [0.97, 0.98] (0.75) | 0.757 [0.73, 0.79] (0.27) | 0.998 [1.00, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s1 | frll/opencv | 0.500 [0.50, 0.50] (0.00) | 0.943 [0.91, 0.97] (0.61) | 0.946 [0.90, 0.98] (0.62) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s1 | frll/facemorpher | 0.527 [0.52, 0.54] (0.03) | 0.932 [0.90, 0.96] (0.58) | 0.905 [0.84, 0.96] (0.51) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s2 | frgcferet/opencv | 0.500 [0.50, 0.50] (0.00) | 0.996 [0.99, 1.00] (1.00) | 0.781 [0.75, 0.81] (0.30) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s2 | frgcferet/facemorpher | 0.513 [0.51, 0.51] (0.01) | 0.996 [0.99, 1.00] (1.00) | 0.783 [0.75, 0.81] (0.30) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s2 | frll/opencv | 0.500 [0.50, 0.50] (0.00) | 0.986 [0.97, 1.00] (0.85) | 0.926 [0.87, 0.97] (0.56) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s2 | frll/facemorpher | 0.527 [0.52, 0.54] (0.03) | 0.985 [0.97, 1.00] (0.85) | 0.899 [0.83, 0.95] (0.50) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s3 | frgcferet/opencv | 0.500 [0.50, 0.50] (0.00) | 0.997 [0.99, 1.00] (1.00) | 0.772 [0.74, 0.80] (0.29) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s3 | frgcferet/facemorpher | 0.510 [0.51, 0.51] (0.01) | 0.996 [0.99, 1.00] (1.00) | 0.770 [0.74, 0.80] (0.29) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s3 | frll/opencv | 0.500 [0.50, 0.50] (0.00) | 0.982 [0.96, 1.00] (0.82) | 0.933 [0.89, 0.97] (0.58) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s3 | frll/facemorpher | 0.517 [0.51, 0.53] (0.02) | 0.984 [0.97, 1.00] (0.84) | 0.881 [0.82, 0.93] (0.46) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s4 | frgcferet/opencv | 0.500 [0.50, 0.50] (0.00) | 0.987 [0.98, 0.99] (0.86) | 0.758 [0.72, 0.79] (0.27) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s4 | frgcferet/facemorpher | 0.520 [0.52, 0.52] (0.02) | 0.984 [0.98, 0.99] (0.83) | 0.758 [0.72, 0.79] (0.27) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s4 | frll/opencv | 0.500 [0.50, 0.50] (0.00) | 0.975 [0.96, 0.99] (0.76) | 0.899 [0.84, 0.95] (0.49) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s4 | frll/facemorpher | 0.531 [0.52, 0.55] (0.03) | 0.975 [0.96, 0.99] (0.76) | 0.869 [0.79, 0.93] (0.44) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s5 | frgcferet/opencv | 0.500 [0.50, 0.50] (0.00) | 0.948 [0.94, 0.96] (0.63) | 0.767 [0.73, 0.80] (0.28) | 0.995 [0.99, 1.00] (1.00) | 0.995 [0.99, 1.00] | reads morphing | identity reading | identity reading |
| M3 s5 | frgcferet/facemorpher | 0.513 [0.51, 0.52] (0.01) | 0.949 [0.94, 0.96] (0.64) | 0.779 [0.75, 0.81] (0.30) | 0.996 [0.99, 1.00] (1.00) | 0.996 [0.99, 1.00] | reads morphing | identity reading | identity reading |
| M3 s5 | frll/opencv | 0.500 [0.50, 0.50] (0.00) | 0.915 [0.87, 0.95] (0.53) | 0.935 [0.88, 0.97] (0.59) | 0.996 [0.98, 1.00] (1.00) | 0.996 [0.98, 1.00] | not applied | not applied | not applied |
| M3 s5 | frll/facemorpher | 0.535 [0.52, 0.55] (0.03) | 0.916 [0.87, 0.95] (0.54) | 0.907 [0.84, 0.96] (0.51) | 0.999 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s6 | frgcferet/opencv | 0.500 [0.50, 0.50] (0.00) | 0.986 [0.98, 0.99] (0.86) | 0.777 [0.74, 0.81] (0.30) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s6 | frgcferet/facemorpher | 0.515 [0.51, 0.52] (0.01) | 0.986 [0.98, 0.99] (0.85) | 0.781 [0.75, 0.82] (0.30) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s6 | frll/opencv | 0.500 [0.50, 0.50] (0.00) | 0.920 [0.89, 0.95] (0.55) | 0.925 [0.87, 0.97] (0.56) | 0.998 [0.99, 1.00] (1.00) | 0.998 [0.99, 1.00] | not applied | not applied | not applied |
| M3 s6 | frll/facemorpher | 0.532 [0.52, 0.55] (0.03) | 0.916 [0.88, 0.95] (0.53) | 0.891 [0.82, 0.95] (0.48) | 0.997 [0.99, 1.00] (1.00) | 0.997 [0.99, 1.00] | not applied | not applied | not applied |
| M3 s7 | frgcferet/opencv | 0.500 [0.50, 0.50] (0.00) | 0.991 [0.99, 1.00] (0.92) | 0.765 [0.73, 0.80] (0.28) | 0.998 [1.00, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s7 | frgcferet/facemorpher | 0.513 [0.51, 0.52] (0.01) | 0.989 [0.98, 0.99] (0.89) | 0.763 [0.73, 0.80] (0.28) | 0.998 [1.00, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s7 | frll/opencv | 0.500 [0.50, 0.50] (0.00) | 0.982 [0.96, 1.00] (0.81) | 0.916 [0.86, 0.96] (0.54) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s7 | frll/facemorpher | 0.523 [0.51, 0.54] (0.02) | 0.979 [0.96, 1.00] (0.79) | 0.881 [0.81, 0.94] (0.46) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s8 | frgcferet/opencv | 0.500 [0.50, 0.50] (0.00) | 0.988 [0.98, 0.99] (0.88) | 0.768 [0.73, 0.80] (0.28) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s8 | frgcferet/facemorpher | 0.507 [0.50, 0.51] (0.01) | 0.988 [0.98, 0.99] (0.87) | 0.773 [0.74, 0.80] (0.29) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s8 | frll/opencv | 0.500 [0.50, 0.50] (0.00) | 0.960 [0.94, 0.98] (0.68) | 0.908 [0.85, 0.95] (0.52) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s8 | frll/facemorpher | 0.532 [0.53, 0.55] (0.03) | 0.956 [0.93, 0.98] (0.66) | 0.875 [0.80, 0.93] (0.45) | 0.999 [0.99, 1.00] (1.00) | 0.999 [0.99, 1.00] | not applied | not applied | not applied |

#### Ladder B: R0 -> R2w -> R3 -> R4 (main contrast R2w vs R4)

| Detector | Pool / tool | R0->R2w AUC [CI] (share) | R2w->R3 AUC [CI] (share) | R3->R4 AUC [CI] (share) | R2w vs R4 AUC [CI] (share) | R0 vs R4 | main verdict | side R3 vs R4 | side R2w vs R3 |
|---|---|---|---|---|---|---|---|---|---|
| SelfMAD | frgcferet/opencv | 0.710 [0.69, 0.73] (0.25) | 0.922 [0.91, 0.94] (0.65) | 0.689 [0.65, 0.73] (0.23) | 0.966 [0.95, 0.98] (0.84) | 0.986 [0.98, 0.99] | mixed | mixed | identity reading |
| SelfMAD | frgcferet/facemorpher | 0.650 [0.64, 0.66] (0.16) | 0.959 [0.95, 0.97] (0.72) | 0.663 [0.63, 0.70] (0.17) | 0.984 [0.98, 0.99] (0.88) | 0.992 [0.99, 1.00] | reads morphing | mixed | identity reading |
| SelfMAD | frll/opencv | 0.904 [0.88, 0.93] (0.51) | 0.996 [0.99, 1.00] (1.00) | 0.604 [0.50, 0.70] (0.10) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| SelfMAD | frll/facemorpher | 0.811 [0.77, 0.85] (0.34) | 0.999 [1.00, 1.00] (1.00) | 0.573 [0.47, 0.67] (0.07) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-B/16 | frgcferet/opencv | 0.566 [0.55, 0.58] (0.07) | 0.948 [0.94, 0.96] (0.70) | 0.695 [0.65, 0.73] (0.22) | 0.986 [0.98, 0.99] (0.94) | 0.990 [0.98, 0.99] | reads morphing | mixed | identity reading |
| MADation ViT-B/16 | frgcferet/facemorpher | 0.511 [0.50, 0.52] (0.01) | 0.948 [0.94, 0.96] (0.73) | 0.672 [0.63, 0.71] (0.20) | 0.984 [0.97, 0.99] (0.97) | 0.987 [0.98, 0.99] | reads morphing | mixed | identity reading |
| MADation ViT-B/16 | frll/opencv | 0.665 [0.63, 0.71] (0.17) | 0.944 [0.92, 0.97] (0.62) | 0.877 [0.80, 0.94] (0.45) | 0.997 [0.98, 1.00] (1.00) | 0.999 [0.99, 1.00] | not applied | not applied | not applied |
| MADation ViT-B/16 | frll/facemorpher | 0.583 [0.55, 0.62] (0.08) | 0.957 [0.93, 0.98] (0.66) | 0.828 [0.74, 0.90] (0.37) | 0.999 [0.99, 1.00] (1.00) | 0.999 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-L/14 | frgcferet/opencv | 0.427 [0.41, 0.44] (-0.08) | 0.896 [0.88, 0.91] (0.53) | 0.749 [0.71, 0.79] (0.28) | 0.992 [0.98, 1.00] (1.01) | 0.991 [0.98, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frgcferet/facemorpher | 0.463 [0.45, 0.48] (-0.04) | 0.926 [0.91, 0.94] (0.58) | 0.737 [0.70, 0.77] (0.26) | 0.994 [0.99, 1.00] (1.01) | 0.993 [0.98, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frll/opencv | 0.346 [0.30, 0.38] (-0.15) | 0.851 [0.79, 0.91] (0.40) | 0.941 [0.90, 0.98] (0.61) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-L/14 | frll/facemorpher | 0.394 [0.35, 0.43] (-0.10) | 0.884 [0.83, 0.93] (0.46) | 0.887 [0.82, 0.94] (0.47) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| MixFaceNet-MAD | frgcferet/opencv | 0.587 [0.58, 0.60] (0.15) | 0.813 [0.80, 0.83] (0.61) | 0.619 [0.58, 0.65] (0.21) | 0.890 [0.86, 0.91] (0.84) | 0.928 [0.91, 0.95] | reads morphing | mixed | identity reading |
| MixFaceNet-MAD | frgcferet/facemorpher | 0.528 [0.52, 0.54] (0.05) | 0.841 [0.83, 0.86] (0.73) | 0.598 [0.56, 0.63] (0.18) | 0.901 [0.88, 0.92] (0.94) | 0.914 [0.89, 0.93] | reads morphing | no identity reading | identity reading |
| MixFaceNet-MAD | frll/opencv | 0.664 [0.64, 0.70] (0.20) | 0.818 [0.78, 0.86] (0.43) | 0.794 [0.69, 0.88] (0.39) | 0.960 [0.91, 0.99] (0.82) | 0.983 [0.96, 1.00] | not applied | not applied | not applied |
| MixFaceNet-MAD | frll/facemorpher | 0.567 [0.54, 0.60] (0.09) | 0.863 [0.83, 0.90] (0.56) | 0.728 [0.62, 0.82] (0.31) | 0.967 [0.93, 0.99] (0.94) | 0.975 [0.94, 1.00] | not applied | not applied | not applied |
| M3 s1 | frgcferet/opencv | 0.643 [0.63, 0.66] (0.14) | 0.972 [0.97, 0.98] (0.74) | 0.765 [0.73, 0.80] (0.28) | 0.998 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s1 | frgcferet/facemorpher | 0.552 [0.54, 0.56] (0.05) | 0.972 [0.96, 0.98] (0.74) | 0.757 [0.73, 0.79] (0.27) | 0.998 [1.00, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s1 | frll/opencv | 0.599 [0.57, 0.63] (0.10) | 0.926 [0.89, 0.96] (0.56) | 0.946 [0.90, 0.98] (0.62) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s1 | frll/facemorpher | 0.577 [0.56, 0.60] (0.08) | 0.920 [0.88, 0.96] (0.55) | 0.905 [0.84, 0.96] (0.51) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s2 | frgcferet/opencv | 0.624 [0.61, 0.64] (0.12) | 0.995 [0.99, 1.00] (0.99) | 0.781 [0.75, 0.81] (0.30) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s2 | frgcferet/facemorpher | 0.549 [0.54, 0.56] (0.05) | 0.995 [0.99, 1.00] (1.00) | 0.783 [0.75, 0.81] (0.30) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s2 | frll/opencv | 0.620 [0.60, 0.65] (0.12) | 0.968 [0.95, 0.99] (0.72) | 0.926 [0.87, 0.97] (0.56) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s2 | frll/facemorpher | 0.610 [0.60, 0.64] (0.11) | 0.977 [0.96, 0.99] (0.78) | 0.899 [0.83, 0.95] (0.50) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s3 | frgcferet/opencv | 0.603 [0.59, 0.62] (0.10) | 0.996 [0.99, 1.00] (1.00) | 0.772 [0.74, 0.80] (0.29) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s3 | frgcferet/facemorpher | 0.536 [0.53, 0.54] (0.03) | 0.996 [0.99, 1.00] (1.00) | 0.770 [0.74, 0.80] (0.29) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s3 | frll/opencv | 0.554 [0.53, 0.58] (0.05) | 0.977 [0.96, 0.99] (0.77) | 0.933 [0.89, 0.97] (0.58) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s3 | frll/facemorpher | 0.544 [0.53, 0.56] (0.04) | 0.981 [0.96, 0.99] (0.80) | 0.881 [0.82, 0.93] (0.46) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s4 | frgcferet/opencv | 0.692 [0.67, 0.71] (0.20) | 0.984 [0.98, 0.99] (0.84) | 0.758 [0.72, 0.79] (0.27) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s4 | frgcferet/facemorpher | 0.577 [0.57, 0.59] (0.08) | 0.983 [0.98, 0.99] (0.82) | 0.758 [0.72, 0.79] (0.27) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s4 | frll/opencv | 0.646 [0.62, 0.68] (0.15) | 0.950 [0.93, 0.97] (0.64) | 0.899 [0.84, 0.95] (0.49) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s4 | frll/facemorpher | 0.612 [0.59, 0.64] (0.11) | 0.963 [0.94, 0.98] (0.69) | 0.869 [0.79, 0.93] (0.44) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s5 | frgcferet/opencv | 0.665 [0.65, 0.68] (0.17) | 0.944 [0.93, 0.95] (0.62) | 0.767 [0.73, 0.80] (0.28) | 0.994 [0.99, 1.00] (0.98) | 0.995 [0.99, 1.00] | reads morphing | identity reading | identity reading |
| M3 s5 | frgcferet/facemorpher | 0.563 [0.55, 0.57] (0.06) | 0.948 [0.94, 0.96] (0.63) | 0.779 [0.75, 0.81] (0.30) | 0.995 [0.99, 1.00] (1.00) | 0.996 [0.99, 1.00] | reads morphing | identity reading | identity reading |
| M3 s5 | frll/opencv | 0.654 [0.62, 0.69] (0.15) | 0.864 [0.82, 0.91] (0.43) | 0.935 [0.88, 0.97] (0.59) | 0.994 [0.97, 1.00] (0.97) | 0.996 [0.98, 1.00] | not applied | not applied | not applied |
| M3 s5 | frll/facemorpher | 0.607 [0.59, 0.63] (0.11) | 0.894 [0.85, 0.93] (0.49) | 0.907 [0.84, 0.96] (0.51) | 0.999 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s6 | frgcferet/opencv | 0.636 [0.62, 0.65] (0.14) | 0.984 [0.98, 0.99] (0.83) | 0.777 [0.74, 0.81] (0.30) | 0.998 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s6 | frgcferet/facemorpher | 0.550 [0.54, 0.56] (0.05) | 0.985 [0.98, 0.99] (0.84) | 0.781 [0.75, 0.82] (0.30) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s6 | frll/opencv | 0.608 [0.59, 0.64] (0.11) | 0.877 [0.84, 0.91] (0.45) | 0.925 [0.87, 0.97] (0.56) | 0.997 [0.99, 1.00] (1.00) | 0.998 [0.99, 1.00] | not applied | not applied | not applied |
| M3 s6 | frll/facemorpher | 0.597 [0.58, 0.62] (0.10) | 0.888 [0.85, 0.92] (0.47) | 0.891 [0.82, 0.95] (0.48) | 0.994 [0.98, 1.00] (0.97) | 0.997 [0.99, 1.00] | not applied | not applied | not applied |
| M3 s7 | frgcferet/opencv | 0.643 [0.63, 0.66] (0.14) | 0.989 [0.98, 0.99] (0.89) | 0.765 [0.73, 0.80] (0.28) | 0.998 [0.99, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s7 | frgcferet/facemorpher | 0.559 [0.55, 0.57] (0.06) | 0.988 [0.98, 0.99] (0.87) | 0.763 [0.73, 0.80] (0.28) | 0.998 [1.00, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s7 | frll/opencv | 0.596 [0.57, 0.63] (0.09) | 0.967 [0.94, 0.99] (0.71) | 0.916 [0.86, 0.96] (0.54) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s7 | frll/facemorpher | 0.584 [0.56, 0.61] (0.08) | 0.970 [0.95, 0.99] (0.73) | 0.881 [0.81, 0.94] (0.46) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s8 | frgcferet/opencv | 0.568 [0.56, 0.58] (0.07) | 0.986 [0.98, 0.99] (0.85) | 0.768 [0.73, 0.80] (0.28) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s8 | frgcferet/facemorpher | 0.533 [0.53, 0.54] (0.03) | 0.987 [0.98, 0.99] (0.86) | 0.773 [0.74, 0.80] (0.29) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s8 | frll/opencv | 0.602 [0.57, 0.64] (0.10) | 0.941 [0.91, 0.96] (0.61) | 0.908 [0.85, 0.95] (0.52) | 0.999 [0.99, 1.00] (1.00) | 0.999 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s8 | frll/facemorpher | 0.591 [0.58, 0.61] (0.09) | 0.940 [0.91, 0.97] (0.60) | 0.875 [0.80, 0.93] (0.45) | 0.998 [0.99, 1.00] (1.00) | 0.999 [0.99, 1.00] | not applied | not applied | not applied |

#### Ladder C: R0 -> R2w -> R3m -> R4 (main contrast R2w vs R4)

| Detector | Pool / tool | R0->R2w AUC [CI] (share) | R2w->R3m AUC [CI] (share) | R3m->R4 AUC [CI] (share) | R2w vs R4 AUC [CI] (share) | R0 vs R4 | main verdict | side R3m vs R4 | side R2w vs R3m |
|---|---|---|---|---|---|---|---|---|---|
| SelfMAD | frgcferet/opencv | 0.710 [0.69, 0.73] (0.25) | 0.916 [0.90, 0.93] (0.63) | 0.650 [0.61, 0.69] (0.18) | 0.966 [0.95, 0.98] (0.84) | 0.986 [0.98, 0.99] | mixed | mixed | identity reading |
| SelfMAD | frgcferet/facemorpher | 0.650 [0.64, 0.66] (0.16) | 0.961 [0.95, 0.97] (0.73) | 0.588 [0.55, 0.63] (0.09) | 0.984 [0.98, 0.99] (0.88) | 0.992 [0.99, 1.00] | reads morphing | no identity reading | identity reading |
| SelfMAD | frll/opencv | 0.904 [0.88, 0.93] (0.51) | 0.988 [0.98, 1.00] (0.88) | 0.718 [0.62, 0.80] (0.22) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| SelfMAD | frll/facemorpher | 0.811 [0.77, 0.85] (0.34) | 0.993 [0.98, 1.00] (0.95) | 0.584 [0.48, 0.67] (0.08) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-B/16 | frgcferet/opencv | 0.566 [0.55, 0.58] (0.07) | 0.966 [0.96, 0.97] (0.78) | 0.658 [0.62, 0.70] (0.17) | 0.986 [0.98, 0.99] (0.94) | 0.990 [0.98, 0.99] | reads morphing | mixed | identity reading |
| MADation ViT-B/16 | frgcferet/facemorpher | 0.511 [0.50, 0.52] (0.01) | 0.968 [0.96, 0.98] (0.83) | 0.610 [0.57, 0.66] (0.13) | 0.984 [0.97, 0.99] (0.97) | 0.987 [0.98, 0.99] | reads morphing | mixed | identity reading |
| MADation ViT-B/16 | frll/opencv | 0.665 [0.63, 0.71] (0.17) | 0.973 [0.95, 0.99] (0.75) | 0.838 [0.75, 0.92] (0.38) | 0.997 [0.98, 1.00] (1.00) | 0.999 [0.99, 1.00] | not applied | not applied | not applied |
| MADation ViT-B/16 | frll/facemorpher | 0.583 [0.55, 0.62] (0.08) | 0.981 [0.96, 1.00] (0.81) | 0.806 [0.71, 0.89] (0.33) | 0.999 [0.99, 1.00] (1.00) | 0.999 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-L/14 | frgcferet/opencv | 0.427 [0.41, 0.44] (-0.08) | 0.971 [0.96, 0.98] (0.80) | 0.641 [0.60, 0.68] (0.15) | 0.992 [0.98, 1.00] (1.01) | 0.991 [0.98, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frgcferet/facemorpher | 0.463 [0.45, 0.48] (-0.04) | 0.983 [0.98, 0.99] (0.86) | 0.615 [0.58, 0.66] (0.12) | 0.994 [0.99, 1.00] (1.01) | 0.993 [0.98, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frll/opencv | 0.346 [0.30, 0.38] (-0.15) | 0.990 [0.98, 1.00] (0.90) | 0.806 [0.72, 0.89] (0.34) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-L/14 | frll/facemorpher | 0.394 [0.35, 0.43] (-0.10) | 0.984 [0.96, 1.00] (0.83) | 0.723 [0.62, 0.81] (0.23) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| MixFaceNet-MAD | frgcferet/opencv | 0.587 [0.58, 0.60] (0.15) | 0.774 [0.76, 0.79] (0.52) | 0.637 [0.60, 0.67] (0.24) | 0.890 [0.86, 0.91] (0.84) | 0.928 [0.91, 0.95] | reads morphing | mixed | identity reading |
| MixFaceNet-MAD | frgcferet/facemorpher | 0.528 [0.52, 0.54] (0.05) | 0.806 [0.79, 0.82] (0.63) | 0.616 [0.58, 0.65] (0.22) | 0.901 [0.88, 0.92] (0.94) | 0.914 [0.89, 0.93] | reads morphing | mixed | identity reading |
| MixFaceNet-MAD | frll/opencv | 0.664 [0.64, 0.70] (0.20) | 0.908 [0.88, 0.94] (0.62) | 0.629 [0.53, 0.72] (0.16) | 0.960 [0.91, 0.99] (0.82) | 0.983 [0.96, 1.00] | not applied | not applied | not applied |
| MixFaceNet-MAD | frll/facemorpher | 0.567 [0.54, 0.60] (0.09) | 0.941 [0.91, 0.97] (0.80) | 0.584 [0.48, 0.68] (0.11) | 0.967 [0.93, 0.99] (0.94) | 0.975 [0.94, 1.00] | not applied | not applied | not applied |
| M3 s1 | frgcferet/opencv | 0.643 [0.63, 0.66] (0.14) | 0.982 [0.98, 0.99] (0.81) | 0.720 [0.68, 0.76] (0.23) | 0.998 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s1 | frgcferet/facemorpher | 0.552 [0.54, 0.56] (0.05) | 0.985 [0.98, 0.99] (0.84) | 0.694 [0.65, 0.74] (0.20) | 0.998 [1.00, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s1 | frll/opencv | 0.599 [0.57, 0.63] (0.10) | 0.998 [0.99, 1.00] (1.00) | 0.860 [0.78, 0.93] (0.42) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s1 | frll/facemorpher | 0.577 [0.56, 0.60] (0.08) | 0.998 [0.99, 1.00] (1.00) | 0.828 [0.73, 0.91] (0.37) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s2 | frgcferet/opencv | 0.624 [0.61, 0.64] (0.12) | 0.993 [0.99, 1.00] (0.96) | 0.850 [0.82, 0.88] (0.40) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s2 | frgcferet/facemorpher | 0.549 [0.54, 0.56] (0.05) | 0.994 [0.99, 1.00] (0.98) | 0.846 [0.81, 0.88] (0.40) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s2 | frll/opencv | 0.620 [0.60, 0.65] (0.12) | 0.997 [0.99, 1.00] (1.00) | 0.839 [0.76, 0.91] (0.38) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s2 | frll/facemorpher | 0.610 [0.60, 0.64] (0.11) | 0.998 [0.99, 1.00] (1.00) | 0.822 [0.73, 0.90] (0.36) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s3 | frgcferet/opencv | 0.603 [0.59, 0.62] (0.10) | 0.996 [0.99, 1.00] (1.00) | 0.752 [0.71, 0.79] (0.26) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s3 | frgcferet/facemorpher | 0.536 [0.53, 0.54] (0.03) | 0.997 [0.99, 1.00] (1.00) | 0.732 [0.69, 0.77] (0.24) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s3 | frll/opencv | 0.554 [0.53, 0.58] (0.05) | 0.997 [0.99, 1.00] (1.00) | 0.740 [0.66, 0.82] (0.25) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s3 | frll/facemorpher | 0.544 [0.53, 0.56] (0.04) | 0.999 [1.00, 1.00] (1.00) | 0.697 [0.60, 0.78] (0.20) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s4 | frgcferet/opencv | 0.692 [0.67, 0.71] (0.20) | 0.992 [0.99, 1.00] (0.94) | 0.719 [0.68, 0.76] (0.22) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s4 | frgcferet/facemorpher | 0.577 [0.57, 0.59] (0.08) | 0.993 [0.99, 1.00] (0.95) | 0.714 [0.67, 0.76] (0.22) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s4 | frll/opencv | 0.646 [0.62, 0.68] (0.15) | 0.999 [1.00, 1.00] (1.00) | 0.742 [0.64, 0.84] (0.25) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s4 | frll/facemorpher | 0.612 [0.59, 0.64] (0.11) | 1.000 [1.00, 1.00] (1.00) | 0.750 [0.63, 0.85] (0.26) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s5 | frgcferet/opencv | 0.665 [0.65, 0.68] (0.17) | 0.961 [0.95, 0.97] (0.69) | 0.715 [0.67, 0.75] (0.22) | 0.994 [0.99, 1.00] (0.98) | 0.995 [0.99, 1.00] | reads morphing | mixed | identity reading |
| M3 s5 | frgcferet/facemorpher | 0.563 [0.55, 0.57] (0.06) | 0.970 [0.96, 0.98] (0.73) | 0.717 [0.68, 0.76] (0.22) | 0.995 [0.99, 1.00] (1.00) | 0.996 [0.99, 1.00] | reads morphing | mixed | identity reading |
| M3 s5 | frll/opencv | 0.654 [0.62, 0.69] (0.15) | 0.984 [0.96, 1.00] (0.83) | 0.763 [0.68, 0.84] (0.28) | 0.994 [0.97, 1.00] (0.97) | 0.996 [0.98, 1.00] | not applied | not applied | not applied |
| M3 s5 | frll/facemorpher | 0.607 [0.59, 0.63] (0.11) | 0.990 [0.97, 1.00] (0.91) | 0.757 [0.66, 0.85] (0.27) | 0.999 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s6 | frgcferet/opencv | 0.636 [0.62, 0.65] (0.14) | 0.989 [0.98, 0.99] (0.89) | 0.737 [0.69, 0.78] (0.25) | 0.998 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s6 | frgcferet/facemorpher | 0.550 [0.54, 0.56] (0.05) | 0.991 [0.99, 0.99] (0.92) | 0.725 [0.68, 0.77] (0.23) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s6 | frll/opencv | 0.608 [0.59, 0.64] (0.11) | 0.979 [0.96, 0.99] (0.79) | 0.772 [0.68, 0.86] (0.29) | 0.997 [0.99, 1.00] (1.00) | 0.998 [0.99, 1.00] | not applied | not applied | not applied |
| M3 s6 | frll/facemorpher | 0.597 [0.58, 0.62] (0.10) | 0.980 [0.96, 0.99] (0.80) | 0.728 [0.62, 0.83] (0.24) | 0.994 [0.98, 1.00] (0.97) | 0.997 [0.99, 1.00] | not applied | not applied | not applied |
| M3 s7 | frgcferet/opencv | 0.643 [0.63, 0.66] (0.14) | 0.991 [0.99, 1.00] (0.92) | 0.755 [0.72, 0.79] (0.27) | 0.998 [0.99, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s7 | frgcferet/facemorpher | 0.559 [0.55, 0.57] (0.06) | 0.992 [0.99, 1.00] (0.93) | 0.737 [0.69, 0.78] (0.25) | 0.998 [1.00, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s7 | frll/opencv | 0.596 [0.57, 0.63] (0.09) | 0.995 [0.99, 1.00] (1.00) | 0.809 [0.73, 0.88] (0.34) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s7 | frll/facemorpher | 0.584 [0.56, 0.61] (0.08) | 0.997 [0.99, 1.00] (1.00) | 0.785 [0.69, 0.87] (0.31) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s8 | frgcferet/opencv | 0.568 [0.56, 0.58] (0.07) | 0.988 [0.98, 0.99] (0.88) | 0.775 [0.74, 0.81] (0.29) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s8 | frgcferet/facemorpher | 0.533 [0.53, 0.54] (0.03) | 0.992 [0.99, 1.00] (0.93) | 0.764 [0.73, 0.80] (0.28) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s8 | frll/opencv | 0.602 [0.57, 0.64] (0.10) | 0.991 [0.98, 1.00] (0.92) | 0.749 [0.66, 0.83] (0.26) | 0.999 [0.99, 1.00] (1.00) | 0.999 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s8 | frll/facemorpher | 0.591 [0.58, 0.61] (0.09) | 0.990 [0.98, 1.00] (0.91) | 0.731 [0.63, 0.82] (0.24) | 0.998 [0.99, 1.00] (1.00) | 0.999 [0.99, 1.00] | not applied | not applied | not applied |

#### Ladder D: R0 -> R2wm -> R3m -> R4 (main contrast R2wm vs R4)

| Detector | Pool / tool | R0->R2wm AUC [CI] (share) | R2wm->R3m AUC [CI] (share) | R3m->R4 AUC [CI] (share) | R2wm vs R4 AUC [CI] (share) | R0 vs R4 | main verdict | side R3m vs R4 | side R2wm vs R3m |
|---|---|---|---|---|---|---|---|---|---|
| SelfMAD | frgcferet/opencv | 0.705 [0.69, 0.72] (0.25) | 0.921 [0.91, 0.94] (0.65) | 0.650 [0.61, 0.69] (0.18) | 0.967 [0.96, 0.98] (0.84) | 0.986 [0.98, 0.99] | mixed | mixed | identity reading |
| SelfMAD | frgcferet/facemorpher | 0.646 [0.63, 0.66] (0.15) | 0.967 [0.96, 0.98] (0.76) | 0.588 [0.55, 0.63] (0.09) | 0.987 [0.98, 0.99] (0.91) | 0.992 [0.99, 1.00] | reads morphing | no identity reading | identity reading |
| SelfMAD | frll/opencv | 0.879 [0.85, 0.91] (0.46) | 0.985 [0.97, 1.00] (0.85) | 0.718 [0.62, 0.80] (0.22) | 0.998 [0.99, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| SelfMAD | frll/facemorpher | 0.766 [0.73, 0.81] (0.28) | 0.995 [0.99, 1.00] (1.00) | 0.584 [0.48, 0.67] (0.08) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| SelfMAD | frll_clean/opencv | 0.879 [0.85, 0.91] (0.46) | 0.985 [0.97, 1.00] (0.85) | 0.634 [0.56, 0.71] (0.13) | 0.994 [0.99, 1.00] (0.98) | 0.999 [1.00, 1.00] | mixed | mixed | identity reading |
| SelfMAD | frll_clean/facemorpher | 0.766 [0.73, 0.81] (0.28) | 0.995 [0.99, 1.00] (1.00) | 0.534 [0.47, 0.60] (0.03) | 0.998 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | mixed | no identity reading | identity reading |
| MADation ViT-B/16 | frgcferet/opencv | 0.557 [0.54, 0.57] (0.06) | 0.968 [0.96, 0.98] (0.80) | 0.658 [0.62, 0.70] (0.17) | 0.987 [0.98, 0.99] (0.96) | 0.990 [0.98, 0.99] | reads morphing | mixed | identity reading |
| MADation ViT-B/16 | frgcferet/facemorpher | 0.510 [0.50, 0.52] (0.01) | 0.970 [0.96, 0.98] (0.84) | 0.610 [0.57, 0.66] (0.13) | 0.986 [0.98, 0.99] (0.98) | 0.987 [0.98, 0.99] | reads morphing | mixed | identity reading |
| MADation ViT-B/16 | frll/opencv | 0.680 [0.64, 0.72] (0.18) | 0.972 [0.95, 0.99] (0.74) | 0.838 [0.75, 0.92] (0.38) | 0.996 [0.98, 1.00] (1.00) | 0.999 [0.99, 1.00] | not applied | not applied | not applied |
| MADation ViT-B/16 | frll/facemorpher | 0.568 [0.54, 0.60] (0.07) | 0.982 [0.96, 1.00] (0.81) | 0.806 [0.71, 0.89] (0.33) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-B/16 | frll_clean/opencv | 0.680 [0.64, 0.72] (0.18) | 0.972 [0.95, 0.99] (0.74) | 0.749 [0.69, 0.81] (0.26) | 0.996 [0.99, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-B/16 | frll_clean/facemorpher | 0.568 [0.54, 0.60] (0.07) | 0.982 [0.96, 1.00] (0.81) | 0.722 [0.66, 0.78] (0.23) | 0.997 [0.99, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frgcferet/opencv | 0.408 [0.39, 0.42] (-0.10) | 0.972 [0.96, 0.98] (0.81) | 0.641 [0.60, 0.68] (0.15) | 0.992 [0.98, 1.00] (1.03) | 0.991 [0.98, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frgcferet/facemorpher | 0.442 [0.43, 0.46] (-0.06) | 0.983 [0.98, 0.99] (0.85) | 0.615 [0.58, 0.66] (0.12) | 0.993 [0.98, 1.00] (0.99) | 0.993 [0.98, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frll/opencv | 0.370 [0.33, 0.40] (-0.13) | 0.989 [0.97, 1.00] (0.89) | 0.806 [0.72, 0.89] (0.34) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-L/14 | frll/facemorpher | 0.392 [0.36, 0.42] (-0.11) | 0.984 [0.96, 1.00] (0.83) | 0.723 [0.62, 0.81] (0.23) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| MADation ViT-L/14 | frll_clean/opencv | 0.370 [0.33, 0.40] (-0.13) | 0.989 [0.97, 1.00] (0.89) | 0.731 [0.66, 0.80] (0.24) | 0.997 [0.99, 1.00] (1.00) | 0.996 [0.99, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frll_clean/facemorpher | 0.392 [0.36, 0.42] (-0.11) | 0.984 [0.96, 1.00] (0.83) | 0.669 [0.60, 0.74] (0.17) | 0.996 [0.99, 1.00] (1.00) | 0.995 [0.99, 1.00] | reads morphing | mixed | identity reading |
| MixFaceNet-MAD | frgcferet/opencv | 0.587 [0.58, 0.60] (0.15) | 0.774 [0.76, 0.79] (0.51) | 0.637 [0.60, 0.67] (0.24) | 0.888 [0.86, 0.91] (0.84) | 0.928 [0.91, 0.95] | reads morphing | mixed | identity reading |
| MixFaceNet-MAD | frgcferet/facemorpher | 0.520 [0.51, 0.53] (0.04) | 0.810 [0.79, 0.83] (0.64) | 0.616 [0.58, 0.65] (0.22) | 0.904 [0.88, 0.93] (0.96) | 0.914 [0.89, 0.93] | reads morphing | mixed | identity reading |
| MixFaceNet-MAD | frll/opencv | 0.647 [0.62, 0.68] (0.18) | 0.914 [0.88, 0.95] (0.64) | 0.629 [0.53, 0.72] (0.16) | 0.961 [0.92, 0.99] (0.83) | 0.983 [0.96, 1.00] | not applied | not applied | not applied |
| MixFaceNet-MAD | frll/facemorpher | 0.547 [0.52, 0.58] (0.06) | 0.943 [0.92, 0.97] (0.81) | 0.584 [0.48, 0.68] (0.11) | 0.971 [0.94, 0.99] (0.97) | 0.975 [0.94, 1.00] | not applied | not applied | not applied |
| MixFaceNet-MAD | frll_clean/opencv | 0.647 [0.62, 0.68] (0.15) | 0.914 [0.88, 0.95] (0.55) | 0.735 [0.69, 0.78] (0.25) | 0.986 [0.97, 0.99] (0.88) | 0.994 [0.99, 1.00] | reads morphing | mixed | identity reading |
| MixFaceNet-MAD | frll_clean/facemorpher | 0.547 [0.52, 0.58] (0.05) | 0.943 [0.92, 0.97] (0.68) | 0.706 [0.65, 0.75] (0.23) | 0.988 [0.98, 1.00] (0.97) | 0.990 [0.98, 1.00] | reads morphing | mixed | identity reading |
| M3 s4 | frgcferet/opencv | 0.692 [0.67, 0.71] (0.19) | 0.993 [0.99, 1.00] (0.95) | 0.719 [0.68, 0.76] (0.22) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s4 | frgcferet/facemorpher | 0.575 [0.57, 0.58] (0.07) | 0.993 [0.99, 1.00] (0.95) | 0.714 [0.67, 0.76] (0.22) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s4 | frll/opencv | 0.653 [0.63, 0.69] (0.15) | 0.999 [1.00, 1.00] (1.00) | 0.742 [0.64, 0.84] (0.25) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s4 | frll/facemorpher | 0.599 [0.58, 0.62] (0.10) | 1.000 [1.00, 1.00] (1.00) | 0.750 [0.63, 0.85] (0.26) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s5 | frgcferet/opencv | 0.662 [0.64, 0.68] (0.16) | 0.961 [0.95, 0.97] (0.69) | 0.715 [0.67, 0.75] (0.22) | 0.994 [0.99, 1.00] (0.98) | 0.995 [0.99, 1.00] | reads morphing | mixed | identity reading |
| M3 s5 | frgcferet/facemorpher | 0.555 [0.55, 0.56] (0.05) | 0.971 [0.96, 0.98] (0.73) | 0.717 [0.68, 0.76] (0.22) | 0.995 [0.99, 1.00] (1.00) | 0.996 [0.99, 1.00] | reads morphing | mixed | identity reading |
| M3 s5 | frll/opencv | 0.671 [0.64, 0.71] (0.17) | 0.984 [0.96, 1.00] (0.83) | 0.763 [0.68, 0.84] (0.28) | 0.994 [0.97, 1.00] (0.98) | 0.996 [0.98, 1.00] | not applied | not applied | not applied |
| M3 s5 | frll/facemorpher | 0.605 [0.59, 0.63] (0.10) | 0.991 [0.97, 1.00] (0.92) | 0.757 [0.66, 0.85] (0.27) | 0.999 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s6 | frgcferet/opencv | 0.638 [0.62, 0.65] (0.14) | 0.989 [0.98, 0.99] (0.89) | 0.737 [0.69, 0.78] (0.25) | 0.998 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s6 | frgcferet/facemorpher | 0.548 [0.54, 0.56] (0.05) | 0.991 [0.99, 0.99] (0.92) | 0.725 [0.68, 0.77] (0.23) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s6 | frll/opencv | 0.631 [0.61, 0.66] (0.13) | 0.981 [0.96, 0.99] (0.81) | 0.772 [0.68, 0.86] (0.29) | 0.997 [0.99, 1.00] (1.00) | 0.998 [0.99, 1.00] | not applied | not applied | not applied |
| M3 s6 | frll/facemorpher | 0.585 [0.57, 0.61] (0.08) | 0.982 [0.96, 1.00] (0.81) | 0.728 [0.62, 0.83] (0.24) | 0.995 [0.98, 1.00] (1.00) | 0.997 [0.99, 1.00] | not applied | not applied | not applied |
| M3 s7 | frgcferet/opencv | 0.646 [0.63, 0.66] (0.15) | 0.991 [0.99, 1.00] (0.92) | 0.755 [0.72, 0.79] (0.27) | 0.998 [0.99, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s7 | frgcferet/facemorpher | 0.554 [0.55, 0.56] (0.05) | 0.992 [0.99, 1.00] (0.93) | 0.737 [0.69, 0.78] (0.25) | 0.998 [0.99, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | mixed | identity reading |
| M3 s7 | frll/opencv | 0.626 [0.60, 0.66] (0.12) | 0.998 [0.99, 1.00] (1.00) | 0.809 [0.73, 0.88] (0.34) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s7 | frll/facemorpher | 0.579 [0.56, 0.60] (0.08) | 0.998 [0.99, 1.00] (1.00) | 0.785 [0.69, 0.87] (0.31) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s8 | frgcferet/opencv | 0.574 [0.56, 0.59] (0.07) | 0.988 [0.98, 0.99] (0.88) | 0.775 [0.74, 0.81] (0.29) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s8 | frgcferet/facemorpher | 0.534 [0.53, 0.54] (0.03) | 0.991 [0.99, 0.99] (0.92) | 0.764 [0.73, 0.80] (0.28) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s8 | frll/opencv | 0.620 [0.59, 0.66] (0.12) | 0.991 [0.98, 1.00] (0.92) | 0.749 [0.66, 0.83] (0.26) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | not applied | not applied | not applied |
| M3 s8 | frll/facemorpher | 0.585 [0.57, 0.61] (0.08) | 0.991 [0.98, 1.00] (0.92) | 0.731 [0.63, 0.82] (0.24) | 0.998 [0.99, 1.00] (1.00) | 0.999 [0.99, 1.00] | not applied | not applied | not applied |

#### Ladder E: R0 -> R2w4 -> R3 -> R4 (main contrast R2w4 vs R4)

| Detector | Pool / tool | R0->R2w4 AUC [CI] (share) | R2w4->R3 AUC [CI] (share) | R3->R4 AUC [CI] (share) | R2w4 vs R4 AUC [CI] (share) | R0 vs R4 | main verdict | side R3 vs R4 | side R2w4 vs R3 |
|---|---|---|---|---|---|---|---|---|---|
| SelfMAD | frgcferet/opencv | 0.715 [0.70, 0.73] (0.26) | 0.912 [0.90, 0.93] (0.62) | 0.689 [0.65, 0.73] (0.23) | 0.959 [0.95, 0.97] (0.80) | 0.986 [0.98, 0.99] | mixed | mixed | identity reading |
| SelfMAD | frgcferet/facemorpher | 0.664 [0.65, 0.68] (0.17) | 0.954 [0.94, 0.96] (0.69) | 0.663 [0.63, 0.70] (0.17) | 0.981 [0.97, 0.99] (0.85) | 0.992 [0.99, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-B/16 | frgcferet/opencv | 0.561 [0.55, 0.58] (0.07) | 0.949 [0.94, 0.96] (0.70) | 0.695 [0.65, 0.73] (0.22) | 0.986 [0.98, 0.99] (0.95) | 0.990 [0.98, 0.99] | reads morphing | mixed | identity reading |
| MADation ViT-B/16 | frgcferet/facemorpher | 0.503 [0.49, 0.52] (0.00) | 0.948 [0.94, 0.96] (0.73) | 0.672 [0.63, 0.71] (0.20) | 0.984 [0.97, 0.99] (0.96) | 0.987 [0.98, 0.99] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frgcferet/opencv | 0.415 [0.40, 0.43] (-0.09) | 0.898 [0.88, 0.92] (0.54) | 0.749 [0.71, 0.79] (0.28) | 0.992 [0.98, 1.00] (1.02) | 0.991 [0.98, 1.00] | reads morphing | mixed | identity reading |
| MADation ViT-L/14 | frgcferet/facemorpher | 0.454 [0.44, 0.47] (-0.05) | 0.926 [0.91, 0.94] (0.58) | 0.737 [0.70, 0.77] (0.26) | 0.994 [0.99, 1.00] (1.01) | 0.993 [0.98, 1.00] | reads morphing | mixed | identity reading |
| MixFaceNet-MAD | frgcferet/opencv | 0.587 [0.58, 0.60] (0.15) | 0.814 [0.80, 0.83] (0.61) | 0.619 [0.58, 0.65] (0.21) | 0.889 [0.86, 0.91] (0.84) | 0.928 [0.91, 0.95] | reads morphing | mixed | identity reading |
| MixFaceNet-MAD | frgcferet/facemorpher | 0.521 [0.51, 0.53] (0.04) | 0.846 [0.83, 0.86] (0.75) | 0.598 [0.56, 0.63] (0.18) | 0.903 [0.88, 0.92] (0.95) | 0.914 [0.89, 0.93] | reads morphing | no identity reading | identity reading |
| M3 s1 | frgcferet/opencv | 0.652 [0.64, 0.67] (0.15) | 0.971 [0.96, 0.98] (0.74) | 0.765 [0.73, 0.80] (0.28) | 0.998 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s1 | frgcferet/facemorpher | 0.556 [0.55, 0.57] (0.06) | 0.971 [0.96, 0.98] (0.74) | 0.757 [0.73, 0.79] (0.27) | 0.998 [0.99, 1.00] (1.00) | 0.998 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s2 | frgcferet/opencv | 0.635 [0.62, 0.65] (0.13) | 0.994 [0.99, 1.00] (0.98) | 0.781 [0.75, 0.81] (0.30) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s2 | frgcferet/facemorpher | 0.567 [0.56, 0.58] (0.07) | 0.994 [0.99, 1.00] (0.98) | 0.783 [0.75, 0.81] (0.30) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s3 | frgcferet/opencv | 0.613 [0.60, 0.63] (0.11) | 0.996 [0.99, 1.00] (1.00) | 0.772 [0.74, 0.80] (0.29) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s3 | frgcferet/facemorpher | 0.543 [0.54, 0.55] (0.04) | 0.996 [0.99, 1.00] (1.00) | 0.770 [0.74, 0.80] (0.29) | 1.000 [1.00, 1.00] (1.00) | 1.000 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s4 | frgcferet/opencv | 0.702 [0.68, 0.72] (0.21) | 0.984 [0.98, 0.99] (0.83) | 0.758 [0.72, 0.79] (0.27) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | mixed | identity reading | identity reading |
| M3 s4 | frgcferet/facemorpher | 0.581 [0.57, 0.59] (0.08) | 0.982 [0.98, 0.99] (0.82) | 0.758 [0.72, 0.79] (0.27) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s8 | frgcferet/opencv | 0.572 [0.56, 0.59] (0.07) | 0.985 [0.98, 0.99] (0.85) | 0.768 [0.73, 0.80] (0.28) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |
| M3 s8 | frgcferet/facemorpher | 0.536 [0.53, 0.55] (0.04) | 0.986 [0.98, 0.99] (0.86) | 0.773 [0.74, 0.80] (0.29) | 0.999 [1.00, 1.00] (1.00) | 0.999 [1.00, 1.00] | reads morphing | identity reading | identity reading |

#### Key contrasts on the primary pool (ladder B rows), with the best simple baseline

| Detector | tool | contrast | detector AUC [CI] | best simple baseline (AUC) | excess [CI] | best non-content (AUC) | excess [CI] |
|---|---|---|---|---|---|---|---|
| SelfMAD | opencv | R2wvsR4 | 0.966 [0.95, 0.98] | lapvar (0.774) | 0.192 [0.16, 0.23] | bytes (0.685) | 0.281 [0.25, 0.31] |
| SelfMAD | opencv | R0->R2w | 0.710 [0.69, 0.73] | band (0.858) | -0.148 [-0.17, -0.13] | bytes (0.637) | 0.073 [0.05, 0.09] |
| SelfMAD | opencv | R3->R4 | 0.689 [0.65, 0.73] | band (0.631) | 0.059 [0.01, 0.11] | background (0.597) | 0.092 [0.04, 0.14] |
| SelfMAD | opencv | R2w4vsR4 | 0.959 [0.95, 0.97] | lapvar (0.768) | 0.191 [0.16, 0.23] | bytes (0.682) | 0.278 [0.24, 0.31] |
| SelfMAD | opencv | R2wvsR2w4 | 0.508 [0.50, 0.52] | background (0.570) | -0.062 [-0.08, -0.04] | background (0.570) | -0.062 [-0.08, -0.04] |
| SelfMAD | facemorpher | R2wvsR4 | 0.984 [0.98, 0.99] | band (0.756) | 0.228 [0.19, 0.26] | bytes (0.687) | 0.297 [0.26, 0.33] |
| SelfMAD | facemorpher | R0->R2w | 0.650 [0.64, 0.66] | band (0.719) | -0.069 [-0.09, -0.05] | bytes (0.575) | 0.075 [0.06, 0.09] |
| SelfMAD | facemorpher | R3->R4 | 0.663 [0.63, 0.70] | band (0.622) | 0.041 [-0.01, 0.10] | background (0.621) | 0.042 [-0.01, 0.09] |
| SelfMAD | facemorpher | R2w4vsR4 | 0.981 [0.97, 0.99] | band (0.762) | 0.218 [0.18, 0.25] | bytes (0.685) | 0.296 [0.26, 0.33] |
| SelfMAD | facemorpher | R2wvsR2w4 | 0.515 [0.50, 0.53] | background (0.598) | -0.083 [-0.10, -0.06] | background (0.598) | -0.083 [-0.10, -0.06] |
| MADation ViT-B/16 | opencv | R2wvsR4 | 0.986 [0.98, 0.99] | lapvar (0.774) | 0.212 [0.18, 0.24] | bytes (0.685) | 0.300 [0.27, 0.33] |
| MADation ViT-B/16 | opencv | R0->R2w | 0.566 [0.55, 0.58] | band (0.858) | -0.292 [-0.32, -0.26] | bytes (0.637) | -0.071 [-0.09, -0.05] |
| MADation ViT-B/16 | opencv | R3->R4 | 0.695 [0.65, 0.73] | band (0.631) | 0.064 [-0.00, 0.13] | background (0.597) | 0.098 [0.05, 0.15] |
| MADation ViT-B/16 | opencv | R2w4vsR4 | 0.986 [0.98, 0.99] | lapvar (0.768) | 0.218 [0.19, 0.25] | bytes (0.682) | 0.305 [0.27, 0.33] |
| MADation ViT-B/16 | opencv | R2wvsR2w4 | 0.494 [0.48, 0.51] | background (0.570) | -0.077 [-0.10, -0.06] | background (0.570) | -0.077 [-0.10, -0.06] |
| MADation ViT-B/16 | facemorpher | R2wvsR4 | 0.984 [0.97, 0.99] | band (0.756) | 0.229 [0.19, 0.26] | bytes (0.687) | 0.298 [0.27, 0.33] |
| MADation ViT-B/16 | facemorpher | R0->R2w | 0.511 [0.50, 0.52] | band (0.719) | -0.208 [-0.23, -0.18] | bytes (0.575) | -0.063 [-0.08, -0.05] |
| MADation ViT-B/16 | facemorpher | R3->R4 | 0.672 [0.63, 0.71] | band (0.622) | 0.049 [-0.01, 0.12] | background (0.621) | 0.051 [-0.00, 0.10] |
| MADation ViT-B/16 | facemorpher | R2w4vsR4 | 0.984 [0.97, 0.99] | band (0.762) | 0.222 [0.19, 0.26] | bytes (0.685) | 0.299 [0.27, 0.33] |
| MADation ViT-B/16 | facemorpher | R2wvsR2w4 | 0.491 [0.48, 0.50] | background (0.598) | -0.107 [-0.13, -0.09] | background (0.598) | -0.107 [-0.13, -0.09] |
| MADation ViT-L/14 | opencv | R2wvsR4 | 0.992 [0.98, 1.00] | lapvar (0.774) | 0.218 [0.19, 0.25] | bytes (0.685) | 0.307 [0.27, 0.34] |
| MADation ViT-L/14 | opencv | R0->R2w | 0.427 [0.41, 0.44] | band (0.858) | -0.431 [-0.46, -0.40] | bytes (0.637) | -0.211 [-0.23, -0.19] |
| MADation ViT-L/14 | opencv | R3->R4 | 0.749 [0.71, 0.79] | band (0.631) | 0.119 [0.06, 0.18] | background (0.597) | 0.152 [0.10, 0.20] |
| MADation ViT-L/14 | opencv | R2w4vsR4 | 0.992 [0.98, 1.00] | lapvar (0.768) | 0.224 [0.19, 0.26] | bytes (0.682) | 0.310 [0.28, 0.34] |
| MADation ViT-L/14 | opencv | R2wvsR2w4 | 0.489 [0.48, 0.50] | background (0.570) | -0.081 [-0.10, -0.06] | background (0.570) | -0.081 [-0.10, -0.06] |
| MADation ViT-L/14 | facemorpher | R2wvsR4 | 0.994 [0.99, 1.00] | band (0.756) | 0.238 [0.20, 0.27] | bytes (0.687) | 0.307 [0.28, 0.34] |
| MADation ViT-L/14 | facemorpher | R0->R2w | 0.463 [0.45, 0.48] | band (0.719) | -0.256 [-0.28, -0.23] | bytes (0.575) | -0.111 [-0.13, -0.10] |
| MADation ViT-L/14 | facemorpher | R3->R4 | 0.737 [0.70, 0.77] | band (0.622) | 0.114 [0.05, 0.18] | background (0.621) | 0.116 [0.07, 0.16] |
| MADation ViT-L/14 | facemorpher | R2w4vsR4 | 0.994 [0.99, 1.00] | band (0.762) | 0.231 [0.20, 0.27] | bytes (0.685) | 0.309 [0.28, 0.34] |
| MADation ViT-L/14 | facemorpher | R2wvsR2w4 | 0.490 [0.48, 0.50] | background (0.598) | -0.108 [-0.13, -0.09] | background (0.598) | -0.108 [-0.13, -0.09] |
| MixFaceNet-MAD | opencv | R2wvsR4 | 0.890 [0.86, 0.91] | lapvar (0.774) | 0.116 [0.08, 0.15] | bytes (0.685) | 0.204 [0.17, 0.24] |
| MixFaceNet-MAD | opencv | R0->R2w | 0.587 [0.58, 0.60] | band (0.858) | -0.271 [-0.30, -0.25] | bytes (0.637) | -0.050 [-0.07, -0.03] |
| MixFaceNet-MAD | opencv | R3->R4 | 0.619 [0.58, 0.65] | band (0.631) | -0.012 [-0.07, 0.05] | background (0.597) | 0.022 [-0.03, 0.07] |
| MixFaceNet-MAD | opencv | R2w4vsR4 | 0.889 [0.86, 0.91] | lapvar (0.768) | 0.120 [0.09, 0.15] | bytes (0.682) | 0.207 [0.17, 0.24] |
| MixFaceNet-MAD | opencv | R2wvsR2w4 | 0.499 [0.49, 0.51] | background (0.570) | -0.071 [-0.09, -0.05] | background (0.570) | -0.071 [-0.09, -0.05] |
| MixFaceNet-MAD | facemorpher | R2wvsR4 | 0.901 [0.88, 0.92] | band (0.756) | 0.145 [0.11, 0.19] | bytes (0.687) | 0.214 [0.18, 0.25] |
| MixFaceNet-MAD | facemorpher | R0->R2w | 0.528 [0.52, 0.54] | band (0.719) | -0.191 [-0.21, -0.17] | bytes (0.575) | -0.047 [-0.06, -0.03] |
| MixFaceNet-MAD | facemorpher | R3->R4 | 0.598 [0.56, 0.63] | band (0.622) | -0.025 [-0.09, 0.04] | background (0.621) | -0.023 [-0.08, 0.03] |
| MixFaceNet-MAD | facemorpher | R2w4vsR4 | 0.903 [0.88, 0.92] | band (0.762) | 0.141 [0.10, 0.18] | bytes (0.685) | 0.218 [0.19, 0.25] |
| MixFaceNet-MAD | facemorpher | R2wvsR2w4 | 0.493 [0.49, 0.50] | background (0.598) | -0.105 [-0.12, -0.09] | background (0.598) | -0.105 [-0.12, -0.09] |
| M3 s1 | opencv | R2wvsR4 | 0.998 [1.00, 1.00] | lapvar (0.774) | 0.224 [0.19, 0.26] | bytes (0.685) | 0.313 [0.28, 0.34] |
| M3 s1 | opencv | R0->R2w | 0.643 [0.63, 0.66] | band (0.858) | -0.215 [-0.23, -0.19] | bytes (0.637) | 0.006 [-0.01, 0.02] |
| M3 s1 | opencv | R3->R4 | 0.765 [0.73, 0.80] | band (0.631) | 0.134 [0.08, 0.19] | background (0.597) | 0.168 [0.12, 0.21] |
| M3 s1 | opencv | R2w4vsR4 | 0.998 [1.00, 1.00] | lapvar (0.768) | 0.230 [0.20, 0.26] | bytes (0.682) | 0.317 [0.28, 0.35] |
| M3 s1 | opencv | R2wvsR2w4 | 0.509 [0.50, 0.52] | background (0.570) | -0.062 [-0.08, -0.04] | background (0.570) | -0.062 [-0.08, -0.04] |
| M3 s1 | facemorpher | R2wvsR4 | 0.998 [1.00, 1.00] | band (0.756) | 0.243 [0.21, 0.28] | bytes (0.687) | 0.311 [0.28, 0.34] |
| M3 s1 | facemorpher | R0->R2w | 0.552 [0.54, 0.56] | band (0.719) | -0.167 [-0.19, -0.15] | bytes (0.575) | -0.023 [-0.03, -0.01] |
| M3 s1 | facemorpher | R3->R4 | 0.757 [0.73, 0.79] | band (0.622) | 0.135 [0.08, 0.19] | background (0.621) | 0.136 [0.09, 0.18] |
| M3 s1 | facemorpher | R2w4vsR4 | 0.998 [0.99, 1.00] | band (0.762) | 0.235 [0.20, 0.27] | bytes (0.685) | 0.313 [0.28, 0.34] |
| M3 s1 | facemorpher | R2wvsR2w4 | 0.505 [0.50, 0.51] | background (0.598) | -0.093 [-0.11, -0.08] | background (0.598) | -0.093 [-0.11, -0.08] |
| M3 s2 | opencv | R2wvsR4 | 0.999 [1.00, 1.00] | lapvar (0.774) | 0.225 [0.20, 0.26] | bytes (0.685) | 0.313 [0.28, 0.35] |
| M3 s2 | opencv | R0->R2w | 0.624 [0.61, 0.64] | band (0.858) | -0.235 [-0.26, -0.21] | bytes (0.637) | -0.014 [-0.03, 0.00] |
| M3 s2 | opencv | R3->R4 | 0.781 [0.75, 0.81] | band (0.631) | 0.150 [0.10, 0.21] | background (0.597) | 0.184 [0.14, 0.23] |
| M3 s2 | opencv | R2w4vsR4 | 0.999 [1.00, 1.00] | lapvar (0.768) | 0.230 [0.20, 0.26] | bytes (0.682) | 0.317 [0.29, 0.35] |
| M3 s2 | opencv | R2wvsR2w4 | 0.514 [0.51, 0.52] | background (0.570) | -0.057 [-0.08, -0.04] | background (0.570) | -0.057 [-0.08, -0.04] |
| M3 s2 | facemorpher | R2wvsR4 | 0.999 [1.00, 1.00] | band (0.756) | 0.243 [0.21, 0.28] | bytes (0.687) | 0.312 [0.28, 0.34] |
| M3 s2 | facemorpher | R0->R2w | 0.549 [0.54, 0.56] | band (0.719) | -0.170 [-0.19, -0.15] | bytes (0.575) | -0.026 [-0.04, -0.02] |
| M3 s2 | facemorpher | R3->R4 | 0.783 [0.75, 0.81] | band (0.622) | 0.160 [0.10, 0.22] | background (0.621) | 0.162 [0.12, 0.21] |
| M3 s2 | facemorpher | R2w4vsR4 | 0.999 [1.00, 1.00] | band (0.762) | 0.236 [0.20, 0.27] | bytes (0.685) | 0.314 [0.28, 0.35] |
| M3 s2 | facemorpher | R2wvsR2w4 | 0.519 [0.51, 0.52] | background (0.598) | -0.079 [-0.10, -0.06] | background (0.598) | -0.079 [-0.10, -0.06] |
| M3 s3 | opencv | R2wvsR4 | 1.000 [1.00, 1.00] | lapvar (0.774) | 0.226 [0.20, 0.26] | bytes (0.685) | 0.314 [0.28, 0.35] |
| M3 s3 | opencv | R0->R2w | 0.603 [0.59, 0.62] | band (0.858) | -0.255 [-0.28, -0.23] | bytes (0.637) | -0.034 [-0.05, -0.02] |
| M3 s3 | opencv | R3->R4 | 0.772 [0.74, 0.80] | band (0.631) | 0.141 [0.09, 0.19] | background (0.597) | 0.175 [0.13, 0.22] |
| M3 s3 | opencv | R2w4vsR4 | 1.000 [1.00, 1.00] | lapvar (0.768) | 0.231 [0.20, 0.26] | bytes (0.682) | 0.318 [0.29, 0.35] |
| M3 s3 | opencv | R2wvsR2w4 | 0.509 [0.50, 0.52] | background (0.570) | -0.062 [-0.08, -0.04] | background (0.570) | -0.062 [-0.08, -0.04] |
| M3 s3 | facemorpher | R2wvsR4 | 1.000 [1.00, 1.00] | band (0.756) | 0.244 [0.21, 0.28] | bytes (0.687) | 0.313 [0.28, 0.34] |
| M3 s3 | facemorpher | R0->R2w | 0.536 [0.53, 0.54] | band (0.719) | -0.184 [-0.20, -0.16] | bytes (0.575) | -0.039 [-0.05, -0.03] |
| M3 s3 | facemorpher | R3->R4 | 0.770 [0.74, 0.80] | band (0.622) | 0.148 [0.10, 0.20] | background (0.621) | 0.149 [0.10, 0.19] |
| M3 s3 | facemorpher | R2w4vsR4 | 1.000 [1.00, 1.00] | band (0.762) | 0.237 [0.20, 0.27] | bytes (0.685) | 0.315 [0.28, 0.35] |
| M3 s3 | facemorpher | R2wvsR2w4 | 0.508 [0.50, 0.51] | background (0.598) | -0.090 [-0.11, -0.07] | background (0.598) | -0.090 [-0.11, -0.07] |
| M3 s4 | opencv | R2wvsR4 | 0.999 [1.00, 1.00] | lapvar (0.774) | 0.225 [0.20, 0.26] | bytes (0.685) | 0.314 [0.28, 0.35] |
| M3 s4 | opencv | R0->R2w | 0.692 [0.67, 0.71] | band (0.858) | -0.166 [-0.18, -0.15] | bytes (0.637) | 0.055 [0.04, 0.07] |
| M3 s4 | opencv | R3->R4 | 0.758 [0.72, 0.79] | band (0.631) | 0.127 [0.07, 0.18] | background (0.597) | 0.161 [0.11, 0.21] |
| M3 s4 | opencv | R2w4vsR4 | 0.999 [1.00, 1.00] | lapvar (0.768) | 0.231 [0.20, 0.26] | bytes (0.682) | 0.317 [0.29, 0.35] |
| M3 s4 | opencv | R2wvsR2w4 | 0.512 [0.50, 0.52] | background (0.570) | -0.059 [-0.08, -0.04] | background (0.570) | -0.059 [-0.08, -0.04] |
| M3 s4 | facemorpher | R2wvsR4 | 0.999 [1.00, 1.00] | band (0.756) | 0.243 [0.21, 0.28] | bytes (0.687) | 0.312 [0.28, 0.34] |
| M3 s4 | facemorpher | R0->R2w | 0.577 [0.57, 0.59] | band (0.719) | -0.142 [-0.16, -0.12] | bytes (0.575) | 0.002 [-0.01, 0.01] |
| M3 s4 | facemorpher | R3->R4 | 0.758 [0.72, 0.79] | band (0.622) | 0.135 [0.08, 0.19] | background (0.621) | 0.137 [0.09, 0.18] |
| M3 s4 | facemorpher | R2w4vsR4 | 0.999 [1.00, 1.00] | band (0.762) | 0.236 [0.20, 0.27] | bytes (0.685) | 0.314 [0.28, 0.35] |
| M3 s4 | facemorpher | R2wvsR2w4 | 0.505 [0.50, 0.51] | background (0.598) | -0.093 [-0.11, -0.08] | background (0.598) | -0.093 [-0.11, -0.08] |
| M3 s5 | opencv | R2wvsR4 | 0.994 [0.99, 1.00] | lapvar (0.774) | 0.220 [0.19, 0.25] | bytes (0.685) | 0.309 [0.28, 0.34] |
| M3 s5 | opencv | R0->R2w | 0.665 [0.65, 0.68] | band (0.858) | -0.193 [-0.21, -0.17] | bytes (0.637) | 0.027 [0.01, 0.04] |
| M3 s5 | opencv | R3->R4 | 0.767 [0.73, 0.80] | band (0.631) | 0.137 [0.08, 0.20] | background (0.597) | 0.170 [0.12, 0.22] |
| M3 s5 | opencv | R2w4vsR4 | - - | lapvar (0.768) | - - | bytes (0.682) | - - |
| M3 s5 | opencv | R2wvsR2w4 | - - | background (0.570) | - - | background (0.570) | - - |
| M3 s5 | facemorpher | R2wvsR4 | 0.995 [0.99, 1.00] | band (0.756) | 0.240 [0.21, 0.28] | bytes (0.687) | 0.309 [0.28, 0.34] |
| M3 s5 | facemorpher | R0->R2w | 0.563 [0.55, 0.57] | band (0.719) | -0.157 [-0.18, -0.14] | bytes (0.575) | -0.012 [-0.02, -0.00] |
| M3 s5 | facemorpher | R3->R4 | 0.779 [0.75, 0.81] | band (0.622) | 0.157 [0.10, 0.21] | background (0.621) | 0.158 [0.11, 0.20] |
| M3 s5 | facemorpher | R2w4vsR4 | - - | band (0.762) | - - | bytes (0.685) | - - |
| M3 s5 | facemorpher | R2wvsR2w4 | - - | background (0.598) | - - | background (0.598) | - - |
| M3 s6 | opencv | R2wvsR4 | 0.998 [1.00, 1.00] | lapvar (0.774) | 0.224 [0.20, 0.26] | bytes (0.685) | 0.313 [0.28, 0.34] |
| M3 s6 | opencv | R0->R2w | 0.636 [0.62, 0.65] | band (0.858) | -0.222 [-0.24, -0.20] | bytes (0.637) | -0.001 [-0.02, 0.02] |
| M3 s6 | opencv | R3->R4 | 0.777 [0.74, 0.81] | band (0.631) | 0.146 [0.09, 0.20] | background (0.597) | 0.180 [0.13, 0.23] |
| M3 s6 | opencv | R2w4vsR4 | - - | lapvar (0.768) | - - | bytes (0.682) | - - |
| M3 s6 | opencv | R2wvsR2w4 | - - | background (0.570) | - - | background (0.570) | - - |
| M3 s6 | facemorpher | R2wvsR4 | 0.999 [1.00, 1.00] | band (0.756) | 0.243 [0.21, 0.28] | bytes (0.687) | 0.312 [0.28, 0.34] |
| M3 s6 | facemorpher | R0->R2w | 0.550 [0.54, 0.56] | band (0.719) | -0.169 [-0.19, -0.15] | bytes (0.575) | -0.024 [-0.04, -0.01] |
| M3 s6 | facemorpher | R3->R4 | 0.781 [0.75, 0.82] | band (0.622) | 0.159 [0.10, 0.22] | background (0.621) | 0.160 [0.11, 0.21] |
| M3 s6 | facemorpher | R2w4vsR4 | - - | band (0.762) | - - | bytes (0.685) | - - |
| M3 s6 | facemorpher | R2wvsR2w4 | - - | background (0.598) | - - | background (0.598) | - - |
| M3 s7 | opencv | R2wvsR4 | 0.998 [0.99, 1.00] | lapvar (0.774) | 0.224 [0.19, 0.26] | bytes (0.685) | 0.313 [0.28, 0.34] |
| M3 s7 | opencv | R0->R2w | 0.643 [0.63, 0.66] | band (0.858) | -0.215 [-0.23, -0.20] | bytes (0.637) | 0.006 [-0.01, 0.02] |
| M3 s7 | opencv | R3->R4 | 0.765 [0.73, 0.80] | band (0.631) | 0.134 [0.08, 0.19] | background (0.597) | 0.168 [0.12, 0.21] |
| M3 s7 | opencv | R2w4vsR4 | - - | lapvar (0.768) | - - | bytes (0.682) | - - |
| M3 s7 | opencv | R2wvsR2w4 | - - | background (0.570) | - - | background (0.570) | - - |
| M3 s7 | facemorpher | R2wvsR4 | 0.998 [1.00, 1.00] | band (0.756) | 0.242 [0.21, 0.28] | bytes (0.687) | 0.311 [0.28, 0.34] |
| M3 s7 | facemorpher | R0->R2w | 0.559 [0.55, 0.57] | band (0.719) | -0.160 [-0.18, -0.14] | bytes (0.575) | -0.016 [-0.03, -0.01] |
| M3 s7 | facemorpher | R3->R4 | 0.763 [0.73, 0.80] | band (0.622) | 0.140 [0.09, 0.19] | background (0.621) | 0.142 [0.09, 0.19] |
| M3 s7 | facemorpher | R2w4vsR4 | - - | band (0.762) | - - | bytes (0.685) | - - |
| M3 s7 | facemorpher | R2wvsR2w4 | - - | background (0.598) | - - | background (0.598) | - - |
| M3 s8 | opencv | R2wvsR4 | 0.999 [1.00, 1.00] | lapvar (0.774) | 0.225 [0.20, 0.26] | bytes (0.685) | 0.314 [0.28, 0.35] |
| M3 s8 | opencv | R0->R2w | 0.568 [0.56, 0.58] | band (0.858) | -0.290 [-0.31, -0.27] | bytes (0.637) | -0.069 [-0.09, -0.05] |
| M3 s8 | opencv | R3->R4 | 0.768 [0.73, 0.80] | band (0.631) | 0.138 [0.09, 0.19] | background (0.597) | 0.171 [0.12, 0.22] |
| M3 s8 | opencv | R2w4vsR4 | 0.999 [1.00, 1.00] | lapvar (0.768) | 0.231 [0.20, 0.26] | bytes (0.682) | 0.317 [0.29, 0.35] |
| M3 s8 | opencv | R2wvsR2w4 | 0.505 [0.50, 0.51] | background (0.570) | -0.066 [-0.09, -0.05] | background (0.570) | -0.066 [-0.09, -0.05] |
| M3 s8 | facemorpher | R2wvsR4 | 0.999 [1.00, 1.00] | band (0.756) | 0.244 [0.21, 0.28] | bytes (0.687) | 0.313 [0.28, 0.34] |
| M3 s8 | facemorpher | R0->R2w | 0.533 [0.53, 0.54] | band (0.719) | -0.186 [-0.21, -0.17] | bytes (0.575) | -0.042 [-0.05, -0.03] |
| M3 s8 | facemorpher | R3->R4 | 0.773 [0.74, 0.80] | band (0.622) | 0.151 [0.10, 0.20] | background (0.621) | 0.152 [0.10, 0.20] |
| M3 s8 | facemorpher | R2w4vsR4 | 0.999 [1.00, 1.00] | band (0.762) | 0.237 [0.20, 0.27] | bytes (0.685) | 0.314 [0.28, 0.35] |
| M3 s8 | facemorpher | R2wvsR2w4 | 0.504 [0.50, 0.51] | background (0.598) | -0.094 [-0.11, -0.08] | background (0.598) | -0.094 [-0.11, -0.08] |

#### Extra warp contrasts (primary pool)

| Detector | tool | R0 vs R2w4 | R2w vs R2w4 | R2w4 vs R4 | R3m vs R3 |
|---|---|---|---|---|---|
| SelfMAD | opencv | 0.715 [0.70, 0.73] | 0.508 [0.50, 0.52] | 0.959 [0.95, 0.97] | 0.520 [0.50, 0.55] |
| SelfMAD | facemorpher | 0.664 [0.65, 0.68] | 0.515 [0.50, 0.53] | 0.981 [0.97, 0.99] | 0.553 [0.53, 0.58] |
| MADation ViT-B/16 | opencv | 0.561 [0.55, 0.58] | 0.494 [0.48, 0.51] | 0.986 [0.98, 0.99] | 0.550 [0.53, 0.57] |
| MADation ViT-B/16 | facemorpher | 0.503 [0.49, 0.52] | 0.491 [0.48, 0.50] | 0.984 [0.97, 0.99] | 0.572 [0.55, 0.59] |
| MADation ViT-L/14 | opencv | 0.415 [0.40, 0.43] | 0.489 [0.48, 0.50] | 0.992 [0.98, 1.00] | 0.624 [0.60, 0.65] |
| MADation ViT-L/14 | facemorpher | 0.454 [0.44, 0.47] | 0.490 [0.48, 0.50] | 0.994 [0.99, 1.00] | 0.635 [0.61, 0.66] |
| MixFaceNet-MAD | opencv | 0.587 [0.58, 0.60] | 0.499 [0.49, 0.51] | 0.889 [0.86, 0.91] | 0.473 [0.46, 0.49] |
| MixFaceNet-MAD | facemorpher | 0.521 [0.51, 0.53] | 0.493 [0.49, 0.50] | 0.903 [0.88, 0.92] | 0.475 [0.46, 0.49] |
| M3 s1 | opencv | 0.652 [0.64, 0.67] | 0.509 [0.50, 0.52] | 0.998 [1.00, 1.00] | 0.579 [0.55, 0.60] |
| M3 s1 | facemorpher | 0.556 [0.55, 0.57] | 0.505 [0.50, 0.51] | 0.998 [0.99, 1.00] | 0.602 [0.58, 0.63] |
| M3 s2 | opencv | 0.635 [0.62, 0.65] | 0.514 [0.51, 0.52] | 0.999 [1.00, 1.00] | 0.440 [0.41, 0.47] |
| M3 s2 | facemorpher | 0.567 [0.56, 0.58] | 0.519 [0.51, 0.52] | 0.999 [1.00, 1.00] | 0.459 [0.43, 0.49] |
| M3 s3 | opencv | 0.613 [0.60, 0.63] | 0.509 [0.50, 0.52] | 1.000 [1.00, 1.00] | 0.550 [0.52, 0.58] |
| M3 s3 | facemorpher | 0.543 [0.54, 0.55] | 0.508 [0.50, 0.51] | 1.000 [1.00, 1.00] | 0.575 [0.55, 0.60] |
| M3 s4 | opencv | 0.702 [0.68, 0.72] | 0.512 [0.50, 0.52] | 0.999 [1.00, 1.00] | 0.582 [0.56, 0.61] |
| M3 s4 | facemorpher | 0.581 [0.57, 0.59] | 0.505 [0.50, 0.51] | 0.999 [1.00, 1.00] | 0.590 [0.57, 0.62] |
| M3 s5 | opencv | - | - | - | 0.576 [0.55, 0.60] |
| M3 s5 | facemorpher | - | - | - | 0.594 [0.57, 0.62] |
| M3 s6 | opencv | - | - | - | 0.571 [0.54, 0.60] |
| M3 s6 | facemorpher | - | - | - | 0.597 [0.57, 0.63] |
| M3 s7 | opencv | - | - | - | 0.536 [0.51, 0.56] |
| M3 s7 | facemorpher | - | - | - | 0.561 [0.54, 0.59] |
| M3 s8 | opencv | 0.572 [0.56, 0.59] | 0.505 [0.50, 0.51] | 0.999 [1.00, 1.00] | 0.511 [0.49, 0.54] |
| M3 s8 | facemorpher | 0.536 [0.53, 0.55] | 0.504 [0.50, 0.51] | 0.999 [1.00, 1.00] | 0.535 [0.51, 0.56] |

#### Sensitivity without the 8 validation-reserved hosts (primary, ladder B)

| Detector | tool | R2w vs R4 all | without 8 | R0 vs R4 all | without 8 |
|---|---|---|---|---|---|
| SelfMAD | opencv | 0.966 | 0.967 [0.96, 0.98] | 0.986 | 0.986 |
| SelfMAD | facemorpher | 0.984 | 0.984 [0.98, 0.99] | 0.992 | 0.992 |
| MADation ViT-B/16 | opencv | 0.986 | 0.985 [0.98, 0.99] | 0.990 | 0.990 |
| MADation ViT-B/16 | facemorpher | 0.984 | 0.984 [0.97, 0.99] | 0.987 | 0.987 |
| MADation ViT-L/14 | opencv | 0.992 | 0.991 [0.98, 1.00] | 0.991 | 0.991 |
| MADation ViT-L/14 | facemorpher | 0.994 | 0.994 [0.99, 1.00] | 0.993 | 0.993 |
| MixFaceNet-MAD | opencv | 0.890 | 0.889 [0.86, 0.91] | 0.928 | 0.927 |
| MixFaceNet-MAD | facemorpher | 0.901 | 0.900 [0.88, 0.92] | 0.914 | 0.913 |
| M3 s1 | opencv | 0.998 | 0.998 [1.00, 1.00] | 0.999 | 0.999 |
| M3 s1 | facemorpher | 0.998 | 0.998 [1.00, 1.00] | 0.998 | 0.998 |
| M3 s2 | opencv | 0.999 | 0.999 [1.00, 1.00] | 0.999 | 0.999 |
| M3 s2 | facemorpher | 0.999 | 0.999 [1.00, 1.00] | 0.999 | 0.999 |
| M3 s3 | opencv | 1.000 | 1.000 [1.00, 1.00] | 1.000 | 1.000 |
| M3 s3 | facemorpher | 1.000 | 1.000 [1.00, 1.00] | 1.000 | 1.000 |
| M3 s4 | opencv | 0.999 | 0.999 [1.00, 1.00] | 0.999 | 0.999 |
| M3 s4 | facemorpher | 0.999 | 0.999 [1.00, 1.00] | 0.999 | 0.999 |
| M3 s5 | opencv | 0.994 | 0.994 [0.99, 1.00] | 0.995 | 0.995 |
| M3 s5 | facemorpher | 0.995 | 0.996 [0.99, 1.00] | 0.996 | 0.996 |
| M3 s6 | opencv | 0.998 | 0.998 [1.00, 1.00] | 0.999 | 0.999 |
| M3 s6 | facemorpher | 0.999 | 0.999 [1.00, 1.00] | 0.999 | 0.999 |
| M3 s7 | opencv | 0.998 | 0.998 [0.99, 1.00] | 0.998 | 0.998 |
| M3 s7 | facemorpher | 0.998 | 0.998 [1.00, 1.00] | 0.998 | 0.998 |
| M3 s8 | opencv | 0.999 | 0.999 [1.00, 1.00] | 0.999 | 0.999 |
| M3 s8 | facemorpher | 0.999 | 1.000 [1.00, 1.00] | 0.999 | 1.000 |

#### Flag rates at the detector's FRLL benchmark EER threshold (neutral genuine), primary pool

| Detector | tool | bench EER | R0 | R2w | R3 (twin) | R3m | R2w4 | R4 |
|---|---|---|---|---|---|---|---|---|
| SelfMAD | opencv | 0.08 | 25.4% [21.7, 29.3] | 53.5% [49.2, 57.8] | 99.6% [98.7, 100.0] | 99.4% [98.4, 99.9] | 53.7% [49.4, 58.0] | 100.0% [99.3, 100.0] |
| SelfMAD | facemorpher | 0.12 | 46.6% [42.4, 51.0] | 67.2% [63.0, 71.1] | 100.0% [99.3, 100.0] | 100.0% [99.3, 100.0] | 68.8% [64.7, 72.7] | 100.0% [99.3, 100.0] |
| MADation ViT-B/16 | opencv | 1.72 | 3.7% [2.3, 5.7] | 5.2% [3.5, 7.5] | 78.7% [75.0, 82.1] | 86.0% [82.8, 88.8] | 4.5% [2.9, 6.6] | 93.8% [91.5, 95.7] |
| MADation ViT-B/16 | facemorpher | 0.98 | 3.0% [1.7, 4.8] | 3.9% [2.4, 5.9] | 72.8% [68.8, 76.5] | 82.3% [78.8, 85.4] | 3.7% [2.3, 5.7] | 91.8% [89.1, 94.0] |
| MADation ViT-L/14 | opencv | 2.78 | 1.1% [0.4, 2.4] | 1.3% [0.5, 2.7] | 66.8% [62.6, 70.8] | 81.3% [77.8, 84.6] | 1.5% [0.6, 2.9] | 93.8% [91.5, 95.7] |
| MADation ViT-L/14 | facemorpher | 0.98 | 1.1% [0.4, 2.4] | 0.9% [0.3, 2.2] | 72.0% [68.0, 75.8] | 87.5% [84.4, 90.2] | 1.5% [0.6, 2.9] | 96.1% [94.1, 97.6] |
| MixFaceNet-MAD | opencv | 4.01 | 15.1% [12.2, 18.4] | 24.1% [20.5, 27.9] | 69.8% [65.7, 73.6] | 65.3% [61.1, 69.3] | 23.3% [19.8, 27.1] | 85.4% [82.2, 88.3] |
| MixFaceNet-MAD | facemorpher | 2.94 | 12.5% [9.8, 15.6] | 13.8% [11.0, 17.0] | 64.0% [59.8, 68.1] | 59.7% [55.4, 63.9] | 13.6% [10.8, 16.8] | 75.9% [72.1, 79.5] |
| M3 s1 | opencv | 0.08 | 1.1% [0.4, 2.4] | 1.7% [0.8, 3.2] | 81.3% [77.8, 84.6] | 89.0% [86.0, 91.5] | 1.7% [0.8, 3.2] | 98.7% [97.3, 99.5] |
| M3 s1 | facemorpher | 0.08 | 2.2% [1.2, 3.9] | 3.2% [1.9, 5.0] | 84.7% [81.4, 87.6] | 91.8% [89.1, 94.0] | 3.4% [2.0, 5.3] | 98.7% [97.3, 99.5] |
| M3 s2 | opencv | 1.15 | 3.4% [2.0, 5.3] | 5.8% [4.0, 8.1] | 99.4% [98.4, 99.9] | 99.1% [97.8, 99.7] | 7.5% [5.4, 10.0] | 100.0% [99.3, 100.0] |
| M3 s2 | facemorpher | 1.96 | 3.7% [2.3, 5.7] | 6.2% [4.3, 8.5] | 99.3% [98.1, 99.8] | 99.4% [98.4, 99.9] | 7.6% [5.5, 10.2] | 100.0% [99.3, 100.0] |
| M3 s3 | opencv | 0.12 | 3.9% [2.4, 5.9] | 6.0% [4.1, 8.3] | 98.7% [97.3, 99.5] | 99.1% [97.8, 99.7] | 6.2% [4.3, 8.5] | 100.0% [99.3, 100.0] |
| M3 s3 | facemorpher | 0.98 | 5.8% [4.0, 8.1] | 6.5% [4.6, 9.0] | 98.7% [97.3, 99.5] | 98.9% [97.6, 99.6] | 7.1% [5.1, 9.6] | 100.0% [99.3, 100.0] |
| M3 s4 | opencv | 0.82 | 1.3% [0.5, 2.7] | 1.9% [0.9, 3.4] | 85.1% [81.8, 88.0] | 94.4% [92.1, 96.2] | 1.9% [0.9, 3.4] | 98.9% [97.6, 99.6] |
| M3 s4 | facemorpher | 1.88 | 1.7% [0.8, 3.2] | 1.9% [0.9, 3.4] | 85.4% [82.2, 88.3] | 93.5% [91.0, 95.4] | 1.9% [0.9, 3.4] | 99.1% [97.8, 99.7] |
| M3 s5 | opencv | 0.86 | 1.1% [0.4, 2.4] | 2.2% [1.2, 3.9] | 66.4% [62.2, 70.4] | 76.7% [72.9, 80.2] | - | 96.1% [94.1, 97.6] |
| M3 s5 | facemorpher | 0.20 | 0.9% [0.3, 2.2] | 1.9% [0.9, 3.4] | 67.2% [63.0, 71.1] | 81.2% [77.6, 84.4] | - | 95.9% [93.9, 97.4] |
| M3 s6 | opencv | 2.94 | 0.7% [0.2, 1.9] | 0.7% [0.2, 1.9] | 73.5% [69.6, 77.2] | 83.6% [80.2, 86.6] | - | 97.4% [95.7, 98.6] |
| M3 s6 | facemorpher | 4.78 | 0.9% [0.3, 2.2] | 0.7% [0.2, 1.9] | 78.5% [74.8, 81.9] | 89.6% [86.6, 92.0] | - | 97.2% [95.4, 98.4] |
| M3 s7 | opencv | 0.98 | 1.7% [0.8, 3.2] | 1.9% [0.9, 3.4] | 92.4% [89.8, 94.5] | 94.4% [92.1, 96.2] | - | 99.8% [99.0, 100.0] |
| M3 s7 | facemorpher | 0.98 | 2.1% [1.0, 3.6] | 2.1% [1.0, 3.6] | 92.7% [90.2, 94.8] | 95.0% [92.8, 96.7] | - | 99.8% [99.0, 100.0] |
| M3 s8 | opencv | 1.84 | 0.9% [0.3, 2.2] | 0.9% [0.3, 2.2] | 85.8% [82.6, 88.7] | 89.0% [86.0, 91.5] | 1.3% [0.5, 2.7] | 99.3% [98.1, 99.8] |
| M3 s8 | facemorpher | 1.06 | 0.9% [0.3, 2.2] | 0.9% [0.3, 2.2] | 87.1% [84.0, 89.8] | 89.9% [87.1, 92.3] | 0.9% [0.3, 2.2] | 99.1% [97.8, 99.7] |

#### FRLL benchmark side and bridge

| Detector | tool | genuine | R4pub vs R0raw | R1f (E7) vs R0f | R4f vs R0f | E7 share | bench EER | bridge pub vs ours [CI] | detect pub / ours |
|---|---|---|---|---|---|---|---|---|---|
| SelfMAD | opencv | neutral_only | 0.999 [1.00, 1.00] | 0.949 [0.92, 0.97] | 0.999 [1.00, 1.00] | 0.63 | 0.08 | 0.519 [0.47, 0.57] | 1.00 / 1.00 |
| SelfMAD | opencv | all_photos | 0.999 [1.00, 1.00] | 0.929 [0.91, 0.95] | 0.999 [1.00, 1.00] | 0.57 | 0.08 |  |  |
| SelfMAD | facemorpher | neutral_only | 0.999 [1.00, 1.00] | 0.920 [0.89, 0.95] | 0.999 [1.00, 1.00] | 0.54 | 0.12 | 0.239 [0.19, 0.28] | 1.00 / 1.00 |
| SelfMAD | facemorpher | all_photos | 0.999 [1.00, 1.00] | 0.899 [0.87, 0.93] | 0.999 [1.00, 1.00] | 0.50 | 0.94 |  |  |
| MADation ViT-B/16 | opencv | neutral_only | 0.998 [1.00, 1.00] | 0.753 [0.72, 0.80] | 0.999 [1.00, 1.00] | 0.27 | 1.72 | 0.333 [0.29, 0.36] | 0.99 / 0.99 |
| MADation ViT-B/16 | opencv | all_photos | 0.999 [1.00, 1.00] | 0.771 [0.74, 0.80] | 0.999 [1.00, 1.00] | 0.29 | 0.98 |  |  |
| MADation ViT-B/16 | facemorpher | neutral_only | 0.999 [1.00, 1.00] | 0.725 [0.69, 0.77] | 0.999 [1.00, 1.00] | 0.23 | 0.98 | 0.448 [0.39, 0.50] | 0.99 / 0.99 |
| MADation ViT-B/16 | facemorpher | all_photos | 1.000 [1.00, 1.00] | 0.742 [0.72, 0.77] | 1.000 [1.00, 1.00] | 0.25 | 0.57 |  |  |
| MADation ViT-L/14 | opencv | neutral_only | 0.991 [0.98, 1.00] | 0.376 [0.34, 0.40] | 0.999 [1.00, 1.00] | -0.12 | 2.78 | 0.417 [0.38, 0.45] | 0.97 / 0.99 |
| MADation ViT-L/14 | opencv | all_photos | 0.995 [0.99, 1.00] | 0.465 [0.45, 0.48] | 0.999 [1.00, 1.00] | -0.03 | 2.49 |  |  |
| MADation ViT-L/14 | facemorpher | neutral_only | 0.998 [0.99, 1.00] | 0.381 [0.35, 0.40] | 1.000 [1.00, 1.00] | -0.12 | 0.98 | 0.382 [0.33, 0.43] | 0.99 / 0.99 |
| MADation ViT-L/14 | facemorpher | all_photos | 0.999 [1.00, 1.00] | 0.465 [0.45, 0.48] | 1.000 [1.00, 1.00] | -0.03 | 0.98 |  |  |
| MixFaceNet-MAD | opencv | neutral_only | 0.989 [0.98, 1.00] | 0.697 [0.67, 0.74] | 0.991 [0.98, 1.00] | 0.22 | 4.01 | 0.244 [0.21, 0.28] | 0.96 / 0.98 |
| MixFaceNet-MAD | opencv | all_photos | 0.988 [0.98, 1.00] | 0.707 [0.68, 0.74] | 0.992 [0.98, 1.00] | 0.23 | 4.01 |  |  |
| MixFaceNet-MAD | facemorpher | neutral_only | 0.993 [0.98, 1.00] | 0.670 [0.64, 0.71] | 0.989 [0.98, 1.00] | 0.19 | 2.94 | 0.563 [0.53, 0.60] | 0.97 / 0.97 |
| MixFaceNet-MAD | facemorpher | all_photos | 0.992 [0.98, 1.00] | 0.684 [0.66, 0.72] | 0.990 [0.98, 1.00] | 0.21 | 3.03 |  |  |
| M3 s1 | opencv | neutral_only | - | 0.725 [0.69, 0.76] | 1.000 [1.00, 1.00] | 0.23 | 0.08 |  |  |
| M3 s1 | opencv | all_photos | - | 0.716 [0.69, 0.74] | 1.000 [1.00, 1.00] | 0.22 | 0.08 |  |  |
| M3 s1 | facemorpher | neutral_only | - | 0.699 [0.67, 0.74] | 1.000 [1.00, 1.00] | 0.20 | 0.08 |  |  |
| M3 s1 | facemorpher | all_photos | - | 0.701 [0.68, 0.73] | 1.000 [1.00, 1.00] | 0.20 | 0.08 |  |  |
| M3 s2 | opencv | neutral_only | - | 0.701 [0.67, 0.74] | 0.999 [1.00, 1.00] | 0.20 | 1.15 |  |  |
| M3 s2 | opencv | all_photos | - | 0.701 [0.68, 0.73] | 0.999 [1.00, 1.00] | 0.20 | 1.47 |  |  |
| M3 s2 | facemorpher | neutral_only | - | 0.674 [0.65, 0.71] | 0.999 [1.00, 1.00] | 0.18 | 1.96 |  |  |
| M3 s2 | facemorpher | all_photos | - | 0.683 [0.66, 0.71] | 0.998 [1.00, 1.00] | 0.18 | 2.49 |  |  |
| M3 s3 | opencv | neutral_only | - | 0.648 [0.62, 0.68] | 1.000 [1.00, 1.00] | 0.15 | 0.12 |  |  |
| M3 s3 | opencv | all_photos | - | 0.666 [0.64, 0.69] | 1.000 [1.00, 1.00] | 0.17 | 0.49 |  |  |
| M3 s3 | facemorpher | neutral_only | - | 0.620 [0.60, 0.65] | 1.000 [1.00, 1.00] | 0.12 | 0.98 |  |  |
| M3 s3 | facemorpher | all_photos | - | 0.650 [0.63, 0.67] | 1.000 [1.00, 1.00] | 0.15 | 1.02 |  |  |
| M3 s4 | opencv | neutral_only | - | 0.735 [0.70, 0.78] | 1.000 [1.00, 1.00] | 0.24 | 0.82 |  |  |
| M3 s4 | opencv | all_photos | - | 0.742 [0.71, 0.78] | 1.000 [1.00, 1.00] | 0.25 | 1.39 |  |  |
| M3 s4 | facemorpher | neutral_only | - | 0.706 [0.68, 0.75] | 0.999 [1.00, 1.00] | 0.21 | 1.88 |  |  |
| M3 s4 | facemorpher | all_photos | - | 0.723 [0.70, 0.76] | 0.998 [1.00, 1.00] | 0.23 | 2.45 |  |  |
| M3 s5 | opencv | neutral_only | - | 0.784 [0.74, 0.83] | 1.000 [1.00, 1.00] | 0.30 | 0.86 |  |  |
| M3 s5 | opencv | all_photos | - | 0.726 [0.71, 0.75] | 1.000 [1.00, 1.00] | 0.23 | 0.49 |  |  |
| M3 s5 | facemorpher | neutral_only | - | 0.747 [0.71, 0.79] | 1.000 [1.00, 1.00] | 0.26 | 0.20 |  |  |
| M3 s5 | facemorpher | all_photos | - | 0.704 [0.69, 0.72] | 1.000 [1.00, 1.00] | 0.21 | 0.45 |  |  |
| M3 s6 | opencv | neutral_only | - | 0.703 [0.68, 0.74] | 0.998 [1.00, 1.00] | 0.21 | 2.94 |  |  |
| M3 s6 | opencv | all_photos | - | 0.705 [0.68, 0.73] | 0.998 [1.00, 1.00] | 0.21 | 2.90 |  |  |
| M3 s6 | facemorpher | neutral_only | - | 0.675 [0.65, 0.71] | 0.996 [0.99, 1.00] | 0.18 | 4.78 |  |  |
| M3 s6 | facemorpher | all_photos | - | 0.689 [0.67, 0.71] | 0.997 [0.99, 1.00] | 0.19 | 3.92 |  |  |
| M3 s7 | opencv | neutral_only | - | 0.707 [0.68, 0.75] | 1.000 [1.00, 1.00] | 0.21 | 0.98 |  |  |
| M3 s7 | opencv | all_photos | - | 0.710 [0.68, 0.74] | 1.000 [1.00, 1.00] | 0.21 | 1.39 |  |  |
| M3 s7 | facemorpher | neutral_only | - | 0.679 [0.65, 0.72] | 0.999 [1.00, 1.00] | 0.18 | 0.98 |  |  |
| M3 s7 | facemorpher | all_photos | - | 0.694 [0.67, 0.72] | 0.999 [1.00, 1.00] | 0.20 | 1.47 |  |  |
| M3 s8 | opencv | neutral_only | - | 0.719 [0.69, 0.76] | 0.999 [1.00, 1.00] | 0.22 | 1.84 |  |  |
| M3 s8 | opencv | all_photos | - | 0.745 [0.72, 0.77] | 1.000 [1.00, 1.00] | 0.26 | 0.98 |  |  |
| M3 s8 | facemorpher | neutral_only | - | 0.688 [0.66, 0.72] | 0.999 [1.00, 1.00] | 0.19 | 1.06 |  |  |
| M3 s8 | facemorpher | all_photos | - | 0.723 [0.70, 0.75] | 1.000 [1.00, 1.00] | 0.23 | 0.98 |  |  |

#### AR2 graded FaceMorpher mixing (300 hosts): mean logit per level, Page trend test, AUC vs m = 0

| Detector | mean logit m=0 / .1 / .2 / .3 / .4 / .5 | Page L, p | AUC(m vs 0) .1 / .2 / .3 / .4 / .5 |
|---|---|---|---|
| SelfMAD | -1.90 / 1.12 / 4.18 / 6.12 / 7.24 / 7.60 | 26834, 3.9e-273 | 0.801 / 0.945 / 0.978 / 0.987 / 0.989 |
| MADation ViT-B/16 | -11.86 / -11.38 / -8.61 / -3.31 / 1.92 / 4.26 | 26937, 6.4e-285 | 0.619 / 0.810 / 0.928 / 0.976 / 0.984 |
| MADation ViT-L/14 | -12.77 / -12.29 / -10.18 / -4.73 / 1.01 / 3.27 | 26671, 5.3e-255 | 0.511 / 0.775 / 0.927 / 0.983 / 0.992 |
| MixFaceNet-MAD | -13.09 / -9.43 / -6.61 / -4.50 / -3.02 / -2.53 | 26722, 1.3e-260 | 0.666 / 0.788 / 0.862 / 0.904 / 0.917 |
| M3 s1 | -3.43 / -2.89 / -1.15 / 1.47 / 2.71 / 2.94 | 27118, 3.2e-306 | 0.669 / 0.879 / 0.978 / 0.994 / 0.998 |
| M3 s2 | -3.58 / -2.14 / 1.05 / 2.84 / 3.23 / 3.29 | 27129, 1.5e-307 | 0.811 / 0.979 / 0.995 / 0.998 / 0.998 |
| M3 s3 | -3.65 / -2.93 / -0.13 / 2.35 / 3.15 / 3.29 | 27124, 6e-307 | 0.751 / 0.963 / 0.996 / 0.999 / 1.000 |
| M3 s4 | -3.16 / -2.35 / -0.01 / 2.36 / 3.07 / 3.16 | 27139, 9.5e-309 | 0.738 / 0.907 / 0.983 / 0.997 / 0.998 |
| M3 s5 | -3.40 / -3.03 / -1.64 / 0.62 / 2.13 / 2.50 | 27133, 5e-308 | 0.696 / 0.864 / 0.956 / 0.990 / 0.995 |
| M3 s6 | -3.46 / -2.85 / -0.55 / 2.07 / 2.92 / 3.07 | 27109, 3.8e-305 | 0.702 / 0.909 / 0.984 / 0.996 / 0.998 |
| M3 s7 | -3.59 / -3.07 / -0.71 / 1.89 / 2.91 / 3.10 | 27141, 5.4e-309 | 0.719 / 0.929 / 0.988 / 0.996 / 0.997 |
| M3 s8 | -3.67 / -3.44 / -1.86 / 0.66 / 2.19 / 2.51 | 27057, 5.8e-299 | 0.675 / 0.923 / 0.987 / 0.997 / 0.999 |

#### AR4 blanking (primary pool): AUC with background blanked / face blanked

| Detector | tool | variant | R2w vs R4 | R0 vs R4 | R3 vs R4 | R0 vs R2w | works? |
|---|---|---|---|---|---|---|---|
| SelfMAD | opencv | bg blanked | 0.901 [0.88, 0.92] | 0.950 [0.94, 0.96] | 0.661 [0.63, 0.70] | 0.695 [0.68, 0.71] | True |
| SelfMAD | facemorpher | bg blanked | 0.913 [0.90, 0.93] | 0.970 [0.96, 0.98] | 0.732 [0.70, 0.77] | 0.692 [0.68, 0.71] | True |
| SelfMAD | opencv | face blanked | 0.888 [0.86, 0.92] | 0.904 [0.87, 0.93] | 0.512 [0.47, 0.55] | 0.538 [0.53, 0.55] | True |
| SelfMAD | facemorpher | face blanked | 0.924 [0.90, 0.95] | 0.931 [0.91, 0.95] | 0.496 [0.46, 0.54] | 0.515 [0.51, 0.52] | True |
| MADation ViT-B/16 | opencv | bg blanked | 0.814 [0.79, 0.84] | 0.858 [0.84, 0.88] | 0.560 [0.52, 0.60] | 0.627 [0.61, 0.64] | True |
| MADation ViT-B/16 | facemorpher | bg blanked | 0.820 [0.80, 0.84] | 0.860 [0.84, 0.88] | 0.576 [0.54, 0.61] | 0.607 [0.59, 0.62] | True |
| MADation ViT-B/16 | opencv | face blanked | 0.912 [0.89, 0.93] | 0.934 [0.92, 0.95] | 0.604 [0.56, 0.64] | 0.589 [0.58, 0.60] | True |
| MADation ViT-B/16 | facemorpher | face blanked | 0.909 [0.89, 0.93] | 0.912 [0.89, 0.93] | 0.608 [0.57, 0.65] | 0.491 [0.48, 0.50] | True |
| MixFaceNet-MAD | opencv | bg blanked | 0.791 [0.76, 0.82] | 0.837 [0.81, 0.87] | 0.605 [0.57, 0.64] | 0.570 [0.56, 0.58] | True |
| MixFaceNet-MAD | facemorpher | bg blanked | 0.821 [0.79, 0.85] | 0.833 [0.80, 0.86] | 0.590 [0.55, 0.63] | 0.512 [0.50, 0.53] | True |
