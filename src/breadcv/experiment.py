from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from .audit import run_audit
from .cnn import train_mobilenet_regressor
from .config import resolve_path
from .data import find_csv_path, find_dataset_root, read_measurements
from .evaluation import bland_altman, regression_metrics
from .features import FEATURE_COLUMNS
from .manifest import build_size_manifest
from .models import build_model
from .plots import (
    plot_bland_altman,
    plot_model_comparison,
    plot_pipeline,
    plot_predicted_vs_actual,
    plot_segmentation_examples,
)
from .processing import extract_features
from .reporting import render_articles, render_results
from .splitting import assert_group_disjoint, grouped_train_validation_test_split
from .statistics import bootstrap_mae_ci, paired_absolute_error_test


def _git_revision(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _source_tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    included = [root / "pyproject.toml", root / "uv.lock"]
    for directory in (root / "src", root / "scripts", root / "configs"):
        included.extend(
            path
            for path in directory.rglob("*")
            if path.is_file() and path.suffix in {".py", ".yaml", ".yml"}
        )
    for path in sorted(included):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _package_versions() -> dict[str, str]:
    packages = (
        "numpy",
        "pandas",
        "opencv-python-headless",
        "scikit-learn",
        "scipy",
        "torch",
        "torchvision",
    )
    versions: dict[str, str] = {}
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not-installed"
    return versions


def _predict_linear_calibration(
    train: pd.DataFrame, evaluate: pd.DataFrame
) -> tuple[np.ndarray, dict[str, object]]:
    width = LinearRegression().fit(train[["width_px"]], train["target_width"])
    height = LinearRegression().fit(train[["height_px"]], train["target_height"])
    predicted = np.column_stack(
        [width.predict(evaluate[["width_px"]]), height.predict(evaluate[["height_px"]])]
    )
    metadata = {
        "width_coefficient": float(width.coef_[0]),
        "width_intercept": float(width.intercept_),
        "height_coefficient": float(height.coef_[0]),
        "height_intercept": float(height.intercept_),
    }
    return predicted, metadata


def _prediction_rows(
    evaluate: pd.DataFrame, predicted: np.ndarray, method: str, split: str
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "sample_id": evaluate["sample_id"].to_numpy(),
            "relative_path": evaluate["relative_path"].to_numpy(),
            "split": split,
            "method": method,
            "actual_width": evaluate["target_width"].to_numpy(),
            "predicted_width": predicted[:, 0],
            "actual_height": evaluate["target_height"].to_numpy(),
            "predicted_height": predicted[:, 1],
        }
    )


def _metrics(
    predictions: pd.DataFrame,
    *,
    bootstrap_iterations: int,
    confidence: float,
    seed: int,
) -> pd.DataFrame:
    rows = []
    for (method, split), group in predictions.groupby(["method", "split"]):
        for target in ("width", "height"):
            values = regression_metrics(group[f"actual_{target}"], group[f"predicted_{target}"])
            lower, upper = bootstrap_mae_ci(
                group[f"actual_{target}"].to_numpy(),
                group[f"predicted_{target}"].to_numpy(),
                iterations=bootstrap_iterations,
                confidence=confidence,
                seed=seed,
            )
            for metric, value in values.items():
                rows.append(
                    {
                        "method": method,
                        "split": split,
                        "target": target,
                        "metric": metric,
                        "value": value,
                        "ci_lower": lower if metric == "mae" else np.nan,
                        "ci_upper": upper if metric == "mae" else np.nan,
                        "n": len(group),
                    }
                )
    return pd.DataFrame(rows)


def _best_validation_method(metrics: pd.DataFrame) -> str:
    validation = metrics[(metrics["split"] == "validation") & (metrics["metric"] == "mae")]
    return str(validation.groupby("method")["value"].mean().idxmin())


def run_experiment(config: dict[str, object]) -> dict[str, object]:
    root = resolve_path(".")
    data_root = resolve_path(config["dataset"]["root"])
    reports_dir = resolve_path(config["outputs"]["reports_dir"])
    results_dir = resolve_path(config["outputs"]["results_dir"])
    figures_dir = resolve_path(config["outputs"]["figures_dir"])
    for path in (
        reports_dir,
        results_dir / "metrics",
        results_dir / "predictions",
        results_dir / "models",
        results_dir / "data",
        figures_dir,
    ):
        path.mkdir(parents=True, exist_ok=True)

    csv_name = config["dataset"].get("csv_name", "size/Data.csv")
    audit = run_audit(data_root, reports_dir, csv_name)
    dataset_root = find_dataset_root(data_root, csv_name)
    measurements = read_measurements(find_csv_path(data_root, csv_name))
    inventory = pd.read_csv(reports_dir / "files_inventory.csv")
    manifest = build_size_manifest(measurements, inventory)
    eligible = manifest[manifest["eligible_width_height"]].copy()
    if len(eligible) < 30:
        raise RuntimeError(f"Only {len(eligible)} uniquely mapped samples; experiment is blocked")
    eligible["split"] = grouped_train_validation_test_split(
        eligible,
        "sample_id",
        train_fraction=float(config["split"]["train"]),
        validation_fraction=float(config["split"]["validation"]),
        test_fraction=float(config["split"]["test"]),
        seed=int(config["seed"]),
    )
    manifest = manifest.merge(eligible[["csv_row", "split"]], on="csv_row", how="left")
    assert_group_disjoint(eligible, "sample_id", "split")
    manifest.to_csv(results_dir / "data" / "manifest.csv", index=False)
    eligible[["sample_id", "relative_path", "split"]].to_csv(
        results_dir / "data" / "splits.csv", index=False
    )

    features, examples = extract_features(eligible, dataset_root, config["image"])
    features.to_csv(results_dir / "data" / "features.csv", index=False)
    failures = features[features["processing_status"] != "ok"]
    clean = features[features["processing_status"] == "ok"].copy()
    if failures["split"].eq("test").any():
        raise RuntimeError("A final-test image failed segmentation; silent exclusion is prohibited")
    if len(clean) < 30:
        raise RuntimeError("Too few successfully segmented samples")

    feature_sets = {
        "pixels": ["width_px", "height_px"],
        "morphology": FEATURE_COLUMNS,
    }
    model_names = list(config["models"]["ml"])
    validation_predictions: list[pd.DataFrame] = []
    test_predictions: list[pd.DataFrame] = []
    model_metadata: dict[str, object] = {}
    train = clean[clean["split"] == "train"]
    validation = clean[clean["split"] == "validation"]
    test = clean[clean["split"] == "test"]
    train_validation = clean[clean["split"].isin(["train", "validation"])]
    y_columns = ["target_width", "target_height"]

    predicted, metadata = _predict_linear_calibration(train, validation)
    validation_predictions.append(
        _prediction_rows(validation, predicted, "linear_calibration", "validation")
    )
    predicted, final_metadata = _predict_linear_calibration(train_validation, test)
    test_predictions.append(_prediction_rows(test, predicted, "linear_calibration", "test"))
    model_metadata["linear_calibration"] = {
        "validation_fit": metadata,
        "final_fit": final_metadata,
    }

    for name in model_names:
        method = name
        validation_model = build_model(name, int(config["seed"]))
        validation_model.fit(train[feature_sets["morphology"]], train[y_columns])
        validation_predictions.append(
            _prediction_rows(
                validation,
                validation_model.predict(validation[feature_sets["morphology"]]),
                method,
                "validation",
            )
        )
        final_model = build_model(name, int(config["seed"]))
        final_model.fit(train_validation[feature_sets["morphology"]], train_validation[y_columns])
        test_predictions.append(
            _prediction_rows(
                test,
                final_model.predict(test[feature_sets["morphology"]]),
                method,
                "test",
            )
        )
        joblib.dump(final_model, results_dir / "models" / f"{name}.joblib")

    cnn_metadata: dict[str, object] | None = None
    if config["models"]["cnn"].get("enabled", False):
        cnn_predictions, cnn_metadata = train_mobilenet_regressor(
            eligible,
            dataset_root,
            config["models"]["cnn"],
            int(config["seed"]),
            results_dir / "models" / "mobilenet_v3_small.pt",
        )
        validation_predictions.append(cnn_predictions[cnn_predictions["split"] == "validation"])
        test_predictions.append(cnn_predictions[cnn_predictions["split"] == "test"])

    # Small, pre-specified ablation: Ridge on pixel-only vs full morphology.
    ablation_rows = []
    for feature_set, columns in feature_sets.items():
        model = build_model("ridge", int(config["seed"]))
        model.fit(train_validation[columns], train_validation[y_columns])
        predicted = model.predict(test[columns])
        for target_index, target in enumerate(("width", "height")):
            values = regression_metrics(test[y_columns[target_index]], predicted[:, target_index])
            ablation_rows.append(
                {"feature_set": feature_set, "target": target, **values, "n": len(test)}
            )
    pd.DataFrame(ablation_rows).to_csv(results_dir / "metrics" / "ablation.csv", index=False)

    predictions = pd.concat(validation_predictions + test_predictions, ignore_index=True)
    metrics = _metrics(
        predictions,
        bootstrap_iterations=int(config["evaluation"]["bootstrap_iterations"]),
        confidence=float(config["evaluation"]["confidence"]),
        seed=int(config["seed"]),
    )
    best_method = _best_validation_method(metrics)
    predictions.to_csv(results_dir / "predictions" / "predictions.csv", index=False)
    predictions[predictions["split"] == "test"].to_csv(
        results_dir / "predictions" / "test_predictions.csv", index=False
    )
    metrics.to_csv(results_dir / "metrics" / "metrics.csv", index=False)

    best_test = predictions[
        (predictions["method"] == best_method) & (predictions["split"] == "test")
    ]
    baseline_test = predictions[
        (predictions["method"] == "linear_calibration") & (predictions["split"] == "test")
    ].set_index("sample_id")
    statistics: dict[str, object] = {"best_method_selected_on_validation": best_method}
    for target in ("width", "height"):
        indexed = best_test.set_index("sample_id")
        common = indexed.index.intersection(baseline_test.index)
        statistics[target] = {
            "bland_altman": {
                key: value
                for key, value in bland_altman(
                    indexed.loc[common, f"actual_{target}"],
                    indexed.loc[common, f"predicted_{target}"],
                ).items()
                if key not in {"means", "differences"}
            },
            "wilcoxon_vs_linear_calibration": paired_absolute_error_test(
                indexed.loc[common, f"actual_{target}"].to_numpy(),
                indexed.loc[common, f"predicted_{target}"].to_numpy(),
                baseline_test.loc[common, f"predicted_{target}"].to_numpy(),
            ),
        }
    (results_dir / "metrics" / "statistics.json").write_text(
        json.dumps(statistics, indent=2), encoding="utf-8"
    )
    (results_dir / "models" / "metadata.json").write_text(
        json.dumps({**model_metadata, "mobilenet_v3_small": cnn_metadata}, indent=2),
        encoding="utf-8",
    )

    plot_pipeline(figures_dir / "pipeline")
    plot_segmentation_examples(examples, figures_dir / "segmentation_examples")
    plot_predicted_vs_actual(predictions, best_method, figures_dir / "predicted_vs_actual")
    plot_bland_altman(predictions, best_method, figures_dir / "bland_altman")
    plot_model_comparison(metrics, figures_dir / "model_comparison")

    provenance = {
        "run_id": datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "dataset_doi": config["dataset"]["doi"],
        "dataset_version": config["dataset"]["version"],
        "csv_rows": len(measurements),
        "eligible_samples": len(eligible),
        "segmentation_failures": len(failures),
        "split_counts": eligible["split"].value_counts().to_dict(),
        "best_method_selected_on_validation": best_method,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "cpu_count": __import__("os").cpu_count(),
        "git_revision": _git_revision(root),
        "source_tree_sha256": _source_tree_sha256(root),
        "package_versions": _package_versions(),
        "mean_cv_processing_ms": float(clean["processing_ms"].mean()),
        "images_per_second": float(1000.0 / clean["processing_ms"].mean()),
        "audit": audit,
        "target_unit_limitation": (
            "Data.csv does not encode units; values are treated as nominal mm."
        ),
        "cnn_status": "completed" if cnn_metadata is not None else "disabled",
    }
    (results_dir / "metrics" / "provenance.json").write_text(
        json.dumps(provenance, indent=2, default=str), encoding="utf-8"
    )
    render_results(
        metrics,
        pd.read_csv(results_dir / "metrics" / "ablation.csv"),
        provenance,
        statistics,
        reports_dir / "results.md",
    )
    render_articles(metrics, provenance, root / "paper")
    return provenance
