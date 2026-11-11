# Hypotheses in plain terms

Author ruling, 11 Nov: a genuine image that was only processed is not a morph; a morph of two photos
of one person is a morph. So the main contrast everywhere is "processed genuine image against morph".
"Twin" tests (same-person morph against two-person morph) are the side study of whether a detector
reads the second identity.

Each has a test that can fail. Thresholds are fixed here, before any run. AUC = area under the ROC
curve (0.5 is chance). "Twin" = a one-identity image from the same pipeline as the morph, with the
same post-processing. "Held-out pipeline" = a generator never used in training.

## Audit side (why existing numbers are not about morphing)

**A1. A network can pass the diffusion benchmarks without ever seeing a morph.**
Train only on SMDD renders against their own shrunk copies (the registered A47 data). If it reaches the published error on FRLL diffusion morphs, those cells
do not measure morph detection.
Status: seen once (A47 I-3: 0.00% on MorDIFF). To do: repeat with a fixed checkpoint rule and a
working chance control.
Fails if: error above 15% in at least 3 of 5 seeds. Chance reference: five label-permuted networks and one untrained network.

**A2. Existing detectors cannot tell a morph from its twin.**
Score released detectors on morph-vs-twin sets for all three families (landmark, GAN, diffusion).
Status: GAN done (max AUC 0.59), diffusion done for one release. Landmark twins have never been built.
Read with the verdict rules of `11_AUDIT_PLAN.md` (no identity reading: below 0.60, upper bound below
0.65; identity reading: at least 0.75, lower bound above 0.65).

**A3. Their features do not contain the morph signal either.**
Refit only the last layer of each released detector on twin-balanced data.
Fails if: held-out twin AUC ≥ 0.65. (Then the features are fine and only the training data was at fault.
That is also a result.)

## Method side (can anything detect the morphing itself)

**M1. Landmark morphs leave a trace that one-identity warps do not.**
Blending two different faces leaves ghosting; blending two photos of one person leaves much less.
Train on morph-vs-self-morph pairs.
Two tiers. Signal: held-out-tool twin AUC with lower bound above 0.55. Method claim: AUC ≥ 0.80, with
the rejection rate of genuine images at 10% missed attacks reported. The 32-pixel thumbnail model is
reported beside it as a decomposition (an "average face" is partly visible at low resolution), not as
a kill rule.

**M2. Generator morphs (GAN, diffusion) carry an identity-mixing signal in one image.**
Same training, latent morphs against same-person latent blends.
Expected to be hard. Our zero-shot results predict failure.
Same two tiers as M1 on a held-out generator.

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
Descriptive, no pass rule: benchmark error on corrected MAD22 and FRLL, native and under E7, for the
twin-trained detector and the same backbone trained the usual way. If benchmarks reward cues, a
cue-free detector is expected to score worse on them; the size of that gap is itself a result.

**M6. The signal is a dose, not a switch.**
Predicted mixing fraction should climb smoothly from 0 to 0.5. A jump at the first step means the
network found a pipeline cue.
Fails if: rank correlation with the true fraction on a held-out pipeline is below 0.3.

## Guard hypotheses (things that would make a positive result worthless)

**G1. Pose gap.** Two photos of one person differ less in pose than photos of two people, so ghosting
size alone could separate the classes. Check: twins and morphs use the same kinds of photo (composition rule in `11_AUDIT_PLAN.md`); pairs
are binned by landmark distance. Pass: within every bin the detector beats "landmark distance only"
with a paired lower bound above 0.

**G2. History leak.** Frozen CLIP features always contain history, so the probe is on the score: the
score shift under the E7 control must be the same for morphs and twins (difference interval includes 0).

**G3. Identity leak.** No person may appear in both training and test, and every person must appear
under both labels inside a split.

**G4. Smoother output from interpolation.** A blend of two latents may be smoother than a single
reconstruction. Check with a frequency-only probe on twins; use same-person blends, not plain
reconstructions, as the main negatives.
