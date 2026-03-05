"""CRUD manager for annotation projects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .models import Annotation, AnnotatedImage, AnnotationProject, BrickClass, Dataset
from .yolo_format import YoloFormatter


class AnnotationManager:
    """Manages CRUD operations on annotation projects."""

    def __init__(self) -> None:
        self._project: Optional[AnnotationProject] = None
        self._current_image_index: int = 0

    # ------------------------------------------------------------------
    # Project lifecycle
    # ------------------------------------------------------------------

    def create_new_project(self, dataset: Dataset) -> None:
        """Create a new project wrapping an existing Dataset."""
        self._project = AnnotationProject(name=dataset.name, dataset=dataset)
        self._current_image_index = 0

    def save_project(self, path: Path) -> bool:
        """Serialise the project to JSON. Returns True on success."""
        if self._project is None:
            return False
        try:
            path = Path(path)
            data = _project_to_dict(self._project)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load_project(self, path: Path) -> None:
        """Load a project from JSON. Raises on failure."""
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._project = _project_from_dict(data)
        self._current_image_index = 0

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    @property
    def current_image_index(self) -> int:
        return self._current_image_index

    @property
    def current_image(self) -> Optional[AnnotatedImage]:
        if self._project is None or not self._project.dataset.images:
            return None
        idx = max(0, min(self._current_image_index, len(self._project.dataset.images) - 1))
        return self._project.dataset.images[idx]

    @property
    def dataset(self) -> Optional[Dataset]:
        return self._project.dataset if self._project else None

    def next_image(self) -> None:
        if self._project is None:
            return
        n = len(self._project.dataset.images)
        if n > 0:
            self._current_image_index = min(self._current_image_index + 1, n - 1)

    def previous_image(self) -> None:
        self._current_image_index = max(self._current_image_index - 1, 0)

    # ------------------------------------------------------------------
    # Annotation CRUD
    # ------------------------------------------------------------------

    def _find_image(self, image_path: Path) -> Optional[AnnotatedImage]:
        """Find an AnnotatedImage by its path."""
        if self._project is None:
            return None
        target = Path(image_path)
        for img in self._project.dataset.images:
            if Path(img.image_path) == target:
                return img
        return None

    def _find_annotation(self, ann_id: str) -> Optional[tuple[AnnotatedImage, Annotation]]:
        """Find an annotation by ID, returning (image, annotation)."""
        if self._project is None:
            return None
        for img in self._project.dataset.images:
            for ann in img.annotations:
                if ann.id == ann_id:
                    return img, ann
        return None

    def create_annotation(
        self,
        image_path: Path,
        class_id: int,
        class_name: str,
        x: int,
        y: int,
        w: int,
        h: int,
        img_width: int,
        img_height: int,
    ) -> Optional[Annotation]:
        """Create and add a new annotation to the specified image."""
        img = self._find_image(image_path)
        if img is None:
            return None
        ann = Annotation.from_pixel_coords(class_id, class_name, x, y, w, h, img_width, img_height)
        img.add_annotation(ann)
        return ann

    def update_annotation(
        self,
        ann_id: str,
        x: int,
        y: int,
        w: int,
        h: int,
        img_width: int,
        img_height: int,
    ) -> bool:
        """Update bbox of an existing annotation in-place. Returns True on success."""
        result = self._find_annotation(ann_id)
        if result is None:
            return False
        _, ann = result
        ann.x_center = (x + w / 2) / img_width
        ann.y_center = (y + h / 2) / img_height
        ann.width = w / img_width
        ann.height = h / img_height
        return True

    def delete_annotation(self, ann_id: str) -> bool:
        """Delete an annotation by ID. Returns True on success."""
        result = self._find_annotation(ann_id)
        if result is None:
            return False
        img, _ = result
        return img.remove_annotation(ann_id)


# ------------------------------------------------------------------
# JSON serialisation helpers
# ------------------------------------------------------------------

def _project_to_dict(project: AnnotationProject) -> dict:
    ds = project.dataset
    return {
        "name": project.name,
        "created_at": project.created_at,
        "dataset": {
            "name": ds.name,
            "root_path": str(ds.root_path),
            "classes": [
                {
                    "id": c.id,
                    "name": c.name,
                    "display_name": c.display_name,
                    "color": list(c.color),
                }
                for c in ds.classes
            ],
            "images": [
                {
                    "image_path": str(img.image_path),
                    "split": img.split,
                    "annotations": [
                        {
                            "id": ann.id,
                            "class_id": ann.class_id,
                            "class_name": ann.class_name,
                            "x_center": ann.x_center,
                            "y_center": ann.y_center,
                            "width": ann.width,
                            "height": ann.height,
                        }
                        for ann in img.annotations
                    ],
                }
                for img in ds.images
            ],
        },
    }


def _project_from_dict(data: dict) -> AnnotationProject:
    ds_data = data["dataset"]
    classes = [
        BrickClass(
            id=c["id"],
            name=c["name"],
            display_name=c["display_name"],
            color=tuple(c["color"]),
        )
        for c in ds_data.get("classes", [])
    ]
    images = []
    for img_data in ds_data.get("images", []):
        annotations = [
            Annotation(
                id=a["id"],
                class_id=a["class_id"],
                class_name=a["class_name"],
                x_center=a["x_center"],
                y_center=a["y_center"],
                width=a["width"],
                height=a["height"],
            )
            for a in img_data.get("annotations", [])
        ]
        images.append(
            AnnotatedImage(
                image_path=Path(img_data["image_path"]),
                annotations=annotations,
                split=img_data.get("split"),
            )
        )
    dataset = Dataset(
        name=ds_data["name"],
        root_path=Path(ds_data["root_path"]),
        classes=classes,
        images=images,
    )
    return AnnotationProject(
        name=data["name"],
        dataset=dataset,
        created_at=data.get("created_at", ""),
    )
