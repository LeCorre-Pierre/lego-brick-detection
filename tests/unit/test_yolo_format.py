"""Unit tests for src/annotation/yolo_format.py."""

import pytest
from pathlib import Path

from src.annotation.models import Annotation, BrickClass
from src.annotation.yolo_format import YoloFormatter


CLASSES = [
    BrickClass(id=0, name="3001", display_name="2x4 Brick", color=(255, 0, 0)),
    BrickClass(id=1, name="3003", display_name="2x2 Brick", color=(0, 255, 0)),
]


class TestPixelToNormalized:
    def test_center_of_image(self):
        x_c, y_c, w_n, h_n = YoloFormatter.pixel_to_normalized(
            x=0, y=0, w=640, h=480, img_width=640, img_height=480
        )
        assert x_c == pytest.approx(0.5)
        assert y_c == pytest.approx(0.5)
        assert w_n == pytest.approx(1.0)
        assert h_n == pytest.approx(1.0)

    def test_values_in_range(self):
        x_c, y_c, w_n, h_n = YoloFormatter.pixel_to_normalized(
            x=100, y=100, w=200, h=150, img_width=640, img_height=480
        )
        assert 0.0 <= x_c <= 1.0
        assert 0.0 <= y_c <= 1.0
        assert 0.0 < w_n <= 1.0
        assert 0.0 < h_n <= 1.0


class TestNormalizedToPixel:
    def test_round_trip(self):
        orig_x, orig_y, orig_w, orig_h = 100, 100, 200, 150
        x_c, y_c, w_n, h_n = YoloFormatter.pixel_to_normalized(
            orig_x, orig_y, orig_w, orig_h, 640, 480
        )
        x, y, w, h = YoloFormatter.normalized_to_pixel(x_c, y_c, w_n, h_n, 640, 480)
        assert abs(x - orig_x) < 2
        assert abs(y - orig_y) < 2
        assert abs(w - orig_w) < 2
        assert abs(h - orig_h) < 2

    def test_full_image(self):
        x, y, w, h = YoloFormatter.normalized_to_pixel(0.5, 0.5, 1.0, 1.0, 640, 480)
        assert x == 0
        assert y == 0
        assert w == 640
        assert h == 480


class TestWriteReadLabelFile:
    def test_write_creates_file(self, tmp_path):
        label_path = tmp_path / "test.txt"
        ann = Annotation.from_pixel_coords(0, "3001", 50, 50, 100, 100, 640, 480)
        YoloFormatter.write_label_file(label_path, [ann])
        assert label_path.exists()

    def test_read_roundtrip(self, tmp_path):
        label_path = tmp_path / "labels" / "test.txt"
        ann = Annotation.from_pixel_coords(0, "3001", 50, 50, 100, 100, 640, 480)
        YoloFormatter.write_label_file(label_path, [ann])
        annotations = YoloFormatter.read_label_file(label_path, CLASSES)
        assert len(annotations) == 1
        assert annotations[0].class_id == 0
        assert annotations[0].class_name == "3001"
        assert annotations[0].x_center == pytest.approx(ann.x_center, abs=1e-4)
        assert annotations[0].y_center == pytest.approx(ann.y_center, abs=1e-4)

    def test_format_correct(self, tmp_path):
        label_path = tmp_path / "test.txt"
        ann = Annotation(id="x", class_id=1, class_name="3003",
                         x_center=0.5, y_center=0.5, width=0.25, height=0.25)
        YoloFormatter.write_label_file(label_path, [ann])
        content = label_path.read_text().strip()
        parts = content.split()
        assert parts[0] == "1"
        assert float(parts[1]) == pytest.approx(0.5, abs=1e-5)

    def test_empty_annotations(self, tmp_path):
        label_path = tmp_path / "empty.txt"
        YoloFormatter.write_label_file(label_path, [])
        result = YoloFormatter.read_label_file(label_path, CLASSES)
        assert result == []

    def test_read_nonexistent_returns_empty(self, tmp_path):
        result = YoloFormatter.read_label_file(tmp_path / "nope.txt", CLASSES)
        assert result == []
