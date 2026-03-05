"""Domain models for the annotation system."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class BrickClass:
    """A detection class (= LEGO part number)."""

    id: int
    name: str
    display_name: str
    color: Tuple[int, int, int]


@dataclass
class Annotation:
    """Normalized YOLO bounding box annotation."""

    id: str
    class_id: int
    class_name: str
    x_center: float
    y_center: float
    width: float
    height: float

    @classmethod
    def from_pixel_coords(
        cls,
        class_id: int,
        class_name: str,
        x: int,
        y: int,
        w: int,
        h: int,
        img_width: int,
        img_height: int,
    ) -> "Annotation":
        """Create annotation from pixel-space bbox (top-left x, y, width, height)."""
        x_center = (x + w / 2) / img_width
        y_center = (y + h / 2) / img_height
        width = w / img_width
        height = h / img_height
        return cls(
            id=str(uuid.uuid4()),
            class_id=class_id,
            class_name=class_name,
            x_center=x_center,
            y_center=y_center,
            width=width,
            height=height,
        )


@dataclass
class AnnotatedImage:
    """An image with its YOLO annotations."""

    image_path: Path
    annotations: List[Annotation] = field(default_factory=list)
    split: Optional[str] = None  # 'train', 'val', or None

    @property
    def annotation_count(self) -> int:
        return len(self.annotations)

    def add_annotation(self, ann: Annotation) -> None:
        self.annotations.append(ann)

    def remove_annotation(self, ann_id: str) -> bool:
        for i, ann in enumerate(self.annotations):
            if ann.id == ann_id:
                del self.annotations[i]
                return True
        return False


@dataclass
class Dataset:
    """A dataset of annotated images for YOLO training."""

    name: str
    root_path: Path
    classes: List[BrickClass]
    images: List[AnnotatedImage] = field(default_factory=list)

    def add_image(self, path: Path) -> AnnotatedImage:
        img = AnnotatedImage(image_path=Path(path))
        self.images.append(img)
        return img

    @property
    def num_images(self) -> int:
        return len(self.images)

    @property
    def num_annotations(self) -> int:
        return sum(img.annotation_count for img in self.images)

    @property
    def num_train(self) -> int:
        return sum(1 for img in self.images if img.split == "train")

    @property
    def num_val(self) -> int:
        return sum(1 for img in self.images if img.split == "val")

    def get_statistics(self) -> Dict[str, Any]:
        """Return dataset statistics including class distribution."""
        class_dist: Dict[str, int] = {}
        for img in self.images:
            for ann in img.annotations:
                class_dist[ann.class_name] = class_dist.get(ann.class_name, 0) + 1
        return {
            "total_images": self.num_images,
            "total_annotations": self.num_annotations,
            "num_train": self.num_train,
            "num_val": self.num_val,
            "class_distribution": class_dist,
        }


@dataclass
class AnnotationProject:
    """Persistable envelope for an annotation project."""

    name: str
    dataset: Dataset
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
