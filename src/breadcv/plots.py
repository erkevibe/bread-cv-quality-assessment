from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .evaluation import bland_altman


def _save(figure: plt.Figure, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=300, bbox_inches="tight")
    figure.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(figure)


def plot_pipeline(output: Path) -> None:
    labels = ["RGB image", "Otsu + morphology", "Contour features", "Calibration", "Dimensions"]
    figure, axis = plt.subplots(figsize=(10, 2.2))
    axis.set_xlim(0, len(labels))
    axis.set_ylim(0, 1)
    axis.axis("off")
    for index, label in enumerate(labels):
        axis.text(
            index + 0.5,
            0.5,
            label,
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.5", "facecolor": "#e8f1fa", "edgecolor": "#285f8f"},
        )
        if index < len(labels) - 1:
            axis.annotate(
                "",
                (index + 1.08, 0.5),
                (index + 0.92, 0.5),
                arrowprops={"arrowstyle": "->"},
            )
    axis.set_title("Automated bread dimension assessment pipeline")
    _save(figure, output)


def plot_segmentation_examples(examples: list[dict[str, object]], output: Path) -> None:
    selected = examples[:2]
    figure, axes = plt.subplots(len(selected), 3, figsize=(9, 3 * len(selected)), squeeze=False)
    for row, example in enumerate(selected):
        for column, (key, title) in enumerate(
            (("original", "Original"), ("mask", "Mask"), ("overlay", "Contour and measurement"))
        ):
            axes[row, column].imshow(example[key], cmap="gray" if key == "mask" else None)
            axes[row, column].set_title(f"{title} — {example['sample_id']}")
            axes[row, column].axis("off")
    figure.tight_layout()
    _save(figure, output)


def plot_predicted_vs_actual(predictions: pd.DataFrame, method: str, output: Path) -> None:
    subset = predictions[(predictions["method"] == method) & (predictions["split"] == "test")]
    figure, axes = plt.subplots(1, 2, figsize=(9, 4))
    for axis, target in zip(axes, ("width", "height"), strict=True):
        actual = subset[f"actual_{target}"]
        predicted = subset[f"predicted_{target}"]
        lower = min(actual.min(), predicted.min())
        upper = max(actual.max(), predicted.max())
        axis.scatter(actual, predicted, alpha=0.75, edgecolor="none")
        axis.plot([lower, upper], [lower, upper], "k--", linewidth=1)
        axis.set_xlabel(f"Actual {target} (dataset unit)")
        axis.set_ylabel(f"Predicted {target} (dataset unit)")
        axis.set_title(target.capitalize())
    figure.suptitle(f"Ground truth vs prediction — {method}")
    figure.tight_layout()
    _save(figure, output)


def plot_bland_altman(predictions: pd.DataFrame, method: str, output: Path) -> None:
    subset = predictions[(predictions["method"] == method) & (predictions["split"] == "test")]
    figure, axes = plt.subplots(1, 2, figsize=(10, 4))
    for axis, target in zip(axes, ("width", "height"), strict=True):
        agreement = bland_altman(
            subset[f"actual_{target}"].to_numpy(), subset[f"predicted_{target}"].to_numpy()
        )
        axis.scatter(agreement["means"], agreement["differences"], alpha=0.75, edgecolor="none")
        axis.axhline(agreement["bias"], color="black", label="Mean bias")
        axis.axhline(agreement["lower_loa"], color="tab:red", linestyle="--", label="95% LoA")
        axis.axhline(agreement["upper_loa"], color="tab:red", linestyle="--")
        axis.set_xlabel(f"Mean {target} (dataset unit)")
        axis.set_ylabel("Predicted − actual")
        axis.set_title(target.capitalize())
    axes[0].legend(fontsize=8)
    figure.suptitle(f"Bland–Altman agreement — {method}")
    figure.tight_layout()
    _save(figure, output)


def plot_model_comparison(metrics: pd.DataFrame, output: Path) -> None:
    subset = metrics[(metrics["split"] == "test") & (metrics["metric"] == "mae")]
    pivot = subset.pivot(index="method", columns="target", values="value").sort_values("width")
    figure, axis = plt.subplots(figsize=(9, 4.8))
    positions = np.arange(len(pivot))
    width = 0.38
    axis.bar(positions - width / 2, pivot["width"], width, label="Width")
    axis.bar(positions + width / 2, pivot["height"], width, label="Height")
    axis.set_xticks(positions, pivot.index, rotation=30, ha="right")
    axis.set_ylabel("MAE (dataset unit)")
    axis.set_title("Test-set model comparison")
    axis.legend()
    figure.tight_layout()
    _save(figure, output)
