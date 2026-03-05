"""Manages frame capture sessions for annotation data collection."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np
import yaml

from .models import BrickClass
from .yolo_format import YoloFormatter


class CaptureManager:
    """Manages capture sessions: saves frames + optional YOLO labels."""

    def __init__(self, dataset_root: Path, session_name: Optional[str] = None) -> None:
        self._dataset_root = Path(dataset_root)
        if session_name is None:
            session_name = "session_" + datetime.datetime.now().strftime("%Y%m%d_%H%M")
        self._session_name = session_name
        self._session_path = self._dataset_root / session_name
        (self._session_path / "images").mkdir(parents=True, exist_ok=True)
        (self._session_path / "labels").mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_frame(
        self,
        frame: np.ndarray,
        part_number: str,
        bbox: Optional[Tuple[int, int, int, int]] = None,
    ) -> Tuple[Path, Optional[Path]]:
        """Save a frame as JPEG and optionally write a YOLO label.

        Args:
            frame: BGR numpy array from OpenCV.
            part_number: LEGO part number used as filename prefix.
            bbox: Optional (x, y, w, h) pixel bbox. If provided, writes a YOLO .txt.

        Returns:
            (image_path, label_path or None)
        """
        count = self.get_capture_count(part_number)
        stem = f"{part_number}_{count:04d}"

        image_path = self._session_path / "images" / f"{stem}.jpg"
        cv2.imwrite(str(image_path), frame)

        label_path: Optional[Path] = None
        if bbox is not None:
            x, y, w, h = bbox
            img_h, img_w = frame.shape[:2]
            x_c, y_c, w_n, h_n = YoloFormatter.pixel_to_normalized(x, y, w, h, img_w, img_h)
            label_path = self._session_path / "labels" / f"{stem}.txt"
            with open(label_path, "w") as f:
                f.write(f"0 {x_c:.6f} {y_c:.6f} {w_n:.6f} {h_n:.6f}\n")

        return image_path, label_path

    def auto_detect_bbox(
        self, frame: np.ndarray
    ) -> Optional[Tuple[int, int, int, int]]:
        """Return the bounding rect of the largest foreground region, or None.

        Uses a permissive contour approach suited for a single brick on a table:
        converts to grayscale, blurs, thresholds adaptively, then returns the
        bounding rect of the largest contour above a minimum area.

        Returns (x, y, w, h) in pixel coordinates (top-left origin).
        """
        img_h, img_w = frame.shape[:2]
        min_area = (img_w * img_h) * 0.005  # at least 0.5% of frame

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Otsu threshold — works well when brick contrasts with background
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Close small gaps so the brick reads as one region
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        # Pick the largest contour that exceeds the minimum area threshold
        valid = [c for c in contours if cv2.contourArea(c) >= min_area]
        if not valid:
            return None

        largest = max(valid, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        return x, y, w, h

    def get_capture_count(self, part_number: str) -> int:
        """Return how many frames have been saved for the given part number."""
        images_dir = self._session_path / "images"
        if not images_dir.exists():
            return 0
        return len(list(images_dir.glob(f"{part_number}_*.jpg")))

    def get_session_path(self) -> Path:
        """Return the current session directory path."""
        return self._session_path

    def generate_data_yaml(self, classes: List[BrickClass]) -> Path:
        """Write/update data.yaml at dataset root, listing all sessions.

        Args:
            classes: List of BrickClass objects defining the class names.

        Returns:
            Path to the written data.yaml file.
        """
        sessions = sorted(
            d.name
            for d in self._dataset_root.iterdir()
            if d.is_dir() and d.name.startswith("session_")
        )
        train_paths = [f"{s}/images" for s in sessions]

        yaml_data = {
            "path": str(self._dataset_root),
            "train": train_paths,
            "val": [],
            "nc": len(classes),
            "names": sorted(c.name for c in classes),
        }
        yaml_path = self._dataset_root / "data.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True)
        return yaml_path
