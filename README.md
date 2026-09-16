# Bread CV Quality Assessment

Reproducible research software for automated, non-contact estimation of bread width, height,
and quantitative shape characteristics from RGB images. The project compares a classical
pixel-to-millimetre calibration, regression on automatically extracted morphology, and an
optional lightweight MobileNetV3 image-regression baseline.

> Scientific status: results in this repository are generated from the pinned experiment and
> must not be interpreted until `reports/data_audit.md` confirms the image-to-sample mapping and
> the grouped split passes its leakage checks.

## Research objective

Can a fully automated, low-cost RGB computer-vision pipeline estimate bread dimensions with
useful agreement to instrument measurements, and does learned calibration improve upon simple
linear pixel-to-mm calibration?

## Dataset

The experiment uses Juan Mora, *A dataset containing images of bread crumb and crust, along with
measurements of size, color, and hardness*, Mendeley Data, version 1,
[DOI 10.17632/f663p7c89m.1](https://doi.org/10.17632/f663p7c89m.1).

The source dataset is distributed under CC BY 4.0 and is not included in this repository.
The required row-level final-test prediction table is a derived research result and retains the
dataset attribution; full manifests, features, inventories, and validation predictions are
generated locally and excluded from Git.
Follow [data/README.md](data/README.md) to obtain and unpack the official archive.

## Method

1. Audit every CSV field and image; establish a defensible physical `sample_id` mapping.
2. Freeze group-disjoint train/validation/test partitions (seed 42).
3. Segment bread using grayscale, Gaussian blur, Otsu thresholding, morphology, and the largest
   valid contour; compute geometric descriptors.
4. Fit validation candidates on train; after selection, refit classical models on train+validation.
5. Optionally train a frozen-backbone MobileNetV3-Small regression head.
6. Evaluate width and height using MAE, RMSE, R², bootstrap confidence intervals, paired tests,
   Bland–Altman agreement, and CPU inference timing.

The `color` crops are excluded from the size experiment unless the audit proves a safe grouped
relationship to their source images. Thickness is included only if a mapped view physically
contains that dimension.

## Installation

```bash
git clone https://github.com/erkevibe/bread-cv-quality-assessment.git
cd bread-cv-quality-assessment
uv sync --extra dev --extra cnn
```

Python 3.11 or 3.12 is required. The pinned experiment enables the CNN baseline. For a
classical-only development environment, first disable `models.cnn.enabled` in a copied config,
then install without the `cnn` extra:

```bash
uv sync --extra dev
```

## Data preparation

Download version 1 from the official Mendeley page and unpack it anywhere below `data/raw/`.
The pipeline discovers the single `Data.csv` recursively:

```bash
mkdir -p data/raw
# unpack the official archive into data/raw/
uv run python scripts/audit_dataset.py --config configs/experiment.yaml
```

The audit is intentionally a gate. Training refuses to proceed if a physical-sample mapping is
ambiguous or if any sample occurs in more than one split.

## Reproduce the experiment

```bash
make experiment
# equivalent:
uv run python scripts/run_all.py --config configs/experiment.yaml
```

The command produces the audit, canonical manifest, frozen split, features, model predictions,
metrics, statistical comparisons, no more than five figures, the results report, and both paper
drafts. It never downloads data implicitly and does not commit source images or learned weights.

## Word articles

The publication-ready Word versions are available as
[`paper/article_ru.docx`](paper/article_ru.docx) and
[`paper/article_en.docx`](paper/article_en.docx). They include the five generated figures,
summary tables, page headers and footers, and the verified 17-item bibliography.

Regenerate both documents after changing the Markdown articles, figures, or metrics:

```bash
make word
```

## Main results

<!-- GENERATED_RESULTS_START -->
Validation-selected method: **hist_gradient_boosting**; untouched test n=26.

| Target | MAE | RMSE | R² |
|:--|--:|--:|--:|
| Width | 2.103 | 3.122 | 0.694 |
| Height | 2.400 | 3.016 | 0.847 |

Classical CV processing: 4.25 ms/image. Values use the dataset's nominal unit; see the unit limitation in the report.
<!-- GENERATED_RESULTS_END -->

See `reports/results.md` for every model, confidence intervals, agreement analysis and
limitations. No numerical claim in this section is maintained by hand.

## Testing

```bash
make lint
make test
```

CI installs the lightweight dependency set and runs lint/unit tests; it does not download the
dataset or train models.

## Citation

Project citation metadata is in [CITATION.cff](CITATION.cff). Replace `AUTHOR_NAME`,
`AUTHOR_ORCID`, and `AFFILIATION` before a formal release. Dataset citation remains separate and
is recorded in `paper/references.bib`.

## License

Code is MIT licensed. Dataset files remain under CC BY 4.0 and are not redistributed here.
