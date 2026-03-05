"""Dataset creation, splitting, export, and validation utilities."""

from __future__ import annotations

import random
from pathlib import Path
from typing import List

import yaml

from .models import BrickClass, Dataset
from .yolo_format import YoloFormatter


class DatasetBuilder:
    """Static utility methods for building and exporting YOLO datasets."""

    @staticmethod
    def create_dataset(name: str, root_path: Path, classes: List[BrickClass]) -> Dataset:
        """Create a new Dataset and initialise its directory structure."""
        root_path = Path(root_path)
        root_path.mkdir(parents=True, exist_ok=True)
        (root_path / "images").mkdir(exist_ok=True)
        return Dataset(name=name, root_path=root_path, classes=classes)

    @staticmethod
    def split_train_val(dataset: Dataset, ratio: float = 0.8, shuffle: bool = True) -> None:
        """Assign train/val split to each image in-place."""
        if not dataset.images:
            return
        images = dataset.images[:]
        if shuffle:
            random.shuffle(images)
        n_train = max(1, int(len(images) * ratio))
        for i, img in enumerate(images):
            img.split = "train" if i < n_train else "val"

    @staticmethod
    def export_dataset(dataset: Dataset) -> bool:
        """Export dataset to YOLO format (labels/*.txt + data.yaml).

        Returns True on success.
        """
        try:
            root = dataset.root_path

            # Create label split directories
            (root / "labels" / "train").mkdir(parents=True, exist_ok=True)
            (root / "labels" / "val").mkdir(parents=True, exist_ok=True)

            # Write one label file per image
            for img in dataset.images:
                split = img.split or "train"
                label_name = Path(img.image_path).stem + ".txt"
                label_path = root / "labels" / split / label_name
                YoloFormatter.write_label_file(label_path, img.annotations)

            # Write data.yaml
            yaml_data = {
                "path": str(root),
                "train": "images",
                "val": "images",
                "nc": len(dataset.classes),
                "names": [c.name for c in dataset.classes],
            }
            with open(root / "data.yaml", "w") as f:
                yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True)

            return True
        except Exception:
            return False

    @staticmethod
    def validate_dataset(dataset: Dataset) -> List[str]:
        """Validate dataset annotations and return a list of error strings."""
        errors: List[str] = []
        for img in dataset.images:
            for ann in img.annotations:
                if not (0.0 <= ann.x_center <= 1.0):
                    errors.append(
                        f"Invalid x_center={ann.x_center:.4f} in {img.image_path}"
                    )
                if not (0.0 <= ann.y_center <= 1.0):
                    errors.append(
                        f"Invalid y_center={ann.y_center:.4f} in {img.image_path}"
                    )
                if not (0.0 <= ann.width <= 1.0):
                    errors.append(
                        f"Invalid width={ann.width:.4f} in {img.image_path}"
                    )
                if not (0.0 <= ann.height <= 1.0):
                    errors.append(
                        f"Invalid height={ann.height:.4f} in {img.image_path}"
                    )
        return errors
