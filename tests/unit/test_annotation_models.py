"""Unit tests for src/annotation/models.py."""

import pytest
from pathlib import Path

from src.annotation.models import (
    Annotation,
    AnnotatedImage,
    BrickClass,
    Dataset,
    AnnotationProject,
)


def make_classes():
    return [
        BrickClass(id=0, name="3001", display_name="2x4 Brick", color=(255, 0, 0)),
        BrickClass(id=1, name="3003", display_name="2x2 Brick", color=(0, 255, 0)),
    ]


class TestBrickClass:
    def test_fields(self):
        bc = BrickClass(id=0, name="3001", display_name="2x4 Brick", color=(255, 0, 0))
        assert bc.id == 0
        assert bc.name == "3001"
        assert bc.display_name == "2x4 Brick"
        assert bc.color == (255, 0, 0)


class TestAnnotation:
    def test_from_pixel_coords_normalization(self):
        ann = Annotation.from_pixel_coords(
            class_id=0,
            class_name="3001",
            x=100, y=100, w=200, h=100,
            img_width=640, img_height=480,
        )
        assert 0.0 <= ann.x_center <= 1.0
        assert 0.0 <= ann.y_center <= 1.0
        assert 0.0 < ann.width <= 1.0
        assert 0.0 < ann.height <= 1.0

    def test_from_pixel_coords_values(self):
        ann = Annotation.from_pixel_coords(
            class_id=1, class_name="3003",
            x=0, y=0, w=640, h=480,
            img_width=640, img_height=480,
        )
        assert ann.x_center == pytest.approx(0.5)
        assert ann.y_center == pytest.approx(0.5)
        assert ann.width == pytest.approx(1.0)
        assert ann.height == pytest.approx(1.0)

    def test_unique_ids(self):
        a1 = Annotation.from_pixel_coords(0, "3001", 10, 10, 50, 50, 640, 480)
        a2 = Annotation.from_pixel_coords(0, "3001", 10, 10, 50, 50, 640, 480)
        assert a1.id != a2.id


class TestAnnotatedImage:
    def test_add_and_count(self):
        img = AnnotatedImage(image_path=Path("test.jpg"))
        assert img.annotation_count == 0
        ann = Annotation.from_pixel_coords(0, "3001", 10, 10, 50, 50, 640, 480)
        img.add_annotation(ann)
        assert img.annotation_count == 1

    def test_remove_annotation(self):
        img = AnnotatedImage(image_path=Path("test.jpg"))
        ann = Annotation.from_pixel_coords(0, "3001", 10, 10, 50, 50, 640, 480)
        img.add_annotation(ann)
        assert img.remove_annotation(ann.id)
        assert img.annotation_count == 0

    def test_remove_nonexistent_returns_false(self):
        img = AnnotatedImage(image_path=Path("test.jpg"))
        assert not img.remove_annotation("does-not-exist")

    def test_annotations_list_accessible(self):
        img = AnnotatedImage(image_path=Path("test.jpg"))
        ann = Annotation(id="x", class_id=0, class_name="3001",
                         x_center=1.5, y_center=0.5, width=0.2, height=0.2)
        img.annotations.append(ann)
        assert img.annotation_count == 1


class TestDataset:
    def test_add_image(self, tmp_path):
        classes = make_classes()
        ds = Dataset(name="test", root_path=tmp_path, classes=classes)
        img_path = tmp_path / "a.jpg"
        img_path.touch()
        annotated = ds.add_image(img_path)
        assert ds.num_images == 1
        assert annotated.image_path == img_path

    def test_num_annotations(self, tmp_path):
        classes = make_classes()
        ds = Dataset(name="test", root_path=tmp_path, classes=classes)
        img_path = tmp_path / "a.jpg"
        img_path.touch()
        ds.add_image(img_path)
        ann = Annotation.from_pixel_coords(0, "3001", 10, 10, 50, 50, 640, 480)
        ds.images[0].add_annotation(ann)
        assert ds.num_annotations == 1

    def test_train_val_counts(self, tmp_path):
        classes = make_classes()
        ds = Dataset(name="test", root_path=tmp_path, classes=classes)
        for i in range(4):
            p = tmp_path / f"{i}.jpg"
            p.touch()
            img = ds.add_image(p)
            img.split = "train" if i < 3 else "val"
        assert ds.num_train == 3
        assert ds.num_val == 1

    def test_get_statistics_keys(self, tmp_path):
        classes = make_classes()
        ds = Dataset(name="test", root_path=tmp_path, classes=classes)
        p = tmp_path / "a.jpg"
        p.touch()
        ds.add_image(p)
        ann = Annotation.from_pixel_coords(0, "3001", 10, 10, 50, 50, 640, 480)
        ds.images[0].add_annotation(ann)
        stats = ds.get_statistics()
        assert "total_images" in stats
        assert "total_annotations" in stats
        assert "class_distribution" in stats
        assert stats["total_images"] == 1
        assert stats["total_annotations"] == 1


class TestAnnotationProject:
    def test_creation(self, tmp_path):
        classes = make_classes()
        ds = Dataset(name="proj", root_path=tmp_path, classes=classes)
        project = AnnotationProject(name="proj", dataset=ds)
        assert project.name == "proj"
        assert project.dataset is ds
        assert project.created_at  # non-empty
