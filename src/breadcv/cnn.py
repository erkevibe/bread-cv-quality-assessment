from __future__ import annotations

import copy
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageOps


def build_preprocess(weights, image_size: int):
    from torchvision import transforms

    preset = weights.transforms() if weights is not None else None
    normalise = (
        transforms.Normalize(mean=preset.mean, std=preset.std) if preset is not None else None
    )

    class Letterbox:
        def __call__(self, image: Image.Image) -> Image.Image:
            contained = ImageOps.contain(image, (image_size, image_size))
            return ImageOps.pad(contained, (image_size, image_size), color=(0, 0, 0))

    operations: list[object] = [Letterbox(), transforms.ToTensor()]
    if normalise is not None:
        operations.append(normalise)
    return transforms.Compose(operations)


def train_mobilenet_regressor(
    manifest: pd.DataFrame,
    dataset_root: Path,
    config: dict[str, object],
    seed: int,
    model_path: Path,
) -> tuple[pd.DataFrame, dict[str, object]]:
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, Dataset
    from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    image_size = int(config.get("image_size", 224))
    weights = MobileNet_V3_Small_Weights.DEFAULT if config.get("pretrained", True) else None
    transform = build_preprocess(weights, image_size)
    target_mean = manifest[manifest["split"] == "train"][["target_width", "target_height"]].mean()
    target_std = manifest[manifest["split"] == "train"][["target_width", "target_height"]].std()

    class BreadDataset(Dataset):
        def __init__(self, frame: pd.DataFrame) -> None:
            self.frame = frame.reset_index(drop=True)

        def __len__(self) -> int:
            return len(self.frame)

        def __getitem__(self, index: int):
            row = self.frame.iloc[index]
            with Image.open(dataset_root / row["relative_path"]) as image:
                tensor = transform(image.convert("RGB"))
            target = torch.tensor([row["target_width"], row["target_height"]], dtype=torch.float32)
            mean_tensor = torch.tensor(target_mean.to_numpy(), dtype=torch.float32)
            std_tensor = torch.tensor(target_std.to_numpy(), dtype=torch.float32)
            target = (target - mean_tensor) / std_tensor
            return tensor, target, str(row["sample_id"]), str(row["relative_path"])

    partitions = {
        split: manifest[manifest["split"] == split].copy()
        for split in ("train", "validation", "test")
    }
    loaders = {
        split: DataLoader(
            BreadDataset(frame),
            batch_size=int(config.get("batch_size", 16)),
            shuffle=split == "train",
            num_workers=0,
            generator=torch.Generator().manual_seed(seed),
        )
        for split, frame in partitions.items()
    }
    model = mobilenet_v3_small(weights=weights)
    for parameter in model.parameters():
        parameter.requires_grad = False
    input_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(input_features, 2)
    for parameter in model.classifier.parameters():
        parameter.requires_grad = True
    optimizer = torch.optim.AdamW(
        model.classifier.parameters(), lr=float(config.get("learning_rate", 0.001))
    )
    loss_function = nn.MSELoss()
    best_state = copy.deepcopy(model.state_dict())
    best_validation = float("inf")
    history = []
    for epoch in range(int(config.get("epochs", 25))):
        model.train()
        train_losses = []
        for images, targets, _, _ in loaders["train"]:
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model(images), targets)
            loss.backward()
            optimizer.step()
            train_losses.append(float(loss.detach()))
        model.eval()
        validation_losses = []
        with torch.no_grad():
            for images, targets, _, _ in loaders["validation"]:
                validation_losses.append(float(loss_function(model(images), targets)))
        validation_loss = float(np.mean(validation_losses))
        history.append(
            {
                "epoch": epoch + 1,
                "train_loss": float(np.mean(train_losses)),
                "validation_loss": validation_loss,
            }
        )
        if validation_loss < best_validation:
            best_validation = validation_loss
            best_state = copy.deepcopy(model.state_dict())
    model.load_state_dict(best_state)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_path)

    prediction_rows: list[dict[str, object]] = []
    timings = []
    model.eval()
    with torch.no_grad():
        for split in ("validation", "test"):
            frame_by_id = partitions[split].set_index("sample_id")
            for images, _, sample_ids, paths in loaders[split]:
                started = time.perf_counter()
                output = model(images).numpy()
                timings.append((time.perf_counter() - started) * 1000.0 / len(images))
                output = output * target_std.to_numpy() + target_mean.to_numpy()
                for index, sample_id in enumerate(sample_ids):
                    row = frame_by_id.loc[sample_id]
                    prediction_rows.append(
                        {
                            "sample_id": sample_id,
                            "relative_path": paths[index],
                            "split": split,
                            "method": "mobilenet_v3_small",
                            "actual_width": row["target_width"],
                            "predicted_width": output[index, 0],
                            "actual_height": row["target_height"],
                            "predicted_height": output[index, 1],
                        }
                    )
    parameters = sum(parameter.numel() for parameter in model.parameters())
    trainable = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    metadata = {
        "epochs": len(history),
        "best_validation_loss": best_validation,
        "parameter_count": parameters,
        "trainable_parameter_count": trainable,
        "model_bytes": model_path.stat().st_size,
        "mean_cpu_inference_ms_per_image": float(np.mean(timings)),
        "history": history,
        "pretrained": bool(config.get("pretrained", True)),
        "backbone_frozen": True,
    }
    return pd.DataFrame(prediction_rows), metadata
