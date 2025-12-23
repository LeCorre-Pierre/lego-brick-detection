"""YOLOv8 brick detection engine wrapper."""

import os
from typing import List, Optional, Tuple
import numpy as np
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

    def __init__(self, confidence_threshold: float = 0.5):
        """Initialize detection engine.
        
        Args:
            confidence_threshold: Minimum confidence for detection results (0-1)
        """
        self.model = None
        self.confidence_threshold = confidence_threshold
        self.state_manager = DetectionStateManager()
        self.last_detections: List[Detection] = []
        logger.info(f"YOLOv8Engine initialized (threshold={confidence_threshold})")

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
            self.state_manager.set_state(DetectionState.READY)
            logger.info("Model loaded successfully")
            return True

        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            logger.error(error_msg)
            self.state_manager.set_state(DetectionState.ERROR, error_msg)
            return False

    def infer(self, frame: np.ndarray) -> List[Detection]:
        """Run inference on a frame.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List of Detection objects
        """
        if self.model is None:
            logger.warning("Model not loaded, skipping inference")
            return []

        try:
            # Run YOLOv8 inference
            results = self.model(frame, verbose=False)
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
                    
                    detection = Detection(
                        bbox=(x1, y1, x2, y2),
                        class_id=class_id,
                        class_name=class_name,
                        confidence=confidence
                    )
                    detections.append(detection)

            self.last_detections = detections
            return detections

        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
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
