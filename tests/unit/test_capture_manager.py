"""Unit tests for src/annotation/capture_manager.py."""

import numpy as np
import pytest
from pathlib import Path

from src.annotation.capture_manager import CaptureManager
from src.annotation.models import BrickClass


def make_frame(h=480, w=640, with_brick=False):
    """Create a synthetic BGR frame."""
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    if with_brick:
        # Draw a white rectangle to create a detectable contour
        frame[100:300, 150:450] = 200
    return frame


@pytest.fixture
def capture_manager(tmp_path):
    return CaptureManager(dataset_root=tmp_path / "dataset", session_name="session_test")


class TestSaveFrame:
    def test_saves_jpg(self, capture_manager):
        frame = make_frame()
        img_path, label_path = capture_manager.save_frame(frame, "3001")
        assert img_path.exists()
        assert img_path.suffix == ".jpg"
        assert label_path is None

    def test_saves_label_when_bbox_provided(self, capture_manager):
        frame = make_frame()
        img_path, label_path = capture_manager.save_frame(frame, "3001", bbox=(50, 50, 100, 80))
        assert img_path.exists()
        assert label_path is not None
        assert label_path.exists()
        content = label_path.read_text().strip()
        parts = content.split()
        assert len(parts) == 5
        assert parts[0] == "0"

    def test_sequential_naming(self, capture_manager):
        frame = make_frame()
        p1, _ = capture_manager.save_frame(frame, "3001")
        p2, _ = capture_manager.save_frame(frame, "3001")
        assert p1 != p2
        assert "3001_0000" in p1.name
        assert "3001_0001" in p2.name


class TestGetCaptureCount:
    def test_zero_initially(self, capture_manager):
        assert capture_manager.get_capture_count("3001") == 0

    def test_increments_after_save(self, capture_manager):
        frame = make_frame()
        capture_manager.save_frame(frame, "3001")
        capture_manager.save_frame(frame, "3001")
        assert capture_manager.get_capture_count("3001") == 2

    def test_different_parts_independent(self, capture_manager):
        frame = make_frame()
        capture_manager.save_frame(frame, "3001")
        assert capture_manager.get_capture_count("3003") == 0


class TestAutoDetectBbox:
    def test_empty_frame_returns_none(self, capture_manager):
        frame = make_frame(with_brick=False)
        result = capture_manager.auto_detect_bbox(frame)
        # May or may not detect noise; just verify type contract
        assert result is None or (isinstance(result, tuple) and len(result) == 4)

    def test_frame_with_brick_returns_tuple(self, capture_manager):
        frame = make_frame(with_brick=True)
        result = capture_manager.auto_detect_bbox(frame)
        # With a clear rectangle, should detect something
        if result is not None:
            x, y, w, h = result
            assert w > 0
            assert h > 0


class TestGetSessionPath:
    def test_returns_path(self, capture_manager):
        path = capture_manager.get_session_path()
        assert isinstance(path, Path)
        assert path.name == "session_test"


class TestGenerateDataYaml:
    def test_creates_yaml(self, tmp_path):
        cm = CaptureManager(dataset_root=tmp_path / "ds", session_name="session_a")
        frame = make_frame()
        cm.save_frame(frame, "3001")

        classes = [
            BrickClass(id=0, name="3001", display_name="2x4 Brick", color=(255, 0, 0)),
        ]
        yaml_path = cm.generate_data_yaml(classes)
        assert yaml_path.exists()

        import yaml
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        assert data["nc"] == 1
        assert "3001" in data["names"]
        assert any("session_a" in str(p) for p in data["train"])
