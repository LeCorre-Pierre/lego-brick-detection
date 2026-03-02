"""YOLOv8 brick detection engine wrapper."""

import os
import time
from typing import List, Optional, Tuple
from numpy.typing import NDArray
import numpy as np
import cv2
import requests
import torch
from ..utils.logger import get_logger
from .detection_state import DetectionState, DetectionStateManager

logger = get_logger("detection_engine")


class Detection:
    """Represents a single brick detection result."""

    def __init__(self, bbox: Tuple[float, float, float, float], 
                 class_id: int, class_name: str, confidence: float):
        """Initialize detection.
        
        Args:
            bbox: Bounding box as (x1, y1, x2, y2) in pixel coordinates
            class_id: YOLOv8 class ID
            class_name: Human-readable class name (e.g., "2×4 Red Brick")
            confidence: Detection confidence score (0-1)
        """
        self.bbox = bbox
        self.class_id = class_id
        self.class_name = class_name
        self.confidence = confidence

    def __repr__(self) -> str:
        return f"Detection({self.class_name}, conf={self.confidence:.2f})@{self.bbox}"


class YOLOv8Engine:
    """YOLOv8 brick detection engine."""

    def __init__(self, confidence_threshold: float = 0.2, device: Optional[str] = None):
        """Initialize detection engine.
        
        Args:
            confidence_threshold: Minimum confidence for detection results (0-1)
            device: Preferred device ("cpu" or "cuda"). If None, auto-select CUDA when available.
        """
        self.model = None
        self.confidence_threshold = confidence_threshold
        self.state_manager = DetectionStateManager()
        self.last_detections: List[Detection] = []
        self.allowed_class_names: Optional[set[str]] = None  # If set, restrict detections to these names/tokens
        # Auto-select device: prefer CUDA if available
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._fallback_attempted = False  # Track CUDA→CPU fallback attempts
        self.roboflow_api_key = os.getenv("ROBOFLOW_API_KEY", "").strip()
        self.roboflow_model_id = os.getenv("ROBOFLOW_MODEL_ID", "").strip()
        self.roboflow_api_url = os.getenv("ROBOFLOW_API_URL", "https://detect.roboflow.com").strip().rstrip("/")
        self.roboflow_timeout = float(os.getenv("ROBOFLOW_TIMEOUT_SECONDS", "10"))
        self.enable_roboflow_fallback = os.getenv("ROBOFLOW_FALLBACK", "1").strip().lower() in {
            "1", "true", "yes", "on"
        }
        self.roboflow_min_interval_seconds = float(os.getenv("ROBOFLOW_MIN_INTERVAL_SECONDS", "0.4"))
        self._last_roboflow_request = 0.0
        logger.info(f"YOLOv8Engine initialized (threshold={confidence_threshold}, device={self.device})")
        if self.is_remote_configured():
            logger.info(f"Roboflow remote fallback enabled for model: {self.roboflow_model_id}")

    def is_remote_configured(self) -> bool:
        """Return True when Roboflow hosted inference is configured."""
        return bool(self.roboflow_api_key and self.roboflow_model_id)

    def set_confidence_threshold(self, threshold: float) -> None:
        """Update the confidence threshold used for filtering detections.

        Args:
            threshold: Value between 0.0 and 1.0.
        """
        try:
            t = max(0.0, min(1.0, float(threshold)))
            self.confidence_threshold = t
            logger.info(f"Detection confidence threshold set -> {t:.2f}")
        except Exception as e:
            logger.error(f"Failed to set confidence threshold: {e}")

    def set_allowed_class_names(self, names: Optional[set[str]]):
        """Set allowed class names for filtering detections.
        
        Args:
            names: Set of allowed class names/tokens. If None or empty, allow all classes.
        """
        try:
            if names is None or len(names) == 0:
                self.allowed_class_names = None
                logger.info("Detection class filter disabled (allow all classes)")
            else:
                # Normalize to lowercase tokens for robust matching
                self.allowed_class_names = {str(n).strip().lower() for n in names if str(n).strip()}
                logger.info(f"Detection class filter enabled for {len(self.allowed_class_names)} names/tokens")
        except Exception as e:
            logger.error(f"Failed to set allowed class names: {e}")

    def load_model(self, model_path: str) -> bool:
        """Load YOLOv8 model from file.
        
        Args:
            model_path: Path to .pt model file
            
        Returns:
            True if load successful, False otherwise
        """
        try:
            # Validate file exists
            if not os.path.exists(model_path):
                error_msg = f"Model file not found: {model_path}"
                logger.error(error_msg)
                self.state_manager.set_state(DetectionState.ERROR, error_msg)
                return False

            # Import YOLO here to handle missing ultralytics gracefully
            try:
                from ultralytics import YOLO
            except ImportError:
                error_msg = "ultralytics package not installed. Run: pip install ultralytics"
                logger.error(error_msg)
                self.state_manager.set_state(DetectionState.ERROR, error_msg)
                return False

            logger.info(f"Loading YOLOv8 model from {model_path}")
            self.model = YOLO(model_path)

            # Force model to the preferred device (default CPU). This avoids CUDA NMS issues on systems
            # without properly built torchvision ops.
            try:
                self.model.to(self.device)
                logger.info(f"Model moved to device: {self.device}")
            except Exception as move_err:
                logger.warning(f"Could not move model to {self.device}: {move_err}. Falling back to CPU.")
                self.model.to("cpu")
                self.device = "cpu"

            self.state_manager.set_state(DetectionState.READY)
            logger.info("Model loaded successfully")
            return True

        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            logger.error(error_msg)
            self.state_manager.set_state(DetectionState.ERROR, error_msg)
            return False

    def infer(self, frame: NDArray[np.uint8]) -> List[Detection]:
        """Run inference on a frame.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List of Detection objects
        """
        if self.model is None:
            if self.is_remote_configured():
                return self._infer_with_roboflow(frame)
            logger.warning("Model not loaded, skipping inference")
            return []

        try:
            # Run YOLOv8 inference
            results = self.model(frame, verbose=False, device=self.device, conf=self.confidence_threshold)
            detections = []

            for result in results:
                if result.boxes is None:
                    continue

                for box in result.boxes:
                    confidence = float(box.conf[0])
                    
                    # Filter by confidence threshold
                    if confidence < self.confidence_threshold:
                        continue

                    # Extract bounding box coordinates
                    x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
                    class_id = int(box.cls[0])
                    
                    # Get class name (use generic if not available)
                    class_name = self.model.names.get(class_id, f"Class {class_id}")

                    # Optional filtering by allowed class names/tokens
                    if not self._is_detection_allowed(class_name):
                        continue
                    
                    detection = Detection(
                        bbox=(x1, y1, x2, y2),
                        class_id=class_id,
                        class_name=class_name,
                        confidence=confidence
                    )
                    detections.append(detection)

            if len(detections) == 0 and self.enable_roboflow_fallback and self.is_remote_configured():
                remote_detections = self._infer_with_roboflow(frame)
                if remote_detections:
                    self.last_detections = remote_detections
                    return remote_detections

            self.last_detections = detections
            return detections

        except Exception as e:
            err_msg = str(e)
            # If CUDA NMS is missing or fails, fall back to CPU once
            if ("nms" in err_msg.lower() and "cuda" in err_msg.lower() and not self._fallback_attempted):
                logger.warning("CUDA NMS unavailable; falling back to CPU for inference")
                try:
                    self.model.to("cpu")
                    self.device = "cpu"
                    self._fallback_attempted = True
                    return self.infer(frame)
                except Exception as fallback_err:
                    logger.error(f"CPU fallback failed: {fallback_err}")
                    return []

            logger.error(f"Inference failed: {err_msg}")
            return []

    def _is_detection_allowed(self, class_name: str) -> bool:
        """Return True if class should be included based on active set filter."""
        if not self.allowed_class_names:
            return True
        name_lower = class_name.lower()
        if name_lower in self.allowed_class_names:
            return True
        return any(token in name_lower for token in self.allowed_class_names)

    def _infer_with_roboflow(self, frame: NDArray[np.uint8]) -> List[Detection]:
        """Run hosted inference using Roboflow API and map output to Detection objects."""
        if not self.is_remote_configured():
            return []

        now = time.time()
        if now - self._last_roboflow_request < self.roboflow_min_interval_seconds:
            return self.last_detections.copy()

        self._last_roboflow_request = now

        try:
            ok, encoded = cv2.imencode(".jpg", frame)
            if not ok:
                logger.error("Roboflow fallback failed: could not encode frame to JPEG")
                return []

            endpoint = f"{self.roboflow_api_url}/{self.roboflow_model_id}"
            params = {
                "api_key": self.roboflow_api_key,
                "confidence": int(self.confidence_threshold * 100),
                "format": "json",
            }
            response = requests.post(
                endpoint,
                params=params,
                files={"file": ("frame.jpg", encoded.tobytes(), "image/jpeg")},
                timeout=self.roboflow_timeout,
            )
            response.raise_for_status()

            payload = response.json()
            predictions = payload.get("predictions", [])
            detections: List[Detection] = []

            for pred in predictions:
                confidence = float(pred.get("confidence", 0.0))
                if confidence < self.confidence_threshold:
                    continue

                class_name = str(pred.get("class", pred.get("class_name", "Unknown")))
                if not self._is_detection_allowed(class_name):
                    continue

                x = float(pred.get("x", 0.0))
                y = float(pred.get("y", 0.0))
                w = float(pred.get("width", 0.0))
                h = float(pred.get("height", 0.0))
                x1 = x - (w / 2.0)
                y1 = y - (h / 2.0)
                x2 = x + (w / 2.0)
                y2 = y + (h / 2.0)

                class_id_raw = pred.get("class_id", -1)
                try:
                    class_id = int(class_id_raw)
                except Exception:
                    class_id = -1

                detections.append(
                    Detection(
                        bbox=(x1, y1, x2, y2),
                        class_id=class_id,
                        class_name=class_name,
                        confidence=confidence,
                    )
                )

            return detections
        except Exception as e:
            logger.warning(f"Roboflow fallback inference failed: {e}")
            return []

    def get_detections(self) -> List[Detection]:
        """Get last inference results.
        
        Returns:
            List of Detection objects from last inference
        """
        return self.last_detections.copy()

    def unload_model(self) -> None:
        """Unload model and free memory."""
        try:
            if self.model is not None:
                del self.model
                self.model = None
                self.state_manager.set_state(DetectionState.OFF)
                logger.info("Model unloaded")
        except Exception as e:
            logger.error(f"Error unloading model: {str(e)}")

    def get_state(self) -> DetectionState:
        """Get current detection state."""
        return self.state_manager.get_state()

    def set_state(self, state: DetectionState, error_msg: Optional[str] = None) -> None:
        """Set detection state."""
        self.state_manager.set_state(state, error_msg)
