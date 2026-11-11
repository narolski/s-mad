# Hypotheses in plain terms

Each has a test that can fail. Thresholds are fixed here, before any run. AUC = area under the ROC
curve (0.5 is chance). "Twin" = a one-identity image from the same pipeline as the morph, with the
same post-processing. "Held-out pipeline" = a generator never used in training.

## Audit side (why existing numbers are not about morphing)

**A1. A network can pass the diffusion benchmarks without ever seeing a morph.**
Train "render vs photo" only. If it reaches the published error on FRLL diffusion morphs, those cells
do not measure morph detection.
Status: seen once (A47 I-3: 0.00% on MorDIFF). To do: repeat with a fixed checkpoint rule and a
working chance control.
Fails if: error above 15% in 2 of 3 seeds.

**A2. Existing detectors cannot tell a morph from its twin.**
Score released detectors on morph-vs-twin sets for all three families (landmark, GAN, diffusion).
Status: GAN done (max AUC 0.59), diffusion done for one release. Landmark twins have never been built.
Fails if: a released detector reaches AUC ≥ 0.65 on twins of a family. That family is then excluded
from the shortcut claim.

**A3. Their features do not contain the morph signal either.**
Refit only the last layer of each released detector on twin-balanced data.
Fails if: held-out twin AUC ≥ 0.65. (Then the features are fine and only the training data was at fault.
That is also a result.)

## Method side (can anything detect the morphing itself)

**M1. Landmark morphs leave a trace that one-identity warps do not.**
Blending two different faces leaves ghosting; blending two photos of one person leaves much less.
Train on morph-vs-self-morph pairs.
Fails if: held-out-tool twin AUC < 0.60, or a 32-pixel thumbnail model comes within 0.03.

**M2. Generator morphs (GAN, diffusion) carry an identity-mixing signal in one image.**
Same training, latent morphs against same-person latent blends.
Expected to be hard. Our zero-shot results predict failure.
Fails if: held-out-generator twin AUC < 0.60.

**M3. A morph is a more "average" face, and that is measurable.**
The mean of two identity vectors is shorter than either: by a factor of about 0.71 for unrelated
people and 0.87 for look-alikes. So face-recognition feature norm and distance to the population
centre should shift.
Fails if: the score does not rise step by step with the mixing fraction (0, 0.1 … 0.5), or does not
fall as the two contributors become more similar.

**M4. A network can recover both contributors from one morph.**
A two-output head predicts two identity embeddings. If it works, the gap between them is the score,
and no file property can explain it.
Fails if: the two outputs find the true contributors in a 10,000-person gallery no better than the
morph's own embedding does.

**M5. Twin training does not cost benchmark accuracy.**
A detector trained with twins should stay within 2 points EER of the same backbone trained the usual
way on MAD22 and FRLL, while its error under the E7 control stops rising.
Fails if: benchmark error rises by more than 2 points, or the E7 rise stays above half of baseline.

**M6. The signal is a dose, not a switch.**
Predicted mixing fraction should climb smoothly from 0 to 0.5. A jump at the first step means the
network found a pipeline cue.
Fails if: rank correlation with the true fraction on a held-out pipeline is below 0.3.

## Guard hypotheses (things that would make a positive result worthless)

**G1. Pose gap.** Two photos of one person differ less in pose than photos of two people, so ghosting
size alone could separate the classes. Check: match pairs on head pose and landmark distance; report
AUC of "ghosting size only".

**G2. History leak.** A probe on the detector's features should not predict JPEG quality, source
resolution or generator above AUC 0.60.

**G3. Identity leak.** No person may appear in both training and test, and every person must appear
under both labels inside a split.

**G4. Smoother output from interpolation.** A blend of two latents may be smoother than a single
reconstruction. Check with a frequency-only probe on twins; use same-person blends, not plain
reconstructions, as the main negatives.
