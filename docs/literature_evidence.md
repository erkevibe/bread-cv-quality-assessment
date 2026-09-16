# Literature verification ledger

Science/TRIZ independently checked the 17 entries in `paper/references.bib` against DOI records
and primary publisher/dataset pages on 2026-09-16. Applied sources are primarily from 2022–2026;
older entries are primary sources for Otsu thresholding, Bland–Altman agreement, MobileNetV3,
and Random Forests. Reviews are used for context only, not as experimental evidence.

The closest precedent is Martínez-Lara et al. (2025), DOI
`10.1007/s44187-025-00568-3`: controlled RGB imaging, Gaussian blur, Otsu segmentation, OpenCV,
pixel-to-mm measurement, and error metrics for sliced bread. These operations are therefore a
baseline, not the novelty claim. This project's defensible contribution is the reproducible
automated batch workflow, learned physical calibration, leakage-safe grouped evaluation,
measurement-agreement analysis, and low computational cost.

Modality, bread type, camera geometry, reference scale, sample size, and target traits differ
across studies; published accuracy values are not transferred to this dataset.
