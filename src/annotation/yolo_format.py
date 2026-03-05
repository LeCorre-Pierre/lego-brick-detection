"""YOLO label format read/write utilities."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import List, Tuple

from .models import Annotation, BrickClass


class YoloFormatter:
    """Utility class for YOLO label format conversions."""

    @staticmethod
    def pixel_to_normalized(
        x: int,
        y: int,
        w: int,
        h: int,
        img_width: int,
        img_height: int,
    ) -> Tuple[float, float, float, float]:
        """Convert pixel bbox (top-left x, y, w, h) to YOLO normalized (x_c, y_c, w_n, h_n)."""
        x_c = (x + w / 2) / img_width
        y_c = (y + h / 2) / img_height
        w_n = w / img_width
        h_n = h / img_height
        return x_c, y_c, w_n, h_n

    @staticmethod
    def normalized_to_pixel(
        x_c: float,
        y_c: float,
        w_n: float,
        h_n: float,
        img_width: int,
        img_height: int,
    ) -> Tuple[int, int, int, int]:
        """Convert YOLO normalized (x_c, y_c, w_n, h_n) to pixel bbox (top-left x, y, w, h)."""
        w = int(round(w_n * img_width))
        h = int(round(h_n * img_height))
        x = int(round(x_c * img_width - w / 2))
        y = int(round(y_c * img_height - h / 2))
        return x, y, w, h

    @staticmethod
    def write_label_file(path: Path, annotations: List[Annotation]) -> None:
        """Write a YOLO label .txt file (one annotation per line)."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            for ann in annotations:
                f.write(
                    f"{ann.class_id} {ann.x_center:.6f} {ann.y_center:.6f}"
                    f" {ann.width:.6f} {ann.height:.6f}\n"
                )

    @staticmethod
    def read_label_file(path: Path, classes: List[BrickClass]) -> List[Annotation]:
        """Read a YOLO label .txt file and return a list of Annotations."""
        path = Path(path)
        if not path.exists():
            return []

        class_map = {c.id: c.name for c in classes}
        annotations: List[Annotation] = []

        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 5:
                    continue
                class_id = int(parts[0])
                x_c = float(parts[1])
                y_c = float(parts[2])
                w = float(parts[3])
                h = float(parts[4])
                class_name = class_map.get(class_id, str(class_id))
                annotations.append(
                    Annotation(
                        id=str(uuid.uuid4()),
                        class_id=class_id,
                        class_name=class_name,
                        x_center=x_c,
                        y_center=y_c,
                        width=w,
                        height=h,
                    )
                )

        return annotations
