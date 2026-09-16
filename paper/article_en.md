# Automated Non-Contact Assessment of Bread Size and Shape from RGB Images Using Computer Vision

## Abstract

Manual dimensional inspection is difficult to scale in bakery quality control. This study
developed a fully automated and reproducible pipeline for estimating bread width and height and
for describing shape from ordinary RGB images. Mendeley Data version 1 (DOI
10.17632/f663p7c89m.1) was audited before modelling. Of 173 CSV rows, 171 uniquely mapped samples
were eligible after excluding conflicting or unmatched records, and a deterministic grouped
70/15/15 split protected the final test set. Bread was segmented with Gaussian smoothing, Otsu
thresholding, morphology, and contour validation. Validation-stage train-only pixel calibration was
compared with linear, ridge, random-forest, and histogram-gradient-boosting regression on
morphological features. The method selected on validation data was hist_gradient_boosting. On 26 untouched
test samples it achieved width MAE 2.10, height MAE 2.40, width RMSE 3.12,
height RMSE 3.02, and R² values of 0.694 and 0.847, respectively, in the
dataset's nominal millimetre unit. Classical processing required 3.4 ms/image on CPU.
The results establish a transparent low-cost baseline while exposing metadata, calibration, and
external-validity limitations.

**Keywords:** computer vision; bread quality; non-destructive measurement; image processing;
machine learning; measurement agreement; quality control

## 1. Introduction

Dimensions and visible shape are practical indicators of process consistency in bakery
production, yet manual caliper measurements are intermittent, labour-intensive, and difficult to
trace. RGB imaging offers inexpensive, non-contact acquisition and can run at line speed when the
view, illumination, and scale are controlled. Reviews of imaging for baked goods describe broad
use of colour, texture, size, and shape features, but also identify inconsistent acquisition and
limited reproducibility [16,17]. Recent bread studies already use Gaussian filtering, Otsu
thresholding, morphology, and OpenCV contours [2,5]; these operations are therefore a baseline,
not the claimed novelty.

Existing work ranges from sliced-bread dimensional analysis [2] and baguette geometry [3] to
sensory-trait prediction [4] and crumb-texture fingerprints [8]. Accuracy from those systems
cannot be transferred because bread type, camera geometry, labels, and reference scales differ.
The present contribution is an auditable batch workflow that links each image to instrument
measurements, freezes a group-safe test set, compares simple and learned physical calibration,
quantifies agreement, and reports CPU cost. The research question is whether this low-cost RGB
pipeline can estimate width and height with useful accuracy and whether morphology-based learning
reduces error relative to one-dimensional pixel calibration.

## 2. Materials and Methods

### 2.1 Dataset and audit

The public CC BY 4.0 dataset by Mora [1] was downloaded from its official versioned record and
kept outside Git. It contains `texture`, `color`, and `size` directories plus a semicolon-delimited
CSV using decimal commas. The published total of 1,635 images was not treated as the dimensional
sample count. The CSV has 173 rows and links one width/height view and one thickness view to each
record. A repeated filename carries conflicting labels; both conflicting rows were excluded
rather than silently corrected. This left 171 eligible physical sample identifiers. Source colour
crops and texture images were not mixed into the dimension experiment. The CSV does not state the
unit explicitly; values are treated as nominal millimetres and this uncertainty is preserved as
a limitation.

### 2.2 Segmentation and shape features

Each RGB image was converted to grayscale, smoothed with a Gaussian kernel, and thresholded by
Otsu's method [12]. Both threshold polarities were evaluated deterministically; morphological
opening and closing removed small artefacts, after which the largest valid contour was retained.
The implementation recorded failures, border contact, polarity, and processing time. Extracted
features were bounding-box width and height, contour area, perimeter, aspect ratio, circularity,
solidity, extent, equivalent diameter, and ellipse axes/eccentricity when defined. They are
quantitative descriptors; no unsupported good/bad shape class was created.

### 2.3 Splitting and models

Sample identifiers, rather than images, were assigned to 70% training, 15% validation, and 15%
test partitions with seed 42. Assertions require zero identifier overlap. Segmentation parameters
and method selection did not use test outcomes. Method A fitted separate linear transforms from
pixel width and height to physical targets using training data only. Method B compared ordinary
linear regression, ridge regression, Random Forests [15], and histogram gradient boosting on the
full morphology vector. A pre-specified ablation compared only width/height pixels against the
full feature set. Preprocessing and imputation were fitted inside each training pipeline.

### 2.4 Evaluation

Models were selected by mean validation MAE and then fitted on training plus validation data for a
single final-test evaluation. Width and height were scored separately using MAE, RMSE, MAPE where
defined, and R². MAE confidence intervals used deterministic bootstrap resampling. Absolute
errors were compared with paired Wilcoxon tests on identical samples. Because association is not
agreement, the selected method was also assessed using Bland--Altman mean bias and 95% limits of
agreement [13]. CPU timing includes segmentation and feature extraction after image loading.

## 3. Results and Discussion

The validation-selected method was **hist_gradient_boosting**. On 26 untouched test samples, width MAE and
RMSE were 2.10 and 3.12; height MAE and RMSE were 2.40 and 3.02.
The corresponding R² values were 0.694 for width and 0.847 for height. Full per-method
metrics, bootstrap intervals, predictions, ablation results, paired tests, and Bland--Altman
limits are generated from the same run in `reports/results.md` and `results/`. Classical image
processing averaged 3.4 ms/image on the recorded CPU environment. The lightweight image
regression status for this run was `completed`; no missing CNN result is represented as a
successful comparison.

Differences between width and height errors can arise from irregular crust boundaries,
orientation, and the fact that an axis-aligned bounding box responds to pose. Learned morphology
can capture area and compactness relationships that a one-dimensional calibration omits, but it
also remains tied to the acquisition booth and the observed bread families. Direct numerical
comparison with prior work would be misleading: the sliced-bread study [2], baguette system [3],
and RGB-D food systems [11] use different geometries and targets. The relevant advance is the
fully traced evaluation rather than an unsupported claim of universal superiority.

## 4. Conclusion

The study delivered a reproducible RGB workflow connecting dataset audit, automatic contour
measurement, leakage-safe calibration, compact regressors, agreement analysis, and CPU benchmarking.
The validation-selected hist_gradient_boosting model obtained test MAE of 2.10 for width and 2.40
for height in the nominal dataset unit. Practical deployment remains conditional on external
validation under new cameras, products, poses, and lighting; explicit reference geometry would
also remove ambiguity in physical units. Future work should validate the pipeline prospectively,
quantify instrument uncertainty, evaluate rotated geometries or learned segmentation, and test a
lightweight CNN only when effective sample size and compute support a defensible experiment.

## References

Verified bibliographic metadata and DOI values are provided in `references.bib`.
