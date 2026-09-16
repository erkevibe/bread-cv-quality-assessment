# Experimental results

Run ID: `20260916T015000Z`. Dataset: `10.17632/f663p7c89m.1` version 1.

The audit found 173 CSV rows; 171 uniquely mapped width/height samples were eligible. The frozen split contains {'train': 119, 'test': 26, 'validation': 26}. Segmentation failures: 0.

## Model comparison on the untouched final test set

| method                 |   ('width', 'mae') |   ('width', 'rmse') |   ('width', 'r2') |   ('height', 'mae') |   ('height', 'rmse') |   ('height', 'r2') |
|:-----------------------|-------------------:|--------------------:|------------------:|--------------------:|---------------------:|-------------------:|
| hist_gradient_boosting |              2.103 |               3.122 |             0.694 |               2.4   |                3.016 |              0.847 |
| linear_calibration     |              4.553 |               5.36  |             0.097 |               3.002 |                3.683 |              0.772 |
| linear_regression      |              2.499 |               3.186 |             0.681 |               2.718 |                3.617 |              0.78  |
| mobilenet_v3_small     |              2.833 |               3.363 |             0.645 |               4.516 |                5.533 |              0.485 |
| random_forest          |              2.228 |               3.031 |             0.711 |               2.883 |                3.531 |              0.79  |
| ridge                  |              3.336 |               3.959 |             0.507 |               2.638 |                3.532 |              0.79  |

The method selected using validation MAE before opening final-test results was **hist_gradient_boosting**.

## Ablation

| feature_set   | target   |   mae |   rmse |    r2 |   mape |   n |
|:--------------|:---------|------:|-------:|------:|-------:|----:|
| pixels        | width    | 4.543 |  5.431 | 0.073 |  4.694 |  26 |
| pixels        | height   | 3.023 |  3.706 | 0.769 |  3.486 |  26 |
| morphology    | width    | 3.336 |  3.959 | 0.507 |  3.385 |  26 |
| morphology    | height   | 2.638 |  3.532 | 0.79  |  3.04  |  26 |

## Measurement agreement and paired errors

- Width: bias -0.031; 95% limits of agreement [-6.272, 6.209]; paired Wilcoxon versus linear calibration p=0.0001662.
- Height: bias 0.907; 95% limits of agreement [-4.842, 6.655]; paired Wilcoxon versus linear calibration p=0.1291.

## Computational cost

Mean classical image segmentation and feature extraction time was 4.25 ms/image (235.11 images/s) on the recorded CPU environment.

## Limitations

The CSV misspells `height` as `heigth` and does not encode measurement units. Values are reported as nominal millimetres because the experiment specification and measurement magnitudes support that interpretation, but the missing unit metadata is retained as a limitation. One duplicated filename with conflicting ground truth is excluded rather than repaired by assumption. Controlled imaging limits external validity; calibration is camera/setup-specific. Test segmentation failures, if any, are blocking rather than silently discarded. The CNN status is: `completed`.
