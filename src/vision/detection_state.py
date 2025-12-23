"""Detection state management for YOLOv8 brick detection."""

from enum import Enum
from threading import Lock
from typing import Optional
from ..utils.logger import get_logger

logger = get_logger("detection_state")


class DetectionState(Enum):
    """Enumeration of detection states."""
    OFF = "off"                    # Detection disabled
    LOADING = "loading"            # Model loading in progress
    READY = "ready"                # Model loaded, detection available but not active
    ACTIVE = "active"              # Detection running
    ERROR = "error"                # Model failed to load or inference error


class DetectionStateManager:
    """Thread-safe detection state management."""

    def __init__(self):
        self._state = DetectionState.LOADING
        self._error_message: Optional[str] = None
        self._lock = Lock()
        logger.info(f"Detection state initialized: {self._state.value}")

    def set_state(self, state: DetectionState, error_msg: Optional[str] = None) -> None:
        """Set detection state (thread-safe).
        
        Args:
            state: New detection state
            error_msg: Error message if state is ERROR
        """
        with self._lock:
            old_state = self._state
            self._state = state
            self._error_message = error_msg
            logger.info(f"Detection state changed: {old_state.value} → {state.value}")
            if error_msg:
                logger.error(f"Detection error: {error_msg}")

    def get_state(self) -> DetectionState:
        """Get current detection state (thread-safe)."""
        with self._lock:
            return self._state

    def get_error_message(self) -> Optional[str]:
        """Get error message if state is ERROR (thread-safe)."""
        with self._lock:
            return self._error_message

    def is_loading(self) -> bool:
        """Check if model is currently loading."""
        return self.get_state() == DetectionState.LOADING

    def is_ready(self) -> bool:
        """Check if model is loaded and detection is available."""
        return self.get_state() == DetectionState.READY

    def is_active(self) -> bool:
        """Check if detection is currently active."""
        return self.get_state() == DetectionState.ACTIVE

    def is_error(self) -> bool:
        """Check if an error occurred."""
        return self.get_state() == DetectionState.ERROR
