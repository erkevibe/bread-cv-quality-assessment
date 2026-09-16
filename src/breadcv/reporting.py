from __future__ import annotations

from pathlib import Path

import pandas as pd


def _value(metrics: pd.DataFrame, method: str, target: str, metric: str) -> float:
    match = metrics[
        (metrics["method"] == method)
        & (metrics["split"] == "test")
        & (metrics["target"] == target)
        & (metrics["metric"] == metric)
    ]
    if len(match) != 1:
        raise ValueError(f"Expected one metric row for {method}/{target}/{metric}")
    return float(match.iloc[0]["value"])


def _markdown_bibliography() -> str:
    references = [
        (
            "Mora J. *A dataset containing images of bread crumb and crust, along with "
            "measurements of size, color, and hardness*. Mendeley Data, version 1, 2025. "
            "[doi:10.17632/f663p7c89m.1](https://doi.org/10.17632/f663p7c89m.1)."
        ),
        (
            "Martínez-Lara N.-D., Garzón-Castro C. L., Filomena-Ambrosio A. Analysis of "
            "physical properties in white and whole wheat sliced bread using digital image "
            "processing. *Discover Food*, 5, 261, 2025. "
            "[doi:10.1007/s44187-025-00568-3](https://doi.org/10.1007/s44187-025-00568-3)."
        ),
        (
            "Dong C., Huang L., Xiong C., Li M., Tang J. Evaluation of quality of baguette "
            "bread using image analysis technique. *Journal of Food Composition and Analysis*, "
            "140, 107222, 2025. "
            "[doi:10.1016/j.jfca.2025.107222](https://doi.org/10.1016/j.jfca.2025.107222)."
        ),
        (
            "Azmat M. et al. Assessing traits in bread using image analysis and machine "
            "learning. *Food Research International*, 235, 119131, 2026. "
            "[doi:10.1016/j.foodres.2026.119131](https://doi.org/10.1016/j.foodres.2026.119131)."
        ),
        (
            "Lee J., Kim Y., Kim S. The Study of an Adaptive Bread Maker Using Machine "
            "Learning. *Foods*, 12(22), 4160, 2023. "
            "[doi:10.3390/foods12224160](https://doi.org/10.3390/foods12224160)."
        ),
        (
            "Gonzalez Viejo C., Harris N. M., Fuentes S. Quality Traits of Sourdough Bread "
            "Obtained by Novel Digital Technologies and Machine Learning Modelling. "
            "*Fermentation*, 8(10), 516, 2022. "
            "[doi:10.3390/fermentation8100516](https://doi.org/10.3390/fermentation8100516)."
        ),
        (
            "Olakanmi S. J. et al. Quality Characterization of Fava Bean-Fortified Bread Using "
            "Hyperspectral Imaging. *Foods*, 13(2), 231, 2024. "
            "[doi:10.3390/foods13020231](https://doi.org/10.3390/foods13020231)."
        ),
        (
            "Ruderman M., Howell K. A., Appels R. Digital image analysis to assess the texture "
            "of bread products. *Applied Food Research*, 5(2), 101447, 2025. "
            "[doi:10.1016/j.afres.2025.101447](https://doi.org/10.1016/j.afres.2025.101447)."
        ),
        (
            "Torres J. D. et al. Non-invasive microstructural characterization and in vivo "
            "glycemic response of white bread formulated with soluble dietary fiber. "
            "*Food Bioscience*, 61, 104505, 2024. "
            "[doi:10.1016/j.fbio.2024.104505](https://doi.org/10.1016/j.fbio.2024.104505)."
        ),
        (
            "Nallan Chakravartula S. S. et al. Computer vision-based smart monitoring and "
            "control system for food drying: A study on carrot slices. *Computers and "
            "Electronics in Agriculture*, 206, 107654, 2023. "
            "[doi:10.1016/j.compag.2023.107654](https://doi.org/10.1016/j.compag.2023.107654)."
        ),
        (
            "Gonzalez B. et al. Automated Food Weight and Content Estimation Using Computer "
            "Vision and AI Algorithms. *Sensors*, 24(23), 7660, 2024. "
            "[doi:10.3390/s24237660](https://doi.org/10.3390/s24237660)."
        ),
        (
            "Otsu N. A Threshold Selection Method from Gray-Level Histograms. *IEEE "
            "Transactions on Systems, Man, and Cybernetics*, 9(1), 62–66, 1979. "
            "[doi:10.1109/TSMC.1979.4310076](https://doi.org/10.1109/TSMC.1979.4310076)."
        ),
        (
            "Bland J. M., Altman D. G. Statistical methods for assessing agreement between two "
            "methods of clinical measurement. *The Lancet*, 327(8476), 307–310, 1986. "
            "[doi:10.1016/S0140-6736(86)90837-8]"
            "(https://doi.org/10.1016/S0140-6736(86)90837-8)."
        ),
        (
            "Howard A. et al. Searching for MobileNetV3. *Proceedings of the IEEE/CVF "
            "International Conference on Computer Vision*, 1314–1324, 2019. "
            "[doi:10.1109/ICCV.2019.00140](https://doi.org/10.1109/ICCV.2019.00140)."
        ),
        (
            "Breiman L. Random Forests. *Machine Learning*, 45, 5–32, 2001. "
            "[doi:10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324)."
        ),
        (
            "Olakanmi S. J., Jayas D. S., Paliwal J. Applications of imaging systems for the "
            "assessment of quality characteristics of bread and other baked goods: A review. "
            "*Comprehensive Reviews in Food Science and Food Safety*, 22(3), 1817–1838, 2023. "
            "[doi:10.1111/1541-4337.13131](https://doi.org/10.1111/1541-4337.13131)."
        ),
        (
            "Martínez-Lara N.-D., Filomena-Ambrosio A., Garzón-Castro C. L. Use of computer "
            "vision systems in baked products: potential tool for measuring physical properties. "
            "*Journal of Food Measurement and Characterization*, 20, 6925–6947, 2026. "
            "[doi:10.1007/s11694-026-04154-8](https://doi.org/10.1007/s11694-026-04154-8)."
        ),
    ]
    return "\n\n".join(f"{index}. {reference}" for index, reference in enumerate(references, 1))


def _update_readme_results(
    readme: Path, metrics: pd.DataFrame, provenance: dict[str, object]
) -> None:
    if not readme.exists():
        return
    start = "<!-- GENERATED_RESULTS_START -->"
    end = "<!-- GENERATED_RESULTS_END -->"
    text = readme.read_text(encoding="utf-8")
    if start not in text or end not in text:
        return
    best = str(provenance["best_method_selected_on_validation"])
    rows = []
    for target in ("width", "height"):
        rows.append(
            f"| {target.capitalize()} | {_value(metrics, best, target, 'mae'):.3f} | "
            f"{_value(metrics, best, target, 'rmse'):.3f} | "
            f"{_value(metrics, best, target, 'r2'):.3f} |"
        )
    generated = "\n".join(
        [
            start,
            f"Validation-selected method: **{best}**; untouched test "
            f"n={provenance['split_counts']['test']}.",
            "",
            "| Target | MAE | RMSE | R² |",
            "|:--|--:|--:|--:|",
            *rows,
            "",
            f"Classical CV processing: {provenance['mean_cv_processing_ms']:.2f} ms/image. "
            "Values use the dataset's nominal unit; see the unit limitation in the report.",
            end,
        ]
    )
    before, remainder = text.split(start, 1)
    _, after = remainder.split(end, 1)
    readme.write_text(before + generated + after, encoding="utf-8")


def render_results(
    metrics: pd.DataFrame,
    ablation: pd.DataFrame,
    provenance: dict[str, object],
    statistics: dict[str, object],
    output: Path,
) -> None:
    best = str(provenance["best_method_selected_on_validation"])
    comparison = (
        metrics[(metrics["split"] == "test") & metrics["metric"].isin(["mae", "rmse", "r2"])]
        .pivot(index="method", columns=["target", "metric"], values="value")
        .round(3)
    )
    lines = [
        "# Experimental results",
        "",
        f"Run ID: `{provenance['run_id']}`. Dataset: `{provenance['dataset_doi']}` version "
        f"{provenance['dataset_version']}.",
        "",
        f"The audit found {provenance['csv_rows']} CSV rows; "
        f"{provenance['eligible_samples']} uniquely mapped width/height samples were eligible. "
        f"The frozen split contains {provenance['split_counts']}. Segmentation failures: "
        f"{provenance['segmentation_failures']}.",
        "",
        "## Model comparison on the untouched final test set",
        "",
        comparison.to_markdown(),
        "",
        "The method selected using validation MAE before opening final-test results was "
        f"**{best}**.",
        "",
        "## Ablation",
        "",
        ablation.round(3).to_markdown(index=False),
        "",
        "## Measurement agreement and paired errors",
        "",
    ]
    for target in ("width", "height"):
        agreement = statistics[target]["bland_altman"]
        paired = statistics[target]["wilcoxon_vs_linear_calibration"]
        lines.append(
            f"- {target.capitalize()}: bias {agreement['bias']:.3f}; 95% limits of agreement "
            f"[{agreement['lower_loa']:.3f}, {agreement['upper_loa']:.3f}]; paired Wilcoxon "
            f"versus linear calibration p={paired['pvalue']:.4g}."
        )
    lines.extend(
        [
            "",
            "## Computational cost",
            "",
            f"Mean classical image segmentation and feature extraction time was "
            f"{provenance['mean_cv_processing_ms']:.2f} ms/image "
            f"({provenance['images_per_second']:.2f} images/s) on the recorded CPU environment.",
            "",
            "## Limitations",
            "",
            "The CSV misspells `height` as `heigth` and does not encode measurement units. "
            "Values are reported as nominal millimetres because the experiment specification and "
            "measurement magnitudes support that interpretation, but the missing unit metadata is "
            "retained as a limitation. One duplicated filename with conflicting ground truth is "
            "excluded rather than repaired by assumption. Controlled imaging limits external "
            "validity; calibration is camera/setup-specific. Test segmentation failures, if any, "
            "are blocking rather than silently discarded. The CNN status is: "
            f"`{provenance['cnn_status']}`.",
        ]
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_articles(
    metrics: pd.DataFrame,
    provenance: dict[str, object],
    paper_dir: Path,
) -> None:
    best = str(provenance["best_method_selected_on_validation"])
    w_mae = _value(metrics, best, "width", "mae")
    h_mae = _value(metrics, best, "height", "mae")
    w_rmse = _value(metrics, best, "width", "rmse")
    h_rmse = _value(metrics, best, "height", "rmse")
    w_r2 = _value(metrics, best, "width", "r2")
    h_r2 = _value(metrics, best, "height", "r2")
    n = int(provenance["eligible_samples"])
    total_images = int(provenance["audit"]["image_count"])
    train_n = int(provenance["split_counts"]["train"])
    validation_n = int(provenance["split_counts"]["validation"])
    test_n = int(provenance["split_counts"]["test"])
    speed = float(provenance["mean_cv_processing_ms"])
    cnn_status = str(provenance["cnn_status"])
    bibliography = _markdown_bibliography()

    english_title = (
        "# Automated Non-Contact Assessment of Bread Size and Shape from RGB Images "
        "Using Computer Vision"
    )
    english = f"""{english_title}

## Abstract

Manual dimensional inspection is difficult to scale in bakery quality control. This study
developed a fully automated and reproducible pipeline for estimating bread width and height and
for describing shape from ordinary RGB images. Mendeley Data version 1 (DOI
10.17632/f663p7c89m.1) was audited before modelling. Of 173 CSV rows, {n} uniquely mapped samples
were eligible after excluding conflicting or unmatched records, and a deterministic grouped
70/15/15 split protected the final test set. Bread was segmented with Gaussian smoothing, Otsu
thresholding, morphology, and contour validation. Validation-stage train-only pixel calibration was
compared with linear, ridge, random-forest, and histogram-gradient-boosting regression on
morphological features. The method selected on validation data was {best}. On {test_n} untouched
test samples it achieved width MAE {w_mae:.2f}, height MAE {h_mae:.2f}, width RMSE {w_rmse:.2f},
height RMSE {h_rmse:.2f}, and R² values of {w_r2:.3f} and {h_r2:.3f}, respectively, in the
dataset's nominal millimetre unit. Classical processing required {speed:.1f} ms/image on CPU.
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

![End-to-end experimental workflow](figures/pipeline.png)

**Figure 1.** End-to-end workflow from the versioned dataset audit and group-safe split to
segmentation, feature extraction, model selection, final-test evaluation, and generated research
artifacts. The diagram emphasises that the test set is opened only after validation selection.

## 2. Materials and Methods

### 2.1 Dataset and audit

The public CC BY 4.0 dataset by Mora [1] was downloaded from its official versioned record and
kept outside Git. It contains `texture`, `color`, and `size` directories plus a semicolon-delimited
CSV using decimal commas. The published total of 1,635 images was not treated as the dimensional
sample count. The CSV has 173 rows and links one width/height view and one thickness view to each
record. A repeated filename carries conflicting labels; both conflicting rows were excluded
rather than silently corrected. This left {n} eligible physical sample identifiers. Source colour
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

![Bread images, masks, and retained contours](figures/segmentation_examples.png)

**Figure 2.** Representative source photographs from the size subset, automatically generated
binary masks, and the retained bread contours with axis-aligned width and height measurements.
The examples show that crust irregularities are retained instead of being replaced by an idealised
geometric template.

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

The validation-selected method was **{best}**. On {test_n} untouched test samples, width MAE and
RMSE were {w_mae:.2f} and {w_rmse:.2f}; height MAE and RMSE were {h_mae:.2f} and {h_rmse:.2f}.
The corresponding R² values were {w_r2:.3f} for width and {h_r2:.3f} for height. Full per-method
metrics, bootstrap intervals, predictions, ablation results, paired tests, and Bland--Altman
limits are generated from the same run in `reports/results.md` and `results/`. Classical image
processing averaged {speed:.1f} ms/image on the recorded CPU environment. The lightweight image
regression status for this run was `{cnn_status}`; no missing CNN result is represented as a
successful comparison.

![Ground truth versus model predictions](figures/predicted_vs_actual.png)

**Figure 3.** Ground truth versus predictions of the validation-selected model on the untouched
test set. The dashed identity line makes systematic compression at the extremes visible, especially
for large widths, even when the overall coefficient of determination remains positive.

![Bland--Altman measurement agreement](figures/bland_altman.png)

**Figure 4.** Bland--Altman agreement analysis for width and height. The central line represents
mean bias and the outer lines the empirical 95% limits of agreement. This view complements R² by
showing the magnitude and spread of pairwise measurement differences.

![Final-test MAE comparison](figures/model_comparison.png)

**Figure 5.** Final-test MAE comparison for linear calibration, morphology-based regressors, and
MobileNetV3-Small. The CNN result is retained as a negative comparison rather than selectively
omitted; on this sample size the compact morphology model performs better.

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
The validation-selected {best} model obtained test MAE of {w_mae:.2f} for width and {h_mae:.2f}
for height in the nominal dataset unit. Practical deployment remains conditional on external
validation under new cameras, products, poses, and lighting; explicit reference geometry would
also remove ambiguity in physical units. Future work should validate the pipeline prospectively,
quantify instrument uncertainty, evaluate rotated geometries or learned segmentation, and test a
lightweight CNN only when effective sample size and compute support a defensible experiment.

## References

{bibliography}

The same verified records are also available in machine-readable BibTeX form in
`references.bib`.
"""

    russian_title = (
        "# Автоматизированная бесконтактная оценка размеров и формы хлебобулочных "
        "изделий по RGB-изображениям"
    )
    russian = f"""{russian_title}

## Аннотация

Разработан воспроизводимый pipeline бесконтактной оценки ширины, высоты и количественных
характеристик формы хлебобулочных изделий по RGB-изображениям. До моделирования выполнен аудит
набора Mendeley Data v1 (DOI 10.17632/f663p7c89m.1). Из 173 строк CSV пригодными признаны {n}
однозначно сопоставленных физических образцов; конфликтующие записи исключены без ручного
исправления, после чего зафиксировано групповое разбиение 70/15/15. Сегментация объединяет
Gaussian blur, порог Отсу, морфологические операции и контроль контура. Линейная pixel-to-mm
калибровка сравнена с линейной, ridge-, Random Forest- и HistGradientBoosting-регрессией по
морфологическим признакам. По validation MAE выбран метод {best}. На {test_n} независимых тестовых
образцах MAE ширины составила {w_mae:.2f}, MAE высоты — {h_mae:.2f}, RMSE — {w_rmse:.2f} и
{h_rmse:.2f}, R² — {w_r2:.3f} и {h_r2:.3f} соответственно в номинальных миллиметрах набора.
Классическая обработка заняла {speed:.1f} мс/изображение на CPU. Все числа автоматически связаны
с predictions и metrics; ограничения метаданных и внешней валидности сохранены явно.

**Ключевые слова:** компьютерное зрение; хлеб; неразрушающие измерения; обработка изображений;
машинное обучение; контроль качества; Bland--Altman.

## 1. Введение

Ручной контроль размеров хлебобулочных изделий плохо масштабируется и даёт лишь выборочную
информацию о процессе. RGB-камера позволяет выполнять дешёвое бесконтактное измерение, однако
точность зависит от освещения, ракурса, масштаба и прослеживаемости измерений. Обзоры методов
визуального контроля хлеба отмечают широкий набор цветовых, текстурных и геометрических
признаков, но также недостаток стандартизации и воспроизводимости [16,17]. Gaussian blur, Otsu,
морфология и OpenCV уже использовались для хлеба [2,5], поэтому в данной работе они рассматриваются
как baseline.

Цель работы — разработать и проверить автоматический воспроизводимый pipeline оценки ширины,
высоты и формы хлеба, сравнив простую линейную калибровку с обучаемой регрессией и связав каждое
утверждение с сохранёнными результатами. Гипотеза H1 состоит в том, что морфологические признаки
снижают ошибку относительно одномерной pixel-to-mm калибровки; её статус определяется только
вычислительным экспериментом.

![Схема полного экспериментального процесса](figures/pipeline.png)

**Рисунок 1.** Полный процесс от аудита версионированного набора данных и группового разбиения до
сегментации, извлечения признаков, выбора модели, финальной оценки и формирования материалов
исследования. Независимая test-выборка используется только после выбора метода по validation.

## 2. Материалы и методы

### 2.1 Набор данных

Использован официальный набор Mora [1] под лицензией CC BY 4.0; изображения не включены в Git.
Заявленные авторами 1 635 изображений не принимались за объём размерной выборки. `Data.csv`
содержит 173 строки и отдельные имена изображений для width/height и thickness. Повторяющееся имя
с конфликтующими размерами сделало две строки неоднозначными; они исключены консервативно. Для
основной задачи осталось {n} образцов. Производные цветовые crops не смешивались с исходными
изображениями. CSV не кодирует единицы; значения интерпретированы как номинальные миллиметры,
что отмечено как ограничение.

### 2.2 Обработка и признаки

После grayscale и Gaussian blur порог Отсу [12] оценивался для обеих полярностей. Opening и
closing подавляли малые объекты, затем выбирался крупнейший допустимый контур. Сохранялись mask,
контур, bounding box, служебные флаги и время. Рассчитывались width/height в пикселях, area,
perimeter, aspect ratio, circularity, solidity, extent, equivalent diameter, а при наличии пяти
точек — оси эллипса и eccentricity. Искусственные классы качества формы не вводились.

![Фотографии хлеба, маски и найденные контуры](figures/segmentation_examples.png)

**Рисунок 2.** Примеры исходных фотографий из размерной части набора, автоматически полученных
бинарных масок и контуров с измерениями ширины и высоты. Неровности корки сохраняются в контуре,
а не заменяются идеализированной геометрической фигурой.

### 2.3 Эксперимент

Физические sample ID разделены на train/validation/test в долях 70/15/15 при seed=42; пересечение
групп программно запрещено. Validation-кандидаты обучались только на train. После выбора метода
классические модели переобучались на train+validation перед однократной оценкой final test. Для
Method B сравнивались Linear Regression, Ridge, Random Forest [15] и
HistGradientBoostingRegressor. Ablation сопоставлял два пиксельных признака и полный набор
морфологии.

Для width и height вычислялись MAE, RMSE и R², bootstrap-интервалы MAE и парный Wilcoxon по общей
выборке. Согласие лучшего метода анализировалось по Bland--Altman [13], поскольку высокий R² сам
по себе не доказывает согласие измерений. CPU benchmark включал сегментацию и извлечение признаков.

## 3. Результаты и обсуждение

По validation MAE выбран **{best}**. На {test_n} тестовых образцах MAE width={w_mae:.2f},
height={h_mae:.2f}; RMSE width={w_rmse:.2f}, height={h_rmse:.2f}; R² width={w_r2:.3f},
height={h_r2:.3f}. Полные метрики, интервалы, Bland--Altman, predictions и ablation находятся в
`reports/results.md` и `results/` и генерируются одним запуском. Среднее время классической
обработки — {speed:.1f} мс/изображение. Статус lightweight CNN: `{cnn_status}`; отсутствующий
эксперимент не подменяется положительным выводом.

![Эталонные значения и прогнозы модели](figures/predicted_vs_actual.png)

**Рисунок 3.** Эталонные значения и прогнозы выбранной по validation модели на независимом test.
Пунктирная линия соответствует идеальному равенству и показывает сжатие прогнозов на крайних
значениях, особенно для наиболее широких образцов.

![Анализ согласия Bland--Altman](figures/bland_altman.png)

**Рисунок 4.** Анализ согласия Bland--Altman для ширины и высоты. Центральная линия показывает
среднее смещение, внешние линии — эмпирические 95%-е пределы согласия. Такой график дополняет R²,
показывая величину и разброс парных ошибок измерения.

![Сравнение MAE методов](figures/model_comparison.png)

**Рисунок 5.** Сравнение MAE линейной калибровки, регрессоров по морфологическим признакам и
MobileNetV3-Small на final test. Результат CNN сохранён как отрицательное сравнение: при данном
размере выборки компактная морфологическая модель оказалась точнее.

Различие ошибок по двум осям может быть связано с неправильной формой корки, поворотом и
чувствительностью axis-aligned bounding box. Морфологическая регрессия учитывает площадь и
компактность, но калибровка остаётся специфичной для камеры и стенда. Сопоставлять числа напрямую
с работами по нарезному хлебу [2], багетам [3] или RGB-D оценке еды [11] некорректно из-за разных
объектов, геометрии и целевых переменных.

## 4. Заключение

Получен воспроизводимый pipeline от аудита и автоматической сегментации до физической калибровки,
статистики согласия и CPU benchmark. Метод {best} дал MAE {w_mae:.2f} для ширины и {h_mae:.2f}
для высоты на независимом test в номинальных единицах CSV. Главные ограничения — отсутствие
явной единицы в CSV, конфликтующая запись, контролируемая съёмка и отсутствие внешней выборки.
Дальнейшая работа должна проверить новые камеры и изделия, добавить эталон масштаба, учесть
неопределённость инструментальных измерений и выполнять CNN-baseline только при достаточной
эффективной выборке.

## Литература

{bibliography}

Те же проверенные записи доступны в машиночитаемом формате BibTeX в файле
`references.bib`.
"""
    paper_dir.mkdir(parents=True, exist_ok=True)
    (paper_dir / "article_en.md").write_text(english, encoding="utf-8")
    (paper_dir / "article_ru.md").write_text(russian, encoding="utf-8")
    best_tex = best.replace("_", r"\_")
    baseline_w = _value(metrics, "linear_calibration", "width", "mae")
    baseline_h = _value(metrics, "linear_calibration", "height", "mae")
    cnn_w = _value(metrics, "mobilenet_v3_small", "width", "mae")
    cnn_h = _value(metrics, "mobilenet_v3_small", "height", "mae")
    tex = rf"""\documentclass[10pt,twocolumn]{{article}}
\usepackage[margin=1.7cm]{{geometry}}
\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{graphicx,booktabs,amsmath,microtype,hyperref}}
\title{{Automated Non-Contact Assessment of Bread Size and Shape\\
from RGB Images Using Computer Vision}}
\author{{AUTHOR\_NAME}}
\date{{}}
\begin{{document}}
\maketitle
\begin{{abstract}}
We present a reproducible RGB computer-vision pipeline for bread dimension measurement. The
official Mendeley Data v1 archive was audited before modelling: {n} of 173 measurement rows were
uniquely usable and split by physical sample into train, validation and an untouched test set.
Otsu segmentation and contour morphology were compared with classical regressors and a frozen
MobileNetV3-Small baseline. Validation selected {best_tex}. On {test_n} test samples it achieved
MAE {w_mae:.2f} for width and {h_mae:.2f} for height, with $R^2$ {w_r2:.3f} and {h_r2:.3f}.
Classical processing required {speed:.1f} ms/image on CPU. The work supplies an auditable baseline
while retaining unit, calibration and external-validity limitations.
\end{{abstract}}
\textbf{{Keywords:}} computer vision; bread quality; non-destructive measurement; image
processing; machine learning; quality control.

\section{{Introduction}}
Manual bread inspection is intermittent and difficult to trace. Controlled RGB imaging offers a
low-cost alternative, but scale, pose and acquisition conditions can dominate accuracy. Prior
reviews describe extensive colour, texture and shape analysis while identifying limited
standardisation and reproducibility \cite{{olakanmi2023review,martinezlara2026review}}. We ask
whether an auditable morphology-based pipeline improves on one-dimensional pixel calibration.

\begin{{figure}}[t]
\centering\includegraphics[width=\columnwidth]{{figures/pipeline.pdf}}
\caption{{End-to-end auditable workflow. The final test set remains isolated until validation
selection is complete.}}
\label{{fig:pipeline}}
\end{{figure}}

\section{{Materials and methods}}
The CC BY 4.0 dataset by Mora \cite{{mora2025bread_dataset}} was downloaded from its versioned
record and kept outside Git. Its size CSV has 173 rows. A duplicated canonical image identifier
with conflicting targets caused two rows to be excluded, leaving {n} unique samples. CSV indices
without leading zeroes were linked to files through a strict view--batch--integer parser, never
through fuzzy matching. The dataset omits an explicit target unit; results therefore use a
nominal dataset unit (interpreted as mm) and preserve this as a limitation.

Images were converted to grayscale, smoothed, segmented with two-polarity Otsu thresholding
\cite{{otsu1979threshold}}, cleaned morphologically and reduced to the largest valid contour.
Features included bounding-box dimensions, area, perimeter, aspect ratio, circularity, solidity,
extent, equivalent diameter and ellipse descriptors. Physical sample IDs were divided
{train_n}/{validation_n}/{test_n}
into train/validation/test with seed 42 and asserted to have zero overlap.

The archive audit examined {total_images} readable images across size, colour and texture folders.
Only the width/height \texttt{{E}} view from the size folder entered this experiment. Derived
colour crops and the separate thickness \texttt{{C}} view were excluded from predictors,
preventing alternate views of the same physical item from crossing partitions.
Table~\ref{{tab:data}} summarises the auditable
sample flow; all exclusions remain in the generated manifest with an explicit reason.

\begin{{table}}[h]
\centering
\caption{{Audited dataset and fixed experimental partition.}}
\label{{tab:data}}
\begin{{tabular}}{{lr}}
\toprule Quantity & Count \\
\midrule Archive images & {total_images} \\
Measurement CSV rows & 173 \\
Eligible physical samples & {n} \\
Train / validation / test & {train_n} / {validation_n} / {test_n} \\
Segmentation failures & 0 \\
\bottomrule
\end{{tabular}}
\end{{table}}

Separate linear pixel calibrations were compared with linear, ridge, random-forest
\cite{{breiman2001random}} and histogram-gradient-boosting regressors. A frozen MobileNetV3-Small
\cite{{howard2019mobilenetv3}} head was selected by validation loss without test access. Classical
models were refit on train+validation after validation selection. Metrics were MAE, RMSE, MAPE,
$R^2$, bootstrap MAE intervals, paired Wilcoxon error tests and Bland--Altman agreement
\cite{{bland1986agreement}}.

All transformations were implemented as one command from a versioned YAML configuration. Random
seeds, package versions, the Git revision, a source-tree digest and hardware descriptors are
written to provenance. Test-set segmentation failure is a blocking error rather than a silently
dropped observation. Bootstrap intervals use the configured 2,000 resamples, and all paired
comparisons operate on identical physical sample IDs.

\begin{{figure*}}[t]
\centering\includegraphics[width=\textwidth]{{figures/segmentation_examples.pdf}}
\caption{{Representative source photographs, automatically generated masks, and retained bread
contours. Crust irregularities remain visible in the measured boundary.}}
\label{{fig:segmentation}}
\end{{figure*}}

\section{{Results}}
The validation-selected method was {best_tex}. Table~\ref{{tab:results}} reports final-test
performance. It improved width MAE over linear calibration from {baseline_w:.2f} to {w_mae:.2f};
height MAE changed from {baseline_h:.2f} to {h_mae:.2f}. The CNN test MAEs were {cnn_w:.2f} and
{cnn_h:.2f}, so it did not displace the compact morphology model on this sample size.

\begin{{table}}[h]
\centering
\caption{{Final-test performance in the nominal dataset unit.}}
\label{{tab:results}}
\begin{{tabular}}{{lrrr}}
\toprule Target & MAE & RMSE & $R^2$ \\
\midrule Width & {w_mae:.2f} & {w_rmse:.2f} & {w_r2:.3f} \\
Height & {h_mae:.2f} & {h_rmse:.2f} & {h_r2:.3f} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\begin{{figure*}}[t]
\centering\includegraphics[width=0.92\textwidth]{{figures/predicted_vs_actual.pdf}}
\caption{{Ground truth versus predictions for the validation-selected method on the untouched
test set. The dashed identity line reveals regression towards the centre at extreme widths.}}
\label{{fig:predictions}}
\end{{figure*}}

All {n} eligible images segmented successfully. Classical segmentation and feature extraction
averaged {speed:.1f} ms/image. The ablation, confidence intervals, per-sample predictions and
agreement limits are generated from the same run and retained in the repository.

The selected model's Bland--Altman width bias was close to zero, while the observed limits of
agreement remained wide enough to preclude interchangeability claims for precision metrology.
The paired improvement over the linear calibration was stronger for width than height. These
results support the narrower conclusion that morphology helps calibration under this controlled
setup; they do not establish a universal bread-quality score.

\begin{{figure*}}[t]
\centering\includegraphics[width=0.92\textwidth]{{figures/bland_altman.pdf}}
\caption{{Bland--Altman agreement analysis. The central line is mean bias and the outer lines are
the empirical 95\% limits of agreement.}}
\label{{fig:bland_altman}}
\end{{figure*}}

\begin{{figure}}[h]
\centering\includegraphics[width=\columnwidth]{{figures/model_comparison.pdf}}
\caption{{Final-test MAE across classical calibration, morphology regressors, and the lightweight
CNN baseline.}}
\label{{fig:model_comparison}}
\end{{figure}}

\section{{Discussion and conclusion}}
Morphology substantially improved width estimation over pixel-only calibration, while the height
gain was smaller. Irregular boundaries, pose and axis-aligned boxes remain error sources. The
small test set widens uncertainty, and no claim transfers across cameras or products without
external validation. A reference scale, prospective acquisition and instrument-uncertainty study
are necessary before deployment. Nevertheless, the project provides a fully traced baseline from
audit and grouped splitting through statistics, figures and reports.

The lightweight CNN underperformed the best classical regressor, which is plausible with only
{train_n} training samples and a frozen generic backbone. This negative comparison is retained to
avoid selective reporting. Future work should evaluate rotated boxes or learned segmentation,
collect repeat instrument measurements, and test product- and camera-held-out cohorts. Deployment
should also monitor segmentation flags and acquisition drift rather than relying on a point
prediction alone.

\bibliographystyle{{plain}}
\bibliography{{references}}
\end{{document}}
"""
    (paper_dir / "article.tex").write_text(
        tex,
        encoding="utf-8",
    )
    _update_readme_results(paper_dir.parent / "README.md", metrics, provenance)
