"""Background model loading worker thread for YOLOv8."""

from PyQt6.QtCore import QThread, pyqtSignal
import time
from .detection_engine import YOLOv8Engine
from .detection_state import DetectionState
from ..utils.logger import get_logger

logger = get_logger("model_loader")


class ModelLoaderThread(QThread):
    """Background thread for loading YOLOv8 model without blocking UI."""

    # Signals
    progress = pyqtSignal(str)      # Emitted with progress messages
    finished = pyqtSignal(bool)     # Emitted when loading complete (True=success, False=failed)
    error = pyqtSignal(str)         # Emitted on error with error message

    def __init__(self, engine: YOLOv8Engine, model_path: str):
        """Initialize model loader thread.
        
        Args:
            engine: YOLOv8Engine instance to load model into
            model_path: Path to .pt model file
        """
        super().__init__()
        self.engine = engine
        self.model_path = model_path
        self.logger = logger

    def run(self):
        """Run model loading in background thread."""
        try:
            self.logger.info(f"Starting model load in background: {self.model_path}")
            self.progress.emit("Loading model...")
            
            start_time = time.time()
            success = self.engine.load_model(self.model_path)
            elapsed_time = time.time() - start_time
            
            if success:
                self.logger.info(f"Model loaded successfully in {elapsed_time:.2f}s")
                self.progress.emit(f"Model loaded ({elapsed_time:.1f}s)")
                self.finished.emit(True)
            else:
                error_msg = self.engine.state_manager.get_error_message()
                self.logger.error(f"Model loading failed: {error_msg}")
                self.error.emit(error_msg or "Unknown error loading model")
                self.finished.emit(False)
                
        except Exception as e:
            error_msg = f"Model loading exception: {str(e)}"
            self.logger.error(error_msg)
            self.engine.state_manager.set_state(DetectionState.ERROR, error_msg)
            self.error.emit(error_msg)
            self.finished.emit(False)
